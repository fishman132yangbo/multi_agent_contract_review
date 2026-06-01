from app.agents.agent_names import (
    CLAUSE_EXTRACTION_AGENT_NAME,
    HUMAN_REVIEW_AGENT_NAME,
    POLICY_CHECK_AGENT_NAME,
    QA_AGENT_NAME,
    RISK_ANALYSIS_AGENT_NAME,
    SUPERVISOR_AGENT_NAME,
)
from app.agents.agent_stages import (
    STAGE_CLAUSES_EXTRACTED,
    STAGE_HUMAN_REVIEWED,
    STAGE_PARSED,
    STAGE_POLICY_CHECKED,
    STAGE_QA_PASSED,
    STAGE_REVIEW_META,
    STAGE_RISKS_ANALYZED,
)
from app.agents.agent_states import (
    AGENT_STATE_DONE,
    AGENT_STATE_FAILED,
    AGENT_STATE_PENDING,
)
from app.agents.review_types import AgentStepDict
from app.schemas.review import AgentState

AGENT_STEP_DEFINITIONS = [
    {
        "name": SUPERVISOR_AGENT_NAME,
        "stage": STAGE_PARSED,
        "description": "创建审查任务，调度各 Agent 执行合同初筛。",
    },
    {
        "name": CLAUSE_EXTRACTION_AGENT_NAME,
        "stage": STAGE_CLAUSES_EXTRACTED,
        "description": "提取付款、验收、知识产权、终止、责任和争议解决条款线索。",
    },
    {
        "name": RISK_ANALYSIS_AGENT_NAME,
        "stage": STAGE_RISKS_ANALYZED,
        "description": "执行规则库，识别合同风险项。",
    },
    {
        "name": POLICY_CHECK_AGENT_NAME,
        "stage": STAGE_POLICY_CHECKED,
        "description": "根据风险项生成规则检查结果。",
    },
    {
        "name": HUMAN_REVIEW_AGENT_NAME,
        "stage": STAGE_HUMAN_REVIEWED,
        "description": "根据风险等级和合同内容判断人工审核原因。",
    },
    {
        "name": QA_AGENT_NAME,
        "stage": STAGE_QA_PASSED,
        "description": "检查审查结果一致性并生成审计日志。",
    },
]

STAGE_ORDER = [
    STAGE_PARSED,
    STAGE_CLAUSES_EXTRACTED,
    STAGE_RISKS_ANALYZED,
    STAGE_POLICY_CHECKED,
    STAGE_HUMAN_REVIEWED,
    STAGE_REVIEW_META,
    STAGE_QA_PASSED,
]


def resolve_agent_state(
    step_stage: str, current_stage: str, failed_stage: str | None = None
) -> AgentState:
    if failed_stage:
        step_index = STAGE_ORDER.index(step_stage)
        failed_index = STAGE_ORDER.index(failed_stage)
        if step_index < failed_index:
            return AGENT_STATE_DONE
        if step_index == failed_index:
            return AGENT_STATE_FAILED
        return AGENT_STATE_PENDING
    step_index = STAGE_ORDER.index(step_stage)
    current_index = STAGE_ORDER.index(current_stage)

    if step_index <= current_index:
        return AGENT_STATE_DONE

    return AGENT_STATE_PENDING


def build_agent_steps(
    current_stage: str, failed_stage: str | None = None
) -> list[AgentStepDict]:
    return [
        {
            "name": step["name"],
            "description": step["description"],
            "state": resolve_agent_state(
                step["stage"],
                current_stage,
                failed_stage,
            ),
        }
        for step in AGENT_STEP_DEFINITIONS
    ]
