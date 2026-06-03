from app.rules.contract_rules import (
    RULE_CONFIDENTIALITY,
    RULE_IP_OWNERSHIP,
    RULE_TERMINATION,
    check_confidentiality_risk,
    check_ip_ownership_risk,
    check_unilateral_termination_risk,
)


def test_confidentiality_risk_ignores_non_sensitive_deliverables():
    risk = check_confidentiality_risk(
        "甲方委托乙方提供企业管理咨询服务，乙方应提交项目交付成果报告。"
    )

    assert risk is None


def test_confidentiality_risk_requires_clause_for_software_source_code_and_docs():
    risk = check_confidentiality_risk(
        "乙方负责开发订单管理软件，交付源代码和技术文档。"
    )

    assert risk is not None
    assert risk["ruleId"] == RULE_CONFIDENTIALITY


def test_confidentiality_risk_requires_clause_for_customized_deliverables():
    risk = check_confidentiality_risk("乙方应向甲方提交定制化交付成果。")

    assert risk is not None
    assert risk["ruleId"] == RULE_CONFIDENTIALITY


def test_ip_ownership_risk_ignores_contract_without_software_system_or_deliverables():
    risk = check_ip_ownership_risk("乙方为甲方提供开发流程咨询服务和团队培训。")

    assert risk is None


def test_ip_ownership_risk_requires_clause_for_software_system_or_deliverables():
    risk = check_ip_ownership_risk("乙方为甲方开发订单管理系统并交付源代码。")

    assert risk is not None
    assert risk["ruleId"] == RULE_IP_OWNERSHIP


def test_ip_ownership_risk_evidence_keeps_complete_sentence_context():
    contract_text = (
        "第一条 合同背景：甲方正在推进内部数字化管理升级，"
        "并要求乙方按照既有业务流程和权限模型完成订单管理系统的设计、开发、测试和上线部署。"
        "第二条 费用：合同金额为人民币100000元。"
    )

    risk = check_ip_ownership_risk(contract_text)

    assert risk is not None
    assert risk["evidence"] == (
        "第一条 合同背景：甲方正在推进内部数字化管理升级，"
        "并要求乙方按照既有业务流程和权限模型完成订单管理系统的设计、开发、测试和上线部署。"
    )


def test_unilateral_termination_risk_ignores_breach_based_termination():
    risk = check_unilateral_termination_risk(
        "乙方逾期交付超过十日，经甲方书面催告后仍未完成的，甲方有权单方解除合同。"
    )

    assert risk is None


def test_unilateral_termination_risk_reports_unconditional_termination():
    risk = check_unilateral_termination_risk(
        "甲方可随时解除本合同，且无需承担任何赔偿责任。"
    )

    assert risk is not None
    assert risk["ruleId"] == RULE_TERMINATION
