#!/usr/bin/env python3
"""Smoke-test patched PGPR policy environment and beam search for Amazon."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--dataset", default="amazon_book_kgat_v1")
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--max-acts", type=int, default=10000)
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    summary_path = Path(args.summary_json).resolve()
    pgpr_root = runtime_root / "models" / "PGPR"
    os.chdir(pgpr_root)
    sys.path.insert(0, str(pgpr_root))
    sys.path.insert(0, str(runtime_root))

    import numpy as np
    import torch

    from kg_env import BatchKGEnvironment
    from test_agent import batch_beam_search
    from train_agent import ActorCritic
    from utils import (
        BOOK,
        ENTITY,
        SELF_LOOP,
        USER,
        get_book_relationships,
        load_labels,
    )

    env = BatchKGEnvironment(args.dataset, args.max_acts, max_path_len=3, state_history=1)
    train_labels = load_labels(args.dataset, "train")
    chosen = None
    for uid in sorted(train_labels):
        for pid in train_labels[uid]:
            for relation in get_book_relationships():
                middle_entities = env.kg(BOOK, pid, relation)
                for middle_entity in middle_entities:
                    tail_books = [
                        book
                        for book in env.kg(ENTITY, middle_entity, relation)
                        if book != pid
                    ]
                    if tail_books:
                        chosen = {
                            "uid": uid,
                            "source_book": pid,
                            "relation": relation,
                            "entity": middle_entity,
                            "target_book": tail_books[0],
                        }
                        break
                if chosen:
                    break
            if chosen:
                break
        if chosen:
            break
    if chosen is None:
        raise RuntimeError("Could not find an Amazon PGPR native book-entity-book path")

    def select_action(expected_relation: str, expected_node: int) -> int:
        actions = env._batch_curr_actions[0]
        for index, (relation, node_id) in enumerate(actions):
            if relation == expected_relation and node_id == expected_node:
                return index
        raise RuntimeError(
            f"Missing action relation={expected_relation!r} node={expected_node}; "
            f"available_examples={actions[:20]}"
        )

    env.reset([chosen["uid"]])
    manual_rewards = []
    manual_done = False
    purchased_action = select_action("purchased", chosen["source_book"])
    _state, reward, manual_done = env.batch_step([purchased_action])
    manual_rewards.append(float(reward[0]))
    relation_action = select_action(chosen["relation"], chosen["entity"])
    _state, reward, manual_done = env.batch_step([relation_action])
    manual_rewards.append(float(reward[0]))
    target_action = select_action(chosen["relation"], chosen["target_book"])
    _state, reward, manual_done = env.batch_step([target_action])
    manual_rewards.append(float(reward[0]))
    manual_path = env._batch_path[0]
    manual_pattern_ok = env._has_pattern(manual_path)
    manual_final_is_book = manual_path[-1][1] == BOOK
    manual_reward_finite = all(math.isfinite(value) for value in manual_rewards)

    torch.manual_seed(123)
    np.random.seed(123)
    model = ActorCritic(
        env.state_dim,
        env.act_dim,
        gamma=0.99,
        hidden_sizes=[32, 16],
    ).to(torch.device("cpu"))
    beam_paths, beam_probs = batch_beam_search(
        env,
        model,
        [chosen["uid"]],
        torch.device("cpu"),
        topk=[2, 2, 1],
    )
    beam_book_endings = sum(path[-1][1] == BOOK for path in beam_paths)
    status = "PASS"
    if not (
        manual_done
        and manual_pattern_ok
        and manual_final_is_book
        and manual_reward_finite
        and beam_paths
    ):
        status = "FAIL"
    summary = {
        "dataset": args.dataset,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "runtime_root": str(runtime_root),
        "max_acts": args.max_acts,
        "state_dim": env.state_dim,
        "act_dim": env.act_dim,
        "embed_size": env.embed_size,
        "selected_path": chosen,
        "manual_path": manual_path,
        "manual_done": manual_done,
        "manual_pattern_ok": manual_pattern_ok,
        "manual_final_is_book": manual_final_is_book,
        "manual_rewards": manual_rewards,
        "manual_reward_finite": manual_reward_finite,
        "beam_path_count": len(beam_paths),
        "beam_probability_rows": len(beam_probs),
        "beam_book_endings": beam_book_endings,
        "beam_path_examples": beam_paths[:5],
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
