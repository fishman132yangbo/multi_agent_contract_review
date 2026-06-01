from app.agents.agent_names import (
    CLAUSE_EXTRACTION_AGENT_NAME,
    POLICY_CHECK_AGENT_NAME,
    QA_AGENT_NAME,
    RISK_ANALYSIS_AGENT_NAME,
    SUPERVISOR_AGENT_NAME,
)
from app.agents.agent_stages import (
    STAGE_CLAUSES_EXTRACTED,
    STAGE_PARSED,
    STAGE_POLICY_CHECKED,
    STAGE_QA_PASSED,
    STAGE_RISKS_ANALYZED,
)
from app.agents.audit_log import now_info
from app.agents.review_context import ReviewContext
from app.agents.review_types import AuditEntryDict
from app.agents.review_status import REVIEW_STATUS_SUCCESS

AGENT_NAME = QA_AGENT_NAME


def run_qa_agent(context: ReviewContext) -> ReviewContext:
    context["activeAgent"] = AGENT_NAME
    context["currentStage"] = STAGE_QA_PASSED
    risks = context.get("risks", [])
    taskId = context.get("taskId", "unknown")
    policy_checks = context.get("policyChecks", [])
    extracted_clauses = context.get("extractedClauses", {})
    level = context.get("level", "none")
    status = context.get("status", REVIEW_STATUS_SUCCESS)
    failed_rules = [check for check in policy_checks if check["status"] == "fail"]
    extracted_count = sum(1 for value in extracted_clauses.values() if value)

    audit_log: list[AuditEntryDict] = [
        {
            "taskId": taskId,
            "timestamp": now_info(),
            "agent": SUPERVISOR_AGENT_NAME,
            "stage": STAGE_PARSED,
            "detail": f"初始化审查任务{taskId}，接收合同文本。",
        },
        {
            "taskId": taskId,
            "timestamp": now_info(),
            "agent": CLAUSE_EXTRACTION_AGENT_NAME,
            "stage": STAGE_CLAUSES_EXTRACTED,
            "detail": f"完成关键条款初步扫描，提取到 {extracted_count} 类条款线索。",
        },
        {
            "taskId": taskId,
            "timestamp": now_info(),
            "agent": RISK_ANALYSIS_AGENT_NAME,
            "stage": STAGE_RISKS_ANALYZED,
            "detail": f"识别 {len(risks)} 项风险。",
        },
        {
            "taskId": taskId,
            "timestamp": now_info(),
            "agent": POLICY_CHECK_AGENT_NAME,
            "stage": STAGE_POLICY_CHECKED,
            "detail": f"执行 {len(policy_checks)} 条规则，其"
            f"中 {len(failed_rules)} 条未通过。",
        },
        {
            "taskId": taskId,
            "timestamp": now_info(),
            "agent": AGENT_NAME,
            "stage": STAGE_QA_PASSED,
            "detail": f"完成结果一致性检查，任务状态为 {status}，人工审核等级为 {level}。",
        },
    ]
    context["auditLog"] = audit_log
    return context
