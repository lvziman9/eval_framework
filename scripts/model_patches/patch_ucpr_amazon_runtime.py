#!/usr/bin/env python3
"""Apply canonical Amazon-book KGAT support to a UCPR runtime copy.

The UCPR source tree is kept outside this repository and copied into an
experiment runtime before execution.  This patch deliberately mutates only
that runtime copy.  It injects the canonical Amazon-book KGAT schema into the
generic UCPR constants and makes the KG-based preprocess path accept the new
dataset key.
"""

from __future__ import annotations

import argparse
from pathlib import Path


AMAZON_SCHEMA_MARKER = "# BEGIN CANONICAL AMAZON_BOOK_KGAT UCPR SCHEMA"
AMAZON_SCHEMA_BLOCK = f"""

{AMAZON_SCHEMA_MARKER}
AMAZON_BOOK_KGAT = 'amazon_book_kgat_v1'
AZ_BOOK_CORE = AMAZON_BOOK_KGAT
ENTITY = 'entity'
PURCHASED = 'purchased'

BOOK_AUTHOR_ENTITY = 'book_author_entity'
BOOK_GENRE_ENTITY = 'book_genre_entity'
BOOK_ORIGINAL_LANGUAGE_ENTITY = 'book_original_language_entity'
BOOK_SUBJECT_ENTITY = 'book_subject_entity'
BOOK_NEXT_IN_SERIES_ENTITY = 'book_next_in_series_entity'
BOOK_PREVIOUS_IN_SERIES_ENTITY = 'book_previous_in_series_entity'
BOOK_PART_OF_SERIES_ENTITY = 'book_part_of_series_entity'
BOOK_CHARACTER_ENTITY = 'book_character_entity'
BOOK_INTERIOR_ILLUSTRATION_ENTITY = 'book_interior_illustration_entity'

AMAZON_BOOK_RELATION_PATTERN_IDS = {{
    10: BOOK_AUTHOR_ENTITY,
    13: BOOK_GENRE_ENTITY,
    11: BOOK_ORIGINAL_LANGUAGE_ENTITY,
    5: BOOK_SUBJECT_ENTITY,
    20: BOOK_NEXT_IN_SERIES_ENTITY,
    15: BOOK_PREVIOUS_IN_SERIES_ENTITY,
    18: BOOK_PART_OF_SERIES_ENTITY,
    19: BOOK_CHARACTER_ENTITY,
    36: BOOK_INTERIOR_ILLUSTRATION_ENTITY,
}}
AMAZON_BOOK_RELATIONS = list(AMAZON_BOOK_RELATION_PATTERN_IDS.values())

DATASET_DIR[AMAZON_BOOK_KGAT] = f'{{ROOT_DIR}}/data/{{AMAZON_BOOK_KGAT}}/preprocessed/{{MODEL}}'
TMP_DIR[AMAZON_BOOK_KGAT] = f'{{DATASET_DIR[AMAZON_BOOK_KGAT]}}/tmp'
LOG_DATASET_DIR[AMAZON_BOOK_KGAT] = f'{{LOG_DIR}}/{{AMAZON_BOOK_KGAT}}/{{MODEL}}'
CFG_DIR[AMAZON_BOOK_KGAT] = f'{{LOG_DATASET_DIR[AMAZON_BOOK_KGAT]}}/hparams_cfg'
BEST_CFG_DIR[AMAZON_BOOK_KGAT] = f'{{LOG_DATASET_DIR[AMAZON_BOOK_KGAT]}}/best_hparams_cfg'
RECOM_METRICS_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{CFG_DIR[AMAZON_BOOK_KGAT]}}/{{RECOM_METRICS_FILE_NAME}}'
TEST_METRICS_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{CFG_DIR[AMAZON_BOOK_KGAT]}}/{{TEST_METRICS_FILE_NAME}}'
BEST_TEST_METRICS_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{BEST_CFG_DIR[AMAZON_BOOK_KGAT]}}/{{TEST_METRICS_FILE_NAME}}'
CFG_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{CFG_DIR[AMAZON_BOOK_KGAT]}}/{{CONFIG_FILE_NAME}}'
BEST_CFG_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{BEST_CFG_DIR[AMAZON_BOOK_KGAT]}}/{{CONFIG_FILE_NAME}}'
TRANSE_TEST_METRICS_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{CFG_DIR[AMAZON_BOOK_KGAT]}}/{{TRANSE_TEST_METRICS_FILE_NAME}}'
BEST_TRANSE_TEST_METRICS_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{BEST_CFG_DIR[AMAZON_BOOK_KGAT]}}/{{TRANSE_TEST_METRICS_FILE_NAME}}'
TRANSE_CFG_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{CFG_DIR[AMAZON_BOOK_KGAT]}}/{{TRANSE_CFG_FILE_NAME}}'
BEST_TRANSE_CFG_FILE_PATH[AMAZON_BOOK_KGAT] = f'{{BEST_CFG_DIR[AMAZON_BOOK_KGAT]}}/{{TRANSE_CFG_FILE_NAME}}'
SAVE_MODEL_DIR[AMAZON_BOOK_KGAT] = f'{{LOG_DATASET_DIR[AMAZON_BOOK_KGAT]}}/save'
EVALUATION[AMAZON_BOOK_KGAT] = f'{{LOG_DATASET_DIR[AMAZON_BOOK_KGAT]}}/eva_pre'
EVALUATION_2[AMAZON_BOOK_KGAT] = f'{{LOG_DATASET_DIR[AMAZON_BOOK_KGAT]}}/eval'
CASE_ST[AMAZON_BOOK_KGAT] = f'{{LOG_DATASET_DIR[AMAZON_BOOK_KGAT]}}/case_st'
TEST[AMAZON_BOOK_KGAT] = f'{{LOG_DATASET_DIR[AMAZON_BOOK_KGAT]}}/test'
LABELS[AMAZON_BOOK_KGAT] = (
    TMP_DIR[AMAZON_BOOK_KGAT] + '/train_label.pkl',
    TMP_DIR[AMAZON_BOOK_KGAT] + '/valid_label.pkl',
    TMP_DIR[AMAZON_BOOK_KGAT] + '/test_label.pkl',
)

INTERACTION[AMAZON_BOOK_KGAT] = PURCHASED
KG_RELATION[AMAZON_BOOK_KGAT] = {{
    USER: {{
        PURCHASED: PRODUCT,
    }},
    PRODUCT: dict(
        [(PURCHASED, USER)]
        + [(relation, ENTITY) for relation in AMAZON_BOOK_RELATIONS]
    ),
    ENTITY: {{
        relation: PRODUCT for relation in AMAZON_BOOK_RELATIONS
    }},
}}
PATH_PATTERN[AMAZON_BOOK_KGAT] = {{
    0: (
        (None, USER),
        (PURCHASED, PRODUCT),
        (PURCHASED, USER),
        (PURCHASED, PRODUCT),
    ),
}}
PATH_PATTERN[AMAZON_BOOK_KGAT].update({{
    pattern_id: (
        (None, USER),
        (PURCHASED, PRODUCT),
        (relation, ENTITY),
        (relation, PRODUCT),
    )
    for pattern_id, relation in AMAZON_BOOK_RELATION_PATTERN_IDS.items()
}})
MAIN_PRODUCT_INTERACTION[AMAZON_BOOK_KGAT] = (PRODUCT, INTERACTION[AMAZON_BOOK_KGAT])
# END CANONICAL AMAZON_BOOK_KGAT UCPR SCHEMA
"""


