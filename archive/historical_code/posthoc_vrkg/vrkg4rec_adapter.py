"""
VRKG4Rec Adapter
================
Loads a trained VRKG4Rec model checkpoint, extracts top-K recommendations
per user, finds connecting paths via reverse-KG adjacency enumeration (fast,
O(deg²) per user), and writes the three xrecsys CSV files.

Does NOT use vrkg4rec's evaluate_vrkg_interpretability.py.
Runs in the vrkg4rec conda environment (needs PyTorch + vrkg4rec modules).

Path format produced
--------------------
  4-node: [vrkg_uid, seed_entity_id, bridge_entity_id, target_entity_id]
      → 12-token xrecsys string (full LIR/SEP/ETD support)
  3-node: [vrkg_uid, seed_entity_id, target_entity_id]
      → 9-token xrecsys string (LIR = 0)

Pre-requisite
-------------
  Run adapters/vrkg4rec_data_prep.py once before training to generate
  lookup files in adapters/vrkg_lookups/<dataset>/.

Output (written to xrecsys/paths/<dataset>/agent_topk=<tag>/)
    pred_paths.csv           uid, pid, path_score, path_prob, path
    uid_topk.csv             uid, top10
    uid_pid_explanation.csv  uid, pid, path

Usage (from eval_framework/ root, in vrkg4rec conda env):
    conda run -n vrkg4rec python adapters/vrkg4rec_adapter.py \\
        --vrkg4rec-dir /usr1/home/s125mdg43_08/vrkg4rec \\
        --ckpt weights/model_xrecsys_lastfm.ckpt \\
        --dataset lastfm \\
        --topk 10 \\
        --topk-paths 5 \\
        --gpu-id 1 \\
        --agent-topk-tag 10-12-1
"""

import argparse
import json
import os
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from base_adapter import load_train_labels, write_csvs

# ---------------------------------------------------------------------------
# Dataset constants
# ---------------------------------------------------------------------------

ITEM_ETYPE = {
    'lastfm': 'song',
    'ml1m':   'movie',
}

USER_RELATION = {
    'lastfm': 'listened',
    'ml1m':   'watched',
}

