# Devpost Submission Matrix — All Things Agentic Hackathon 2026

Canonical project: **EvidenceBound Recovery Mesh**  
Category: **Fortified Enterprise Fleet**  
Project start answer: **08-14-26**  
Devpost project: `evidencebound-recovery-mesh`  
Submission ID: `1136853`

> Current-state document. A field is listed as implemented/used only when backed by repository, production, or Devpost evidence.

## Final submission state

| Devpost field | Submitted answer / state | Evidence status |
|---|---|---|
| Submitter Type | `Team of individuals` | SUBMITTED |
| Country | `Ukraine` | SUBMITTED |
| Category | `Fortified Enterprise Fleet` | SUBMITTED |
| Startup Prize organization/email | blank | INTENTIONALLY NOT CLAIMED; submission is not on behalf of an incorporated organization |
| Public code repository | `https://github.com/moneyparking/evidencebound-recovery-mesh` | PASS |
| Reproducible README | `Yes` | PASS |
| Hosted project URL | `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/` | LIVE |
| Private judge testing instructions | private Devpost field + public detailed runbook | OWNER-VISIBLE; credential must remain private |
| Google SDK | `Agent Development Kit (ADK)` | LIVE / VERIFIED |
| Google Cloud service answer | `Cloud Run` | LIVE / VERIFIED |
| Google AI model | `Gemini 3.5 Flash via Vertex AI` | LIVE / VERIFIED |
| Architecture diagram | Architecture Diagram v2 | UPLOADED / VERIFIED AGAINST CURRENT ARCHITECTURE |
| Demo video | `https://youtu.be/AExuVCC-m7o` | PUBLIC / SUBMITTED |
| Bonus technical article | DEV.to URL supplied in Devpost | SUBMITTED |
| Bonus social post | LinkedIn URL with `#AllThingsAgenticHackathon` | SUBMITTED |

The Devpost gallery images are presentation assets rather than runtime evidence; they must not introduce capabilities that are absent from the live system.

## Current production evidence

Production service:

```text
Project: evidencebound-rm-c977c1
Cloud Run revision: evidencebound-recovery-mesh-00005-82k
Hosted URL: https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/
Health endpoint: /health
Provider: google_adk_vertex
Model: gemini-3.5-flash
Google ADK: 2.7.0
```

Verified judge path:

```text
4 live ADK agents
TRUST BREAK: history_snapshot
ACTION BLOCKED: publish_action
SAFE WORK REUSED: scout
SELECTIVE RECOVERY: statistician + skeptic + orchestrator rerun
FINAL ACTION: VERIFIED
```

Protected production API evidence includes unauthenticated `POST /api/runs -> 401` before model execution.

## Measured receipts

Current submission-ready revision smoke:

```text
Full restart:        4 model calls / 1728 input tokens
Selective recovery: 3 model calls / 1393 input tokens
Saved:               1 model call / 335 input tokens (~19%)
```

Fresh browser/video capture:

```text
Run:                 run-72e5ad9cd0e8
Full restart:        4 model calls / 1788 input tokens
Selective recovery: 3 model calls / 1427 input tokens
Saved:               1 model call / 361 input tokens (20%)
```

Reference production acceptance:

```text
Run:                 run-4707af5a2fb6
Full restart:        4 model calls / 1781 input tokens
Selective recovery: 3 model calls / 1358 input tokens
Saved:               1 model call / 423 input tokens (~24%)
```

These are controlled-run measurements, not universal savings claims. Gemini token usage varies across runs.

## Verified Google Agent Registry evidence

```text
AGENT_REGISTRY=PASS
AGENT_REGISTRY_SERVICE=projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
AGENT_REGISTRY_AGENT=projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_INTERFACE=https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app
AGENT_REGISTRY_DISCOVERY=PASS
Workflow: 31871557186
```

The Registry entry represents the Recovery Mesh fleet entry point. The submission does not claim separate Registry entries for the four internal ADK roles.

## New-project boundary

Recovery Mesh is a new isolated hackathon repository. Pre-existing EvidenceBound verification/provenance ideas and SignalReview concepts are disclosed in `PREEXISTING_WORK.md`. No SignalReview production source or prior EvidenceBound implementation source is copied into the Recovery Mesh core.

## Explicit non-claims

The live submission uses a bounded process-local hot store. It does **not** claim:

- durable multi-week context;
- Firestore persistence;
- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- durable exactly-once semantics across process restart;
- 100 live Gemini agents in the synthetic scale probe.

## Remaining owner-visible presentation item

The invited teammate must accept the Devpost project invite and appear in the project roster before the end of the submission period if the project is presented as a team submission.

Everything else in this matrix describes the current submitted/verified state, not the earlier bootstrap plan.
