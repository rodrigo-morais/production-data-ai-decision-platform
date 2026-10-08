from pathlib import Path

import pytest

from decision_platform.classifiers import LocalTypedClassifier
from decision_platform.contracts import DecisionStatus, ExecutionPolicy, Opportunity
from decision_platform.engine import DecisionEngine
from decision_platform.fallbacks import synthetic_fallback
from decision_platform.telemetry import JsonlTelemetry


def opportunity(**changes: object) -> Opportunity:
    base: dict[str, object] = {
        "title": "Synthetic operational signal",
        "description": "A synthetic signal used to verify the public decision platform.",
        "source": "fixture",
        "source_coverage": 0.99,
        "evidence_count": 5,
        "impact": 0.8,
        "urgency": 0.75,
        "complexity": 0.5,
    }
    base.update(changes)
    return Opportunity.model_validate(base)


@pytest.mark.asyncio
async def test_releases_a_well_supported_decision(tmp_path: Path) -> None:
    engine = DecisionEngine(
        classifier=LocalTypedClassifier(),
        policy=ExecutionPolicy(),
        telemetry=JsonlTelemetry(str(tmp_path / "events.jsonl")),
        scoring_url="http://unavailable.invalid",
    )
    result = await engine.run(opportunity())
    assert result.status is DecisionStatus.RELEASED
    assert result.graph[-1] == "gate:released"
    assert result.route in {"fast", "balanced", "frontier"}


@pytest.mark.asyncio
async def test_fails_closed_when_coverage_is_low(tmp_path: Path) -> None:
    engine = DecisionEngine(
        classifier=LocalTypedClassifier(),
        policy=ExecutionPolicy(),
        telemetry=JsonlTelemetry(str(tmp_path / "events.jsonl")),
        scoring_url="http://unavailable.invalid",
    )
    result = await engine.run(opportunity(source_coverage=0.5))
    assert result.status is DecisionStatus.REVIEW
    assert "source_coverage" in result.evaluation.failures


@pytest.mark.asyncio
async def test_fallback_can_recover_coverage(tmp_path: Path) -> None:
    engine = DecisionEngine(
        classifier=LocalTypedClassifier(),
        policy=ExecutionPolicy(),
        telemetry=JsonlTelemetry(str(tmp_path / "events.jsonl")),
        scoring_url="http://unavailable.invalid",
        fallback=synthetic_fallback,
    )
    result = await engine.run(opportunity(source_coverage=0.5, evidence_count=0))
    assert result.status is DecisionStatus.RELEASED
    assert "fallback" in result.graph
