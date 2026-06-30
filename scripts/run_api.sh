#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate
export PYTHONPATH=backend
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
