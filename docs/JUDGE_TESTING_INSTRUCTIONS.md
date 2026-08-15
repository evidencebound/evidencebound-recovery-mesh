# Devpost judge testing instructions

Hosted app:

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/`

Fastest Proof-of-Action route:

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/?autorun=stale_evidence`

1. Open the Proof-of-Action route.
2. Enter the private judge testing key supplied in the Devpost judge-only field and click **Unlock controls**. Do not place the key in the URL.
3. The app creates a fresh Google ADK / Gemini 3.5 Flash baseline and injects the controlled stale-evidence fault through the production API.
4. Observe: `history_snapshot · TRUST BREAK`, exact red blast-radius edges, `publish_action = BLOCKED`, and `scout · REUSED`.
5. Click **3 · Autonomous selective recovery**.
6. Observe that Statistician, Skeptic, and Orchestrator rerun, Scout is preserved, and `publish_action` returns to `VERIFIED` only after re-verification.
7. Read the measured benchmark panel. The values are generated from the current run; do not expect them to exactly match the reference acceptance receipt below because Gemini token usage can vary between runs.

Reference production acceptance receipt from 2026-08-15:

- revision: `evidencebound-recovery-mesh-00004-24m`
- run: `run-4707af5a2fb6`
- full restart: `4 model calls / 1781 input tokens`
- selective recovery: `3 model calls / 1358 input tokens`
- saved in that run: `1 model call / 423 input tokens (~24%)`
- unauthenticated `POST /api/runs`: `401`

Security note: the judge key is stored by the browser only in tab-scoped `sessionStorage`; it is sent as `X-Recovery-Mesh-Judge-Key`. Run objects are process-local, so old run IDs are not promised as durable permalinks after Cloud Run scales to zero. The reproducible path is to create a fresh live run using the route above.
