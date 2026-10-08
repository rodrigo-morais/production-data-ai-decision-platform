from decision_platform.contracts import (
    EvaluationResult,
    ExecutionPolicy,
    Opportunity,
    TypedDecision,
)


def evaluate(
    opportunity: Opportunity,
    decision: TypedDecision,
    policy: ExecutionPolicy,
) -> EvaluationResult:
    checks = {
        "source_coverage": opportunity.source_coverage >= policy.min_source_coverage,
        "classifier_confidence": decision.confidence >= policy.min_classifier_confidence,
        "evidence": opportunity.evidence_count >= policy.minimum_evidence,
        "rationale": len(decision.rationale.strip()) >= 12,
        "typed_output": bool(decision.priority.value and decision.risk.value),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return EvaluationResult(
        score=sum(checks.values()) / len(checks),
        checks=checks,
        failures=failures,
    )
