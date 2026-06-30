from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.dependencies import db_session, get_current_user
from app.models import Document, User
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/documents", tags=["documents"])
service = KnowledgeService()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> dict:
    settings = get_settings()
    upload_dir = settings.artifacts_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "upload.bin").suffix
    destination = upload_dir / f"{uuid4().hex}{extension}"
    destination.write_bytes(await file.read())

    document = await service.ingest_document(
        session=session,
        user_id=user.id,
        name=file.filename or destination.name,
        file_path=destination,
        mime_type=file.content_type or "application/octet-stream",
    )
    return {"document_id": document.id, "name": document.name}


@router.get("/")
async def list_documents(
    session: AsyncSession = Depends(db_session),
    user: User = Depends(get_current_user),
) -> list[dict]:
    result = await session.execute(select(Document).where(Document.owner_id == user.id).order_by(Document.id.desc()))
    return [
        {
            "id": doc.id,
            "name": doc.name,
            "mime_type": doc.mime_type,
            "storage_path": doc.storage_path,
            "created_at": doc.created_at,
        }
        for doc in result.scalars().all()
    ]
