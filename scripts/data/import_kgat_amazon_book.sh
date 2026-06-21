#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/usr1/home/s125mdg43_08/eval_framework}"
OUT_DIR="${2:-$ROOT/data_sources/kgat_amazon_book}"
REPO_URL="https://github.com/xiangwang1223/knowledge_graph_attention_network.git"
COMMIT="c03737be46ac26a0b5431efe149828e982ffbbfb"

if [[ -f "$OUT_DIR/import.complete" ]]; then
  echo "KGAT Amazon-book source already imported: $OUT_DIR"
  exit 0
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

git clone --no-checkout "$REPO_URL" "$TMP_DIR/repo"
git -C "$TMP_DIR/repo" checkout --detach "$COMMIT"

SOURCE="$TMP_DIR/repo/Data/amazon-book"
(
  cd "$SOURCE"
  sha256sum --check <<'EOF'
01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b  README.md
4d10106bb06a77e11df660429903c0067aeb85b86431807836b0d8b7edc30c38  train.txt
f47eff9d35fb95c07d74251a991478a84095ce6c5969b0dafcb4afe99fc716ec  test.txt
ae2e001d4e49fd82d4c7e25f950827a8be2fbd5c6f3a16dacb2d104edb32310e  user_list.txt
efea8518cd68e515584fdfbfca95f318b25ef551c64498c5935897c2b02e436f  item_list.txt
b03e9cb7eeab38756f0b10c06478a611201a7d42cb16acb8513624dda05270ca  entity_list.txt
50fe9c6560224b20d8ace78ae8ca0b8dad39248f6dc900f6744b633ba8c33f4b  relation_list.txt
ae1adad6c59ac2faf46066fb03b680a8a93db60588fcc63fdb0670df0f32161a  kg_final.txt.zip
EOF
)

mkdir -p "$OUT_DIR"
cp \
  "$SOURCE/README.md" \
  "$SOURCE/train.txt" \
  "$SOURCE/test.txt" \
  "$SOURCE/user_list.txt" \
  "$SOURCE/item_list.txt" \
  "$SOURCE/entity_list.txt" \
  "$SOURCE/relation_list.txt" \
  "$SOURCE/kg_final.txt.zip" \
  "$OUT_DIR/"

{
  printf 'source_repository=%s\n' "$REPO_URL"
  printf 'source_commit=%s\n' "$COMMIT"
  printf 'source_subdirectory=Data/amazon-book\n'
  printf 'imported_at=%s\n' "$(date --iso-8601=seconds)"
} > "$OUT_DIR/source_manifest.txt"

(
  cd "$OUT_DIR"
  sha256sum \
    README.md \
    train.txt \
    test.txt \
    user_list.txt \
    item_list.txt \
    entity_list.txt \
    relation_list.txt \
    kg_final.txt.zip \
    > SHA256SUMS
)

date --iso-8601=seconds > "$OUT_DIR/import.complete"
echo "Imported KGAT Amazon-book source to $OUT_DIR"
