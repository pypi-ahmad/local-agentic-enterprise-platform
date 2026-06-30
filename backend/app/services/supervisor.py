from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentResult
from app.agents.business_agents import ALL_AGENT_TYPES
from app.models import AgentExecution
from app.services.model_router import ModelRouter
from app.services.ollama_client import OllamaClient


class SupervisorService:
    """Coordinates agent routing, execution, retries, and trace persistence."""

    def __init__(self) -> None:
        self.model_router = ModelRouter()
        self.ollama = OllamaClient()

    async def execute_agent_task(
        self,
        session: AsyncSession,
        agent_name: str,
        task: str,
        payload: dict[str, Any],
        context: dict[str, Any],
        workflow_run_id: int | None = None,
        retries: int = 1,
    ) -> AgentResult:
        if agent_name not in ALL_AGENT_TYPES:
            msg = f"Unknown agent: {agent_name}"
            raise ValueError(msg)

        agent = ALL_AGENT_TYPES[agent_name](self.model_router, self.ollama)
        last_error: Exception | None = None
        for _ in range(retries + 1):
            try:
                result = await agent.run(task=task, payload=payload, context=context)
                await self._write_execution(
                    session=session,
                    workflow_run_id=workflow_run_id,
                    agent_name=agent_name,
                    payload=payload,
                    result=result,
                )
                return result
            except Exception as exc:  # noqa: PERF203
                last_error = exc

        msg = str(last_error) if last_error else "Unknown agent execution error"
        raise RuntimeError(msg)

    async def _write_execution(
        self,
        session: AsyncSession,
        workflow_run_id: int | None,
        agent_name: str,
        payload: dict[str, Any],
        result: AgentResult,
    ) -> None:
        execution = AgentExecution(
            workflow_run_id=workflow_run_id,
            agent_name=agent_name,
            input_payload=payload,
            output_payload=result.output,
            status=result.status,
            duration_ms=result.duration_ms,
            error="",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(execution)
        await session.commit()
