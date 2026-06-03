from collections.abc import Callable
from typing import TypedDict

from app.agents.review_types import (
    ExtractedClauses,
    RiskDict,
    RuleRiskDict,
)
from app.schemas.review import RiskLevel

RuleChecker = Callable[[str, ExtractedClauses | None], RuleRiskDict | None]


class RuleDefinition(TypedDict):
    ruleId: str
    name: str
    severity: RiskLevel
    checker: RuleChecker


RULE_PAYMENT_TERM = "R003"
RULE_ACCEPTANCE = "R005"
RULE_LIABILITY_CAP = "R011"
RULE_BREACH_LIABILITY = "R012"
RULE_IP_OWNERSHIP = "R016"
RULE_TERMINATION = "R020"
RULE_CONFIDENTIALITY = "R025"
RULE_DISPUTE_RESOLUTION = "R030"

LEVEL_LOW: RiskLevel = "low"
LEVEL_MEDIUM: RiskLevel = "medium"
LEVEL_HIGH: RiskLevel = "high"

PAYMENT_KEYWORDS = ["付款", "支付", "合同金额", "人民币", "价款", "费用", "元"]
PAYMENT_TERM_KEYWORDS = [
    "付款期限",
    "付款时间",
    "付款节点",
    "支付期限",
    "支付时间",
    "支付节点",
    "预付款",
    "进度款",
    "阶段款",
    "尾款",
    "分期",
    "收到发票",
    "验收合格后",
    "交付后",
    "日内",
    "工作日内",
]
ACCEPTANCE_KEYWORDS = ["验收标准", "验收流程", "验收期限"]
DELIVERABLE_KEYWORDS = ["软件", "系统", "源代码", "交付成果", "开发", "技术文档"]
IP_SUBJECT_KEYWORDS = [
    "软件",
    "系统",
    "源代码",
    "源码",
    "交付成果",
    "交付物",
    "技术文档",
]
CONFIDENTIALITY_SUBJECT_KEYWORDS = [
    "软件",
    "源代码",
    "源码",
    "技术文档",
    "技术资料",
    "接口文档",
    "定制化交付成果",
    "定制交付成果",
    "定制化交付物",
    "定制交付物",
]
IP_CLAUSE_KEYWORDS = [
    "知识产权归属",
    "知识产权归甲方",
    "知识产权归乙方",
    "著作权",
    "版权",
]
TERMINATION_KEYWORDS = [
    "甲方有权随时解除",
    "甲方可随时解除",
    "甲方有权单方解除",
    "甲方可单方解除",
    "甲方有权任意解除",
    "甲方可任意解除",
    "甲方有权无理由解除",
    "甲方可无理由解除",
    "甲方无需说明理由解除",
]
TERMINATION_PROTECTION_KEYWORDS = ["提前通知", "通知期限", "补偿", "结算", "已完成工作"]
TERMINATION_REASONABLE_CAUSE_KEYWORDS = [
    "乙方违约",
    "严重违约",
    "逾期交付",
    "逾期完成",
    "验收不合格",
    "未达到标准",
    "未按约定",
    "违法违规",
    "破产",
    "资不抵债",
    "不可抗力",
    "经催告",
    "催告后",
    "未改正",
    "仍未完成",
]
LIABILITY_KEYWORDS = ["所有损失", "全部损失", "一切损失", "无限责任", "全额赔偿"]
LIABILITY_CAP_KEYWORDS = [
    "责任上限",
    "赔偿上限",
    "最高不超过",
    "不超过合同总金额",
    "累计赔偿",
]
BREACH_OBLIGATION_KEYWORDS = ["交付", "付款", "支付", "验收", "服务", "开发", "完成"]
BREACH_LIABILITY_KEYWORDS = [
    "违约责任",
    "违约金",
    "逾期交付",
    "逾期付款",
    "赔偿责任",
    "承担违约责任",
    "损失赔偿",
]
CONFIDENTIALITY_KEYWORDS = [
    "保密",
    "保密义务",
    "保密期限",
    "商业秘密",
    "秘密信息",
    "不得披露",
    "未经许可不得",
]
DISPUTE_RESOLUTION_KEYWORDS = ["争议解决", "仲裁", "法院", "管辖", "诉讼"]
EVIDENCE_BOUNDARIES = "。！？；\n\r"


