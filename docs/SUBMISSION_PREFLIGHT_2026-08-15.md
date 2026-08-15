# Final submission preflight — 2026-08-15

## Current production evidence

- Cloud Run revision: `evidencebound-recovery-mesh-00005-82k`
- Provider: `google_adk_vertex`
- Model: `gemini-3.5-flash`
- Google ADK: `2.7.0`
- Live baseline: 4 specialized ADK agents
- Trust break: stale evidence at `history_snapshot`
- Blocked action: `publish_action`
- Reused agent checkpoint: `scout`
- Selective reruns: `statistician`, `skeptic`, `orchestrator`
- Final action: `VERIFIED`
- Google Agent Registry: `PASS`
- Agent Registry workflow: `31871557186`
- Agent Registry Service: `recovery-mesh-fleet`
- Agent Registry discovery: `PASS`

## Final video receipt

Public video:

`https://youtu.be/AExuVCC-m7o`

Fresh sanitized browser capture:

- workflow: `31876152726` — `SUCCESS`
- captured run: `run-72e5ad9cd0e8`
- full restart: `4 calls / 1788 input tokens`
- selective recovery: `3 calls / 1427 input tokens`
- saving in that run: `1 call / 361 input tokens (20%)`

Reference production acceptance remains separately labeled:

- run: `run-4707af5a2fb6`
- full restart: `4 calls / 1781 input tokens`
- selective recovery: `3 calls / 1358 input tokens`
- saving in that run: `1 call / 423 input tokens (~24%)`

These are controlled-run measurements, not universal savings claims.

## Final Devpost state

- Submission ID: `1136853`
- Status: `Submitted`
- Category: `Fortified Enterprise Fleet`
- Submitter type: `Team of individuals`
- Country: `Ukraine`
- Public repo: `https://github.com/moneyparking/evidencebound-recovery-mesh`
- Hosted judge UI: `https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/`
- Video URL: `https://youtu.be/AExuVCC-m7o`
- Architecture Diagram v2 uploaded in the required file field
- Google SDK answer: `Agent Development Kit (ADK)`
- Google Cloud service answer: `Cloud Run`
- Google AI model answer: `Gemini 3.5 Flash via Vertex AI`
- Bonus technical article URL added
- Bonus LinkedIn URL added with `#AllThingsAgenticHackathon`
- Devpost project thumbnail synchronized to the same visual identity as the YouTube thumbnail

## Final checklist

- [x] Core live Google ADK / Gemini / Cloud Run acceptance
- [x] Fail-closed judge API auth receipt (`401` without key)
- [x] Trust Graph / exact blast-radius UI
- [x] Current Cloud Run revision verified
- [x] Google Agent Registry Service + generated Agent discovery verified
- [x] Judge-first README with reproducible setup
- [x] Judge testing instructions
- [x] Protected browser-level capture of baseline / trust break / recovery / benchmark
- [x] Final public <=4-minute YouTube video
- [x] English subtitles
- [x] Architecture Diagram v2 uploaded
- [x] DEV.to bonus article published and URL added
- [x] LinkedIn bonus post published and URL added
- [x] Devpost project submitted
- [x] Submitter type changed from `Individuals` to `Team of individuals`
- [ ] Invited teammate has accepted the Devpost project invite and is visibly listed as a project member — owner-side verification required because the connector does not expose the team-member roster
- [ ] Optional additional Google AI model bonus — intentionally not claimed; no extra model was integrated merely for points

## Scope / truth boundary

Recovery Mesh is the submitted product. AdsForge remains outside the submitted runtime and is not represented as a hackathon-built Recovery Mesh workload.

The live deployment uses process-local hot state. Durable multi-week context, Firestore persistence, BigQuery export, Agent Runtime, Memory Bank and Model Armor remain explicit non-claims unless separately implemented and verified.

Google Agent Registry is a verified enterprise catalog/discovery integration for the Recovery Mesh fleet entry point; it is not trust authority and does not replace the deterministic verification, provenance, integrity, blast-radius or action-gating logic.

## Prize-oriented status

The submission now aligns with the three judging pillars:

1. **Innovation & Operational Utility (40%)** — autonomous trust-break detection, exact blast radius, fail-closed action, selective recovery and safe reuse.
2. **Architectural Discipline & Tech Stack (30%)** — deterministic trust boundary, specialized ADK roles, WIF, Secret Manager, Cloud Run, Agent Registry, explicit non-claims and failure handling.
3. **Demo & Production Readiness (30%)** — public Proof-of-Action video, live Google Cloud deployment evidence, clean architecture diagram, reproducible README, protected judge route and measured receipts.

Remaining owner-visible item: confirm that the invited teammate has accepted the Devpost project invite so the public team roster matches `Team of individuals` before judging.