#!/usr/bin/env python3
"""Apply reproducible inference fixes to a UCPR runtime copy.

The upstream parser accepts ``--topk`` and then unconditionally resets it to
``[25, 5, 1]``. Its beam search also adds one to valid action probabilities
for top-k selection and accidentally persists those offset values as native
probabilities. This patch is intentionally applied to an experiment runtime
copy rather than the external source repository.
"""

from __future__ import annotations

import argparse
from pathlib import Path


HARDCODED_TOPK_LINE = "    args.topk = [25, 5, 1]\n"
TOPK_REPLACEMENT_LINE = "    # Preserve the --topk value parsed from the command line.\n"
EMPTY_TAG_LINE = '    args.topk_string = ""\n'
TAG_REPLACEMENT_LINE = '    args.topk_string = "-".join(str(k) for k in args.topk)\n'


def patch_file(path: Path) -> str:
    text = path.read_text()
    changed = False
    if HARDCODED_TOPK_LINE in text:
        text = text.replace(HARDCODED_TOPK_LINE, TOPK_REPLACEMENT_LINE, 1)
        changed = True
    elif TOPK_REPLACEMENT_LINE not in text:
        raise RuntimeError(
            f"Could not find the expected UCPR top-k override in {path}; "
            "the upstream parser may have changed."
        )

    if EMPTY_TAG_LINE in text:
        text = text.replace(EMPTY_TAG_LINE, TAG_REPLACEMENT_LINE, 1)
        changed = True
    elif TAG_REPLACEMENT_LINE not in text:
        raise RuntimeError(
            f"Could not find the expected UCPR top-k tag override in {path}; "
            "the upstream parser may have changed."
        )

    if changed:
        path.write_text(text)
        return "patched"
    if TOPK_REPLACEMENT_LINE in text and TAG_REPLACEMENT_LINE in text:
        return "already_patched"
    raise RuntimeError(f"Unexpected patch state in {path}")


def patch_distribution_file(path: Path) -> bool:
    text = path.read_text()
    old = (
        "        distrib = np.power(np.array(distrib, dtype=np.float), 0.75)\n"
        "        distrib = distrib / distrib.sum()\n"
    )
    partially_patched = (
        "        distrib = np.power(np.array(distrib, dtype=float), 0.75)\n"
        "        distrib = distrib / distrib.sum()\n"
    )
    new = (
        "        distrib = np.power(np.array(distrib, dtype=float), 0.75)\n"
        "        if distrib.sum() <= 0:\n"
        "            distrib = np.ones_like(distrib, dtype=float)\n"
        "        distrib = distrib / distrib.sum()\n"
    )
    if new in text:
        return False
    if old in text:
        path.write_text(text.replace(old, new, 1))
        return True
    if partially_patched in text:
        path.write_text(text.replace(partially_patched, new, 1))
        return True
    raise RuntimeError(f"Could not find the UCPR distribution normalization in {path}")


