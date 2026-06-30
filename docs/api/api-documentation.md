# API Documentation

OpenAPI available at `/docs` and `/openapi.json`.

## Endpoint Groups

- `/api/v1/auth`: login, user, OAuth handshake.
- `/api/v1/agents`: list agents, execute tasks, execution traces.
- `/api/v1/workflows`: create definitions, run workflows, inspect runs.
- `/api/v1/approvals`: create and decide approval requests.
- `/api/v1/email`, `/api/v1/calendar`: operational automation APIs.
- `/api/v1/reports`: create and export reports.
- `/api/v1/analytics`: metrics ingestion + trend/anomaly summary.
- `/api/v1/dashboards`: dashboard definition CRUD.
- `/api/v1/sql`: generate/execute SQL with safety gates.
- `/api/v1/database`: schema/table exploration.
- `/api/v1/documents`, `/api/v1/knowledge`: ingestion and retrieval.
- `/api/v1/memory`: upsert/list/delete memory.
- `/api/v1/notifications`: in-app notifications.
- `/api/v1/scheduler`: one-time and cron jobs.
- `/api/v1/logs`: audit logs.
- `/api/v1/settings`: org runtime settings.
- `/api/v1/system`: models, monitoring.
- `/api/v1/health`: liveness/readiness.

## Auth

- Bearer JWT required for protected endpoints.
- Login via `/api/v1/auth/login`.

## Sensitive Operations

- Destructive SQL: approval request created unless `confirm=true`.
- Email sending blocked by policy; drafting only.
