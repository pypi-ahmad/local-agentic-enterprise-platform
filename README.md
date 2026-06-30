# Local Agentic Enterprise Platform (LAEP)

Production-grade local AI business automation platform with multi-agent orchestration, workflow approvals, SQL safety, reporting exports, observability, and full web UI.

This README is based on a **real end-to-end run** executed on **June 30, 2026**.
No mock or dry-run data is documented here.

---

## 1) What This Platform Does

LAEP combines:

- FastAPI backend + Next.js frontend
- Local-model AI workflows via Ollama
- Business agents (email, calendar, analytics, SQL, workflow, notifications)
- Workflow orchestration with approval gates
- SQL generation + guarded execution
- Report generation (PDF / XLSX / PPTX)
- Dashboard + memory persistence
- Audit logs, system monitoring, model routing visibility

---

## 2) Real Verification Snapshot (June 30, 2026)

### Environment used in run

- OS: Linux
- Python (system): `3.14.4`
- Python (project venv): `3.12.10`
- `uv`: `0.11.19`
- Node: `v24.16.0`
- npm: `11.13.0`

### Compile + quality checks (real)

- `uv sync --group dev` -> success
- `npm ls --depth=0` -> all frontend deps resolved
- `./scripts/checks.sh` -> success
  - `ruff` passed
  - `mypy` passed
  - `pytest`: `10 passed, 2 skipped`
- `npm run build` -> success (all 20 app routes generated)

### Real E2E execution output directory

- `artifacts/e2e/20260630_153730`

### Real E2E summary

- Backend: `ok`
- Frontend: `ok`
- Admin auth user: `local-admin`
- Viewer auth user: `viewer_live_20260630_153730`
- Analytics average: `103.47368421052632`
- Report ID: `4`
- Dashboard ID: `4`
- Workflow run ID: `5`
- Workflow final state: `waiting_approval`
- Workflow timeline events: `2`
- Follow-up notification ID: `1`
- Installed Ollama models detected: `18`
- Audit log rows returned: `143`

### Real generated report artifacts

- `artifacts/reports/report_4_weekly.pdf` (`1463` bytes)
- `artifacts/reports/report_4_weekly.xlsx` (`4957` bytes)
- `artifacts/reports/report_4_weekly.pptx` (`28441` bytes)

### Real business chain executed

`summarize_data -> generate_report -> update_dashboard -> create_followup_action`

---

## 3) Architecture (Code-Level)

## Backend

- Entry point: `backend/app/main.py`
- API router registry: `backend/app/api/router.py`
- Routers: `backend/app/api/routers/*`
- Core services: `backend/app/services/*`
- Agents: `backend/app/agents/*`
- Data models: `backend/app/models/entities.py`
- Security/auth: `backend/app/core/security.py`, `backend/app/services/auth_service.py`

## Frontend

- Framework: Next.js App Router
- Root layout: `frontend/app/layout.tsx`
- Shell/nav: `frontend/components/AppShell.tsx`
- Feature pages: `frontend/app/*/page.tsx`
- API client: `frontend/lib/api.ts`

## Data / Runtime

- Primary recommended DB: PostgreSQL
- Local fallback supported: SQLite
- Local model inference: Ollama
- Optional infra targets (configured): Redis, MinIO

---

## 4) Zero-to-Hero Setup (Exact Steps)

## Step A: Bootstrap backend env

```bash
cd /home/ahmad/AI/local-agentic-enterprise-platform
export UV_CACHE_DIR=/tmp/uv-cache
uv sync --group dev
```

## Step B: Install frontend deps

```bash
cd /home/ahmad/AI/local-agentic-enterprise-platform/frontend
npm install
```

## Step C: Build + checks

```bash
cd /home/ahmad/AI/local-agentic-enterprise-platform
./scripts/checks.sh

cd frontend
npm run build
```

## Step D: Run backend (local verified mode)

For the verified run, backend used SQLite override for local reliability:

