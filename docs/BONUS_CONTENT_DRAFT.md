# Bonus contribution drafts

These are drafts only. Publishing them is an external side effect and is not claimed until a public URL is added to the Devpost submission.

## Public technical article draft

### Trust-Aware Recovery in Agent Fleets: Why Restarting Everything Is the Wrong Default

I created this article for the purposes of entering the Google All Things Agentic Hackathon 2026.

Autonomous agent systems fail differently from ordinary services. A single stale evidence record, malformed worker output, poisoned tool result, or policy change can contaminate downstream state even when most of the fleet's earlier work is still valid.

EvidenceBound Recovery Mesh treats that as a trust-graph problem rather than a process-restart problem.

Each material step becomes a checkpoint with explicit dependencies, output digests, evidence/tool digests, policy version, provenance, integrity metadata, and a deterministic verification state. When a trust break is detected, the runtime freezes unsafe downstream action, traverses the dependency graph, computes the exact blast radius, preserves checkpoints that remain verifiable, and reruns only the affected branch.

The key design choice is that the language model is not the source of truth for trust. Gemini agents can analyze evidence and return bounded structured output, but deterministic code decides whether a checkpoint is VERIFIED, INVALIDATED, RECOMPUTE, or BLOCKED. The model cannot override policy, provenance, integrity, or side-effect gates.

In the production acceptance run on Google Cloud, four Google ADK agents used Gemini 3.5 Flash through Vertex AI. A controlled stale-evidence fault invalidated the history snapshot and blocked the publish action. Scout remained reusable while Statistician, Skeptic, and Orchestrator were selectively recomputed. The final action resumed only after deterministic re-verification.

Measured on that controlled run:

- Full restart: 4 model calls / 1781 input tokens
- Selective recovery: 3 model calls / 1358 input tokens
- Saved: 1 model call / 423 input tokens, about 24% of input tokens for that run

This is not a general savings claim. It is a measured receipt from one bounded production scenario.

The broader lesson is simple: persisted state should not be treated as trusted state merely because it exists. For autonomous fleets, recovery should preserve only work whose evidence, provenance, dependencies, integrity, and policy context are still verifiable.

Project: EvidenceBound Recovery Mesh
Hackathon: Google All Things Agentic Hackathon 2026
Category: Fortified Enterprise Fleet

## LinkedIn / X draft

Built **EvidenceBound Recovery Mesh** for the Google All Things Agentic Hackathon 2026: a trust-aware flight recorder and selective self-healing engine for autonomous agent fleets.

Production judge flow on Google Cloud:
TRUST BREAK → BLAST RADIUS → ACTION BLOCKED → SAFE WORK REUSED → AFFECTED BRANCH RECOMPUTED → VERIFIED RECOVERY.

Live stack: Google ADK + Vertex AI / Gemini 3.5 Flash + Cloud Run.

Controlled production benchmark: full restart 4 model calls / 1781 input tokens vs selective recovery 3 calls / 1358 input tokens — 1 call and 423 input tokens saved in that measured run.

#AllThingsAgenticHackathon
