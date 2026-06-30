# Ollama Guide

## Required Runtime

- `ollama serve` must be running.
- API default URL: `http://localhost:11434`.

## Model Routing Behavior

- Chat: `qwen3.5:4b` preferred.
- Embedding: `qwen3-embedding:4b` preferred.
- OCR: `glm-ocr:latest` preferred.
- Fallback chain selected from installed local inventory.

## Verify Model Inventory

```bash
ollama list
curl http://localhost:11434/api/tags
```
