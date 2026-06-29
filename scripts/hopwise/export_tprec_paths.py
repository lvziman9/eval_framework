#!/usr/bin/env python3
"""Export validated canonical paths from a trained TPRec policy checkpoint."""

from __future__ import annotations

import argparse
import json
import math
import pickle
from functools import reduce
from pathlib import Path
from typing import Any

import numpy as np
import torch

from hopwise.config import Config
from hopwise.data import create_dataset, data_preparation
from hopwise.utils import get_model, init_seed

from scripts.hopwise.tprec_runtime import (
    build_tprec_config,
    install_tprec_runtime_patches,
)


DATASET_ALIASES = {
    "canonical_ml1m_v1": {
        "canonical_dataset": "ml1m",
        "product_type": "movie",
        "ui_relation": "watched",
    },
    "canonical_lastfm_v1": {
        "canonical_dataset": "lastfm",
        "product_type": "song",
        "ui_relation": "listened",
    },
    "canonical_amazon_book_kgat_v1": {
        "canonical_dataset": "amazon_book_kgat_v1",
        "product_type": "book",
        "ui_relation": "purchased",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASET_ALIASES), required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--policy-checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--shard-dir",
        type=Path,
        help="Write one atomic path shard per evaluation batch and resume existing shards.",
    )
    parser.add_argument("--summary-json", type=Path)
    parser.add_argument("--gpu-id", default="")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--beam-search-hop", type=int, nargs=3, default=(25, 50, 1))
    parser.add_argument("--max-users", type=int)
    parser.add_argument("--verify-determinism", action="store_true")
    return parser.parse_args()


def field_token(dataset, field: str, index: int) -> str:
    return str(dataset.field2id_token[field][int(index)])


def parse_entity_token(token: str) -> tuple[str, int]:
    entity_type, separator, raw_id = token.rpartition(":")
    if not separator or not entity_type:
        raise ValueError(f"Entity token has no semantic type prefix: {token!r}")
    return entity_type, int(raw_id)


def validate_internal_path(path, model) -> None:
    if len(path) != model.max_num_nodes:
        raise ValueError(f"TPRec path has unexpected length: {path}")
    if path[0][0] != "self_loop" or path[0][1] != "user":
        raise ValueError(f"TPRec path has invalid origin: {path}")
    if not model._has_pattern(path):
        raise ValueError(f"TPRec path violates configured native pattern: {path}")

    for previous, current in zip(path, path[1:]):
        relation, current_type, current_id = current
        if relation == "self_loop":
            raise ValueError(f"TPRec exported a self-loop continuation: {path}")
        previous_type, previous_id = previous[1], int(previous[2])
        current_id = int(current_id)
        try:
            neighbors = model.graph_dict[previous_type][previous_id][int(relation)]
        except KeyError as error:
            raise ValueError(f"TPRec path edge is absent from graph: {previous} -> {current}") from error
        if current_id not in neighbors:
            raise ValueError(f"TPRec path edge is absent from graph: {previous} -> {current}")
        expected_type = model._get_next_node_type(previous_type, int(relation))
        if current_type != expected_type:
            raise ValueError(
                f"TPRec node type mismatch: expected={expected_type}, actual={current_type}"
            )


def canonicalize_path(path, dataset, aliases) -> list[tuple[str, str, int]]:
    canonical = []
    for relation, node_type, node_id in path:
        if relation == "self_loop":
            relation_name = "self_loop"
        else:
            relation_name = field_token(dataset, dataset.relation_field, int(relation))
            if relation_name == dataset.ui_relation:
                relation_name = aliases["ui_relation"]

        node_id = int(node_id)
        if node_type == "user":
            canonical_type = "user"
            canonical_id = int(field_token(dataset, dataset.uid_field, node_id))
        elif node_type == "entity" and node_id < dataset.item_num:
            canonical_type = aliases["product_type"]
            canonical_id = int(field_token(dataset, dataset.iid_field, node_id))
        elif node_type == "entity":
            canonical_type, canonical_id = parse_entity_token(
                field_token(dataset, dataset.entity_field, node_id)
            )
        else:
            raise ValueError(f"Unsupported TPRec node type: {node_type!r}")
        canonical.append((relation_name, canonical_type, canonical_id))
    return canonical


