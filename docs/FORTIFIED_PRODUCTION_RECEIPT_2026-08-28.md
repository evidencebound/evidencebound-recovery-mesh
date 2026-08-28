# Fortified Production Receipt — 2026-08-28

This receipt records only evidence observed from the deployed EvidenceBound Recovery Mesh production path. It does not substitute diagrams, local tests, or planned integrations for live Google Cloud evidence.

## Production deployment

```text
GCP project:             evidencebound-rm-c977c1
Cloud Run region:        europe-west1
Service:                 evidencebound-recovery-mesh
Revision:                evidencebound-recovery-mesh-00007-bjm
Canonical service URL:   https://evidencebound-recovery-mesh-457699623691.europe-west1.run.app
Public judge URL:        https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app
Execution provider:      google_adk_vertex
Model:                   gemini-3.5-flash
Persistence:             firestore / durable=true
Deployment workflow:     33196157041 — SUCCESS
```

The deploy workflow verified the canonical Firestore `(default)` database in `europe-west1`, deployed revision `00007-bjm`, routed 100% of service traffic to it, and completed the protected production smoke.

## Fresh live acceptance

```text
Acceptance workflow:     33196523402 — SUCCESS
Live judge job:          SUCCESS
Cloud proof job:         SUCCESS
Acceptance run:          run-4f1eba151be7
Unauthenticated POST:    401
Live ADK baseline:       4 agents
Trust break source:      history_snapshot / STALE_EVIDENCE
Blocked action:          publish_action
Reused agent work:       Scout
Selective recovery:      3 rerun / 1 reused
Final action:            VERIFIED
```

Measured values for this run only:

```text
Full restart:            4 model calls / 1707 input tokens
Selective recovery:      3 model calls / 1432 input tokens
Saved in this run:       1 model call / 275 input tokens (~16.1%)
```

These values are not a universal savings claim. Gemini token usage varies by live execution.

## Firestore Durable Trust Ledger proof

The production smoke verified the durable data plane before and after recovery:

```text
FIRESTORE_DATABASE=READY
FIRESTORE_DATABASE_LOCATION=europe-west1
FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0 run_id=run-4f1eba151be7
DURABLE_BLOCKED=PASS action=BLOCKED receipt=absent persisted_trust=validated
DURABLE_RECOVERY=PASS receipt=present rehydration=trusted
FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1 run_id=run-4f1eba151be7
```

Interpretation:

- while `publish_action` is BLOCKED, no durable side-effect receipt exists;
- after selective recomputation and deterministic re-verification, exactly one durable receipt exists;
- persisted state is revalidated before being treated as trusted;
- Firestore is persistence, not trust authority.

This acceptance does not claim that a forced Cloud Run instance-kill/restart was executed as part of this exact live run. Restart/crash semantics are separately covered by repository tests; the live receipt above proves the active Firestore data path and deterministic rehydration gate on the deployed revision.

## Exact-run Google Cloud Logging proof

The `cloud-proof` job authenticated through the separate read-only auditor identity:

```text
recovery-mesh-auditor@evidencebound-rm-c977c1.iam.gserviceaccount.com
```

It queried Google Cloud Logging for the exact acceptance run `run-4f1eba151be7` and returned:

```text
EXACT_RUN_CLOUD_LOGGING=PASS
GCP_PROOF_RECEIPT=PASS
```

The observed causal sequence for that same run included:

```text
RUN_STARTED
CHECKPOINT_VERIFIED
TRUST_BREAK_DETECTED
BLAST_RADIUS_COMPUTED
ACTION_BLOCKED
CHECKPOINT_REUSED
RECOMPUTE_STARTED
CHECKPOINT_REVERIFIED
ACTION_RESUMED
RECOVERY_COMPLETED
```

The key judge sequence is therefore backed by production Cloud Logging rather than a self-authored screenshot:

```text
TRUST BREAK
→ EXACT BLAST RADIUS
→ ACTION BLOCKED
→ SAFE WORK REUSED
→ AFFECTED BRANCH RECOMPUTED
→ VERIFIED RECOVERY
```

## Google integration truth boundary

Verified active integrations in this receipt:

- Google Cloud Run;
- Google ADK;
- Vertex AI / Gemini 3.5 Flash;
- Firestore Durable Trust Ledger;
- Google Cloud Logging exact-run causal audit;
- Google Secret Manager;
- Google Workload Identity Federation;
- Google Agent Registry fleet catalog/discovery entry.

Still not claimed without separate evidence:

- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- a forced process-kill production replay proving restart-surviving exactly-once behavior;
- a universal token/cost savings percentage.

## Primary evidence locations

- deployment workflow: `https://github.com/evidencebound/evidencebound-recovery-mesh/actions/runs/33196157041`
- fresh live acceptance + exact-run cloud proof: `https://github.com/evidencebound/evidencebound-recovery-mesh/actions/runs/33196523402`
- judge UI: `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/`
- preferred hands-off route: `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/?autorun=stale_evidence&recover=1`
