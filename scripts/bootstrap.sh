#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"

uv venv --python 3.12.10
source .venv/bin/activate
uv sync --group dev
cp -n .env.example .env || true

echo "Bootstrap complete. Activate env: source .venv/bin/activate"
