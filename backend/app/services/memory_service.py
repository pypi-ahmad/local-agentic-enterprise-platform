from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MemoryRecord


class MemoryService:
    """Manages short-term and long-term memory records."""

    async def upsert(
        self,
        session: AsyncSession,
        user_id: int,
        scope: str,
        key: str,
        value: dict,
    ) -> MemoryRecord:
        result = await session.execute(
            select(MemoryRecord).where(
                MemoryRecord.user_id == user_id,
                MemoryRecord.scope == scope,
                MemoryRecord.key == key,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            record.value = value
        else:
            record = MemoryRecord(user_id=user_id, scope=scope, key=key, value=value)
            session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    async def list(self, session: AsyncSession, user_id: int, scope: str | None = None) -> list[MemoryRecord]:
        query = select(MemoryRecord).where(MemoryRecord.user_id == user_id)
        if scope:
            query = query.where(MemoryRecord.scope == scope)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def delete(self, session: AsyncSession, user_id: int, memory_id: int) -> None:
        await session.execute(
            delete(MemoryRecord).where(MemoryRecord.id == memory_id, MemoryRecord.user_id == user_id)
        )
        await session.commit()
