from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.services.model_router import Workload


class GenericChatAgent(BaseAgent):
    prompt_prefix: str = ""

    async def _execute(
        self,
        task: str,
        payload: dict[str, Any],
        context: dict[str, Any],
        model: str,
    ) -> dict[str, Any]:
        prompt = (
            f"{self.prompt_prefix}\n"
            f"Task: {task}\n"
            f"Payload: {payload}\n"
            f"Context: {context}\n"
            "Return strict JSON with actionable steps, rationale, and risks."
        )
        response = await self.ollama.generate(model=model, prompt=prompt)
        return {"result": response, "timestamp": datetime.utcnow().isoformat()}


class EmailAgent(GenericChatAgent):
    name = "email"
    workload = Workload.CHAT
    prompt_prefix = (
        "You are Email Agent. Capabilities: inbox summarization, priority classification, "
        "drafting replies, suggestions, follow-up reminders, attachment extraction, sentiment, "
        "action item extraction. Never send email automatically."
    )


class CalendarAgent(GenericChatAgent):
    name = "calendar"
    workload = Workload.CHAT
    prompt_prefix = (
        "You are Calendar Agent. Capabilities: scheduling, availability check, recurring events, "
        "reminders, conflict detection, meeting summaries, agendas, task extraction."
    )


class ReportAgent(GenericChatAgent):
    name = "report"
    workload = Workload.ANALYTICS
    prompt_prefix = (
        "You are Report Agent. Generate daily/weekly/monthly and executive reports. "
        "Output should include KPI narratives and export hints."
    )


class AnalyticsAgent(GenericChatAgent):
    name = "analytics"
    workload = Workload.ANALYTICS
    prompt_prefix = (
        "You are Analytics Agent. Do trend analysis, anomaly detection, KPI tracking, forecasting, "
        "and visualization recommendations."
    )


class DatabaseAgent(GenericChatAgent):
    name = "database"
    workload = Workload.SQL
    prompt_prefix = (
        "You are Database Agent. Handle schema discovery, table exploration, CRUD, migrations, backups, "
        "and indexing recommendations with safety notes."
    )


class SQLAgent(GenericChatAgent):
    name = "sql"
    workload = Workload.SQL
    prompt_prefix = (
        "You are SQL Agent. Convert natural language to SQL and explain query, joins, group by, CTE, "
        "window functions. Highlight destructive operations."
    )


class DashboardAgent(GenericChatAgent):
    name = "dashboard"
    workload = Workload.ANALYTICS
    prompt_prefix = (
        "You are Dashboard Agent. Build KPI-focused interactive dashboard plans with drill-down filters and alerts."
    )


class DocumentAgent(GenericChatAgent):
    name = "document"
    workload = Workload.CHAT
    prompt_prefix = "You are Document Agent. Parse, summarize, classify documents and extract entities."


class OCRAgent(GenericChatAgent):
    name = "ocr"
    workload = Workload.OCR
    prompt_prefix = "You are OCR Agent. Extract accurate text from scanned docs/images with confidence notes."


class WorkflowAgent(GenericChatAgent):
    name = "workflow"
    workload = Workload.CHAT
    prompt_prefix = "You are Workflow Agent. Build automations with branching, retries, and approval gates."


class NotificationAgent(GenericChatAgent):
    name = "notification"
    workload = Workload.CHAT
    prompt_prefix = "You are Notification Agent. Produce concise alerts for users/channels with priority labels."


class KnowledgeAgent(GenericChatAgent):
    name = "knowledge"
    workload = Workload.EMBEDDING
    prompt_prefix = "You are Knowledge Agent. Answer with citations from indexed business knowledge base."


class MemoryAgent(GenericChatAgent):
    name = "memory"
    workload = Workload.CHAT
    prompt_prefix = "You are Memory Agent. Manage short-term and long-term memory snapshots and retrieval."


class ApprovalAgent(GenericChatAgent):
    name = "approval"
    workload = Workload.CHAT
    prompt_prefix = "You are Approval Agent. Prepare risk summaries for human approval decisions."


class SchedulerAgent(GenericChatAgent):
    name = "scheduler"
    workload = Workload.CHAT
    prompt_prefix = "You are Scheduler Agent. Schedule long-running workflows and recurring jobs."


ALL_AGENT_TYPES: dict[str, type[BaseAgent]] = {
    "email": EmailAgent,
    "calendar": CalendarAgent,
    "report": ReportAgent,
    "analytics": AnalyticsAgent,
    "database": DatabaseAgent,
    "sql": SQLAgent,
    "dashboard": DashboardAgent,
    "document": DocumentAgent,
    "ocr": OCRAgent,
    "workflow": WorkflowAgent,
    "notification": NotificationAgent,
    "knowledge": KnowledgeAgent,
    "memory": MemoryAgent,
    "approval": ApprovalAgent,
    "scheduler": SchedulerAgent,
}


def agent_names() -> list[str]:
    return sorted(ALL_AGENT_TYPES.keys())
