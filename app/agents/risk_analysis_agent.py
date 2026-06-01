from app.agents.agent_names import RISK_ANALYSIS_AGENT_NAME
from app.agents.agent_stages import STAGE_RISKS_ANALYZED
from app.agents.review_context import ReviewContext
from app.rules.contract_rules import (
    collect_risks,
)

AGENT_NAME = RISK_ANALYSIS_AGENT_NAME


def run_risk_analysis_agent(context: ReviewContext) -> ReviewContext:
    context["activeAgent"] = AGENT_NAME
    context["currentStage"] = STAGE_RISKS_ANALYZED
    contract_text = context["contractText"]
    extracted_clauses = context["extractedClauses"]
    context["risks"] = collect_risks(contract_text, extracted_clauses)
    return context
