from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.models import User
from app.services.email_service import EmailService

router = APIRouter(prefix="/email", tags=["email"])
service = EmailService()


class InboxSummaryRequest(BaseModel):
    emails: list[dict] = Field(default_factory=list)


class DraftRequest(BaseModel):
    email_thread: str
    tone: str = "professional"


class AttachmentActionRequest(BaseModel):
    text: str


@router.post("/summarize")
async def summarize_inbox(
    payload: InboxSummaryRequest,
    _: User = Depends(get_current_user),
) -> dict:
    return await service.summarize_inbox(payload.emails)


@router.post("/draft-reply")
async def draft_reply(
    payload: DraftRequest,
    _: User = Depends(get_current_user),
) -> dict:
    return await service.draft_reply(payload.email_thread, payload.tone)


@router.post("/extract-attachments")
async def extract_attachments(
    payload: AttachmentActionRequest,
    _: User = Depends(get_current_user),
) -> dict:
    return await service.extract_attachment_actions(payload.text)
