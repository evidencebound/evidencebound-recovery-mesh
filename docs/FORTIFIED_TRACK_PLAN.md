# Fortified Enterprise Fleet — current-track plan

Status date: 2026-08-14. This document separates current official track expectations from verified implementation evidence. It is a plan, not a claim that enterprise-agent services are live.

## Why this exists

The current All Things Agentic Fortified Enterprise Fleet description expects more than a secure single agent. It emphasizes a centrally governed institutional fleet: discoverability/cataloging, persistent context across asynchronous work, secure runtime identity and access, observability, and safe interaction with production data.

Recovery Mesh already supplies the deterministic trust/recovery layer. The Google enterprise services below are considered only where they materially strengthen the judge proof; none is claimed until a real invocation/resource receipt exists.

## Phase ordering

### Gate A — core production proof (must pass first)

1. isolated hackathon project billing enabled;
2. live Gemini 3.5+ preflight;
3. Google ADK four-role baseline;
4. Cloud Run deployment with bounded runtime/build identities;
5. Secret Manager protected judge API;
6. exact trust-break / blast-radius / blocked-action / selective-recovery smoke;
7. Cloud Run proof receipt.

A failure at Gate A blocks every later enterprise add-on. Do not mask it by adding more services.

### Gate B — Agent Registry discovery (prepared, not live)

After Gate A succeeds, enable and test Agent Registry. `scripts/register-agent-registry.sh` is prepared to manually register the Cloud Run Recovery Mesh fleet controller as a **standard REST agent** in `global` and then wait for the read-only discoverable Agent projection.

Why this is material:

- gives the fleet a Google-managed discovery/catalog entry rather than only a README/UI catalog;
- creates a concrete cross-department discovery proof for the Fortified track;
- preserves the current Cloud Run architecture instead of forcing an unverified runtime migration;
- does not misrepresent the four internal worker roles as separately network-addressable agents.

Required live receipt before claiming it:

```text
AGENT_REGISTRY=PASS ...
AGENT_REGISTRY_SERVICE=...
AGENT_REGISTRY_AGENT=...
AGENT_REGISTRY_INTERFACE=https://...
```

The script intentionally fails if it observes only the writable Service but not the read-only Agent projection.

### Gate C — durable cross-session trust state (decision after Gate A)

Current demo runs are process-local. That is sufficient for the causal vertical slice but is not yet evidence of context surviving weeks of asynchronous institutional work.

After Gate A, choose the smallest durable implementation that preserves EvidenceBound semantics:

- preferred trust ledger: Firestore or another Google Cloud durable store for checkpoint/event snapshots;
- persisted data is always revalidated on read; storage existence never implies `VERIFIED`;
- retain original failure/invalidation history instead of overwriting it;
- idempotency keys must survive process restart before claiming durable exactly-once behavior.

Do not call Memory Bank an immutable or authoritative trust ledger. If Memory Bank entitlement is available, it can be evaluated only as advisory long-term agent context while deterministic checkpoint trust remains EvidenceBound-owned.

### Gate D — optional Gemini Enterprise Agent Platform services

Inspect actual entitlement and runtime behavior only after Gate A. Candidate services:

- Agent Runtime: only if moving a worker or orchestration boundary there materially improves the judge proof without destabilizing Cloud Run;
- Memory Bank: advisory contextual memory only, never automatic trusted memory;
- Agent Identity / Agent Gateway: only if a real cross-agent/resource authorization path exists;
- Agent Observability: only if actual traces/logs improve the Flight Recorder proof;
- Model Armor: only for documented/observed supported security behavior, never described as a generic policy-drift detector.

No service enters the architecture diagram merely because it is recommended by the track.

## Judge mapping

| Fortified concern | Recovery Mesh evidence | Google-managed evidence target |
|---|---|---|
| Multi-agent fleet | four separated ADK roles + deterministic dependency graph | live ADK receipts |
| Central catalog | role catalog in workload/Flight Recorder | Agent Registry discoverable fleet entry |
| Runtime security | fail-closed judge API, secret-backed key, model-call guard | Cloud Run runtime identity + Secret Manager |
| Blast-radius containment | exact DAG descendants + reusable set | live production run/log receipt |
| Persistent context | checkpoint schema/version/provenance semantics | durable store only after Gate A |
| Asynchronous recovery | deterministic recompute plan/idempotency | durable state/long-running service only if verified |
| Observability | Flight Recorder causal events | Cloud Run logs; enterprise observability only if actually integrated |
| Cross-department governance | deterministic policy/provenance gates | Registry discovery + IAM evidence |

## Non-claims until proven

- no Agent Registry PASS until the real projected Agent exists;
- no Agent Runtime or Memory Bank usage until a real resource/invocation exists;
- no weeks-long persistence claim while the runtime remains process-local;
- no durable exactly-once claim while the idempotency ledger remains process-local;
- no enterprise security service credit for behavior implemented solely by EvidenceBound.
