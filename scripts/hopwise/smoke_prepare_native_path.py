#!/usr/bin/env python3
"""Load a canonical benchmark with a Hopwise native-path model.

This smoke test deliberately calls the knowledge-dataset split builder rather
than the path-language-model builder. It validates the fixed benchmark splits,
KG, link mapping, tokenizer, and model-specific dataset selection without
enumerating training paths.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from hopwise.config import Config
from hopwise.data import create_dataset
from hopwise.data.dataset import KGGLMDataset, KnowledgeBasedDataset, KnowledgePathDataset
from hopwise.utils import ModelType, get_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("PEARLM", "KGGLM"), required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--sample-paths",
        action="store_true",
        help="Also sample and tokenize the training paths using a sparse relation lookup.",
    )
    parser.add_argument(
        "--instantiate-model",
        action="store_true",
        help="Instantiate the model and its KG-constrained decoder after path sampling.",
    )
    return parser.parse_args()


def install_sparse_relation_lookup() -> None:
    """Replace Hopwise's quadratic vertex-by-vertex relation matrix.

    Upstream currently allocates ``len(vertices) ** 2`` integers merely to map
    each sampled edge back to its relation. That is not viable for canonical
    LastFM or Amazon-book. The lookup below is O(|E| + sampled paths).
    """

    def add_paths_relations(self, graph, paths):
        paths = list(paths)
        complete_path_length = self.path_hop_length * 2 + 1
        paths_with_relations = np.full(
            (len(paths), complete_path_length),
            fill_value=self.PATH_PADDING,
            dtype=int,
        )
        relation_token_id = self.field2token_id[self.relation_field]
        relation_by_edge: dict[tuple[int, int], int] = {}
        for edge in graph.es:
            relation = relation_token_id[edge["type"]]
            relation_by_edge[(edge.source, edge.target)] = relation
            if not graph.is_directed():
                relation_by_edge[(edge.target, edge.source)] = relation

        for row_idx, path in enumerate(paths):
            path = list(path)
            paths_with_relations[row_idx, 0 : len(path) * 2 : 2] = path
            for hop_idx, (head, tail) in enumerate(zip(path, path[1:])):
                try:
                    paths_with_relations[row_idx, hop_idx * 2 + 1] = relation_by_edge[(head, tail)]
                except KeyError as error:
                    raise KeyError(f"sampled edge absent from relation lookup: {(head, tail)}") from error
        return paths_with_relations

    KnowledgePathDataset._add_paths_relations = add_paths_relations


def install_kgglm_serial_sampler() -> None:
    """Fix both lazy-parallel and missing-kwargs branches in KGGLM sampling."""

    def generate_pretrain_dataset(self):
        if self._path_dataset is not None:
            return

        graph = self._create_ckg_igraph(show_relation=True, directed=False)
        kg_relation_count = len(self.relations)
        graph.es["weight"] = [0.0] * self.inter_num + [1.0] * kg_relation_count

        graph_min_iid = 1 + self.user_num
        min_hop, max_hop = self.pretrain_hop_length
        max_tries = self.config["path_sample_args"]["MAX_RW_TRIES_PER_IID"]
        paths: set[tuple[int, ...]] = set()

        for start_node in range(graph_min_iid + 1, len(graph.vs)):
            for _ in range(self.pretrain_paths):
                for _ in range(max_tries):
                    hop_length = np.random.randint(min_hop, max_hop + 1)
                    path = tuple(graph.random_walk(start_node, hop_length, weights="weight"))
                    if path not in paths:
                        paths.add(path)
                        break

        paths_with_relations = self._add_paths_relations(graph, paths)
        self._path_dataset = "".join(self._format_path(path) + "\n" for path in paths_with_relations)

    KGGLMDataset.generate_pretrain_dataset = generate_pretrain_dataset


def main() -> None:
    args = parse_args()
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    config_dict = {
        "gpu_id": "",
        "use_gpu": False,
        "data_path": str(args.data_root),
        "checkpoint_dir": str(args.checkpoint_dir),
        "benchmark_filename": ["train", "valid", "test"],
        "load_col": {
            "inter": ["user_id", "item_id", "rating", "timestamp"],
            "kg": ["head_id", "relation_id", "tail_id"],
            "link": ["item_id", "entity_id"],
        },
        "eval_args": {
            "split": {"RS": [0.8, 0.1, 0.1]},
            "order": "RO",
            "group_by": "user",
            "mode": {"valid": "full", "test": "full"},
        },
        "metrics": ["Recall", "NDCG"],
        "topk": [10],
        "valid_metric": "NDCG@10",
        "path_hop_length": 3,
        "MAX_PATHS_PER_USER": 1,
        "path_sample_args": {
            "strategy": "constrained-rw",
            "temporal_causality": False,
            "collaborative_path": True,
            "restrict_by_phase": False,
            # KGGLM upstream creates a lazy joblib generator without consuming
            # it when this is non-zero. Serial mode is required until fixed.
            "parallel_max_workers": 0 if args.model == "KGGLM" else 1,
        },
    }
    if args.model == "KGGLM":
        config_dict.update(
            {
                "train_stage": "pretrain",
                "pretrain_epochs": 1,
                "save_step": 1,
            }
        )

    config = Config(model=args.model, dataset=args.dataset, config_dict=config_dict)
    dataset = create_dataset(config)

    if config["MODEL_TYPE"] != ModelType.PATH_LANGUAGE_MODELING:
        raise AssertionError(f"{args.model} is not registered as a path-language model")
    if not isinstance(dataset, KnowledgePathDataset):
        raise AssertionError(f"unexpected dataset class: {type(dataset).__name__}")

    if args.instantiate_model and not args.sample_paths:
        raise ValueError("--instantiate-model requires --sample-paths")

    if args.sample_paths:
        install_sparse_relation_lookup()
        if args.model == "KGGLM":
            install_kgglm_serial_sampler()
        split_datasets = dataset.build()
    else:
        # Avoid KnowledgePathDataset.build(), which also samples all training paths.
        split_datasets = KnowledgeBasedDataset.build(dataset)
    split_rows = [len(split.inter_feat) for split in split_datasets]
    source_rows = [
        sum(1 for _ in (args.data_root / args.dataset / f"{args.dataset}.{phase}.inter").open()) - 1
        for phase in ("train", "valid", "test")
    ]
    if split_rows != source_rows:
        raise AssertionError(f"fixed split mismatch: hopwise={split_rows}, source={source_rows}")
    if args.sample_paths and len(split_datasets[0]) <= 1:
        raise AssertionError("path sampling produced no non-empty training paths")

    model_parameters = None
    if args.instantiate_model:
        model = get_model(args.model)(config, split_datasets[0])
        model_parameters = sum(parameter.numel() for parameter in model.parameters())

    summary = {
        "status": "PASS",
        "model": args.model,
        "dataset": args.dataset,
        "model_type": config["MODEL_TYPE"].name,
        "dataset_class": type(dataset).__name__,
        "split_rows": dict(zip(("train", "valid", "test"), split_rows)),
        "users": dataset.user_num,
        "items": dataset.item_num,
        "entities": dataset.entity_num,
        "relations": dataset.relation_num,
        "kg_triples": len(dataset.kg_feat),
        "linked_items": len(dataset.item2entity),
        "tokenizer_vocab": len(dataset.tokenizer),
        "path_hop_length": dataset.path_hop_length,
        "sampled_training_paths": len(split_datasets[0]) if args.sample_paths else None,
        "path_sampling": "PASS" if args.sample_paths else "NOT_RUN",
        "model_instantiation": "PASS" if args.instantiate_model else "NOT_RUN",
        "model_parameters": model_parameters,
        "note": "Model training was intentionally not run.",
    }

    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
