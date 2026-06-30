import asyncio
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WorkflowDefinition, WorkflowRun, WorkflowRunStatus
from app.services.approval_service import ApprovalService
from app.services.supervisor import SupervisorService


class WorkflowRuntimeService:
    """Executes workflow graphs with sequential/parallel/conditional behavior."""

    def __init__(self, supervisor: SupervisorService | None = None) -> None:
        self.supervisor = supervisor or SupervisorService()
        self.approval_service = ApprovalService()

    async def start_run(self, session: AsyncSession, workflow_definition_id: int, user_id: int, context: dict) -> WorkflowRun:
        run = WorkflowRun(
            workflow_definition_id=workflow_definition_id,
            initiated_by=user_id,
            status=WorkflowRunStatus.PENDING,
            context=context,
            execution_timeline={"events": []},
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        asyncio.create_task(self._execute_run(run_id=run.id))
        return run

    async def _execute_run(self, run_id: int) -> None:
        from app.core.database import SessionLocal

        async with SessionLocal() as session:
            result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
            run = result.scalar_one()
            definition_result = await session.execute(
                select(WorkflowDefinition).where(WorkflowDefinition.id == run.workflow_definition_id)
            )
            definition = definition_result.scalar_one()

            run.status = WorkflowRunStatus.RUNNING
            timeline: list[dict[str, Any]] = run.execution_timeline.get("events", [])
            await session.commit()

            graph = definition.graph
            nodes = {node["id"]: node for node in graph.get("nodes", [])}
            edges = graph.get("edges", [])
            indegree: dict[str, int] = {node_id: 0 for node_id in nodes}
            for edge in edges:
                indegree[edge["target"]] += 1

            frontier = [node_id for node_id, count in indegree.items() if count == 0]
            pause_requested = False

            try:
                while frontier and not pause_requested:
                    batch = list(frontier)
                    frontier.clear()
                    tasks = [self._execute_node(session, run, nodes[node_id], run.context) for node_id in batch]
                    node_results = await asyncio.gather(*tasks)

                    for node_id, output in zip(batch, node_results, strict=True):
                        event = {
                            "timestamp": datetime.now(UTC).isoformat(),
                            "node_id": node_id,
                            "output": output,
                        }
                        timeline = [*timeline, event]
                        run.execution_timeline = {"events": timeline}
                        run.context = {**run.context, node_id: output}

                        if nodes[node_id].get("type") == "approval":
                            run.status = WorkflowRunStatus.WAITING_APPROVAL
                            pause_requested = True
                            continue

                        for edge in [e for e in edges if e["source"] == node_id]:
                            if self._edge_allowed(edge, run.context):
                                indegree[edge["target"]] -= 1
                                if indegree[edge["target"]] == 0:
                                    frontier.append(edge["target"])

                    await session.commit()

                if not pause_requested:
                    run.status = WorkflowRunStatus.SUCCESS
            except Exception as exc:  # noqa: BLE001
                run.status = WorkflowRunStatus.FAILED
                timeline = [
                    *timeline,
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "error": str(exc),
                    },
                ]

            run.execution_timeline = {"events": timeline}
            await session.commit()

    async def _execute_node(
        self,
        session: AsyncSession,
        run: WorkflowRun,
        node: dict,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        node_type = node["type"]
        config = node.get("config", {})

        if node_type == "agent":
            result = await self.supervisor.execute_agent_task(
                session=session,
                agent_name=config["agent_name"],
                task=config.get("task", "run"),
                payload=config.get("payload", {}),
                context=context,
                workflow_run_id=run.id,
                retries=config.get("retries", 1),
            )
            return result.output

        if node_type == "condition":
            expression = config.get("expression", "True")
            allowed_globals: dict[str, object] = {"__builtins__": {}}
            allowed_locals: dict[str, object] = {"context": context}
            decision = bool(eval(expression, allowed_globals, allowed_locals))  # noqa: S307
            return {"decision": decision, "expression": expression}

        if node_type == "approval":
            approval = await self.approval_service.create(
                session=session,
                requester_id=run.initiated_by,
                operation_type=config.get("operation_type", "workflow_action"),
                payload=config.get("payload", {}),
                approver_id=config.get("approver_id"),
            )
            return {"approval_id": approval.id, "status": approval.status.value}

        if node_type == "notification":
            return {
                "channel": config.get("channel", "in_app"),
                "message": config.get("message", "Workflow notification"),
            }

        return {"status": "terminal"}

    @staticmethod
    def _edge_allowed(edge: dict[str, Any], context: dict[str, Any]) -> bool:
        condition = edge.get("condition")
        if not condition:
            return True
        allowed_globals: dict[str, object] = {"__builtins__": {}}
        allowed_locals: dict[str, object] = {"context": context}
        return bool(eval(condition, allowed_globals, allowed_locals))  # noqa: S307
