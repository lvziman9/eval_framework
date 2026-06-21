#!/usr/bin/env python3
"""Apply reproducible inference fixes to an isolated PGPR runtime copy."""

from __future__ import annotations

import argparse
from pathlib import Path


def patch_runtime(runtime_root: Path) -> list[str]:
    test_file = runtime_root / "models" / "PGPR" / "test_agent.py"
    text = test_file.read_text()
    original = text
    changed = []

    # This import is only used by the legacy built-in evaluation. Canonical
    # runs export native paths and evaluate them through the shared adapter.
    text = text.replace("from myutils import get_interaction2timestamp\n", "")
    text = text.replace(
        "    r = np.asfarray(r)[:k]\n",
        "    r = np.asarray(r, dtype=float)[:k]\n",
    )
    old_probability_block = (
        "        probs, _ = model((state_tensor, actmask_tensor))  # Tensor of [bs, act_dim]\n"
        "        probs = probs + actmask_tensor.float()  # In order to differ from masked actions\n"
        "        topk_probs, topk_idxs = torch.topk(probs, topk[hop], dim=1)  # LongTensor of [bs, k]\n"
    )
    new_probability_block = (
        "        probs, _ = model((state_tensor, actmask_tensor))  # Tensor of [bs, act_dim]\n"
        "        selection_scores = probs + actmask_tensor.float()\n"
        "        _, topk_idxs = torch.topk(selection_scores, topk[hop], dim=1)\n"
        "        # Keep the original policy probability in exported paths; the +1\n"
        "        # mask offset is only an action-selection device.\n"
        "        topk_probs = probs.gather(1, topk_idxs)\n"
    )
    if new_probability_block not in text:
        if old_probability_block not in text:
            raise RuntimeError(f"Could not patch exported path probabilities in {test_file}")
        text = text.replace(old_probability_block, new_probability_block, 1)

    beam_function = "def batch_beam_search(env, model, uids, device, topk=[25, 5, 1]):\n"
    decorated_beam_function = "@torch.no_grad()\n" + beam_function
    if decorated_beam_function not in text:
        if beam_function not in text:
            raise RuntimeError(f"Could not add no_grad to {test_file}")
        text = text.replace(beam_function, decorated_beam_function, 1)

    if "    batch_size = args.beam_batch_size\n" not in text:
        if "    batch_size = 16\n" not in text:
            raise RuntimeError(f"Could not patch beam batch size in {test_file}")
        text = text.replace(
            "    batch_size = 16\n",
            "    batch_size = args.beam_batch_size\n",
            1,
        )

    topk_arg = (
        "    parser.add_argument('--topk', type=list, nargs='*', "
        "default=[25,50,1], help='number of samples')\n"
    )
    fixed_topk_arg = (
        "    parser.add_argument('--topk', type=int, nargs='*', "
        "default=[25,50,1], help='number of samples')\n"
        "    parser.add_argument('--beam_batch_size', type=int, default=16, "
        "help='number of users per inference beam batch')\n"
    )
    if fixed_topk_arg not in text:
        if topk_arg not in text:
            raise RuntimeError(f"Could not patch top-k parser in {test_file}")
        text = text.replace(topk_arg, fixed_topk_arg, 1)

    if "        torch.cuda.empty_cache()\n" not in text:
        marker = "        pbar.update(batch_size)\n"
        if marker not in text:
            raise RuntimeError(f"Could not add CUDA cache cleanup to {test_file}")
        text = text.replace(
            marker,
            marker
            + "        if torch.cuda.is_available():\n"
            + "            torch.cuda.empty_cache()\n",
            1,
        )

    seed_marker = "    args.log_dir = TMP_DIR[args.dataset] + '/' + args.name\n    test(args)\n"
    seeded_marker = "    args.log_dir = TMP_DIR[args.dataset] + '/' + args.name\n    set_random_seed(args.seed)\n    test(args)\n"
    if seeded_marker not in text:
        if seed_marker not in text:
            raise RuntimeError(f"Could not add inference seed to {test_file}")
        text = text.replace(seed_marker, seeded_marker, 1)

    if text != original:
        test_file.write_text(text)
        changed.append(str(test_file))

    kg_env_file = runtime_root / "models" / "PGPR" / "kg_env.py"
    kg_text = kg_env_file.read_text()
    old_scale = """        # Compute user-product scores for scaling.
        if dataset_str == \"ml1m\":
            u_p_scores = np.dot(self.embeds[USER] + self.embeds[WATCHED][0], self.embeds[MOVIE].T)
        elif dataset_str == \"lastfm\":
            u_p_scores = np.dot(self.embeds[USER] + self.embeds[LISTENED][0], self.embeds[SONG].T)
        self.u_p_scales = np.max(u_p_scores, axis=1)
"""
    new_scale = """        # Compute the per-user maximum without materializing the
        # complete user-product score matrix.
        if dataset_str == \"ml1m\":
            user_queries = self.embeds[USER] + self.embeds[WATCHED][0]
            product_embeds = self.embeds[MOVIE]
        elif dataset_str == \"lastfm\":
            user_queries = self.embeds[USER] + self.embeds[LISTENED][0]
            product_embeds = self.embeds[SONG]
        self.u_p_scales = np.empty(len(user_queries), dtype=np.float32)
        score_batch_size = 256
        for start in range(0, len(user_queries), score_batch_size):
            end = min(start + score_batch_size, len(user_queries))
            batch_scores = np.dot(user_queries[start:end], product_embeds.T)
            self.u_p_scales[start:end] = np.max(batch_scores, axis=1)
"""
    if new_scale not in kg_text:
        if old_scale not in kg_text:
            raise RuntimeError(f"Could not patch batched user-product scaling in {kg_env_file}")
        kg_env_file.write_text(kg_text.replace(old_scale, new_scale, 1))
        changed.append(str(kg_env_file))

    train_file = runtime_root / "models" / "PGPR" / "train_agent.py"
    train_text = train_file.read_text()
    fixed_dropout = train_text.replace(
        "F.dropout(F.elu(x), p=0.5)",
        "F.dropout(F.elu(x), p=0.5, training=self.training)",
    ).replace(
        "F.dropout(F.elu(out), p=0.5)",
        "F.dropout(F.elu(out), p=0.5, training=self.training)",
    )
    if fixed_dropout.count("training=self.training") < 2:
        raise RuntimeError(f"Could not patch inference dropout in {train_file}")
    if fixed_dropout != train_text:
        train_file.write_text(fixed_dropout)
        changed.append(str(train_file))

    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    args = parser.parse_args()
    changed = patch_runtime(Path(args.runtime_root))
    if changed:
        print("patched:")
        for path in changed:
            print(f"  {path}")
    else:
        print("already_patched")


if __name__ == "__main__":
    main()
