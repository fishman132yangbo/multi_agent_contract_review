from app.agents.agent_names import CLAUSE_EXTRACTION_AGENT_NAME
from app.agents.agent_stages import STAGE_CLAUSES_EXTRACTED
from app.agents.review_context import ReviewContext
from app.agents.review_types import ExtractedClauses

AGENT_NAME = CLAUSE_EXTRACTION_AGENT_NAME


def find_clause(text: str, keywords: list[str]) -> str | None:
    for keyword in keywords:
        index = text.find(keyword)
        if index == -1:
            continue

        start = max(index - 40, 0)
        end = min(index + len(keyword) + 80, len(text))
        return text[start:end].strip()

    return None


def normalize_extracted_clauses(raw: dict[str, object]) -> ExtractedClauses:
    return {
        "payment": raw.get("payment") if isinstance(raw.get("payment"), str) else None,
        "acceptance": raw.get("acceptance")
        if isinstance(raw.get("acceptance"), str)
        else None,
        "intellectualProperty": raw.get("intellectualProperty")
        if isinstance(raw.get("intellectualProperty"), str)
        else None,
        "termination": raw.get("termination")
        if isinstance(raw.get("termination"), str)
        else None,
        "liability": raw.get("liability")
        if isinstance(raw.get("liability"), str)
        else None,
        "confidentiality": raw.get("confidentiality")
        if isinstance(raw.get("confidentiality"), str)
        else None,
        "disputeResolution": raw.get("disputeResolution")
        if isinstance(raw.get("disputeResolution"), str)
        else None,
    }


def run_clause_extraction_agent(context: ReviewContext) -> ReviewContext:
    context["activeAgent"] = AGENT_NAME
    context["currentStage"] = STAGE_CLAUSES_EXTRACTED
    contract_text = context["contractText"]
    extracted_clauses: ExtractedClauses = {
        "payment": find_clause(
            contract_text, ["付款", "支付", "合同金额", "人民币", "元"]
        ),
        "acceptance": find_clause(
            contract_text, ["验收标准", "验收流程", "验收期限", "验收合格", "验收方式"]
        ),
        "intellectualProperty": find_clause(
            contract_text,
            ["知识产权归属", "知识产权归甲方", "知识产权归乙方", "著作权", "版权"],
        ),
        "termination": find_clause(
            contract_text,
            [
                "甲方有权随时解除",
                "甲方可随时解除",
                "甲方有权单方解除",
                "甲方可单方解除",
                "解除",
                "终止",
            ],
        ),
        "liability": find_clause(
            contract_text,
            [
                "赔偿",
                "违约责任",
                "所有损失",
                "全部损失",
                "一切损失",
                "无限责任",
                "全额赔偿",
                "责任上限",
                "赔偿上限",
            ],
        ),
        "confidentiality": find_clause(
            contract_text,
            ["保密", "保密义务", "保密期限", "商业秘密", "秘密信息", "不得披露"],
        ),
        "disputeResolution": find_clause(
            contract_text, ["争议解决", "仲裁", "法院", "管辖", "诉讼"]
        ),
    }
    context["extractedClauses"] = extracted_clauses
    context["clauseExtractionSource"] = "keyword"
    return context
