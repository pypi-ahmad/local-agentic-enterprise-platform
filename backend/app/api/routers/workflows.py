from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import User, WorkflowDefinition, WorkflowRun
from app.schemas.workflow import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionView,
    WorkflowRunCreate,
    WorkflowRunView,
)
from app.services.workflow_runtime import WorkflowRuntimeService

router = APIRouter(prefix="/workflows", tags=["workflows"])
runtime = WorkflowRuntimeService()


@router.post("/definitions", response_model=WorkflowDefinitionView)
async def create_definition(
    payload: WorkflowDefinitionCreate,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> WorkflowDefinitionView:
    definition = WorkflowDefinition(
        name=payload.name,
        description=payload.description,
        graph={
            "nodes": [node.model_dump() for node in payload.nodes],
            "edges": [edge.model_dump() for edge in payload.edges],
        },
        is_template=payload.is_template,
    )
    session.add(definition)
    await session.commit()
    await session.refresh(definition)
    return WorkflowDefinitionView.model_validate(definition)


@router.get("/definitions", response_model=list[WorkflowDefinitionView])
async def list_definitions(
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[WorkflowDefinitionView]:
    result = await session.execute(select(WorkflowDefinition).order_by(WorkflowDefinition.id.desc()))
    return [WorkflowDefinitionView.model_validate(item) for item in result.scalars().all()]


@router.post("/runs", response_model=WorkflowRunView)
async def start_run(
    payload: WorkflowRunCreate,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> WorkflowRunView:
    definition = await session.get(WorkflowDefinition, payload.workflow_definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="Workflow definition not found")
    run = await runtime.start_run(
        session=session,
        workflow_definition_id=payload.workflow_definition_id,
        user_id=user.id,
        context=payload.context,
    )
    return WorkflowRunView.model_validate(run)


@router.get("/runs", response_model=list[WorkflowRunView])
async def list_runs(
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[WorkflowRunView]:
    result = await session.execute(select(WorkflowRun).order_by(WorkflowRun.id.desc()).limit(200))
    return [WorkflowRunView.model_validate(item) for item in result.scalars().all()]
