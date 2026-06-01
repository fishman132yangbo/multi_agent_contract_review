from app.agents.review_context import ReviewContext
from app.agents.review_types import RiskDict
from app.rules.contract_rules import (
    LEVEL_HIGH,
    LEVEL_MEDIUM,
)

REVIEW_NONE = "none"
REVIEW_RECOMMENDED = "recommended"
REVIEW_REQUIRED = "required"


def enrich_review_meta(context: ReviewContext) -> ReviewContext:
    risks = context.get("risks", [])
    score, level, summary = build_review_result_meta(risks)
    context["score"] = score
    context["level"] = level
    context["summary"] = summary
    return context


def build_review_result_meta(risks: list[RiskDict]) -> tuple[int, str, str]:
    high_count = sum(1 for risk in risks if risk["level"] == LEVEL_HIGH)
    medium_count = sum(1 for risk in risks if risk["level"] == LEVEL_MEDIUM)

    score = 100 - high_count * 18 - medium_count * 10
    score = max(score, 0)

    if high_count > 0:
        level = REVIEW_REQUIRED
    elif medium_count > 0:
        level = REVIEW_RECOMMENDED
    else:
        level = REVIEW_NONE

    if not risks:
        summary = "该合同未命中当前规则库中的明显风险，可作为低风险初筛结果。"
    else:
        summary = (
            f"该合同命中 {len(risks)} 项风险，其中高风险 {high_count} 项、"
            f"中风险 {medium_count} 项，建议结合业务背景进一步复核。"
        )

    return score, level, summary
