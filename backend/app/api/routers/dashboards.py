from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import Dashboard, User

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


class DashboardCreate(BaseModel):
    name: str
    definition: dict = Field(default_factory=dict)


@router.post("/")
async def create_dashboard(
    payload: DashboardCreate,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> dict:
    dashboard = Dashboard(name=payload.name, definition=payload.definition, owner_id=user.id)
    session.add(dashboard)
    await session.commit()
    await session.refresh(dashboard)
    return {"id": dashboard.id, "name": dashboard.name}


@router.get("/")
async def list_dashboards(
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[dict]:
    result = await session.execute(select(Dashboard).order_by(Dashboard.id.desc()))
    return [{"id": item.id, "name": item.name, "definition": item.definition} for item in result.scalars().all()]
