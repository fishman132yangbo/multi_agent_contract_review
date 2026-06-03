from app.agents.audit_log import build_error_audit_log
from app.agents.human_review_agent import (
    build_error_human_review_reasons,
)
from app.agents.review_context import ReviewContext
from app.agents.review_status import (
    REVIEW_STATUS_FAILED,
)
from app.schemas.review import ReviewResponse
from app.services.review_meta import REVIEW_REQUIRED


def build_review_response(context: ReviewContext) -> ReviewResponse:
    return ReviewResponse(
        taskId=context["taskId"],
        status=context["status"],
        score=context["score"],
        level=context["level"],
        summary=context["summary"],
        agentSteps=context["agentSteps"],
        policyChecks=context["policyChecks"],
        humanApproval=context["humanApproval"],
        risks=context["risks"],
        humanReviewReasons=context["humanReviewReasons"],
        auditLog=context["auditLog"],
    )


def build_error_review_response(context: ReviewContext) -> ReviewResponse:
    error_message = context.get("error", "合同审查失败")
    agentSteps = context.get("agentSteps", [])
    humanReviewReasons = build_error_human_review_reasons(context)
    auditLog = build_error_audit_log(context)
    return ReviewResponse(
        taskId=context["taskId"],
        score=0,
        status=REVIEW_STATUS_FAILED,
        level=REVIEW_REQUIRED,
        summary=error_message,
        agentSteps=agentSteps,
        policyChecks=[],
        risks=[],
        humanReviewReasons=humanReviewReasons,
        auditLog=auditLog,
    )
