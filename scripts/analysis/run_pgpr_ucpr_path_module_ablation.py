#!/usr/bin/env python3
"""
PGPR/UCPR path-module ablation report generator.

This script is intentionally read-only with respect to model artifacts: it
consumes frozen xrecsys result CSVs plus canonical validation JSON files and
writes derived ablation tables, SVG tradeoff figures, and lightweight
explanation cases.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


EXPECTED_ALPHAS = [round(i * 0.05, 2) for i in range(21)]
REC_METRICS = ("ndcg", "hr", "precision", "recall")
EXP_METRICS = ("LIR", "SEP", "ETD")
ALL_METRICS = REC_METRICS + EXP_METRICS
TOPK = 10
TOTAL_PATH_TYPES = {"lastfm": 9, "ml1m": 10}
STRICT_SWEEP_PROTOCOL = (
    "strict baseline-preserving canonical alpha sweep over the frozen original top-k item set"
)
STRICT_NDCG_SCOPE = (
    "strict canonical NDCG@10; alpha=0 is verified to exactly preserve the original top-k ranking"
)


@dataclass(frozen=True)
class Artifact:
    dataset: str
    dataset_label: str
    model: str
    role: str
    result_dir: Path
    paths_dir: Path
    export_validation_json: Path
    accuracy_json: Path
    sweep_protocol: str
    ndcg_scope: str


@dataclass
class PathCandidate:
    pid: int
    path_score: float
    path_prob: float
    path: Tuple[Tuple[str, str, str], ...]
    path_str: str
    path_type: str
    score_norm: float = 0.0
    lir: float = 0.0
    sep: float = 0.0


@dataclass
class StrictPathData:
    dataset: str
    dataset_label: str
    original_topk: Dict[int, List[int]]
    original_explanations: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]]
    original_explanation_text: Dict[int, Dict[int, str]]
    candidate_paths: Dict[int, Dict[int, List[PathCandidate]]]
    test_labels: Dict[int, Set[int]]
    uid_pid_timestamp: Dict[int, Dict[int, int]]
    lir_matrix: Dict[int, Dict[int, float]]
    sep_matrix: Dict[str, Dict[int, float]]


ARTIFACTS = [
    Artifact(
        dataset="lastfm",
        dataset_label="LastFM",
        model="PGPR",
        role="main",
        result_dir=Path("xrecsys/results/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score"),
        paths_dir=Path("xrecsys/paths/lastfm/agent_topk=25-50-1-pgpr-canonical-native-score"),
        export_validation_json=Path("reports/tables/canonical_export_validation/lastfm_pgpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/pgpr_lastfm_accuracy.json"),
        sweep_protocol=STRICT_SWEEP_PROTOCOL,
        ndcg_scope=STRICT_NDCG_SCOPE,
    ),
    Artifact(
        dataset="lastfm",
        dataset_label="LastFM",
        model="UCPR",
        role="auxiliary",
        result_dir=Path("xrecsys/results/lastfm/agent_topk=25-50-1-ucpr-canonical-matched"),
        paths_dir=Path("xrecsys/paths/lastfm/agent_topk=25-50-1-ucpr-canonical-matched"),
        export_validation_json=Path("reports/tables/canonical_export_validation/lastfm_ucpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/ucpr_lastfm_accuracy.json"),
        sweep_protocol=STRICT_SWEEP_PROTOCOL,
        ndcg_scope=STRICT_NDCG_SCOPE,
    ),
    Artifact(
        dataset="ml1m",
        dataset_label="ML-1M",
        model="PGPR",
        role="main",
        result_dir=Path("xrecsys/results/ml1m/agent_topk=25-50-1-pgpr-canonical-ml1m-canonical-all-users"),
        paths_dir=Path("xrecsys/paths/ml1m/agent_topk=25-50-1-pgpr-canonical-ml1m"),
        export_validation_json=Path("reports/tables/canonical_export_validation/ml1m_pgpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/pgpr_ml1m_accuracy.json"),
        sweep_protocol=STRICT_SWEEP_PROTOCOL,
        ndcg_scope=STRICT_NDCG_SCOPE,
    ),
    Artifact(
        dataset="ml1m",
        dataset_label="ML-1M",
        model="UCPR",
        role="auxiliary",
        result_dir=Path("xrecsys/results/ml1m/agent_topk=25-50-1-ucpr-canonical-ml1m-canonical-all-users"),
        paths_dir=Path("xrecsys/paths/ml1m/agent_topk=25-50-1-ucpr-canonical-ml1m"),
        export_validation_json=Path("reports/tables/canonical_export_validation/ml1m_ucpr.json"),
        accuracy_json=Path("runs/debug_compare/2026-06-20_native_path_expansion/ucpr_ml1m_accuracy.json"),
        sweep_protocol=STRICT_SWEEP_PROTOCOL,
        ndcg_scope=STRICT_NDCG_SCOPE,
    ),
]


def pct(numerator: float, denominator: float) -> float:
    if denominator == 0 or math.isnan(denominator):
        return float("nan")
    return numerator / abs(denominator) * 100.0


def pct_change(value: float, baseline: float) -> float:
    return pct(value - baseline, baseline)


def fmt_float(value: object, digits: int = 4) -> str:
    if value is None:
        return ""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(fval):
        return ""
    return f"{fval:.{digits}f}"


def fmt_pct(value: object, digits: int = 2) -> str:
    if value is None:
        return ""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(fval):
        return ""
    return f"{fval:.{digits}f}%"


def read_json(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def ensure_inputs(artifact: Artifact) -> None:
    if artifact.dataset not in {"lastfm", "ml1m"}:
        raise ValueError(f"Dataset is not allowed in this ablation: {artifact.dataset}")
    required = [
        artifact.paths_dir / "uid_topk.csv",
        artifact.paths_dir / "uid_pid_explanation.csv",
        artifact.paths_dir / "pred_paths.csv",
        artifact.export_validation_json,
        artifact.accuracy_json,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required ablation inputs:\n" + "\n".join(missing))

    validation = read_json(artifact.export_validation_json)
    if validation.get("status") != "PASS":
        raise ValueError(f"Export validation is not PASS: {artifact.export_validation_json}")
    accuracy = read_json(artifact.accuracy_json)
    if accuracy.get("status") != "PASS":
        raise ValueError(f"Accuracy validation is not PASS: {artifact.accuracy_json}")


def mean(values: Sequence[float]) -> float:
    if not values:
        return float("nan")
    return sum(values) / len(values)


def normalize_path(path_str: str) -> Tuple[Tuple[str, str, str], ...]:
    tokens = path_str.split()
    if len(tokens) % 3 != 0:
        raise ValueError(f"Malformed path string: {path_str}")
    return tuple(
        (tokens[idx], tokens[idx + 1], tokens[idx + 2])
        for idx in range(0, len(tokens), 3)
    )


def render_path(path: Tuple[Tuple[str, str, str], ...]) -> str:
    return " ".join(part for triple in path for part in triple)


def strict_path_type(path: Tuple[Tuple[str, str, str], ...]) -> str:
    if not path:
        return "unknown"
    return path[-1][0]


def interaction_id(path: Tuple[Tuple[str, str, str], ...]) -> Optional[int]:
    if len(path) < 2:
        return None
    try:
        return int(path[1][2])
    except ValueError:
        return None


def related_entity(path: Tuple[Tuple[str, str, str], ...]) -> Tuple[str, Optional[int]]:
    if len(path) < 2:
        return "unknown", None
    try:
        return path[-2][1], int(path[-2][2])
    except ValueError:
        return path[-2][1], None


def load_label_sets(labels_dir: Path, split: str = "test") -> Dict[int, Set[int]]:
    with (labels_dir / f"{split}_label.pkl").open("rb") as handle:
        return {
            int(uid): {int(pid) for pid in pids}
            for uid, pids in pickle.load(handle).items()
        }


def load_user_mapping(dataset: str) -> Dict[int, int]:
    path = Path("xrecsys/datasets") / dataset / "mappings/user_mappings.txt"
    mapping: Dict[int, int] = {}
    with path.open() as handle:
        next(handle, None)
        for line in handle:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            kg_uid = int(parts[0])
            raw_uid = int(parts[1])
            mapping[raw_uid] = kg_uid
    return mapping


def load_product_mapping(dataset: str) -> Dict[int, int]:
    path = Path("xrecsys/datasets") / dataset / "mappings/product_mappings.txt"
    mapping: Dict[int, int] = {}
    with path.open() as handle:
        next(handle, None)
        for line in handle:
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            kg_pid = int(parts[0])
            raw_pid = int(parts[1])
            mapping[raw_pid] = kg_pid
    return mapping


def load_uid_pid_timestamp(dataset: str) -> Dict[int, Dict[int, int]]:
    user_mapping = load_user_mapping(dataset)
    product_mapping = load_product_mapping(dataset)
    train_path = Path("xrecsys/datasets") / dataset / "train.txt"
    uid_pid_timestamp: Dict[int, Dict[int, int]] = {}
    with train_path.open() as handle:
        for line in handle:
            parts = line.strip().split()
            if not parts:
                continue
            raw_uid = int(parts[0])
            raw_pid = int(parts[1])
            if raw_uid not in user_mapping or raw_pid not in product_mapping:
                continue
            uid = user_mapping[raw_uid]
            pid = product_mapping[raw_pid]
            timestamp = int(parts[3]) if dataset == "ml1m" else int(parts[2])
            uid_pid_timestamp.setdefault(uid, {})[pid] = timestamp
    return uid_pid_timestamp


def load_pickle_dict(path: Path) -> dict:
    with path.open("rb") as handle:
        return pickle.load(handle)


def load_baseline_topk(paths_dir: Path) -> Dict[int, List[int]]:
    topk: Dict[int, List[int]] = {}
    with (paths_dir / "uid_topk.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["uid", "top10"]:
            raise ValueError(f"Unexpected uid_topk.csv columns in {paths_dir}: {reader.fieldnames}")
        for row in reader:
            topk[int(row["uid"])] = [int(value) for value in row["top10"].split() if value]
    return topk


def load_baseline_explanation_paths(
    paths_dir: Path,
) -> Tuple[
    Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]],
    Dict[int, Dict[int, str]],
]:
    explanations: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]] = {}
    explanation_text: Dict[int, Dict[int, str]] = {}
    with (paths_dir / "uid_pid_explanation.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["uid", "pid", "path"]:
            raise ValueError(
                f"Unexpected uid_pid_explanation.csv columns in {paths_dir}: {reader.fieldnames}"
            )
        for row in reader:
            uid = int(row["uid"])
            pid = int(row["pid"])
            path_text = row["path"]
            explanations.setdefault(uid, {})[pid] = normalize_path(path_text)
            explanation_text.setdefault(uid, {})[pid] = path_text
    return explanations, explanation_text


def load_candidate_paths(
    paths_dir: Path,
    original_topk: Dict[int, List[int]],
    original_explanations: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]],
    original_explanation_text: Dict[int, Dict[int, str]],
    uid_pid_timestamp: Dict[int, Dict[int, int]],
    lir_matrix: Dict[int, Dict[int, float]],
    sep_matrix: Dict[str, Dict[int, float]],
) -> Dict[int, Dict[int, List[PathCandidate]]]:
    topk_sets = {uid: set(pids[:TOPK]) for uid, pids in original_topk.items()}
    candidates: Dict[int, Dict[int, List[PathCandidate]]] = {
        uid: {pid: [] for pid in pids[:TOPK]}
        for uid, pids in original_topk.items()
    }
    with (paths_dir / "pred_paths.csv").open() as handle:
        header = handle.readline().strip().split(",")
        expected = ["uid", "pid", "path_score", "path_prob", "path"]
        if header != expected:
            raise ValueError(f"Unexpected pred_paths.csv columns in {paths_dir}: {header}")
        for line in handle:
            uid_s, pid_s, path_score_s, path_prob_s, path_text = line.rstrip("\n").split(",", 4)
            uid = int(uid_s)
            pid = int(pid_s)
            if uid not in topk_sets or pid not in topk_sets[uid]:
                continue
            path = normalize_path(path_text)
            candidates.setdefault(uid, {}).setdefault(pid, []).append(
                PathCandidate(
                    pid=pid,
                    path_score=float(path_score_s),
                    path_prob=float(path_prob_s),
                    path=path,
                    path_str=path_text,
                    path_type=strict_path_type(path),
                    lir=lir_value_from(uid_pid_timestamp, lir_matrix, path),
                    sep=sep_value_from(sep_matrix, path),
                )
            )

    for uid, pid_paths in original_explanations.items():
        for pid, path in pid_paths.items():
            if uid not in topk_sets or pid not in topk_sets[uid]:
                continue
            path_text = original_explanation_text[uid][pid]
            existing = candidates.setdefault(uid, {}).setdefault(pid, [])
            if not any(candidate.path == path for candidate in existing):
                existing.append(
                    PathCandidate(
                        pid=pid,
                        path_score=0.0,
                        path_prob=0.0,
                        path=path,
                        path_str=path_text,
                        path_type=strict_path_type(path),
                        lir=lir_value_from(uid_pid_timestamp, lir_matrix, path),
                        sep=sep_value_from(sep_matrix, path),
                    )
                )
    for uid_candidates in candidates.values():
        for pid, pid_candidates in list(uid_candidates.items()):
            if not pid_candidates:
                continue
            scores = [candidate.path_score for candidate in pid_candidates]
            min_score = min(scores)
            max_score = max(scores)
            for candidate in pid_candidates:
                if max_score == min_score:
                    candidate.score_norm = 1.0
                else:
                    candidate.score_norm = (candidate.path_score - min_score) / (max_score - min_score)

    # A second pass keeps only candidates that can win on the fixed alpha grid.
    # This is exact for the reported 0.05 grid and avoids repeatedly scanning
    # thousands of dominated paths during the sweep.
    for uid, uid_candidates in candidates.items():
        for pid, pid_candidates in list(uid_candidates.items()):
            if not pid_candidates:
                continue
            original_path = original_explanations.get(uid, {}).get(pid)
            keep: Dict[int, PathCandidate] = {}
            for candidate in pid_candidates:
                if candidate.path == original_path:
                    keep[id(candidate)] = candidate

            for metric in ("LIR", "SEP"):
                for alpha in EXPECTED_ALPHAS:
                    def metric_score(candidate: PathCandidate) -> Tuple[float, float, float]:
                        metric_component = candidate.lir if metric == "LIR" else candidate.sep
                        original_bonus = 1.0 if candidate.path == original_path else 0.0
                        return (
                            (1.0 - alpha) * candidate.score_norm + alpha * metric_component,
                            original_bonus,
                            candidate.path_prob,
                        )

                    winner = max(pid_candidates, key=metric_score)
                    keep[id(winner)] = winner

            by_type: Dict[str, PathCandidate] = {}
            for candidate in pid_candidates:
                original_bonus = 1.0 if candidate.path == original_path else 0.0
                current = by_type.get(candidate.path_type)
                key = (candidate.score_norm, original_bonus, candidate.path_prob)
                if current is None:
                    by_type[candidate.path_type] = candidate
                else:
                    current_bonus = 1.0 if current.path == original_path else 0.0
                    current_key = (current.score_norm, current_bonus, current.path_prob)
                    if key > current_key:
                        by_type[candidate.path_type] = candidate
            for candidate in by_type.values():
                keep[id(candidate)] = candidate

            uid_candidates[pid] = list(keep.values())
    return candidates


def load_strict_path_data(artifact: Artifact) -> StrictPathData:
    validation = read_json(artifact.export_validation_json)
    labels_dir = Path(validation["labels_dir"])
    if not labels_dir.is_absolute():
        labels_dir = Path.cwd() / labels_dir
    original_topk = load_baseline_topk(artifact.paths_dir)
    original_explanations, original_explanation_text = load_baseline_explanation_paths(
        artifact.paths_dir
    )
    uid_pid_timestamp = load_uid_pid_timestamp(artifact.dataset)
    lir_matrix = load_pickle_dict(Path("xrecsys/models/PGPR/tmp") / artifact.dataset / "lir_matrix.pkl")
    sep_matrix = load_pickle_dict(Path("xrecsys/models/PGPR/tmp") / artifact.dataset / "sep_matrix.pkl")
    candidate_paths = load_candidate_paths(
        artifact.paths_dir,
        original_topk,
        original_explanations,
        original_explanation_text,
        uid_pid_timestamp,
        lir_matrix,
        sep_matrix,
    )
    return StrictPathData(
        dataset=artifact.dataset,
        dataset_label=artifact.dataset_label,
        original_topk=original_topk,
        original_explanations=original_explanations,
        original_explanation_text=original_explanation_text,
        candidate_paths=candidate_paths,
        test_labels=load_label_sets(labels_dir, "test"),
        uid_pid_timestamp=uid_pid_timestamp,
        lir_matrix=lir_matrix,
        sep_matrix=sep_matrix,
    )


def read_overall_table(path: Path) -> Dict[float, Dict[str, float]]:
    by_alpha: Dict[float, Dict[str, float]] = {}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        expected = {"alpha", "metric", "group", "data"}
        if not expected.issubset(reader.fieldnames or []):
            raise ValueError(f"Malformed result CSV: {path}")
        for row in reader:
            if row["group"] != "Overall":
                continue
            alpha = round(float(row["alpha"]), 2)
            metric = row["metric"]
            if metric not in ALL_METRICS:
                continue
            by_alpha.setdefault(alpha, {})[metric] = float(row["data"])
    return by_alpha


def validate_alpha_table(path: Path, by_alpha: Dict[float, Dict[str, float]]) -> None:
    found = sorted(by_alpha)
    if found != EXPECTED_ALPHAS:
        raise ValueError(f"Incomplete alpha sweep in {path}: found={found}")
    for alpha in EXPECTED_ALPHAS:
        missing = [metric for metric in ALL_METRICS if metric not in by_alpha[alpha]]
        if missing:
            raise ValueError(f"Missing metrics for alpha={alpha} in {path}: {missing}")


def ndcg_at_10(hits: Sequence[int], relevant_count: int) -> float:
    if relevant_count <= 0:
        return 0.0
    dcg = sum(value / math.log2(rank + 2) for rank, value in enumerate(hits[:TOPK]))
    ideal_hits = min(TOPK, relevant_count)
    idcg = sum(1.0 / math.log2(rank + 2) for rank in range(ideal_hits))
    return dcg / idcg if idcg else 0.0


def evaluate_canonical_rec(
    topk: Dict[int, List[int]],
    test_labels: Dict[int, Set[int]],
) -> Dict[str, float]:
    values = {metric: [] for metric in REC_METRICS}
    for uid, relevant in test_labels.items():
        pids = topk.get(uid, [])[:TOPK]
        hits = [1 if pid in relevant else 0 for pid in pids]
        hit_count = sum(hits)
        values["ndcg"].append(ndcg_at_10(hits, len(relevant)))
        values["hr"].append(1.0 if hit_count > 0 else 0.0)
        values["precision"].append(hit_count / TOPK)
        values["recall"].append(hit_count / len(relevant) if relevant else 0.0)
    return {metric: mean(scores) for metric, scores in values.items()}


def lir_value_from(
    uid_pid_timestamp: Dict[int, Dict[int, int]],
    lir_matrix: Dict[int, Dict[int, float]],
    path: Tuple[Tuple[str, str, str], ...],
) -> float:
    if not path:
        return 0.0
    try:
        uid = int(path[0][2])
    except ValueError:
        return 0.0
    interaction = interaction_id(path)
    if interaction is None:
        return 0.0
    timestamp = uid_pid_timestamp.get(uid, {}).get(interaction)
    if timestamp is None:
        return 0.0
    return float(lir_matrix.get(uid, {}).get(timestamp, 0.0))


def sep_value_from(
    sep_matrix: Dict[str, Dict[int, float]],
    path: Tuple[Tuple[str, str, str], ...],
) -> float:
    entity_type, entity_id = related_entity(path)
    if entity_id is None:
        return 0.0
    return float(sep_matrix.get(entity_type, {}).get(entity_id, 0.0))


def lir_value(data: StrictPathData, path: Tuple[Tuple[str, str, str], ...]) -> float:
    return lir_value_from(data.uid_pid_timestamp, data.lir_matrix, path)


def sep_value(data: StrictPathData, path: Tuple[Tuple[str, str, str], ...]) -> float:
    return sep_value_from(data.sep_matrix, path)


def explanation_value(
    data: StrictPathData,
    metric: str,
    path: Tuple[Tuple[str, str, str], ...],
) -> float:
    if metric == "LIR":
        return lir_value(data, path)
    if metric == "SEP":
        return sep_value(data, path)
    raise ValueError(f"Unsupported single-path explanation metric: {metric}")


def evaluate_explanation_metrics(
    data: StrictPathData,
    topk: Dict[int, List[int]],
    explanations: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]],
) -> Dict[str, float]:
    lir_scores: List[float] = []
    sep_scores: List[float] = []
    etd_scores: List[float] = []
    total_path_types = TOTAL_PATH_TYPES[data.dataset]

    for uid, relevant in data.test_labels.items():
        if uid not in topk:
            continue
        user_paths = explanations.get(uid, {})
        user_lir: List[float] = []
        user_sep: List[float] = []
        unique_types = set()
        for pid in topk[uid][:TOPK]:
            path = user_paths.get(pid)
            if path is None:
                continue
            user_lir.append(lir_value(data, path))
            user_sep.append(sep_value(data, path))
            unique_types.add(strict_path_type(path))
        if user_lir or uid in data.lir_matrix:
            lir_scores.append(mean(user_lir) if user_lir else 0.0)
        if user_sep:
            sep_scores.append(mean(user_sep))
        etd_scores.append(len(unique_types) / total_path_types)

    return {
        "LIR": mean(lir_scores),
        "SEP": mean(sep_scores),
        "ETD": mean(etd_scores),
    }


def evaluate_all_metrics(
    data: StrictPathData,
    topk: Dict[int, List[int]],
    explanations: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]],
) -> Dict[str, float]:
    metrics = evaluate_canonical_rec(topk, data.test_labels)
    metrics.update(evaluate_explanation_metrics(data, topk, explanations))
    return metrics


def rank_score(rank_index: int, length: int) -> float:
    if length <= 0:
        return 0.0
    return (length - rank_index) / length


def candidate_path_score_norm(candidates: Sequence[PathCandidate], candidate: PathCandidate) -> float:
    return candidate.score_norm


def original_candidate(data: StrictPathData, uid: int, pid: int) -> PathCandidate:
    path = data.original_explanations[uid][pid]
    return PathCandidate(
        pid=pid,
        path_score=0.0,
        path_prob=0.0,
        path=path,
        path_str=data.original_explanation_text[uid][pid],
        path_type=strict_path_type(path),
        score_norm=0.0,
        lir=lir_value(data, path),
        sep=sep_value(data, path),
    )


def candidates_for_pid(data: StrictPathData, uid: int, pid: int) -> List[PathCandidate]:
    candidates = list(data.candidate_paths.get(uid, {}).get(pid, []))
    if uid in data.original_explanations and pid in data.original_explanations[uid]:
        original_path = data.original_explanations[uid][pid]
        if not any(candidate.path == original_path for candidate in candidates):
            candidates.append(original_candidate(data, uid, pid))
    return candidates


def select_metric_path(
    data: StrictPathData,
    uid: int,
    pid: int,
    metric: str,
    alpha: float,
) -> PathCandidate:
    candidates = candidates_for_pid(data, uid, pid)
    if not candidates:
        return original_candidate(data, uid, pid)
    original_path = data.original_explanations[uid][pid]
    if alpha == 0:
        for candidate in candidates:
            if candidate.path == original_path:
                return candidate
        return original_candidate(data, uid, pid)

    def score(candidate: PathCandidate) -> Tuple[float, float, float]:
        metric_component = candidate.lir if metric == "LIR" else candidate.sep
        path_component = candidate_path_score_norm(candidates, candidate)
        original_bonus = 1.0 if candidate.path == original_path else 0.0
        return (
            (1.0 - alpha) * path_component + alpha * metric_component,
            original_bonus,
            candidate.path_prob,
        )

    return max(candidates, key=score)


def select_etd_path(
    data: StrictPathData,
    uid: int,
    pid: int,
    seen_types: Set[str],
    alpha: float,
) -> PathCandidate:
    candidates = candidates_for_pid(data, uid, pid)
    if not candidates:
        return original_candidate(data, uid, pid)
    original_path = data.original_explanations[uid][pid]
    if alpha == 0:
        for candidate in candidates:
            if candidate.path == original_path:
                return candidate
        return original_candidate(data, uid, pid)

    def score(candidate: PathCandidate) -> Tuple[float, float, float, float]:
        novelty = 1.0 if candidate.path_type not in seen_types else 0.0
        path_component = candidate_path_score_norm(candidates, candidate)
        original_bonus = 1.0 if candidate.path == original_path else 0.0
        return (
            alpha * novelty + 0.01 * (1.0 - alpha) * path_component,
            novelty,
            original_bonus,
            candidate.path_prob,
        )

    return max(candidates, key=score)


def strict_module_output(
    data: StrictPathData,
    optimized_metric: str,
    alpha: float,
) -> Tuple[
    Dict[int, List[int]],
    Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]],
]:
    if alpha == 0:
        return (
            {uid: list(pids) for uid, pids in data.original_topk.items()},
            {
                uid: dict(pid_paths)
                for uid, pid_paths in data.original_explanations.items()
            },
        )

    topk: Dict[int, List[int]] = {}
    explanations: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]] = {}

    for uid, original_pids in data.original_topk.items():
        pids = original_pids[:TOPK]
        if not pids:
            topk[uid] = []
            explanations[uid] = {}
            continue
        original_rank = {pid: idx for idx, pid in enumerate(pids)}

        if optimized_metric in {"LIR", "SEP"}:
            items = []
            for pid in pids:
                if uid not in data.original_explanations or pid not in data.original_explanations[uid]:
                    continue
                selected = select_metric_path(data, uid, pid, optimized_metric, alpha)
                metric_component = selected.lir if optimized_metric == "LIR" else selected.sep
                base_component = rank_score(original_rank[pid], len(pids))
                combined = (1.0 - alpha) * base_component + alpha * metric_component
                items.append((combined, -original_rank[pid], pid, selected))
            items.sort(reverse=True)
            topk[uid] = [pid for _, _, pid, _ in items]
            explanations[uid] = {pid: selected.path for _, _, pid, selected in items}
            continue

        if optimized_metric != "ETD":
            raise ValueError(f"Unknown optimized metric: {optimized_metric}")

        remaining = set(pids)
        seen_types: Set[str] = set()
        ordered: List[int] = []
        selected_paths: Dict[int, Tuple[Tuple[str, str, str], ...]] = {}
        while remaining:
            best_key: Optional[Tuple[float, float, int, int]] = None
            best_pid: Optional[int] = None
            best_selected: Optional[PathCandidate] = None
            for pid in remaining:
                if uid not in data.original_explanations or pid not in data.original_explanations[uid]:
                    continue
                selected = select_etd_path(data, uid, pid, seen_types, alpha)
                novelty = 1.0 if selected.path_type not in seen_types else 0.0
                base_component = rank_score(original_rank[pid], len(pids))
                path_component = selected.score_norm
                combined = (
                    (1.0 - alpha) * base_component
                    + alpha * novelty
                    + 0.001 * alpha * path_component
                )
                candidate_key = (combined, novelty, -original_rank[pid], pid)
                if best_key is None or candidate_key > best_key:
                    best_key = candidate_key
                    best_pid = pid
                    best_selected = selected
            if best_pid is None or best_selected is None:
                for pid in sorted(remaining, key=lambda value: original_rank[value]):
                    ordered.append(pid)
                    selected_paths[pid] = data.original_explanations[uid][pid]
                break
            ordered.append(best_pid)
            selected_paths[best_pid] = best_selected.path
            seen_types.add(best_selected.path_type)
            remaining.remove(best_pid)
        topk[uid] = ordered
        explanations[uid] = selected_paths

    return topk, explanations


def exact_topk_match(left: Dict[int, List[int]], right: Dict[int, List[int]]) -> Tuple[int, int]:
    users = sorted(set(left) | set(right))
    exact = sum(1 for uid in users if left.get(uid, [])[:TOPK] == right.get(uid, [])[:TOPK])
    return exact, len(users)


def exact_explanation_match(
    left: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]],
    right: Dict[int, Dict[int, Tuple[Tuple[str, str, str], ...]]],
    topk: Dict[int, List[int]],
) -> Tuple[int, int]:
    total = 0
    exact = 0
    for uid, pids in topk.items():
        for pid in pids[:TOPK]:
            total += 1
            if left.get(uid, {}).get(pid) == right.get(uid, {}).get(pid):
                exact += 1
    return exact, total


def build_alpha0_validation_rows(
    artifact: Artifact,
    data: StrictPathData,
    baseline_metrics: Dict[str, float],
) -> List[dict]:
    rows = []
    for optimized_metric in EXP_METRICS:
        topk, explanations = strict_module_output(data, optimized_metric, 0.0)
        metrics = evaluate_all_metrics(data, topk, explanations)
        exact_users, total_users = exact_topk_match(data.original_topk, topk)
        exact_paths, total_paths = exact_explanation_match(
            data.original_explanations, explanations, data.original_topk
        )
        max_metric_delta = max(
            abs(metrics[metric] - baseline_metrics[metric])
            for metric in ALL_METRICS
        )
        rows.append({
            "dataset": artifact.dataset_label,
            "model": artifact.model,
            "role": artifact.role,
            "optimized_metric": optimized_metric,
            "alpha": 0.0,
            "exact_topk_users": exact_users,
            "topk_users": total_users,
            "exact_topk_pct": pct(exact_users, total_users),
            "exact_explanation_pairs": exact_paths,
            "explanation_pairs": total_paths,
            "exact_explanation_pct": pct(exact_paths, total_paths),
            "max_metric_abs_delta_vs_original": max_metric_delta,
            "status": "PASS" if exact_users == total_users and exact_paths == total_paths and max_metric_delta == 0 else "FAIL",
        })
    return rows


def write_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def build_main_ablation_rows(tradeoff_rows: Sequence[dict]) -> List[dict]:
    rows = []
    for row in tradeoff_rows:
        recommended_use = "main ablation table"
        if str(row.get("constraint", "")).startswith("no alpha"):
            recommended_use = "endpoint exception; discuss separately"
        rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "role": row["role"],
            "module_target": row["optimized_metric"],
            "selected_alpha": row["alpha"],
            "selection_rule": row["constraint"],
            "ndcg_retention_pct": row["ndcg_retention_pct"],
            "explanation_gain_pct": row["optimized_metric_gain_pct"],
            "sweep_ndcg": row["ndcg"],
            "explanation_metric_value": row[row["optimized_metric"]],
            "ndcg_scope": row["ndcg_scope"],
            "recommended_use": recommended_use,
        })
    return rows


def rows_to_markdown(rows: Sequence[dict], columns: Sequence[Tuple[str, str]]) -> str:
    header = "| " + " | ".join(label for _, label in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, divider]
    for row in rows:
        values = []
        for key, _ in columns:
            value = row.get(key, "")
            values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def endpoint_row(
    artifact: Artifact,
    module: str,
    opt_metric: str,
    alpha: float,
    metrics: Dict[str, float],
    baseline: Dict[str, float],
) -> dict:
    row = {
        "dataset": artifact.dataset_label,
        "model": artifact.model,
        "role": artifact.role,
        "module": module,
        "optimized_metric": opt_metric,
        "alpha": alpha,
        "sweep_protocol": artifact.sweep_protocol,
        "ndcg_scope": artifact.ndcg_scope,
    }
    for metric in ALL_METRICS:
        row[metric] = metrics.get(metric, float("nan"))
        row[f"{metric}_delta_pct"] = pct_change(metrics.get(metric, float("nan")), baseline.get(metric, float("nan")))
    return row


def build_ablation_tables(
    artifacts: Sequence[Artifact],
    case_user_limit: Optional[int] = None,
) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict], List[dict]]:
    endpoint_rows: List[dict] = []
    curve_rows: List[dict] = []
    tradeoff_rows: List[dict] = []
    provenance_rows: List[dict] = []
    alpha0_validation_rows: List[dict] = []
    cases: List[dict] = []

    for artifact in artifacts:
        print(f"Processing strict ablation: {artifact.dataset_label}/{artifact.model}", flush=True)
        ensure_inputs(artifact)
        validation = read_json(artifact.export_validation_json)
        accuracy = read_json(artifact.accuracy_json)
        data = load_strict_path_data(artifact)
        baseline = evaluate_all_metrics(
            data,
            data.original_topk,
            data.original_explanations,
        )
        alpha0_rows = build_alpha0_validation_rows(artifact, data, baseline)
        alpha0_validation_rows.extend(alpha0_rows)
        alpha0_status = "PASS" if all(row["status"] == "PASS" for row in alpha0_rows) else "FAIL"

        provenance_rows.append({
            "dataset": artifact.dataset_label,
            "model": artifact.model,
            "role": artifact.role,
            "export_status": validation.get("status"),
            "accuracy_status": accuracy.get("status"),
            "canonical_test_users": validation.get("canonical_test_users"),
            "topk_users": validation.get("topk_users"),
            "candidate_users": validation.get("candidate_users"),
            "explanations": validation.get("explanations"),
            "pred_path_rows": validation.get("pred_path_rows"),
            "accuracy_hr": accuracy.get("metrics", {}).get("hr"),
            "accuracy_ndcg": accuracy.get("metrics", {}).get("ndcg"),
            "accuracy_precision": accuracy.get("metrics", {}).get("precision"),
            "accuracy_recall": accuracy.get("metrics", {}).get("recall"),
            "strict_baseline_hr": baseline["hr"],
            "strict_baseline_ndcg": baseline["ndcg"],
            "strict_baseline_precision": baseline["precision"],
            "strict_baseline_recall": baseline["recall"],
            "strict_accuracy_max_abs_delta": max(
                abs(baseline[metric] - float(accuracy.get("metrics", {}).get(metric, float("nan"))))
                for metric in REC_METRICS
            ),
            "alpha0_preservation_status": alpha0_status,
            "slot_coverage": accuracy.get("recommendation_coverage", {}).get("slot_coverage"),
            "sweep_protocol": artifact.sweep_protocol,
            "ndcg_scope": artifact.ndcg_scope,
            "result_dir": str(artifact.result_dir),
            "paths_dir": str(artifact.paths_dir),
        })

        endpoint_rows.append(endpoint_row(artifact, "Original recommender", "none", 0.0, baseline, baseline))

        for exp_metric in EXP_METRICS:
            sweep: Dict[float, Dict[str, float]] = {}
            for alpha in EXPECTED_ALPHAS:
                topk, explanations = strict_module_output(data, exp_metric, alpha)
                sweep[alpha] = evaluate_all_metrics(data, topk, explanations)

            endpoint_rows.append(
                endpoint_row(
                    artifact,
                    "Recommender + proposed explanation/path module",
                    exp_metric,
                    1.0,
                    sweep[1.0],
                    baseline,
                )
            )

            best: Optional[dict] = None
            for alpha in EXPECTED_ALPHAS:
                metrics = sweep[alpha]
                ndcg_retention = pct(metrics["ndcg"], baseline["ndcg"])
                exp_gain = pct_change(metrics[exp_metric], baseline[exp_metric])
                curve_row = {
                    "dataset": artifact.dataset_label,
                    "model": artifact.model,
                    "role": artifact.role,
                    "optimized_metric": exp_metric,
                    "alpha": alpha,
                    "ndcg_retention_pct": ndcg_retention,
                    "optimized_metric_gain_pct": exp_gain,
                    "sweep_protocol": artifact.sweep_protocol,
                    "ndcg_scope": artifact.ndcg_scope,
                }
                for metric in ALL_METRICS:
                    curve_row[metric] = metrics[metric]
                    curve_row[f"{metric}_delta_pct"] = pct_change(metrics[metric], baseline[metric])
                curve_rows.append(curve_row)

                candidate = {
                    "dataset": artifact.dataset_label,
                    "model": artifact.model,
                    "role": artifact.role,
                    "optimized_metric": exp_metric,
                    "alpha": alpha,
                    "constraint": "max explanation gain with NDCG retention >= 95%",
                    "ndcg_retention_pct": ndcg_retention,
                    "optimized_metric_gain_pct": exp_gain,
                    "sweep_protocol": artifact.sweep_protocol,
                    "ndcg_scope": artifact.ndcg_scope,
                }
                for metric in ALL_METRICS:
                    candidate[metric] = metrics[metric]
                    candidate[f"{metric}_delta_pct"] = pct_change(metrics[metric], baseline[metric])
                if ndcg_retention >= 95.0:
                    if best is None or (
                        candidate["optimized_metric_gain_pct"],
                        candidate["alpha"],
                    ) > (
                        best["optimized_metric_gain_pct"],
                        best["alpha"],
                    ):
                        best = candidate

            if best is None:
                endpoint = sweep[1.0]
                best = {
                    "dataset": artifact.dataset_label,
                    "model": artifact.model,
                    "role": artifact.role,
                    "optimized_metric": exp_metric,
                    "alpha": 1.0,
                    "constraint": "no alpha retained >=95% NDCG; reporting alpha=1 endpoint",
                    "ndcg_retention_pct": pct(endpoint["ndcg"], baseline["ndcg"]),
                    "optimized_metric_gain_pct": pct_change(endpoint[exp_metric], baseline[exp_metric]),
                    "sweep_protocol": artifact.sweep_protocol,
                    "ndcg_scope": artifact.ndcg_scope,
                }
                for metric in ALL_METRICS:
                    best[metric] = endpoint[metric]
                    best[f"{metric}_delta_pct"] = pct_change(endpoint[metric], baseline[metric])
            tradeoff_rows.append(best)
        if case_user_limit is not None:
            cases.append(build_case_from_data(artifact, data, case_user_limit))

    return endpoint_rows, curve_rows, tradeoff_rows, provenance_rows, alpha0_validation_rows, cases


def metric_at(rows: Sequence[dict], dataset: str, model: str, exp_metric: str) -> List[dict]:
    return [
        row for row in rows
        if row["dataset"] == dataset and row["model"] == model and row["optimized_metric"] == exp_metric
    ]


def nice_num(value: float) -> str:
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def scale(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
    if src_max == src_min:
        return (dst_min + dst_max) / 2.0
    return dst_min + (value - src_min) / (src_max - src_min) * (dst_max - dst_min)


def svg_polyline(points: Sequence[Tuple[float, float]], color: str) -> str:
    data = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline points="{data}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'


def render_tradeoff_svg(curve_rows: Sequence[dict], dataset_label: str, out_path: Path) -> None:
    colors = {"PGPR": "#1565C0", "UCPR": "#C62828"}
    width = 1180
    height = 480
    margin_left = 72
    panel_gap = 48
    panel_width = (width - margin_left - 42 - 2 * panel_gap) / 3
    panel_height = 285
    panel_top = 96
    panel_bottom = panel_top + panel_height
    title = f"{dataset_label}: Performance-explainability tradeoff"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#212121">{html.escape(title)}</text>',
        '<text x="32" y="60" font-family="Arial, sans-serif" font-size="13" fill="#555">Y axis: strict canonical NDCG retention vs Original. X axis: optimized explanation gain. Markers show alpha=0 and alpha=1.</text>',
    ]
    if dataset_label == "LastFM":
        parts.append('<text x="32" y="76" font-family="Arial, sans-serif" font-size="12" fill="#777">LastFM legacy sweep NDCG is excluded; this figure uses the strict canonical baseline-preserving protocol.</text>')

    for idx, exp_metric in enumerate(EXP_METRICS):
        panel_left = margin_left + idx * (panel_width + panel_gap)
        panel_right = panel_left + panel_width
        panel_rows = [row for row in curve_rows if row["dataset"] == dataset_label and row["optimized_metric"] == exp_metric]
        x_values = [float(row["optimized_metric_gain_pct"]) for row in panel_rows]
        y_values = [float(row["ndcg_retention_pct"]) for row in panel_rows]
        x_min = min([0.0] + x_values)
        x_max = max([1.0] + x_values)
        y_min = min([95.0] + y_values)
        y_max = max([101.0] + y_values)
        x_pad = max(1.0, (x_max - x_min) * 0.08)
        y_pad = max(0.5, (y_max - y_min) * 0.08)
        x_min -= x_pad
        x_max += x_pad
        y_min -= y_pad
        y_max += y_pad

        parts.extend([
            f'<rect x="{panel_left:.2f}" y="{panel_top}" width="{panel_width:.2f}" height="{panel_height}" fill="#fafafa" stroke="#dddddd"/>',
            f'<text x="{(panel_left + panel_right) / 2:.2f}" y="{panel_top - 18}" font-family="Arial, sans-serif" font-size="16" font-weight="700" text-anchor="middle" fill="#212121">{exp_metric}</text>',
        ])
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            x = panel_left + frac * panel_width
            y = panel_top + frac * panel_height
            parts.append(f'<line x1="{x:.2f}" y1="{panel_top}" x2="{x:.2f}" y2="{panel_bottom}" stroke="#e6e6e6" stroke-width="1"/>')
            parts.append(f'<line x1="{panel_left:.2f}" y1="{y:.2f}" x2="{panel_right:.2f}" y2="{y:.2f}" stroke="#e6e6e6" stroke-width="1"/>')
        y95 = scale(95.0, y_min, y_max, panel_bottom, panel_top)
        parts.append(f'<line x1="{panel_left:.2f}" y1="{y95:.2f}" x2="{panel_right:.2f}" y2="{y95:.2f}" stroke="#777" stroke-width="1.2" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{panel_right - 4:.2f}" y="{y95 - 5:.2f}" font-family="Arial, sans-serif" font-size="11" text-anchor="end" fill="#555">95%</text>')

        for model in ("PGPR", "UCPR"):
            rows = sorted(
                [row for row in panel_rows if row["model"] == model],
                key=lambda row: float(row["alpha"]),
            )
            points = [
                (
                    scale(float(row["optimized_metric_gain_pct"]), x_min, x_max, panel_left, panel_right),
                    scale(float(row["ndcg_retention_pct"]), y_min, y_max, panel_bottom, panel_top),
                )
                for row in rows
            ]
            if not points:
                continue
            color = colors[model]
            parts.append(svg_polyline(points, color))
            x0, y0 = points[0]
            x1, y1 = points[-1]
            parts.append(f'<circle cx="{x0:.2f}" cy="{y0:.2f}" r="4.6" fill="{color}" stroke="#fff" stroke-width="1.4"/>')
            parts.append(f'<rect x="{x1 - 4.8:.2f}" y="{y1 - 4.8:.2f}" width="9.6" height="9.6" fill="{color}" stroke="#fff" stroke-width="1.4"/>')

        parts.extend([
            f'<text x="{panel_left:.2f}" y="{panel_bottom + 28}" font-family="Arial, sans-serif" font-size="12" fill="#444">{nice_num(x_min)}%</text>',
            f'<text x="{panel_right:.2f}" y="{panel_bottom + 28}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#444">{nice_num(x_max)}%</text>',
            f'<text x="{(panel_left + panel_right) / 2:.2f}" y="{panel_bottom + 44}" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#444">{exp_metric} gain (%)</text>',
            f'<text x="{panel_left - 10:.2f}" y="{panel_bottom:.2f}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#444">{nice_num(y_min)}%</text>',
            f'<text x="{panel_left - 10:.2f}" y="{panel_top + 4:.2f}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#444">{nice_num(y_max)}%</text>',
        ])
        if idx == 0:
            parts.append(f'<text x="22" y="{(panel_top + panel_bottom) / 2:.2f}" font-family="Arial, sans-serif" font-size="13" text-anchor="middle" fill="#444" transform="rotate(-90 22 {(panel_top + panel_bottom) / 2:.2f})">NDCG retention (%)</text>')

    legend_y = height - 28
    legend_x = 430
    for offset, model in enumerate(("PGPR", "UCPR")):
        x = legend_x + offset * 125
        color = colors[model]
        parts.append(f'<line x1="{x}" y1="{legend_y}" x2="{x + 26}" y2="{legend_y}" stroke="{color}" stroke-width="2.6"/>')
        parts.append(f'<circle cx="{x + 13}" cy="{legend_y}" r="4" fill="{color}" stroke="#fff" stroke-width="1"/>')
        parts.append(f'<text x="{x + 34}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="13" fill="#333">{model}</text>')
    parts.append(f'<circle cx="{legend_x + 265}" cy="{legend_y}" r="4.6" fill="#555" stroke="#fff" stroke-width="1"/>')
    parts.append(f'<text x="{legend_x + 276}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="13" fill="#333">alpha=0</text>')
    parts.append(f'<rect x="{legend_x + 352}" y="{legend_y - 4.8}" width="9.6" height="9.6" fill="#555" stroke="#fff" stroke-width="1"/>')
    parts.append(f'<text x="{legend_x + 367}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="13" fill="#333">alpha=1</text>')
    parts.append("</svg>")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts) + "\n")


def path_type(path: str) -> str:
    tokens = path.split()
    if len(tokens) < 3:
        return "unknown"
    return tokens[-3]


def baseline_topk(paths_dir: Path) -> Dict[int, List[int]]:
    topk: Dict[int, List[int]] = {}
    with (paths_dir / "uid_topk.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            values = [int(value) for value in row["top10"].split() if value]
            topk[int(row["uid"])] = values
    return topk


def baseline_explanations(paths_dir: Path) -> Dict[int, Dict[int, str]]:
    explanations: Dict[int, Dict[int, str]] = {}
    with (paths_dir / "uid_pid_explanation.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            uid = int(row["uid"])
            pid = int(row["pid"])
            explanations.setdefault(uid, {})[pid] = row["path"]
    return explanations


def select_etd_candidates(candidates: Sequence[dict], limit: int = 10) -> List[dict]:
    bins: Dict[str, List[dict]] = {}
    for candidate in candidates:
        bins.setdefault(candidate["path_type"], []).append(candidate)
    for path_list in bins.values():
        path_list.sort(key=lambda item: item["path_score"], reverse=True)

    selected: List[dict] = []
    selected_pids = set()
    seen_types = set()
    while len(selected) < limit and bins:
        best_type = ""
        best_score = -float("inf")
        for current_type, path_list in list(bins.items()):
            while path_list and path_list[0]["pid"] in selected_pids:
                path_list.pop(0)
            if not path_list:
                bins.pop(current_type, None)
                continue
            candidate = path_list[0]
            bonus = 1.0 if current_type not in seen_types else 0.0
            score = candidate["path_score"] + bonus
            if score > best_score:
                best_score = score
                best_type = current_type
        if not best_type:
            break
        chosen = bins[best_type].pop(0)
        selected.append(chosen)
        selected_pids.add(chosen["pid"])
        seen_types.add(best_type)
        if not bins.get(best_type):
            bins.pop(best_type, None)

    for candidate in sorted(candidates, key=lambda item: item["path_score"], reverse=True):
        if len(selected) >= limit:
            break
        if candidate["pid"] in selected_pids:
            continue
        selected.append(candidate)
        selected_pids.add(candidate["pid"])

    return sorted(selected, key=lambda item: item["path_score"], reverse=True)


def compact_items(items: Sequence[dict], limit: int = 10) -> List[dict]:
    compact = []
    for rank, item in enumerate(items[:limit], start=1):
        compact.append({
            "rank": rank,
            "pid": item["pid"],
            "path_type": item["path_type"],
            "path_score": item.get("path_score"),
            "path": item["path"],
        })
    return compact


def build_case_from_data(artifact: Artifact, data: StrictPathData, max_completed_users: int) -> dict:
    module_topk, module_explanations = strict_module_output(data, "ETD", 1.0)
    best_case: Optional[dict] = None

    def item_record(uid: int, pid: int, path: Tuple[Tuple[str, str, str], ...], score: Optional[float]) -> dict:
        return {
            "pid": pid,
            "path_type": strict_path_type(path),
            "path_score": score,
            "path": render_path(path),
        }

    def evaluate(uid: int) -> Optional[dict]:
        if uid not in data.original_topk or uid not in data.original_explanations:
            return None
        original_items = []
        for pid in data.original_topk[uid][:TOPK]:
            path = data.original_explanations[uid].get(pid)
            if path is None:
                continue
            original_items.append(item_record(uid, pid, path, None))
        if len(original_items) < 5:
            return None

        module_items = []
        for pid in module_topk.get(uid, [])[:TOPK]:
            path = module_explanations.get(uid, {}).get(pid)
            if path is None:
                continue
            score = None
            for candidate in candidates_for_pid(data, uid, pid):
                if candidate.path == path:
                    score = candidate.path_score
                    break
            module_items.append(item_record(uid, pid, path, score))
        if len(module_items) < 5:
            return None
        original_types = {item["path_type"] for item in original_items}
        module_types = {item["path_type"] for item in module_items}
        original_pids = [item["pid"] for item in original_items]
        module_pids = [item["pid"] for item in module_items]
        gain = len(module_types) - len(original_types)
        changed = sum(1 for left, right in zip(original_pids, module_pids) if left != right)
        if len(module_pids) > len(original_pids):
            changed += len(module_pids) - len(original_pids)
        return {
            "dataset": artifact.dataset_label,
            "model": artifact.model,
            "role": artifact.role,
            "user_id": uid,
            "case_type": "qualitative explanation case",
            "quantitative_use": "illustration only; strict alpha=0 preservation is validated separately",
            "module": "strict baseline-preserving ETD path module at alpha=1",
            "original_unique_path_types": len(original_types),
            "module_unique_path_types": len(module_types),
            "unique_path_type_gain": gain,
            "changed_top10_positions": changed,
            "original_top10": compact_items(original_items),
            "module_top10": compact_items(module_items),
        }

    completed = 0
    for uid in data.original_topk:
        case = evaluate(uid)
        if case is not None and (
            best_case is None or (
                case["unique_path_type_gain"],
                case["changed_top10_positions"],
            ) > (
                best_case["unique_path_type_gain"],
                best_case["changed_top10_positions"],
            )
        ):
            best_case = case
            if case["unique_path_type_gain"] > 0 and case["changed_top10_positions"] > 0:
                return case
        completed += 1
        if completed >= max_completed_users:
            break

    if best_case is None:
        raise ValueError(f"No usable explanation case found for {artifact.dataset_label}/{artifact.model}")
    return best_case


def build_case_for_artifact(artifact: Artifact, max_completed_users: int) -> dict:
    return build_case_from_data(artifact, load_strict_path_data(artifact), max_completed_users)


def write_cases(cases: Sequence[dict], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# PGPR/UCPR Path-Module Qualitative Explanation Cases",
        "",
        "Cases compare the frozen Original recommender top-10 against the strict baseline-preserving ETD path module at alpha=1.",
        "",
        "The module is constrained to the original top-k item set; alpha=0 preservation is validated in the ablation report.",
        "",
    ]
    for case in cases:
        lines.extend([
            f"## {case['dataset']} / {case['model']} / user {case['user_id']}",
            "",
            f"- Role: {case['role']}",
            f"- Case type: {case['case_type']}",
            f"- Module: {case['module']}",
            f"- Unique path types: {case['original_unique_path_types']} -> {case['module_unique_path_types']}",
            f"- Changed top-10 positions: {case['changed_top10_positions']}",
            "",
            "Original recommender sample:",
            "",
        ])
        for item in case["original_top10"]:
            lines.append(f"- rank {item['rank']}: pid={item['pid']}, type={item['path_type']}, path=`{item['path']}`")
        lines.extend(["", "Path module sample:", ""])
        for item in case["module_top10"]:
            lines.append(
                f"- rank {item['rank']}: pid={item['pid']}, type={item['path_type']}, "
                f"score={fmt_float(item['path_score'], 4)}, path=`{item['path']}`"
            )
        lines.append("")
    md_path.write_text("\n".join(lines) + "\n")


def render_report(
    out_path: Path,
    main_rows: Sequence[dict],
    endpoint_rows: Sequence[dict],
    tradeoff_rows: Sequence[dict],
    provenance_rows: Sequence[dict],
    alpha0_validation_rows: Sequence[dict],
    cases: Sequence[dict],
    figure_paths: Sequence[Path],
) -> None:
    main_md_rows = []
    for row in main_rows:
        selection = "max gain @ >=95% NDCG"
        if str(row.get("selection_rule", "")).startswith("no alpha"):
            selection = "no >=95%; alpha=1 endpoint"
        main_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "target": row["module_target"],
            "alpha": fmt_float(row["selected_alpha"], 2),
            "selection": selection,
            "retention": fmt_pct(row["ndcg_retention_pct"]),
            "gain": fmt_pct(row["explanation_gain_pct"]),
            "scope": row["ndcg_scope"],
        })

    endpoint_md_rows = []
    for row in endpoint_rows:
        endpoint_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "role": row["role"],
            "module": row["module"],
            "opt": row["optimized_metric"],
            "alpha": fmt_float(row["alpha"], 2),
            "ndcg": fmt_float(row["ndcg"], 4),
            "hr": fmt_float(row["hr"], 4),
            "precision": fmt_float(row["precision"], 4),
            "recall": fmt_float(row["recall"], 4),
            "LIR": fmt_float(row["LIR"], 4),
            "SEP": fmt_float(row["SEP"], 4),
            "ETD": fmt_float(row["ETD"], 4),
            "ndcg_delta": fmt_pct(row["ndcg_delta_pct"]),
            "opt_delta": "" if row["optimized_metric"] == "none" else fmt_pct(row[f"{row['optimized_metric']}_delta_pct"]),
        })

    tradeoff_md_rows = []
    for row in tradeoff_rows:
        constraint = "max gain @ >=95% NDCG"
        if str(row.get("constraint", "")).startswith("no alpha"):
            constraint = "no >=95%; alpha=1 endpoint"
        tradeoff_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "opt": row["optimized_metric"],
            "alpha": fmt_float(row["alpha"], 2),
            "constraint": constraint,
            "ndcg_ret": fmt_pct(row["ndcg_retention_pct"]),
            "gain": fmt_pct(row["optimized_metric_gain_pct"]),
            "ndcg": fmt_float(row["ndcg"], 4),
            "metric": fmt_float(row[row["optimized_metric"]], 4),
        })

    provenance_md_rows = []
    for row in provenance_rows:
        provenance_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "role": row["role"],
            "export": row["export_status"],
            "accuracy": row["accuracy_status"],
            "users": row["canonical_test_users"],
            "topk": row["topk_users"],
            "paths": row["pred_path_rows"],
            "coverage": fmt_float(row["slot_coverage"], 4),
            "strict_ndcg": fmt_float(row["accuracy_ndcg"], 4),
            "baseline_ndcg": fmt_float(row["strict_baseline_ndcg"], 4),
            "max_delta": fmt_float(row["strict_accuracy_max_abs_delta"], 8),
            "alpha0": row["alpha0_preservation_status"],
            "scope": row["ndcg_scope"],
        })

    alpha0_md_rows = []
    for row in alpha0_validation_rows:
        alpha0_md_rows.append({
            "dataset": row["dataset"],
            "model": row["model"],
            "target": row["optimized_metric"],
            "topk": f"{row['exact_topk_users']}/{row['topk_users']}",
            "paths": f"{row['exact_explanation_pairs']}/{row['explanation_pairs']}",
            "topk_pct": fmt_pct(row["exact_topk_pct"]),
            "path_pct": fmt_pct(row["exact_explanation_pct"]),
            "metric_delta": fmt_float(row["max_metric_abs_delta_vs_original"], 8),
            "status": row["status"],
        })

    case_md_rows = []
    for case in cases:
        case_md_rows.append({
            "dataset": case["dataset"],
            "model": case["model"],
            "user": case["user_id"],
            "types": f"{case['original_unique_path_types']} -> {case['module_unique_path_types']}",
            "changed": case["changed_top10_positions"],
        })

    lines = [
        "# PGPR/UCPR Path-Module Ablation",
        "",
        "Scope: PGPR is the main model; UCPR is the auxiliary model. Datasets are LastFM and ML-1M only.",
        "",
        "Excluded by design: Amazon-Book classic baseline is not part of this ablation. Amazon-Book remains only an auxiliary large-dataset result from the existing main experiment.",
        "",
        "The ablation is deterministic and read-only with respect to model artifacts: it consumes frozen uid_topk / uid_pid_explanation / pred_paths CSVs, canonical export validation JSON, and accuracy JSON. Legacy xrecsys alpha-sweep CSVs are not used for the main ablation because their optimizers can reconstruct top-k from the candidate pool at alpha=0.",
        "",
        "Protocol: alpha=0 must exactly preserve the original recommender top-k ranking and original explanation path for every recommended item. For alpha>0, the module may only re-rank the frozen original top-k item set and/or choose alternative paths for those same items; it cannot introduce candidate-pool replacement items.",
        "",
        "## Main Ablation Table",
        "",
        "Use this table for the main text. It selects the largest explanation gain under a >=95% strict canonical NDCG-retention rule. When no alpha meets that rule, the row is explicitly marked as an endpoint exception.",
        "",
        rows_to_markdown(
            main_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("target", "Module target"),
                ("alpha", "Selected alpha"),
                ("selection", "Selection"),
                ("retention", "NDCG retention"),
                ("gain", "Explanation gain"),
                ("scope", "NDCG scope"),
            ],
        ),
        "",
        "## Metric Scope",
        "",
        "All rows in the main ablation use strict canonical NDCG@10, HR@10, Precision@10, and Recall@10 over the validated canonical test users. The earlier LastFM legacy sweep NDCG is intentionally excluded from the main table.",
        "",
        "Strict accuracy provenance remains available below to connect these ablations to the validated main artifacts.",
        "",
        "## Alpha=0 Baseline Preservation Validation",
        "",
        "This validation is the key protocol check: every optimizer target must reproduce the frozen Original recommender exactly when alpha=0.",
        "",
        rows_to_markdown(
            alpha0_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("target", "Target"),
                ("topk", "Exact top-k users"),
                ("paths", "Exact explanation pairs"),
                ("topk_pct", "Top-k exact"),
                ("path_pct", "Path exact"),
                ("metric_delta", "Max metric delta"),
                ("status", "Status"),
            ],
        ),
        "",
        "## Tradeoff Summary",
        "",
        "This is the expanded version of the main table with selected strict-sweep NDCG and optimized metric values.",
        "",
        rows_to_markdown(
            tradeoff_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("opt", "Opt"),
                ("alpha", "Alpha"),
                ("constraint", "Selection"),
                ("ndcg_ret", "NDCG retention"),
                ("gain", "Opt gain"),
                ("ndcg", "Sweep NDCG"),
                ("metric", "Opt value"),
            ],
        ),
        "",
        "## Figures",
        "",
    ]
    for figure in figure_paths:
        lines.append(f"- {figure}")
    lines.extend([
        "",
        "## Provenance",
        "",
        rows_to_markdown(
            provenance_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("role", "Role"),
                ("export", "Export"),
                ("accuracy", "Accuracy"),
                ("users", "Canonical users"),
                ("topk", "Top-k users"),
                ("paths", "Pred path rows"),
                ("coverage", "Slot coverage"),
                ("strict_ndcg", "Validated accuracy NDCG"),
                ("baseline_ndcg", "Strict baseline NDCG"),
                ("max_delta", "Max rec delta"),
                ("alpha0", "Alpha=0 preservation"),
                ("scope", "NDCG scope"),
            ],
        ),
        "",
        "## Qualitative Explanation Cases",
        "",
        "These cases are qualitative illustrations of the strict alpha=1 ETD module; quantitative evidence is the validated alpha sweep above.",
        "",
        rows_to_markdown(
            case_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("user", "User"),
                ("types", "Unique path types"),
                ("changed", "Changed top-10 positions"),
            ],
        ),
        "",
        "Detailed cases are in `reports/cases/ablation/pgpr_ucpr_path_module_cases.md` and the companion JSON file.",
        "",
        "## Appendix: Alpha=1 Endpoint Stress Test",
        "",
        "Do not use this as the main ablation table. These rows show the extreme alpha=1 setting; large recommendation drops are expected for some targets and help characterize the performance-explainability boundary.",
        "",
        rows_to_markdown(
            endpoint_md_rows,
            [
                ("dataset", "Dataset"),
                ("model", "Model"),
                ("role", "Role"),
                ("module", "Condition"),
                ("opt", "Opt"),
                ("alpha", "Alpha"),
                ("ndcg", "NDCG"),
                ("hr", "HR"),
                ("precision", "Precision"),
                ("recall", "Recall"),
                ("LIR", "LIR"),
                ("SEP", "SEP"),
                ("ETD", "ETD"),
                ("ndcg_delta", "NDCG delta"),
                ("opt_delta", "Opt metric delta"),
            ],
        ),
        "",
    ])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PGPR/UCPR path-module ablation artifacts")
    parser.add_argument("--out-tables", default="reports/tables/ablation/pgpr_ucpr_path_module")
    parser.add_argument("--out-figures", default="reports/figures/ablation/pgpr_ucpr_path_module")
    parser.add_argument("--out-cases", default="reports/cases/ablation")
    parser.add_argument("--out-summary", default="reports/summaries/pgpr_ucpr_path_module_ablation.md")
    parser.add_argument("--case-user-limit", type=int, default=250)
    args = parser.parse_args()

    out_tables = Path(args.out_tables)
    out_figures = Path(args.out_figures)
    out_cases = Path(args.out_cases)
    out_summary = Path(args.out_summary)

    (
        endpoint_rows,
        curve_rows,
        tradeoff_rows,
        provenance_rows,
        alpha0_validation_rows,
        cases,
    ) = build_ablation_tables(ARTIFACTS, case_user_limit=args.case_user_limit)
    main_rows = build_main_ablation_rows(tradeoff_rows)

    main_fields = [
        "dataset", "model", "role", "module_target", "selected_alpha",
        "selection_rule", "ndcg_retention_pct", "explanation_gain_pct",
        "sweep_ndcg", "explanation_metric_value", "ndcg_scope", "recommended_use",
    ]
    endpoint_fields = [
        "dataset", "model", "role", "module", "optimized_metric", "alpha",
        *ALL_METRICS,
        *(f"{metric}_delta_pct" for metric in ALL_METRICS),
        "sweep_protocol", "ndcg_scope",
    ]
    curve_fields = [
        "dataset", "model", "role", "optimized_metric", "alpha",
        *ALL_METRICS,
        *(f"{metric}_delta_pct" for metric in ALL_METRICS),
        "ndcg_retention_pct", "optimized_metric_gain_pct", "sweep_protocol", "ndcg_scope",
    ]
    tradeoff_fields = [
        "dataset", "model", "role", "optimized_metric", "alpha", "constraint",
        *ALL_METRICS,
        *(f"{metric}_delta_pct" for metric in ALL_METRICS),
        "ndcg_retention_pct", "optimized_metric_gain_pct", "sweep_protocol", "ndcg_scope",
    ]
    provenance_fields = [
        "dataset", "model", "role", "export_status", "accuracy_status",
        "canonical_test_users", "topk_users", "candidate_users", "explanations",
        "pred_path_rows", "accuracy_hr", "accuracy_ndcg", "accuracy_precision",
        "accuracy_recall", "strict_baseline_hr", "strict_baseline_ndcg",
        "strict_baseline_precision", "strict_baseline_recall",
        "strict_accuracy_max_abs_delta", "alpha0_preservation_status",
        "slot_coverage", "sweep_protocol", "ndcg_scope", "result_dir", "paths_dir",
    ]
    alpha0_validation_fields = [
        "dataset", "model", "role", "optimized_metric", "alpha",
        "exact_topk_users", "topk_users", "exact_topk_pct",
        "exact_explanation_pairs", "explanation_pairs", "exact_explanation_pct",
        "max_metric_abs_delta_vs_original", "status",
    ]

    write_csv(out_tables / "main_ablation_table_95pct_ndcg.csv", main_rows, main_fields)
    write_csv(out_tables / "endpoint_comparison.csv", endpoint_rows, endpoint_fields)
    write_csv(out_tables / "tradeoff_curves_long.csv", curve_rows, curve_fields)
    write_csv(out_tables / "tradeoff_summary_95pct_ndcg.csv", tradeoff_rows, tradeoff_fields)
    write_csv(out_tables / "provenance_validation.csv", provenance_rows, provenance_fields)
    write_csv(out_tables / "alpha0_baseline_preservation.csv", alpha0_validation_rows, alpha0_validation_fields)

    figure_paths = []
    for dataset_label in ("LastFM", "ML-1M"):
        out_path = out_figures / f"{dataset_label.lower().replace('-', '')}_ndcg_tradeoff.svg"
        render_tradeoff_svg(curve_rows, dataset_label, out_path)
        figure_paths.append(out_path)

    write_cases(
        cases,
        out_cases / "pgpr_ucpr_path_module_cases.json",
        out_cases / "pgpr_ucpr_path_module_cases.md",
    )

    render_report(
        out_summary,
        main_rows,
        endpoint_rows,
        tradeoff_rows,
        provenance_rows,
        alpha0_validation_rows,
        cases,
        figure_paths,
    )

    print("Generated PGPR/UCPR path-module ablation artifacts:")
    for path in [
        out_tables / "endpoint_comparison.csv",
        out_tables / "main_ablation_table_95pct_ndcg.csv",
        out_tables / "tradeoff_curves_long.csv",
        out_tables / "tradeoff_summary_95pct_ndcg.csv",
        out_tables / "provenance_validation.csv",
        out_tables / "alpha0_baseline_preservation.csv",
        *figure_paths,
        out_cases / "pgpr_ucpr_path_module_cases.json",
        out_cases / "pgpr_ucpr_path_module_cases.md",
        out_summary,
    ]:
        print(f"  {path}")


if __name__ == "__main__":
    main()
