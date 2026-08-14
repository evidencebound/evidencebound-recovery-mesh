# <=4-minute Proof-of-Action video plan

This is a recording plan, not evidence. Replace every bracketed value only after the live Google Cloud acceptance run produces the receipt.

## Pre-recording security setup — not shown in video

- Open the live Flight Recorder.
- Retrieve the private judge testing key locally from Secret Manager.
- Enter it into the **Bounded Judge Access** box before recording begins.
- Verify the UI says the key is stored/unlocked.
- Never show the secret value, Secret Manager reveal dialog, terminal output containing the value, browser devtools request headers, or Devpost private testing field in the recording.
- The public video may show only that judge access is protected, never the credential itself.

## 0:00-0:20 — Problem and product

Show the live Cloud Run Flight Recorder and one sentence:

> EvidenceBound Recovery Mesh is a trust-aware flight recorder and selective self-healing engine for autonomous agent fleets. A trust break freezes unsafe action, computes exact downstream impact, preserves still-verifiable work, reruns only affected agents, then re-verifies before resuming.

Keep the Cloud Run origin visible without exposing query-string credentials. The production UI does not use credentials in the URL.

## 0:20-0:45 — Working fleet

Create a fresh protected production run. Show:

- judge controls are unlocked without revealing the key;
- execution provider: `google_adk_vertex`;
- model: the actually deployed Gemini model;
- four ADK roles: Statistician, Scout, Skeptic, Orchestrator;
- all baseline checkpoints `VERIFIED`;
- ADK invocation receipts in the live run.

Do not call the deterministic test executor a Gemini run. Do not show the private request header.

## 0:45-1:25 — Trust break and action block

Inject the visibly labeled controlled `stale_evidence` fault through the production UI/API.

Show, in this order:

1. `TRUST BREAK DETECTED` at `history_snapshot`;
2. exact blast radius;
3. `publish_action = BLOCKED`;
4. `scout = VERIFIED` and explicitly reusable;
5. recomputation set selected by Recovery Mesh, not by the judge.

Core visual moment:

`TRUST BREAK -> BLAST RADIUS -> ACTION BLOCKED`

## 1:25-2:10 — Selective autonomous recovery

Trigger one recovery action. Show that only the affected agent branch reruns. For the stale-evidence scenario the expected agent reruns are Statistician, Skeptic, and Orchestrator; Scout remains reused.

Show each affected checkpoint moving through recompute and re-verification. Then show `publish_action` resuming only after dependencies become `VERIFIED`.

Core visual moment:

`SAFE WORK REUSED -> AFFECTED BRANCH RECOMPUTED -> VERIFIED RECOVERY`

## 2:10-2:43 — Measured receipt

Show only values from that exact production run:

- full-restart agent executions: `[LIVE_VALUE]`;
- selective-recovery agent executions: `[LIVE_VALUE]`;
- reused agent checkpoints: `[LIVE_VALUE]`;
- full-restart model calls: `[LIVE_VALUE_OR_NOT_EXPOSED]`;
- selective model calls: `[LIVE_VALUE_OR_NOT_EXPOSED]`;
- input/output tokens: `[LIVE_VALUES_OR_NOT_EXPOSED]`;
- elapsed times: `[LIVE_VALUES]`.

If ADK does not expose token usage in the events, say that token telemetry was unavailable for this run; do not estimate it.

## 2:43-3:10 — Fleet-scale proof

Show the deterministic 100-agent-checkpoint scale probe separately. Label it clearly as synthetic deterministic graph scale, not 100 live Gemini calls.

Show the exact measured receipt from the current build and avoid extrapolating the result beyond that run.

## 3:10-3:42 — Google Cloud + security proof

Show Google Cloud Console evidence for the exact deployed service:

- isolated hackathon project ID;
- Cloud Run service/revision;
- runtime service account;
- live service URL;
- recent Cloud Run request/log evidence from the same run;
- Secret Manager secret **name/version only** (`recovery-mesh-judge-key:1`), never reveal its value;
- production smoke receipt `JUDGE_API_AUTH=PASS unauthenticated_post=401` if visible in a sanitized terminal/log capture.

The security point is concise: public judge discovery remains easy, but run creation/read/fault/recovery operations reject unauthenticated traffic before model execution.

Do not claim Gemini Enterprise Agent Platform features unless separately invoked and verified.

## 3:42-3:58 — Close

Show the recovered trust graph and final action state. Close with:

> Recovery Mesh does not trust persisted state because it exists. It reuses work only while its evidence, integrity, dependencies, provenance, and policy remain verifiable.

Target final duration: 3:45-3:58.
