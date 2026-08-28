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
6. In the Durable Trust Ledger panel, confirm that the blocked state has **no committed action receipt**, and that verified recovery produces a committed durable receipt only after deterministic re-verification.
7. Read the measured benchmark panel. The values are generated from the current run; do not expect them to exactly match the reference acceptance receipt below because Gemini token usage can vary between runs.

Manual inspection route:

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/?autorun=stale_evidence`

The manual route intentionally stops at the blocked trust-break state so a judge can inspect the blast radius before clicking **3 · Autonomous selective recovery**. The hands-off route above is the stronger autonomy demonstration because the operator does not select the repair set or trigger recovery after the controlled fault has been introduced.

## Reference fortified production receipt — 2026-08-28

- Cloud Run revision: `evidencebound-recovery-mesh-00007-bjm`
- deployment workflow: `33196157041` — SUCCESS
- acceptance + exact-run cloud-proof workflow: `33196523402` — SUCCESS
- acceptance run: `run-4f1eba151be7`
- provider: `google_adk_vertex`
- model: `gemini-3.5-flash`
- persistence: `firestore`, `durable=true`
- live baseline: `4` Google ADK agents
- full restart: `4 model calls / 1707 input tokens`
- selective recovery: `3 model calls / 1432 input tokens`
- saved in that run: `1 model call / 275 input tokens (~16.1%)`
- trust break: `history_snapshot / STALE_EVIDENCE`
- unsafe action: `publish_action = BLOCKED`
- blocked Firestore action receipt count: `0`
- unaffected work: `scout = REUSED`
- selective recovery: `3` agents rerun / `1` reused
- recovered Firestore action receipt count: `1`
- rehydration: `trusted only after validation`
- final action: `VERIFIED`
- unauthenticated `POST /api/runs`: `401`
- exact-run Cloud Logging: `PASS`
- GCP proof receipt: `PASS`

The metrics above belong only to `run-4f1eba151be7`. Do not combine token counts across runs.

## External Google Cloud proof

The acceptance workflow has a second job using a separate read-only auditor identity. For the exact same `run-4f1eba151be7`, Google Cloud Logging returned the causal event sequence containing:

```text
TRUST_BREAK_DETECTED
BLAST_RADIUS_COMPUTED
ACTION_BLOCKED
CHECKPOINT_REUSED
RECOMPUTE_STARTED
CHECKPOINT_REVERIFIED
ACTION_RESUMED
RECOVERY_COMPLETED
```

The workflow terminates with:

```text
EXACT_RUN_CLOUD_LOGGING=PASS
GCP_PROOF_RECEIPT=PASS
```

This proves that the production recovery sequence is externally observable in Google Cloud Logging. It does not make Cloud Logging the trust authority.

## Security and durability notes

The judge key is stored by the browser only in tab-scoped `sessionStorage`; it is sent as `X-Recovery-Mesh-Judge-Key`.

The live production revision now uses Firestore for the Durable Trust Ledger. Persisted state is not accepted merely because it exists in Firestore: Recovery Mesh revalidates dependency/input digests, provenance/integrity metadata and active policy before reuse. The current live acceptance proves the active Firestore data path and the `0 receipts while BLOCKED → exactly 1 receipt after VERIFIED recovery` invariant.

A forced Cloud Run instance-kill/restart was not part of this exact live acceptance, so judges should not interpret the receipt as a separate production proof of forced-restart exactly-once semantics. The reproducible judge path remains to create a fresh live run using one of the routes above.

Canonical evidence receipt: [`FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md`](FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md).
