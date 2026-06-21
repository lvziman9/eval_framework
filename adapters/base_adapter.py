"""
Shared utilities for all model adapters.

Adapters convert model-specific output into the three CSV files
required by xrecsys:

  pred_paths.csv          uid, pid, path_score, path_prob, path
  uid_topk.csv            uid, top10
  uid_pid_explanation.csv uid, pid, path

Path string format (xrecsys convention):
  Each hop is a (relation, entity_type, entity_id) triple,
  all triples are space-joined:
  "self_loop user 1 watched movie 466 belong_to category 86 belong_to movie 956"
"""

import csv
import pickle
from pathlib import Path
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def format_path(path_tuples) -> str:
    """Flatten a list of (relation, etype, eid) tuples into a space-joined string."""
    parts = []
    for tup in path_tuples:
        for x in tup:
            parts.append(str(x))
    return ' '.join(parts)


def load_train_labels(xrecsys_dir: str, dataset: str, labels_dir: str = None) -> dict:
    """
    Load labels used to filter already-seen items.

    Canonical datasets use train/validation/test splits, so validation items
    are also prior interactions at test time. Legacy xrecsys layouts without a
    validation label file retain train-only behavior.

    Returns:
        {uid: set(pids)}
    """
    if labels_dir:
        pkl = Path(labels_dir) / 'train_label.pkl'
    else:
        pkl = Path(xrecsys_dir) / 'models' / 'PGPR' / 'tmp' / dataset / 'train_label.pkl'
    with open(pkl, 'rb') as f:
        raw = pickle.load(f)
    excluded = {uid: set(pids) for uid, pids in raw.items()}
    if labels_dir:
        valid_pkl = Path(labels_dir) / 'valid_label.pkl'
        if valid_pkl.exists():
            with open(valid_pkl, 'rb') as f:
                valid = pickle.load(f)
            for uid, pids in valid.items():
                excluded.setdefault(uid, set()).update(pids)
    return excluded


def write_csvs(
    output_dir: Path,
    pred_rows: List[Tuple],
    uid_topk: dict,
    uid_pid_best: dict,
) -> None:
    """
    Write the three xrecsys CSV files.

    pred_rows   : [(uid, pid, norm_score, path_prob, path_str), ...]
    uid_topk    : {uid: [pid, pid, ...]}   (descending score order)
    uid_pid_best: {uid: {pid: path_str}}
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / 'pred_paths.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['uid', 'pid', 'path_score', 'path_prob', 'path'])
        w.writerows(pred_rows)

    with open(output_dir / 'uid_topk.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['uid', 'top10'])
        for uid, pids in uid_topk.items():
            w.writerow([uid, ' '.join(str(p) for p in pids)])

    with open(output_dir / 'uid_pid_explanation.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['uid', 'pid', 'path'])
        for uid, pid_paths in uid_pid_best.items():
            for pid, path_str in pid_paths.items():
                w.writerow([uid, pid, path_str])


# ---------------------------------------------------------------------------
# Stub kept for backward-compat imports (unused in new code)
# ---------------------------------------------------------------------------

class _DeprecatedBaseAdapter:
    """Legacy base class — not used by the new adapters."""
    def convert(self, model_output_path: str) -> None:
        """
        Complete conversion pipeline: load -> convert -> save.

        Args:
            model_output_path: Path to model's output directory or file
        """
        print(f"\n{'='*60}")
        print(f"Converting {self.model_name} output for {self.dataset_name}")
        print(f"{'='*60}")
        
        # Load raw output
        print(f"Loading model output from {model_output_path}...")
        raw_output = self.load_model_output(model_output_path)
        
        # Convert to standard format
        print("Converting to standard format...")
        pred_paths, uid_topk, uid_pid_explanation = self.convert_to_standard_format(raw_output)
        
        # Validate outputs
        self._validate_outputs(pred_paths, uid_topk, uid_pid_explanation)
        
        # Save
        self.save_standard_output(pred_paths, uid_topk, uid_pid_explanation)
        
        print(f"✓ Conversion complete!")
        print(f"  - pred_paths: {len(pred_paths)} rows")
        print(f"  - uid_topk: {len(uid_topk)} users")
        print(f"  - uid_pid_explanation: {len(uid_pid_explanation)} explanations")
    
    def _validate_outputs(self, pred_paths, uid_topk,
                         uid_pid_explanation) -> None:
        """Validate that outputs have correct schema"""
        # Check pred_paths
        required_cols = ['uid', 'pid', 'path_score', 'path_prob', 'path']
        if not all(col in pred_paths.columns for col in required_cols):
            raise ValueError(f"pred_paths missing required columns. Expected {required_cols}, got {pred_paths.columns.tolist()}")
        
        # Check uid_topk
        if not all(col in uid_topk.columns for col in ['uid', 'topk_pids']):
            raise ValueError(f"uid_topk missing required columns")
        
        # Check uid_pid_explanation
        if not all(col in uid_pid_explanation.columns for col in ['uid', 'pid', 'explanation']):
            raise ValueError(f"uid_pid_explanation missing required columns")
        
        print("✓ Output validation passed")


# Preserve the historical package import while new adapters use the functions
# above directly.
BaseAdapter = _DeprecatedBaseAdapter
