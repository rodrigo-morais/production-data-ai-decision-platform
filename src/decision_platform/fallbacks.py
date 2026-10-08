from decision_platform.contracts import Opportunity


async def synthetic_fallback(opportunity: Opportunity) -> Opportunity:
    """Simulates a second provider improving coverage without changing identity."""
    return opportunity.model_copy(
        update={
            "source": f"{opportunity.source}+fallback",
            "source_coverage": max(opportunity.source_coverage, 0.98),
            "evidence_count": max(opportunity.evidence_count, 4),
        }
    )
