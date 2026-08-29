# Devpost Submission Matrix — All Things Agentic Hackathon 2026

Canonical project: **EvidenceBound Recovery Mesh**  
Category: **Fortified Enterprise Fleet**  
Devpost project: `evidencebound-recovery-mesh`  
Submission ID: `1136853`

> Current-state document. A field is listed as implemented/used only when backed by repository, production, Google Cloud, or live Devpost evidence.

## Current submission state — 2026-08-29

| Devpost field | Submitted answer / state | Evidence status |
|---|---|---|
| Submitter Type | `Team of individuals` | SUBMITTED / OWNER-VISIBLE |
| Country | `Ukraine` | SUBMITTED |
| Category | `Fortified Enterprise Fleet` | SUBMITTED |
| Startup Prize organization/email | blank | INTENTIONALLY NOT CLAIMED |
| Public code repository | `https://github.com/evidencebound/evidencebound-recovery-mesh` | LIVE / READ BACK |
| Reproducible README | `Yes` | PASS |
| Hosted project URL | `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/` | LIVE / VERIFIED |
| Preferred judge route | `?autorun=stale_evidence&recover=1` | HANDS-OFF / VERIFIED |
| Private judge testing instructions | private Devpost field + public runbook | OWNER-VISIBLE; credential remains private |
| Google SDK | `Agent Development Kit (ADK)` | LIVE / VERIFIED |
| Google Cloud runtime | `Cloud Run` | LIVE / VERIFIED |
| Durable persistence | `Firestore Durable Trust Ledger` | LIVE / VERIFIED |
| Google AI model | `Gemini 3.5 Flash via Vertex AI` | LIVE / VERIFIED |
| External causal audit | `Google Cloud Logging exact-run proof` | LIVE / VERIFIED |
| Agent discovery | `Google Agent Registry fleet entry point` | LIVE / VERIFIED |
| Architecture diagram | current Firestore + Cloud Logging architecture | OWNER UPDATED IN DEVPOST UI 2026-08-29 |
| Project thumbnail | Recovery Mesh trust-break / verified-recovery visual | UPLOAD ACCEPTED BY DEVPOST |
| Demo video | `https://youtu.be/3OtS17yf-Xo` | V2 LIVE PROJECT READBACK |
| Bonus technical article | DEV.to URL supplied in Devpost | SUBMITTED |
| Bonus social post | LinkedIn URL with `#AllThingsAgenticHackathon` | SUBMITTED |

The live Devpost description was also rewritten around the current judging rubric: explicit **Twist**, autonomous execution, specialized sub-agents, an “Unlikely Hero” football performance / match-intelligence analyst workload, durable state, failure tolerance, exact-run Google Cloud proof, and explicit non-claims.

## Innovation / operational-utility evidence

The V2 submission makes the hackathon-built invention explicit:

1. directed Trust Graph with deterministic exact blast radius;
2. trust-aware selective recovery instead of restart-everything or continue-contaminated-state;
3. persisted state is not automatically trusted state;
4. fail-closed durable side-effect protocol: `0 receipts while BLOCKED -> exactly 1 after VERIFIED recovery`;
5. Gemini reasoning separated from deterministic trust/action authority;
6. the same `run_id` binds Flight Recorder, Firestore, and Google Cloud Logging evidence;
7. measured selective recovery using actual live model-call/token receipts.

The judge workload models a football performance / match-intelligence operations analyst using safe controlled fixture/history/policy data. No live SignalReview/provider truth is claimed.

## Current fortified production evidence

```text
Project:              evidencebound-rm-c977c1
Cloud Run revision:   evidencebound-recovery-mesh-00007-bjm
Hosted URL:           https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/
Canonical .run.app:   https://evidencebound-recovery-mesh-457699623691.europe-west1.run.app
Health endpoint:      /health
Provider:             google_adk_vertex
Model:                gemini-3.5-flash
Google ADK:           2.7.0
Persistence:          firestore / durable=true
Firestore database:   (default) / europe-west1
Deployment workflow:  33196157041 — SUCCESS
Acceptance workflow:  33196523402 — SUCCESS
Acceptance run:       run-4f1eba151be7
Exact-run Cloud Logs: PASS
GCP proof receipt:    PASS
```