def write_pickle_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    temporary.replace(path)


def validate_resumable_shard(
    payload: dict,
    *,
    dataset: str,
    policy_checkpoint: Path,
    beam_search_hop: tuple[int, ...],
    batch_index: int,
    max_users: int | None,
) -> None:
    expected = {
        "schema_version": 1,
        "dataset": dataset,
        "policy_checkpoint": str(policy_checkpoint.resolve()),
        "beam_search_hop": list(beam_search_hop),
        "batch_index": batch_index,
        "max_users": max_users,
    }
    mismatches = {
        key: (expected_value, payload.get(key))
        for key, expected_value in expected.items()
        if payload.get(key) != expected_value
    }
    if mismatches:
        raise ValueError(f"TPRec resume shard metadata mismatch: {mismatches}")
    if not isinstance(payload.get("rows"), list):
        raise ValueError(f"TPRec resume shard has no row list: batch={batch_index}")


def canonical_cold_start_user(uid: int, dataset) -> int:
    return int(field_token(dataset, dataset.uid_field, uid))


def convert_generated_paths(
    *,
    paths,
    probabilities,
    expected_users: set[int],
    model,
    dataset,
    aliases: dict,
    temporal_matrix: np.ndarray,
) -> tuple[dict[int, list[dict]], dict[int, int]]:
    rows_by_user = {uid: [] for uid in expected_users}
    positive_reward_paths = {uid: 0 for uid in expected_users}
    for path, probability_steps in zip(paths, probabilities):
        if "self_loop" in [node[0] for node in path[1:]]:
            continue
        if path[-1][1] != "entity" or int(path[-1][2]) >= model.n_items:
            continue
        if not model._has_pattern(path):
            continue
        validate_internal_path(path, model)
        if any(not 0.0 <= float(value) <= 1.0 for value in probability_steps):
            raise ValueError(
                "TPRec emitted out-of-range native probabilities: "
                f"{probability_steps}"
            )

        internal_uid = int(path[0][2])
        if internal_uid not in expected_users:
            raise ValueError(
                f"TPRec batched beam returned unexpected user {internal_uid}"
            )
        internal_pid = int(path[-1][2])
        native_score = float(
            np.dot(
                model.user_embedding[internal_uid] + temporal_matrix[internal_uid],
                model.entity_embedding[internal_pid],
            )
        )
        path_probability = float(
            reduce(lambda left, right: left * right, probability_steps, 1.0)
        )
        if not math.isfinite(native_score) or not math.isfinite(path_probability):
            raise ValueError("TPRec emitted a non-finite path confidence")
        if model._get_reward(path) > 0.0:
            positive_reward_paths[internal_uid] += 1

        canonical_path = canonicalize_path(path, dataset, aliases)
        rows_by_user[internal_uid].append(
            {
                "uid": canonical_path[0][2],
                "pid": canonical_path[-1][2],
                "score": native_score,
                "path_prob": path_probability,
                "path": canonical_path,
            }
        )
    return rows_by_user, positive_reward_paths


