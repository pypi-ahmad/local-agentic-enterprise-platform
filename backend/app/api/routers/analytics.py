from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import AnalyticsRecord, User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
service = AnalyticsService()


class MetricIn(BaseModel):
    metric_name: str
    metric_value: float
    dimensions: dict = Field(default_factory=dict)


@router.post("/metrics")
async def record_metric(
    payload: MetricIn,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> dict:
    rec = AnalyticsRecord(
        metric_name=payload.metric_name,
        metric_value=payload.metric_value,
        dimensions=payload.dimensions,
        recorded_at=datetime.now(UTC),
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return {"id": rec.id}


@router.get("/metrics/{metric_name}")
async def metric_summary(
    metric_name: str,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> dict:
    result = await session.execute(
        select(AnalyticsRecord).where(AnalyticsRecord.metric_name == metric_name).order_by(AnalyticsRecord.id)
    )
    records = list(result.scalars().all())
    values = [rec.metric_value for rec in records]
    summary = service.summarize(values)
    return {
        "metric_name": metric_name,
        "count": len(values),
        "average": summary.average,
        "trend_slope": summary.trend_slope,
        "anomalies": summary.anomalies,
    }
