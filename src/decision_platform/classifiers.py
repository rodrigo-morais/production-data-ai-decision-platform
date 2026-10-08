from __future__ import annotations

from typing import Any, Protocol

import httpx

from decision_platform.contracts import Opportunity, Priority, Risk, TypedDecision


class Classifier(Protocol):
    async def classify(self, opportunity: Opportunity) -> TypedDecision: ...


class LocalTypedClassifier:
    """Deterministic classifier used for local development and reproducible tests."""

    async def classify(self, opportunity: Opportunity) -> TypedDecision:
        weighted = 0.55 * opportunity.impact + 0.45 * opportunity.urgency
        priority = (
            Priority.ACT
            if weighted >= 0.72
            else Priority.INVESTIGATE
            if weighted >= 0.42
            else Priority.OBSERVE
        )
        risk = (
            Risk.HIGH
            if opportunity.complexity >= 0.75
            else Risk.MEDIUM
            if opportunity.complexity >= 0.4
            else Risk.LOW
        )
        confidence = min(
            0.99,
            0.55
            + 0.25 * opportunity.source_coverage
            + 0.02 * min(10, opportunity.evidence_count),
        )
        return TypedDecision(
            priority=priority,
            risk=risk,
            confidence=confidence,
            rationale=(
                "Deterministic classification from impact, urgency, complexity, coverage, "
                "and evidence."
            ),
            classifier="local-typed-v1",
        )


class JevTypedClassifier:
    """Optional adapter for Jev's typed choice, score, and yes/no decisions."""

    def __init__(self, base_url: str, api_key: str, timeout_seconds: float = 5.0) -> None:
        if not api_key:
            raise ValueError("JEV_API_KEY is required when Jev is enabled")
        self.base_url = base_url
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    async def classify(self, opportunity: Opportunity) -> TypedDecision:
        payload: dict[str, Any] = {
            "state": opportunity.model_dump(mode="json"),
            "questions": [
                {
                    "type": "choice",
                    "key": "priority",
                    "question": "What operational priority should this opportunity receive?",
                    "options": [item.value for item in Priority],
                },
                {
                    "type": "choice",
                    "key": "risk",
                    "question": "What is the operational risk?",
                    "options": [item.value for item in Risk],
                },
                {
                    "type": "noul",
                    "key": "release_confidence",
                    "question": "Is the evidence strong enough to release this decision?",
                },
            ],
        }
        headers = {"authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()

        values = body.get("values", body)
        return TypedDecision(
            priority=Priority(values["priority"]),
            risk=Risk(values["risk"]),
            confidence=float(values["release_confidence"]),
            rationale="Typed decision returned by Jev and normalized to the platform contract.",
            classifier="jev",
        )
