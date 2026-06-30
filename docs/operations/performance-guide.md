# Performance Guide

## Optimization Priorities

- Keep Ollama model set lean; unload unused large models.
- Use async API calls for I/O-heavy workflows.
- Cache frequent reads in Redis.
- Keep document chunks bounded to reduce embedding cost.

## Suggested Targets

- P95 API latency < 1.5s for metadata endpoints.
- P95 agent orchestration < 5s for short prompts.
- Workflow recovery < 30s after worker restart.

## Profiling

- Use Prometheus metrics endpoints.
- Trace long workflows via execution timeline in DB.
