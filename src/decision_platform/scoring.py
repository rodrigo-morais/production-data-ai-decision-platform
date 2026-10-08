from __future__ import annotations

import httpx

from decision_platform.contracts import Opportunity


def local_score(opportunity: Opportunity) -> float:
    score = (
        0.45 * opportunity.impact
        + 0.35 * opportunity.urgency
        + 0.20 * opportunity.source_coverage
    )
    return round(max(0.0, min(1.0, score)), 4)


async def score_with_service(opportunity: Opportunity, scoring_url: str) -> float:
    payload = {
        "impact": opportunity.impact,
        "urgency": opportunity.urgency,
        "coverage": opportunity.source_coverage,
    }
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            response = await client.post(f"{scoring_url.rstrip('/')}/score", json=payload)
            response.raise_for_status()
            return float(response.json()["score"])
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return local_score(opportunity)