def patch_beam_batch(runtime_root: Path) -> list[tuple[str, Path]]:
    statuses = []
    parser_path = runtime_root / "models" / "UCPR" / "src" / "parser.py"
    parser_text = parser_path.read_text()
    parser_old = (
        "    parser.add_argument('--topk', type=int, nargs='*', default=[25, 5, 1], help='number of samples')\n"
    )
    parser_new = (
        parser_old
        + "    parser.add_argument('--beam_batch_size', type=int, default=16, "
        "help='number of users per inference beam batch')\n"
    )
    if "--beam_batch_size" not in parser_text:
        if parser_old not in parser_text:
            raise RuntimeError(f"Could not add beam_batch_size to {parser_path}")
        parser_path.write_text(parser_text.replace(parser_old, parser_new, 1))
        statuses.append(("patched", parser_path))
    else:
        statuses.append(("already_patched", parser_path))

    test_path = runtime_root / "models" / "UCPR" / "test.py"
    test_text = test_path.read_text()
    changed = False
    beam_function = "def batch_beam_search(args, env, model, uids, device, topk=[25, 5, 1]):\n"
    decorated_beam_function = "@torch.no_grad()\n" + beam_function
    if decorated_beam_function not in test_text:
        if beam_function not in test_text:
            raise RuntimeError(f"Could not add no_grad to {test_path}")
        test_text = test_text.replace(beam_function, decorated_beam_function, 1)
        changed = True
    if "    batch_size = 16\n" in test_text:
        test_text = test_text.replace(
            "    batch_size = 16\n",
            "    batch_size = args.beam_batch_size\n",
            1,
        )
        changed = True
    if "        torch.cuda.empty_cache()\n" not in test_text:
        marker = "        pbar.update(batch_size)\n"
        if marker not in test_text:
            raise RuntimeError(f"Could not add CUDA cache cleanup to {test_path}")
        test_text = test_text.replace(
            marker,
            marker + "        if torch.cuda.is_available():\n            torch.cuda.empty_cache()\n",
            1,
        )
        changed = True

    old_probability_selection = (
        "        probs = probs + actmask_tensor.float()  # In order to differ from masked actions\n"
        "        del actmask_tensor\n"
        "        topk_probs, topk_idxs = torch.topk(probs, topk[hop], dim=1)  # LongTensor of [bs, k]\n"
        "        topk_idxs = topk_idxs.detach().cpu().numpy()\n"
        "        topk_probs = topk_probs.detach().cpu().numpy()\n"
    )
    new_probability_selection = (
        "        # Use the +1 mask offset only to select valid actions. Persist the\n"
        "        # original softmax probabilities so a three-hop path probability\n"
        "        # remains the product of values in [0, 1].\n"
        "        selection_probs = probs + actmask_tensor.float()\n"
        "        _, topk_idxs = torch.topk(selection_probs, topk[hop], dim=1)\n"
        "        topk_probs = torch.gather(probs, 1, topk_idxs)\n"
        "        del actmask_tensor, selection_probs\n"
        "        topk_idxs = topk_idxs.detach().cpu().numpy()\n"
        "        topk_probs = topk_probs.detach().cpu().numpy()\n"
    )
    if new_probability_selection not in test_text:
        if old_probability_selection not in test_text:
            raise RuntimeError(
                f"Could not patch native UCPR action probabilities in {test_path}"
            )
        test_text = test_text.replace(
            old_probability_selection, new_probability_selection, 1
        )
        changed = True

    probability_helper = (
        "\n\ndef _native_path_probability(probs):\n"
        "    \"\"\"Return a true path probability, repairing historical +1 offsets.\"\"\"\n"
        "    values = np.asarray(probs, dtype=float)\n"
        "    if values.size == 0:\n"
        "        return 1.0\n"
        "    if np.max(values) > 1.0:\n"
        "        values = values - 1.0\n"
        "    if np.any(values < -1e-6) or np.any(values > 1.0 + 1e-6):\n"
        "        raise ValueError(f\"Invalid UCPR action probabilities: {values}\")\n"
        "    values = np.clip(values, 0.0, 1.0)\n"
        "    return float(np.prod(values))\n"
    )
    tolerant_probability_helper = probability_helper.replace(
        "if np.max(values) > 1.0:",
        "if np.max(values) > 1.0 + 1e-6:",
    )
    extract_marker = "\ndef extract_paths(dataset_name, path_file, train_labels, valid_labels, test_labels):\n"
    if probability_helper not in test_text:
        if tolerant_probability_helper in test_text:
            test_text = test_text.replace(
                tolerant_probability_helper, probability_helper, 1
            )
            changed = True
        elif extract_marker not in test_text:
            raise RuntimeError(
                f"Could not add native path probability helper to {test_path}"
            )
        else:
            test_text = test_text.replace(
                extract_marker, probability_helper + extract_marker, 1
            )
            changed = True

    legacy_probability_line = (
        "        path_prob = reduce(lambda x, y: x * y, probs)\n"
    )
    native_probability_line = (
        "        path_prob = _native_path_probability(probs)\n"
    )
    if legacy_probability_line in test_text:
        test_text = test_text.replace(
            legacy_probability_line, native_probability_line
        )
        changed = True
    if test_text.count(native_probability_line) < 2:
        raise RuntimeError(
            f"Expected both UCPR path extraction branches to use native probabilities in {test_path}"
        )

    if changed:
        test_path.write_text(test_text)
        statuses.append(("patched", test_path))
    else:
        statuses.append(("already_patched", test_path))
    return statuses


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runtime-root",
        required=True,
        help="Runtime root containing models/UCPR/src/parser.py",
    )
    args = parser.parse_args()

    parser_path = Path(args.runtime_root) / "models" / "UCPR" / "src" / "parser.py"
    if not parser_path.exists():
        raise FileNotFoundError(parser_path)
    statuses = [(patch_file(parser_path), parser_path)]
    statuses.extend(patch_beam_batch(Path(args.runtime_root)))
    for relative in [
        "models/UCPR/preprocess/transe_model.py",
        "models/UCPR/src/model/lstm_base/model_kg.py",
        "models/UCPR/src/model/lstm_base/model_kg_pre.py",
    ]:
        path = Path(args.runtime_root) / relative
        statuses.append(("patched" if patch_distribution_file(path) else "already_patched", path))
    for status, path in statuses:
        print(f"{status}: {path}")


if __name__ == "__main__":
    main()
