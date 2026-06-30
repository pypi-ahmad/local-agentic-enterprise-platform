from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

_NOTIFICATION_LOG: list[dict] = []


class NotificationIn(BaseModel):
    channel: str = "in_app"
    title: str
    body: str
    metadata: dict = Field(default_factory=dict)


@router.post("/")
async def send_notification(
    payload: NotificationIn,
    user: User = Depends(get_current_user),
) -> dict:
    item = {
        "id": len(_NOTIFICATION_LOG) + 1,
        "user_id": user.id,
        "channel": payload.channel,
        "title": payload.title,
        "body": payload.body,
        "metadata": payload.metadata,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    _NOTIFICATION_LOG.append(item)
    return item


@router.get("/")
async def list_notifications(user: User = Depends(get_current_user)) -> list[dict]:
    return [item for item in _NOTIFICATION_LOG if item["user_id"] == user.id]
