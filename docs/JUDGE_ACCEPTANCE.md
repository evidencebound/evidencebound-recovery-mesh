# Judge acceptance gate

Status as of 2026-08-28: **CORE PRODUCTION ACCEPTANCE SATISFIED / VIDEO V2 PUBLICATION PENDING**.

This file records the acceptance standard and the evidence class that satisfies it. It separates current production acceptance from the remaining public-video publication gate.

## Accepted production evidence

The current public repository contains the hackathon implementation, disclosure, reproducible README, tests, architecture documentation, and green CI on `main`.

Production evidence verifies:

- Gemini 3.5 Flash is invoked with real Google credentials through Vertex AI;
- execution provider is `google_adk_vertex` with Google ADK `2.7.0`;
- the hosted deployment is Cloud Run revision `evidencebound-recovery-mesh-00006-tc4`;
- public health endpoint is `/health`;
- Secret Manager contains the dedicated judge credential while the value remains absent from source/public receipts;
- unauthenticated `POST /api/runs` returns `401` before model execution;
- four specialized live ADK roles participate in the baseline;
- controlled `stale_evidence` invalidates `history_snapshot`;
- exact dependency traversal blocks `publish_action` and preserves `scout`;
- the preferred `?autorun=stale_evidence&recover=1` path performs recovery without a human selecting the repair set or triggering recovery after the fault;
- autonomous selective recovery reruns only Statistician, Skeptic, and Orchestrator;
- recomputed checkpoints are deterministically re-verified;
- `publish_action` resumes only after dependency trust passes;
- duplicate side effects remain idempotency-protected within the current process-local ledger boundary;
- benchmark receipts compare actual full-restart and selective-recovery paths;
- Flight Recorder shows the six-step causal sequence from runtime state;
- Workload Identity Federation is used for keyless GitHub deployment rather than a service-account key;
- Google Agent Registry contains a discoverable Recovery Mesh fleet entry point;
- README, Devpost description, judge instructions, and current production receipts describe the same bounded system.

## Judge moment

```text
TRUST BREAK
  -> EXACT BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

## Current production acceptance receipt

```text
Workflow:             32817763402
Revision:             evidencebound-recovery-mesh-00006-tc4
Run:                  run-6d1427ccb2ca
Provider / model:     google_adk_vertex / gemini-3.5-flash
Live agents:          4
Trust break:          publish_action BLOCKED
Unaffected work:      Scout REUSED
Selective recovery:  3 rerun / 1 reused
Full restart:         4 model calls / 1739 input tokens
Selective recovery:  3 model calls / 1388 input tokens
Saved in that run:    1 model call / 351 input tokens (~20%)
Final action:         VERIFIED
Unauthenticated POST: 401
```

These are controlled-run measurements, not universal savings claims.

## Video V2 evidence class

Video V2 uses a different live capture run and does not mix its metrics with the current acceptance receipt:

```text
Capture run:          run-06fdaf68fdff
Capture mode:         HANDS_OFF_STAGED_AUTORUN
Full restart:         4 model calls / 1744 input tokens
Selective recovery:  3 model calls / 1366 input tokens
Saved in that run:    1 model call / 378 input tokens (~22%)
Continuous segment:   24.080 s / 602 frames
Frame equality:       PASS — 602 / 602 preserved in assembled WebM
Final state:          VERIFIED
```

The assembled V2 master is `75.080 s`, 1920×1080, and under the four-minute limit. Its local assembly is verified, but it is **not** claimed as the public submission video until a public YouTube/Vimeo URL exists and Devpost readback confirms it.

Current public Devpost video remains V1: `https://youtu.be/AExuVCC-m7o`.

## Agent Registry acceptance

The separate keyless registration workflow passed only after the Google long-running operation completed and the generated read-only Agent became observable:

```text
Workflow: 31871557186
AGENT_REGISTRY=PASS
Service: projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
Agent: projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_DISCOVERY=PASS
```

The Registry receipt is production control-plane evidence from 2026-08-15. It is not presented as a new 2026-08-28 registration.

## Evidence-class discipline

The following remain separate evidence classes and are not substituted for each other:

- deterministic/local tests do not prove live Gemini execution;
- the 100-checkpoint synthetic scale probe does not prove 100 live Gemini calls;
- a diagram does not prove a Google integration;
- an authenticated workflow receipt is not represented as a Google Cloud Console screenshot;
- persisted state would not automatically become trusted state;
- Agent Registry catalog/discovery does not authorize Recovery Mesh trust state;
- V2 local verification does not prove public YouTube/Vimeo publication.

## Known limitation / non-claims

Core acceptance does **not** mean the submission demonstrates every recommended Fortified Enterprise Platform component.

The live deployment still uses process-local hot state and therefore does not claim:

- durable multi-week context;
- Firestore persistence;
- BigQuery export;
- Agent Runtime;
- Memory Bank;
- Model Armor;
- restart-surviving exactly-once semantics.

Those limitations are intentional truth boundaries, not hidden PASS claims.

## Remaining gate

The only submission-media gate in this document is public Video V2 publication and Devpost readback. Until that occurs, V1 remains the truthful public video of record.
