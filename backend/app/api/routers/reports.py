from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import Report, User
from app.schemas.report import ReportCreateRequest, ReportView
from app.services.report_service import ReportExportService

router = APIRouter(prefix="/reports", tags=["reports"])
exporter = ReportExportService()


@router.post("/", response_model=ReportView)
async def create_report(
    payload: ReportCreateRequest,
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> ReportView:
    report = Report(
        name=payload.name,
        report_type=payload.report_type,
        generated_by=user.id,
        payload=payload.payload,
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return ReportView.model_validate(report)


@router.get("/", response_model=list[ReportView])
async def list_reports(
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[ReportView]:
    result = await session.execute(select(Report).order_by(Report.id.desc()).limit(200))
    return [ReportView.model_validate(item) for item in result.scalars().all()]


@router.post("/{report_id}/export/{fmt}")
async def export_report(
    report_id: int,
    fmt: str,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> dict:
    report = await session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    filename = f"report_{report.id}_{report.report_type}"
    output_path: Path
    if fmt == "pdf":
        output_path = exporter.to_pdf(filename=filename, report_data=report.payload)
    elif fmt == "xlsx":
        output_path = exporter.to_excel(filename=filename, report_data=report.payload)
    elif fmt == "pptx":
        output_path = exporter.to_pptx(filename=filename, report_data=report.payload)
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

    report.file_path = str(output_path)
    await session.commit()
    return {"path": str(output_path)}
