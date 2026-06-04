from app.agents.clause_extraction_agent import run_clause_extraction_agent
from app.agents.risk_analysis_agent import run_risk_analysis_agent


def test_clause_extraction_uses_local_keywords_without_calling_llm(monkeypatch):
    called = False

    def fail_if_called(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("clause extraction should not send full contract to LLM")

    monkeypatch.setattr(
        "app.agents.clause_extraction_agent.generate_json",
        fail_if_called,
        raising=False,
    )

    context = {
        "taskId": "review-local-extraction",
        "contractText": "乙方为甲方开发订单管理系统并交付源代码。合同金额为人民币100000元。",
    }

    result = run_clause_extraction_agent(context)

    assert called is False
    assert result["clauseExtractionSource"] == "keyword"
    assert "合同金额为人民币100000元" in result["extractedClauses"]["payment"]


def test_risk_analysis_sends_extracted_clauses_and_candidate_risks_to_llm(monkeypatch):
    captured_prompt = ""
    unique_full_text_only_clause = "本句只存在于合同全文中，不应该出现在大模型复核提示里。"

    def fake_generate_json(system_prompt, user_prompt):
        nonlocal captured_prompt
        captured_prompt = user_prompt
        return {
            "risks": [
                {
                    "ruleId": "R016",
                    "status": "fail",
                    "level": "high",
                    "title": "知识产权归属缺失",
                    "description": "合同涉及软件系统和源代码交付，但未明确知识产权归属。",
                    "evidence": "乙方为甲方开发订单管理系统并交付源代码。",
                }
            ]
        }

    monkeypatch.setattr("app.agents.risk_analysis_agent.generate_json", fake_generate_json, raising=False)

    context = {
        "taskId": "review-legal-review",
        "contractText": (
            "乙方为甲方开发订单管理系统并交付源代码。"
            f"{unique_full_text_only_clause}"
        ),
        "extractedClauses": {
            "payment": None,
            "acceptance": None,
            "intellectualProperty": None,
            "termination": None,
            "liability": None,
            "confidentiality": None,
            "disputeResolution": None,
        },
    }

    result = run_risk_analysis_agent(context)

    assert captured_prompt
    assert "R016" in captured_prompt
    assert "乙方为甲方开发订单管理系统并交付源代码。" in captured_prompt
    assert unique_full_text_only_clause not in captured_prompt
    assert result["risks"] == [
        {
            "id": "RISK-001",
            "ruleId": "R016",
            "level": "high",
            "title": "知识产权归属缺失",
            "description": "合同涉及软件系统和源代码交付，但未明确知识产权归属。",
            "evidence": "乙方为甲方开发订单管理系统并交付源代码。",
        }
    ]
