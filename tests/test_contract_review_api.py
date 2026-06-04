from app.main import app
from app.services.review_task_store import save_task
from app.services.response_builder import build_error_review_response
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_review_contract_returns_frontend_shape():
    response = client.post(
        "/contracts/review",
        json={"contract_text": "甲方与乙方签订软件服务合同，合同金额为120000元。"},
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["score"], int)
    assert data["level"] in ["none", "recommended", "required"]
    assert isinstance(data["summary"], str)
    assert isinstance(data["agentSteps"], list)
    assert isinstance(data["policyChecks"], list)
    assert all(isinstance(check["message"], str) for check in data["policyChecks"])
    assert isinstance(data["risks"], list)
    assert isinstance(data["humanReviewReasons"], list)
    assert isinstance(data["auditLog"], list)


def test_review_contract_rejects_empty_text():
    response = client.post("/contracts/review", json={"contract_text": ""})

    assert response.status_code == 422


def test_error_review_response_allows_required_review_level():
    response = build_error_review_response(
        {
            "taskId": "review-test",
            "error": "合同审查失败",
            "failedAgent": "Review Service",
            "failedStage": "review_meta",
            "agentSteps": [],
        }
    )

    assert response.status == "failed"
    assert response.level == "required"


def test_approval_returns_conflict_when_task_is_not_awaiting_human_review():
    task_id = "review-not-awaiting-human"
    save_task(
        {
            "taskId": task_id,
            "status": "success",
            "score": 95,
            "level": "none",
            "summary": "合同风险较低，无需人工复核。",
            "agentSteps": [],
            "policyChecks": [],
            "risks": [],
            "humanReviewReasons": [],
            "humanApproval": {
                "status": "not_required",
                "action": None,
                "reviewer": None,
                "comment": None,
                "decidedAt": None,
            },
            "auditLog": [],
        }
    )

    response = client.post(
        f"/contracts/review/{task_id}/approval",
        json={"action": "approve", "reviewer": "boyang"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": f"Task with id {task_id} is not awaiting human review"
    }


def test_approval_appends_string_audit_log_detail():
    task_id = "review-awaiting-human"
    save_task(
        {
            "taskId": task_id,
            "status": "awaiting_human_review",
            "score": 72,
            "level": "required",
            "summary": "合同需要人工复核。",
            "agentSteps": [],
            "policyChecks": [],
            "risks": [],
            "humanReviewReasons": [],
            "humanApproval": {
                "status": "pending",
                "action": None,
                "reviewer": None,
                "comment": None,
                "decidedAt": None,
            },
            "auditLog": [
                {
                    "taskId": task_id,
                    "timestamp": "2026-06-04 10:00:00 CST",
                    "agent": "QA Agent",
                    "stage": "qa_completed",
                    "detail": "审查流程完成，等待人工审批。",
                }
            ],
        }
    )

    response = client.post(
        f"/contracts/review/{task_id}/approval",
        json={"action": "approve", "reviewer": "哈哈", "comment": "1234"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["auditLog"][-1]["detail"] == "哈哈 提交人工审批结果：approve，备注：1234"
