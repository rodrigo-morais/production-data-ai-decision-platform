from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from decision_platform import __version__
from decision_platform.config import Settings
from decision_platform.contracts import DecisionOutcome, Opportunity
from decision_platform.factory import build_engine

DECISIONS = Counter("decision_requests_total", "Decision requests", ["status", "route"])
LATENCY = Histogram("decision_duration_seconds", "Decision request latency")

settings = Settings()
engine = build_engine(settings)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title="Production Data and AI Decision Platform",
    version=__version__,
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/decisions", response_model=DecisionOutcome)
async def decide(opportunity: Opportunity) -> DecisionOutcome:
    with LATENCY.time():
        outcome = await engine.run(opportunity)
    DECISIONS.labels(status=outcome.status.value, route=outcome.route).inc()
    return outcome
