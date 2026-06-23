"""Canonical TPRec configuration and runtime correctness patches."""

from __future__ import annotations

from collections import defaultdict
from functools import reduce
from pathlib import Path
from types import MethodType

import numpy as np
import torch
import torch.nn.functional as F


ML1M_PATH_CONSTRAINTS = [
    [[None], ["[UI-Relation]"], ["[UI-Relation]"], ["[UI-Relation]"]],
    [[None], ["[UI-Relation]"], ["belong_to"], ["belong_to"]],
    [[None], ["[UI-Relation]"], ["cinematography_by"], ["cinematography_by"]],
    [[None], ["[UI-Relation]"], ["directed_by"], ["directed_by"]],
    [[None], ["[UI-Relation]"], ["edited_by"], ["edited_by"]],
    [[None], ["[UI-Relation]"], ["produced_by_company"], ["produced_by_company"]],
    [[None], ["[UI-Relation]"], ["produced_by_producer"], ["produced_by_producer"]],
    [[None], ["[UI-Relation]"], ["starring"], ["starring"]],
    [[None], ["[UI-Relation]"], ["wrote_by"], ["wrote_by"]],
]

LASTFM_PATH_CONSTRAINTS = [
    [[None], ["[UI-Relation]"], ["[UI-Relation]"], ["[UI-Relation]"]],
    [[None], ["[UI-Relation]"], ["alternative_version_of"], ["alternative_version_of"]],
    [[None], ["[UI-Relation]"], ["belong_to"], ["belong_to"]],
    [[None], ["[UI-Relation]"], ["featured_by"], ["featured_by"]],
    [[None], ["[UI-Relation]"], ["mixed_by"], ["mixed_by"]],
    [[None], ["[UI-Relation]"], ["original_version_of"], ["original_version_of"]],
    [[None], ["[UI-Relation]"], ["produced_by"], ["produced_by"]],
    [[None], ["[UI-Relation]"], ["related_to"], ["related_to"]],
    [[None], ["[UI-Relation]"], ["sang_by"], ["sang_by"]],
]


def canonical_path_constraints(dataset: str) -> list:
    if dataset == "canonical_ml1m_v1":
        return ML1M_PATH_CONSTRAINTS
    if dataset == "canonical_lastfm_v1":
        return LASTFM_PATH_CONSTRAINTS
    raise ValueError(f"TPRec is not configured for canonical dataset {dataset!r}")


def _common_config(*, data_root: Path, checkpoint_dir: Path, gpu_id: str) -> dict:
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
        "metrics": ["Recall", "NDCG", "Hit", "Precision"],
        "topk": [10],
        "valid_metric": "NDCG@10",
        "show_progress": True,
        "save_dataset": False,
        "save_dataloaders": False,
        "kg_reverse_r": False,
    }


def build_transe_config(
    *,
    data_root: Path,
    checkpoint_dir: Path,
    gpu_id: str,
    epochs: int,
    embedding_size: int,
    train_batch_size: int,
) -> dict:
    config = _common_config(
        data_root=data_root,
        checkpoint_dir=checkpoint_dir,
        gpu_id=gpu_id,
    )
    config.update(
        {
            "embedding_size": embedding_size,
            "margin": 1.0,
            "epochs": epochs,
            # Hopwise's knowledge trainer references its validation summary
            # after training even when evaluation is disabled. Evaluate once
            # at the end instead of triggering that uninitialized-state bug.
            "eval_step": max(1, epochs),
            "stopping_step": 1,
            "train_batch_size": train_batch_size,
            "eval_batch_size": 256,
            "learning_rate": 1e-3,
        }
    )
    return config


