# Owner return runbook — Google Cloud production gate

Status date: 2026-08-14.

This runbook is intentionally short. Do not improvise around billing, IAM, or failed live checks.

## Current facts

- Hackathon project ID: `evidencebound-rm-c977c1`
- Project number: `457699623691`
- Project label: `hackathon=all-things-agentic-2026`
- Cloud Run region: `europe-west1`
- Vertex location: `global`
- Gemini model target: `gemini-3.5-flash`
- Public repository: `moneyparking/evidencebound-recovery-mesh`
- Old project `vocal-lightning-7dmzd`: deletion requested; it is not a deployment target.
- Production blocker: billing is not yet verified enabled on the isolated hackathon project.

## Owner-only billing step

Open the intentionally empty billing account selected for the hackathon and link only `evidencebound-rm-c977c1` to it. Do not reopen or relink the deleted legacy project.

After the account is open, verify from authenticated Cloud Shell:

```bash
gcloud config set project evidencebound-rm-c977c1

gcloud billing projects link evidencebound-rm-c977c1 \
  --billing-account=014CCF-9ABDCB-526D33

gcloud billing projects describe evidencebound-rm-c977c1
```

Continue only when the receipt contains `billingEnabled: true`.

## First production bootstrap

Use current public `main`, not an old local copy:

```bash
set -euo pipefail
cd ~
rm -rf evidencebound-recovery-mesh
git clone https://github.com/moneyparking/evidencebound-recovery-mesh.git
cd evidencebound-recovery-mesh

export GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1
export GOOGLE_CLOUD_RUN_REGION=europe-west1
export GOOGLE_CLOUD_LOCATION=global
export RECOVERY_MESH_MODEL=gemini-3.5-flash
export RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET=64

./scripts/gcp-owner-bootstrap.sh 2>&1 | tee ~/recovery-mesh-bootstrap.log
```

The bootstrap fails closed before mutation unless all of these match the isolated project: project ID, project number, hackathon label, ACTIVE lifecycle state, and billing enabled.

The `64` live-call value is a process-local public-demo guard, not a currency/spend limit. It fails provider calls closed after the reservation budget is exhausted and resets if Cloud Run starts a new process/revision.

## Required successful receipt

Do not promote Google Cloud claims unless the live output includes all applicable evidence:

```text
BILLING_ENABLED=true
VERTEX_GEMINI_LIVE=PASS
HEALTH=PASS provider=google_adk_vertex model=gemini-3.5-flash
LIVE_ADK_BASELINE=PASS agents=4
TRUST_BREAK=PASS blocked=publish_action reused=scout
SELECTIVE_RECOVERY=PASS rerun=3 reused=1 final_action=VERIFIED
RUN_ID=...
JUDGE_URL=...
GCP_OWNER_BOOTSTRAP=PASS
SERVICE_URL=...
CLOUD_RUN_REVISION=...
LIVE_MODEL_CALL_BUDGET_PER_PROCESS=64
WORKLOAD_IDENTITY_PROVIDER=...
```

If any command emits `BLOCKER`, `ERROR`, `PERMISSION_DENIED`, `BILLING`, `QUOTA`, or a failed assertion, stop and retain the output. Do not replace a failed Google path with deterministic output.

## Read-only Google Cloud proof receipt

After a successful bootstrap, collect a concise non-mutating receipt for the demo/submission evidence pack:

```bash
export GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1
./scripts/gcp-proof-receipt.sh | tee ~/recovery-mesh-gcp-proof.txt
```

It reports the exact project, project number, Cloud Run service URL/revision/runtime identity, live `/healthz`, and recent Cloud Run request metadata without printing application payloads or credentials.

## After first bootstrap

A manual GitHub Actions workflow exists at `.github/workflows/deploy-cloud-run.yml`. After the bootstrap creates the Workload Identity Pool/provider and deployer service account, that workflow can perform keyless deployments from `main` without service-account keys. It runs the same live preflight and end-to-end smoke gate.

## Submission rule

Cloud Run, Gemini, hosted URL, live benchmark values, and production PASS remain `PENDING` until the real receipts above exist. The deterministic tests and synthetic 100-agent scale probe are separate evidence classes.
