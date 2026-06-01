from typing import Literal

from pydantic import BaseModel, Field, field_validator

ReviewLevel = Literal["none", "recommended", "required"]
AgentState = Literal["pending", "active", "done", "failed"]
RiskLevel = Literal["low", "medium", "high"]
PolicyStatus = Literal["pass", "fail", "needs_review"]
ReviewStatus = Literal["success", "failed", "running"]


class ReviewRequest(BaseModel):
    contract_text: str = Field(..., min_length=1)

    @field_validator("contract_text")
    @classmethod
    def validate_contract_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("contract_text must not be blank")

        return value


class AgentStep(BaseModel):
    name: str
    description: str
    state: AgentState


class PolicyCheck(BaseModel):
    ruleId: str
    rule: str
    status: PolicyStatus
    severity: RiskLevel
    message: str | None = None


class RiskItem(BaseModel):
    id: str
    ruleId: str
    level: RiskLevel
    title: str
    description: str
    evidence: str


class HumanReviewReason(BaseModel):
    category: str
    message: str
    source: str


class AuditEntry(BaseModel):
    taskId: str
    timestamp: str
    agent: str
    stage: str
    detail: str


class ReviewResponse(BaseModel):
    taskId: str
    status: ReviewStatus
    score: int
    level: ReviewLevel
    summary: str
    agentSteps: list[AgentStep]
    policyChecks: list[PolicyCheck]
    risks: list[RiskItem]
    humanReviewReasons: list[HumanReviewReason]
    auditLog: list[AuditEntry]
