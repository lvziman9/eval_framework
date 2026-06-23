#!/usr/bin/env python3
"""Export a canonical Hopwise TransE checkpoint to TPRec atomic features."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from hopwise.config import Config
from hopwise.data import create_dataset

from scripts.hopwise.tprec_runtime import build_transe_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--embedding-size", type=int, default=100)
    parser.add_argument("--summary-json", type=Path, required=True)
    return parser.parse_args()


def write_embeddings(
    output: Path,
    *,
    id_header: str,
    embedding_header: str,
    tokens,
    embeddings: np.ndarray,
) -> int:
    rows = []
    for token, embedding in zip(tokens, embeddings):
        if str(token) == "[PAD]":
            continue
        values = " ".join(f"{float(value):.8f}" for value in embedding)
        rows.append(f"{token}\t{values}")
    output.write_text(
        f"{id_header}\t{embedding_header}\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    return len(rows)


def main() -> None:
    args = parse_args()
    if not args.checkpoint.is_file():
        raise FileNotFoundError(args.checkpoint)

    config = Config(
        model="TransE",
        dataset=args.dataset,
        config_dict=build_transe_config(
            data_root=args.data_root,
            checkpoint_dir=args.checkpoint_dir,
            gpu_id="",
            epochs=1,
            embedding_size=args.embedding_size,
            train_batch_size=2048,
        ),
    )
    dataset = create_dataset(config)
    checkpoint = torch.load(args.checkpoint, weights_only=False, map_location="cpu")
    state = checkpoint["state_dict"]

    arrays = {
        "user": state["user_embedding.weight"].detach().cpu().numpy(),
        "entity": state["entity_embedding.weight"].detach().cpu().numpy(),
        "relation": state["relation_embedding.weight"].detach().cpu().numpy(),
    }
    expected = {
        "user": dataset.user_num,
        "entity": dataset.entity_num,
        "relation": dataset.relation_num,
    }
    for kind, rows in expected.items():
        if arrays[kind].shape != (rows, args.embedding_size):
            raise AssertionError(
                f"{kind} embedding shape mismatch: "
                f"{arrays[kind].shape} != {(rows, args.embedding_size)}"
            )

    dataset_dir = args.data_root / args.dataset
    output_files = {
        "user": dataset_dir / f"{args.dataset}.useremb",
        "entity": dataset_dir / f"{args.dataset}.entityemb",
        "relation": dataset_dir / f"{args.dataset}.relationemb",
    }
    written = {
        "user": write_embeddings(
            output_files["user"],
            id_header="user_embedding_id:token",
            embedding_header="user_embedding:float_seq",
            tokens=dataset.id2token(dataset.uid_field, np.arange(dataset.user_num)),
            embeddings=arrays["user"],
        ),
        "entity": write_embeddings(
            output_files["entity"],
            id_header="entity_embedding_id:token",
            embedding_header="entity_embedding:float_seq",
            tokens=dataset.id2token(dataset.entity_field, np.arange(dataset.entity_num)),
            embeddings=arrays["entity"],
        ),
        "relation": write_embeddings(
            output_files["relation"],
            id_header="relation_embedding_id:token",
            embedding_header="relation_embedding:float_seq",
            tokens=dataset.id2token(dataset.relation_field, np.arange(dataset.relation_num)),
            embeddings=arrays["relation"],
        ),
    }
    for kind, rows in written.items():
        if rows != expected[kind] - 1:
            raise AssertionError(f"{kind} export omitted unexpected rows: {rows}")

    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(
            {
                "status": "PASS",
                "dataset": args.dataset,
                "checkpoint": str(args.checkpoint),
                "embedding_size": args.embedding_size,
                "rows": written,
                "outputs": {key: str(value) for key, value in output_files.items()},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

