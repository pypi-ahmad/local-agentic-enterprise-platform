# Architecture Guide

## Design Goals

- Enterprise-grade reliability on a local single-node deployment.
- Modular services with clean boundaries.
- Strong governance for sensitive operations.
- GPU-optimized local LLM inference with graceful fallback.

## Backend Layers

- API Layer: FastAPI routers per domain.
- Service Layer: orchestration, model routing, analytics, RAG, reporting.
- Domain Layer: SQLAlchemy entities + Pydantic contracts.
- Infrastructure Layer: Postgres, Redis, MinIO, Ollama, Prometheus.

## Frontend Layers

- App shell with global navigation and dark mode.
- Feature pages per business domain.
- API client wrapper + auth token context.
- Notification center and keyboard navigation.

## Multi-Agent Runtime

- Supervisor dispatches tasks to specialist agents.
- Workflow runtime supports sequential, parallel, conditional branches.
- Approval node pauses execution until decision is recorded.
- Execution traces persisted for observability and audit.

## Why LangGraph-Style Runtime

- Deterministic graph execution.
- Better control of retries and error recovery than free-form chat loops.
- Clear path for long-running workflows and resumability.
