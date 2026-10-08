import pytest

from decision_platform.classifiers import LocalTypedClassifier
from decision_platform.contracts import Opportunity
from decision_platform.routing import route_model


@pytest.mark.asyncio
async def test_high_complexity_uses_frontier_route() -> None:
    opportunity = Opportunity(
        title="Complex synthetic signal",
        description="A synthetic case with high operational complexity.",
        source="fixture",
        source_coverage=0.99,
        evidence_count=7,
        impact=0.8,
        urgency=0.7,
        complexity=0.9,
    )
    decision = await LocalTypedClassifier().classify(opportunity)
    assert route_model(opportunity, decision).name == "frontier"
