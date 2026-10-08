from prefect import flow, task

from decision_platform.config import Settings
from decision_platform.contracts import DecisionOutcome, Opportunity
from decision_platform.factory import build_engine


@task(retries=2, retry_delay_seconds=2, timeout_seconds=20)
async def evaluate_opportunity(opportunity: Opportunity) -> DecisionOutcome:
    return await build_engine(Settings()).run(opportunity)


@flow(name="typed-decision-flow", log_prints=True)
async def typed_decision_flow(opportunity: Opportunity) -> DecisionOutcome:
    """Prefect wrapper for scheduled, ad-hoc, or event-triggered execution."""
    return await evaluate_opportunity(opportunity)
