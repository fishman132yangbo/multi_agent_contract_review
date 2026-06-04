from app.agents.agent_names import RISK_ANALYSIS_AGENT_NAME
from app.agents.agent_stages import STAGE_RISKS_ANALYZED
from app.agents.legal_review_prompt import (
    LEGAL_REVIEW_SYSTEM_PROMPT,
    build_legal_review_user_prompt,
)
from app.agents.review_context import ReviewContext
from app.agents.review_types import ExtractedClauses, RiskDict
from app.rules.contract_rules import (
    collect_risks,
)
from app.services.llm_client import generate_json

AGENT_NAME = RISK_ANALYSIS_AGENT_NAME

VALID_RISK_LEVELS = {"low", "medium", "high"}


def run_risk_analysis_agent(context: ReviewContext) -> ReviewContext:
    context["activeAgent"] = AGENT_NAME
    context["currentStage"] = STAGE_RISKS_ANALYZED
    contract_text = context["contractText"]
    extracted_clauses = context["extractedClauses"]
    candidate_risks = collect_risks(contract_text, extracted_clauses)
    context["risks"] = review_candidate_risks_with_llm(
        extracted_clauses,
        candidate_risks,
    )
    return context


def review_candidate_risks_with_llm(
    extracted_clauses: ExtractedClauses,
    candidate_risks: list[RiskDict],
) -> list[RiskDict]:
    if not candidate_risks:
        return []

    try:
        llm_result = generate_json(
            LEGAL_REVIEW_SYSTEM_PROMPT,
            build_legal_review_user_prompt(extracted_clauses, candidate_risks),
        )
        return normalize_reviewed_risks(llm_result, candidate_risks)
    except Exception:
        return candidate_risks


def normalize_reviewed_risks(
    raw: dict[str, object],
    candidate_risks: list[RiskDict],
) -> list[RiskDict]:
    reviewed_items = raw.get("risks")
    if not isinstance(reviewed_items, list):
        return candidate_risks

    candidate_by_rule_id = {risk["ruleId"]: risk for risk in candidate_risks}
    reviewed_risks: list[RiskDict] = []
    for item in reviewed_items:
        if not isinstance(item, dict):
            continue
        if item.get("status") != "fail":
            continue

        rule_id = item.get("ruleId")
        if not isinstance(rule_id, str) or rule_id not in candidate_by_rule_id:
            continue

        candidate = candidate_by_rule_id[rule_id]
        level = item.get("level")
        title = item.get("title")
        description = item.get("description")
        evidence = item.get("evidence")

        reviewed_risks.append(
            {
                "id": f"RISK-{len(reviewed_risks) + 1:03d}",
                "ruleId": rule_id,
                "level": level if level in VALID_RISK_LEVELS else candidate["level"],
                "title": title if isinstance(title, str) else candidate["title"],
                "description": description
                if isinstance(description, str)
                else candidate["description"],
                "evidence": evidence
                if isinstance(evidence, str)
                else candidate["evidence"],
            }
        )

    return reviewed_risks
