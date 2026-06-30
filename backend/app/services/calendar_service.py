from dataclasses import dataclass
from datetime import datetime, timedelta

from app.services.model_router import ModelRouter, Workload
from app.services.ollama_client import OllamaClient


@dataclass(slots=True)
class CalendarEvent:
    title: str
    start: datetime
    end: datetime
    attendees: list[str]


class CalendarService:
    """Calendar planning, conflict detection, and summary generation."""

    def __init__(self) -> None:
        self.router = ModelRouter()
        self.ollama = OllamaClient()

    @staticmethod
    def detect_conflicts(events: list[CalendarEvent]) -> list[dict]:
        conflicts = []
        sorted_events = sorted(events, key=lambda event: event.start)
        for idx in range(1, len(sorted_events)):
            prev_event = sorted_events[idx - 1]
            curr_event = sorted_events[idx]
            if curr_event.start < prev_event.end:
                conflicts.append(
                    {
                        "event_a": prev_event.title,
                        "event_b": curr_event.title,
                        "overlap_minutes": int((prev_event.end - curr_event.start).total_seconds() // 60),
                    }
                )
        return conflicts

    async def generate_agenda(self, meeting_context: str) -> str:
        model = (await self.router.select(Workload.CHAT)).selected_model
        prompt = (
            "Generate agenda with time-boxed topics, owner, expected outcomes, and follow-up tasks.\n"
            f"Context: {meeting_context}"
        )
        return await self.ollama.generate(model, prompt)

    async def summarize_meeting(self, transcript: str) -> str:
        model = (await self.router.select(Workload.CHAT)).selected_model
        prompt = (
            "Summarize meeting transcript into decisions, risks, blockers, and next steps.\n"
            f"Transcript: {transcript}"
        )
        return await self.ollama.generate(model, prompt)

    @staticmethod
    def suggest_slot(duration_minutes: int, day_start: datetime, existing_events: list[CalendarEvent]) -> dict:
        pointer = day_start.replace(hour=9, minute=0, second=0, microsecond=0)
        day_end = day_start.replace(hour=18, minute=0, second=0, microsecond=0)
        slot_delta = timedelta(minutes=duration_minutes)

        while pointer + slot_delta <= day_end:
            candidate_end = pointer + slot_delta
            conflict = any(pointer < event.end and candidate_end > event.start for event in existing_events)
            if not conflict:
                return {"start": pointer.isoformat(), "end": candidate_end.isoformat()}
            pointer += timedelta(minutes=15)
        return {"start": None, "end": None}
