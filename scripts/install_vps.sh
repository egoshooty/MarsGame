#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-egoshooty/ego_trading}"
REF="${REF:-main}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/ego_trading}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --ref) REF="$2"; shift 2 ;;
    --dir) INSTALL_DIR="$2"; shift 2 ;;
    --python) PYTHON_BIN="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

ARCHIVE_URL="https://codeload.github.com/${REPO}/tar.gz/refs/heads/${REF}"
TMP_DIR="$(mktemp -d)"
ARCHIVE_PATH="$TMP_DIR/source.tar.gz"

trap 'rm -rf "$TMP_DIR"' EXIT

echo "Downloading ${ARCHIVE_URL}"
curl -fsSL "$ARCHIVE_URL" -o "$ARCHIVE_PATH"

mkdir -p "$INSTALL_DIR"
tar -xzf "$ARCHIVE_PATH" -C "$TMP_DIR"
EXTRACTED_DIR="$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"

rm -rf "$INSTALL_DIR"
mv "$EXTRACTED_DIR" "$INSTALL_DIR"

cd "$INSTALL_DIR"
$PYTHON_BIN -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r egotrading/requirements.txt

echo
echo "Installed to: $INSTALL_DIR"
echo "Next step:"
echo "source $INSTALL_DIR/.venv/bin/activate && python -m egotrading.main --init-config --config egotrading/config.json"