def main() -> None:
    args = parse_args()
    if not args.policy_checkpoint.is_file():
        raise FileNotFoundError(args.policy_checkpoint)
    policy_checkpoint = args.policy_checkpoint.resolve()
    pretrained = args.checkpoint_dir / f"TPRec-{args.dataset}-pretrained.pth"
    if not pretrained.is_file():
        raise FileNotFoundError(
            f"TPRec policy construction requires the installed pretrain checkpoint: {pretrained}"
        )

    install_tprec_runtime_patches()
    config = Config(
        model="TPRec",
        dataset=args.dataset,
        config_dict=build_tprec_config(
            dataset=args.dataset,
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id=args.gpu_id,
            train_stage="policy",
            epochs=1,
            train_batch_size=64,
            eval_batch_size=args.batch_size,
            beam_search_hop=tuple(args.beam_search_hop),
        ),
    )
    init_seed(config["seed"], config["reproducibility"])
    dataset = create_dataset(config)
    train_data, _, test_data = data_preparation(config, dataset)
    model = get_model("TPRec")(config, train_data.dataset)
    checkpoint = torch.load(
        args.policy_checkpoint,
        weights_only=False,
        map_location="cpu",
    )
    incompatible = model.load_state_dict(checkpoint["state_dict"], strict=False)
    if incompatible.missing_keys or incompatible.unexpected_keys:
        raise ValueError(
            f"TPRec policy checkpoint mismatch: missing={incompatible.missing_keys}, "
            f"unexpected={incompatible.unexpected_keys}"
        )
    model = model.to(config["device"])
    model.eval()

    aliases = DATASET_ALIASES[args.dataset]
    temporal_matrix = np.concatenate(
        (
            np.zeros((1, model.embedding_size), dtype=model.user_embedding.dtype),
            np.asarray(model._build_interacted_matrix(test_data.temporal_weights)),
        ),
        axis=0,
    )
    if temporal_matrix.shape != model.user_embedding.shape:
        raise AssertionError(
            f"TPRec temporal matrix shape mismatch: "
            f"{temporal_matrix.shape} != {model.user_embedding.shape}"
        )

    rows = [] if args.shard_dir is None else None
    row_shards = []
    requested_users = 0
    processed_users = 0
    skipped_cold_start_users = []
    positive_reward_paths = 0
    determinism_checked = False
    raw_path_count = 0
    raw_users = set()
    min_native_score = math.inf
    max_native_score = -math.inf
    min_path_probability = math.inf
    max_path_probability = -math.inf
    if args.shard_dir is not None:
        args.shard_dir.mkdir(parents=True, exist_ok=True)

    test_user_ids = [int(uid) for uid in test_data.uid_list]
    if args.max_users is not None:
        test_user_ids = test_user_ids[: args.max_users]

    for group_start in range(0, len(test_user_ids), args.batch_size):
        indexed_users = list(
            enumerate(
                test_user_ids[group_start : group_start + args.batch_size],
                start=group_start,
            )
        )
        payload_by_index = {}
        pending_users = []

        for user_index, uid in indexed_users:
            shard_path = (
                args.shard_dir / f"batch_{user_index:06d}.pkl"
                if args.shard_dir is not None
                else None
            )
            if shard_path is None or not shard_path.is_file():
                pending_users.append((user_index, uid, shard_path))
                continue

            with shard_path.open("rb") as handle:
                shard_payload = pickle.load(handle)
            validate_resumable_shard(
                shard_payload,
                dataset=args.dataset,
                policy_checkpoint=policy_checkpoint,
                beam_search_hop=tuple(args.beam_search_hop),
                batch_index=user_index,
                max_users=args.max_users,
            )
            if shard_payload.get("internal_users") != [uid]:
                raise ValueError(
                    "TPRec resume shard user order mismatch: "
                    f"batch={user_index}, expected={[uid]}, "
                    f"actual={shard_payload.get('internal_users')}"
                )
            payload_by_index[user_index] = shard_payload

        if pending_users:
            pending_user_ids = [uid for _, uid, _ in pending_users]
            users = torch.tensor(pending_user_ids, dtype=torch.long)
            paths, probabilities = model.beam_search(users)
            group_determinism_checked = False
            if args.verify_determinism and not determinism_checked:
                repeated_paths, repeated_probabilities = model.beam_search(users)
                if repeated_paths != paths:
                    raise AssertionError("TPRec eval-mode beam paths are not deterministic")
                if len(repeated_probabilities) != len(probabilities):
                    raise AssertionError("TPRec deterministic probability row count changed")
                for first, second in zip(probabilities, repeated_probabilities):
                    if not np.allclose(first, second, rtol=0.0, atol=0.0):
                        raise AssertionError(
                            "TPRec eval-mode beam probabilities are not deterministic"
                        )
                group_determinism_checked = True

            rows_by_user, positive_by_user = convert_generated_paths(
                paths=paths,
                probabilities=probabilities,
                expected_users=set(pending_user_ids),
                model=model,
                dataset=train_data.dataset,
                aliases=aliases,
                temporal_matrix=temporal_matrix,
            )
            for pending_position, (user_index, uid, shard_path) in enumerate(
                pending_users
            ):
                cold_start_users = (
                    [canonical_cold_start_user(uid, train_data.dataset)]
                    if uid not in model.graph_dict["user"]
                    else []
                )
                shard_payload = {
                    "schema_version": 1,
                    "dataset": args.dataset,
                    "policy_checkpoint": str(policy_checkpoint),
                    "beam_search_hop": list(args.beam_search_hop),
                    "batch_index": user_index,
                    "max_users": args.max_users,
                    "internal_users": [uid],
                    "native_cold_start_users": cold_start_users,
                    "positive_reward_paths": positive_by_user[uid],
                    "determinism_checked": (
                        group_determinism_checked and pending_position == 0
                    ),
                    "rows": rows_by_user[uid],
                }
                if shard_path is not None:
                    write_pickle_atomic(shard_path, shard_payload)
                payload_by_index[user_index] = shard_payload

        for user_index, _uid in indexed_users:
            shard_payload = payload_by_index[user_index]
            batch_rows = shard_payload["rows"]
            batch_cold_start_users = shard_payload["native_cold_start_users"]
            batch_positive_reward_paths = int(
                shard_payload["positive_reward_paths"]
            )
            batch_determinism_checked = bool(
                shard_payload["determinism_checked"]
            )
            shard_path = (
                args.shard_dir / f"batch_{user_index:06d}.pkl"
                if args.shard_dir is not None
                else None
            )

            if rows is not None:
                rows.extend(batch_rows)
            else:
                row_shards.append(shard_path.resolve())
            requested_users += 1
            processed_users += 1
            skipped_cold_start_users.extend(batch_cold_start_users)
            positive_reward_paths += batch_positive_reward_paths
            determinism_checked = determinism_checked or batch_determinism_checked
            raw_path_count += len(batch_rows)
            raw_users.update(int(row["uid"]) for row in batch_rows)
            if batch_rows:
                min_native_score = min(
                    min_native_score,
                    min(float(row["score"]) for row in batch_rows),
                )
                max_native_score = max(
                    max_native_score,
                    max(float(row["score"]) for row in batch_rows),
                )
                min_path_probability = min(
                    min_path_probability,
                    min(float(row["path_prob"]) for row in batch_rows),
                )
                max_path_probability = max(
                    max_path_probability,
                    max(float(row["path_prob"]) for row in batch_rows),
                )

        print(
            f"requested_users={requested_users} processed_users={processed_users} "
            f"cold_start_users={len(skipped_cold_start_users)} "
            f"raw_paths={raw_path_count} group_start={group_start} "
            f"group_users={len(indexed_users)} generated_users={len(pending_users)}",
            flush=True,
        )

    if raw_path_count == 0:
        raise ValueError("TPRec generated no valid native item-ending paths")
    if positive_reward_paths == 0:
        raise ValueError("TPRec generated no path with a positive temporal reward")

    skipped_cold_start_users = sorted(set(skipped_cold_start_users))
    raw_payload = {
        "schema_version": 2 if row_shards else 1,
        "model": "TPRec",
        "source_dataset": args.dataset,
        "canonical_dataset": aliases["canonical_dataset"],
        "beam_search_hop": list(args.beam_search_hop),
        "requested_users": requested_users,
        "processed_users": processed_users,
        # TPRec still processes these users into self-loop-only beams;
        # record them for audit but do not subtract them from processed.
        "skipped_cold_start_users": [],
        "native_cold_start_users": skipped_cold_start_users,
        "raw_paths": raw_path_count,
        "raw_users": len(raw_users),
    }
    if row_shards:
        raw_payload["row_shards"] = [str(path) for path in row_shards]
    else:
        raw_payload["rows"] = rows
    write_pickle_atomic(args.output, raw_payload)

    summary = {
        "status": "PASS",
        "model": "TPRec",
        "dataset": args.dataset,
        "checkpoint": str(args.policy_checkpoint),
        "beam_search_hop": list(args.beam_search_hop),
        "requested_users": requested_users,
        "processed_users": processed_users,
        "native_cold_start_users": len(skipped_cold_start_users),
        "raw_paths": raw_path_count,
        "raw_users": len(raw_users),
        "path_shards": len(row_shards),
        "positive_reward_paths": positive_reward_paths,
        "determinism_checked": determinism_checked,
        "native_score_range": [min_native_score, max_native_score],
        "path_probability_range": [
            min_path_probability,
            max_path_probability,
        ],
    }
    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(summary)


if __name__ == "__main__":
    main()
