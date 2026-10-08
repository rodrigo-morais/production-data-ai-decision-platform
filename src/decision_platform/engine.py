from __future__ import annotations

from collections.abc import Awaitable, Callable

from decision_platform.classifiers import Classifier
from decision_platform.contracts import (
    DecisionOutcome,
    DecisionStatus,
    ExecutionPolicy,
    Opportunity,
)
from decision_platform.evals import evaluate
from decision_platform.routing import route_model
from decision_platform.scoring import score_with_service
from decision_platform.telemetry import JsonlTelemetry


class DecisionEngine:
    def __init__(
        self,
        classifier: Classifier,
        policy: ExecutionPolicy,
        telemetry: JsonlTelemetry,
        scoring_url: str,
        fallback: Callable[[Opportunity], Awaitable[Opportunity]] | None = None,
    ) -> None:
        self.classifier = classifier
        self.policy = policy
        self.telemetry = telemetry
        self.scoring_url = scoring_url
        self.fallback = fallback

    async def run(self, opportunity: Opportunity) -> DecisionOutcome:
        graph = ["ingest"]
        candidate = opportunity
        if candidate.source_coverage < self.policy.min_source_coverage and self.fallback:
            graph.append("fallback")
            candidate = await self.fallback(candidate)

        graph.append("validate")
        decision = await self.classifier.classify(candidate)
        graph.append("classify")
        route = route_model(candidate, decision)
        graph.append(f"route:{route.name}")
        operational_score = await score_with_service(candidate, self.scoring_url)
        graph.append("score")
        evaluation = evaluate(candidate, decision, self.policy)
        graph.append("evaluate")

        passed = (
            candidate.source_coverage >= self.policy.min_source_coverage
            and evaluation.score >= self.policy.min_evaluation_score
            and decision.confidence >= self.policy.min_classifier_confidence
        )
        status = DecisionStatus.RELEASED if passed else DecisionStatus.REVIEW
        graph.append(f"gate:{status.value}")

        outcome = DecisionOutcome(
            opportunity_id=candidate.id,
            status=status,
            decision=decision,
            evaluation=evaluation,
            route=route.name,
            operational_score=operational_score,
            graph=graph,
        )
        self.telemetry.emit(
            "decision_completed",
            {
                "opportunity_id": candidate.id,
                "status": status.value,
                "route": route.name,
                "evaluation_score": evaluation.score,
                "attributes": candidate.attributes,
            },
        )
        return outcome
