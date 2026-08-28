# Devpost Submission Matrix — All Things Agentic Hackathon 2026

Canonical project: **EvidenceBound Recovery Mesh**  
Category: **Fortified Enterprise Fleet**  
Devpost project: `evidencebound-recovery-mesh`  
Submission ID: `1136853`

> Current-state document. A field is listed as implemented/used only when backed by repository, production, Google Cloud, or live Devpost evidence.

## Current submission state — 2026-08-28

| Devpost field | Submitted answer / state | Evidence status |
|---|---|---|
| Submitter Type | `Team of individuals` | SUBMITTED |
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
| Google AI model | `Gemini 3.5 Flash via Vertex AI` | LIVE / VERIFIED |
| Durable persistence | `Firestore Durable Trust Ledger` | LIVE / VERIFIED |
| External causal audit | `Google Cloud Logging exact-run proof` | LIVE / VERIFIED |
| Agent discovery | `Google Agent Registry fleet entry point` | LIVE / VERIFIED |
| Architecture diagram | must match current Firestore + Cloud Logging architecture | REPO SOURCE UPDATED; DEVPOST IMAGE READBACK STILL OWNER-VISIBLE |
| Demo video | `https://youtu.be/AExuVCC-m7o` | V1 PUBLIC / CURRENT DEVPOST VIDEO |
| Final proof video | current `00007-bjm` + real GCP terminal proof | PUBLICATION PENDING |
| Bonus technical article | DEV.to URL supplied in Devpost | SUBMITTED |
| Bonus social post | LinkedIn URL with `#AllThingsAgenticHackathon` | SUBMITTED |

The Devpost gallery images are presentation assets rather than runtime evidence; they must not introduce capabilities absent from the live system.

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

The current production revision actively uses Firestore for the Durable Trust Ledger. Live acceptance verified:

```text
FIRESTORE_DATABASE=READY
FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0 run_id=run-4f1eba151be7
DURABLE_BLOCKED=PASS action=BLOCKED receipt=absent persisted_trust=validated
DURABLE_RECOVERY=PASS receipt=present rehydration=trusted
FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1 run_id=run-4f1eba151be7
```

Firestore is persistence, not trust authority. Persisted state must pass deterministic validation before reuse.

The exact live acceptance did not deliberately kill a Cloud Run instance between persistence and replay; do not convert this receipt into a broader forced-restart production claim.

## Exact-run Google Cloud Logging proof

The second job in workflow `33196523402` uses the separate auditor identity and queries Cloud Logging for the same acceptance `run_id`.

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

This is production audit evidence; Cloud Logging does not authorize trust transitions.

## Verified Google Agent Registry evidence

```text
AGENT_REGISTRY=PASS
AGENT_REGISTRY_SERVICE=projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
AGENT_REGISTRY_AGENT=projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_INTERFACE=https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app
AGENT_REGISTRY_DISCOVERY=PASS
Workflow: 31871557186
```

This 2026-08-15 control-plane receipt represents the Recovery Mesh fleet entry point. It is not presented as a new 2026-08-28 registration and does not imply separate Registry entries for the four internal ADK roles.

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

## Current video gate

The public Devpost video remains V1 until a new public YouTube/Vimeo proof is uploaded and read back.

The next proof video should use current revision `evidencebound-recovery-mesh-00007-bjm` and visibly show real Google Cloud evidence for:

- project `evidencebound-rm-c977c1`;
- Cloud Run revision `00007-bjm`;
- live `/health` with `google_adk_vertex`, `gemini-3.5-flash`, `firestore`, `durable=true`;
- Firestore `(default)` in `europe-west1`;
- exact-run Cloud Logging for the Recovery Mesh causal events;
- the hands-off Flight Recorder trust-break → selective-recovery judge moment.

Do **not** replace the current V1 video until the new URL is public and Devpost readback shows the exact URL.

Canonical production receipt: [`FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md`](FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md).
