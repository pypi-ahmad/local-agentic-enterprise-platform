from dataclasses import dataclass
from enum import StrEnum

from app.core.config import get_settings
from app.services.gpu_monitor import GPUMonitor
from app.services.ollama_client import OllamaClient


class Workload(StrEnum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    OCR = "ocr"
    ANALYTICS = "analytics"
    SQL = "sql"
    TRANSLATION = "translation"


@dataclass(slots=True)
class ModelSelection:
    workload: Workload
    selected_model: str
    fallback_model: str
    gpu_used: bool
    reason: str


class ModelRouter:
    """Chooses best local Ollama model dynamically by workload and runtime constraints."""

    def __init__(self, ollama_client: OllamaClient | None = None) -> None:
        self.settings = get_settings()
        self.ollama = ollama_client or OllamaClient()
        self.preference_map: dict[Workload, list[str]] = {
            Workload.CHAT: ["qwen3.5:4b", "phi4-mini:3.8b", "granite4.1:3b", "qwen3.5:2b"],
            Workload.EMBEDDING: ["qwen3-embedding:4b", "qwen3-embedding:0.6b"],
            Workload.OCR: ["glm-ocr:latest"],
            Workload.ANALYTICS: ["nemotron-3-nano:4b", "qwen3.5:4b", "granite4.1:3b"],
            Workload.SQL: ["qwen3.5:4b", "phi4-mini:3.8b"],
            Workload.TRANSLATION: ["translategemma:4b", "qwen3.5:2b"],
        }
        self.default_map: dict[Workload, str] = {
            Workload.CHAT: self.settings.model_router_default_chat,
            Workload.EMBEDDING: self.settings.model_router_default_embed,
            Workload.OCR: self.settings.model_router_default_ocr,
            Workload.ANALYTICS: self.settings.model_router_default_chat,
            Workload.SQL: self.settings.model_router_default_chat,
            Workload.TRANSLATION: self.settings.model_router_default_chat,
        }

    async def select(self, workload: Workload) -> ModelSelection:
        available_models = await self._safe_model_list()
        gpu = GPUMonitor.read_status()
        gpu_used = gpu.available and gpu.total_vram_mb > 0

        for candidate in self.preference_map[workload]:
            if candidate in available_models:
                if gpu_used and gpu.total_vram_mb and gpu.used_vram_mb / gpu.total_vram_mb > 0.9:
                    continue
                return ModelSelection(
                    workload=workload,
                    selected_model=candidate,
                    fallback_model=self.default_map[workload],
                    gpu_used=gpu_used,
                    reason=f"selected by capability ranking for {workload.value}",
                )

        return ModelSelection(
            workload=workload,
            selected_model=self.default_map[workload],
            fallback_model=self.default_map[workload],
            gpu_used=gpu_used,
            reason="fallback to configured default",
        )

    async def _safe_model_list(self) -> list[str]:
        try:
            return await self.ollama.list_models()
        except Exception:
            return []
