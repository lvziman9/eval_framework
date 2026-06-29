#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(git rev-parse --show-toplevel)}"
PY="${PY:-/usr1/home/s125mdg43_08/miniconda3/envs/eval_frame/bin/python}"
STATUS_ONLY=0

usage() {
  cat <<'EOF'
usage: regenerate_canonical_native_path_reports.sh [--status-only]

Regenerate report-only canonical native-path artifacts from existing completed
experiment outputs. This script does not launch training or path extraction.

Options:
  --status-only  Regenerate only status CSV/Markdown, skipping figure rebuilds.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --status-only)
      STATUS_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$STATUS_ONLY" -eq 0 ]]; then
  /bin/bash "$ROOT/scripts/analysis/generate_native_path_figures.sh" lastfm
  /bin/bash "$ROOT/scripts/analysis/generate_native_path_figures.sh" ml1m
fi

"$PY" "$ROOT/scripts/analysis/validate_canonical_export_evidence.py" --manifest-only
"$PY" "$ROOT/scripts/analysis/audit_amazon_classic_port_readiness.py" > /dev/null
"$PY" "$ROOT/scripts/analysis/generate_canonical_status_matrix.py"
"$PY" "$ROOT/scripts/analysis/generate_canonical_artifact_manifest.py"

"$PY" - "$ROOT" <<'PY'
import csv
import sys
from pathlib import Path

root = Path(sys.argv[1])

status_csv = root / "reports" / "tables" / "canonical_native_path_status_matrix.csv"
status_md = root / "reports" / "tables" / "canonical_native_path_status_matrix.md"
rows = list(csv.DictReader(status_csv.open()))
assert len(rows) == 18, f"expected 18 status rows, found {len(rows)}"
complete_rows = [row for row in rows if row["stage"].startswith("Complete")]
assert len(complete_rows) == 14, f"expected 14 complete rows, found {len(complete_rows)}"
for row in complete_rows:
    assert row["export_validation"] == "PASS", row
    assert row["export_evidence"].endswith(".json"), row

for dataset, directory in {
    "LastFM": root / "reports" / "figures" / "tradeoff" / "canonical_lastfm_native_paths_v4_six_model",
    "ML-1M": root / "reports" / "figures" / "tradeoff" / "canonical_ml1m_native_paths_v2",
}.items():
    png = len(list(directory.glob("*.png")))
    csv_count = len(list(directory.glob("*.csv")))
    assert png == 12 and csv_count == 12, (
        f"{dataset} figure bundle incomplete: {png} PNG + {csv_count} CSV"
    )

markdown = status_md.read_text()
assert "Amazon classic-port acceptance criteria" in markdown
assert "Amazon-Book KGAT | PEARLM | Complete" in markdown

readiness_path = root / "reports" / "tables" / "amazon_classic_port_readiness.json"
assert readiness_path.exists(), readiness_path
readiness_md_path = root / "reports" / "tables" / "amazon_classic_port_readiness.md"
assert readiness_md_path.exists(), readiness_md_path
print("amazon classic readiness audit present")

artifact_manifest = root / "reports" / "tables" / "canonical_native_path_artifact_manifest.json"
assert artifact_manifest.exists(), artifact_manifest
print("artifact manifest present")
print("canonical native-path report validation PASS")
PY

echo "Canonical native-path reports regenerated."
