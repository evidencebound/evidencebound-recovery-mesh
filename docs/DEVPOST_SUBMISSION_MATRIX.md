# Devpost Submission Matrix — All Things Agentic Hackathon 2026

Canonical project: **EvidenceBound Recovery Mesh**  
Category: **Fortified Enterprise Fleet**  
Devpost project: `evidencebound-recovery-mesh`  
Submission ID: `1136853`

> Current-state document. A field is listed as implemented/used only when backed by repository, production, or live Devpost evidence.

## Current submission state — 2026-08-28

| Devpost field | Submitted answer / state | Evidence status |
|---|---|---|
| Submitter Type | `Team of individuals` | SUBMITTED |
| Country | `Ukraine` | SUBMITTED |
| Category | `Fortified Enterprise Fleet` | SUBMITTED |
| Startup Prize organization/email | blank | INTENTIONALLY NOT CLAIMED |
| Public code repository | `https://github.com/evidencebound/evidencebound-recovery-mesh` | LIVE / READ BACK |
| Reproducible README | `Yes` | PASS |
| Hosted project URL | `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/` | LIVE / VERIFIED BY CURRENT ACCEPTANCE |
| Preferred judge route | `?autorun=stale_evidence&recover=1` | HANDS-OFF / VERIFIED |
| Private judge testing instructions | private Devpost field + public detailed runbook | OWNER-VISIBLE; credential remains private |
| Google SDK | `Agent Development Kit (ADK)` | LIVE / VERIFIED |
| Google Cloud service answer | `Cloud Run` | LIVE / VERIFIED |
| Google AI model | `Gemini 3.5 Flash via Vertex AI` | LIVE / VERIFIED |
| Architecture diagram | Architecture Diagram v2 | UPLOADED / VERIFIED AGAINST CURRENT ARCHITECTURE |
| Demo video | `https://youtu.be/AExuVCC-m7o` | V1 PUBLIC / CURRENT DEVPOST VIDEO |
| Video V2 | 75.080 s publication-ready master | LOCAL ASSEMBLY VERIFIED / PUBLICATION PENDING |
| Bonus technical article | DEV.to URL supplied in Devpost | SUBMITTED |
| Bonus social post | LinkedIn URL with `#AllThingsAgenticHackathon` | SUBMITTED |

The Devpost gallery images are presentation assets rather than runtime evidence; they must not introduce capabilities absent from the live system.

## Current production evidence

```text
Project:              evidencebound-rm-c977c1
Cloud Run revision:   evidencebound-recovery-mesh-00006-tc4
Hosted URL:           https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/
Canonical .run.app:   https://evidencebound-recovery-mesh-457699623691.europe-west1.run.app
Health endpoint:      /health
Provider:             google_adk_vertex
Model:                gemini-3.5-flash
Google ADK:           2.7.0
Acceptance workflow:  32817763402
Acceptance run:       run-6d1427ccb2ca
```

Verified hands-off judge path:

```text
4 live ADK agents
TRUST BREAK: history_snapshot
ACTION BLOCKED: publish_action
SAFE WORK REUSED: scout
SELECTIVE RECOVERY: statistician + skeptic + orchestrator rerun
FINAL ACTION: VERIFIED
```

Protected production API evidence includes unauthenticated `POST /api/runs -> 401` before model execution.

## Current measured production receipt

```text
Run:                 run-6d1427ccb2ca
Full restart:        4 model calls / 1739 input tokens
Selective recovery: 3 model calls / 1388 input tokens
Saved:               1 model call / 351 input tokens (~20%)
```

These values belong only to that controlled production run and are not a universal savings claim.

## Video V2 capture receipt — separate evidence class

```text
Capture run:         run-06fdaf68fdff
Mode:                HANDS_OFF_STAGED_AUTORUN
Full restart:        4 model calls / 1744 input tokens
Selective recovery: 3 model calls / 1366 input tokens
Saved:               1 model call / 378 input tokens (~22%)
Continuous segment:  24.080 s / 602 frames
Frame equality:      PASS — 602 / 602 preserved in assembled WebM
```

Capture metrics are intentionally kept separate from the newer production acceptance receipt.

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

## Remaining publication gate

Do **not** replace the current Devpost V1 video until Video V2 is publicly uploaded to YouTube/Vimeo, opens without owner authentication, and the Devpost project readback shows the exact new URL.

The canonical repository URL and current Devpost description have already been read back as current. Team-roster acceptance remains a separate owner-visible field and must not be inferred from repository or runtime evidence.
