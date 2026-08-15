# Submission preflight — 2026-08-15

## Core production evidence

Current submission-ready deployment:

- Cloud Run revision: `evidencebound-recovery-mesh-00005-82k`
- Current revision smoke run: `run-439f7d87c2a3`
- Provider: `google_adk_vertex`
- Model: `gemini-3.5-flash`
- Live baseline: 4 Google ADK agents
- Trust break: stale evidence at `history_snapshot`
- Blocked action: `publish_action`
- Reused agent checkpoint: `scout`
- Selective reruns: `statistician`, `skeptic`, `orchestrator`
- Final action: `VERIFIED`
- Current smoke: full restart 4 calls / 1728 input tokens; selective recovery 3 calls / 1393 input tokens

Reference production acceptance receipt:

- run: `run-4707af5a2fb6`
- full restart: 4 model calls / 1781 input tokens
- selective recovery: 3 model calls / 1358 input tokens
- controlled-run saving: 1 model call / 423 input tokens (~24%)

## Submission checklist

- [x] Core live Google ADK / Gemini / Cloud Run acceptance
- [x] Fail-closed judge API auth receipt (`401` without key)
- [x] Trust Graph / blast-radius UI implemented
- [x] Final UI patch deployed: safe `/health`, judge autorun after unlock, historical trust-break/reuse visibility, exact benchmark counts
- [x] Final UI revision passed protected end-to-end Cloud Run smoke
- [x] Judge-first README prepared
- [x] Architecture diagram available in README Mermaid
- [x] Reproducible local setup instructions prepared
- [x] Judge testing instructions prepared
- [x] <=4-minute video script locked to measured receipts with live-vs-reference distinction
- [x] Public technical article draft prepared
- [x] Social-post draft prepared
- [x] Devpost description updated from pre-production wording to current production receipts
- [ ] Browser-level screenshot/video capture confirms the final graph visually in a real browser
- [ ] Final public demo video recorded and uploaded to YouTube/Vimeo
- [ ] Architecture diagram file confirmed/uploaded in required Devpost file field
- [ ] Public technical article published and URL added to Devpost
- [ ] Social post published with `#AllThingsAgenticHackathon` and URL added to Devpost
- [ ] Optional additional Google AI model: only if genuinely integrated and verified; no bonus currently claimed
- [ ] Final Devpost form audited and submitted/updated with video and any bonus URLs

## Scope decision

AdsForge is excluded from the core submission. A second workload is not worth destabilizing a production-accepted judge journey. The bounded four-agent workload already demonstrates specialization, deterministic trust propagation, fail-closed action, exact blast radius, selective recovery, and measured reuse.

No Gemini Enterprise Agent Platform service is claimed unless a real invocation and receipt are separately verified. The current demo's run store is process-local; durable multi-week enterprise memory remains an explicit Fortified-track gap rather than a fabricated claim.
