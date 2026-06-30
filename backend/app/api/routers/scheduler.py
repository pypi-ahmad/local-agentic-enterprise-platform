from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.models import User
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["scheduler"])
service = SchedulerService()


class ScheduleOnceIn(BaseModel):
    run_at: datetime
    message: str


class ScheduleCronIn(BaseModel):
    cron: str
    message: str


def _noop_task(message: str) -> None:
    _ = message


@router.post("/once")
async def schedule_once(payload: ScheduleOnceIn, _: User = Depends(get_current_user)) -> dict:
    job_id = service.schedule_once(payload.run_at, _noop_task, {"message": payload.message})
    return {"job_id": job_id}


@router.post("/cron")
async def schedule_cron(payload: ScheduleCronIn, _: User = Depends(get_current_user)) -> dict:
    job_id = service.schedule_cron(payload.cron, _noop_task, {"message": payload.message})
    return {"job_id": job_id}


@router.get("/jobs")
async def list_jobs(_: User = Depends(get_current_user)) -> list[dict]:
    return service.list_jobs()
