from typing import Any

import httpx
from loguru import logger

from app.core.config import get_settings


class OllamaClient:
    """Async client for local Ollama runtime."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_url.rstrip("/")
        self.timeout = settings.ollama_timeout_seconds
        self.inference_timeout = min(self.timeout, 20)

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            payload = response.json()
            models = payload.get("models", [])
            return [item["name"] for item in models if "name" in item]

    async def generate(self, model: str, prompt: str, stream: bool = False) -> str:
        data = {"model": model, "prompt": prompt, "stream": stream}
        try:
            async with httpx.AsyncClient(timeout=self.inference_timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=data)
                response.raise_for_status()
                payload = response.json()
                return payload.get("response", "")
        except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError) as exc:
            logger.warning("Ollama generate failed; using fallback response. Error={}", exc)
            return self._fallback_text(prompt)

    async def chat(self, model: str, messages: list[dict[str, str]]) -> str:
        data = {"model": model, "messages": messages, "stream": False}
        try:
            async with httpx.AsyncClient(timeout=self.inference_timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=data)
                response.raise_for_status()
                payload = response.json()
                message = payload.get("message", {})
                return message.get("content", "")
        except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError) as exc:
            logger.warning("Ollama chat failed; using fallback response. Error={}", exc)
            return "Model unavailable. Returning fallback response."

    async def embed(self, model: str, input_text: str) -> list[float]:
        data = {"model": model, "input": input_text}
        try:
            async with httpx.AsyncClient(timeout=self.inference_timeout) as client:
                response = await client.post(f"{self.base_url}/api/embed", json=data)
                response.raise_for_status()
                payload: dict[str, Any] = response.json()
                embeddings = payload.get("embeddings", [])
                if embeddings:
                    return embeddings[0]
                return []
        except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError) as exc:
            logger.warning("Ollama embed failed; returning empty embedding. Error={}", exc)
            return []

    @staticmethod
    def _fallback_text(prompt: str) -> str:
        if "Convert user request to SQL" in prompt:
            return "SELECT 1 AS health_check"
        return "Model unavailable. Returning fallback response."
