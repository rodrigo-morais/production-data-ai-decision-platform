# Fail closed at the release boundary

## Status

Accepted

## Context

Classifiers and language models can produce plausible output when evidence is weak or source data is incomplete.

## Decision

Release a decision only when data coverage, typed confidence, evidence, and evaluation score satisfy explicit policy. Route every other result to review.

## Consequences

Low-confidence work stays visible without becoming an automatic action. Thresholds can be versioned and tested independently from model prompts.
