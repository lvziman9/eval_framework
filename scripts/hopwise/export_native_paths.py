#!/usr/bin/env python3
"""Export PEARLM/KGGLM native generated paths from a trained checkpoint."""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import torch
from safetensors.torch import load_file

from hopwise.config import Config
from hopwise.data import create_dataset, data_preparation
from hopwise.utils import get_model, init_seed

from scripts.hopwise.canonical_config import build_kgglm_config, build_pearlm_config
from scripts.hopwise.smoke_prepare_native_path import (
    install_bounded_logits_mask_cache,
    install_cumulative_score_alignment,
    install_kgglm_serial_sampler,
    install_sparse_relation_lookup,
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
    parser.add_argument("--model", choices=("PEARLM", "KGGLM"), required=True)
    parser.add_argument("--dataset", choices=sorted(DATASET_ALIASES), required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu-id", default="0")
    parser.add_argument("--embedding-size", type=int, required=True)
    parser.add_argument("--num-heads", type=int, required=True)
    parser.add_argument("--num-layers", type=int, required=True)
    parser.add_argument(
        "--pre-model-path",
        type=Path,
        help="KGGLM generic pretraining checkpoint used to construct the finetune model.",
    )
    parser.add_argument("--paths-per-user", type=int, default=25)
    parser.add_argument("--num-beams", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-users", type=int)
    parser.add_argument(
        "--shard-dir",
        type=Path,
        help="Optional atomic per-batch shard directory for resumable full export.",
    )
    return parser.parse_args()


def field_token(dataset, field: str, index: int) -> str:
    return str(dataset.field2id_token[field][int(index)])


def parse_entity_token(token: str) -> tuple[str, int]:
    entity_type, separator, raw_id = token.rpartition(":")
    if not separator or not entity_type:
        raise ValueError(f"Entity token has no semantic type prefix: {token!r}")
    return entity_type, int(raw_id)


def internal_kg_edges(dataset) -> set[tuple[int, int, int]]:
    heads = dataset.kg_feat[dataset.head_entity_field].tolist()
    relations = dataset.kg_feat[dataset.relation_field].tolist()
    tails = dataset.kg_feat[dataset.tail_entity_field].tolist()
    return {(int(head), int(relation), int(tail)) for head, relation, tail in zip(heads, relations, tails)}


def validate_internal_path(path, dataset, train_used_ids, kg_edges, ui_relation_id) -> None:
    if not path or path[0][1] != "user" or path[-1][1] != "item":
        raise ValueError(f"Invalid PEARLM path endpoints: {path}")

    for previous, current in zip(path, path[1:]):
        relation = current[0]
        if not isinstance(relation, int):
            raise ValueError(f"Non-integer relation inside path: {current}")
        previous_type, previous_id = previous[1], int(previous[2])
        current_type, current_id = current[1], int(current[2])

        if {previous_type, current_type} == {"user", "item"}:
            if relation != ui_relation_id:
                raise ValueError(f"User-item edge has non-UI relation: {previous} -> {current}")
            user_id = previous_id if previous_type == "user" else current_id
            item_id = previous_id if previous_type == "item" else current_id
            if item_id not in train_used_ids[user_id]:
                raise ValueError(f"Generated collaborative edge is absent from train: user={user_id}, item={item_id}")
            continue

        if "user" in {previous_type, current_type}:
            raise ValueError(f"Unsupported non-item user edge: {previous} -> {current}")

        edge = (previous_id, relation, current_id)
        reverse_edge = (current_id, relation, previous_id)
        if edge not in kg_edges and reverse_edge not in kg_edges:
            raise ValueError(f"Generated edge is absent from KG: {previous} -> {current}")


def canonicalize_path(path, dataset, aliases) -> list[tuple[str, str, int]]:
    canonical = []
    for relation, node_type, node_id in path:
        if relation == "self_loop":
            relation_name = "self_loop"
        else:
            relation_name = field_token(dataset, dataset.relation_field, int(relation))
            if relation_name == dataset.ui_relation:
                relation_name = aliases["ui_relation"]

        if node_type == "user":
            canonical_type = "user"
            canonical_id = int(field_token(dataset, dataset.uid_field, int(node_id)))
        elif node_type == "item":
            canonical_type = aliases["product_type"]
            canonical_id = int(field_token(dataset, dataset.iid_field, int(node_id)))
        elif node_type == "entity":
            token = field_token(dataset, dataset.entity_field, int(node_id))
            canonical_type, canonical_id = parse_entity_token(token)
        else:
            raise ValueError(f"Unknown path node type: {node_type!r}")
        canonical.append((relation_name, canonical_type, canonical_id))
    return canonical


def canonical_uid_from_input(input_ids, dataset) -> int:
    user_token_id = int(input_ids[1])
    user_token = dataset.tokenizer.convert_ids_to_tokens(user_token_id)
    if not user_token.startswith("U"):
        raise ValueError(f"Expected Hopwise user token, got {user_token!r}")
    internal_uid = int(user_token[1:])
    return int(field_token(dataset, dataset.uid_field, internal_uid))


def checkpoint_identity(checkpoint: Path) -> dict:
    model_file = checkpoint / "model.safetensors"
    stat = model_file.stat()
    return {
        "checkpoint": str(checkpoint.resolve()),
        "model_size": stat.st_size,
        "model_mtime_ns": stat.st_mtime_ns,
    }


def load_validated_shard(path: Path, expected_metadata: dict) -> dict:
    with path.open("rb") as handle:
        payload = pickle.load(handle)
    if payload.get("metadata") != expected_metadata:
        raise ValueError(
            f"PEARLM shard metadata mismatch for {path}: "
            f"expected={expected_metadata!r}, actual={payload.get('metadata')!r}"
        )
    required = {"requested_users", "processed_users", "skipped_cold_start_users", "rows"}
    missing = required.difference(payload)
    if missing:
        raise ValueError(f"PEARLM shard {path} is missing fields: {sorted(missing)}")
    expected_users = set(expected_metadata["requested_user_ids"])
    skipped_users = {int(uid) for uid in payload["skipped_cold_start_users"]}
    generated_users = {int(row["uid"]) for row in payload["rows"]}
    expected_user_count = len(expected_metadata["requested_user_ids"])
    if int(payload["requested_users"]) != expected_user_count:
        raise ValueError(f"PEARLM shard {path} has an invalid requested-user count")
    if int(payload["processed_users"]) + len(skipped_users) != expected_user_count:
        raise ValueError(f"PEARLM shard {path} has inconsistent user accounting")
    if skipped_users.intersection(generated_users):
        raise ValueError(f"PEARLM shard {path} generated a path for a skipped user")
    if not generated_users.issubset(expected_users):
        raise ValueError(f"PEARLM shard {path} contains users outside its batch")
    return payload


def write_atomic_pickle(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    temporary.replace(path)


def relative_shard_path(shard_path: Path, output_path: Path) -> str:
    try:
        return str(shard_path.resolve().relative_to(output_path.parent.resolve()))
    except ValueError:
        return str(shard_path.resolve())


def main() -> None:
    args = parse_args()
    if args.num_beams < args.paths_per_user:
        raise ValueError("--num-beams must be >= --paths-per-user")
    if not (args.checkpoint / "model.safetensors").is_file():
        raise FileNotFoundError(args.checkpoint / "model.safetensors")

    install_sparse_relation_lookup()
    install_cumulative_score_alignment()
    install_bounded_logits_mask_cache()
    if args.model == "KGGLM":
        if args.pre_model_path is None:
            raise ValueError("--pre-model-path is required for KGGLM export")
        install_kgglm_serial_sampler()
        config_dict = build_kgglm_config(
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id=args.gpu_id,
            train_stage="finetune",
            pre_model_path=args.pre_model_path,
            epochs=1,
            pretrain_epochs=1,
            embedding_size=args.embedding_size,
            num_heads=args.num_heads,
            num_layers=args.num_layers,
            paths_per_user=args.paths_per_user,
            num_beams=args.num_beams,
            eval_batch_size=args.batch_size,
        )
    else:
        if args.pre_model_path is not None:
            raise ValueError("--pre-model-path is only valid for KGGLM")
        config_dict = build_pearlm_config(
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id=args.gpu_id,
            epochs=1,
            embedding_size=args.embedding_size,
            num_heads=args.num_heads,
            num_layers=args.num_layers,
            paths_per_user=args.paths_per_user,
            num_beams=args.num_beams,
            eval_batch_size=args.batch_size,
        )
    config = Config(model=args.model, dataset=args.dataset, config_dict=config_dict)
    init_seed(config["seed"], config["reproducibility"])
    dataset = create_dataset(config)
    train_data, _, test_data = data_preparation(config, dataset)

    model = get_model(args.model)(config, train_data.dataset)
    weights = load_file(str(args.checkpoint / "model.safetensors"))
    incompatible = model.load_state_dict(weights, strict=False)
    missing_keys = set(incompatible.missing_keys)
    tied_lm_head = (
        missing_keys == {"lm_head.weight"}
        and model.lm_head.weight.data_ptr() == model.transformer.wte.weight.data_ptr()
    )
    if (missing_keys and not tied_lm_head) or incompatible.unexpected_keys:
        raise ValueError(
            f"Checkpoint mismatch: missing={incompatible.missing_keys}, "
            f"unexpected={incompatible.unexpected_keys}"
        )
    model = model.to(config["device"])
    model.eval()

    train_dataset = train_data.dataset
    train_used_ids = train_dataset.get_user_used_ids()
    kg_edges = internal_kg_edges(train_dataset)
    ui_relation_id = train_dataset.field2token_id[train_dataset.relation_field][train_dataset.ui_relation]
    aliases = DATASET_ALIASES[args.dataset]

    rows = []
    row_shards = []
    raw_paths = 0
    max_native_score = -float("inf")
    processed_users = 0
    requested_users = 0
    skipped_cold_start_users = []
    tokenized_ckg = model.logits_processor_list[0].tokenized_ckg
    checkpoint_meta = checkpoint_identity(args.checkpoint)
    if args.shard_dir is not None:
        args.shard_dir.mkdir(parents=True, exist_ok=True)
    with torch.no_grad():
        for batch_index, batched_data in enumerate(test_data):
            interaction = batched_data[0]
            batch_users = len(interaction)
            requested_user_ids = [
                canonical_uid_from_input(input_ids, train_dataset)
                for input_ids in interaction["input_ids"]
            ]
            requested_users += batch_users
            shard_metadata = {
                "model": args.model,
                "source_dataset": args.dataset,
                **checkpoint_meta,
                "paths_per_user": args.paths_per_user,
                "num_beams": args.num_beams,
                "batch_size": args.batch_size,
                "batch_index": batch_index,
                "requested_user_ids": requested_user_ids,
            }
            shard_path = (
                args.shard_dir / f"batch_{batch_index:06d}.pkl"
                if args.shard_dir is not None
                else None
            )
            if shard_path is not None and shard_path.is_file():
                shard = load_validated_shard(shard_path, shard_metadata)
                processed_users += int(shard["processed_users"])
                skipped_cold_start_users.extend(shard["skipped_cold_start_users"])
                shard_rows = shard["rows"]
                raw_paths += len(shard_rows)
                if shard_rows:
                    max_native_score = max(
                        max_native_score,
                        max(float(row["score"]) for row in shard_rows),
                    )
                row_shards.append(relative_shard_path(shard_path, args.output))
                if args.shard_dir is None:
                    rows.extend(shard_rows)
                print(
                    f"resumed_batch={batch_index} requested_users={requested_users} "
                    f"processed_users={processed_users} "
                    f"skipped_cold_start_users={len(skipped_cold_start_users)} "
                    f"raw_paths={raw_paths}",
                    flush=True,
                )
                if args.max_users is not None and requested_users >= args.max_users:
                    break
                continue

            eligible_positions = []
            batch_skipped_users = []
            for position, input_ids in enumerate(interaction["input_ids"]):
                user_token_id = int(input_ids[1])
                if user_token_id in tokenized_ckg:
                    eligible_positions.append(position)
                    continue

                canonical_uid = canonical_uid_from_input(input_ids, train_dataset)
                batch_skipped_users.append(canonical_uid)
                skipped_cold_start_users.append(canonical_uid)

            batch_rows = []
            if not eligible_positions:
                if shard_path is not None:
                    write_atomic_pickle(
                        shard_path,
                        {
                            "metadata": shard_metadata,
                            "requested_users": batch_users,
                            "processed_users": 0,
                            "skipped_cold_start_users": batch_skipped_users,
                            "rows": batch_rows,
                        },
                    )
                    row_shards.append(relative_shard_path(shard_path, args.output))
                print(
                    f"requested_users={requested_users} processed_users={processed_users} "
                    f"skipped_cold_start_users={len(skipped_cold_start_users)} raw_paths={raw_paths}",
                    flush=True,
                )
                if args.max_users is not None and requested_users >= args.max_users:
                    break
                continue

            interaction = interaction[torch.tensor(eligible_positions)].to(config["device"])
            _, paths = model.explain(
                interaction,
                return_dict_in_generate=True,
                output_scores=True,
                **config["path_generation_args"],
            )
            for internal_uid, internal_item, score, path in paths:
                validate_internal_path(path, train_dataset, train_used_ids, kg_edges, ui_relation_id)
                canonical_path = canonicalize_path(path, train_dataset, aliases)
                canonical_uid = canonical_path[0][2]
                canonical_item = canonical_path[-1][2]
                if canonical_uid != int(field_token(train_dataset, train_dataset.uid_field, int(internal_uid))):
                    raise ValueError("Canonical user mapping differs from path endpoint")
                if canonical_item != int(field_token(train_dataset, train_dataset.iid_field, int(internal_item))):
                    raise ValueError("Canonical item mapping differs from path endpoint")
                native_score = float(score)
                row = {
                    "uid": canonical_uid,
                    "pid": canonical_item,
                    "score": native_score,
                    "path_prob": native_score,
                    "path": canonical_path,
                }
                batch_rows.append(row)
                raw_paths += 1
                max_native_score = max(max_native_score, native_score)
                if args.shard_dir is None:
                    rows.append(row)

            processed_users += len(eligible_positions)
            if shard_path is not None:
                write_atomic_pickle(
                    shard_path,
                    {
                        "metadata": shard_metadata,
                        "requested_users": batch_users,
                        "processed_users": len(eligible_positions),
                        "skipped_cold_start_users": batch_skipped_users,
                        "rows": batch_rows,
                    },
                )
                row_shards.append(relative_shard_path(shard_path, args.output))
            print(
                f"requested_users={requested_users} processed_users={processed_users} "
                f"skipped_cold_start_users={len(skipped_cold_start_users)} raw_paths={raw_paths}",
                flush=True,
            )
            if args.max_users is not None and requested_users >= args.max_users:
                break

    if raw_paths == 0:
        raise ValueError(f"{args.model} generated no valid item-ending paths")
    if max_native_score <= 0.0:
        raise ValueError(
            f"All {args.model} native path scores are non-positive; "
            "generation-token probability alignment is likely broken"
        )
    skipped_cold_start_users = sorted(set(skipped_cold_start_users))
    if args.max_users is None and requested_users != processed_users + len(skipped_cold_start_users):
        raise ValueError(
            "Full-export user accounting mismatch: "
            f"requested={requested_users}, processed={processed_users}, "
            f"skipped={len(skipped_cold_start_users)}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as handle:
        payload = {
            "model": args.model,
            "source_dataset": args.dataset,
            "canonical_dataset": aliases["canonical_dataset"],
            "paths_per_user": args.paths_per_user,
            "num_beams": args.num_beams,
            "requested_users": requested_users,
            "processed_users": processed_users,
            "skipped_cold_start_users": skipped_cold_start_users,
            "raw_paths": raw_paths,
        }
        if args.shard_dir is None:
            payload["rows"] = rows
        else:
            payload["row_shards"] = row_shards
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Wrote manifest for {raw_paths:,} validated canonical paths to {args.output}")


if __name__ == "__main__":
    main()
