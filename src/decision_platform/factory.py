from decision_platform.classifiers import JevTypedClassifier, LocalTypedClassifier
from decision_platform.config import Settings
from decision_platform.engine import DecisionEngine
from decision_platform.fallbacks import synthetic_fallback
from decision_platform.telemetry import JsonlTelemetry


def build_engine(settings: Settings) -> DecisionEngine:
    classifier = (
        JevTypedClassifier(settings.jev_base_url, settings.jev_api_key)
        if settings.jev_enabled
        else LocalTypedClassifier()
    )
    return DecisionEngine(
        classifier=classifier,
        policy=settings.policy(),
        telemetry=JsonlTelemetry(settings.telemetry_path),
        scoring_url=settings.scoring_url,
        fallback=synthetic_fallback,
    )
