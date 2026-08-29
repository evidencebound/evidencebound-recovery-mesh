# Proof-of-Action video status

**Final public submission video:**

`https://youtu.be/3OtS17yf-Xo`

Devpost project readback on 2026-08-29 confirms that exact URL as the current submitted video.

The final judge master is approximately 1:51, in English, and uses the current production truth rather than the older pre-Firestore V1/V2 receipts.

## What the final video proves

The video is built around evidence rather than generic presentation cards:

- real Recovery Mesh Flight Recorder state;
- trust break and exact blast-radius visualization;
- `publish_action = BLOCKED` before the unsafe side effect;
- Scout preserved/reused while the contaminated branch is recomputed;
- verified recovery;
- real Google Cloud / Cloud Shell proof;
- current Cloud Run revision `evidencebound-recovery-mesh-00007-bjm`;
- `/health` showing `google_adk_vertex`, `gemini-3.5-flash`, `firestore`, and `durable=true`;
- Firestore `(default)` database in `europe-west1`;
- exact-run Google Cloud Logging evidence for the Recovery Mesh causal sequence.

Judge sequence:

```text
TRUST BREAK
  -> EXACT BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

## Current production evidence bound to the video

```text
Cloud Run revision:   evidencebound-recovery-mesh-00007-bjm
Deployment workflow:  33196157041 — SUCCESS
Acceptance workflow:  33196523402 — SUCCESS
Acceptance run:       run-4f1eba151be7
Provider:             google_adk_vertex
Model:                gemini-3.5-flash
Persistence:          firestore / durable=true
Exact-run Cloud Logs: PASS
GCP proof receipt:    PASS
```

Measured values for `run-4f1eba151be7` only:

```text
Full restart:        4 model calls / 1707 input tokens
Selective recovery: 3 model calls / 1432 input tokens
Saved in this run:   1 model call / 275 input tokens (~16.1%)
Blocked receipt:     0 durable action receipts
Recovered receipt:   exactly 1 durable action receipt
Rehydration:         trusted only after deterministic validation
Final action:        VERIFIED
```

These are run-specific measurements, not universal savings claims.

## Firestore proof boundary

The current live integration is active production persistence through the Durable Trust Ledger.

Verified live invariant:

```text
FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0
DURABLE_RECOVERY=PASS receipt=present rehydration=trusted
FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1
```

Persistence is not trust authority. Recovery Mesh revalidates stored checkpoint bindings before reuse.

The reference production acceptance did not deliberately kill a Cloud Run instance between write and replay; the submission therefore does not claim a separate forced-instance-restart production benchmark.

## Exact-run Cloud Logging proof

Workflow `33196523402` queried Google Cloud Logging under a separate read-only auditor identity for the same `run-4f1eba151be7` and returned:

```text
EXACT_RUN_CLOUD_LOGGING=PASS
GCP_PROOF_RECEIPT=PASS
```

Observed events include:

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

Cloud Logging is external audit proof; Recovery Mesh deterministic code remains the trust authority.

## Google Agent Registry boundary

Verified control-plane receipt remains:

```text
Workflow: 31871557186
AGENT_REGISTRY=PASS
AGENT_REGISTRY_SERVICE=projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
AGENT_REGISTRY_DISCOVERY=PASS
```

Agent Registry is catalog/discovery only and cannot authorize trust transitions.

## Public judge route

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/?autorun=stale_evidence&recover=1`

After the private judge key is entered once, no human recovery choice is required. The runtime performs the trust break, exact repair planning, selective recomputation, deterministic re-verification, durable receipt commit, and final recovery automatically.

## Explicit non-claims

The final video does not claim without separate evidence:

- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- universal savings percentages;
- forced Cloud Run process-kill production replay proving restart-surviving exactly-once behavior;
- separate Registry entries for each internal ADK role.

Canonical current receipt: [`FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md`](FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md).
