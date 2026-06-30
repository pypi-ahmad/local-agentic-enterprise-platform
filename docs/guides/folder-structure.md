# Folder Structure

```text
local-agentic-enterprise-platform/
  backend/
    app/
      api/routers/
      agents/
      core/
      models/
      schemas/
      services/
    alembic/
    tests/
  frontend/
    app/
    components/
    lib/
  docs/
    architecture/
    guides/
    api/
    database/
    operations/
  scripts/
  deployments/
```

## Structure Rationale

- `backend/app` isolates business logic from deployment wrappers.
- `services` owns orchestration, analytics, SQL safety, export, RAG.
- `routers` keeps HTTP adapters thin.
- `frontend/app` maps exactly to business pages.
