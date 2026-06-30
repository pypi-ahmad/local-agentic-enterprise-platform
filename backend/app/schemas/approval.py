from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApprovalCreate(BaseModel):
    operation_type: str
    payload: dict = Field(default_factory=dict)
    approver_id: int | None = None


class ApprovalDecisionRequest(BaseModel):
    approve: bool
    reason: str = ""


class ApprovalView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_id: int
    approver_id: int | None
    operation_type: str
    payload: dict
    status: str
    decision_reason: str
    created_at: datetime
