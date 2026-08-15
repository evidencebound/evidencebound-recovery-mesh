# <=4-minute Proof-of-Action video plan

**Status: recording pending.** This is the final recording script, not proof that a public video has already been recorded or uploaded.

Current production deployment:

```text
Cloud Run revision: evidencebound-recovery-mesh-00005-82k
Provider: google_adk_vertex
Model: gemini-3.5-flash
Latest deployment smoke: run-439f7d87c2a3
```

Reference acceptance benchmark requested for the submission narrative:

```text
Acceptance run: run-4707af5a2fb6
Full restart: 4 model calls / 1781 input tokens
Selective recovery: 3 model calls / 1358 input tokens
Measured saving: 1 model call / 423 input tokens (~24%)
```

The fresh run recorded in the video can have different token counts. **Never narrate the reference numbers as if they came from a different live run.** Show the fresh run's actual Flight Recorder values first; then, if desired, show the README's clearly labeled reference acceptance receipt with `1781 / 1358`.

## Pre-recording security setup — not shown in video

- Open the live Flight Recorder.
- Retrieve the private judge testing key locally from Secret Manager.
- Enter it into the **Bounded Judge Access** box before recording begins.
- Verify the UI says the key is stored/unlocked.
- Never show the secret value, Secret Manager reveal dialog, terminal output containing the value, browser devtools request headers, or Devpost private testing field in the recording.
- The public video may show only that judge access is protected, never the credential itself.

## 0:00-0:20 — Problem and product

Show the live Cloud Run Flight Recorder and say:

> EvidenceBound Recovery Mesh is a trust-aware flight recorder and selective self-healing engine for autonomous agent fleets. A trust break freezes unsafe action, computes exact downstream impact, preserves still-verifiable work, reruns only affected agents, then re-verifies before resuming.

Keep the Cloud Run origin visible. Do not place credentials in the URL.

## 0:20-0:45 — Working fleet

Create a fresh protected production run. Show:

- judge controls unlocked without revealing the key;
- `google_adk_vertex`;
- `gemini-3.5-flash`;
- four ADK roles: Statistician, Scout, Skeptic, Orchestrator;
- baseline checkpoints `VERIFIED`.

Do not call deterministic test execution a Gemini run. Do not show the private request header.

## 0:45-1:25 — Trust break and action block

Inject the visibly labeled controlled `stale_evidence` fault through the production UI/API.

Show, in this order:

1. `TRUST BREAK` at `history_snapshot`;
2. exact blast radius;
3. `publish_action = BLOCKED`;
4. `scout = VERIFIED · REUSED`;
5. recomputation set selected by Recovery Mesh, not by the judge.

Core visual moment:

```text
TRUST BREAK -> BLAST RADIUS -> ACTION BLOCKED
```

Hold this screen long enough for the red trust-break node, affected edges, blocked action, and green reused Scout to be readable.

## 1:25-2:10 — Selective autonomous recovery

Trigger **Autonomous selective recovery** once. Show that only Statistician, Skeptic, and Orchestrator rerun while Scout remains reused.

Show the affected checkpoints re-verifying and `publish_action` resuming only after dependencies become `VERIFIED`.

Core visual moment:

```text
SAFE WORK REUSED -> AFFECTED BRANCH RECOMPUTED -> VERIFIED RECOVERY
```

## 2:10-2:45 — Measured production receipt

Keep the fresh run's benchmark panel visible. Read the **numbers actually shown on screen**.

Then spend a few seconds on the README reference receipt and say:

> Our reference production acceptance run measured a full restart at 4 model calls and 1781 input tokens versus selective recovery at 3 calls and 1358 input tokens — one call and 423 input tokens saved, about 24% for that controlled run. Live Gemini token counts vary, so the Flight Recorder reports each run's actual values.

This satisfies the requested `1781 vs 1358` proof without misattributing it to the fresh recording run.

## 2:45-3:08 — Fleet-scale proof

Show the deterministic 100-agent-checkpoint scale probe separately and label it clearly as **synthetic deterministic graph scale**, not 100 live Gemini calls.

Current locked scale receipt:

```text
100 agent checkpoints
14 affected
86 reused
1 blocked action
```

## 3:08-3:40 — Google Cloud + security proof

Show Google Cloud Console evidence for the exact deployment:

- project `evidencebound-rm-c977c1`;
- Cloud Run service `evidencebound-recovery-mesh`;
- revision `evidencebound-recovery-mesh-00005-82k`;
- runtime service account;
- live `.run.app` URL;
- recent request/log evidence;
- Secret Manager secret **name/version only**: `recovery-mesh-judge-key:1`;
- sanitized receipt: `JUDGE_API_AUTH=PASS unauthenticated_post=401`.

Do not reveal the secret value. Do not claim Gemini Enterprise Agent Platform services unless separately invoked and verified.

## 3:40-3:58 — Close

Show the recovered trust graph and final action state. Close with:

> Recovery Mesh does not trust persisted state because it exists. It reuses work only while its evidence, integrity, dependencies, provenance, and policy remain verifiable.

Target final duration: **3:45–3:58**. The final video must be public on YouTube or Vimeo and in English or have English subtitles.
