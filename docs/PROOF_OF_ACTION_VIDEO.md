# Final Proof-of-Action video receipt

**Status: PUBLIC / SUBMITTED.**

Public YouTube video:

`https://youtu.be/AExuVCC-m7o`

Final title:

`EvidenceBound Recovery Mesh — Proof of Action | Google All Things Agentic 2026`

Final duration: approximately **3:28**, below the hackathon's ~4-minute limit.

## What the final video proves

The video preserves the judge sequence:

```text
TRUST BREAK
  -> EXACT BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

It uses sanitized captures from the protected production judge flow, not mock UI states.

Fresh browser-capture workflow:

```text
GitHub Actions workflow: judge-video-capture
Run: 31876152726
Result: SUCCESS
Provider: GOOGLE_ADK_VERTEX / GEMINI-3.5-FLASH
Fresh captured run: run-72e5ad9cd0e8
```

The capture workflow retrieves the private judge key through the existing WIF + Secret Manager control path, masks it before browser use, drives the production UI with Playwright, and uploads only sanitized screenshots/receipts. The judge-key value is never present in the public video.

## Fresh measured run shown in the final video

```text
Full restart:        4 model calls / 1788 input tokens
Selective recovery: 3 model calls / 1427 input tokens
Saved:               1 model call / 361 input tokens (20% for this controlled run)
```

These numbers belong to the fresh capture shown in the final video.

## Reference acceptance benchmark

The video separately labels the earlier production acceptance receipt:

```text
Acceptance run:      run-4707af5a2fb6
Full restart:        4 model calls / 1781 input tokens
Selective recovery: 3 model calls / 1358 input tokens
Saved:               1 model call / 423 input tokens (~24% for that controlled run)
```

Live Gemini token usage varies between runs, so neither percentage is presented as a universal savings claim.

## Fleet-scale proof

A separate deterministic graph probe is explicitly labeled synthetic graph-scale evidence:

```text
100 agent checkpoints
14 affected
86 reused
1 blocked action
```

The video does **not** present this as 100 live Gemini calls.

## Google Cloud / enterprise control-plane proof

The final cut identifies the verified stack and receipts:

- Cloud Run revision `evidencebound-recovery-mesh-00005-82k`;
- Google ADK `2.7.0`;
- Vertex AI / `gemini-3.5-flash`;
- Secret Manager judge credential by **name/version only**;
- keyless Workload Identity Federation;
- Google Agent Registry workflow `31871557186`;
- Registry Service `recovery-mesh-fleet`;
- generated read-only Agent discovery `PASS`.

Agent Registry is shown as catalog/discovery control plane only. It does not override the deterministic Trust Graph or action gate.

## Explicit non-claims retained in the video

The final video does not claim durable multi-week context, Firestore persistence, BigQuery export, Agent Runtime, Memory Bank, Model Armor, or separate Agent Registry entries for each internal ADK role.

The live run store remains process-local in this bounded hackathon deployment. Durable persistence remains a separated enterprise extension boundary.

## Audio / accessibility

- English ElevenLabs narration.
- English YouTube subtitles uploaded from the exact voiceover transcript.
- Music: `Technology - Tech Technology` by APALONBeats, downloaded under the Pixabay Content License.

The video is the final public Proof-of-Action asset referenced by the Devpost submission.