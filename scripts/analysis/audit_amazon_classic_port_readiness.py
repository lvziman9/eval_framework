#!/usr/bin/env python3
"""Audit whether classic native-path baselines are ready for Amazon-book."""

from __future__ import annotations

import ast
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "tables" / "amazon_classic_port_readiness.json"
OUT_MD = ROOT / "reports" / "tables" / "amazon_classic_port_readiness.md"
RUN = ROOT / "runs" / "debug_compare" / "2026-06-20_native_path_expansion"
PGPR_AMAZON_VIEW_METADATA = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_view_metadata.json"
)
PGPR_AMAZON_PREPROCESS_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_runtime_preprocess_smoke.json"
)
PGPR_AMAZON_TRANSE_FORWARD_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_transe_forward_smoke.json"
)
PGPR_AMAZON_TRANSE_TRAINING_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_transe_training_smoke.json"
)
PGPR_AMAZON_POLICY_ENV_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_policy_env_smoke.json"
)
PGPR_AMAZON_POLICY_TRAINING_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_policy_training_smoke.json"
)
PGPR_AMAZON_POLICY_INFERENCE_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_policy_inference_smoke.json"
)
PGPR_AMAZON_EXPORT_SMOKE_VALIDATION = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "pgpr"
    / "pgpr_export_smoke_validation.json"
)
PGPR_AMAZON_EXPORT_VALIDATION = RUN / "pgpr_amazon_book_kgat_export_validation.json"
PGPR_AMAZON_ACCURACY = RUN / "pgpr_amazon_book_kgat_accuracy.json"
TPREC_AMAZON_TIMESTAMP_AUDIT = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "tprec"
    / "tprec_timestamp_semantics_audit.json"
)
UCPR_AMAZON_VIEW_METADATA = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "ucpr"
    / "preprocessed"
    / "ucpr_view_metadata.json"
)
UCPR_AMAZON_PREPROCESS_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "ucpr"
    / "ucpr_runtime_preprocess_smoke.json"
)
UCPR_AMAZON_TRANSE_FORWARD_SMOKE = (
    RUN
    / "amazon_book_kgat_v1"
    / "model_views"
    / "ucpr"
    / "ucpr_transe_forward_smoke.json"
)
UCPR_AMAZON_EXPORT_VALIDATION = RUN / "ucpr_amazon_book_kgat_export_validation.json"
UCPR_AMAZON_ACCURACY = RUN / "ucpr_amazon_book_kgat_accuracy.json"
TPREC_AMAZON_HOPWISE_MANIFEST = (
    RUN
    / "hopwise_data"
    / "canonical_amazon_book_kgat_v1"
    / "hopwise_view_manifest.json"
)
MODEL_ORDER = ["PGPR", "UCPR", "CAFE", "TPRec"]


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text()


