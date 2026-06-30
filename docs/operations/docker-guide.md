# Docker Guide

## Start Stack

```bash
docker compose up --build
```

Services:
- `api` on `8000`
- `frontend` on `3000`
- `postgres` on `5432`
- `redis` on `6379`
- `minio` on `9000` and console `9001`

## GPU Notes

Ollama runs on host. API calls Ollama through `host.docker.internal:11434`.
