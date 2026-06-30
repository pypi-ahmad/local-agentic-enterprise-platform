from datetime import UTC, datetime, timedelta
from typing import Any

from app.services.model_router import ModelRouter, Workload
from app.services.ollama_client import OllamaClient


class EmailService:
    """Email analysis and draft tooling with explicit-send guardrails."""

    def __init__(self) -> None:
        self.router = ModelRouter()
        self.ollama = OllamaClient()

    async def summarize_inbox(self, emails: list[dict[str, Any]]) -> dict[str, Any]:
        model = (await self.router.select(Workload.CHAT)).selected_model
        prompt = (
            "Summarize inbox, classify priorities, extract sentiment and action items.\n"
            f"Emails: {emails}\n"
            "Return JSON with keys summary, priorities, sentiments, action_items."
        )
        summary = await self.ollama.generate(model, prompt)
        return {"summary": summary, "count": len(emails)}

    async def draft_reply(self, email_thread: str, tone: str = "professional") -> dict[str, str]:
        model = (await self.router.select(Workload.CHAT)).selected_model
        prompt = (
            "Draft email reply without sending.\n"
            f"Tone: {tone}\n"
            f"Thread: {email_thread}\n"
            "Return concise draft and follow-up reminder recommendation."
        )
        draft = await self.ollama.generate(model, prompt)
        follow_up = (datetime.now(UTC) + timedelta(days=2)).isoformat()
        return {"draft": draft, "follow_up_reminder_at": follow_up, "send_allowed": "false"}

    async def extract_attachment_actions(self, text: str) -> dict[str, Any]:
        model = (await self.router.select(Workload.CHAT)).selected_model
        prompt = (
            "Extract attachment references and tasks from email body."
            f"\nBody: {text}\nReturn JSON array with attachment and action."
        )
        extracted = await self.ollama.generate(model, prompt)
        return {"extracted": extracted}
