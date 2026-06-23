"""Shared Hopwise configuration for canonical native-path experiments."""

from __future__ import annotations

from pathlib import Path


def build_pearlm_config(
    *,
    data_root: Path,
    checkpoint_dir: Path,
    gpu_id: str,
    epochs: int,
    embedding_size: int,
    num_heads: int,
    num_layers: int,
    paths_per_user: int,
    num_beams: int,
    eval_batch_size: int = 32,
    train_batch_size: int = 128,
    learning_rate: float = 2e-4,
    weight_decay: float = 0.01,
    warmup_steps: int = 0,
    eval_step: int = 0,
    stopping_step: int = 1,
) -> dict:
    return {
        "gpu_id": gpu_id,
        "use_gpu": bool(gpu_id),
        "data_path": str(data_root),
        "checkpoint_dir": str(checkpoint_dir),
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
        "metrics": ["Recall", "NDCG", "Hit", "Precision", "Fidelity"],
        "topk": [10],
        "valid_metric": "NDCG@10",
        "epochs": epochs,
        "eval_step": eval_step,
        "stopping_step": stopping_step,
        "train_batch_size": train_batch_size,
        "eval_batch_size": eval_batch_size,
        "learning_rate": learning_rate,
        "weight_decay": weight_decay,
        "warmup_steps": warmup_steps,
        "show_progress": True,
        "embedding_size": embedding_size,
        "num_heads": num_heads,
        "num_layers": num_layers,
        "use_kg_token_types": True,
        "base_model": "distilgpt2",
        "sequence_postprocessor": "Cumulative",
        "path_hop_length": 3,
        "context_length": 9,
        "MAX_PATHS_PER_USER": 1,
        "path_sample_args": {
            "strategy": "constrained-rw",
            "temporal_causality": False,
            "collaborative_path": True,
            "restrict_by_phase": False,
            "parallel_max_workers": 1,
            "MAX_RW_PATHS_PER_HOP": 1,
        },
        "path_generation_args": {
            "paths_per_user": paths_per_user,
            "num_beams": num_beams,
            "num_beam_groups": 1,
            "diversity_penalty": 0.0,
            "length_penalty": 0.0,
            "do_sample": False,
        },
    }


def build_kgglm_config(
    *,
    data_root: Path,
    checkpoint_dir: Path,
    gpu_id: str,
    train_stage: str,
    pre_model_path: Path | None,
    epochs: int,
    pretrain_epochs: int,
    embedding_size: int,
    num_heads: int,
    num_layers: int,
    paths_per_user: int,
    num_beams: int,
    eval_batch_size: int = 32,
    train_batch_size: int = 256,
    learning_rate: float = 2e-4,
    weight_decay: float = 0.01,
    warmup_steps: int = 250,
    eval_step: int = 1,
    stopping_step: int = 2,
    save_step: int = 1,
    pretrain_paths: int = 1,
) -> dict:
    """Build the canonical two-stage KGGLM configuration.

    KGGLM pre-trains on generic KG-only walks and then fine-tunes on
    recommendation paths. The fine-tuning path semantics remain identical to
    the canonical PEARLM view so the two path-language models are comparable.
    """

    if train_stage not in {"pretrain", "finetune"}:
        raise ValueError(f"Unsupported KGGLM train stage: {train_stage}")
    if train_stage == "finetune" and pre_model_path is None:
        raise ValueError("KGGLM finetuning requires a pretrained model path")

    config = build_pearlm_config(
        data_root=data_root,
        checkpoint_dir=checkpoint_dir,
        gpu_id=gpu_id,
        epochs=epochs,
        embedding_size=embedding_size,
        num_heads=num_heads,
        num_layers=num_layers,
        paths_per_user=paths_per_user,
        num_beams=num_beams,
        eval_batch_size=eval_batch_size,
        train_batch_size=train_batch_size,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        warmup_steps=warmup_steps,
        eval_step=eval_step,
        stopping_step=stopping_step,
    )
    config.update(
        {
            "train_stage": train_stage,
            "pre_model_path": str(pre_model_path) if pre_model_path is not None else "",
            "pretrain_epochs": pretrain_epochs,
            "save_step": save_step,
        }
    )
    config["path_sample_args"].update(
        {
            "pretrain_paths": pretrain_paths,
            "MAX_RW_TRIES_PER_IID": 1,
            # The canonical runtime installs a corrected deterministic serial
            # sampler for KGGLM's generic pretraining stage.
            "parallel_max_workers": 0 if train_stage == "pretrain" else 1,
        }
    )
    return config