def has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def extract_evidence_snippet(
    text: str,
    keywords: list[str],
    window: int = 30,
) -> str | None:
    for keyword in keywords:
        index = text.find(keyword)
        if index == -1:
            continue

        sentence_start = max(
            text.rfind(boundary, 0, index) for boundary in EVIDENCE_BOUNDARIES
        )
        sentence_end_candidates = []
        for boundary in EVIDENCE_BOUNDARIES:
            sentence_end = text.find(boundary, index + len(keyword))
            if sentence_end != -1:
                sentence_end_candidates.append(sentence_end)

        if sentence_start != -1 or sentence_end_candidates:
            start = sentence_start + 1 if sentence_start != -1 else 0
            end = (
                min(sentence_end_candidates) + 1
                if sentence_end_candidates
                else len(text)
            )
            return text[start:end].strip()

        start = max(index - window, 0)
        end = min(index + len(keyword) + window, len(text))
        return text[start:end].strip()

    return None


def check_payment_term_risk(
    contract_text: str,
    extracted_clauses: ExtractedClauses | None = None,
) -> RuleRiskDict | None:
    payment_text = extracted_clauses.get("payment") if extracted_clauses else None
    text_to_check = payment_text or contract_text
    payment_evidence = payment_text or extract_evidence_snippet(
        contract_text, PAYMENT_KEYWORDS
    )

    if not payment_evidence:
        return None

    if has_any(text_to_check, PAYMENT_TERM_KEYWORDS):
        return None

    return {
        "ruleId": RULE_PAYMENT_TERM,
        "level": LEVEL_MEDIUM,
        "title": "付款节点不明确",
        "description": "合同涉及付款或合同金额，但未明确付款时间、付款条件或付款比例。",
        "evidence": payment_evidence,
    }


def check_acceptance_risk(
    contract_text: str,
    extracted_clauses: ExtractedClauses | None = None,
) -> RuleRiskDict | None:
    if extracted_clauses and extracted_clauses.get("acceptance"):
        return None
    has_acceptance = has_any(contract_text, ACCEPTANCE_KEYWORDS)

    if has_acceptance:
        return None

    return {
        "ruleId": RULE_ACCEPTANCE,
        "level": LEVEL_HIGH,
        "title": "缺少明确验收标准",
        "description": "合同未定义验收标准、验收流程或验收期限。",
        "evidence": "未检测到验收标准、验收流程或验收期限相关表述。",
    }


def check_breach_liability_risk(
    contract_text: str,
    extracted_clauses: ExtractedClauses | None = None,
) -> RuleRiskDict | None:
    liability_text = extracted_clauses.get("liability") if extracted_clauses else None
    text_to_check = liability_text or contract_text
    obligation_evidence = extract_evidence_snippet(
        contract_text, BREACH_OBLIGATION_KEYWORDS
    )

    if not obligation_evidence:
        return None

    if has_any(text_to_check, BREACH_LIABILITY_KEYWORDS):
        return None

    return {
        "ruleId": RULE_BREACH_LIABILITY,
        "level": LEVEL_MEDIUM,
        "title": "违约责任约定缺失",
        "description": "合同涉及交付、付款或服务义务，但未明确违约责任、违约金或损失赔偿机制。",
        "evidence": obligation_evidence,
    }


def check_ip_ownership_risk(
    contract_text: str,
    extracted_clauses: ExtractedClauses | None = None,
) -> RuleRiskDict | None:

    deliverable_evidence = extract_evidence_snippet(contract_text, IP_SUBJECT_KEYWORDS)
    has_ip_clause = has_any(contract_text, IP_CLAUSE_KEYWORDS)

    if not deliverable_evidence:
        return None

    if extracted_clauses and extracted_clauses.get("intellectualProperty"):
        return None

    if has_ip_clause:
        return None

    return {
        "ruleId": RULE_IP_OWNERSHIP,
        "level": LEVEL_HIGH,
        "title": "知识产权归属缺失",
        "description": "合同涉及软件、系统或交付成果，但未明确知识产权归属。",
        "evidence": deliverable_evidence,
    }


def check_unilateral_termination_risk(
    contract_text: str,
    extracted_clauses: ExtractedClauses | None = None,
) -> RuleRiskDict | None:
    termination_text = (
        extracted_clauses.get("termination") if extracted_clauses else None
    )
    text_to_check = termination_text or contract_text
    termination_evidence = extract_evidence_snippet(text_to_check, TERMINATION_KEYWORDS)
    has_protection = has_any(text_to_check, TERMINATION_PROTECTION_KEYWORDS)
    has_reasonable_cause = has_any(text_to_check, TERMINATION_REASONABLE_CAUSE_KEYWORDS)

    if not termination_evidence:
        return None

    if has_reasonable_cause:
        return None

    if has_protection:
        return None

    return {
        "ruleId": RULE_TERMINATION,
        "level": LEVEL_HIGH,
        "title": "单方解除权过强",
        "description": "合同允许甲方单方或随时解除，但未约定合理解除原因、通知期限、补偿或已完成工作结算。",
        "evidence": termination_evidence,
    }


