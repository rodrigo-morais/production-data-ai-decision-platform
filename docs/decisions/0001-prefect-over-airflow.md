# Prefect for dynamic Python workflows

## Status

Accepted

## Context

The reference workload is Python-heavy, runs on schedules and demand, and benefits from dynamic branching. A small team should be able to operate it without maintaining a large orchestration control plane.

## Decision

Use Prefect as the orchestration adapter and keep the decision engine independent from it.

## Consequences

Python development remains fast, ad-hoc execution is straightforward, and infrastructure stays small. Teams with an established Airflow platform or a broad estate of static DAGs may reasonably choose Airflow instead.
