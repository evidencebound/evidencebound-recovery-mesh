# Google Cloud deployment target

Status as of 2026-08-28: **FORTIFIED LIVE / VERIFIED**.

- Hackathon Google Cloud project ID: `evidencebound-rm-c977c1`
- Project number: `457699623691`
- Project name: `EvidenceBound Recovery Mesh`
- Project label: `hackathon=all-things-agentic-2026`
- Cloud Run region: `europe-west1`
- Vertex location: `global`
- Model: `gemini-3.5-flash`
- Service name: `evidencebound-recovery-mesh`
- Current Cloud Run revision: `evidencebound-recovery-mesh-00007-bjm`
- Hosted URL: `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/`
- Canonical service URL: `https://evidencebound-recovery-mesh-457699623691.europe-west1.run.app`
- Health endpoint: `/health`
- Execution provider: `google_adk_vertex`
- Google ADK: `2.7.0`
- Persistence provider: `firestore`
- Firestore database: `(default)`
- Firestore location: `europe-west1`
- Exact-run audit surface: Google Cloud Logging

## Isolation decision

This project was created specifically for the All Things Agentic 2026 hackathon deployment so Cloud Run, Vertex AI, Firestore, Cloud Logging, IAM identities, secrets and billing evidence remain isolated from older Google Cloud workloads.

The legacy project `vocal-lightning-7dmzd` is not a Recovery Mesh deployment target.

## Verified production gate

Current production deployment workflow:

```text
33196157041 — SUCCESS
```

Current fresh acceptance + cloud-proof workflow:

```text
33196523402 — SUCCESS
run-4f1eba151be7
```

Verified behavior includes:

```text
VERTEX_GEMINI_LIVE=PASS
FIRESTORE_DATABASE=READY
HEALTH=PASS provider=google_adk_vertex model=gemini-3.5-flash persistence=firestore durable=true judge_access=protected
JUDGE_API_AUTH=PASS unauthenticated_post=401
LIVE_ADK_BASELINE=PASS agents=4 persistence=firestore
TRUST_BREAK=PASS blocked=publish_action reused=scout
FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0 run_id=run-4f1eba151be7
SELECTIVE_RECOVERY=PASS rerun=3 reused=1 final_action=VERIFIED
DURABLE_RECOVERY=PASS receipt=present rehydration=trusted
FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1 run_id=run-4f1eba151be7
EXACT_RUN_CLOUD_LOGGING=PASS run_id=run-4f1eba151be7
GCP_PROOF_RECEIPT=PASS
```

Current production configuration remains intentionally bounded:

- Cloud Run `min=0`, `max=1`;
- one CPU and 512 MiB;
- dedicated runtime/build/deployer identities plus a separate read-only auditor identity;
- Secret Manager judge credential;
- keyless GitHub Workload Identity Federation;
- normal deploys verify Firestore rather than provisioning it;
- process-local live model-call guard to reduce accidental public-demo traffic.

The live-call guard is **not** a billing cap.

## Durable persistence boundary

Firestore is now an active production integration through the Durable Trust Ledger. The runtime persists run/checkpoint state, Flight Recorder events and action receipts, while Recovery Mesh deterministic checks remain authoritative.

Current live receipt proves:

```text
BLOCKED action -> 0 durable side-effect receipts
VERIFIED recovery -> exactly 1 durable side-effect receipt
rehydration -> trusted only after deterministic validation
```

Persisted state is never trusted merely because it exists in Firestore.

The exact production acceptance did not deliberately kill a Cloud Run instance between write and replay. Do not infer a separate forced-restart exactly-once production claim from this receipt.

## Google Cloud Logging boundary

The fresh acceptance workflow uses `recovery-mesh-auditor@evidencebound-rm-c977c1.iam.gserviceaccount.com` for a separate read-only proof job. It queries Cloud Logging for the exact same acceptance `run_id` and requires the full causal recovery sequence before reporting PASS.

Cloud Logging is external audit evidence, not trust authority.

## Google Agent Registry

The existing Cloud Run fleet entry point is registered and discoverable in Google Agent Registry:

```text
Service: projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
Agent: projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
Workflow: 31871557186
Discovery: PASS
```

Agent Registry is catalog/discovery control plane only. It does not authorize Trust Graph state or actions.

## Current non-claims

This document does not claim without separate production evidence:

- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- forced Cloud Run instance-kill replay proving restart-surviving exactly-once behavior;
- universal token/cost savings.

Canonical production receipt: [`FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md`](FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md).
