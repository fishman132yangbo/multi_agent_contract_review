from app.agents.agent_names import POLICY_CHECK_AGENT_NAME
from app.agents.agent_stages import STAGE_POLICY_CHECKED
from app.agents.review_context import ReviewContext
from app.agents.review_types import PolicyCheckDict
from app.rules.contract_rules import RULES

AGENT_NAME = POLICY_CHECK_AGENT_NAME


def run_policy_check_agent(context: ReviewContext) -> ReviewContext:
    context["activeAgent"] = AGENT_NAME
    context["currentStage"] = STAGE_POLICY_CHECKED
    risks = context.get("risks", [])
    failed_rule_ids = {risk["ruleId"] for risk in risks}
    risk_messages_by_rule_id = {risk["ruleId"]: risk["title"] for risk in risks}
    policy_checks: list[PolicyCheckDict] = [
        {
            "ruleId": rule["ruleId"],
            "rule": rule["name"],
            "status": "fail" if rule["ruleId"] in failed_rule_ids else "pass",
            "severity": rule["severity"],
            "message": risk_messages_by_rule_id.get(rule["ruleId"], "未发现明显问题"),
        }
        for rule in RULES
    ]
    context["policyChecks"] = policy_checks
    return context
