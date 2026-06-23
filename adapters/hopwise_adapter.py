"""Convert validated Hopwise native paths into canonical xrecsys CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import pickle
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_adapter import format_path, load_train_labels, write_csvs


def load_test_users(labels_dir: Path) -> set[int]:
    with (labels_dir / "test_label.pkl").open("rb") as handle:
        return {int(uid) for uid in pickle.load(handle)}


def load_shard_rows(raw_path: Path, raw: dict) -> Iterator[tuple[Path, list[dict]]]:
    for shard_value in raw.get("row_shards", []):
        shard_path = Path(shard_value)
        if not shard_path.is_absolute():
            shard_path = raw_path.parent / shard_path
        if not shard_path.is_file():
            raise FileNotFoundError(f"Missing Hopwise path shard: {shard_path}")
        with shard_path.open("rb") as handle:
            payload = pickle.load(handle)
        rows = payload.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Hopwise path shard has no row list: {shard_path}")
        yield shard_path, rows


def validate_row(
    row: dict,
    *,
    test_users: set[int],
    excluded: dict[int, set[int]],
) -> tuple[int, int, float, float, list[tuple]] | None:
    uid = int(row["uid"])
    pid = int(row["pid"])
    score = float(row["score"])
    path_prob = float(row["path_prob"])
    path = row["path"]

    if uid not in test_users:
        raise ValueError(f"Hopwise exported uid={uid} outside canonical test users")
    if not math.isfinite(score) or not math.isfinite(path_prob):
        raise ValueError(f"Non-finite Hopwise path confidence for uid={uid}, pid={pid}")
    if not 0.0 <= path_prob <= 1.0:
        raise ValueError(f"Out-of-range Hopwise path probability={path_prob}")
    if not path or path[0][1:] != ("user", uid) or path[-1][2] != pid:
        raise ValueError(
            f"Hopwise canonical path endpoint mismatch: uid={uid}, pid={pid}, path={path}"
        )
    if pid in excluded.get(uid, set()):
        return None
    return uid, pid, score, path_prob, path


def convert_sharded(
    *,
    raw_path: Path,
    raw: dict,
    xrecsys_dir: Path,
    labels_dir: Path,
    topk: int,
    agent_topk_tag: str,
    include_all_test_users: bool,
    summary_json: Path | None,
) -> dict:
    dataset = raw["canonical_dataset"]
    requested_users = int(raw.get("requested_users", 0))
    processed_users = int(raw.get("processed_users", 0))
    skipped_cold_start_users = {
        int(uid) for uid in raw.get("skipped_cold_start_users", [])
    }
    excluded = load_train_labels(
        str(xrecsys_dir), dataset, labels_dir=str(labels_dir)
    )
    test_users = load_test_users(labels_dir)
    if not skipped_cold_start_users.issubset(test_users):
        unexpected = sorted(skipped_cold_start_users - test_users)[:10]
        raise ValueError(f"Cold-start users outside canonical test labels: {unexpected}")
    if requested_users and requested_users != processed_users + len(
        skipped_cold_start_users
    ):
        raise ValueError(
            "Hopwise raw user accounting mismatch: "
            f"requested={requested_users}, processed={processed_users}, "
            f"skipped={len(skipped_cold_start_users)}"
        )

    min_score = math.inf
    max_score = -math.inf
    raw_paths = 0
    unseen_paths = 0
    raw_users = set()
    candidate_users = set()
    users_seen_in_prior_shards = set()
    shard_count = 0

    # First pass validates every row and finds the global native-score range.
    # Exact-path de-duplication stays batch-local because the extractor
    # guarantees each evaluation user occurs in exactly one shard.
    for shard_path, rows in load_shard_rows(raw_path, raw):
        shard_count += 1
        shard_users = {int(row["uid"]) for row in rows}
        overlapping = shard_users & users_seen_in_prior_shards
        if overlapping:
            raise ValueError(
                "Hopwise sharded export repeats users across batches: "
                f"shard={shard_path}, users={sorted(overlapping)[:10]}"
            )
        users_seen_in_prior_shards.update(shard_users)
        raw_users.update(shard_users)
        raw_paths += len(rows)
        seen_path_keys = set()
        for row in rows:
            validated = validate_row(
                row, test_users=test_users, excluded=excluded
            )
            if validated is None:
                continue
            uid, pid, score, _path_prob, path = validated
            path_key = (uid, pid, tuple(path))
            if path_key in seen_path_keys:
                continue
            seen_path_keys.add(path_key)
            unseen_paths += 1
            candidate_users.add(uid)
            min_score = min(min_score, score)
            max_score = max(max_score, score)

    expected_raw_paths = raw.get("raw_paths")
    if expected_raw_paths is not None and raw_paths != int(expected_raw_paths):
        raise ValueError(
            "Hopwise shard row accounting mismatch: "
            f"manifest={expected_raw_paths}, loaded={raw_paths}"
        )
    if unseen_paths == 0:
        raise ValueError("No unseen Hopwise paths remain after canonical history filtering")

    denominator = max_score - min_score
    output_users = sorted(test_users if include_all_test_users else raw_users)
    uid_topk = {uid: [] for uid in output_users}
    uid_pid_best = {uid: {} for uid in output_users}
    finalized_users = set()
    output_dir = xrecsys_dir / "paths" / dataset / f"agent_topk={agent_topk_tag}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Second pass writes the large candidate table directly. Only the best
    # path per item for the users in one shard is held in memory.
    with (output_dir / "pred_paths.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "pid", "path_score", "path_prob", "path"])
        for shard_path, rows in load_shard_rows(raw_path, raw):
            best_by_user: dict[
                int, dict[int, tuple[float, float, str]]
            ] = {}
            seen_path_keys = set()
            for row in rows:
                validated = validate_row(
                    row, test_users=test_users, excluded=excluded
                )
                if validated is None:
                    continue
                uid, pid, score, path_prob, path = validated
                path_key = (uid, pid, tuple(path))
                if path_key in seen_path_keys:
                    continue
                seen_path_keys.add(path_key)
                path_string = format_path(path)
                normalized_score = (
                    (score - min_score) / denominator if denominator else 1.0
                )
                writer.writerow(
                    [uid, pid, normalized_score, path_prob, path_string]
                )
                current = best_by_user.setdefault(uid, {}).get(pid)
                candidate = (score, path_prob, path_string)
                if current is None or candidate[:2] > current[:2]:
                    best_by_user[uid][pid] = candidate

            for uid, item_paths in best_by_user.items():
                if uid in finalized_users:
                    raise ValueError(
                        f"Hopwise user {uid} was finalized by multiple shards"
                    )
                ranked_items = [
                    (pid, score, path_prob, path_string)
                    for pid, (score, path_prob, path_string) in item_paths.items()
                ]
                ranked_items.sort(
                    key=lambda value: (value[1], value[2], -value[0]),
                    reverse=True,
                )
                for pid, _score, _path_prob, path_string in ranked_items[:topk]:
                    uid_topk[uid].append(pid)
                    uid_pid_best[uid][pid] = path_string
                finalized_users.add(uid)

    with (output_dir / "uid_topk.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "top10"])
        for uid, pids in uid_topk.items():
            writer.writerow([uid, " ".join(str(pid) for pid in pids)])

    with (output_dir / "uid_pid_explanation.csv").open(
        "w", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "pid", "path"])
        for uid, pid_paths in uid_pid_best.items():
            for pid, path_string in pid_paths.items():
                writer.writerow([uid, pid, path_string])

    summary = {
        "status": "PASS",
        "dataset": dataset,
        "output_dir": str(output_dir),
        "raw_paths": raw_paths,
        "unseen_paths": unseen_paths,
        "raw_users": len(raw_users),
        "requested_users": requested_users,
        "processed_users": processed_users,
        "skipped_cold_start_users": len(skipped_cold_start_users),
        "output_users": len(uid_topk),
        "users_with_recommendations": sum(bool(items) for items in uid_topk.values()),
        "explanations": sum(len(paths) for paths in uid_pid_best.values()),
        "native_score_range": [min_score, max_score],
        "path_shards": shard_count,
    }
    print(summary)
    if summary_json is not None:
        summary_json.parent.mkdir(parents=True, exist_ok=True)
        summary_json.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return summary


def convert(
    *,
    raw_path: Path,
    xrecsys_dir: Path,
    labels_dir: Path,
    topk: int,
    agent_topk_tag: str,
    include_all_test_users: bool,
    summary_json: Path | None = None,
) -> dict:
    with raw_path.open("rb") as handle:
        raw = pickle.load(handle)

    if raw.get("row_shards"):
        return convert_sharded(
            raw_path=raw_path,
            raw=raw,
            xrecsys_dir=xrecsys_dir,
            labels_dir=labels_dir,
            topk=topk,
            agent_topk_tag=agent_topk_tag,
            include_all_test_users=include_all_test_users,
            summary_json=summary_json,
        )

    dataset = raw["canonical_dataset"]
    rows = raw["rows"]
    requested_users = int(raw.get("requested_users", raw.get("processed_users", 0)))
    processed_users = int(raw.get("processed_users", 0))
    skipped_cold_start_users = {
        int(uid) for uid in raw.get("skipped_cold_start_users", [])
    }
    excluded = load_train_labels(str(xrecsys_dir), dataset, labels_dir=str(labels_dir))
    test_users = load_test_users(labels_dir)

    if not skipped_cold_start_users.issubset(test_users):
        unexpected = sorted(skipped_cold_start_users - test_users)[:10]
        raise ValueError(f"Cold-start users outside canonical test labels: {unexpected}")
    if requested_users and requested_users != processed_users + len(skipped_cold_start_users):
        raise ValueError(
            "Hopwise raw user accounting mismatch: "
            f"requested={requested_users}, processed={processed_users}, "
            f"skipped={len(skipped_cold_start_users)}"
        )

    candidate_paths: dict[int, dict[int, list[tuple[float, float, list[tuple]]]]] = {}
    seen_path_keys = set()
    for row in rows:
        uid = int(row["uid"])
        pid = int(row["pid"])
        score = float(row["score"])
        path_prob = float(row["path_prob"])
        path = row["path"]

        if uid not in test_users:
            raise ValueError(f"Hopwise exported uid={uid} outside canonical test users")
        if not math.isfinite(score) or not math.isfinite(path_prob):
            raise ValueError(f"Non-finite Hopwise path confidence for uid={uid}, pid={pid}")
        if not 0.0 <= path_prob <= 1.0:
            raise ValueError(f"Out-of-range Hopwise path probability={path_prob}")
        if not path or path[0][1:] != ("user", uid) or path[-1][2] != pid:
            raise ValueError(f"Hopwise canonical path endpoint mismatch: uid={uid}, pid={pid}, path={path}")
        if pid in excluded.get(uid, set()):
            continue

        path_key = (uid, pid, tuple(path))
        if path_key in seen_path_keys:
            continue
        seen_path_keys.add(path_key)
        candidate_paths.setdefault(uid, {}).setdefault(pid, []).append((score, path_prob, path))

    raw_users = {int(row["uid"]) for row in rows}
    output_users = sorted(test_users if include_all_test_users else raw_users)
    uid_topk = {uid: [] for uid in output_users}
    uid_pid_best = {uid: {} for uid in output_users}

    unnormalized_rows = []
    for uid in output_users:
        ranked_items = []
        for pid, paths in candidate_paths.get(uid, {}).items():
            for score, path_prob, path in paths:
                unnormalized_rows.append((uid, pid, score, path_prob, format_path(path)))
            best = max(paths, key=lambda value: (value[0], value[1]))
            ranked_items.append((pid, best[0], best[1], best[2]))

        ranked_items.sort(key=lambda value: (value[1], value[2], -value[0]), reverse=True)
        for pid, _, _, path in ranked_items[:topk]:
            uid_topk[uid].append(pid)
            uid_pid_best[uid][pid] = format_path(path)

    if not unnormalized_rows:
        raise ValueError("No unseen Hopwise paths remain after canonical history filtering")
    min_score = min(row[2] for row in unnormalized_rows)
    max_score = max(row[2] for row in unnormalized_rows)
    denominator = max_score - min_score
    pred_rows = [
        (
            uid,
            pid,
            (score - min_score) / denominator if denominator else 1.0,
            path_prob,
            path,
        )
        for uid, pid, score, path_prob, path in unnormalized_rows
    ]

    output_dir = xrecsys_dir / "paths" / dataset / f"agent_topk={agent_topk_tag}"
    write_csvs(output_dir, pred_rows, uid_topk, uid_pid_best)
    summary = {
        "status": "PASS",
        "dataset": dataset,
        "output_dir": str(output_dir),
        "raw_paths": len(rows),
        "unseen_paths": len(pred_rows),
        "raw_users": len(raw_users),
        "requested_users": requested_users,
        "processed_users": processed_users,
        "skipped_cold_start_users": len(skipped_cold_start_users),
        "output_users": len(uid_topk),
        "users_with_recommendations": sum(bool(items) for items in uid_topk.values()),
        "explanations": sum(len(paths) for paths in uid_pid_best.values()),
        "native_score_range": [min_score, max_score],
    }
    print(summary)
    if summary_json is not None:
        summary_json.parent.mkdir(parents=True, exist_ok=True)
        summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-path", type=Path, required=True)
    parser.add_argument("--xrecsys-dir", type=Path, default=Path("xrecsys"))
    parser.add_argument("--labels-dir", type=Path, required=True)
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--agent-topk-tag", required=True)
    parser.add_argument("--include-all-test-users", action="store_true")
    parser.add_argument("--summary-json", type=Path)
    args = parser.parse_args()
    convert(
        raw_path=args.raw_path,
        xrecsys_dir=args.xrecsys_dir,
        labels_dir=args.labels_dir,
        topk=args.topk,
        agent_topk_tag=args.agent_topk_tag,
        include_all_test_users=args.include_all_test_users,
        summary_json=args.summary_json,
    )


if __name__ == "__main__":
    main()
