"""
VRKG4Rec Data Prep
==================
Converts xrecsys dataset (kg.pkl + train/test_label.pkl) into the input
format expected by VRKG4Rec, and saves reverse-lookup tables used by
vrkg4rec_adapter.py to convert paths back to xrecsys strings.

Run once before training VRKG4Rec on a new dataset.

Output directory: <vrkg4rec_dir>/data/<vrkg_dataset>/
    train_data.pkl            numpy [N, 3] (vrkg_uid, item_idx, 1)
    test_data.pkl
    kg_final.txt              head_entity_id  relation_id  tail_entity_id
    kg_final.npy              same content as numpy array
    item_index2entity_id.txt  entity_id  item_index   (VRKG4Rec convention)

Output lookup dir: <eval_framework>/adapters/vrkg_lookups/<dataset>/
    entity_to_xrecsys.json    {entity_id: {"etype": str, "local_id": int}}
    uid_remap.json            {vrkg_uid(str): xrecsys_uid}
    relation_names.json       {relation_id(str): relation_name}
    meta.json                 n_users, n_items, n_entities, n_relations, dataset

Usage (from eval_framework/ root):
    conda run -n eval_frame python adapters/vrkg4rec_data_prep.py \\
        --dataset lastfm \\
        --vrkg4rec-dir /path/to/vrkg4rec \\
        --vrkg-dataset-name xrecsys_lastfm
"""

import argparse
import json
import os
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Dataset-specific constants (mirrors models/PGPR/utils.py)
# ---------------------------------------------------------------------------

LASTFM_KG_RELATION = {
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
}

ML1M_KG_RELATION = {
    'user':              {'watched':                'movie'},
    'actor':             {'starring':               'movie'},
    'director':          {'directed_by':            'movie'},
    'production_company':{'produced_by_company':    'movie'},
    'editor':            {'edited_by':              'movie'},
    'writter':           {'wrote_by':               'movie'},
    'cinematographer':   {'cinematography':         'movie'},
    'composer':          {'composed_by':            'movie'},
    'movie':             {'watched':                'user',
                          'produced_by_company':    'production_company',
                          'produced_by_producer':   'producer',
                          'edited_by':              'editor',
                          'wrote_by':               'writter',
                          'cinematography':         'cinematographer',
                          'belong_to':              'category',
                          'directed_by':            'director',
                          'starring':               'actor',
                          'composed_by':            'composer'},
    'producer':          {'produced_by_producer':   'movie'},
    'category':          {'belong_to':              'movie'},
}

KG_RELATION = {
    'lastfm': LASTFM_KG_RELATION,
    'ml1m':   ML1M_KG_RELATION,
}

ITEM_ETYPE = {
    'lastfm': 'song',
    'ml1m':   'movie',
}

USER_RELATION = {
    'lastfm': 'listened',
    'ml1m':   'watched',
}


def load_xrecsys_data(xrecsys_dir: Path, dataset: str):
    """Load kg.pkl + train/test_label.pkl from xrecsys tmp directory."""
    sys.path.insert(0, str(xrecsys_dir / 'models' / 'PGPR'))
    tmp = xrecsys_dir / 'models' / 'PGPR' / 'tmp' / dataset

    with open(tmp / 'kg.pkl', 'rb') as f:
        kg = pickle.load(f)
    with open(tmp / 'train_label.pkl', 'rb') as f:
        train_labels = pickle.load(f)   # {uid: [item_id, ...]}
    with open(tmp / 'test_label.pkl', 'rb') as f:
        test_labels = pickle.load(f)

    return kg, train_labels, test_labels


def build_entity_index(kg_G, entity_types, item_etype):
    """
    Assign VRKG4Rec global entity IDs to all (etype, local_id) pairs.
    Items (ITEM_ETYPE) are assigned first so that item_index == entity_id.

    Returns:
        entity_to_global : {(etype, local_id): global_id}
        global_to_xrecsys: {global_id: {"etype": etype, "local_id": local_id}}
        n_items          : total number of item entities
    """
    entity_to_global = {}
    global_to_xrecsys = {}
    counter = 0

    # Items first (so item_index = entity_id)
    item_ids = sorted(kg_G[item_etype].keys())
    for lid in item_ids:
        entity_to_global[(item_etype, lid)] = counter
        global_to_xrecsys[counter] = {'etype': item_etype, 'local_id': lid}
        counter += 1
    n_items = counter

    # All other entity types
    for etype in entity_types:
        if etype in ('user', item_etype):
            continue
        for lid in sorted(kg_G[etype].keys()):
            entity_to_global[(etype, lid)] = counter
            global_to_xrecsys[counter] = {'etype': etype, 'local_id': lid}
            counter += 1

    return entity_to_global, global_to_xrecsys, n_items


