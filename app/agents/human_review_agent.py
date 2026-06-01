from app.agents.agent_names import (
    HUMAN_REVIEW_AGENT_NAME,
    REVIEW_SERVICE_NAME,
    RISK_ANALYSIS_AGENT_NAME,
)
from app.agents.agent_stages import STAGE_HUMAN_REVIEWED
from app.agents.error_codes import ERROR_CATEGORY_SYSTEM
from app.agents.review_context import ReviewContext
from app.agents.review_types import HumanReviewReasonDict
from app.rules.contract_rules import LEVEL_HIGH

AGENT_NAME = HUMAN_REVIEW_AGENT_NAME


def run_human_review_agent(context: ReviewContext) -> ReviewContext:
    context["activeAgent"] = AGENT_NAME
    context["currentStage"] = STAGE_HUMAN_REVIEWED
    reasons: list[HumanReviewReasonDict] = []
    risks = context["risks"]
    extracted_clauses = context["extractedClauses"]
    high_risks = [risk for risk in risks if risk["level"] == LEVEL_HIGH]

    if high_risks:
        reasons.append(
            {
                "category": "high_risk",
                "message": f"检测到 {len(high_risks)} 项高风险条款，需要人工复核。",
                "source": RISK_ANALYSIS_AGENT_NAME,
            }
        )

    if extracted_clauses.get("payment"):
        reasons.append(
            {
                "category": "amount_related",
                "message": "合同涉及金额条款，建议结合付款节点和验收条件复核。",
                "source": AGENT_NAME,
            }
        )

    if not reasons:
        reasons.append(
            {
                "category": "none",
                "message": "当前规则未触发强制人工审核原因。",
                "source": AGENT_NAME,
            }
        )

    context["humanReviewReasons"] = reasons

    return context


def build_error_human_review_reasons(
    context: ReviewContext,
) -> list[HumanReviewReasonDict]:
    error_message = context.get("error", "合同审查失败")
    failed_agent = context.get("failedAgent", REVIEW_SERVICE_NAME)
    return [
        {
            "category": ERROR_CATEGORY_SYSTEM,
            "message": f"{failed_agent} 执行失败：{error_message}",
            "source": failed_agent,
        }
    ]
