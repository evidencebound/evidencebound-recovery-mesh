# Devpost judge testing instructions

Hosted app:

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/`

Preferred hands-off Proof-of-Action route:

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/?autorun=stale_evidence&recover=1`

1. Open the hands-off Proof-of-Action route.
2. Enter the private judge testing key supplied in the Devpost judge-only field and click **Unlock controls**. Do not place the key in the URL.
3. From that point, no human recovery action is required. The app creates a fresh Google ADK / Gemini 3.5 Flash baseline, renders it, injects the controlled stale-evidence fault, renders the blocked incident, and then calls the existing selective-recovery endpoint automatically.
4. Observe the visible sequence: verified baseline → `history_snapshot · TRUST BREAK` → exact red blast-radius edges → `publish_action = BLOCKED` → `scout · REUSED` → affected branch recomputation → final `VERIFIED` recovery.
5. Confirm that Statistician, Skeptic, and Orchestrator are rerun while Scout remains preserved.
6. Read the measured benchmark panel. The values are generated from the current run; do not expect them to exactly match the reference acceptance receipt below because Gemini token usage can vary between runs.

Manual inspection route:

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/?autorun=stale_evidence`

The manual route intentionally stops at the blocked trust-break state so a judge can inspect the blast radius before clicking **3 · Autonomous selective recovery**. The hands-off route above is the stronger autonomy demonstration because the operator does not select the repair set or trigger recovery after the controlled fault has been introduced.

Reference production acceptance receipt from 2026-08-28:

- revision: `evidencebound-recovery-mesh-00006-tc4`
- acceptance workflow: `32817763402`
- run: `run-6d1427ccb2ca`
- provider: `google_adk_vertex`
- model: `gemini-3.5-flash`
- live baseline: `4` Google ADK agents
- full restart: `4 model calls / 1739 input tokens`
- selective recovery: `3 model calls / 1388 input tokens`
- saved in that run: `1 model call / 351 input tokens (~20%)`
- trust break: `publish_action = BLOCKED`
- unaffected work: `scout = REUSED`
- selective recovery: `3` agents rerun / `1` reused
- final action: `VERIFIED`
- unauthenticated `POST /api/runs`: `401`

The reference metrics above belong only to `run-6d1427ccb2ca`. Video V2's continuous capture is a different live run (`run-06fdaf68fdff`) and carries its own per-run benchmark receipt. Do not combine token counts across runs.

Security note: the judge key is stored by the browser only in tab-scoped `sessionStorage`; it is sent as `X-Recovery-Mesh-Judge-Key`. Run objects are process-local, so old run IDs are not promised as durable permalinks after Cloud Run scales to zero. The reproducible path is to create a fresh live run using one of the routes above.
