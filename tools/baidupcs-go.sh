#!/usr/bin/env bash
set -euo pipefail

BIN_PATH="${BAIDUPCS_GO_BIN:-$HOME/bin/BaiduPCS-Go}"

if [[ ! -x "$BIN_PATH" ]]; then
  echo "BaiduPCS-Go not found or not executable at: $BIN_PATH" >&2
  echo "Set BAIDUPCS_GO_BIN or place the binary at ~/bin/BaiduPCS-Go" >&2
  exit 1
fi

exec "$BIN_PATH" "$@"

