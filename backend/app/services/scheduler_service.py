from datetime import datetime
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerService:
    """Schedules one-time and recurring jobs."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.started = False

    def start(self) -> None:
        if not self.started:
            self.scheduler.start()
            self.started = True

    def schedule_once(self, run_at: datetime, callback, kwargs: dict | None = None) -> str:
        self.start()
        job_id = uuid4().hex
        self.scheduler.add_job(callback, "date", run_date=run_at, kwargs=kwargs or {}, id=job_id)
        return job_id

    def schedule_cron(self, cron: str, callback, kwargs: dict | None = None) -> str:
        self.start()
        job_id = uuid4().hex
        fields = cron.split()
        if len(fields) != 5:
            msg = "Cron must have 5 fields"
            raise ValueError(msg)
        minute, hour, day, month, day_of_week = fields
        self.scheduler.add_job(
            callback,
            "cron",
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            kwargs=kwargs or {},
            id=job_id,
        )
        return job_id

    def list_jobs(self) -> list[dict]:
        return [
            {
                "id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in self.scheduler.get_jobs()
        ]
