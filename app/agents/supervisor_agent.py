from app.agents.agent_names import (
    SUPERVISOR_AGENT_NAME,
)
from app.agents.clause_extraction_agent import run_clause_extraction_agent
from app.agents.human_review_agent import run_human_review_agent
from app.agents.policy_check_agent import run_policy_check_agent
from app.agents.review_context import ReviewContext
from app.agents.risk_analysis_agent import (
    run_risk_analysis_agent,
)

AGENT_NAME = SUPERVISOR_AGENT_NAME


def run_supervisor_agent(context: ReviewContext) -> ReviewContext:
    context["activeAgent"] = AGENT_NAME
    context = run_clause_extraction_agent(context)
    context = run_risk_analysis_agent(context)
    context = run_policy_check_agent(context)
    context = run_human_review_agent(context)
    return context
