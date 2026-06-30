# Troubleshooting Guide

## API Fails to Start

- Verify `.env` values and DB connectivity.
- Check logs under `logs/app.log`.

## Login Fails

- Ensure break-glass password matches `.env`.
- Remove DB and restart to recreate bootstrap user in local dev.

## Ollama Errors

- Confirm `ollama serve` running.
- Check model exists in `ollama list`.

## Workflow Stuck on Approval

- Inspect `/api/v1/approvals/pending`.
- Post decision to `/api/v1/approvals/{id}/decision`.

## Frontend API Errors

- Validate `NEXT_PUBLIC_API_BASE`.
- Ensure token exists from `/auth/login`.
