#!/usr/bin/env python3
"""Run a one-batch UCPR TransE forward/backward smoke on a patched runtime."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", default="amazon_book_kgat_v1")
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--embed-size", type=int, default=32)
    parser.add_argument("--num-neg-samples", type=int, default=3)
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    summary_json = Path(args.summary_json).resolve()
    os.chdir(runtime_root / "models" / "UCPR")
    sys.path.insert(0, str(runtime_root))

    import torch
    from models.UCPR.preprocess.dataset import DataLoader, Dataset  # type: ignore
    from models.UCPR.preprocess.transe_model import KnowledgeEmbedding  # type: ignore

    smoke_args = SimpleNamespace(
        dataset=args.dataset,
        batch_size=args.batch_size,
        embed_size=args.embed_size,
        num_neg_samples=args.num_neg_samples,
        device=torch.device("cpu"),
        l2_lambda=0.0,
    )
    dataset = Dataset(smoke_args, set_name="train")
    loader = DataLoader(dataset, args.batch_size)
    batch = loader.get_batch()
    model = KnowledgeEmbedding(smoke_args, loader).to(smoke_args.device)
    model.train()
    batch_tensor = torch.from_numpy(batch).to(smoke_args.device)
    loss = model(batch_tensor)
    loss.backward()
    gradient_tensors = sum(
        1
        for parameter in model.parameters()
        if parameter.grad is not None and torch.isfinite(parameter.grad).all()
    )
    named_parameters = [name for name, _ in model.named_parameters()]
    expected_relation_names = set(dataset.other_relation_names + ["purchased"])
    present_relation_names = {
        name
        for name in expected_relation_names
        if name in named_parameters
    }
    passed = (
        tuple(batch_tensor.shape) == (args.batch_size, 11)
        and float(loss.item()) > 0.0
        and gradient_tensors > 0
        and present_relation_names == expected_relation_names
    )
    report = {
        "status": "PASS" if passed else "FAIL",
        "dataset": args.dataset,
        "runtime_root": str(runtime_root),
        "batch_shape": list(batch_tensor.shape),
        "embed_size": args.embed_size,
        "num_neg_samples": args.num_neg_samples,
        "loss": float(loss.item()),
        "gradient_tensors": gradient_tensors,
        "entity_names": sorted(dataset.entity_names),
        "other_relation_names": sorted(dataset.other_relation_names),
        "expected_relation_names": sorted(expected_relation_names),
        "present_relation_names": sorted(present_relation_names),
    }
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
