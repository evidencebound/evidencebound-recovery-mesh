# Proof-of-Action video status

**Current public submission video:** V1 remains public and submitted until the new current-production proof video has a public YouTube/Vimeo URL and Devpost readback confirms it.

Current Devpost video of record:

`https://youtu.be/AExuVCC-m7o`

The previously assembled 75.080-second Video V2 package remains a valid historical artifact for its own captured run, but it predates the now-live Firestore Durable Trust Ledger and exact-run Google Cloud Logging proof. It should therefore **not** be treated as the final strongest submission video.

## Final video target

The new public proof video should use the current production truth:

```text
Cloud Run revision:   evidencebound-recovery-mesh-00007-bjm
Deployment workflow:  33196157041 — SUCCESS
Acceptance workflow:  33196523402 — SUCCESS
Acceptance run:       run-4f1eba151be7
Provider:             google_adk_vertex
Model:                gemini-3.5-flash
Persistence:          firestore / durable=true
Exact-run Cloud Logs: PASS
GCP proof receipt:    PASS
```

The judge sequence remains:

```text
TRUST BREAK
  -> EXACT BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

## Current production receipt to show

Measured values for `run-4f1eba151be7` only:

```text
Full restart:        4 model calls / 1707 input tokens
Selective recovery: 3 model calls / 1432 input tokens
Saved in this run:   1 model call / 275 input tokens (~16.1%)
Blocked receipt:     0 durable action receipts
Recovered receipt:   exactly 1 durable action receipt
Rehydration:         trusted only after deterministic validation
Final action:        VERIFIED
```

Do not generalize the token saving percentage beyond this run.

## Real Google Cloud proof requirement

The final edit should replace generic cloud-proof cards with a short real Google Cloud Console/Cloud Shell segment wherever possible.

The visible proof should establish:

- project `evidencebound-rm-c977c1`;
- Cloud Run service `evidencebound-recovery-mesh`;
- revision `evidencebound-recovery-mesh-00007-bjm`;
- `.run.app` service URL;
- `/health` reporting `google_adk_vertex`, `gemini-3.5-flash`, `firestore`, `durable=true`;
- Firestore `(default)` database in `europe-west1`;
- Cloud Logging entries for the exact Recovery Mesh causal events;
- Google Agent Registry API/service only if the terminal output is clean and current.

Never display access tokens, API keys, judge-key values, credentials files, or private payloads.

## Hands-off Recovery Mesh segment

The production UI route is:

`https://evidencebound-recovery-mesh-i3lzjodgra-ew.a.run.app/?autorun=stale_evidence&recover=1`

After the private judge key is entered and controls are unlocked, the hands-off sequence should remain continuous through:

```text
verified baseline
-> controlled stale-evidence trust break
-> exact blast radius
-> publish_action BLOCKED
-> Scout REUSED
-> affected branch recomputation
-> deterministic re-verification
-> durable action receipt commit
-> VERIFIED recovery
```

The judge must not choose the repair set.

## Firestore proof boundary

The current live integration is no longer an architectural extension. Firestore is active production persistence through the Durable Trust Ledger.

Verified live invariant:

```text
FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0
DURABLE_RECOVERY=PASS receipt=present rehydration=trusted
FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1
```

Do not state that this exact acceptance forced a Cloud Run instance kill/restart. That was not part of the live run.

## Cloud Logging proof boundary

Workflow `33196523402` queried Google Cloud Logging under a separate read-only auditor identity for the exact same `run-4f1eba151be7` and returned:

```text
EXACT_RUN_CLOUD_LOGGING=PASS
GCP_PROOF_RECEIPT=PASS
```

The observed event sequence includes:

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

This is the strongest external audit proof to include after the live UI segment.

## Google Agent Registry boundary

Historical verified control-plane receipt remains:

```text
Workflow: 31871557186
AGENT_REGISTRY=PASS
AGENT_REGISTRY_SERVICE=projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
AGENT_REGISTRY_DISCOVERY=PASS
```

It is catalog/discovery only and is not a trust-authority claim.

## Recommended final structure

Target approximately 70–100 seconds, comfortably below the four-minute limit:

1. `4–6 s` — problem + Recovery Mesh thesis;
2. `20–35 s` — real Google Cloud Shell/Console proof for current production revision, Firestore and Cloud Logging;
3. `24–35 s` — continuous hands-off Recovery Mesh trust-break/recovery sequence;
4. `8–12 s` — measured selective-recovery receipt + durable `0 -> 1` action-receipt proof;
5. `5–8 s` — close with hosted URL and Fortified Enterprise Fleet framing.

Keep any live proof segment honest and unedited internally except for trimming empty lead-in/lead-out. Do not create fake terminal output, fake Google Console cards, or staged PASS screens.

## Explicit non-claims

The final video should not claim without separate evidence:

- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- universal savings percentages;
- forced Cloud Run process-kill production replay proving restart-surviving exactly-once behavior;
- separate Registry entries for each internal ADK role.

## Publication gate

Replace the Devpost V1 URL only after all of the following are true:

1. the new H.264 MP4 is public on YouTube or Vimeo;
2. the public URL opens without owner authentication;
3. English subtitles or equivalent English accessibility are present;
4. Devpost readback shows that exact new URL.

Until that gate passes, V1 remains the public video of record.

Canonical current receipt: [`FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md`](FORTIFIED_PRODUCTION_RECEIPT_2026-08-28.md).
