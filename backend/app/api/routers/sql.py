from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine
from app.dependencies import db_session, get_current_user
from app.models import User
from app.schemas.sql import (
    SQLExecutionRequest,
    SQLExecutionResponse,
    SQLGenerationRequest,
    SQLGenerationResponse,
)
from app.services.approval_service import ApprovalService
from app.services.sql_service import SQLGenerationError, SQLService

router = APIRouter(prefix="/sql", tags=["sql"])
service = SQLService()
approvals = ApprovalService()


@router.post("/generate", response_model=SQLGenerationResponse)
async def generate_sql(
    payload: SQLGenerationRequest,
    _: User = Depends(get_current_user),
) -> SQLGenerationResponse:
    try:
        sql, decision = await service.generate(
            prompt=payload.prompt,
            dialect=payload.dialect,
            schema_hint=payload.schema_hint,
        )
    except SQLGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"code": "sql_generation_failed", "message": str(exc)},
        ) from exc

    return SQLGenerationResponse(
        sql=sql,
        explanation=decision.explanation,
        operation=decision.operation,
        destructive=decision.destructive,
    )


@router.post("/execute", response_model=SQLExecutionResponse)
async def execute_sql(
    payload: SQLExecutionRequest,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> SQLExecutionResponse:
    decision = service.safety.inspect(payload.sql)
    if decision.destructive and not payload.confirm:
        approval = await approvals.create(
            session=session,
            requester_id=user.id,
            operation_type="destructive_sql",
            payload={"sql": payload.sql},
        )
        return SQLExecutionResponse(
            rows=[{"approval_required": approval.id}],
            row_count=0,
            execution_ms=0,
            safe=False,
        )

    rows, row_count, execution_ms, decision = await service.execute(
        session=session,
        engine=engine,
        sql=payload.sql,
        confirm=payload.confirm,
        dry_run=payload.dry_run,
    )
    return SQLExecutionResponse(
        rows=rows,
        row_count=row_count,
        execution_ms=execution_ms,
        safe=not decision.destructive,
    )
