from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import AuditLog, Role, User

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/audit")
async def audit_logs(
    limit: int = 200,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> list[dict]:
    if user.role not in {Role.ORG_ADMIN, Role.MANAGER}:
        return []
    limit = min(limit, 1000)
    result = await session.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit))
    return [
        {
            "id": row.id,
            "user_id": row.user_id,
            "action": row.action,
            "resource_type": row.resource_type,
            "resource_id": row.resource_id,
            "details": row.details,
            "created_at": row.created_at,
        }
        for row in result.scalars().all()
    ]
