from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from decision_platform.contracts import ExecutionPolicy


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    decision_env: str = "development"
    jev_enabled: bool = False
    jev_base_url: str = "https://jevtypesafeai.com/api/v1/decide"
    jev_api_key: str = ""
    min_source_coverage: float = Field(default=0.95, ge=0, le=1)
    min_classifier_confidence: float = Field(default=0.75, ge=0, le=1)
    min_evaluation_score: float = Field(default=0.80, ge=0, le=1)
    scoring_url: str = "http://scoring:8081"
    telemetry_path: str = "/tmp/decision-platform-telemetry.jsonl"

    def policy(self) -> ExecutionPolicy:
        return ExecutionPolicy(
            min_source_coverage=self.min_source_coverage,
            min_classifier_confidence=self.min_classifier_confidence,
            min_evaluation_score=self.min_evaluation_score,
        )