Verified hands-off judge path:

```text
4 live ADK agents
TRUST BREAK: history_snapshot / STALE_EVIDENCE
ACTION BLOCKED: publish_action
BLOCKED FIRESTORE ACTION RECEIPTS: 0
SAFE WORK REUSED: Scout
SELECTIVE RECOVERY: Statistician + Skeptic + Orchestrator rerun
RECOVERED FIRESTORE ACTION RECEIPTS: 1
REHYDRATION: trusted only after deterministic validation
FINAL ACTION: VERIFIED
```

Protected production API evidence includes unauthenticated `POST /api/runs -> 401` before model execution.

## Current measured production receipt

```text
Run:                 run-4f1eba151be7
Full restart:        4 model calls / 1707 input tokens
Selective recovery: 3 model calls / 1432 input tokens
Saved:               1 model call / 275 input tokens (~16.1%)
```

These values belong only to that controlled production run and are not a universal savings claim.

## Firestore durable proof

```text
FIRESTORE_DATABASE=READY
FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0 run_id=run-4f1eba151be7
DURABLE_BLOCKED=PASS action=BLOCKED receipt=absent persisted_trust=validated
DURABLE_RECOVERY=PASS receipt=present rehydration=trusted
FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1 run_id=run-4f1eba151be7
```

Firestore is persistence, not trust authority. The exact acceptance did not deliberately force a Cloud Run instance kill/restart.

## Exact-run Google Cloud Logging proof

```text
EXACT_RUN_CLOUD_LOGGING=PASS run_id=run-4f1eba151be7
GCP_PROOF_RECEIPT=PASS
```

Observed causal events include:

```text
TRUST_BREAK_DETECTED
BLAST_RADIUS_COMPUTED
ACTION_BLOCKED
CHECKPOINT_REUSED
RECOMPUTE_STARTED
CHECKPOINT_REVERIFIED
ACTION_RESUMED
RECOVERY_COMPLETED
```

Cloud Logging is production audit evidence, not trust authority.

## Verified Google Agent Registry evidence

```text
AGENT_REGISTRY=PASS
AGENT_REGISTRY_SERVICE=projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
AGENT_REGISTRY_AGENT=projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_INTERFACE=https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app
AGENT_REGISTRY_DISCOVERY=PASS
Workflow: 31871557186
```

This is the verified 2026-08-15 catalog/discovery receipt and does not imply separate Registry entries for the four internal ADK roles.

## Final public video

Devpost live project readback on 2026-08-29 shows:

`https://youtu.be/3OtS17yf-Xo`

The final video is below four minutes, English, uses current revision `00007-bjm`, and visually shows real Google Cloud / Cloud Shell evidence rather than relying only on self-authored proof cards.

## New-project boundary

Recovery Mesh is a new isolated hackathon repository. Pre-existing EvidenceBound verification/provenance ideas and SignalReview concepts are disclosed in `PREEXISTING_WORK.md`. No SignalReview production source or prior EvidenceBound implementation source is copied into the Recovery Mesh core.

## Explicit non-claims

The live submission does **not** claim without separate evidence:

- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- universal token/cost savings;
- a forced Cloud Run instance-kill production replay proving restart-surviving exactly-once behavior;
- 100 live Gemini agents in the synthetic scale probe;
- that Firestore, Cloud Logging, Agent Registry, or Gemini can override Recovery Mesh deterministic trust authority.

## Owner-visible final form checks

Two form details cannot be safely changed through the available connector without risking the private judge-only testing credential:

1. confirm every invited teammate has accepted the Devpost project invite;
2. confirm **Which Google Cloud Service(s) did you use?** includes both **Cloud Run** and **Firestore**.

The new architecture diagram was uploaded by the owner in Devpost on 2026-08-29.

Canonical production receipt: [`FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md`](FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md).
