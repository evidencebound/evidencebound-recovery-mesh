# Owner return runbook — production operations

> **Status:** The original 2026-08-14 bootstrap checklist has been completed. This file now records the current live state and safe owner operations. It is not evidence that production is still blocked.

## Current facts

- Project ID: `evidencebound-rm-c977c1`
- Project number: `457699623691`
- Project label: `hackathon=all-things-agentic-2026`
- Cloud Run region: `europe-west1`
- Vertex location: `global`
- Model: `gemini-3.5-flash`
- Google ADK: `2.7.0`
- Current Cloud Run revision: `evidencebound-recovery-mesh-00005-82k`
- Hosted UI: `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/`
- Health endpoint: `/health`
- Judge secret: `recovery-mesh-judge-key:1` in Secret Manager
- Agent Registry Service: `recovery-mesh-fleet`
- Public repository: `moneyparking/evidencebound-recovery-mesh`

The old project `vocal-lightning-7dmzd` is not a Recovery Mesh deployment target.

## Current production receipt

The accepted production path has already demonstrated:

```text
VERTEX_GEMINI_LIVE=PASS
HEALTH=PASS provider=google_adk_vertex model=gemini-3.5-flash judge_access=protected
JUDGE_API_AUTH=PASS unauthenticated_post=401
LIVE_ADK_BASELINE=PASS agents=4
TRUST_BREAK=PASS blocked=publish_action reused=scout
SELECTIVE_RECOVERY=PASS rerun=3 reused=1 final_action=VERIFIED
```

Agent Registry separately demonstrated:

```text
Workflow: 31871557186
AGENT_REGISTRY=PASS
AGENT_REGISTRY_DISCOVERY=PASS
```

## Retrieve the private Devpost judge key

Retrieve the value only in an authenticated owner Cloud Shell session:

```bash
gcloud secrets versions access 1 \
  --secret=recovery-mesh-judge-key \
  --project=evidencebound-rm-c977c1
echo
```

Use the value only in Devpost's private judge/testing field and the hosted UI's Bounded Judge Access box.

Never place the value in:

- GitHub;
- chat transcripts;
- screenshots;
- public project text;
- video;
- URLs.

If the key is exposed, rotate the secret and deploy a revision that mounts the intended new version before giving judges the replacement credential.

## Read-only production proof

From a current clone of `main`:

```bash
export GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1
./scripts/gcp-proof-receipt.sh | tee ~/recovery-mesh-gcp-proof.txt
```

The receipt should identify the current project, service, revision, runtime identity, `/health` provider, and recent request metadata without printing application payloads or credentials.

## Deployment path

Normal deployments are performed keylessly through the prepared GitHub Actions Cloud Run workflow using Workload Identity Federation restricted to this repository/owner/`main` branch.

A deployment is not considered accepted merely because Cloud Run created a revision. The same live preflight and protected recovery smoke must pass before the new revision should be promoted as submission evidence.

## Cost posture

The judge deployment is intentionally bounded:

- Cloud Run `min=0`, `max=1`;
- one CPU and 512 MiB;
- protected run/fault/recovery APIs;
- bounded four-agent judge flow;
- process-local live model-call reservation guard;
- deterministic synthetic scale test instead of 100 paid Gemini agents.

The live-call guard is not a financial cap. Billing credits, budget alerts, and actual usage must be monitored independently.

## Agent Registry

Agent Registry registration is already complete for the fleet entry point. Re-registration or updates should use the existing keyless control-plane workflow and remain idempotent.

Do not describe Registry metadata as trust authority. Recovery Mesh deterministic verification, provenance/integrity checks, blast-radius logic, and action gate remain authoritative.

## Persistence limitation

The live run/idempotency store remains process-local. Do not claim multi-week context, restart-surviving exactly-once behavior, Firestore persistence, Memory Bank, Agent Runtime, Model Armor, or BigQuery export unless a future integration is separately implemented and verified.

## Submission-safe operating rule

After the current submission is green, avoid runtime changes unless they materially improve a judging requirement and can be re-run through the complete acceptance gate.

Documentation-only corrections may proceed through normal PR + CI. Any runtime change must be treated as a new production acceptance event, not as a cosmetic patch.
