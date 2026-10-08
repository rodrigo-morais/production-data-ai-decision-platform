import pytest
from pydantic import ValidationError

from decision_platform.contracts import Opportunity


def test_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Opportunity(
            title="Synthetic signal",
            description="Long enough synthetic description.",
            source="fixture",
            source_coverage=1,
            evidence_count=4,
            impact=0.5,
            urgency=0.5,
            complexity=0.5,
            unexpected=True,
        )


def test_rejects_out_of_range_coverage() -> None:
    with pytest.raises(ValidationError):
        Opportunity(
            title="Synthetic signal",
            description="Long enough synthetic description.",
            source="fixture",
            source_coverage=1.2,
            evidence_count=4,
            impact=0.5,
            urgency=0.5,
            complexity=0.5,
        )
