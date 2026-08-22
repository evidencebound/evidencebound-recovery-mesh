# Google Cloud deployment target

Status as of 2026-08-22: **LIVE / VERIFIED**.

- Hackathon Google Cloud project ID: `evidencebound-rm-c977c1`
- Project number: `457699623691`
- Project name: `EvidenceBound Recovery Mesh`
- Project label: `hackathon=all-things-agentic-2026`
- Cloud Run region: `europe-west1`
- Vertex location: `global`
- Model: `gemini-3.5-flash`
- Service name: `evidencebound-recovery-mesh`
- Current Cloud Run revision: `evidencebound-recovery-mesh-00005-82k`
- Hosted URL: `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/`
- Health endpoint: `/health`
- Execution provider: `google_adk_vertex`
- Google ADK: `2.7.0`

## Isolation decision

This project was created specifically for the All Things Agentic 2026 hackathon deployment so Cloud Run, Vertex AI, IAM identities, logs, secrets, and billing evidence remain isolated from older Google Cloud workloads.

The legacy project `vocal-lightning-7dmzd` received a deletion request on 2026-08-14 and is not a Recovery Mesh deployment target.

## Verified production gate

The bootstrap/deployment path has already passed the production gate that the original 2026-08-14 version of this document described as pending.

Verified behavior includes:

```text
VERTEX_GEMINI_LIVE=PASS
HEALTH=PASS provider=google_adk_vertex model=gemini-3.5-flash judge_access=protected
JUDGE_API_AUTH=PASS unauthenticated_post=401
LIVE_ADK_BASELINE=PASS agents=4
TRUST_BREAK=PASS blocked=publish_action reused=scout
SELECTIVE_RECOVERY=PASS rerun=3 reused=1 final_action=VERIFIED
```

Current production configuration remains intentionally bounded:

- Cloud Run `min=0`, `max=1`;
- one CPU and 512 MiB;
- dedicated runtime/build/deployer service accounts;
- Secret Manager judge credential;
- keyless GitHub Workload Identity Federation restricted to the exact repository/owner/`main` branch;
- process-local live model-call guard to reduce accidental public-demo traffic.

The live-call guard is **not** a billing cap.

## Google Agent Registry

The existing Cloud Run fleet entry point is also registered and discoverable in Google Agent Registry:

```text
Service: projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
Agent: projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
Workflow: 31871557186
Discovery: PASS
```

Agent Registry is catalog/discovery control plane only. It does not authorize Trust Graph state or actions.

## Persistence boundary

The current live run store remains process-local. This document does not claim durable multi-week context, Firestore persistence, BigQuery export, Agent Runtime, Memory Bank, or Model Armor.

A durable storage integration may be evaluated separately, but storage existence must never imply trusted state; persisted checkpoints must still pass deterministic revalidation.
