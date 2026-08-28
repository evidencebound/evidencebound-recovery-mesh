# Final Judge-Proof Sync Plan

Date: 2026-08-28
Scope: submission evidence and judge-facing documentation only. No Recovery Mesh runtime, trust semantics, deployment, model configuration, or Google Cloud mutation.

## Outcome

Make repository, production receipt, Video V2 evidence package, and Devpost describe the same verified system before the All Things Agentic submission deadline.

## Source of truth

- Repository: `evidencebound/evidencebound-recovery-mesh`
- Pre-sync main: `699bf5cca14a3e0a5ea62d9d0e534a54839b33f7`
- Current Cloud Run revision: `evidencebound-recovery-mesh-00006-tc4`
- Live acceptance run: `run-6d1427ccb2ca`
- Live acceptance workflow: `32817763402`
- Hands-off route: `?autorun=stale_evidence&recover=1`
- Current live receipt: 4 baseline Google ADK agents; trust break blocks `publish_action`; Scout reused; 3 agents rerun / 1 reused; final action `VERIFIED`; 4→3 model calls; 1739→1388 input tokens.
- Video V2 continuous capture artifact: `recovery-mesh-video-v2-live-capture`, capture run `run-06fdaf68fdff`; 24.08 s untouched live segment; 4→3 model calls; 1744→1366 input tokens.
- Agent Registry production receipt: workflow `31871557186`, `AGENT_REGISTRY=PASS`, service `recovery-mesh-fleet`, discovery `PASS`.

## Deliverable 1 — submission truth sync

1. Update README current production receipt to revision `00006-tc4` and run `run-6d1427ccb2ca`.
2. Make the hands-off route `?autorun=stale_evidence&recover=1` the fastest judge path.
3. Keep manual inspection route explicitly separate.
4. Update `docs/JUDGE_TESTING_INSTRUCTIONS.md` reference receipt to the same current production acceptance.
5. Do not conflate the Video V2 capture run with the newer production acceptance run.

Acceptance: repository judge-facing docs contain no stale `00005-82k` or `00004-24m` production claim in the current-path sections and accurately distinguish current acceptance from capture evidence.

## Deliverable 2 — Video V2 proof package

1. Preserve `video-v2-live-segment.webm` as an internally untouched continuous Proof-of-Action segment.
2. Surround it only with clearly labeled evidence cards; do not cut, splice, or overlay inside the continuous segment.
3. Show verified Google-owned evidence: `.run.app` Cloud Run endpoint, current revision `00006-tc4`, Google ADK / Vertex Gemini 3.5 Flash live acceptance, and Agent Registry production receipt.
4. Show capture-run metrics only with capture run `run-06fdaf68fdff`.
5. Produce an English-captioned MP4 under 4 minutes plus SRT, receipt, and SHA-256.

Acceptance: final media is ≤240 s, 1920×1080, contains the complete 24.08 s capture segment without internal edits, and every mutable claim is traceable to a verified receipt.

## Deliverable 3 — Devpost propagation

1. Update live Devpost text from revision `00005-82k` to current revision `00006-tc4` and current acceptance receipt.
2. Preserve canonical repo URL `https://github.com/evidencebound/evidencebound-recovery-mesh` because live Devpost already uses it.
3. Keep V1 video URL until V2 has a public YouTube/Vimeo URL; never point Devpost at a local/unpublished artifact.
4. After V2 publication, replace the Devpost video field and synchronize `docs/PROOF_OF_ACTION_VIDEO.md`.

Acceptance: public Devpost, public repository, public video, and current production evidence describe one working system.

## Verification and rollback

- Review PR diff before merge.
- Confirm docs-only changes do not match the `gcp-live-acceptance` automatic trigger path (`.github/live-acceptance.trigger`) and therefore do not mutate production.
- After merge, verify current `main`, current Cloud Run live acceptance receipt, and public Devpost readback.
- Rollback is a revert of the docs-only merge; no production runtime state is changed by this plan.
