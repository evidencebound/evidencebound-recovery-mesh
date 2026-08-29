# Judge acceptance gate

Status as of 2026-08-29: **FORTIFIED PRODUCTION ACCEPTANCE SATISFIED / FINAL PUBLIC VIDEO SUBMITTED**.

This file records evidence observed from the current production revision or executable repository verification. It keeps live Google Cloud proof separate from diagrams, synthetic tests, historical receipts, and unverified enterprise extensions.

## Judge moment

```text
TRUST BREAK
  -> EXACT BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

## Current fortified production receipt

```text
Deployment workflow:     33196157041 — SUCCESS
Acceptance workflow:     33196523402 — SUCCESS
Revision:                evidencebound-recovery-mesh-00007-bjm
Acceptance run:          run-4f1eba151be7
Provider / model:        google_adk_vertex / gemini-3.5-flash
Persistence:             firestore / durable=true
Live agents:             4
Trust break:             history_snapshot / STALE_EVIDENCE
Unsafe action:           publish_action BLOCKED
Blocked receipt count:   0
Unaffected work:         Scout REUSED
Selective recovery:      3 rerun / 1 reused
Recovered receipt count: 1
Rehydration:             trusted only after validation
Full restart:            4 model calls / 1707 input tokens
Selective recovery:      3 model calls / 1432 input tokens
Saved in that run:       1 model call / 275 input tokens (~16.1%)
Final action:            VERIFIED
Unauthenticated POST:    401
Exact-run Cloud Logging: PASS
GCP proof receipt:       PASS
```

These measurements belong only to `run-4f1eba151be7`.

Canonical production receipt: [`FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md`](FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md).

## Accepted production evidence

Current production verifies:

- Gemini 3.5 Flash through Vertex AI and provider `google_adk_vertex`;
- Google ADK `2.7.0` with four specialized roles;
- Cloud Run revision `evidencebound-recovery-mesh-00007-bjm`;
- `/health` exposes the real execution and persistence boundary;
- Firestore `(default)` in `europe-west1` is the active Durable Trust Ledger;
- persisted state is deterministically revalidated before reuse;
- unauthenticated state-changing API access fails with `401` before model execution;
- controlled stale evidence invalidates the exact dependent branch;
- `publish_action` becomes BLOCKED before the side effect;
- Firestore contains zero action receipts while BLOCKED;
- Scout remains verifiable and is reused;
- Statistician, Skeptic, and Orchestrator are selectively recomputed;
- recomputed checkpoints are deterministically re-verified;
- after recovery Firestore contains exactly one durable action receipt;
- the same persisted run is rehydrated only after trust validation;
- a separate read-only auditor identity queries Google Cloud Logging for the exact same `run_id`;
- Workload Identity Federation provides keyless deployment/audit identities;
- Google Agent Registry contains a discoverable Recovery Mesh fleet endpoint;
- repository, Devpost description, architecture, video, and current receipts describe the same bounded system.

## Exact-run Cloud Logging evidence

Workflow `33196523402` queried Cloud Logging for `run-4f1eba151be7` and returned:

```text
EXACT_RUN_CLOUD_LOGGING=PASS
GCP_PROOF_RECEIPT=PASS
```

Observed runtime events include:

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

Cloud Logging proves external auditability; it does not make trust decisions.

## Durable Trust Ledger acceptance

```text
FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0 run_id=run-4f1eba151be7
DURABLE_BLOCKED=PASS action=BLOCKED receipt=absent persisted_trust=validated
DURABLE_RECOVERY=PASS receipt=present rehydration=trusted
FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1 run_id=run-4f1eba151be7
```

Firestore persistence never implies trusted state. Stored checkpoints must pass dependency/input digest, integrity, provenance, and active-policy validation before reuse.

The exact production acceptance did not deliberately kill a Cloud Run instance between persistence and replay. Repository tests cover crash/restart invariants; the live receipt proves the deployed Firestore data path, receipt cardinality, and rehydration gate.

## Final public video

Final public judge video:

`https://youtu.be/3OtS17yf-Xo`

Devpost live project readback on 2026-08-29 confirms that exact URL as the current submitted video.

The final video uses current revision `00007-bjm` and includes real Google Cloud / Cloud Shell evidence for Cloud Run, Gemini/ADK health, active Firestore persistence, and exact-run Cloud Logging, alongside the Recovery Mesh trust-break/recovery Proof of Action.

The previous V1 video is historical evidence only and is no longer the submitted Devpost video.

## Agent Registry acceptance

```text
Workflow: 31871557186
AGENT_REGISTRY=PASS
Service: projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
Agent: projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_DISCOVERY=PASS
```

This is the verified 2026-08-15 catalog/discovery control-plane receipt. Agent Registry cannot override Recovery Mesh trust state.

## Evidence-class discipline

- deterministic/local tests do not prove live Gemini execution;
- the 100-checkpoint synthetic scale probe does not prove 100 live Gemini calls;
- a diagram does not prove a Google integration;
- Firestore persistence does not make state automatically trusted;
- Cloud Logging is audit evidence, not trust authority;
- Agent Registry is discovery/catalog, not trust authority;
- per-run savings are not universal savings claims.

## Current non-claims

The submission does not claim without separate evidence:

- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- universal token/cost savings;
- a forced Cloud Run instance-kill production replay proving restart-surviving exactly-once behavior;
- that Google services, rather than Recovery Mesh deterministic contracts, detected or resolved the trust break.

## Remaining owner-visible checks

The production, repository, Devpost project copy, thumbnail, and submitted video have been synchronized. Two Devpost form details remain owner-visible because the available connector does not safely expose/edit them without risking the private judge credential:

1. confirm every invited teammate has accepted the Devpost project invite;
2. confirm the Google Cloud Services multi-select includes both **Cloud Run** and **Firestore**.

The architecture diagram was updated in the Devpost UI by the owner on 2026-08-29.
