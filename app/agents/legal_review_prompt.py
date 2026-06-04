import json

from app.agents.review_types import ExtractedClauses, RiskDict
from app.rules.contract_rules import (
    RULE_ACCEPTANCE,
    RULE_BREACH_LIABILITY,
    RULE_CONFIDENTIALITY,
    RULE_DISPUTE_RESOLUTION,
    RULE_IP_OWNERSHIP,
    RULE_LIABILITY_CAP,
    RULE_PAYMENT_TERM,
    RULE_TERMINATION,
)

LEGAL_REVIEW_SYSTEM_PROMPT = (
    "你是一个合同法律风险复核助手。\n\n"
    "你只会收到本地程序抽取出的合同条款片段、候选风险和规则判断点。"
    "不要假设没有提供的合同全文内容。\n\n"
    "要求：\n"
    "1. 只输出 JSON，不要输出 Markdown，不要解释。\n"
    "2. 只能基于输入中的条款片段和候选风险判断。\n"
    "3. 对每个候选风险判断是否成立，成立时 status 返回 fail，不成立时 status 返回 pass。\n"
    "4. JSON 必须包含 risks 数组。\n"
)

RULE_CHECK_POINTS = {
    RULE_PAYMENT_TERM: [
        "合同是否约定付款期限、付款节点或支付时间。",
        "仅有合同金额但没有付款安排时，应认为付款节点不清晰。",
    ],
    RULE_ACCEPTANCE: [
        "合同是否明确验收标准、验收流程或验收期限。",
        "只有交付或付款表述，不等于已经约定验收机制。",
    ],
    RULE_LIABILITY_CAP: [
        "合同是否存在所有损失、全部损失、一切损失、无限责任等过宽责任表述。",
        "合同是否设置赔偿上限、责任上限或累计赔偿限制。",
    ],
    RULE_BREACH_LIABILITY: [
        "合同涉及交付、付款、服务或开发义务时，是否约定违约责任。",
        "违约责任可包括违约金、逾期责任或损失赔偿机制。",
    ],
    RULE_IP_OWNERSHIP: [
        "合同是否涉及软件、系统、源代码、技术文档或交付成果。",
        "合同是否明确约定知识产权、著作权、版权或成果归属。",
        "只描述开发和交付，不等于已经约定知识产权归属。",
    ],
    RULE_TERMINATION: [
        "合同是否允许一方无理由、随时或单方解除。",
        "合同是否设置提前通知、补偿、结算或合理解除事由。",
    ],
    RULE_CONFIDENTIALITY: [
        "合同是否涉及源代码、技术文档、技术资料或定制化交付成果。",
        "合同是否约定保密义务、保密期限或不得披露义务。",
    ],
    RULE_DISPUTE_RESOLUTION: [
        "合同是否约定争议解决方式。",
        "争议解决方式可包括仲裁、法院管辖或诉讼安排。",
    ],
}


def build_legal_review_user_prompt(
    extracted_clauses: ExtractedClauses,
    candidate_risks: list[RiskDict],
) -> str:
    payload = {
        "extractedClauses": extracted_clauses,
        "candidateRisks": [
            {
                **risk,
                "checkPoints": RULE_CHECK_POINTS.get(risk["ruleId"], []),
            }
            for risk in candidate_risks
        ],
        "outputSchema": {
            "risks": [
                {
                    "ruleId": "规则 ID",
                    "status": "fail 或 pass",
                    "level": "low、medium 或 high",
                    "title": "风险标题",
                    "description": "风险说明",
                    "evidence": "来自输入条款或候选风险证据的原文片段",
                }
            ]
        },
    }
    return "请复核以下本地候选风险，判断风险是否成立：\n\n" + json.dumps(
        payload, ensure_ascii=False
    )
