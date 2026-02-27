#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-$(cat "$ROOT_DIR/VERSION")}" 
OUT_DIR="$ROOT_DIR/dist"
PKG_NAME="ego_trading-${VERSION}"
STAGE_DIR="$OUT_DIR/$PKG_NAME"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"
mkdir -p "$OUT_DIR"

cp -r "$ROOT_DIR/egotrading" "$STAGE_DIR/egotrading"
cp "$ROOT_DIR/README.md" "$STAGE_DIR/README.md"
cp "$ROOT_DIR/VERSION" "$STAGE_DIR/VERSION"

(
  cd "$OUT_DIR"
  tar -czf "${PKG_NAME}.tar.gz" "$PKG_NAME"
)

echo "Created: $OUT_DIR/${PKG_NAME}.tar.gz"