def build_tprec_config(
    *,
    dataset: str,
    data_root: Path,
    checkpoint_dir: Path,
    gpu_id: str,
    train_stage: str,
    epochs: int,
    train_batch_size: int,
    eval_batch_size: int,
    beam_search_hop: tuple[int, int, int],
    transe_checkpoint: Path | None = None,
) -> dict:
    if train_stage not in {"pretrain", "policy"}:
        raise ValueError(f"unsupported TPRec stage: {train_stage}")

    config = _common_config(
        data_root=data_root,
        checkpoint_dir=checkpoint_dir,
        gpu_id=gpu_id,
    )
    config.update(
        {
            "train_stage": train_stage,
            "epochs": epochs,
            "pretrain_epochs": epochs,
            "save_step": 1,
            "eval_step": 0,
            "stopping_step": 1,
            "train_batch_size": train_batch_size,
            "eval_batch_size": eval_batch_size,
            "learning_rate": 1e-3 if train_stage == "pretrain" else 1e-4,
            "state_history": 1,
            "max_acts": 250,
            "gamma": 0.99,
            "action_dropout": 0.0,
            "hidden_sizes": [512, 256],
            "max_path_len": 3,
            "weight_factor": 1e-3,
            "beam_search_hop": list(beam_search_hop),
            "fix_scores_sorting_bug": True,
            "margin": 1.0,
            "cluster_num": 14,
            "cluster_feature": "w-stat",
            "path_constraint": canonical_path_constraints(dataset),
            # Canonical TPRec injects the TransE checkpoint directly during
            # model construction. Upstream atomic-feature aliases merge the
            # item/entity vocabulary a second time and duplicate unlinked
            # item tokens.
            "additional_feat_suffix": [],
            "alias_of_user_id": [],
            "alias_of_entity_id": [],
            "alias_of_relation_id": [],
            "preload_weight": None,
            "canonical_transe_checkpoint": (
                str(transe_checkpoint) if transe_checkpoint is not None else None
            ),
        }
    )
    return config


class _DeferredDot:
    def __init__(self, left: np.ndarray, right: np.ndarray):
        self.left = left
        self.right = right


class _NumpyInitProxy:
    """Delay TPRec's user-by-item matrix until its row maxima are requested."""

    def __init__(self, batch_size: int):
        self.batch_size = batch_size

    def __getattr__(self, name):
        return getattr(np, name)

    def dot(self, left, right, *args, **kwargs):
        if (
            not args
            and not kwargs
            and isinstance(left, np.ndarray)
            and isinstance(right, np.ndarray)
            and left.ndim == 2
            and right.ndim == 2
            and left.shape[1] == right.shape[0]
        ):
            return _DeferredDot(left, right)
        return np.dot(left, right, *args, **kwargs)

    def max(self, value, axis=None, *args, **kwargs):
        if isinstance(value, _DeferredDot):
            if axis != 1:
                raise ValueError("canonical deferred TPRec dot only supports row maxima")
            maxima = []
            for start in range(0, value.left.shape[0], self.batch_size):
                scores = np.dot(
                    value.left[start : start + self.batch_size],
                    value.right,
                )
                maxima.append(np.max(scores, axis=1))
            return np.concatenate(maxima)
        return np.max(value, axis=axis, *args, **kwargs)


