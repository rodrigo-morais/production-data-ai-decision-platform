# Architecture

## Purpose

The platform converts an operational signal into a typed decision while keeping uncertain model output away from external side effects. It is intentionally small enough to run locally and structured enough to demonstrate production boundaries.

## Control plane

FastAPI accepts a strict `Opportunity` contract. The decision engine checks source coverage, invokes a typed classifier, chooses a model tier, requests an operational score, runs evaluations, and releases the result only when every required threshold passes.

Prefect wraps the same engine for scheduled, event-driven, and ad-hoc execution. The business logic does not depend on Prefect, which keeps orchestration replaceable and unit tests fast.

## Typed judgment

The local classifier makes the project reproducible without external services. The Jev adapter demonstrates how a hosted typed-decision model can replace that classifier without changing downstream contracts. Both return enum-backed priority and risk values plus calibrated confidence.

## Scoring service

The Go service owns one small, deterministic scoring boundary. The Python client uses a one-second timeout and falls back to the same local formula if the service is unavailable. This makes the failure behavior visible and testable.

## Release gate

The release gate checks source coverage, evidence count, classifier confidence, rationale presence, and typed output. A failed check produces `review`; it does not disappear and it does not silently release an action.

## Telemetry

Each completed run emits a compact JSON event. Known sensitive keys are redacted recursively. The example records state transitions and outcomes, not hidden reasoning or raw prompts.
