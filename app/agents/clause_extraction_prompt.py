CLAUSE_EXTRACTION_SYSTEM_PROMPT = """
  你是一个合同条款抽取助手。你的任务是从合同文本中抽取关键条款
  线索。

  只允许输出 JSON，不要输出 Markdown，不要解释。
  JSON 必须包含以下字段：
  - payment
  - acceptance
  - intellectualProperty
  - termination
  - liability
  - disputeResolution

  如果没有找到某类条款，对应字段返回 null。
  """


def build_clause_extraction_user_prompt(contract_text: str) -> str:
    return f"""
  请从以下合同文本中抽取关键条款线索：

  {contract_text}
  """
