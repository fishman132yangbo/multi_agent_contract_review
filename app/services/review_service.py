
from app.agents.agent_names import REVIEW_SERVICE_NAME
from app.agents.agent_stages import STAGE_FAILED, STAGE_REVIEW_META
from app.agents.agent_steps import build_agent_steps
from app.agents.qa_agent import run_qa_agent
from app.agents.review_context import create_initial_context
from app.agents.review_status import (
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_AWAITING_HUMAN_REVIEW,
    REVIEW_STATUS_CHANGES_REQUESTED,
    REVIEW_STATUS_FAILED,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_SUCCESS,
)
from app.agents.supervisor_agent import (
    run_supervisor_agent,
)
from app.schemas.review import ApprovalRequest, HumanApproval, ReviewResponse
from app.services.response_builder import (
    build_error_review_response,
    build_review_response,
)
from app.services.review_meta import REVIEW_REQUIRED, enrich_review_meta
from app.services.review_task_store import get_task, save_task
from app.agents.audit_log import now_info


class ReviewTaskNotFoundError(Exception):
    pass


class ReviewTaskConflictError(Exception):
    pass


APPROVAL_STATUS_BY_ACTION = {
    "approve": REVIEW_STATUS_APPROVED,
    "request_changes": REVIEW_STATUS_CHANGES_REQUESTED,
    "reject": REVIEW_STATUS_REJECTED,
}


def review_contract(contract_text: str) -> ReviewResponse:
    context = create_initial_context(contract_text)
    try:
        context = run_supervisor_agent(context)
        context["activeAgent"] = REVIEW_SERVICE_NAME
        context["currentStage"] = STAGE_REVIEW_META
        context = enrich_review_meta(context)
        if context["level"] == REVIEW_REQUIRED:
            context["status"] = REVIEW_STATUS_AWAITING_HUMAN_REVIEW
            context["humanApproval"] = {
                "status": "pending",
                "action": None,
                "reviewer": None,
                "comment": None,
                "decidedAt": None,
            }
        else:
            context["status"] = REVIEW_STATUS_SUCCESS
            context["humanApproval"] = {
                "status": "not_required",
                "action": None,
                "reviewer": None,
                "comment": None,
                "decidedAt": None,
            }
        context = run_qa_agent(context)
        context["agentSteps"] = build_agent_steps(context["currentStage"])
        context = save_task(context)
        return build_review_response(context)
    except Exception as exc:
        failed_stage = context.get("currentStage", STAGE_FAILED)
        context["failedAgent"] = context.get("activeAgent", "unknown")
        context["status"] = REVIEW_STATUS_FAILED
        context["error"] = str(exc)
        context["currentStage"] = STAGE_FAILED
        context["failedStage"] = failed_stage
        context["agentSteps"] = build_agent_steps(
            context["currentStage"], context["failedStage"]
        )
        return build_error_review_response(context)


def get_review_task(task_id: str) -> ReviewResponse | None:
    context = get_task(task_id)
    if context:
        return build_review_response(context)
    return None


def submit_approval(task_id: str, payload: ApprovalRequest) -> ReviewResponse:
    context = get_task(task_id)
    if not context:
        raise ReviewTaskNotFoundError(f"Task with id {task_id} not found")

    if context["status"] != REVIEW_STATUS_AWAITING_HUMAN_REVIEW:
        raise ReviewTaskConflictError(
            f"Task with id {task_id} is not awaiting human review"
        )
    decided_at = now_info()
    next_status = APPROVAL_STATUS_BY_ACTION[payload.action]

    context["status"] = next_status
    context["humanApproval"] = {
        "status": next_status,
        "action": payload.action,
        "reviewer": payload.reviewer,
        "comment": payload.comment,
        "decidedAt": decided_at,
    }
    context["summary"] = (
        f"人工审批结果：{payload.action}。"
        + (f"审核意见：{payload.comment}" if payload.comment else "")
        + f"初审结论：{context['summary']}。"
    )
    context["auditLog"].append(
        {
            "taskId": task_id,
            "timestamp": decided_at,
            "agent": REVIEW_SERVICE_NAME,
            "stage": "human_approval_submitted",
            "detail": f"{payload.reviewer} 提交人工审批结果：{payload.action}"
            + (f"，备注：{payload.comment}" if payload.comment else ""),
        }
    )

    context = save_task(context)
    return build_review_response(context)
