from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine
from app.dependencies import db_session, get_current_user
from app.models import User

router = APIRouter(prefix="/database", tags=["database"])


@router.get("/schemas")
async def list_tables(_: User = Depends(get_current_user)) -> dict:
    async with engine.begin() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
    return {"tables": tables}


@router.get("/tables/{table_name}")
async def table_preview(
    table_name: str,
    limit: int = 20,
    _: User = Depends(get_current_user),
) -> dict:
    if limit > 200:
        raise HTTPException(status_code=400, detail="Limit too high")
    async with engine.begin() as conn:
        valid_tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
    if table_name not in valid_tables:
        raise HTTPException(status_code=404, detail="Table not found")

    query = text(f'SELECT * FROM \"{table_name}\" LIMIT :limit')
    async with engine.begin() as conn:
        result = await conn.execute(query, {"limit": limit})
        rows = [dict(row) for row in result.mappings().all()]
    return {"rows": rows, "count": len(rows)}


@router.post("/query")
async def run_safe_query(
    sql: str,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> dict:
    statement = sql.strip().upper()
    if statement.startswith(("DELETE", "DROP", "TRUNCATE", "ALTER", "UPDATE", "INSERT")):
        raise HTTPException(status_code=400, detail="Use /sql/execute with approval workflow")
    async with engine.begin() as conn:
        result = await conn.execute(text(sql))
        rows = [dict(row) for row in result.mappings().all()] if result.returns_rows else []
    await session.commit()
    return {"rows": rows, "row_count": len(rows)}
