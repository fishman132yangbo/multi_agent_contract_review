from typing import TypedDict

from app.schemas.review import AgentState, PolicyStatus, RiskLevel


class ExtractedClauses(TypedDict):
    payment: str | None
    acceptance: str | None
    intellectualProperty: str | None
    termination: str | None
    liability: str | None
    disputeResolution: str | None


class RuleRiskDict(TypedDict):
    ruleId: str
    level: RiskLevel
    title: str
    description: str
    evidence: str


class RiskDict(RuleRiskDict):
    id: str


class PolicyCheckDict(TypedDict):
    ruleId: str
    rule: str
    status: PolicyStatus
    severity: RiskLevel
    message: str


class HumanReviewReasonDict(TypedDict):
    category: str
    message: str
    source: str


class AuditEntryDict(TypedDict):
    taskId: str
    timestamp: str
    agent: str
    stage: str
    detail: str


class AgentStepDict(TypedDict):
    name: str
    description: str
    state: AgentState
