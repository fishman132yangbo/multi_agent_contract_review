from app.main import app
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