def patch_utils(path: Path) -> str:
    text = path.read_text()
    if AMAZON_SCHEMA_MARKER in text:
        return "already_patched"
    path.write_text(text.rstrip() + AMAZON_SCHEMA_BLOCK + "\n")
    return "patched"


def patch_text_once(path: Path, old: str, new: str) -> str:
    text = path.read_text()
    if new in text:
        return "already_patched"
    if old not in text:
        raise RuntimeError(f"Could not patch {path}; missing expected text: {old!r}")
    path.write_text(text.replace(old, new, 1))
    return "patched"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runtime-root",
        required=True,
        help="Runtime root containing models/UCPR/utils.py",
    )
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root)
    utils_path = runtime_root / "models" / "UCPR" / "utils.py"
    if not utils_path.exists():
        raise FileNotFoundError(utils_path)

    statuses = [(patch_utils(utils_path), utils_path)]
    kg_branch_old = "    if args.dataset in [ML1M, LFM1M]: preprocess_kg_based(args)\n"
    kg_branch_new = (
        "    if args.dataset in [ML1M, LFM1M, AMAZON_BOOK_KGAT]: "
        "preprocess_kg_based(args)\n"
    )
    for relative in [
        "models/UCPR/preprocess.py",
        "models/UCPR/preprocess/preprocess.py",
    ]:
        path = runtime_root / relative
        statuses.append((patch_text_once(path, kg_branch_old, kg_branch_new), path))

    pretrain_old = "        elif args.dataset in [LFM1M,ML1M]:#MOVIE_CORE, AZ_BOOK_CORE]:\n"
    pretrain_new = (
        "        elif args.dataset in [LFM1M,ML1M,AMAZON_BOOK_KGAT]:"
        "#MOVIE_CORE, AZ_BOOK_CORE]:\n"
    )
    for relative in [
        "models/UCPR/train.py",
        "models/UCPR/src/train.py",
    ]:
        path = runtime_root / relative
        statuses.append((patch_text_once(path, pretrain_old, pretrain_new), path))

    adam_old = "    optimizer = optim.Adam(model.parameters(), lr=args.lr)\n"
    adam_new = (
        "    # Canonical Amazon-book KGAT has a large UCPR parameter set; "
        "PyTorch's foreach Adam path materializes a large temporary tensor "
        "during the first optimizer step and OOMs on 24GB GPUs.  The scalar "
        "Adam path preserves optimizer semantics while avoiding that temporary.\n"
        "    optimizer = optim.Adam(model.parameters(), lr=args.lr, foreach=False)\n"
    )
    for relative in [
        "models/UCPR/train.py",
        "models/UCPR/src/train.py",
    ]:
        path = runtime_root / relative
        statuses.append((patch_text_once(path, adam_old, adam_new), path))

    for status, path in statuses:
        print(f"{status}: {path}")


if __name__ == "__main__":
    main()
