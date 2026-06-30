from pathlib import Path

import pytest
from app.models import (
    ApprovalRequest,
    ApprovalStatus,
    Role,
    User,
    WorkflowDefinition,
    WorkflowRun,
    WorkflowRunStatus,
)
from app.models.base import Base
from app.services.workflow_runtime import WorkflowRuntimeService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest.mark.asyncio
async def test_workflow_pauses_on_approval_and_persists_timeline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "workflow_runtime.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_local() as session:
        user = User(
            email="runtime-user@example.com",
            username="runtime-user",
            full_name="Runtime User",
            hashed_password="hash",
            role=Role.ORG_ADMIN,
            is_active=True,
        )
        definition = WorkflowDefinition(
            name="workflow-runtime-approval-test",
            description="approval gate test",
            graph={
                "nodes": [
                    {"id": "n1", "type": "condition", "config": {"expression": "True"}},
                    {
                        "id": "n2",
                        "type": "approval",
                        "config": {"operation_type": "sensitive_followup", "payload": {"action": "approve"}},
                    },
                    {"id": "n3", "type": "notification", "config": {"message": "should not execute"}},
                ],
                "edges": [
                    {"source": "n1", "target": "n2", "condition": 'context["n1"]["decision"] == True'},
                    {"source": "n2", "target": "n3", "condition": None},
                ],
            },
            is_template=False,
        )
        session.add_all([user, definition])
        await session.commit()
        await session.refresh(user)
        await session.refresh(definition)

        run = WorkflowRun(
            workflow_definition_id=definition.id,
            initiated_by=user.id,
            status=WorkflowRunStatus.PENDING,
            context={},
            execution_timeline={"events": []},
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        run_id = run.id

    import app.core.database as database_module

    monkeypatch.setattr(database_module, "SessionLocal", session_local)

    runtime = WorkflowRuntimeService()
    await runtime._execute_run(run_id=run_id)

    async with session_local() as session:
        saved_run = await session.get(WorkflowRun, run_id)
        assert saved_run is not None
        assert saved_run.status == WorkflowRunStatus.WAITING_APPROVAL
        assert "n1" in saved_run.context
        assert "n2" in saved_run.context
        assert "n3" not in saved_run.context

        events = saved_run.execution_timeline.get("events", [])
        assert len(events) == 2
        assert [event["node_id"] for event in events] == ["n1", "n2"]

        pending = await session.execute(
            select(ApprovalRequest).where(ApprovalRequest.operation_type == "sensitive_followup")
        )
        approvals = list(pending.scalars().all())
        assert len(approvals) == 1
        assert approvals[0].status == ApprovalStatus.PENDING

    await engine.dispose()

