CLAUSE_EXTRACTION_SYSTEM_PROMPT = (
    "你是一个合同条款抽取助手。\n\n"
    "你的任务是从合同文本中抽取关键条款的原文片段。\n\n"
    "要求：\n"
    "1. 只输出 JSON，不要输出 Markdown，不要解释。\n"
    "2. 字段值必须来自合同原文，不要总结、不要改写、不要补充合同中没有的内容。\n"
    "3. 如果某类条款没有找到，对应字段返回 null。\n"
    "4. JSON 必须包含以下字段：\n"
    "- payment\n"
    "- acceptance\n"
    "- intellectualProperty\n"
    "- termination\n"
    "- liability\n"
    "- confidentiality\n"
    "- disputeResolution\n"
)


def build_clause_extraction_user_prompt(contract_text: str) -> str:
    return f"请从以下合同文本中抽取关键条款原文片段：\n\n合同文本：\n{contract_text}\n"
