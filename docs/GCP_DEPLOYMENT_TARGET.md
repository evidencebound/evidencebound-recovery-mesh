# Google Cloud deployment target

Status as of 2026-08-14.

- Hackathon Google Cloud project ID: `evidencebound-rm-c977c1`
- Project number: `457699623691`
- Project name: `EvidenceBound Recovery Mesh`
- Lifecycle state observed at creation: `ACTIVE`
- Project label: `hackathon=all-things-agentic-2026`
- Intended Cloud Run region: `europe-west1`
- Intended Vertex location: `global`
- Intended model: `gemini-3.5-flash`
- Intended service name: `evidencebound-recovery-mesh`

## Isolation decision

This project was created specifically for the All Things Agentic 2026 hackathon deployment so Cloud Run, Vertex AI, IAM identities, logs, and billing evidence are isolated from older Google Cloud workloads.

The legacy project `vocal-lightning-7dmzd` received a deletion request on 2026-08-14 and was observed in lifecycle state `DELETE_REQUESTED`. It is not a Recovery Mesh deployment target and must not be modified by Recovery Mesh bootstrap scripts.

## Bootstrap safety boundary

`scripts/gcp-owner-bootstrap.sh` is now locked by default to this exact project ID and project number. Before enabling APIs or creating IAM resources it also verifies:

- project lifecycle is `ACTIVE`;
- the hackathon label matches `all-things-agentic-2026`;
- billing is already enabled.

A mismatch emits `BLOCKER=...` and exits before Google Cloud mutation.

## Current gate

Billing is not yet verified as enabled on this new project. Do not claim live Gemini, Cloud Run deployment, hosted judge URL, or Google Cloud production acceptance until a real bootstrap receipt proves them.

After billing is enabled, use current public `main` and `scripts/gcp-owner-bootstrap.sh` with `GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1`. The bootstrap must emit its live receipts before Google Cloud claims are promoted into the Devpost submission.
