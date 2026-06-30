# Multi-Agent Guide

## Supervisor Agent

Responsibilities:
- Plan execution.
- Route to specialized agents.
- Retry transient failures.
- Persist traces.
- Enforce safety policy and approvals.

## Specialist Agents

- Email, Calendar, Report, Analytics, Database, SQL, Dashboard,
  Document, OCR, Workflow, Notification, Knowledge, Memory,
  Approval, Scheduler.

## Model Routing

- Workload-aware policy (`chat`, `embedding`, `ocr`, `sql`, `analytics`).
- Runtime model inventory from Ollama tags API.
- VRAM-pressure aware fallback behavior.
