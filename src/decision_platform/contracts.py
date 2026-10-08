from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Risk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Priority(StrEnum):
    OBSERVE = "observe"
    INVESTIGATE = "investigate"
    ACT = "act"


class DecisionStatus(StrEnum):
    RELEASED = "released"
    REVIEW = "review"


class Opportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=4, max_length=120)
    description: str = Field(min_length=10, max_length=2_000)
    source: str = Field(min_length=2, max_length=80)
    source_coverage: float = Field(ge=0, le=1)
    evidence_count: int = Field(ge=0, le=10_000)
    impact: float = Field(ge=0, le=1)
    urgency: float = Field(ge=0, le=1)
    complexity: float = Field(ge=0, le=1)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    attributes: dict[str, Any] = Field(default_factory=dict)


class TypedDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priority: Priority
    risk: Risk
    confidence: float = Field(ge=0, le=1)
    rationale: str = Field(min_length=4, max_length=500)
    classifier: str


class EvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0, le=1)
    checks: dict[str, bool]
    failures: list[str] = Field(default_factory=list)


class DecisionOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: UUID
    status: DecisionStatus
    decision: TypedDecision
    evaluation: EvaluationResult
    route: str
    operational_score: float = Field(ge=0, le=1)
    graph: list[str]
    released_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExecutionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    min_source_coverage: float = Field(default=0.95, ge=0, le=1)
    min_classifier_confidence: float = Field(default=0.75, ge=0, le=1)
    min_evaluation_score: float = Field(default=0.80, ge=0, le=1)
    minimum_evidence: int = Field(default=3, ge=1)
    max_attempts: int = Field(default=2, ge=1, le=5)
    timeout_seconds: float = Field(default=20.0, gt=0, le=120)

    @model_validator(mode="after")
    def retries_require_a_timeout(self) -> ExecutionPolicy:
        if self.max_attempts > 1 and self.timeout_seconds <= 0:
            raise ValueError("retries require a positive timeout")
        return self
