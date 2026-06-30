from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import User
from app.schemas.memory import MemoryUpsert, MemoryView
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])
service = MemoryService()


@router.post("/", response_model=MemoryView)
async def upsert_memory(
    payload: MemoryUpsert,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> MemoryView:
    record = await service.upsert(
        session=session,
        user_id=user.id,
        scope=payload.scope,
        key=payload.key,
        value=payload.value,
    )
    return MemoryView.model_validate(record)


@router.get("/", response_model=list[MemoryView])
async def list_memory(
    scope: str | None = None,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> list[MemoryView]:
    records = await service.list(session=session, user_id=user.id, scope=scope)
    return [MemoryView.model_validate(item) for item in records]


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> dict:
    await service.delete(session=session, user_id=user.id, memory_id=memory_id)
    return {"deleted": memory_id}