KG_RELATION = {
    'lastfm': {
        'user':         {'listened':               'song'},
        'artist':       {'sang_by':                'song',
                         'featured_by':            'song'},
        'engineer':     {'mixed_by':               'song'},
        'song':         {'listened':               'user',
                         'produced_by_producer':   'producer',
                         'sang_by':                'artist',
                         'featured_by':            'artist',
                         'mixed_by':               'engineer',
                         'belong_to':              'category',
                         'related_to':             'related_song',
                         'original_version_of':    'related_song',
                         'alternative_version_of': 'related_song'},
        'producer':     {'produced_by_producer':   'song'},
        'category':     {'belong_to':              'song'},
        'related_song': {'related_to':             'song',
                         'original_version_of':    'song',
                         'alternative_version_of': 'song'},
    },
    'ml1m': {
        'user':               {'watched':                'movie'},
        'actor':              {'starring':               'movie'},
        'director':           {'directed_by':            'movie'},
        'production_company': {'produced_by_company':    'movie'},
        'editor':             {'edited_by':              'movie'},
        'writter':            {'wrote_by':               'movie'},
        'cinematographer':    {'cinematography':         'movie'},
        'composer':           {'composed_by':            'movie'},
        'movie':              {'watched':                'user',
                               'produced_by_company':    'production_company',
                               'produced_by_producer':   'producer',
                               'edited_by':              'editor',
                               'wrote_by':               'writter',
                               'cinematography':         'cinematographer',
                               'belong_to':              'category',
                               'directed_by':            'director',
                               'starring':               'actor',
                               'composed_by':            'composer'},
        'producer':           {'produced_by_producer':   'movie'},
        'category':           {'belong_to':              'movie'},
    },
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def load_lookups(dataset: str) -> dict:
    """Load lookup tables produced by vrkg4rec_data_prep.py."""
    lookup_dir = Path(__file__).parent / 'vrkg_lookups' / dataset
    if not lookup_dir.exists():
        raise FileNotFoundError(
            f"Lookup directory not found: {lookup_dir}\n"
            f"Run adapters/vrkg4rec_data_prep.py first."
        )
    with open(lookup_dir / 'entity_to_xrecsys.json') as f:
        raw = json.load(f)
    entity_to_xrecsys = {int(k): v for k, v in raw.items()}

    with open(lookup_dir / 'uid_remap.json') as f:
        raw = json.load(f)
    vrkg_to_xrecsys_uid = {int(k): v for k, v in raw.items()}

    with open(lookup_dir / 'meta.json') as f:
        meta = json.load(f)

    return {
        'entity_to_xrecsys':   entity_to_xrecsys,
        'vrkg_to_xrecsys_uid': vrkg_to_xrecsys_uid,
        'n_items':             meta['n_items'],
    }


def load_xrecsys_kg(xrecsys_dir: Path, dataset: str):
    """
    Load xrecsys KG as a plain dict from pre-exported kg_plain.json.
    This avoids importing knowledge_graph.py (which has heavy dependencies).

    Generate kg_plain.json once with eval_frame env:
        conda run -n eval_frame python -c "
        import pickle, json, sys
        sys.path.insert(0, 'xrecsys/models/PGPR')
        with open('xrecsys/models/PGPR/tmp/<dataset>/kg.pkl', 'rb') as f:
            kg = pickle.load(f)
        out = {}
        for etype, lid_dict in kg.G.items():
            out[etype] = {}
            for lid, rel_dict in lid_dict.items():
                out[etype][int(lid)] = {rel: list(tids) for rel, tids in rel_dict.items()}
        with open('adapters/vrkg_lookups/<dataset>/kg_plain.json', 'w') as f:
            json.dump(out, f)
        "
    """
    json_path = Path(__file__).parent / 'vrkg_lookups' / dataset / 'kg_plain.json'
    if not json_path.exists():
        raise FileNotFoundError(
            f"kg_plain.json not found at {json_path}.\n"
            f"Run the export command above with eval_frame env first."
        )
    with open(json_path) as f:
        raw = json.load(f)
    # Reconstruct as nested dict with int keys where needed
    # raw: {etype: {str(lid): {rel: [tids]}}}
    class _KG:
        pass
    kg = _KG()
    kg.G = {}
    for etype, lid_dict in raw.items():
        kg.G[etype] = {}
        for lid_str, rel_dict in lid_dict.items():
            kg.G[etype][int(lid_str)] = {rel: set(tids) for rel, tids in rel_dict.items()}
    return kg


def find_relation(G, kg_relation_map, src_etype, src_lid, dst_etype, dst_lid):
    """
    Return the relation name connecting (src_etype, src_lid) → (dst_etype, dst_lid).
    Returns None if edge not found.
    """
    if src_etype not in G or src_lid not in G[src_etype]:
        return None
    neighbors = G[src_etype][src_lid]
    rel_dict  = kg_relation_map.get(src_etype, {})
    for rel_name, expected_dst_etype in rel_dict.items():
        if expected_dst_etype != dst_etype:
            continue
        if rel_name not in neighbors:
            continue
        if dst_lid in neighbors[rel_name]:
            return rel_name
    return None


# ---------------------------------------------------------------------------
# Path conversion  (unchanged logic)
# ---------------------------------------------------------------------------

def convert_path(path_nodes, vrkg_uid, xrecsys_uid, dataset, lookups, kg_G):
    """
    Convert an integer-node path to an xrecsys path string.

    4-node path → 12-token xrecsys string (full LIR/SEP/ETD support)
    3-node path →  9-token xrecsys string (LIR = 0)
    Other lengths → None (skipped)
    """
    n = len(path_nodes)
    if n < 3 or n > 4:
        return None

    item_etype  = ITEM_ETYPE[dataset]
    user_rel    = USER_RELATION[dataset]
    entity_map  = lookups['entity_to_xrecsys']
    n_items     = lookups['n_items']
    kg_rel_map  = KG_RELATION[dataset]

    item_global = path_nodes[-1]
    if item_global >= n_items:
        return None
    pid = item_global

    if n == 4:
        e1 = entity_map.get(path_nodes[1])
        e2 = entity_map.get(path_nodes[2])
        if e1 is None or e2 is None:
            return None
        e1_etype, e1_lid = e1['etype'], e1['local_id']
        e2_etype, e2_lid = e2['etype'], e2['local_id']
        if e1_etype != item_etype:
            return None
        rel2 = find_relation(kg_G.G, kg_rel_map, e1_etype, e1_lid, e2_etype, e2_lid)
        rel3 = find_relation(kg_G.G, kg_rel_map, e2_etype, e2_lid, item_etype, pid)
        if rel2 is None or rel3 is None:
            return None
        tokens = [
            'self_loop', 'user',      str(xrecsys_uid),
            user_rel,     item_etype, str(e1_lid),
            rel2,         e2_etype,   str(e2_lid),
            rel3,         item_etype, str(pid),
        ]
    else:  # n == 3
        e1 = entity_map.get(path_nodes[1])
        if e1 is None:
            return None
        e1_etype, e1_lid = e1['etype'], e1['local_id']
        if e1_etype != item_etype:
            return None
        rel2 = find_relation(kg_G.G, kg_rel_map, e1_etype, e1_lid, item_etype, pid)
        if rel2 is None:
            return None
        tokens = [
            'self_loop', 'user',      str(xrecsys_uid),
            user_rel,     item_etype, str(e1_lid),
            rel2,         item_etype, str(pid),
        ]

    return ' '.join(tokens)


# ---------------------------------------------------------------------------
# KG reverse adjacency
# ---------------------------------------------------------------------------

def build_rev_adj(kg_G, dataset, lookups):
    """
    Build reverse adjacency list from the xrecsys KG in entity_id space.
    rev_adj[tgt_entity_id] = [(src_entity_id, src_etype, src_lid), ...]
    where (src_entity_id → tgt_entity_id) is an edge in the xrecsys KG.
    """
    from collections import defaultdict as _dd
    kg_rel_map = KG_RELATION[dataset]
    entity_to_xrecsys = lookups['entity_to_xrecsys']
    xrecsys_to_entity = {(v['etype'], v['local_id']): k
                         for k, v in entity_to_xrecsys.items()}

    rev_adj = _dd(list)
    for src_etype, lid_dict in kg_G.G.items():
        rel_map = kg_rel_map.get(src_etype, {})
        for src_lid, rel_dict in lid_dict.items():
            src_entity = xrecsys_to_entity.get((src_etype, src_lid))
            if src_entity is None:
                continue
            for rel_name, tgt_lids in rel_dict.items():
                tgt_etype = rel_map.get(rel_name)
                if tgt_etype is None:
                    continue
                for tgt_lid in tgt_lids:
                    tgt_entity = xrecsys_to_entity.get((tgt_etype, tgt_lid))
                    if tgt_entity is None:
                        continue
                    rev_adj[tgt_entity].append((src_entity, src_etype, src_lid))
    return rev_adj


# ---------------------------------------------------------------------------
# Fast path finding via reverse KG traversal
# ---------------------------------------------------------------------------

def find_paths_for_item(vrkg_uid, target_entity_id, rev_adj,
                        train_items_set, entity_gcn_emb,
                        item_etype, lookups, max_n_paths=5):
    """
    Enumerate valid paths from user to target item.

    2-hop:  user → seed_item  → target_item
    3-hop:  user → seed_item  → bridge_entity → target_item

    Complexity: O(in_deg(target) * in_deg(bridge)) per call — typically <1ms.
    Returns list[(path_nodes, score)] sorted by score descending.
    """
    import torch.nn.functional as _F
    entity_map = lookups['entity_to_xrecsys']
    paths = []
    target_emb = entity_gcn_emb[target_entity_id]

    for (b_entity, b_etype, b_lid) in rev_adj.get(target_entity_id, []):
        b_emb = entity_gcn_emb[b_entity]

        if b_etype == item_etype and b_entity in train_items_set:
            # 2-hop: user → seed(=b) → target
            score = _F.cosine_similarity(
                b_emb.unsqueeze(0), target_emb.unsqueeze(0)).item()
            paths.append(([vrkg_uid, b_entity, target_entity_id], score))

        # Also try b as bridge for 3-hop (regardless of etype)
        if b_entity == target_entity_id:
            continue
        for (s_entity, s_etype, s_lid) in rev_adj.get(b_entity, []):
            if (s_etype == item_etype
                    and s_entity in train_items_set
                    and s_entity != target_entity_id):
                s_emb = entity_gcn_emb[s_entity]
                score = (_F.cosine_similarity(
                             s_emb.unsqueeze(0), b_emb.unsqueeze(0)).item()
                         + _F.cosine_similarity(
                             b_emb.unsqueeze(0), target_emb.unsqueeze(0)).item()
                         ) / 2.0
                paths.append(([vrkg_uid, s_entity, b_entity, target_entity_id], score))

    paths.sort(key=lambda x: x[1], reverse=True)
    return paths[:max_n_paths]


# ---------------------------------------------------------------------------
# VRKG4Rec model loading
# ---------------------------------------------------------------------------

def load_model_embeddings(vrkg4rec_dir: Path, ckpt_rel: str,
                          dataset_vrkg: str, gpu_id: int):
    """
    Load VRKG4Rec model from checkpoint.
    Returns (entity_gcn_emb, user_gcn_emb, n_params, train_user_set, test_user_set)
    all on CPU.
    """
    import os as _os
    import torch as _torch

    orig_dir = _os.getcwd()
    _os.chdir(str(vrkg4rec_dir))
    sys.path.insert(0, str(vrkg4rec_dir))

    try:
        # Mimic the command-line args VRKG4Rec expects
        sys.argv = [
            'adapter',
            '--dataset', dataset_vrkg,
            '--gpu_id', str(gpu_id),
            '--save', 'False',
        ]
        from utils.parser import parse_args as _parse
        from utils.data_loader import load_data as _load_data
        from utils.data_loader import train_user_set, test_user_set
        from modules.VRKG import Recommender

        args_vrkg = _parse()
        print(f"Loading VRKG4Rec data for dataset '{dataset_vrkg}' ...")
        (train_cf, test_cf, user_dict, n_params,
         graph, triplets, relation_dict,
         [adj_mat_list, norm_mat_list, mean_mat_list]) = _load_data(args_vrkg)

        device = (_torch.device(f'cuda:{gpu_id}')
                  if _torch.cuda.is_available() else _torch.device('cpu'))
        print(f"Building model on {device} ...")
        model = Recommender(n_params, args_vrkg, graph,
                            mean_mat_list[0]).to(device)

        ckpt_path = vrkg4rec_dir / ckpt_rel
        print(f"Loading checkpoint: {ckpt_path}")
        ckpt = _torch.load(str(ckpt_path), map_location=device)
        model.load_state_dict(ckpt)
        model.eval()

        print("Running model.generate() to extract embeddings ...")
        with _torch.no_grad():
            entity_gcn_emb, user_gcn_emb = model.generate()

        return (entity_gcn_emb.cpu(), user_gcn_emb.cpu(),
                n_params,
                dict(user_dict['train_user_set']),
                dict(user_dict['test_user_set']))
    finally:
        _os.chdir(orig_dir)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import torch as _torch

    parser = argparse.ArgumentParser(
        description='VRKG4Rec adapter: load model, extract paths, write xrecsys CSVs')
    parser.add_argument('--vrkg4rec-dir', required=True,
                        help='Root of vrkg4rec repo')
    parser.add_argument('--ckpt',         required=True,
                        help='Checkpoint path (relative to --vrkg4rec-dir or absolute)')
    parser.add_argument('--dataset',      required=True,
                        choices=['lastfm', 'ml1m'],
                        help='xrecsys dataset name')
    parser.add_argument('--vrkg-dataset', default=None,
                        help='VRKG4Rec dataset name (default: xrecsys_<dataset>)')
    parser.add_argument('--xrecsys-dir',  default='xrecsys',
                        help='Root of xrecsys clone (default: xrecsys/)')
    parser.add_argument('--topk',         type=int, default=10,
                        help='Top-K recommended items per user (default: 10)')
    parser.add_argument('--topk-paths',   type=int, default=5,
                        help='Max paths per (user, item) pair (default: 5)')
    parser.add_argument('--gpu-id',       type=int, default=0,
                        help='GPU id (default: 0)')
    parser.add_argument('--agent-topk-tag', default=None,
                        help='Output folder tag e.g. 10-12-1; inferred if omitted')
    args = parser.parse_args()

    vrkg4rec_dir = Path(args.vrkg4rec_dir).resolve()
    xrecsys_dir  = Path(args.xrecsys_dir).resolve()
    dataset      = args.dataset
    vrkg_dataset = args.vrkg_dataset or f'xrecsys_{dataset}'

    # ---- Load model embeddings ----
    (entity_gcn_emb, user_gcn_emb,
     n_params, train_user_set_vrkg, test_user_set_vrkg) = load_model_embeddings(
        vrkg4rec_dir, args.ckpt, vrkg_dataset, args.gpu_id)

    n_items = n_params['n_items']
    print(f"Embeddings ready: {entity_gcn_emb.shape[0]:,} entities, "
          f"{user_gcn_emb.shape[0]:,} users")

    # ---- Load lookups + xrecsys KG ----
    print("Loading lookup tables ...")
    lookups = load_lookups(dataset)

    print("Loading xrecsys KG ...")
    kg_G = load_xrecsys_kg(xrecsys_dir, dataset)

    print("Loading train labels (xrecsys) ...")
    train_set_xrecsys = load_train_labels(xrecsys_dir, dataset)

    vrkg_to_xuid = lookups['vrkg_to_xrecsys_uid']

    # ---- Build reverse KG adjacency ----
    print("Building reverse KG adjacency ...")
    rev_adj = build_rev_adj(kg_G, dataset, lookups)
    print(f"  {len(rev_adj):,} target entities in rev_adj")

    item_etype = ITEM_ETYPE[dataset]

    # ---- Precompute all item embeddings for scoring ----
    all_item_emb = entity_gcn_emb[:n_items]  # [n_items, dim]

    # ---- Per-user path extraction ----
    pred_rows    = []
    uid_topk     = {}
    uid_pid_best = {}

    test_vrkg_uids = sorted(test_user_set_vrkg.keys())
    print(f"Extracting paths for {len(test_vrkg_uids):,} test users ...")

    all_scores_flat = []  # collect for normalisation

    # First pass: find paths, collect raw scores
    raw_results = {}      # vrkg_uid → [(pid, score, path_nodes), ...]

    for i, vrkg_uid in enumerate(test_vrkg_uids):
        if i % 100 == 0:
            print(f"  [{i}/{len(test_vrkg_uids)}] users processed ...", flush=True)
        xuid = vrkg_to_xuid.get(vrkg_uid)
        if xuid is None:
            continue

        # Training items in entity_id space (= xrecsys local_id)
        train_items_set = set(train_user_set_vrkg.get(vrkg_uid, []))

        # Recommend top-K items not in training set
        u_emb = user_gcn_emb[vrkg_uid].unsqueeze(0)          # [1, dim]
        item_scores = _torch.matmul(u_emb, all_item_emb.t()).squeeze(0)  # [n_items]
        for ti in train_items_set:
            if ti < n_items:
                item_scores[ti] = float('-inf')
        top_item_ids = item_scores.topk(args.topk).indices.tolist()

        user_raw = []
        for target_entity_id in top_item_ids:
            paths = find_paths_for_item(
                vrkg_uid, target_entity_id, rev_adj,
                train_items_set, entity_gcn_emb,
                item_etype, lookups, args.topk_paths)
            for path_nodes, score in paths:
                all_scores_flat.append(score)
                user_raw.append((target_entity_id, score, path_nodes))

        raw_results[vrkg_uid] = user_raw

    if not all_scores_flat:
        print("WARNING: no valid paths found for any user.")
        return

    min_s = min(all_scores_flat)
    max_s = max(all_scores_flat)
    rng   = max_s - min_s if max_s != min_s else 1.0
    print(f"  score range: [{min_s:.4f}, {max_s:.4f}]")

    # Second pass: convert to xrecsys strings + build output
    skipped_convert = 0
    for vrkg_uid, user_raw in raw_results.items():
        xuid = vrkg_to_xuid[vrkg_uid]

        # Group by pid, keep best-score path per pid
        pid_best: dict = {}
        for (pid, score, path_nodes) in user_raw:
            norm = (score - min_s) / rng
            path_str = convert_path(path_nodes, vrkg_uid, xuid, dataset, lookups, kg_G)
            if path_str:
                pred_rows.append((xuid, pid, norm, -1, path_str))
                if pid not in pid_best or score > pid_best[pid][0]:
                    pid_best[pid] = (score, path_str)
            else:
                skipped_convert += 1
                if pid not in pid_best or score > pid_best[pid][0]:
                    pid_best[pid] = (score, None)

        items_scored = sorted(pid_best.items(),
                              key=lambda kv: kv[1][0], reverse=True)
        top_items          = items_scored[:args.topk]
        uid_topk[xuid]     = [p for p, _ in top_items]
        uid_pid_best[xuid] = {p: ps for p, (_, ps) in top_items if ps is not None}

    print(f"  skipped (bad format)    : {skipped_convert:,}")
    print(f"  pred_rows               : {len(pred_rows):,}")
    print(f"  users with top-K        : {len(uid_topk):,}")

    # ---- Write CSVs ----
    tag = args.agent_topk_tag or f"{args.topk}-{args.topk + 2}-1"
    output_dir = xrecsys_dir / 'paths' / dataset / f'agent_topk={tag}'
    print(f"Writing CSVs to {output_dir} ...")
    write_csvs(output_dir, pred_rows, uid_topk, uid_pid_best)

    print("Done.")
    print(f"  pred_paths.csv          : {len(pred_rows):,} rows")
    print(f"  uid_topk.csv            : {len(uid_topk):,} users")
    print(f"  uid_pid_explanation.csv : "
          f"{sum(len(v) for v in uid_pid_best.values()):,} uid-pid pairs")


if __name__ == '__main__':
    main()
