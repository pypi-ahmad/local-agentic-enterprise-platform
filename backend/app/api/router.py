from fastapi import APIRouter

from app.api.routers import (
    agents,
    analytics,
    approvals,
    auth,
    calendar,
    dashboards,
    database,
    documents,
    email,
    health,
    knowledge,
    logs,
    memory,
    notifications,
    reports,
    scheduler,
    settings,
    sql,
    system,
    workflows,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(email.router)
api_router.include_router(calendar.router)
api_router.include_router(agents.router)
api_router.include_router(workflows.router)
api_router.include_router(approvals.router)
api_router.include_router(reports.router)
api_router.include_router(analytics.router)
api_router.include_router(dashboards.router)
api_router.include_router(sql.router)
api_router.include_router(database.router)
api_router.include_router(documents.router)
api_router.include_router(knowledge.router)
api_router.include_router(memory.router)
api_router.include_router(notifications.router)
api_router.include_router(scheduler.router)
api_router.include_router(logs.router)
api_router.include_router(settings.router)
api_router.include_router(system.router)
