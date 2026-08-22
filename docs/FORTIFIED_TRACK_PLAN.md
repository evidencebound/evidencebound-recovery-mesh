# Fortified Enterprise Fleet — plan and current scorecard

> **Status:** This document began as the 2026-08-14 implementation plan. It is retained for design rationale, but the current submission state is summarized below. For judge-facing production facts, prefer `README.md`, `docs/JUDGE_TESTING_INSTRUCTIONS.md`, `docs/PROOF_OF_ACTION_VIDEO.md`, and `docs/SUBMISSION_PREFLIGHT_2026-08-15.md`.

Recovery Mesh is the fleet-integrity and selective-recovery plane: a deterministic trust graph surrounds a four-role Google ADK/Gemini agent fleet and prevents one broken checkpoint from forcing a blind whole-fleet restart.

## Current Fortified scorecard

| Fortified concern | Current Recovery Mesh evidence | Status |
|---|---|---|
| Multi-agent orchestration | four separated ADK roles + deterministic dependency graph | LIVE / VERIFIED |
| Corporate discovery/catalog | Google Agent Registry Service + generated read-only Agent | LIVE / VERIFIED |
| Runtime security | Cloud Run identities, protected judge API, Secret Manager, WIF | LIVE / VERIFIED |
| Failure containment | exact DAG blast radius + fail-closed `publish_action` | LIVE / VERIFIED |
| Selective recovery | 3 affected agents rerun, Scout reused | LIVE / VERIFIED |
| Auditability | Flight Recorder causal events + historical break/reuse markers | LIVE / VERIFIED |
| Scale behavior | deterministic 100-checkpoint probe: 14 affected / 86 reused / 1 blocked | VERIFIED SYNTHETIC GRAPH PROBE |
| Long-term cross-session state | current run store is process-local | NOT CLAIMED |
| Multi-week asynchronous context | not demonstrated by current runtime | NOT CLAIMED |
| Enterprise production data | bounded controlled fixtures only | NOT CLAIMED AS LIVE ENTERPRISE DATA |
| Agent Runtime / Memory Bank / Model Armor / Gateway / Identity | no separately verified integration | NOT CLAIMED |

## Gate A — core production proof — COMPLETE

The original plan required the core Google production path to pass before any enterprise add-on could be promoted.

Current evidence:

```text
Cloud Run revision: evidencebound-recovery-mesh-00005-82k
Provider: google_adk_vertex
Model: gemini-3.5-flash
Google ADK: 2.7.0
Protected API: unauthenticated POST /api/runs -> 401
Live baseline: 4 agents
Trust break: history_snapshot
Blocked action: publish_action
Reused work: scout
Selective recovery: 3 rerun / 1 reused
Final action: VERIFIED
```

## Gate B — Google Agent Registry — COMPLETE

The fleet entry point is registered as a standard REST service and the Google-generated read-only Agent projection was observed before PASS:

```text
Workflow: 31871557186
AGENT_REGISTRY=PASS
AGENT_REGISTRY_SERVICE=projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
AGENT_REGISTRY_AGENT=projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_INTERFACE=https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app
AGENT_REGISTRY_DISCOVERY=PASS
```

This is catalog/discovery evidence only. The Registry does not authorize Recovery Mesh trust state and the four internal ADK roles are not claimed as separately registered agents.

## Gate C — durable cross-session trust state — NOT IMPLEMENTED

The current demo runs are process-local. That proves the causal recovery vertical slice but does not prove context surviving weeks of asynchronous institutional work.

Any future durable implementation must preserve these constraints:

- storage existence never implies `VERIFIED`;
- persisted records are revalidated on read;
- original failure/invalidation history is retained rather than overwritten;
- restart-surviving idempotency must be verified before any durable exactly-once claim;
- Memory Bank, if evaluated later, is advisory context rather than immutable trust authority.

Firestore or another durable Google Cloud store remains a possible extension target, not an active submission integration.

## Gate D — optional Gemini Enterprise Agent Platform services — NOT CLAIMED

Agent Runtime, Memory Bank, Agent Identity, Agent Gateway, Model Armor, and enterprise Agent Observability are not promoted into the live architecture without a real resource/invocation receipt.

That constraint is deliberate. Recovery Mesh must not describe a Google service as detecting policy drift, prompt poisoning, or trust failure unless that service actually produced the corresponding result.

## Architectural thesis

The important separation remains:

```text
Gemini / ADK reasoning
        ↓ advisory bounded output
Deterministic checkpoint verification
        ↓
Trust Graph + exact blast radius
        ↓
Fail-closed action gate
        ↓
Selective recomputation
        ↓
Re-verification before resume
```

Persisted memory, Agent Registry metadata, or model assertions cannot override this authority chain.

## Current judge positioning

Recovery Mesh strongly demonstrates discovery, multi-agent orchestration, observability of causal recovery, security posture, fail-closed action, and selective self-healing. The submission explicitly discloses that it does **not** demonstrate durable multi-week context or live enterprise production-data integration.

This honest boundary should remain visible unless a future implementation is separately built, tested, deployed, and verified before the submission deadline.
