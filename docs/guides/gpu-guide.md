# GPU Guide

## Detection

- Runtime uses `nvidia-smi` parsing for GPU status.
- Exposed via `/api/v1/system/monitoring`.

## Fallback

- If GPU unavailable or VRAM pressure too high, router falls back to lower footprint models or CPU execution.

## Validation

- Confirm `nvidia-smi` shows `ollama/llama-server` process.
- Compare latency under GPU vs CPU mode.