```bash
cd /home/ahmad/AI/local-agentic-enterprise-platform
source .venv/bin/activate
export PYTHONPATH=backend
export UV_CACHE_DIR=/tmp/uv-cache
export DATABASE_URL='sqlite+aiosqlite:///./laep.db'
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Step E: Run frontend

```bash
cd /home/ahmad/AI/local-agentic-enterprise-platform/frontend
npm run start -- --hostname 127.0.0.1 --port 3001
```

## Step F: Run full live E2E verifier (recommended)

```bash
cd /home/ahmad/AI/local-agentic-enterprise-platform
./scripts/verify_live_e2e.sh
```

This creates a timestamped evidence pack in `artifacts/e2e/<run_id>/` and writes a machine-readable summary to `verification_summary.json`.

---

## 5) Real E2E Flow Executed

The following live calls were executed successfully (2xx):

1. Health + readiness
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`

2. Authentication + role presence
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/users`
- `POST /api/v1/auth/login` (viewer)
- `GET /api/v1/auth/me` (viewer)

3. Agent workflows
- `GET /api/v1/agents/`
- `POST /api/v1/agents/execute` (approval-required path)

4. Email workflows
- `POST /api/v1/email/summarize`
- `POST /api/v1/email/draft-reply`

5. Calendar workflows
- `POST /api/v1/calendar/conflicts`
- `POST /api/v1/calendar/agenda`

6. Analytics pipeline
- `POST /api/v1/analytics/metrics` (multiple points)
- `GET /api/v1/analytics/metrics/revenue_weekly`

7. Report generation
- `POST /api/v1/reports/`
- `POST /api/v1/reports/{id}/export/pdf`
- `POST /api/v1/reports/{id}/export/xlsx`
- `POST /api/v1/reports/{id}/export/pptx`

8. Database + schema discovery
- `GET /api/v1/database/schemas`
- `GET /api/v1/database/tables/users?limit=10`
- `POST /api/v1/database/query?sql=...`

9. SQL safety + query path
- `POST /api/v1/sql/generate`
- `POST /api/v1/sql/execute` (safe read query)
- `POST /api/v1/sql/execute` (destructive -> approval required)

10. Dashboard + memory persistence
- `POST /api/v1/dashboards/`
- `GET /api/v1/dashboards/`
- `POST /api/v1/memory/`
- `GET /api/v1/memory/`

11. Workflow orchestration + approval gate
- `POST /api/v1/workflows/definitions`
- `POST /api/v1/workflows/runs`
- `GET /api/v1/workflows/runs` (verified `waiting_approval`)
- `GET /api/v1/approvals/pending`
- `POST /api/v1/approvals/{id}/decision`

12. Follow-up action + observability
- `POST /api/v1/notifications/`
- `GET /api/v1/notifications/`
- `POST /api/v1/scheduler/once`
- `GET /api/v1/scheduler/jobs`
- `GET /api/v1/system/models`
- `GET /api/v1/system/monitoring`
- `GET /api/v1/logs/audit`

13. Frontend navigation/usability

Validated live `200 OK` + expected page text + shell nav (`LAEP Console`) for:

- `/`
- `/assistant`
- `/email`
- `/calendar`
- `/reports`
- `/analytics`
- `/database`
- `/sql`
- `/workflows`
- `/documents`
- `/knowledge`
- `/memory`
- `/agents`
- `/logs`
- `/settings`
- `/models`
- `/monitoring`

HTML captures stored in:

- `artifacts/e2e/20260630_153730/web_*.html`

---

## 6) Runtime Hardening Included

During real run, one runtime failure was found and fixed:

- Problem: Ollama generate timeout caused `500 Internal Server Error` on `/email/summarize`.
- Fix applied: resilient fallback path in `backend/app/services/ollama_client.py`
  - capped inference timeout
  - graceful fallback response instead of unhandled crash
- Result: full E2E run completed successfully and produced artifacts.

---

## 7) Production Notes

For production deployment:

- Use PostgreSQL (`DATABASE_URL=postgresql+asyncpg://...`) instead of local SQLite.
- Keep `JWT_SECRET` and external credentials in real secret management.
- Configure CORS origins strictly (remove wildcard behavior).
- Use process manager/container orchestration for backend/frontend lifecycle.
- Add external monitoring/alerts for latency and approval backlog.

---

## 8) Key Paths

- Backend app: `backend/app/`
- Frontend app: `frontend/app/`
- Scripts: `scripts/`
- Reports output: `artifacts/reports/`
- E2E evidence: `artifacts/e2e/20260630_153730/`
