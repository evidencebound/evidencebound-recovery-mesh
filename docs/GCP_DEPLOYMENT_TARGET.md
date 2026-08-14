# Google Cloud deployment target

Status as of 2026-08-14.

- Hackathon Google Cloud project ID: `evidencebound-rm-c977c1`
- Project number: `457699623691`
- Project name: `EvidenceBound Recovery Mesh`
- Lifecycle state observed at creation: `ACTIVE`
- Intended Cloud Run region: `europe-west1`
- Intended Vertex location: `global`
- Intended model: `gemini-3.5-flash`
- Intended service name: `evidencebound-recovery-mesh`

## Isolation decision

This project was created specifically for the All Things Agentic 2026 hackathon deployment so Cloud Run, Vertex AI, IAM identities, logs, and billing evidence are isolated from older Google Cloud workloads.

The previously inspected project `vocal-lightning-7dmzd` is not the deployment target and must not be modified by Recovery Mesh bootstrap scripts.

## Current gate

Billing is not yet verified as enabled on this new project. Do not claim live Gemini, Cloud Run deployment, or Google Cloud production acceptance until a real bootstrap receipt proves them.

After billing is enabled, use `scripts/gcp-owner-bootstrap.sh` with `GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1`. The bootstrap is fail-closed and must emit its live receipts before Google Cloud claims are promoted into the Devpost submission.
