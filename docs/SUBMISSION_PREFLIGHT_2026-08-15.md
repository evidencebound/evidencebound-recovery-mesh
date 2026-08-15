# Submission preflight — 2026-08-15

## Core production evidence

- Cloud Run revision before final UI patch: `evidencebound-recovery-mesh-00004-24m`
- Production acceptance run: `run-4707af5a2fb6`
- Provider: `google_adk_vertex`
- Model: `gemini-3.5-flash`
- Live baseline: 4 Google ADK agents
- Trust break: stale evidence at `history_snapshot`
- Blocked action: `publish_action`
- Reused agent checkpoint: `scout`
- Selective reruns: `statistician`, `skeptic`, `orchestrator`
- Final action: `VERIFIED`
- Full restart: 4 model calls / 1781 input tokens
- Selective recovery: 3 model calls / 1358 input tokens
- Controlled-run saving: 1 model call / 423 input tokens (~24%)

## Submission checklist

- [x] Core live Google ADK / Gemini / Cloud Run acceptance
- [x] Fail-closed judge API auth receipt (`401` without key)
- [x] Trust Graph / blast-radius UI implemented
- [x] Final UI patch prepared: safe `/health`, judge autorun after unlock, historical trust-break/reuse visibility, exact benchmark counts
- [x] Judge-first README prepared
- [x] Architecture diagram available in README Mermaid
- [x] Reproducible local setup instructions prepared
- [x] Judge testing instructions prepared
- [x] <=4-minute video script locked to measured receipts
- [x] Public technical article draft prepared
- [x] Social-post draft prepared
- [ ] Final UI patch deployed and visually accepted
- [ ] Final public demo video recorded and uploaded to YouTube/Vimeo
- [ ] Architecture diagram file confirmed/uploaded in Devpost submission field
- [ ] Devpost description updated from pre-production wording to current production receipts
- [ ] Public technical article published and URL added to Devpost
- [ ] Social post published with `#AllThingsAgenticHackathon` and URL added to Devpost
- [ ] Optional additional Google AI model: only if genuinely integrated and verified; no bonus currently claimed
- [ ] Final Devpost form audited and submitted/updated

## Scope decision

AdsForge is excluded from the core submission. A second workload is not worth destabilizing a production-accepted judge journey. The bounded four-agent workload already demonstrates specialization, deterministic trust propagation, fail-closed action, exact blast radius, selective recovery, and measured reuse.

No Gemini Enterprise Agent Platform service is claimed unless a real invocation and receipt are separately verified.