def install_tprec_runtime_patches(scale_batch_size: int = 512) -> None:
    """Install canonical TPRec fixes without modifying the external Hopwise tree."""

    import hopwise.model.knowledge_aware_recommender.tprec as tprec_module

    tprec_class = tprec_module.TPRec
    if getattr(tprec_class, "_canonical_runtime_patched", False):
        return

    original_init = tprec_class.__init__

    def patched_init(self, config, dataset):
        original_get_preload_weight = None
        if config["train_stage"] == "pretrain":
            checkpoint_path = config["canonical_transe_checkpoint"]
            if not checkpoint_path:
                raise ValueError(
                    "canonical TPRec pretraining requires canonical_transe_checkpoint"
                )
            checkpoint = torch.load(
                checkpoint_path,
                weights_only=False,
                map_location="cpu",
            )
            state = checkpoint["state_dict"]
            pretrained = {
                "user_embedding_id": state["user_embedding.weight"].detach().cpu().numpy(),
                "entity_embedding_id": state["entity_embedding.weight"].detach().cpu().numpy(),
                "relation_embedding_id": state["relation_embedding.weight"].detach().cpu().numpy(),
            }
            expected_shapes = {
                "user_embedding_id": (dataset.user_num, pretrained["user_embedding_id"].shape[1]),
                "entity_embedding_id": (dataset.entity_num, pretrained["entity_embedding_id"].shape[1]),
                "relation_embedding_id": (
                    dataset.relation_num,
                    pretrained["relation_embedding_id"].shape[1],
                ),
            }
            for field, expected_shape in expected_shapes.items():
                if pretrained[field].shape != expected_shape:
                    raise AssertionError(
                        f"{field} checkpoint shape mismatch: "
                        f"{pretrained[field].shape} != {expected_shape}"
                    )

            original_get_preload_weight = dataset.get_preload_weight

            def get_preload_weight(_dataset, field):
                try:
                    return pretrained[field]
                except KeyError as error:
                    raise KeyError(f"unsupported canonical preload field: {field}") from error

            dataset.get_preload_weight = MethodType(get_preload_weight, dataset)

        original_np = tprec_module.np
        tprec_module.np = _NumpyInitProxy(scale_batch_size)
        try:
            original_init(self, config, dataset)
        finally:
            tprec_module.np = original_np
            if original_get_preload_weight is not None:
                dataset.get_preload_weight = original_get_preload_weight

        if self.train_stage == "pretrain":
            # Upstream comments say these embeddings are fine-tuned, but
            # ``from_pretrained`` freezes them unless explicitly overridden.
            self.user_embedding.weight.requires_grad_(True)
            self.entity_embedding.weight.requires_grad_(True)
            self.relation_embedding.weight.requires_grad_(True)
        else:
            # The collaborative graph contains the ordinary UI relation ID.
            # Upstream expands that relation into synthetic ``UI_0`` ...
            # ``UI_n`` names which are never emitted by graph traversal, so
            # every path fails the reward-pattern test. Temporal clusters
            # belong in the reward embedding, not in the graph relation name.
            patterns = []
            for path_constraint in self.path_pattern:
                relations = []
                for node in path_constraint:
                    relation = node[0]
                    if relation is None:
                        continue
                    if relation.endswith("_r"):
                        relation = relation[:-2]
                    relations.append(relation)
                patterns.append(tuple(["self_loop", *relations]))
            self.patterns = patterns

    def patched_forward(self, inputs):
        state, act_mask = inputs
        x = self.l1(state)
        x = F.dropout(F.elu(x), p=0.5, training=self.training)
        x = self.l2(x)
        x = F.dropout(F.elu(x), p=0.5, training=self.training)
        actor_logits = self.actor(x)
        actor_logits[~act_mask] = float("-inf")
        return F.softmax(actor_logits, dim=-1), self.critic(x)

    def patched_interacted_matrix(self, temporal_weight):
        weights_by_user = temporal_weight.uc_weight
        matrix = []
        for uid in range(1, self.user_num):
            user_weights = weights_by_user.get(uid, {})
            item_emb = np.zeros(self.embedding_size, dtype=self.ui_clust_relation_embedding.dtype)
            for cluster_id, weight in user_weights.items():
                item_emb += self.ui_clust_relation_embedding[cluster_id] * weight
            matrix.append(item_emb)
        return matrix

    @torch.no_grad()
    def patched_beam_search(self, users):
        user_ids = [user.item() if isinstance(user, torch.Tensor) else int(user) for user in users]
        state_pool = self.reset(user_ids)
        path_pool = self._batch_path
        probs_pool = [[] for _ in user_ids]

        for hop, requested_k in enumerate(self.beam_search_hop):
            state_tensor = torch.as_tensor(state_pool, dtype=torch.float32, device=self.device)
            acts_pool = self._batch_get_actions(path_pool, False)
            actmask_pool = self._batch_acts_to_masks(acts_pool)
            actmask_tensor = torch.as_tensor(actmask_pool, dtype=torch.bool, device=self.device)
            action_probs, _ = self.forward((state_tensor, actmask_tensor))
            topk_probs, topk_idxs = torch.topk(
                action_probs,
                min(requested_k, action_probs.shape[1]),
                dim=1,
            )

            new_path_pool = []
            new_probs_pool = []
            for row, (indices, probabilities) in enumerate(zip(topk_idxs, topk_probs)):
                path = path_pool[row]
                old_probs = probs_pool[row]
                for index, probability in zip(indices.tolist(), probabilities.tolist()):
                    if index >= len(acts_pool[row]):
                        continue
                    relation, next_node_id = acts_pool[row][index]
                    next_node_type = (
                        path[-1][1]
                        if relation == "self_loop"
                        else self._get_next_node_type(path[-1][1], relation)
                    )
                    new_path_pool.append(path + [(relation, next_node_type, next_node_id)])
                    new_probs_pool.append(old_probs + [probability])
            path_pool = new_path_pool
            probs_pool = new_probs_pool
            if hop < len(self.beam_search_hop) - 1 and path_pool:
                state_pool = self._batch_get_state(path_pool)

        return path_pool, probs_pool

    def patched_collect_scores(self, users, paths, probs, interacted_matrix):
        user_ids = [user.item() if isinstance(user, torch.Tensor) else int(user) for user in users]
        pad_emb = np.zeros((1, self.embedding_size), dtype=self.user_embedding.dtype)
        interacted_embeds = np.concatenate((pad_emb, np.asarray(interacted_matrix)), axis=0)
        if interacted_embeds.shape[0] != self.user_num:
            raise AssertionError(
                "TPRec temporal matrix does not cover the full internal user vocabulary: "
                f"{interacted_embeds.shape[0]} != {self.user_num}"
            )

        batch_scores = np.dot(
            self.user_embedding[user_ids] + interacted_embeds[user_ids],
            self.entity_embedding[: self.n_items].T,
        )
        score_row = {uid: row for row, uid in enumerate(user_ids)}
        pred_paths = {uid: defaultdict(list) for uid in user_ids}

        for path, probability_steps in zip(paths, probs):
            if "self_loop" in [node[0] for node in path[1:]]:
                continue
            if path[-1][1] != "entity":
                continue
            path_uid = int(path[0][2])
            if path_uid not in pred_paths:
                continue
            path_pid = int(path[-1][2])
            if path_pid >= self.n_items or path_pid in self.positives[path_uid]:
                continue
            native_score = float(batch_scores[score_row[path_uid], path_pid])
            path_probability = float(reduce(lambda left, right: left * right, probability_steps, 1.0))
            pred_paths[path_uid][path_pid].append(
                (native_score, path_probability, path)
            )

        results = torch.full((len(user_ids), self.n_items), -torch.inf)
        explanations = []
        for row, uid in enumerate(user_ids):
            best_for_items = []
            for item_paths in pred_paths[uid].values():
                best_for_items.append(max(item_paths, key=lambda value: value[1]))
            ranked = sorted(
                best_for_items,
                key=lambda value: (value[0], value[1]),
                reverse=True,
            )[: max(self.topk)]
            for native_score, _, path in ranked:
                item = int(path[-1][2])
                results[row, item] = native_score
                explanations.append([uid, item, native_score, path])
        return results, explanations

    def patched_get_reward(self, path):
        if len(path) <= 2 or not self._has_pattern(path):
            return 0.0
        _, current_node_type, current_node_id = path[-1]
        if current_node_type != "entity" or current_node_id >= self.n_items:
            return 0.0

        raw_uid = path[0][-1]
        uid = raw_uid.item() if isinstance(raw_uid, torch.Tensor) else int(raw_uid)
        user_weights = self.uc_weight.get(uid, {})
        if not user_weights:
            return 0.0
        item_emb = np.zeros(self.embedding_size, dtype=self.ui_clust_relation_embedding.dtype)
        for cluster_id, weight in user_weights.items():
            item_emb += self.ui_clust_relation_embedding[cluster_id] * weight
        score = float(
            np.dot(
                self.user_embedding[uid] + item_emb,
                self.entity_embedding[int(current_node_id)],
            )
        )
        scale = float(self.u_p_scales[uid])
        if scale == 0.0:
            return 0.0
        return max(score / scale, 0.0)

    tprec_class.__init__ = patched_init
    tprec_class.forward = patched_forward
    tprec_class._build_interacted_matrix = patched_interacted_matrix
    tprec_class.beam_search = patched_beam_search
    tprec_class.collect_scores = patched_collect_scores
    tprec_class._get_reward = patched_get_reward
    tprec_class._canonical_runtime_patched = True
