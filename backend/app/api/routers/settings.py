from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user, require_roles
from app.models import Role, Setting, User

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingUpsert(BaseModel):
    scope: str
    key: str
    value: dict = Field(default_factory=dict)


@router.post("/")
async def upsert_setting(
    payload: SettingUpsert,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(require_roles(Role.ORG_ADMIN, Role.MANAGER)),
) -> dict:
    result = await session.execute(
        select(Setting).where(Setting.scope == payload.scope, Setting.key == payload.key)
    )
    item = result.scalar_one_or_none()
    if item:
        item.value = payload.value
    else:
        item = Setting(scope=payload.scope, key=payload.key, value=payload.value)
        session.add(item)
    await session.commit()
    await session.refresh(item)
    return {"id": item.id, "scope": item.scope, "key": item.key, "value": item.value}


@router.get("/")
async def list_settings(
    scope: str | None = None,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[dict]:
    query = select(Setting).order_by(Setting.id.desc())
    if scope:
        query = query.where(Setting.scope == scope)
    result = await session.execute(query)
    return [
        {"id": item.id, "scope": item.scope, "key": item.key, "value": item.value}
        for item in result.scalars().all()
    ]
