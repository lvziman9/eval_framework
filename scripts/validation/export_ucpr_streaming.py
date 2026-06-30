#!/usr/bin/env python3
"""Run UCPR beam inference and export xrecsys CSVs without giant pickles."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import pickle
import sys
from datetime import datetime, timezone
from functools import reduce
from operator import mul
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np


RELATION_ALIASES = {
    "amazon_book_kgat_v1": {
        "book_author_entity": "book_author",
        "book_character_entity": "book_character",
        "book_genre_entity": "book_genre",
        "book_interior_illustration_entity": "book_interior_illustration",
        "book_next_in_series_entity": "book_next_in_series",
        "book_original_language_entity": "book_original_language",
        "book_part_of_series_entity": "book_part_of_series",
        "book_previous_in_series_entity": "book_previous_in_series",
        "book_subject_entity": "book_subject",
        "purchase": "purchased",
    },
}

ENTITY_ALIASES = {
    "amazon_book_kgat_v1": {
        "product": "book",
    },
}


def load_label_sets(path: Path) -> dict[int, set[int]]:
    with path.open("rb") as handle:
        raw = pickle.load(handle)
    return {int(uid): {int(pid) for pid in pids} for uid, pids in raw.items()}


def load_remap(path: Path, source_column: str, target_column: str) -> dict[int, int]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = set(reader.fieldnames or [])
        expected = {source_column, target_column}
        if not expected.issubset(fields):
            raise ValueError(f"{path} columns={reader.fieldnames}, expected={sorted(expected)}")
        return {int(row[target_column]): int(row[source_column]) for row in reader}


def format_path(path_tuples) -> str:
    return " ".join(str(part) for triple in path_tuples for part in triple)


def convert_path(path_tuples, uid_map: dict[int, int], pid_map: dict[int, int], dataset: str):
    converted = []
    for rel, etype, eid in path_tuples:
        rel = RELATION_ALIASES[dataset].get(rel, rel)
        etype = ENTITY_ALIASES[dataset].get(etype, etype)
        if etype == "book":
            eid = pid_map.get(int(eid))
        elif etype == "user":
            eid = uid_map.get(int(eid))
        else:
            eid = int(eid)
        if eid is None:
            return None
        converted.append((rel, etype, eid))
    return converted


def native_path_probability(probs) -> float:
    values = np.asarray(probs, dtype=float)
    if values.size == 0:
        return 1.0
    if float(np.max(values)) > 1.0:
        values = values - 1.0
    if np.any(values < -1e-6) or np.any(values > 1.0 + 1e-6):
        raise ValueError(f"Invalid UCPR action probabilities: {values}")
    values = np.clip(values, 0.0, 1.0)
    return float(np.prod(values))


def to_jsonable(value: Any):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        return to_jsonable(value.item())
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    return str(value)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(payload), indent=2, sort_keys=True) + "\n")


def build_ucpr_args(args) -> SimpleNamespace:
    return SimpleNamespace(
        dataset=args.dataset,
        name=args.run_name,
        model="UCPR",
        seed=52,
        p_hop=1,
        gpu=str(args.gpu),
        epochs=args.epoch,
        batch_size=128,
        sub_batch_size=1,
        n_memory=32,
        lr=7e-5,
        l2_lambda=0,
        max_acts=args.max_acts,
        max_path_len=3,
        gamma=0.99,
        ent_weight=1e-3,
        reasoning_step=3,
        pretrained_st_epoch=0,
        att_core=0,
        user_core_th=6,
        grad_check=False,
        embed_size=args.embed_size,
        act_dropout=0.5,
        state_history=1,
        hidden=args.hidden,
        gradient_plot="gradient_plot/",
        best_save_model_dir="",
        reward_hybrid=False,
        reward_rh="",
        test_lstm_up=True,
        h0_embbed=0,
        training=False,
        load_pretrain_model=False,
        att_evaluation=False,
        state_rg=False,
        kg_emb_grad=False,
        save_pretrain_model=False,
        mv_test=False,
        env_old=False,
        kg_old=False,
        tri_wd_rm=False,
        tri_pro_rm=False,
        l2_weight=1e-6,
        sam_type="alet",
        topk=args.topk,
        beam_batch_size=args.beam_batch_size,
        run_path=True,
        run_eval=False,
        save_paths=False,
        pretest=False,
        item_core=10,
        user_core=300,
        best_model_epoch=args.epoch,
        kg_fre_lower=15,
        kg_fre_upper=500,
        lambda_num=0.5,
        non_sampling=False,
        gp_setting="6000_800_15_500_50",
        kg_no_grad=False,
        sort_by="prob",
        eva_epochs=args.epoch,
        KGE_pretrained=True,
        load_pt_emb_size=False,
        user_o=False,
        add_products=False,
        do_validation=True,
        early_stop_patience=0,
        early_stop_min_delta=0.0,
        early_stop_metric="avg_valid_reward",
        wandb=False,
        wandb_entity=None,
        policy_path=str(args.policy_path),
    )


def batch_beam_search(ucpr_args, env, model, uids, device, topk):
    import torch
    from models.UCPR.utils import KG_RELATION, SELF_LOOP

    def batch_acts_to_masks(batch_acts):
        batch_masks = []
        for acts in batch_acts:
            num_acts = len(acts)
            act_mask = np.zeros(model.act_dim, dtype=np.uint8)
            act_mask[:num_acts] = 1
            batch_masks.append(act_mask)
        return np.vstack(batch_masks)

    env.reset(ucpr_args.epochs, uids)
    model.reset(uids)
    path_pool = env._batch_path
    probs_pool = [[] for _ in uids]
    index_ori_list = list(range(len(uids)))
    idx_list = list(range(len(uids)))
    model.eval()

    for hop in range(3):
        acts_pool = env._batch_get_actions(path_pool, False)
        actmask_pool = batch_acts_to_masks(acts_pool)
        state_tensor = model.generate_st_emb(path_pool, up_date_hop=idx_list)
        batch_next_action_emb = model.generate_act_emb(path_pool, acts_pool)
        actmask_tensor = torch.BoolTensor(actmask_pool).to(device)
        try:
            next_enti_emb, next_action_emb = batch_next_action_emb[0], batch_next_action_emb[1]
            probs, _ = model(
                (
                    state_tensor[0],
                    state_tensor[1],
                    next_enti_emb,
                    next_action_emb,
                    actmask_tensor,
                )
            )
        except TypeError:
            probs, _ = model((state_tensor, batch_next_action_emb, actmask_tensor))

        selection_probs = probs + actmask_tensor.float()
        _, topk_idxs = torch.topk(selection_probs, topk[hop], dim=1)
        topk_probs = torch.gather(probs, 1, topk_idxs)
        del actmask_tensor, selection_probs
        topk_idxs = topk_idxs.detach().cpu().numpy()
        topk_probs = topk_probs.detach().cpu().numpy()

        new_path_pool, new_probs_pool, new_index_pool, new_idx = [], [], [], []
        for row in range(topk_idxs.shape[0]):
            path = path_pool[row]
            path_probs = probs_pool[row]
            index_ori = index_ori_list[row]
            for idx, probability in zip(topk_idxs[row], topk_probs[row]):
                if idx >= len(acts_pool[row]):
                    continue
                relation, next_node_id = acts_pool[row][idx]
                if relation == SELF_LOOP:
                    next_node_type = path[-1][1]
                else:
                    next_node_type = KG_RELATION[ucpr_args.dataset][path[-1][1]][relation]
                new_path_pool.append(path + [(relation, next_node_type, next_node_id)])
                new_probs_pool.append(path_probs + [probability])
                new_index_pool.append(index_ori)
                new_idx.append(row)
        path_pool = new_path_pool
        probs_pool = new_probs_pool
        index_ori_list = new_index_pool
        idx_list = new_idx

    return path_pool, probs_pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", default="amazon_book_kgat_v1")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--policy-path", required=True)
    parser.add_argument("--labels-dir", required=True)
    parser.add_argument("--user-remap", required=True)
    parser.add_argument("--product-remap", required=True)
    parser.add_argument("--paths-dir", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--embed-size", type=int, default=100)
    parser.add_argument("--max-acts", type=int, default=50)
    parser.add_argument("--beam-batch-size", type=int, default=4)
    parser.add_argument("--topk", type=int, nargs=3, default=[25, 5, 1])
    parser.add_argument("--recommendation-topk", type=int, default=10)
    parser.add_argument("--hidden", type=int, nargs=2, default=[64, 32])
    parser.add_argument("--num-users", type=int, default=0)
    parser.add_argument("--keep-raw-temp", action="store_true")
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    pgm_root = runtime_root / "models" / "UCPR"
    policy_path = Path(args.policy_path).resolve()
    labels_dir = Path(args.labels_dir).resolve()
    paths_dir = Path(args.paths_dir).resolve()
    summary_json = Path(args.summary_json).resolve()
    paths_dir.mkdir(parents=True, exist_ok=True)

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    os.chdir(pgm_root)
    sys.path.insert(0, str(runtime_root))

    import torch
    from models.UCPR.preprocess.dataset import Dataset
    from models.UCPR.src.env.env import BatchKGEnvironment
    from models.UCPR.src.model.UCPR import UCPR
    from models.UCPR.src.para_setting import parameter_path
    from models.UCPR.utils import (
        MAIN_PRODUCT_INTERACTION,
        USER,
        load_embed,
        load_labels,
    )

    if not policy_path.exists():
        raise FileNotFoundError(policy_path)

    ucpr_args = build_ucpr_args(args)
    ucpr_args.device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
    if ucpr_args.device.type != "cuda":
        raise RuntimeError("UCPR streaming export requires CUDA because the UCPR model uses .cuda() modules.")
    parameter_path(ucpr_args)

    uid_map = load_remap(Path(args.user_remap), "canonical_uid", "ucpr_uid")
    pid_map = load_remap(Path(args.product_remap), "canonical_pid", "ucpr_product_idx")
    canonical_test_users = sorted(load_label_sets(labels_dir / "test_label.pkl"))

    train_labels = load_labels(args.dataset, "train")
    valid_labels = load_labels(args.dataset, "valid")
    test_labels = load_labels(args.dataset, "test")

    dataset = Dataset(ucpr_args)
    env = BatchKGEnvironment(ucpr_args, dataset, ucpr_args.max_acts, max_path_len=3, state_history=1)
    model = UCPR(
        ucpr_args,
        env.user_triplet_set,
        env.rela_2_index,
        env.act_dim,
        gamma=ucpr_args.gamma,
        hidden_sizes=ucpr_args.hidden,
    ).to(ucpr_args.device)
    pretrained = torch.load(policy_path, map_location=ucpr_args.device)
    model_state = model.state_dict()
    model_state.update(pretrained)
    model.load_state_dict(model_state)
    model.eval()

    embeds = load_embed(args.dataset)
    main_product, main_interaction = MAIN_PRODUCT_INTERACTION[args.dataset]
    user_embeddings = embeds[USER]
    product_embeddings = embeds[main_product]
    interaction_embedding = embeds[main_interaction][0]
    score_cache: dict[int, dict[int, float]] = {}

    def item_score(uid: int, pid: int) -> float:
        user_scores = score_cache.setdefault(uid, {})
        if pid not in user_scores:
            user_scores[pid] = float(
                np.dot(user_embeddings[uid] + interaction_embedding, product_embeddings[pid])
            )
        return user_scores[pid]

    test_uids = [
        int(uid)
        for uid in sorted(test_labels)
        if uid in train_labels and uid in env.user_list and int(uid) in uid_map
    ]
    if args.num_users > 0:
        test_uids = test_uids[: args.num_users]
    output_users = sorted(uid_map[int(uid)] for uid in test_uids)
    if args.num_users == 0:
        output_users = canonical_test_users

    raw_tmp = paths_dir / "pred_paths.raw.tmp.csv"
    pred_tmp = paths_dir / "pred_paths.csv.tmp"
    uid_tmp = paths_dir / "uid_topk.csv.tmp"
    explanation_tmp = paths_dir / "uid_pid_explanation.csv.tmp"
    top_candidates: dict[int, dict[int, tuple[float, float, str]]] = {}
    min_score = math.inf
    max_score = -math.inf
    raw_rows = 0
    valid_path_count = 0
    skipped_non_product = 0
    skipped_seen = 0
    skipped_unmapped = 0
    processed_users = 0

    start_payload = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "stage": "beam_stream",
        "runtime_root": str(runtime_root),
        "policy_path": str(policy_path),
        "paths_dir": str(paths_dir),
        "labels_dir": str(labels_dir),
        "topk": args.topk,
        "recommendation_topk": args.recommendation_topk,
        "beam_batch_size": args.beam_batch_size,
        "num_users_limit": args.num_users,
        "canonical_test_users": len(canonical_test_users),
        "eligible_test_users": len(test_uids),
        "output_users": len(output_users),
        "act_dim": env.act_dim,
        "device": str(ucpr_args.device),
    }
    write_json(summary_json, start_payload)

    with raw_tmp.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "pid", "raw_score", "path_prob", "path"])
        for start in range(0, len(test_uids), args.beam_batch_size):
            batch_uids = test_uids[start : start + args.beam_batch_size]
            paths, probs = batch_beam_search(
                ucpr_args,
                env,
                model,
                batch_uids,
                ucpr_args.device,
                args.topk,
            )
            processed_users += len(batch_uids)
            for path_tuples, prob_list in zip(paths, probs):
                if not path_tuples or path_tuples[-1][1] != main_product:
                    skipped_non_product += 1
                    continue
                uid = int(path_tuples[0][2])
                pid = int(path_tuples[-1][2])
                if uid not in test_labels:
                    continue
                if uid in valid_labels and pid in valid_labels[uid]:
                    skipped_seen += 1
                    continue
                if pid in train_labels.get(uid, set()):
                    skipped_seen += 1
                    continue
                converted = convert_path(path_tuples, uid_map, pid_map, args.dataset)
                if converted is None:
                    skipped_unmapped += 1
                    continue
                canonical_uid = int(converted[0][2])
                canonical_pid = int(converted[-1][2])
                score = item_score(uid, pid)
                path_prob = native_path_probability(prob_list)
                path_str = format_path(converted)
                writer.writerow([canonical_uid, canonical_pid, score, path_prob, path_str])
                raw_rows += 1
                valid_path_count += 1
                min_score = min(min_score, score)
                max_score = max(max_score, score)

                user_top = top_candidates.setdefault(canonical_uid, {})
                current = user_top.get(canonical_pid)
                if current is not None:
                    if path_prob > current[1]:
                        user_top[canonical_pid] = (score, path_prob, path_str)
                    continue
                if len(user_top) < args.recommendation_topk:
                    user_top[canonical_pid] = (score, path_prob, path_str)
                    continue
                worst_pid, worst = min(
                    user_top.items(), key=lambda row: (row[1][0], row[1][1])
                )
                if (score, path_prob) > (worst[0], worst[1]):
                    del user_top[worst_pid]
                    user_top[canonical_pid] = (score, path_prob, path_str)

            if processed_users % max(args.beam_batch_size * 50, 1) == 0:
                progress = {
                    **start_payload,
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "processed_users": processed_users,
                    "raw_candidate_rows": raw_rows,
                    "candidate_users": len(top_candidates),
                    "stage": "beam_stream",
                    "status": "RUNNING",
                }
                write_json(summary_json, progress)
                print(
                    f"processed_users={processed_users} raw_rows={raw_rows} "
                    f"candidate_users={len(top_candidates)}",
                    flush=True,
                )
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

    if valid_path_count == 0:
        raise ValueError("UCPR produced no unseen product-ending candidate paths.")
    score_range = max_score - min_score if max_score != min_score else 1.0
    with raw_tmp.open(newline="") as source, pred_tmp.open("w", newline="") as target:
        reader = csv.DictReader(source)
        writer = csv.writer(target)
        writer.writerow(["uid", "pid", "path_score", "path_prob", "path"])
        for row in reader:
            score = float(row["raw_score"])
            writer.writerow(
                [
                    row["uid"],
                    row["pid"],
                    (score - min_score) / score_range,
                    row["path_prob"],
                    row["path"],
                ]
            )

    uid_topk = {uid: [] for uid in output_users}
    uid_pid_best = {uid: {} for uid in output_users}
    for uid, pid_candidates in top_candidates.items():
        top_items = sorted(
            (
                (pid, score, path_prob, path_str)
                for pid, (score, path_prob, path_str) in pid_candidates.items()
            ),
            key=lambda row: (row[1], row[2]),
            reverse=True,
        )
        uid_topk[uid] = [pid for pid, _, _, _ in top_items]
        uid_pid_best[uid] = {pid: path_str for pid, _, _, path_str in top_items}

    with uid_tmp.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "top10"])
        for uid in output_users:
            writer.writerow([uid, " ".join(str(pid) for pid in uid_topk[uid])])

    with explanation_tmp.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["uid", "pid", "path"])
        for uid in output_users:
            for pid, path_str in uid_pid_best[uid].items():
                writer.writerow([uid, pid, path_str])

    pred_tmp.replace(paths_dir / "pred_paths.csv")
    uid_tmp.replace(paths_dir / "uid_topk.csv")
    explanation_tmp.replace(paths_dir / "uid_pid_explanation.csv")
    if not args.keep_raw_temp and raw_tmp.exists():
        raw_tmp.unlink()

    recommendation_counts = [len(uid_topk[uid]) for uid in output_users]
    summary = {
        **start_payload,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "stage": "complete",
        "processed_users": processed_users,
        "raw_candidate_rows": raw_rows,
        "valid_path_count": valid_path_count,
        "candidate_users": len(top_candidates),
        "topk_users": len(uid_topk),
        "empty_users": sum(1 for count in recommendation_counts if count == 0),
        "short_users": sum(1 for count in recommendation_counts if count < args.recommendation_topk),
        "min_recommendations": min(recommendation_counts),
        "max_recommendations": max(recommendation_counts),
        "mean_recommendations": sum(recommendation_counts) / len(recommendation_counts),
        "slot_coverage": sum(recommendation_counts)
        / (len(recommendation_counts) * args.recommendation_topk),
        "skipped_non_product_endpoints": skipped_non_product,
        "skipped_seen_items": skipped_seen,
        "skipped_unmapped_paths": skipped_unmapped,
        "score_range": [min_score, max_score],
        "cached_native_item_scores": sum(len(values) for values in score_cache.values()),
        "outputs": {
            "pred_paths": str(paths_dir / "pred_paths.csv"),
            "uid_topk": str(paths_dir / "uid_topk.csv"),
            "uid_pid_explanation": str(paths_dir / "uid_pid_explanation.csv"),
        },
    }
    write_json(summary_json, summary)
    print(json.dumps(to_jsonable(summary), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
