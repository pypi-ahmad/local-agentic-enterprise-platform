from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from app.services.model_router import ModelRouter, Workload
from app.services.ollama_client import OllamaClient


@dataclass(slots=True)
class AgentResult:
    status: str
    output: dict[str, Any]
    model_used: str
    duration_ms: int
    warnings: list[str]


class BaseAgent(ABC):
    name: str
    workload: Workload = Workload.CHAT

    def __init__(self, model_router: ModelRouter, ollama: OllamaClient) -> None:
        self.model_router = model_router
        self.ollama = ollama

    async def run(self, task: str, payload: dict[str, Any], context: dict[str, Any]) -> AgentResult:
        selection = await self.model_router.select(self.workload)
        start = perf_counter()
        output = await self._execute(task=task, payload=payload, context=context, model=selection.selected_model)
        duration_ms = int((perf_counter() - start) * 1000)
        return AgentResult(
            status="success",
            output=output,
            model_used=selection.selected_model,
            duration_ms=duration_ms,
            warnings=[],
        )

    @abstractmethod
    async def _execute(
        self,
        task: str,
        payload: dict[str, Any],
        context: dict[str, Any],
        model: str,
    ) -> dict[str, Any]:
        raise NotImplementedError
