# Database Documentation

## Primary Data Store

- Postgres (recommended production), SQLite fallback for local tests.
- `pgvector` expected for production vector similarity (hybrid search includes keyword scoring).

## Core Tables

- `users`, `organizations`
- `workflow_definitions`, `workflow_runs`
- `agent_executions`, `approval_requests`
- `reports`, `dashboards`, `analytics_records`
- `documents`, `knowledge_chunks`
- `memory_records`, `settings`, `audit_logs`, `secret_store`

## Migration Strategy

- Alembic under `backend/alembic`.
- Migration scripts versioned in `backend/alembic/versions`.

## Backup Guidance

- Nightly full DB dump + hourly WAL archiving (production recommendation).
- Validate restore weekly in isolated environment.
