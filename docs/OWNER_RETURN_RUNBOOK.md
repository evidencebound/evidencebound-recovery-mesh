# Owner return runbook — Google Cloud production gate

Status date: 2026-08-14.

This runbook is intentionally short. Do not improvise around billing, IAM, secrets, or failed live checks.

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

## Create the project-scoped budget alert

After billing is linked and before production work, create the prepared alert-only budget:

```bash
cd ~/evidencebound-recovery-mesh 2>/dev/null || true
export GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1
export RECOVERY_MESH_BILLING_ACCOUNT=014CCF-9ABDCB-526D33
export RECOVERY_MESH_BUDGET_AMOUNT=5
./scripts/create-project-budget-alert.sh
```

The default amount is `5` in the billing account currency, filtered only to the hackathon project, with 50%, 90%, and 100% thresholds. This is deliberately a **notification budget, not a hard spend cap**. The script is idempotent by display name and refuses to modify an existing budget automatically.

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

The bootstrap also generates the private judge access key exactly once, stores it as `recovery-mesh-judge-key:1` in Secret Manager, grants bounded access to the runtime/deployer identities, and mounts it into Cloud Run. The key value is never printed by the bootstrap.

The `64` live-call value is a process-local public-demo guard, not a currency/spend limit. It fails provider calls closed after the reservation budget is exhausted and resets if Cloud Run starts a new process/revision.

## Required successful core receipt

Do not promote Google Cloud claims unless the live output includes all applicable evidence:

```text
BILLING_ENABLED=true
VERTEX_GEMINI_LIVE=PASS
HEALTH=PASS provider=google_adk_vertex model=gemini-3.5-flash judge_access=protected
JUDGE_API_AUTH=PASS unauthenticated_post=401
LIVE_ADK_BASELINE=PASS agents=4
TRUST_BREAK=PASS blocked=publish_action reused=scout
SELECTIVE_RECOVERY=PASS rerun=3 reused=1 final_action=VERIFIED
RUN_ID=...
JUDGE_URL=...
GCP_OWNER_BOOTSTRAP=PASS
SERVICE_URL=...
CLOUD_RUN_REVISION=...
LIVE_MODEL_CALL_BUDGET_PER_PROCESS=64
JUDGE_SECRET_NAME=recovery-mesh-judge-key
JUDGE_SECRET_VERSION=1
WORKLOAD_IDENTITY_PROVIDER=...
```

If any command emits `BLOCKER`, `ERROR`, `PERMISSION_DENIED`, `BILLING`, `QUOTA`, or a failed assertion, stop and retain the output. Do not replace a failed Google path with deterministic output.

## Retrieve the private Devpost testing key

Only after the bootstrap succeeds, retrieve the judge key locally in Cloud Shell with the command printed by the bootstrap, equivalent to:

```bash
gcloud secrets versions access 1 \
  --secret=recovery-mesh-judge-key \
  --project=evidencebound-rm-c977c1
```

Use that value only in Devpost's private judge/testing-credentials field and in the Flight Recorder's **Bounded Judge Access** box. Do not paste the key into chat, GitHub, screenshots, public project text, or the demo video.

The browser stores an entered key only in that tab's `sessionStorage` and sends it as `X-Recovery-Mesh-Judge-Key` to protected run/action endpoints.

## Read-only Google Cloud proof receipt

After a successful bootstrap, collect a concise non-mutating receipt for the demo/submission evidence pack:

```bash
export GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1
./scripts/gcp-proof-receipt.sh | tee ~/recovery-mesh-gcp-proof.txt
```

It reports the exact project, project number, Cloud Run service URL/revision/runtime identity, live `/healthz`, and recent Cloud Run request metadata without printing application payloads or credentials.

## Fortified Gate B — Agent Registry, only after core PASS

Do **not** add enterprise services to rescue a failed core deployment. Once the core receipt above is green, test Google Agent Registry discovery separately:

```bash
gcloud services enable agentregistry.googleapis.com --project=evidencebound-rm-c977c1
export GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1
./scripts/register-agent-registry.sh
```

Promote Agent Registry into the architecture/Devpost story only if the script emits both a writable Service resource and a read-only discoverable Agent projection:

```text
AGENT_REGISTRY=PASS ...
AGENT_REGISTRY_SERVICE=...
AGENT_REGISTRY_AGENT=...
AGENT_REGISTRY_INTERFACE=...
```

If entitlement/API behavior blocks it, leave it out rather than fabricating a Fortified integration.

## After first bootstrap

A manual GitHub Actions workflow exists at `.github/workflows/deploy-cloud-run.yml`. After the bootstrap creates the Workload Identity Pool/provider and deployer service account, that workflow can perform keyless deployments from `main` without service-account keys. It runs the same live preflight and protected end-to-end smoke gate.

## Submission rule

Cloud Run, Gemini, hosted URL, live benchmark values, Secret Manager runtime state, Agent Registry, and production PASS remain `PENDING` until their real receipts exist. The deterministic tests and synthetic 100-agent scale probe are separate evidence classes.