def check_liability_cap_risk(
    contract_text: str,
    extracted_clauses: ExtractedClauses | None = None,
) -> RuleRiskDict | None:
    liability_text = extracted_clauses.get("liability") if extracted_clauses else None
    text_to_check = liability_text or contract_text
    liability_evidence = extract_evidence_snippet(text_to_check, LIABILITY_KEYWORDS)
    has_liability_cap = has_any(text_to_check, LIABILITY_CAP_KEYWORDS)

    if not liability_evidence:
        return None

    if has_liability_cap:
        return None

    return {
        "ruleId": RULE_LIABILITY_CAP,
        "level": LEVEL_MEDIUM,
        "title": "赔偿范围过宽且缺少责任上限",
        "description": "合同约定赔偿范围较宽，但未限制赔偿金额上限，可能扩大责任承担。",
        "evidence": liability_evidence,
    }


def check_confidentiality_risk(
    contract_text: str,
    extracted_clauses: ExtractedClauses | None = None,
) -> RuleRiskDict | None:
    confidentiality_text = (
        extracted_clauses.get("confidentiality") if extracted_clauses else None
    )
    sensitive_evidence = extract_evidence_snippet(
        contract_text, CONFIDENTIALITY_SUBJECT_KEYWORDS
    )

    if not sensitive_evidence:
        return None

    if confidentiality_text:
        return None

    if has_any(contract_text, CONFIDENTIALITY_KEYWORDS):
        return None

    return {
        "ruleId": RULE_CONFIDENTIALITY,
        "level": LEVEL_MEDIUM,
        "title": "保密条款缺失",
        "description": "合同涉及软件、源代码、技术文档或定制化交付成果，但未约定保密义务。",
        "evidence": sensitive_evidence,
    }


def check_dispute_resolution_risk(
    contract_text: str, extracted_clauses: ExtractedClauses | None = None
) -> RuleRiskDict | None:
    if extracted_clauses and extracted_clauses.get("disputeResolution"):
        return None

    has_dispute_clause = has_any(contract_text, DISPUTE_RESOLUTION_KEYWORDS)

    if has_dispute_clause:
        return None

    return {
        "ruleId": RULE_DISPUTE_RESOLUTION,
        "level": LEVEL_MEDIUM,
        "title": "缺少争议解决条款",
        "description": "合同未明确争议解决方式或管辖机构，发生纠纷时可能增加处理成本。",
        "evidence": "未检测到争议解决、仲裁、法院、管辖或诉讼相关表述。",
    }


def collect_risks(
    contract_text: str, extracted_clauses: ExtractedClauses | None = None
) -> list[RiskDict]:
    risks: list[RiskDict] = []

    for rule in RULES:
        risk = rule["checker"](contract_text, extracted_clauses)
        if risk:
            risks.append({**risk, "id": f"RISK-{len(risks) + 1:03d}"})

    return risks


RULES: list[RuleDefinition] = [
    {
        "ruleId": RULE_PAYMENT_TERM,
        "name": "付款节点检查",
        "severity": LEVEL_MEDIUM,
        "checker": check_payment_term_risk,
    },
    {
        "ruleId": RULE_ACCEPTANCE,
        "name": "验收条款检查",
        "severity": LEVEL_HIGH,
        "checker": check_acceptance_risk,
    },
    {
        "ruleId": RULE_LIABILITY_CAP,
        "name": "责任上限检查",
        "severity": LEVEL_MEDIUM,
        "checker": check_liability_cap_risk,
    },
    {
        "ruleId": RULE_BREACH_LIABILITY,
        "name": "违约责任检查",
        "severity": LEVEL_MEDIUM,
        "checker": check_breach_liability_risk,
    },
    {
        "ruleId": RULE_IP_OWNERSHIP,
        "name": "知识产权归属检查",
        "severity": LEVEL_HIGH,
        "checker": check_ip_ownership_risk,
    },
    {
        "ruleId": RULE_TERMINATION,
        "name": "单方解除权检查",
        "severity": LEVEL_HIGH,
        "checker": check_unilateral_termination_risk,
    },
    {
        "ruleId": RULE_CONFIDENTIALITY,
        "name": "保密条款检查",
        "severity": LEVEL_MEDIUM,
        "checker": check_confidentiality_risk,
    },
    {
        "ruleId": RULE_DISPUTE_RESOLUTION,
        "name": "争议解决条款检查",
        "severity": LEVEL_MEDIUM,
        "checker": check_dispute_resolution_risk,
    },
]
