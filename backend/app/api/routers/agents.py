from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.business_agents import agent_names
from app.dependencies import db_session, get_current_user
from app.models import AgentExecution, User
from app.schemas.agent import AgentExecutionTrace, AgentTaskRequest, AgentTaskResult
from app.services.approval_service import ApprovalService
from app.services.supervisor import SupervisorService

router = APIRouter(prefix="/agents", tags=["agents"])
supervisor = SupervisorService()
approvals = ApprovalService()


@router.get("/")
async def list_agents() -> dict:
    return {"agents": agent_names()}


@router.post("/execute", response_model=AgentTaskResult)
async def execute_agent(
    payload: AgentTaskRequest,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> AgentTaskResult:
    if payload.require_approval:
        approval = await approvals.create(
            session=session,
            requester_id=user.id,
            operation_type=f"agent:{payload.agent_name}:{payload.task}",
            payload=payload.payload,
        )
        return AgentTaskResult(
            status="waiting_approval",
            agent_name=payload.agent_name,
            model_used="",
            output={"approval_id": approval.id},
            warnings=["Execution paused pending human approval."],
        )

    result = await supervisor.execute_agent_task(
        session=session,
        agent_name=payload.agent_name,
        task=payload.task,
        payload=payload.payload,
        context=payload.context,
        retries=2,
    )
    return AgentTaskResult(
        status=result.status,
        agent_name=payload.agent_name,
        model_used=result.model_used,
        output=result.output,
        warnings=result.warnings,
    )


@router.get("/executions", response_model=list[AgentExecutionTrace])
async def list_executions(
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[AgentExecutionTrace]:
    result = await session.execute(select(AgentExecution).order_by(AgentExecution.id.desc()).limit(200))
    return [AgentExecutionTrace.model_validate(item) for item in result.scalars().all()]
