from typing import TypedDict
from uuid import uuid4

from app.agents.agent_stages import STAGE_PARSED
from app.agents.review_status import REVIEW_STATUS_RUNNING
from app.agents.review_types import (
    AgentStepDict,
    AuditEntryDict,
    ExtractedClauses,
    HumanReviewReasonDict,
    PolicyCheckDict,
    RiskDict,
)


class ReviewContext(TypedDict, total=False):
    contractText: str
    activeAgent: str
    taskId: str
    extractedClauses: ExtractedClauses
    risks: list[RiskDict]
    policyChecks: list[PolicyCheckDict]
    humanReviewReasons: list[HumanReviewReasonDict]
    auditLog: list[AuditEntryDict]
    agentSteps: list[AgentStepDict]
    error: str
    failedAgent: str
    failedStage: str
    status: str
    currentStage: str
    score: int
    level: str
    summary: str


def create_initial_context(contract_text: str) -> ReviewContext:
    return {
        "contractText": contract_text,
        "status": REVIEW_STATUS_RUNNING,
        "taskId": f"review-{uuid4().hex[:8]}",
        "currentStage": STAGE_PARSED,
    }
