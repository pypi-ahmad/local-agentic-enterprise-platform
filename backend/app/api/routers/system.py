import platform
from dataclasses import asdict
from datetime import UTC, datetime

import psutil
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User
from app.services.gpu_monitor import GPUMonitor
from app.services.model_router import ModelRouter, Workload
from app.services.ollama_client import OllamaClient

router = APIRouter(prefix="/system", tags=["system"])
router_service = ModelRouter()


@router.get("/monitoring")
async def monitoring(_: User = Depends(get_current_user)) -> dict:
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.2)
    gpu = GPUMonitor.read_status()
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "cpu_percent": cpu_percent,
        "memory_used_percent": memory.percent,
        "memory_available_gb": round(memory.available / (1024**3), 2),
        "gpu": asdict(gpu),
    }


@router.get("/models")
async def model_manager(_: User = Depends(get_current_user)) -> dict:
    models = []
    try:
        models = await OllamaClient().list_models()
    except Exception:
        models = []

    selections = {}
    for workload in Workload:
        selection = await router_service.select(workload)
        selections[workload.value] = {
            "workload": selection.workload.value,
            "selected_model": selection.selected_model,
            "fallback_model": selection.fallback_model,
            "gpu_used": selection.gpu_used,
            "reason": selection.reason,
        }

    return {"installed_models": models, "routing": selections}
