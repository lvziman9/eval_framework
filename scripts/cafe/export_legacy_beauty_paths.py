#!/usr/bin/env python3
"""Execute the historical CAFE Beauty program and save canonical-ready paths.

The original CAFE evaluator only writes aggregate metrics. This wrapper uses
the original model, KG, inferred metapath candidates, and profile-guided
program executor, but retains every executed recommendation path so the shared
adapter can validate and evaluate it.
"""

from __future__ import annotations

import argparse
import math
import os
import pickle
import random
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from tqdm import tqdm


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cafe-root", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--infer-path-data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset", default="beauty")
    parser.add_argument("--sample-size", type=int, default=15)
    parser.add_argument("--embed-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument(
        "--max-users",
        type=int,
        default=0,
        help="Optional deterministic smoke limit; zero executes every test user.",
    )
    args = parser.parse_args()

    cafe_root = Path(args.cafe_root).resolve()
    os.chdir(cafe_root)
    sys.path.insert(0, str(cafe_root))

    import utils as cafe_utils
    from data_utils import KGMask
    from execute_neural_symbol import (
        MetaProgramExecutor,
        NeuralProgramLayout,
    )
    from symbolic_model import create_symbolic_model

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError(f"CUDA device requested but unavailable: {args.device}")

    model_args = SimpleNamespace(
        dataset=args.dataset,
        device=device,
        embed_size=args.embed_size,
        deep_module=True,
        use_dropout=True,
        symbolic_model=str(Path(args.checkpoint).resolve()),
    )

    kg = cafe_utils.load_kg(args.dataset)
    kg_mask = KGMask(kg)
    train_labels = cafe_utils.load_labels(args.dataset, "train")
    test_labels = cafe_utils.load_labels(args.dataset, "test")
    path_counts = cafe_utils.load_path_count(args.dataset)
    with open(Path(args.infer_path_data).resolve(), "rb") as f:
        raw_paths = pickle.load(f)

    model = create_symbolic_model(model_args, kg, train=False)
    executor = MetaProgramExecutor(model, kg_mask, model_args)

    def create_program(raw_paths_with_scores, prior_count):
        counts = prior_count.astype(int)
        counts[counts > 5] = 5
        metapath_scores = np.ones(len(kg.metapaths)) * -99
        for metapath_id, paths in raw_paths_with_scores.items():
            if not paths:
                continue
            scores = np.asarray([values[-1] for _ids, values in paths], dtype=float)
            scores[scores < -5.0] = -5.0
            metapath_scores[metapath_id] = np.mean(scores)

        normalized = np.zeros(len(kg.metapaths))
        remaining = args.sample_size
        for metapath_id in np.argsort(metapath_scores)[::-1]:
            normalized[metapath_id] = min(counts[metapath_id], remaining)
            remaining -= normalized[metapath_id]
            if remaining <= 0:
                break
        layout = NeuralProgramLayout(kg.metapaths)
        layout.update_by_path_count(normalized)
        return layout

    user_ids = sorted(test_labels)
    if args.max_users:
        user_ids = user_ids[: args.max_users]

    predicted_paths = {}
    with torch.no_grad():
        for uid in tqdm(user_ids, desc="CAFE Beauty path execution"):
            program = create_program(raw_paths[uid], path_counts[uid])
            executor.execute(program, uid, list(train_labels.get(uid, [])))
            results = executor.collect_results(program)
            user_paths = {}
            for entity_ids, step_log_scores, relations in results:
                if len(entity_ids) != len(relations) + 1:
                    raise ValueError(
                        f"Malformed CAFE path for uid={uid}: "
                        f"entities={entity_ids}, relations={relations}"
                    )
                path = [("self_loop", "user", int(entity_ids[0]))]
                for relation, entity_id in zip(relations, entity_ids[1:]):
                    tail_type = kg.relation_info[relation][1]
                    path.append((relation, tail_type, int(entity_id)))
                if path[-1][1] != "product":
                    continue
                pid = int(entity_ids[-1])
                path_log_score = float(np.sum(step_log_scores))
                path_probability = float(math.exp(path_log_score))
                user_paths.setdefault(pid, []).append(
                    (path_log_score, path_probability, path)
                )
            predicted_paths[int(uid)] = user_paths

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        pickle.dump(predicted_paths, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(
        f"Wrote {output}: users={len(predicted_paths)}, "
        f"uid-pid pairs={sum(len(paths) for paths in predicted_paths.values())}, "
        f"paths={sum(len(rows) for paths in predicted_paths.values() for rows in paths.values())}"
    )


if __name__ == "__main__":
    main()
