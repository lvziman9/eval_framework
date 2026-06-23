#!/usr/bin/env python3
"""Apply reproducible compatibility/correctness fixes to a CAFE runtime copy."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_required(path: Path, old: str, new: str, count: int = 1) -> bool:
    text = path.read_text()
    if new in text:
        return False
    if text.count(old) < count:
        raise RuntimeError(f"Expected patch target not found in {path}: {old!r}")
    path.write_text(text.replace(old, new, count))
    return True


def patch_runtime(runtime_root: Path) -> list[str]:
    cafe = runtime_root / "models" / "CAFE"
    changed = []

    symbolic = cafe / "symbolic_model.py"
    if replace_required(
        symbolic,
        "                getattr(self, name).data = weight\n",
        (
            "                embedding = getattr(self, name)\n"
            "                if tuple(embedding.weight.shape) != tuple(weight.shape):\n"
            "                    raise ValueError(\n"
            "                        f\"Embedding shape mismatch for {name}: \"\n"
            "                        f\"model={tuple(embedding.weight.shape)}, init={tuple(weight.shape)}\"\n"
            "                    )\n"
            "                embedding.weight.data.copy_(weight)\n"
        ),
    ):
        changed.append(str(symbolic))

    execute = cafe / "execute_neural_symbol.py"
    text = execute.read_text()
    original = text
    text = text.replace("np.asfarray(r)", "np.asarray(r, dtype=float)")
    text = text.replace("prior_count.astype(np.int)", "prior_count.astype(int)")
    if "@torch.no_grad()\ndef infer_paths" not in text:
        text = text.replace(
            "def infer_paths(args, topk_paths=25):\n",
            "@torch.no_grad()\ndef infer_paths(args, topk_paths=25):\n",
            1,
        )
    if "@torch.no_grad()\ndef run_program" not in text:
        text = text.replace(
            "def run_program(args):\n",
            "@torch.no_grad()\ndef run_program(args):\n",
            1,
        )
    old_path_scoring = (
        "    pred_labels = {}\n"
        "    pbar = tqdm(total=len(test_labels))\n"
        "    pred_paths_istances = {}\n"
        "    for uid in test_labels:\n"
        "        pred_paths_istances[uid] = {}\n"
        "        program = create_heuristic_program(kg.metapaths, raw_paths[uid], path_counts[uid], args.sample_size)\n"
        "        program_exe.execute(program, uid, train_valid_labels[uid])\n"
        "        paths = program_exe.collect_results(program)\n"
        "        tmp = [(r[0][-1], reduce(lambda x, y: x * y, r[1])) for r in paths]\n"
        "        for r in paths:\n"
        "            path = [(\"self_loop\", 'user', r[0][0])]\n"
        "            for i in range(len(r[-1])):\n"
        "                path.append((r[-1][i], r[2][i], r[0][i + 1]))\n"
        "                if i == len(r[-1]) - 1: continue\n"
        "            pred_paths_istances[r[0][0]][r[0][-1]] = [(reduce(lambda x, y: x * y, r[1]), np.mean(r[1][-1]), path)]\n"
        "        tmp = sorted(tmp, key=lambda x: x[1], reverse=True)[:10]\n"
        "        pred_labels[uid] = [t[0] for t in tmp]\n"
        "        pbar.update(1)\n"
        "    save_pred_paths(args.dataset, pred_paths_istances)\n"
    )
    best_only_path_scoring = (
        "    pred_labels = {}\n"
        "    pbar = tqdm(total=len(test_labels))\n"
        "    pred_paths_instances = {}\n"
        "    for uid in test_labels:\n"
        "        pred_paths_instances[uid] = {}\n"
        "        program = create_heuristic_program(kg.metapaths, raw_paths[uid], path_counts[uid], args.sample_size)\n"
        "        program_exe.execute(program, uid, train_valid_labels[uid])\n"
        "        paths = program_exe.collect_results(program)\n"
        "        best_item_scores = {}\n"
        "        for r in paths:\n"
        "            path = [(\"self_loop\", 'user', r[0][0])]\n"
        "            for i in range(len(r[-1])):\n"
        "                path.append((r[-1][i], r[2][i], r[0][i + 1]))\n"
        "            # Step values are log-softmax scores, so path log-probability\n"
        "            # is their sum. Multiplying log scores reverses/warps ranking.\n"
        "            path_log_score = float(np.sum(r[1]))\n"
        "            path_probability = float(np.exp(path_log_score))\n"
        "            pid = int(r[0][-1])\n"
        "            current = pred_paths_instances[uid].get(pid)\n"
        "            if current is None or path_log_score > current[0][0]:\n"
        "                pred_paths_instances[uid][pid] = [\n"
        "                    (path_log_score, path_probability, path)\n"
        "                ]\n"
        "                best_item_scores[pid] = path_log_score\n"
        "        ranked_items = sorted(\n"
        "            best_item_scores.items(), key=lambda item: item[1], reverse=True\n"
        "        )[:10]\n"
        "        pred_labels[uid] = [pid for pid, _score in ranked_items]\n"
        "        pbar.update(1)\n"
        "    save_pred_paths(args.dataset, pred_paths_instances)\n"
    )
    new_path_scoring = best_only_path_scoring.replace(
        "            current = pred_paths_instances[uid].get(pid)\n"
        "            if current is None or path_log_score > current[0][0]:\n"
        "                pred_paths_instances[uid][pid] = [\n"
        "                    (path_log_score, path_probability, path)\n"
        "                ]\n"
        "                best_item_scores[pid] = path_log_score\n",
        "            pred_paths_instances[uid].setdefault(pid, []).append(\n"
        "                (path_log_score, path_probability, path)\n"
        "            )\n"
        "            best_item_scores[pid] = max(\n"
        "                path_log_score, best_item_scores.get(pid, float('-inf'))\n"
        "            )\n",
    )
    current_path_scoring_markers = (
        "path_log_score = float(np.sum(r[1]))",
        "path_probability = float(np.exp(path_log_score))",
        "pred_paths_instances[uid].setdefault(pid, []).append(",
        "best_item_scores[pid] = max(",
    )
    if new_path_scoring not in text and not all(
        marker in text for marker in current_path_scoring_markers
    ):
        if best_only_path_scoring in text:
            text = text.replace(best_only_path_scoring, new_path_scoring, 1)
        elif old_path_scoring in text:
            text = text.replace(old_path_scoring, new_path_scoring, 1)
        else:
            raise RuntimeError(f"Could not patch path scoring in {execute}")
    missing_native_path_guard = (
        "    skipped_native_users = []\n"
        "    for uid in test_labels:\n"
        "        pred_paths_instances[uid] = {}\n"
        "        if uid not in raw_paths or uid not in path_counts:\n"
        "            # CAFE builds both artifacts from the training graph. Test-only\n"
        "            # users have no executable native program; preserve an empty\n"
        "            # recommendation row instead of fabricating a fallback path.\n"
        "            pred_labels[uid] = []\n"
        "            skipped_native_users.append(uid)\n"
        "            pbar.update(1)\n"
        "            continue\n"
        "        program = create_heuristic_program(kg.metapaths, raw_paths[uid], path_counts[uid], args.sample_size)\n"
        "        program_exe.execute(program, uid, train_valid_labels.get(uid, []))\n"
    )
    unguarded_native_path_block = (
        "    for uid in test_labels:\n"
        "        pred_paths_instances[uid] = {}\n"
        "        program = create_heuristic_program(kg.metapaths, raw_paths[uid], path_counts[uid], args.sample_size)\n"
        "        program_exe.execute(program, uid, train_valid_labels[uid])\n"
    )
    if missing_native_path_guard not in text:
        if unguarded_native_path_block not in text:
            raise RuntimeError(f"Could not patch missing-user path guard in {execute}")
        text = text.replace(
            unguarded_native_path_block,
            missing_native_path_guard,
            1,
        )
    skipped_native_log = (
        "    logger.info(\n"
        "        f\"CAFE native-path-ineligible test users: {len(skipped_native_users)}\"\n"
        "    )\n"
        "    save_pred_paths(args.dataset, pred_paths_instances)\n"
    )
    if skipped_native_log not in text:
        save_marker = "    save_pred_paths(args.dataset, pred_paths_instances)\n"
        if save_marker not in text:
            raise RuntimeError(f"Could not add missing-user audit log in {execute}")
        text = text.replace(save_marker, skipped_native_log, 1)
    bad_merge = (
        "    train_valid_labels = dict(zip(train_labels.keys(), "
        "list(train_labels.values()) + list(valid_labels.values())))\n"
    )
    good_merge = (
        "    train_valid_labels = {\n"
        "        uid: list(train_labels.get(uid, [])) + list(valid_labels.get(uid, []))\n"
        "        for uid in set(train_labels) | set(valid_labels)\n"
        "    }\n"
    )
    text = text.replace(bad_merge, good_merge)
    if text != original:
        execute.write_text(text)
        changed.append(str(execute))
    elif (
        "np.asfarray" in text
        or "astype(np.int)" in text
        or bad_merge in text
        or old_path_scoring in text
        or best_only_path_scoring in text
    ):
        raise RuntimeError(f"Failed to patch {execute}")

    cafe_utils = cafe / "cafe_utils.py"
    text = cafe_utils.read_text()
    original = text
    text = text.replace("import scipy.sparse as sp\n", "")
    text = text.replace("from sklearn.feature_extraction.text import TfidfTransformer\n", "")
    text = text.replace(
        "    parser.add_argument('--do_validation', type=bool, default=True, "
        "help='Whether to perform validation')\n",
        "    parser.add_argument('--do_validation', type=boolean, default=True, "
        "help='Whether to perform validation')\n",
    )
    score_batch_arg = (
        "    parser.add_argument('--score_batch_size', type=int, default=256, "
        "help='users per batch when computing dense KG item scores')\n"
    )
    if "--score_batch_size" not in text:
        parser_marker = (
            "    parser.add_argument('--sample_size', type=int, default=500, "
            "help='sample size for model.')\n"
        )
        if parser_marker not in text:
            raise RuntimeError(f"Could not add score_batch_size to {cafe_utils}")
        text = text.replace(parser_marker, parser_marker + score_batch_arg, 1)
    if text != original:
        cafe_utils.write_text(text)
        changed.append(str(cafe_utils))

    if replace_required(
        cafe_utils,
        "ROOT_DIR = os.environ('TREX_DATA_ROOT') if 'TREX_DATA_ROOT' in os.environ else '../..'\n",
        "ROOT_DIR = os.environ.get('TREX_DATA_ROOT', '../..')\n",
    ):
        if str(cafe_utils) not in changed:
            changed.append(str(cafe_utils))

    knowledge_graph = cafe / "knowledge_graph.py"
    kg_text = knowledge_graph.read_text()
    fast_count_marker = (
        "        # All supported CAFE rules are user-product-middle-product.\n"
    )
    if fast_count_marker not in kg_text:
        count_prefix = (
            "    def count_paths_with_target(self, mpath_id, user_id, target_id, sample_size=50):\n"
            "        \"\"\"This is an approx count, not exact.\"\"\"\n"
            "        metapath = self.metapaths[mpath_id]\n"
        )
        count_prefix_with_fast_path = (
            count_prefix
            + "        # All supported CAFE rules are user-product-middle-product.\n"
            + "        # Count matching history products directly instead of expanding the\n"
            + "        # complete reverse neighborhood for every training interaction.\n"
            + "        if (\n"
            + "            len(metapath) == 4\n"
            + "            and metapath[0][1] == USER\n"
            + "            and metapath[1][1] == PRODUCT\n"
            + "            and metapath[-1][1] == PRODUCT\n"
            + "        ):\n"
            + "            history_ids = self.get(USER, user_id, metapath[1][0])\n"
            + "            if len(history_ids) > sample_size:\n"
            + "                history_ids = np.random.choice(\n"
            + "                    history_ids, size=sample_size, replace=False\n"
            + "                ).tolist()\n"
            + "            middle_relation = metapath[2][0]\n"
            + "            target_middle_ids = set(\n"
            + "                self.get(PRODUCT, target_id, middle_relation)\n"
            + "            )\n"
            + "            return sum(\n"
            + "                bool(\n"
            + "                    target_middle_ids.intersection(\n"
            + "                        self.get(PRODUCT, history_id, middle_relation)\n"
            + "                    )\n"
            + "                )\n"
            + "                for history_id in set(history_ids)\n"
            + "            )\n"
        )
        if count_prefix not in kg_text:
            raise RuntimeError(f"Could not patch path counting in {knowledge_graph}")
        knowledge_graph.write_text(
            kg_text.replace(count_prefix, count_prefix_with_fast_path, 1)
        )
        changed.append(str(knowledge_graph))

    preprocess = cafe / "preprocess.py"
    preprocess_text = preprocess.read_text()
    old_topk = (
        "def compute_top100_items(dataset):\n"
        "    embeds = load_embed(dataset)\n"
        "    user_embed = embeds[USER]\n"
        "    product_embed = embeds[PRODUCT]\n"
        "    purchase_embed, purchase_bias = embeds[INTERACTION[dataset]]\n"
        "    scores = np.dot(user_embed + purchase_embed, product_embed.T)\n"
        "    user_products = np.argsort(scores, axis=1)  # From worst to best\n"
        "    best100 = user_products[:, -100:][:, ::-1]\n"
        "    print(best100.shape)\n"
        "    return best100\n"
    )
    new_topk = (
        "def compute_top100_items(dataset, batch_size=256):\n"
        "    embeds = load_embed(dataset)\n"
        "    user_embed = embeds[USER]\n"
        "    product_embed = embeds[PRODUCT]\n"
        "    purchase_embed, purchase_bias = embeds[INTERACTION[dataset]]\n"
        "    # load_kg_embedding keeps one vocab-padding row for CAFE's\n"
        "    # embedding shape; it is not a real KG product candidate.\n"
        "    candidate_product_embed = product_embed[:-1]\n"
        "    topk = min(100, len(candidate_product_embed))\n"
        "    best100 = np.empty((len(user_embed), topk), dtype=np.int64)\n"
        "    for start in tqdm(range(0, len(user_embed), batch_size), desc='Top-100 item batches'):\n"
        "        end = min(start + batch_size, len(user_embed))\n"
        "        scores = np.dot(user_embed[start:end] + purchase_embed, candidate_product_embed.T)\n"
        "        best100[start:end] = np.argsort(scores, axis=1)[:, -topk:][:, ::-1]\n"
        "    print(best100.shape)\n"
        "    return best100\n"
    )
    legacy_batched_topk = new_topk.replace(
        "    # load_kg_embedding keeps one vocab-padding row for CAFE's\n"
        "    # embedding shape; it is not a real KG product candidate.\n"
        "    candidate_product_embed = product_embed[:-1]\n"
        "    topk = min(100, len(candidate_product_embed))\n",
        "    topk = min(100, len(product_embed))\n",
    ).replace(
        "candidate_product_embed.T",
        "product_embed.T",
    )
    if new_topk not in preprocess_text:
        if legacy_batched_topk in preprocess_text:
            preprocess_text = preprocess_text.replace(
                legacy_batched_topk, new_topk, 1
            )
        elif old_topk in preprocess_text:
            preprocess_text = preprocess_text.replace(old_topk, new_topk, 1)
        else:
            raise RuntimeError(f"Could not patch batched top-k scoring in {preprocess}")
    preprocess_text = preprocess_text.replace(
        "    best100 = compute_top100_items(args.dataset)\n",
        "    best100 = compute_top100_items(args.dataset, args.score_batch_size)\n",
        1,
    )
    if preprocess_text != preprocess.read_text():
        preprocess.write_text(preprocess_text)
        changed.append(str(preprocess))

    train_file = cafe / "train_neural_symbol.py"
    train_text = train_file.read_text()
    old_schedule = (
        "        splits_to_compute = list(loaders.items())\n"
        "        if first_iterate:\n"
        "            first_iterate = False\n"
        "            splits_to_compute.insert(0, ('valid', valid_dataloader))\n"
        "        for split_name, dataloader in splits_to_compute:                    \n"
        "            if split_name == 'valid' and epoch%5 == 0:\n"
        "                model.eval()\n"
        "            else:\n"
        "                model.train()\n"
    )
    legacy_patched_schedule = (
        "        splits_to_compute = [('train', train_dataloader)]\n"
        "        if first_iterate or epoch % 5 == 0:\n"
        "            splits_to_compute.append(('valid', valid_dataloader))\n"
        "        first_iterate = False\n"
        "        for split_name, dataloader in splits_to_compute:\n"
        "            if split_name == 'valid':\n"
        "                model.eval()\n"
        "            else:\n"
        "                model.train()\n"
    )
    new_schedule = (
        "        splits_to_compute = [('train', train_dataloader)]\n"
        "        if args.do_validation and (first_iterate or epoch % 5 == 0):\n"
        "            splits_to_compute.append(('valid', valid_dataloader))\n"
        "        first_iterate = False\n"
        "        for split_name, dataloader in splits_to_compute:\n"
        "            if split_name == 'valid':\n"
        "                model.eval()\n"
        "            else:\n"
        "                model.train()\n"
    )
    if new_schedule not in train_text:
        if legacy_patched_schedule in train_text:
            train_file.write_text(
                train_text.replace(legacy_patched_schedule, new_schedule, 1)
            )
        elif old_schedule in train_text:
            train_file.write_text(train_text.replace(old_schedule, new_schedule, 1))
        else:
            raise RuntimeError(f"Could not patch validation schedule in {train_file}")
        changed.append(str(train_file))

    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    args = parser.parse_args()
    runtime_root = Path(args.runtime_root)
    changed = patch_runtime(runtime_root)
    if changed:
        print("patched:")
        for path in changed:
            print(f"  {path}")
    else:
        print("already_patched")


if __name__ == "__main__":
    main()
