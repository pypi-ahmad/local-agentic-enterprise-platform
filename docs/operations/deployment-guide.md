# Deployment Guide

## Single-Node Self-Hosted

Recommended target for v1.

### Steps

1. Configure `.env`.
2. Start dependencies (Postgres/Redis/MinIO).
3. Start API service.
4. Start frontend service.
5. Verify health and auth path.

### Health Validation

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- dashboard login + model manager view

### Production Hardening

- Reverse proxy with TLS.
- Network segmentation.
- Secret manager integration.
- Continuous backup policy.
