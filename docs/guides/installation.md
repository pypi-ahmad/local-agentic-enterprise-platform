# Installation Guide

## Prerequisites

- Linux host with Docker, Node 24+, and `uv`.
- Ollama installed and running (`ollama serve`).
- NVIDIA GPU optional but recommended.

## Step-by-Step

1. Clone repository into `/home/ahmad/AI/local-agentic-enterprise-platform`.
2. Run bootstrap:

```bash
./scripts/bootstrap.sh
```

3. Configure environment:

```bash
cp .env.example .env
```

4. Edit `.env` secrets:
- `JWT_SECRET`
- `BREAK_GLASS_PASSWORD`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (if Google integration enabled)

5. Start backend and frontend:

```bash
./scripts/run_api.sh
./scripts/run_frontend.sh
```

6. Log in from Dashboard using break-glass credentials.

## Why This Setup

- `uv` ensures deterministic Python environments.
- Break-glass user guarantees recovery path if OAuth unavailable.
- Local Ollama keeps data on-prem and avoids external API costs.
