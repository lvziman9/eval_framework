#!/usr/bin/env python3
"""Run one PGPR TransE forward/backward batch for a patched runtime."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--embed-size", type=int, default=16)
    parser.add_argument("--num-neg-samples", type=int, default=2)
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    summary_path = Path(args.summary_json).resolve()
    pgpr_root = runtime_root / "models" / "PGPR"
    os.chdir(pgpr_root)
    sys.path.insert(0, str(pgpr_root))
    sys.path.insert(0, str(runtime_root))

    import torch
    from data_utils import AmazonDataLoader
    from transe_model import KnowledgeEmbedding
    from utils import get_product_relationships, load_dataset

    dataset = load_dataset(args.dataset)
    dataloader = AmazonDataLoader(dataset, args.batch_size)
    batch = dataloader.get_batch()
    model_args = SimpleNamespace(
        dataset=args.dataset,
        device=torch.device("cpu"),
        embed_size=args.embed_size,
        num_neg_samples=args.num_neg_samples,
        l2_lambda=0.0,
    )
    model = KnowledgeEmbedding(dataset, model_args)
    batch_tensor = torch.from_numpy(batch).long()
    loss = model(batch_tensor)
    loss_value = float(loss.detach().cpu().item())
    if not math.isfinite(loss_value):
        raise ValueError(f"non-finite PGPR TransE smoke loss: {loss_value}")
    loss.backward()
    grad_tensors = sum(
        1
        for parameter in model.parameters()
        if parameter.grad is not None
    )
    if grad_tensors <= 0:
        raise ValueError("PGPR TransE smoke produced no gradients")

    summary = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "runtime_root": str(runtime_root),
        "batch_size": args.batch_size,
        "batch_shape": list(batch.shape),
        "embed_size": args.embed_size,
        "num_neg_samples": args.num_neg_samples,
        "product_relations": get_product_relationships(args.dataset),
        "loss": loss_value,
        "gradient_tensors": grad_tensors,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
