# Pre-existing work disclosure

EvidenceBound Recovery Mesh is a new project created during the Google All Things Agentic
Hackathon 2026 submission period (which began 2026-08-03).

## Pre-existing concepts and references

Before this hackathon, the author had built and discussed other projects including:

- EvidenceBound verification/provenance patterns and "Verified Memory" experiments.
- SignalReview, a sports-intelligence application with multi-agent debate concepts.
- A separate EvidenceBound Verified Memory project for a different hackathon.

These pre-existing projects informed the problem selection and vocabulary around evidence,
provenance, policy, verification, and multi-agent roles.

## Code boundary

Recovery Mesh core implementation in this repository is clean-room code written for this
hackathon. No SignalReview production source is copied into this repository. No source from
the earlier EvidenceBound Verified Memory repository is copied into the Recovery Mesh core.
Any future optional adapter must be isolated, minimal, license-compatible, and explicitly
listed here before submission.

## Submission claim boundary

The submitted work is the Recovery Mesh implementation: deterministic trust graph,
checkpoint contracts, invalidation/blast-radius semantics, selective recovery, fail-closed
action gating, idempotency, Google ADK/Gemini integration, Flight Recorder, benchmark, and
Google Cloud deployment built during this hackathon period.
