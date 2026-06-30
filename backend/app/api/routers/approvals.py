from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import User
from app.schemas.approval import ApprovalCreate, ApprovalDecisionRequest, ApprovalView
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])
service = ApprovalService()


@router.post("/", response_model=ApprovalView)
async def create_approval(
    payload: ApprovalCreate,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> ApprovalView:
    approval = await service.create(
        session=session,
        requester_id=user.id,
        operation_type=payload.operation_type,
        payload=payload.payload,
        approver_id=payload.approver_id,
    )
    return ApprovalView.model_validate(approval)


@router.post("/{approval_id}/decision", response_model=ApprovalView)
async def decide_approval(
    approval_id: int,
    payload: ApprovalDecisionRequest,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> ApprovalView:
    approval = await service.decide(session, approval_id, payload.approve, payload.reason)
    return ApprovalView.model_validate(approval)


@router.get("/pending", response_model=list[ApprovalView])
async def pending_approvals(
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[ApprovalView]:
    pending = await service.list_pending(session)
    return [ApprovalView.model_validate(item) for item in pending]
