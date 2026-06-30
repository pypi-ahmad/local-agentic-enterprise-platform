from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApprovalRequest, ApprovalStatus


class ApprovalService:
    """Manages approval requests for sensitive actions."""

    async def create(
        self,
        session: AsyncSession,
        requester_id: int,
        operation_type: str,
        payload: dict,
        approver_id: int | None = None,
    ) -> ApprovalRequest:
        request = ApprovalRequest(
            requester_id=requester_id,
            approver_id=approver_id,
            operation_type=operation_type,
            payload=payload,
            status=ApprovalStatus.PENDING,
        )
        session.add(request)
        await session.commit()
        await session.refresh(request)
        return request

    async def decide(
        self,
        session: AsyncSession,
        approval_id: int,
        approve: bool,
        reason: str,
    ) -> ApprovalRequest:
        result = await session.execute(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))
        approval = result.scalar_one()
        approval.status = ApprovalStatus.APPROVED if approve else ApprovalStatus.REJECTED
        approval.decision_reason = reason
        await session.commit()
        await session.refresh(approval)
        return approval

    async def list_pending(self, session: AsyncSession) -> list[ApprovalRequest]:
        result = await session.execute(
            select(ApprovalRequest).where(ApprovalRequest.status == ApprovalStatus.PENDING)
        )
        return list(result.scalars().all())
