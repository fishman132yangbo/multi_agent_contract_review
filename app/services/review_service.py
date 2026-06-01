from app.agents.agent_names import REVIEW_SERVICE_NAME
from app.agents.agent_stages import STAGE_FAILED, STAGE_REVIEW_META
from app.agents.agent_steps import build_agent_steps
from app.agents.qa_agent import run_qa_agent
from app.agents.review_context import create_initial_context
from app.agents.review_status import REVIEW_STATUS_FAILED, REVIEW_STATUS_SUCCESS
from app.agents.supervisor_agent import (
    run_supervisor_agent,
)
from app.schemas.review import ReviewResponse
from app.services.response_builder import (
    build_error_review_response,
    build_review_response,
)
from app.services.review_meta import enrich_review_meta


def review_contract(contract_text: str) -> ReviewResponse:
    context = create_initial_context(contract_text)
    try:
        context = run_supervisor_agent(context)
        context["activeAgent"] = REVIEW_SERVICE_NAME
        context["currentStage"] = STAGE_REVIEW_META
        context = enrich_review_meta(context)
        context["status"] = REVIEW_STATUS_SUCCESS
        context = run_qa_agent(context)
        context["agentSteps"] = build_agent_steps(context["currentStage"])
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
