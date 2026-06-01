from datetime import UTC, datetime

from app.agents.agent_names import REVIEW_SERVICE_NAME
from app.agents.agent_stages import STAGE_FAILED
from app.agents.review_context import ReviewContext
from app.agents.review_types import AuditEntryDict


def build_error_audit_log(context: ReviewContext) -> list[AuditEntryDict]:
    error_message = context.get("error", "合同审查失败")
    failed_stage = context.get("failedStage", STAGE_FAILED)
    failed_agent = context.get("failedAgent", "unknown")
    return [
        {
            "taskId": context["taskId"],
            "timestamp": now_info(),
            "agent": REVIEW_SERVICE_NAME,
            "stage": STAGE_FAILED,
            "detail": (
                f"审查流程在 {failed_stage} 阶段失败，"
                f"失败 Agent 为 {failed_agent}：{error_message}"
            ),
        }
    ]


def now_info() -> str:
    return datetime.now(UTC).isoformat()
