#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate
export PYTHONPATH=backend
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"
uv run ruff check backend
uv run mypy backend/app
uv run pytest backend/tests -q