def build_kg_triples(kg_G, entity_to_global, kg_relation, item_etype):
    """
    Enumerate all KG edges and assign integer relation IDs.
    User↔item interactions are handled separately by VRKG4Rec.

    Returns:
        triples         : list of (head_id, rel_id, tail_id)
        rel_name_to_id  : {relation_name: rel_id}
        rel_id_to_name  : {rel_id: relation_name}
    """
    rel_name_to_id = {}
    triples = []

    for src_etype, rel_dict in kg_relation.items():
        if src_etype == 'user':
            continue  # user→item edges are in train_data, not kg_final
        if src_etype not in kg_G:
            continue
        for rel_name, dst_etype in rel_dict.items():
            if rel_name not in rel_name_to_id:
                rel_name_to_id[rel_name] = len(rel_name_to_id)
            rel_id = rel_name_to_id[rel_name]

            if dst_etype not in kg_G:
                continue
            for src_lid, neighbors in kg_G[src_etype].items():
                if rel_name not in neighbors:
                    continue
                src_gid = entity_to_global.get((src_etype, src_lid))
                if src_gid is None:
                    continue
                for dst_lid in neighbors[rel_name]:
                    dst_gid = entity_to_global.get((dst_etype, dst_lid))
                    if dst_gid is None:
                        continue
                    triples.append((src_gid, rel_id, dst_gid))

    rel_id_to_name = {v: k for k, v in rel_name_to_id.items()}
    return triples, rel_name_to_id, rel_id_to_name


def build_interaction_arrays(train_labels, test_labels, item_etype, kg_G):
    """
    Build numpy arrays for VRKG4Rec train/test data.
    Also build uid remap: xrecsys_uid → vrkg_uid (0-indexed).

    VRKG4Rec expects: [vrkg_uid, item_idx, label]
    item_idx == entity_id for item entities (since we assigned them first).
    """
    # Collect all user IDs; remap to 0-indexed
    all_uids = sorted(set(list(train_labels.keys()) + list(test_labels.keys())))
    xrecsys_to_vrkg_uid = {uid: i for i, uid in enumerate(all_uids)}
    vrkg_to_xrecsys_uid = {i: uid for uid, i in xrecsys_to_vrkg_uid.items()}

    item_ids = sorted(kg_G[item_etype].keys())
    item_lid_to_idx = {lid: idx for idx, lid in enumerate(item_ids)}

    def make_array(labels):
        rows = []
        for xuid, items in labels.items():
            vuid = xrecsys_to_vrkg_uid[xuid]
            for item_lid in items:
                idx = item_lid_to_idx.get(item_lid)
                if idx is not None:
                    rows.append([vuid, idx, 1])
        return np.array(rows, dtype=np.int32) if rows else np.zeros((0, 3), dtype=np.int32)

    train_arr = make_array(train_labels)
    test_arr  = make_array(test_labels)

    return train_arr, test_arr, xrecsys_to_vrkg_uid, vrkg_to_xrecsys_uid, item_lid_to_idx


