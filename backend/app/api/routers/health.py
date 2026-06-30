from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine
from app.dependencies import db_session
from app.services.gpu_monitor import GPUMonitor
from app.services.ollama_client import OllamaClient

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def readiness(session: AsyncSession = Depends(db_session)) -> dict:
    db_ok = False
    try:
        await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    ollama_ok = False
    try:
        models = await OllamaClient().list_models()
        ollama_ok = len(models) > 0
    except Exception:
        ollama_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "ollama": ollama_ok,
        "gpu": asdict(GPUMonitor.read_status()),
        "database_url": str(engine.url),
    }
