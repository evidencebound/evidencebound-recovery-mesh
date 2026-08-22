# Judge acceptance gate

Status as of 2026-08-22: **CORE PRODUCTION ACCEPTANCE SATISFIED**.

This file records the acceptance standard and the evidence class that satisfies it. It is no longer a pre-deployment blocker document.

## Accepted production evidence

The current public repository contains the hackathon implementation, disclosure, reproducible README, tests, architecture documentation, and a green final audit CI on `main`.

Production evidence verifies:

- Gemini 3.5 Flash is invoked with real Google credentials through Vertex AI;
- execution provider is `google_adk_vertex` with Google ADK `2.7.0`;
- the hosted deployment is Cloud Run revision `evidencebound-recovery-mesh-00005-82k`;
- public health endpoint is `/health`;
- Secret Manager contains the dedicated judge credential while the value remains absent from source/public receipts;
- unauthenticated `POST /api/runs` returns `401` before model execution;
- four specialized live ADK roles participate in the baseline;
- controlled `stale_evidence` invalidates `history_snapshot`;
- exact dependency traversal blocks `publish_action` and preserves `scout`;
- autonomous selective recovery reruns only Statistician, Skeptic, and Orchestrator;
- recomputed checkpoints are deterministically re-verified;
- `publish_action` resumes only after dependency trust passes;
- duplicate side effects remain idempotency-protected within the current process-local ledger boundary;
- benchmark receipts compare actual full-restart and selective-recovery paths;
- Flight Recorder shows the six-step causal sequence from runtime state;
- Workload Identity Federation is used for keyless GitHub deployment rather than a service-account key;
- Google Agent Registry contains a discoverable Recovery Mesh fleet entry point;
- architecture, README, Devpost description, testing instructions, and final public video describe the same bounded system.

## Judge moment

```text
TRUST BREAK
  -> EXACT BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

## Measured receipts

Reference production acceptance:

```text
Run:                 run-4707af5a2fb6
Full restart:        4 model calls / 1781 input tokens
Selective recovery: 3 model calls / 1358 input tokens
Saved:               1 model call / 423 input tokens (~24%)
```

Fresh final-video browser capture:

```text
Run:                 run-72e5ad9cd0e8
Full restart:        4 model calls / 1788 input tokens
Selective recovery: 3 model calls / 1427 input tokens
Saved:               1 model call / 361 input tokens (20%)
```

These are controlled-run measurements, not universal savings claims.

## Agent Registry acceptance

The separate keyless registration workflow passed only after the Google long-running operation completed and the generated read-only Agent became observable:

```text
Workflow: 31871557186
AGENT_REGISTRY=PASS
Service: projects/evidencebound-rm-c977c1/locations/global/services/recovery-mesh-fleet
Agent: projects/457699623691/locations/global/agents/agentregistry-00000000-0000-0000-a7f5-b9837959f789
AGENT_REGISTRY_DISCOVERY=PASS
```

## Evidence-class discipline

The following remain separate evidence classes and are not substituted for each other:

- deterministic/local tests do not prove live Gemini execution;
- the 100-checkpoint synthetic scale probe does not prove 100 live Gemini calls;
- a diagram does not prove a Google integration;
- persisted state would not automatically become trusted state;
- Agent Registry catalog/discovery does not authorize Recovery Mesh trust state.

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