def literal_assignment(relative: str, name: str) -> Any:
    tree = ast.parse(read_text(relative), filename=relative)
    constants: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        try:
            constants[node.targets[0].id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue

    class ConstantNameResolver(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name) -> ast.AST:
            if node.id not in constants:
                return node
            replacement = ast.parse(repr(constants[node.id]), mode="eval").body
            return ast.copy_location(replacement, node)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    resolved = ConstantNameResolver().visit(node.value)
                    ast.fix_missing_locations(resolved)
                    return ast.literal_eval(resolved)
    raise KeyError(f"{name} not found in {relative}")


def check(name: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"name": name, "passed": passed, "evidence": evidence}


def md_escape(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def status_label(status: str) -> str:
    return "Ready" if status == "READY" else "Blocked"


def failed_check_names(result: dict[str, Any]) -> list[str]:
    return [item["name"] for item in result["checks"] if not item["passed"]]


def passed_check_count(result: dict[str, Any]) -> str:
    passed = sum(1 for item in result["checks"] if item["passed"])
    total = len(result["checks"])
    return f"{passed}/{total}"


def pgpr_view_validation_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_VIEW_METADATA.exists():
        return False, f"missing {PGPR_AMAZON_VIEW_METADATA.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_VIEW_METADATA.read_text())
    validation = data.get("identity_label_validation", {})
    exact_splits = [
        split
        for split, result in validation.items()
        if result.get("exact_match") is True
    ]
    expected_splits = {"train", "valid", "test"}
    passed = set(exact_splits) == expected_splits
    return (
        passed,
        (
            f"{PGPR_AMAZON_VIEW_METADATA.relative_to(ROOT)} "
            f"exact_splits={sorted(exact_splits)}"
        ),
    )


def pgpr_preprocess_smoke_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_PREPROCESS_SMOKE.exists():
        return False, f"missing {PGPR_AMAZON_PREPROCESS_SMOKE.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_PREPROCESS_SMOKE.read_text())
    split_status = {
        item["split"]: item.get("exact_match") is True
        for item in data.get("split_checks", [])
    }
    core_exists = all(
        item.get("exists") is True
        for item in data.get("core_files", {}).values()
    )
    passed = data.get("status") == "PASS" and split_status == {
        "train": True,
        "test": True,
    } and core_exists
    return (
        passed,
        (
            f"{PGPR_AMAZON_PREPROCESS_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} split_exact={split_status} "
            f"core_files_exist={core_exists}"
        ),
    )


def pgpr_formal_result_status() -> tuple[bool, str]:
    missing = [
        path.relative_to(ROOT)
        for path in (PGPR_AMAZON_EXPORT_VALIDATION, PGPR_AMAZON_ACCURACY)
        if not path.exists()
    ]
    if missing:
        return False, f"missing formal outputs: {[str(path) for path in missing]}"
    export_validation = json.loads(PGPR_AMAZON_EXPORT_VALIDATION.read_text())
    accuracy = json.loads(PGPR_AMAZON_ACCURACY.read_text())
    passed = (
        export_validation.get("status") == "PASS"
        and accuracy.get("status") == "PASS"
    )
    return (
        passed,
        (
            f"{PGPR_AMAZON_EXPORT_VALIDATION.relative_to(ROOT)} "
            f"status={export_validation.get('status')}; "
            f"{PGPR_AMAZON_ACCURACY.relative_to(ROOT)} "
            f"status={accuracy.get('status')}"
        ),
    )


def pgpr_transe_forward_smoke_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_TRANSE_FORWARD_SMOKE.exists():
        return False, f"missing {PGPR_AMAZON_TRANSE_FORWARD_SMOKE.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_TRANSE_FORWARD_SMOKE.read_text())
    passed = (
        data.get("status") == "PASS"
        and data.get("batch_shape") == [64, 11]
        and float(data.get("loss", "nan")) > 0.0
        and int(data.get("gradient_tensors", 0)) > 0
    )
    return (
        passed,
        (
            f"{PGPR_AMAZON_TRANSE_FORWARD_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} batch_shape={data.get('batch_shape')} "
            f"loss={data.get('loss')} gradient_tensors={data.get('gradient_tensors')}"
        ),
    )


def pgpr_transe_training_smoke_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_TRANSE_TRAINING_SMOKE.exists():
        return False, f"missing {PGPR_AMAZON_TRANSE_TRAINING_SMOKE.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_TRANSE_TRAINING_SMOKE.read_text())
    checkpoint = data.get("checkpoint", {})
    embedding = data.get("embedding_pickle", {})
    train_log = data.get("train_log", {})
    passed = (
        data.get("status") == "PASS"
        and data.get("embed_size_ok") is True
        and checkpoint.get("exists") is True
        and embedding.get("exists") is True
        and train_log.get("contains_epoch_01") is True
        and not data.get("missing_embedding_keys")
    )
    return (
        passed,
        (
            f"{PGPR_AMAZON_TRANSE_TRAINING_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} epoch={data.get('epoch')} "
            f"embed_size_ok={data.get('embed_size_ok')} "
            f"checkpoint_exists={checkpoint.get('exists')} "
            f"embedding_exists={embedding.get('exists')}"
        ),
    )


def pgpr_policy_env_smoke_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_POLICY_ENV_SMOKE.exists():
        return False, f"missing {PGPR_AMAZON_POLICY_ENV_SMOKE.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_POLICY_ENV_SMOKE.read_text())
    passed = (
        data.get("status") == "PASS"
        and data.get("manual_done") is True
        and data.get("manual_pattern_ok") is True
        and data.get("manual_final_is_book") is True
        and data.get("manual_reward_finite") is True
        and int(data.get("beam_path_count", 0)) > 0
    )
    return (
        passed,
        (
            f"{PGPR_AMAZON_POLICY_ENV_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} manual_pattern_ok={data.get('manual_pattern_ok')} "
            f"beam_path_count={data.get('beam_path_count')} "
            f"beam_book_endings={data.get('beam_book_endings')}"
        ),
    )


def pgpr_policy_training_smoke_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_POLICY_TRAINING_SMOKE.exists():
        return False, f"missing {PGPR_AMAZON_POLICY_TRAINING_SMOKE.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_POLICY_TRAINING_SMOKE.read_text())
    checkpoint = data.get("checkpoint", {})
    train_log = data.get("train_log", {})
    shape_checks = data.get("shape_checks", {})
    passed = (
        data.get("status") == "PASS"
        and checkpoint.get("exists") is True
        and train_log.get("contains_save_marker") is True
        and bool(shape_checks)
        and all(shape_checks.values())
    )
    return (
        passed,
        (
            f"{PGPR_AMAZON_POLICY_TRAINING_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} epoch={data.get('epoch')} "
            f"run_name={data.get('run_name')} checkpoint_exists={checkpoint.get('exists')} "
            f"shape_checks={shape_checks}"
        ),
    )


def pgpr_policy_inference_smoke_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_POLICY_INFERENCE_SMOKE.exists():
        return False, f"missing {PGPR_AMAZON_POLICY_INFERENCE_SMOKE.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_POLICY_INFERENCE_SMOKE.read_text())
    path_count = int(data.get("path_count", 0))
    probability_rows = int(data.get("probability_rows", 0))
    finite_probability_rows = int(data.get("finite_probability_rows", 0))
    book_endings = int(data.get("book_ending_path_count", 0))
    passed = (
        data.get("status") == "PASS"
        and path_count > 0
        and probability_rows == path_count
        and finite_probability_rows == probability_rows
        and book_endings > 0
    )
    return (
        passed,
        (
            f"{PGPR_AMAZON_POLICY_INFERENCE_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} users={data.get('num_users')} "
            f"path_count={path_count} book_ending_path_count={book_endings} "
            f"finite_probability_rows={finite_probability_rows}/{probability_rows}"
        ),
    )


def pgpr_export_smoke_status() -> tuple[bool, str]:
    if not PGPR_AMAZON_EXPORT_SMOKE_VALIDATION.exists():
        return False, f"missing {PGPR_AMAZON_EXPORT_SMOKE_VALIDATION.relative_to(ROOT)}"
    data = json.loads(PGPR_AMAZON_EXPORT_SMOKE_VALIDATION.read_text())
    pred_rows = int(data.get("pred_path_rows", 0))
    candidate_users = int(data.get("candidate_users", 0))
    explanations = int(data.get("explanations", 0))
    passed = (
        data.get("status") == "PASS"
        and data.get("dataset") == "amazon_book_kgat_v1"
        and data.get("require_all_test_users") is False
        and pred_rows > 0
        and candidate_users > 0
        and explanations > 0
    )
    return (
        passed,
        (
            f"{PGPR_AMAZON_EXPORT_SMOKE_VALIDATION.relative_to(ROOT)} "
            f"status={data.get('status')} pred_path_rows={pred_rows} "
            f"candidate_users={candidate_users} explanations={explanations} "
            f"require_all_test_users={data.get('require_all_test_users')}"
        ),
    )


def ucpr_view_validation_status() -> tuple[bool, str]:
    if not UCPR_AMAZON_VIEW_METADATA.exists():
        return False, f"missing {UCPR_AMAZON_VIEW_METADATA.relative_to(ROOT)}"
    data = json.loads(UCPR_AMAZON_VIEW_METADATA.read_text())
    validation = data.get("label_validation", {})
    exact_splits = [
        split
        for split, result in validation.items()
        if result.get("exact_match") is True
    ]
    expected_splits = {"train", "valid", "test"}
    split_stats = data.get("split_stats", {})
    skipped = {
        split: int(stats.get("skipped_user", 0)) + int(stats.get("skipped_product", 0))
        for split, stats in split_stats.items()
    }
    relations = data.get("schema_projection", {}).get("relations", {})
    relation_edges = {
        name: int(stats.get("edges", 0))
        for name, stats in relations.items()
    }
    core_counts_ok = (
        int(data.get("user_count", 0)) > 0
        and int(data.get("product_count", 0)) > 0
    )
    passed = (
        data.get("model_dataset") == "amazon_book_kgat_v1"
        and set(exact_splits) == expected_splits
        and set(skipped) == expected_splits
        and all(value == 0 for value in skipped.values())
        and core_counts_ok
        and len(relation_edges) >= 9
        and all(value > 0 for value in relation_edges.values())
    )
    return (
        passed,
        (
            f"{UCPR_AMAZON_VIEW_METADATA.relative_to(ROOT)} "
            f"exact_splits={sorted(exact_splits)} "
            f"users={data.get('user_count')} products={data.get('product_count')} "
            f"relations={len(relation_edges)} skipped={skipped}"
        ),
    )


def ucpr_adapter_amazon_alias_status() -> tuple[bool, str]:
    adapter = read_text("adapters/ucpr_adapter.py")
    passed = (
        "amazon_book_kgat_v1" in adapter
        and '"product": "book"' in adapter
        and "book_author_entity" in adapter
    )
    return (
        passed,
        (
            "adapters/ucpr_adapter.py maps Amazon UCPR product paths to "
            f"canonical book endpoints and strips relation suffixes={passed}"
        ),
    )


def ucpr_runtime_amazon_support_status() -> tuple[bool, str]:
    patcher = read_text("scripts/model_patches/patch_ucpr_amazon_runtime.py")
    has_runtime_patch = (
        "AMAZON_BOOK_KGAT = 'amazon_book_kgat_v1'" in patcher
        and "KG_RELATION[AMAZON_BOOK_KGAT]" in patcher
        and "PATH_PATTERN[AMAZON_BOOK_KGAT]" in patcher
        and "MAIN_PRODUCT_INTERACTION[AMAZON_BOOK_KGAT]" in patcher
    )
    return (
        has_runtime_patch,
        (
            "scripts/model_patches/patch_ucpr_amazon_runtime.py has Amazon runtime "
            f"constants/path-pattern patch={has_runtime_patch}"
        ),
    )


def ucpr_preprocess_smoke_status() -> tuple[bool, str]:
    if not UCPR_AMAZON_PREPROCESS_SMOKE.exists():
        return False, f"missing {UCPR_AMAZON_PREPROCESS_SMOKE.relative_to(ROOT)}"
    data = json.loads(UCPR_AMAZON_PREPROCESS_SMOKE.read_text())
    label_checks = data.get("label_checks", {})
    schema_checks = data.get("schema_checks", {})
    dataset_checks = data.get("dataset_checks", {})
    kg_checks = data.get("kg_checks", {})
    exact_splits = [
        split
        for split, result in label_checks.items()
        if result.get("exact_match") is True
    ]
    passed = (
        data.get("status") == "PASS"
        and set(exact_splits) == {"train", "valid", "test"}
        and all(schema_checks.values())
        and dataset_checks.get("relation2entity_all_entity") is True
        and kg_checks.get("all_relation_edges_nonempty") is True
    )
    return (
        passed,
        (
            f"{UCPR_AMAZON_PREPROCESS_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} exact_splits={sorted(exact_splits)} "
            f"review_rows={dataset_checks.get('review_rows')} "
            f"user_purchase_edges={kg_checks.get('user_purchase_edges')}"
        ),
    )


def ucpr_formal_result_status() -> tuple[bool, str]:
    missing = [
        path.relative_to(ROOT)
        for path in (UCPR_AMAZON_EXPORT_VALIDATION, UCPR_AMAZON_ACCURACY)
        if not path.exists()
    ]
    if missing:
        return False, f"missing formal outputs: {[str(path) for path in missing]}"
    export_validation = json.loads(UCPR_AMAZON_EXPORT_VALIDATION.read_text())
    accuracy = json.loads(UCPR_AMAZON_ACCURACY.read_text())
    passed = (
        export_validation.get("status") == "PASS"
        and accuracy.get("status") == "PASS"
    )
    return (
        passed,
        (
            f"{UCPR_AMAZON_EXPORT_VALIDATION.relative_to(ROOT)} "
            f"status={export_validation.get('status')}; "
            f"{UCPR_AMAZON_ACCURACY.relative_to(ROOT)} "
            f"status={accuracy.get('status')}"
        ),
    )


def ucpr_transe_forward_smoke_status() -> tuple[bool, str]:
    if not UCPR_AMAZON_TRANSE_FORWARD_SMOKE.exists():
        return False, f"missing {UCPR_AMAZON_TRANSE_FORWARD_SMOKE.relative_to(ROOT)}"
    data = json.loads(UCPR_AMAZON_TRANSE_FORWARD_SMOKE.read_text())
    expected_relations = set(data.get("expected_relation_names", []))
    present_relations = set(data.get("present_relation_names", []))
    passed = (
        data.get("status") == "PASS"
        and data.get("batch_shape") == [64, 11]
        and float(data.get("loss", "nan")) > 0.0
        and int(data.get("gradient_tensors", 0)) > 0
        and expected_relations == present_relations
        and "purchased" in present_relations
    )
    return (
        passed,
        (
            f"{UCPR_AMAZON_TRANSE_FORWARD_SMOKE.relative_to(ROOT)} "
            f"status={data.get('status')} batch_shape={data.get('batch_shape')} "
            f"loss={data.get('loss')} gradient_tensors={data.get('gradient_tensors')} "
            f"relations={len(present_relations)}"
        ),
    )


def pgpr_audit() -> dict[str, Any]:
    relation_files = literal_assignment("scripts/data/canonical/build_pgpr_view.py", "RELATION_FILES")
    product_entities = literal_assignment("scripts/data/canonical/build_pgpr_view.py", "PRODUCT_ENTITIES")
    text = read_text("scripts/data/canonical/build_pgpr_view.py")
    view_passed, view_evidence = pgpr_view_validation_status()
    smoke_passed, smoke_evidence = pgpr_preprocess_smoke_status()
    transe_smoke_passed, transe_smoke_evidence = pgpr_transe_forward_smoke_status()
    transe_training_passed, transe_training_evidence = pgpr_transe_training_smoke_status()
    policy_env_passed, policy_env_evidence = pgpr_policy_env_smoke_status()
    policy_training_passed, policy_training_evidence = pgpr_policy_training_smoke_status()
    policy_inference_passed, policy_inference_evidence = pgpr_policy_inference_smoke_status()
    export_smoke_passed, export_smoke_evidence = pgpr_export_smoke_status()
    formal_passed, formal_evidence = pgpr_formal_result_status()
    checks = [
        check(
            "RELATION_FILES includes amazon_book_kgat_v1 or amazon",
            any(key in relation_files for key in ("amazon_book_kgat_v1", "amazon", "book")),
            f"available keys={sorted(relation_files)}",
        ),
        check(
            "PRODUCT_ENTITIES includes Amazon book entity",
            any(key in product_entities for key in ("amazon_book_kgat_v1", "amazon", "book")),
            f"available keys={sorted(product_entities)}",
        ),
        check(
            "CLI model-dataset choices include an Amazon option",
            "amazon" in text[text.find("--model-dataset") : text.find("--model-dataset") + 220],
            f"parser choices are derived from RELATION_FILES keys={sorted(relation_files)}",
        ),
        check(
            "Generated Amazon PGPR view round-trips canonical labels",
            view_passed,
            view_evidence,
        ),
        check(
            "Isolated Amazon PGPR runtime preprocess smoke passes",
            smoke_passed,
            smoke_evidence,
        ),
        check(
            "Amazon PGPR TransE one-batch forward/backward smoke passes",
            transe_smoke_passed,
            transe_smoke_evidence,
        ),
        check(
            "Amazon PGPR TransE training smoke passes",
            transe_training_passed,
            transe_training_evidence,
        ),
        check(
            "Amazon PGPR policy environment and beam smoke passes",
            policy_env_passed,
            policy_env_evidence,
        ),
        check(
            "Amazon PGPR policy training smoke passes",
            policy_training_passed,
            policy_training_evidence,
        ),
        check(
            "Amazon PGPR policy inference smoke passes",
            policy_inference_passed,
            policy_inference_evidence,
        ),
        check(
            "Amazon PGPR adapter/export smoke validation passes",
            export_smoke_passed,
            export_smoke_evidence,
        ),
        check(
            "Formal Amazon PGPR export and accuracy validation exist",
            formal_passed,
            formal_evidence,
        ),
    ]
    return {
        "status": "READY" if all(item["passed"] for item in checks) else "BLOCKED",
        "checks": checks,
        "required_next_steps": [
            "Run full/formal PGPR Amazon policy training and native path export from the ported runtime.",
            "Run strict full-user export validation and strict accuracy validation before any formal report row.",
        ],
    }


def ucpr_audit() -> dict[str, Any]:
    config = literal_assignment("scripts/data/canonical/build_ucpr_view.py", "DATASET_CONFIG")
    text = read_text("scripts/data/canonical/build_ucpr_view.py")
    view_passed, view_evidence = ucpr_view_validation_status()
    adapter_passed, adapter_evidence = ucpr_adapter_amazon_alias_status()
    runtime_passed, runtime_evidence = ucpr_runtime_amazon_support_status()
    preprocess_passed, preprocess_evidence = ucpr_preprocess_smoke_status()
    transe_forward_passed, transe_forward_evidence = ucpr_transe_forward_smoke_status()
    formal_passed, formal_evidence = ucpr_formal_result_status()
    checks = [
        check(
            "DATASET_CONFIG includes Amazon",
            any(key in config for key in ("amazon_book_kgat_v1", "amazon", "book")),
            f"available keys={sorted(config)}",
        ),
        check(
            "CLI model-dataset choices include an Amazon option",
            "amazon" in text[text.find("--model-dataset") : text.find("--model-dataset") + 220],
            "parser choices are derived from DATASET_CONFIG",
        ),
        check(
            "Generated Amazon UCPR view round-trips canonical labels",
            view_passed,
            view_evidence,
        ),
        check(
            "UCPR adapter supports Amazon book path aliases",
            adapter_passed,
            adapter_evidence,
        ),
        check(
            "Active UCPR runtime supports Amazon path semantics",
            runtime_passed,
            runtime_evidence,
        ),
        check(
            "Isolated Amazon UCPR runtime preprocess smoke passes",
            preprocess_passed,
            preprocess_evidence,
        ),
        check(
            "Amazon UCPR TransE one-batch forward/backward smoke passes",
            transe_forward_passed,
            transe_forward_evidence,
        ),
        check(
            "Formal Amazon UCPR export and accuracy validation exist",
            formal_passed,
            formal_evidence,
        ),
    ]
    return {
        "status": "READY" if all(item["passed"] for item in checks) else "BLOCKED",
        "checks": checks,
        "required_next_steps": [
            "Run UCPR Amazon TransE and policy training from the patched runtime.",
            "Run UCPR Amazon native-path inference/export with full canonical test-user coverage.",
            "Run strict full-user export validation and strict accuracy validation before formal reporting.",
        ],
    }


def cafe_audit() -> dict[str, Any]:
    config = literal_assignment("scripts/data/canonical/build_cafe_view.py", "DATASET_CONFIG")
    text = read_text("scripts/data/canonical/build_cafe_view.py")
    checks = [
        check(
            "DATASET_CONFIG includes Amazon",
            any(key in config for key in ("amazon_book_kgat_v1", "amazon", "book")),
            f"available keys={sorted(config)}",
        ),
        check(
            "CLI model-dataset choices include an Amazon option",
            "amazon" in text[text.find("--model-dataset") : text.find("--model-dataset") + 220],
            "parser choices are derived from DATASET_CONFIG",
        ),
    ]
    return {
        "status": "READY" if all(item["passed"] for item in checks) else "BLOCKED",
        "checks": checks,
        "required_next_steps": [
            "Build a compatible Amazon UCPR view first.",
            "Add executable Amazon CAFE entity/relation schema and metapaths.",
            "Validate that CAFE emits non-empty native paths mapped back to canonical uid/pid.",
        ],
    }


def tprec_audit() -> dict[str, Any]:
    runtime = read_text("scripts/hopwise/tprec_runtime.py")
    pipeline = read_text("scripts/hopwise/run_canonical_tprec_pipeline.sh")
    runner = read_text("scripts/hopwise/run_canonical_tprec.py")
    exporter = read_text("scripts/hopwise/export_tprec_paths.py")
    timestamp_audit_passed = False
    timestamp_evidence = f"missing {TPREC_AMAZON_TIMESTAMP_AUDIT.relative_to(ROOT)}"
    if TPREC_AMAZON_TIMESTAMP_AUDIT.exists():
        data = json.loads(TPREC_AMAZON_TIMESTAMP_AUDIT.read_text())
        timestamp_audit_passed = (
            data.get("status") == "PASS"
            and data.get("formal_temporal_reward_approved") is True
        )
        timestamp_evidence = (
            f"{TPREC_AMAZON_TIMESTAMP_AUDIT.relative_to(ROOT)} "
            f"status={data.get('status')} "
            f"formal_temporal_reward_approved={data.get('formal_temporal_reward_approved')} "
            f"timestamp_policy={data.get('canonical_metadata_timestamp_policy')} "
            f"train_sentinel_fraction="
            f"{data.get('canonical_timestamp_summary', {}).get('train', {}).get('sentinel_fraction')}"
        )

    hopwise_manifest_passed = False
    hopwise_evidence = f"missing {TPREC_AMAZON_HOPWISE_MANIFEST.relative_to(ROOT)}"
    if TPREC_AMAZON_HOPWISE_MANIFEST.exists():
        data = json.loads(TPREC_AMAZON_HOPWISE_MANIFEST.read_text())
        hopwise_manifest_passed = (
            data.get("status") == "PASS"
            and data.get("interactions_preserved") is True
            and data.get("kg_preserved") is True
            and int(data.get("kept_link_rows", 0)) > 0
        )
        hopwise_evidence = (
            f"{TPREC_AMAZON_HOPWISE_MANIFEST.relative_to(ROOT)} "
            f"status={data.get('status')} kept_link_rows={data.get('kept_link_rows')} "
            f"dropped_link_rows={data.get('dropped_link_rows')}"
        )
    checks = [
        check(
            "canonical_path_constraints supports canonical_amazon_book_kgat_v1",
            "canonical_amazon_book_kgat_v1" in runtime,
            "tprec_runtime.py defines Amazon relation-token path constraints",
        ),
        check(
            "run_canonical_tprec.py CLI accepts canonical_amazon_book_kgat_v1",
            "canonical_amazon_book_kgat_v1" in runner,
            "run_canonical_tprec.py parser choices include Amazon",
        ),
        check(
            "export_tprec_paths.py aliases canonical_amazon_book_kgat_v1",
            "amazon_book_kgat_v1" in exporter and '"product_type": "book"' in exporter,
            "export_tprec_paths.py maps Amazon products to canonical book endpoints",
        ),
        check(
            "pipeline case statement supports canonical_amazon_book_kgat_v1",
            "canonical_amazon_book_kgat_v1)" in pipeline,
            "run_canonical_tprec_pipeline.sh contains an Amazon case with a timestamp gate",
        ),
        check(
            "Hopwise Amazon view is present and preserves interactions/KG",
            hopwise_manifest_passed,
            hopwise_evidence,
        ),
        check(
            "Amazon timestamps support formal TPRec temporal rewards",
            timestamp_audit_passed,
            timestamp_evidence,
        ),
    ]
    return {
        "status": "READY" if all(item["passed"] for item in checks) else "BLOCKED",
        "checks": checks,
        "required_next_steps": [
            "Keep Amazon TPRec formal reporting blocked while canonical timestamps are sentinel -1.",
            "Either rebuild Amazon-book KGAT with real interaction timestamps or define an explicitly labeled non-temporal TPRec ablation protocol.",
            "Only after timestamp semantics are approved, run full TPRec training/export with strict full-user validation.",
        ],
    }


def build_report() -> dict[str, Any]:
    models = {
        "PGPR": pgpr_audit(),
        "UCPR": ucpr_audit(),
        "CAFE": cafe_audit(),
        "TPRec": tprec_audit(),
    }
    blocked = [model for model, result in models.items() if result["status"] != "READY"]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "canonical_amazon_book_kgat_v1",
        "status": "READY" if not blocked else "BLOCKED",
        "ready_models": [model for model in models if model not in blocked],
        "blocked_models": blocked,
        "models": models,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Amazon Classic Native-Path Port Readiness",
        "",
        f"Generated at `{report['generated_at_utc']}`.",
        "",
        f"Dataset: `{report['dataset']}`.",
        "",
        f"Overall status: `{report['status']}`.",
        "",
        (
            "This report is intentionally a readiness gate, not an accuracy result. "
            "A blocked row means the model is not yet an honest runnable "
            "Amazon-book KGAT baseline."
        ),
        "",
        "| Model | Readiness | Checks passed | Failed gates | Required next actions |",
        "|---|---:|---:|---|---|",
    ]
    for model in MODEL_ORDER:
        result = report["models"][model]
        failed = failed_check_names(result)
        failed_text = "<br>".join(md_escape(item) for item in failed) if failed else "None"
        next_steps = "<br>".join(md_escape(item) for item in result["required_next_steps"])
        lines.append(
            "| {model} | {status} | {passed} | {failed} | {next_steps} |".format(
                model=model,
                status=status_label(result["status"]),
                passed=passed_check_count(result),
                failed=failed_text,
                next_steps=next_steps,
            )
        )

    lines.extend(
        [
            "",
            "## Check evidence",
            "",
            "| Model | Check | Result | Evidence |",
            "|---|---|---:|---|",
        ]
    )
    for model in MODEL_ORDER:
        for item in report["models"][model]["checks"]:
            lines.append(
                "| {model} | {check} | {result} | {evidence} |".format(
                    model=model,
                    check=md_escape(item["name"]),
                    result="PASS" if item["passed"] else "FAIL",
                    evidence=md_escape(item["evidence"]),
                )
            )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit whether classic native-path baselines are ready for Amazon-book.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=OUT,
        help=f"JSON report path, default: {OUT}",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=OUT_MD,
        help=f"Markdown report path, default: {OUT_MD}",
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Only write the JSON readiness report.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if not args.no_markdown:
        write_markdown(report, args.markdown_output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
