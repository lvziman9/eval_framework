import argparse
import csv
import gzip
import pickle
from collections import defaultdict
from pathlib import Path


def load_user_mapping(mapping_path):
    mapping = {}
    with open(mapping_path, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for row in reader:
            if not row:
                continue
            kgid = int(row[0])
            raw_uid = int(row[1])
            mapping[raw_uid] = kgid
    return mapping


def load_valid_product_ids(mapping_path):
    valid = set()
    with open(mapping_path, "r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for row in reader:
            if not row:
                continue
            valid.add(int(row[0]))
    return valid


def build_labels(split_path, user_map, valid_product_ids):
    labels = defaultdict(list)
    skipped_user = 0
    skipped_product = 0
    kept = 0
    with gzip.open(split_path, "rt") as f:
        reader = csv.reader(f, delimiter=" ")
        for row in reader:
            if not row:
                continue
            raw_uid = int(row[0])
            raw_pid = int(row[1])
            uid = user_map.get(raw_uid)
            if uid is None:
                skipped_user += 1
                continue
            pid = raw_pid
            if pid not in valid_product_ids:
                skipped_product += 1
                continue
            labels[uid].append(pid)
            kept += 1
    return dict(labels), {
        "kept_interactions": kept,
        "skipped_user_interactions": skipped_user,
        "skipped_product_interactions": skipped_product,
        "users": len(labels),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", required=True, help="Dataset root, e.g. xrecsys/datasets/lastfm")
    parser.add_argument("--out-dir", required=True, help="Output directory for canonical labels")
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    user_map = load_user_mapping(dataset_dir / "mappings" / "user_mappings.txt")
    valid_product_ids = load_valid_product_ids(dataset_dir / "mappings" / "product_mappings.txt")

    train_labels, train_stats = build_labels(dataset_dir / "train.txt.gz", user_map, valid_product_ids)
    test_labels, test_stats = build_labels(dataset_dir / "test.txt.gz", user_map, valid_product_ids)

    with open(out_dir / "train_label.pkl", "wb") as f:
        pickle.dump(train_labels, f)
    with open(out_dir / "test_label.pkl", "wb") as f:
        pickle.dump(test_labels, f)

    with open(out_dir / "summary.txt", "w") as f:
        f.write("canonical labels summary\n")
        f.write(f"dataset_dir={dataset_dir}\n")
        f.write(f"train_users={train_stats['users']}\n")
        f.write(f"train_kept_interactions={train_stats['kept_interactions']}\n")
        f.write(f"train_skipped_user_interactions={train_stats['skipped_user_interactions']}\n")
        f.write(f"train_skipped_product_interactions={train_stats['skipped_product_interactions']}\n")
        f.write(f"test_users={test_stats['users']}\n")
        f.write(f"test_kept_interactions={test_stats['kept_interactions']}\n")
        f.write(f"test_skipped_user_interactions={test_stats['skipped_user_interactions']}\n")
        f.write(f"test_skipped_product_interactions={test_stats['skipped_product_interactions']}\n")

    print("Wrote canonical labels to", out_dir)
    print("Train stats:", train_stats)
    print("Test stats:", test_stats)


if __name__ == "__main__":
    main()
