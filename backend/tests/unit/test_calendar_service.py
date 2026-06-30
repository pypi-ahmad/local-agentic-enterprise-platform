from datetime import datetime

from app.services.calendar_service import CalendarEvent, CalendarService


def test_conflict_detection() -> None:
    events = [
        CalendarEvent(
            title="A",
            start=datetime(2026, 1, 1, 10, 0),
            end=datetime(2026, 1, 1, 11, 0),
            attendees=[],
        ),
        CalendarEvent(
            title="B",
            start=datetime(2026, 1, 1, 10, 30),
            end=datetime(2026, 1, 1, 11, 15),
            attendees=[],
        ),
    ]
    conflicts = CalendarService.detect_conflicts(events)
    assert len(conflicts) == 1
