from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.models import User
from app.services.calendar_service import CalendarEvent, CalendarService

router = APIRouter(prefix="/calendar", tags=["calendar"])
service = CalendarService()


class EventIn(BaseModel):
    title: str
    start: datetime
    end: datetime
    attendees: list[str] = Field(default_factory=list)


class ConflictRequest(BaseModel):
    events: list[EventIn]


class AgendaRequest(BaseModel):
    context: str


class SummaryRequest(BaseModel):
    transcript: str


class SlotRequest(BaseModel):
    duration_minutes: int
    day_start: datetime
    events: list[EventIn] = Field(default_factory=list)


@router.post("/conflicts")
async def detect_conflicts(
    payload: ConflictRequest,
    _: User = Depends(get_current_user),
) -> dict:
    events = [CalendarEvent(**event.model_dump()) for event in payload.events]
    return {"conflicts": service.detect_conflicts(events)}


@router.post("/agenda")
async def generate_agenda(payload: AgendaRequest, _: User = Depends(get_current_user)) -> dict:
    return {"agenda": await service.generate_agenda(payload.context)}


@router.post("/summary")
async def summarize_meeting(payload: SummaryRequest, _: User = Depends(get_current_user)) -> dict:
    return {"summary": await service.summarize_meeting(payload.transcript)}


@router.post("/suggest-slot")
async def suggest_slot(payload: SlotRequest, _: User = Depends(get_current_user)) -> dict:
    events = [CalendarEvent(**event.model_dump()) for event in payload.events]
    return service.suggest_slot(payload.duration_minutes, payload.day_start, events)
