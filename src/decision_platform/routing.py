from dataclasses import dataclass

from decision_platform.contracts import Opportunity, Risk, TypedDecision


@dataclass(frozen=True)
class ModelRoute:
    name: str
    reason: str
    relative_cost: float


def route_model(opportunity: Opportunity, decision: TypedDecision) -> ModelRoute:
    if decision.risk is Risk.HIGH or opportunity.complexity >= 0.8:
        return ModelRoute("frontier", "High risk or complexity requires the strongest model.", 1.0)
    if decision.confidence < 0.82 or opportunity.complexity >= 0.45:
        return ModelRoute("balanced", "Moderate uncertainty needs a balanced model.", 0.35)
    return ModelRoute(
        "fast",
        "High-confidence, low-complexity decision uses the economical route.",
        0.08,
    )
