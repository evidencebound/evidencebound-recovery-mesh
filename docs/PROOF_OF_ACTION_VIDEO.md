# Proof-of-Action video receipt

**Current public submission video:** V1 remains public and submitted until Video V2 has a public YouTube/Vimeo URL.

Current Devpost video of record:

`https://youtu.be/AExuVCC-m7o`

**Video V2 status:** `LOCAL ASSEMBLY VERIFIED / PUBLICATION PENDING`.

The V2 master is the stronger autonomy proof because it preserves the complete hands-off production execution captured by the current `?autorun=stale_evidence&recover=1` route. It must not replace V1 in Devpost until a public YouTube/Vimeo URL exists and is read back successfully.

Detailed V2 hashes and integrity checks: [`VIDEO_V2_PROOF_PACKAGE.md`](VIDEO_V2_PROOF_PACKAGE.md).

## Video V2 judge sequence

```text
TRUST BREAK
  -> EXACT BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

The centerpiece is the complete `24.080 s` hands-off production segment from capture run `run-06fdaf68fdff`.

Verified assembly receipt:

```text
V2 duration:          75.080 s
Resolution:           1920x1080
Frame rate:           25 fps
Upload codec:         H.264
Continuous segment:   24.080 s / 602 frames
Internal cuts:        NONE
Internal overlays:    NONE
Speed changes:        NONE
Frame equality:       PASS — 602 / 602 source frames
```

The continuous source run is preserved in full. Evidence cards before and after it are clearly separated from the live execution and do not masquerade as Google Cloud Console screenshots.

## V2 continuous-capture receipt

```text
Capture run:          run-06fdaf68fdff
Provider:             google_adk_vertex
Model:                gemini-3.5-flash
Full restart:         4 model calls / 1744 input tokens
Selective recovery:  3 model calls / 1366 input tokens
Saved in that run:    1 model call / 378 input tokens (~22%)
Unaffected work:      Scout REUSED
Final state:          VERIFIED
```

These values belong only to the capture run and are not generalized.

## Current production acceptance shown separately

The newer production acceptance is a distinct receipt and is not mixed with capture metrics:

```text
Workflow:             32817763402
Revision:             evidencebound-recovery-mesh-00006-tc4
Acceptance run:       run-6d1427ccb2ca
Provider / model:     google_adk_vertex / gemini-3.5-flash
Live agents:          4
Trust break:          publish_action BLOCKED
Reuse / rerun:        Scout REUSED / 3 rerun / 1 reused
Full restart:         4 model calls / 1739 input tokens
Selective recovery:  3 model calls / 1388 input tokens
Final action:         VERIFIED
Unauthenticated POST: 401
```

## Google Cloud / enterprise control-plane proof

V2 visibly identifies the verified Google execution boundary using traceable production receipts:

- canonical Cloud Run `.run.app` URL;
- current Cloud Run revision `evidencebound-recovery-mesh-00006-tc4`;
- Google ADK `2.7.0`;
- Vertex AI / `gemini-3.5-flash` through provider `google_adk_vertex`;
- protected judge API receipt;
- Google Agent Registry workflow `31871557186`;
- Registry Service `recovery-mesh-fleet`;
- generated read-only Agent discovery `PASS`.

The Cloud Run / Vertex card reproduces values from authenticated `gcloud` and live `/health` acceptance receipts. It is explicitly **not** represented as a Google Cloud Console screenshot. Agent Registry remains catalog/discovery control plane only and cannot override Recovery Mesh trust state or action authorization.

## Explicit non-claims

Neither V1 nor V2 claims durable multi-week context, Firestore persistence, BigQuery export, Agent Runtime, Memory Bank, Model Armor, or separate Agent Registry entries for each internal ADK role.

The live run store remains process-local in this bounded hackathon deployment. Durable persistence remains a separated enterprise extension boundary.

## Publication gate

Replace the Devpost V1 URL only after all of the following are true:

1. the V2 H.264 MP4 is public on YouTube or Vimeo;
2. the public URL opens without owner authentication;
3. English subtitles are attached or equivalent English accessibility is present;
4. Devpost readback shows that exact V2 URL.

Until that gate passes, V1 is the truthful public video of record and V2 is a verified publication-ready master, not a claimed public asset.