def save_outputs(
    vrkg_data_dir: Path,
    lookup_dir: Path,
    train_arr, test_arr,
    triples,
    global_to_xrecsys,
    vrkg_to_xrecsys_uid,
    xrecsys_to_vrkg_uid,
    rel_id_to_name,
    n_items,
    dataset,
    vrkg_dataset_name,
):
    vrkg_data_dir.mkdir(parents=True, exist_ok=True)
    lookup_dir.mkdir(parents=True, exist_ok=True)

    # --- VRKG4Rec data files ---
    with open(vrkg_data_dir / 'train_data.pkl', 'wb') as f:
        pickle.dump(train_arr, f)
    with open(vrkg_data_dir / 'test_data.pkl', 'wb') as f:
        pickle.dump(test_arr, f)

    triples_np = np.array(triples, dtype=np.int32)
    np.save(vrkg_data_dir / 'kg_final.npy', triples_np)
    np.savetxt(str(vrkg_data_dir / 'kg_final.txt'),
               triples_np, fmt='%d', delimiter='\t')

    # item_index2entity_id.txt: entity_id  item_index
    # (VRKG4Rec convention: col0=entity_id, col1=item_index)
    # Since we assigned entity_id = item_index for songs, it's trivial.
    with open(vrkg_data_dir / 'item_index2entity_id.txt', 'w') as f:
        for gid, info in global_to_xrecsys.items():
            if gid < n_items:   # only items
                f.write(f"{gid}\t{gid}\n")

    # --- Lookup tables for adapter ---
    # entity_to_xrecsys: {entity_id_str: {"etype": ..., "local_id": ...}}
    with open(lookup_dir / 'entity_to_xrecsys.json', 'w') as f:
        json.dump({str(k): v for k, v in global_to_xrecsys.items()}, f)

    with open(lookup_dir / 'uid_remap.json', 'w') as f:
        json.dump({str(k): v for k, v in vrkg_to_xrecsys_uid.items()}, f)

    with open(lookup_dir / 'relation_names.json', 'w') as f:
        json.dump({str(k): v for k, v in rel_id_to_name.items()}, f)

    n_users    = len(vrkg_to_xrecsys_uid)
    n_entities = len(global_to_xrecsys)
    n_relations = len(rel_id_to_name)
    meta = {
        'dataset':          dataset,
        'vrkg_dataset_name': vrkg_dataset_name,
        'n_users':          n_users,
        'n_items':          n_items,
        'n_entities':       n_entities,
        'n_relations':      n_relations,
    }
    with open(lookup_dir / 'meta.json', 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"  train interactions : {len(train_arr):,}")
    print(f"  test  interactions : {len(test_arr):,}")
    print(f"  KG triples         : {len(triples):,}")
    print(f"  n_users            : {n_users:,}")
    print(f"  n_items            : {n_items:,}")
    print(f"  n_entities         : {n_entities:,}")
    print(f"  n_relations        : {n_relations}")
    print(f"\n  VRKG4Rec data  → {vrkg_data_dir}")
    print(f"  Adapter lookups→ {lookup_dir}")


def run(dataset, vrkg4rec_dir, vrkg_dataset_name, xrecsys_dir):
    xrecsys_dir  = Path(xrecsys_dir)
    vrkg4rec_dir = Path(vrkg4rec_dir)
    lookup_dir   = Path(__file__).parent / 'vrkg_lookups' / dataset

    kg_relation = KG_RELATION[dataset]
    item_etype  = ITEM_ETYPE[dataset]

    print(f"Loading xrecsys '{dataset}' data ...")
    kg, train_labels, test_labels = load_xrecsys_data(xrecsys_dir, dataset)

    entity_types = list(kg.G.keys())
    print(f"  Entity types: {entity_types}")

    print("Building entity index ...")
    entity_to_global, global_to_xrecsys, n_items = build_entity_index(
        kg.G, entity_types, item_etype)

    print("Building KG triples ...")
    triples, rel_name_to_id, rel_id_to_name = build_kg_triples(
        kg.G, entity_to_global, kg_relation, item_etype)

    print("Building interaction arrays ...")
    (train_arr, test_arr,
     xrecsys_to_vrkg_uid, vrkg_to_xrecsys_uid,
     item_lid_to_idx) = build_interaction_arrays(
        train_labels, test_labels, item_etype, kg.G)

    vrkg_data_dir = vrkg4rec_dir / 'data' / vrkg_dataset_name
    print(f"\nSaving outputs ...")
    save_outputs(
        vrkg_data_dir, lookup_dir,
        train_arr, test_arr, triples,
        global_to_xrecsys, vrkg_to_xrecsys_uid, xrecsys_to_vrkg_uid,
        rel_id_to_name, n_items, dataset, vrkg_dataset_name,
    )
    print("\nDone.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare xrecsys data for VRKG4Rec')
    parser.add_argument('--dataset',          required=True,
                        choices=['lastfm', 'ml1m'],
                        help='xrecsys dataset name')
    parser.add_argument('--vrkg4rec-dir',     required=True,
                        help='Root of VRKG4Rec repo')
    parser.add_argument('--vrkg-dataset-name', required=True,
                        help='Name for the new dataset dir under vrkg4rec/data/')
    parser.add_argument('--xrecsys-dir',      default='xrecsys',
                        help='Root of xrecsys repo (default: xrecsys/)')
    args = parser.parse_args()

    run(
        dataset=args.dataset,
        vrkg4rec_dir=args.vrkg4rec_dir,
        vrkg_dataset_name=args.vrkg_dataset_name,
        xrecsys_dir=args.xrecsys_dir,
    )
