# EvidenceBound Recovery Mesh

> Trust-aware flight recorder and self-healing engine for autonomous agent fleets.

Recovery Mesh detects when a checkpoint in an agent workflow becomes untrustworthy,
computes the exact downstream trust blast radius, blocks unsafe actions, preserves still-
verifiable work, recomputes only the affected branch, re-verifies the new state, and resumes
only when the final policy gate passes.

## Judge thesis

```text
TRUST BREAK
  -> BLAST RADIUS
  -> ACTION BLOCKED
  -> SAFE WORK REUSED
  -> AFFECTED BRANCH RECOMPUTED
  -> VERIFIED RECOVERY
```

The Flight Recorder UI renders this exact six-step proof sequence from runtime state; it is not
a staged screenshot or a separate demo-only state machine.

## Core invariant

**Persisted memory is not automatically trusted memory.**

Gemini output never overrides deterministic trust, provenance, integrity, dependency, policy,
or side-effect gates.

## Hackathon boundary

This is a new, isolated Google All Things Agentic Hackathon 2026 project. No SignalReview
production source or prior EvidenceBound implementation source is copied into this repository.
See [`PREEXISTING_WORK.md`](PREEXISTING_WORK.md) for the disclosure and clean-room boundary.

## Judge evidence map

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — canonical architecture source and trust-authority boundary.
- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) — Fortified fleet threats, controls, and explicit non-claims.
- [`docs/JUDGE_ACCEPTANCE.md`](docs/JUDGE_ACCEPTANCE.md) — production acceptance gates that must be proven before final submission.
- [`docs/DEVPOST_SUBMISSION_MATRIX.md`](docs/DEVPOST_SUBMISSION_MATRIX.md) — field-by-field evidence state.
- [`docs/PROOF_OF_ACTION_VIDEO.md`](docs/PROOF_OF_ACTION_VIDEO.md) — <=4 minute recording plan; it is not evidence by itself.
- [`docs/OWNER_RETURN_RUNBOOK.md`](docs/OWNER_RETURN_RUNBOOK.md) — isolated Google Cloud first-bootstrap runbook.

## Architecture

```mermaid
flowchart LR
  U[Judge / API] --> M[Recovery Mesh Controller]
  M --> A1[Google ADK · Statistician]
  M --> A2[Google ADK · Scout]
  M --> A3[Google ADK · Skeptic]
  M --> A4[Google ADK · Orchestrator]
  A1 --> G[Deterministic Trust Graph]
  A2 --> G
  A3 --> G
  A4 --> G
  G --> V[Checkpoint verifier]
  V --> B[Blast-radius planner]
  B --> X[Fail-closed action gate]
  B --> R[Selective recompute]
  R --> A1
  R --> A2
  R --> A3
  R --> A4
  X --> F[Flight Recorder]
  G --> F
  F --> C[Cloud Run UI/API]
```

The public judge deployment is configured to use **Google ADK + Gemini**. The deterministic
executor exists only for credential-free unit/contract tests and is surfaced as
`deterministic_test`; there is no silent fallback from a failed Google invocation.

## Trust graph

The bounded clean-room workload is:

```text
fixture_snapshot -----+----> statistician ----+
                      |                        |
history_snapshot -----+                        +--> skeptic --> orchestrator --> publish_action
                      |                        |                   ^
                      +----> scout ------------+                   |
policy_rules -----------------------------------------------------+
```

Every checkpoint binds:

- run/checkpoint/agent IDs and versions;
- dependency checkpoint IDs;
- **actual parent output digests** as input digests;
- evidence/tool-result digests where applicable;
- policy version;
- structured output digest;
- trust state (`VERIFIED`, `INVALIDATED`, `RECOMPUTE`, `BLOCKED`);
- provenance/integrity metadata and timestamps.

## Controlled trust breaks

All demo faults are visibly labeled controlled faults and enter the same trust contracts used
by runtime verification:

- `stale_evidence` — invalidates `history_snapshot` and exactly its downstream branch;
- `malformed_worker` — strict agent-output schema failure at `scout`;
- `policy_drift` — policy version drift invalidates policy-dependent state.

The Recovery Mesh computes the rerun plan. A judge never selects which agents to rerun.

## Execution modes

### Deterministic test mode

Default when no environment override is set:

```bash
RECOVERY_MESH_EXECUTION_MODE=deterministic python -m pytest
```

This validates graph/recovery behavior without credentials. It **does not** claim Gemini,
ADK, model-call, or token execution.

### Google ADK / Vertex AI mode

The Cloud Run deployment sets:

```text
RECOVERY_MESH_EXECUTION_MODE=google_adk
GOOGLE_GENAI_USE_VERTEXAI=TRUE
RECOVERY_MESH_MODEL=gemini-3.5-flash
```

Each agent checkpoint invokes a fresh bounded ADK agent. Execution receipts retain provider,
model, elapsed time, ADK invocation IDs/authors, and token usage when the ADK event exposes it.
If ADK/Gemini is unavailable or the worker violates the strict output contract, the request
fails closed rather than silently switching to deterministic output.

## Fleet-scale proof without 100 LLM calls

The live judge workflow intentionally keeps four specialized Gemini/ADK roles so the causal
story stays understandable and bounded. Separately, a deterministic scale probe constructs
**100 synthetic agent checkpoints** across independent branches and measures the same exact
blast-radius planner. This proves graph-scale reuse behavior without pretending that 100 model
calls are necessary or cost-effective.

```bash
PYTHONPATH=src python scripts/benchmark-scale.py
```

The CI locks the controlled scale receipt to **100 agent checkpoints / 14 affected / 86 reused /
1 blocked action**. The receipt is explicitly labeled `deterministic_synthetic_scale_probe`;
it is not evidence of 100 live Gemini invocations.

## Measured recovery economics

The benchmark compares:

1. a full four-agent restart; and
2. the Recovery Mesh selective rerun set.

In deterministic test mode only checkpoint/agent execution counts and elapsed time are
reported. In live Google mode the benchmark actually executes both paths and additionally
records model calls and input/output token usage when returned by ADK events. Any percentage
shown in the UI is explicitly scoped to that controlled run; no general savings claim is made.

## Local verification

```bash
python -m pytest --cov=recovery_mesh --cov-branch --cov-report=term-missing
python -m py_compile app/agent.py src/recovery_mesh/*.py scripts/benchmark-scale.py
bash -n scripts/gcp-owner-bootstrap.sh scripts/gcp-live-preflight.sh scripts/deploy-cloud-run.sh scripts/smoke-cloud-run.sh
node --check static/app.js
PYTHONPATH=src python scripts/benchmark-scale.py
```

`src/recovery_mesh/google_adk.py` is intentionally excluded from credential-free unit coverage;
it is owned by the live ADK/Gemini integration gate. A local core PASS is not a Google
integration PASS.

The full CI also runs Ruff, mypy, secret scanning, exact scale-receipt assertions, and a Docker
build.

## Run the local Flight Recorder

```bash
PYTHONPATH=src uvicorn recovery_mesh.api:app --host 127.0.0.1 --port 8080
```

Then open `http://127.0.0.1:8080`. For an automated visual flow:

```text
/?autorun=stale_evidence
/?autorun=stale_evidence&recover=1
```

These query parameters call the real API/runtime; they do not fabricate UI state.

## Cloud Run deployment

The isolated hackathon deployment target is:

```text
Project ID: evidencebound-rm-c977c1
Project number: 457699623691
Cloud Run region: europe-west1
Vertex location: global
Model target: gemini-3.5-flash
```

Billing and authenticated owner bootstrap are explicit prerequisites. The bootstrap fails closed
before API/IAM mutation unless the exact project ID, project number, `hackathon` label, ACTIVE
lifecycle state, and enabled billing match the isolated target.

For the first deployment, run the owner bootstrap once from an authenticated Google Cloud
Shell. It performs live Gemini preflight, creates separate least-privilege runtime/build
identities, makes the judge service public once, deploys the bounded Cloud Run service, runs the
live acceptance smoke, and creates keyless GitHub Workload Identity Federation restricted to
this repository ID, owner, and `main` branch. No service-account key is created or exported.

```bash
export GOOGLE_CLOUD_PROJECT=evidencebound-rm-c977c1
export GOOGLE_CLOUD_RUN_REGION=europe-west1
export GOOGLE_CLOUD_LOCATION=global
export RECOVERY_MESH_MODEL=gemini-3.5-flash
./scripts/gcp-owner-bootstrap.sh
```

After the first bootstrap, `.github/workflows/deploy-cloud-run.yml` provides an explicit manual
keyless deployment path. Recurring deploy credentials do not receive permission to enable APIs,
mutate project IAM, or change public access. Source builds run as the dedicated
`recovery-mesh-build` identity and revisions run as the separate `recovery-mesh-runtime`
identity.

The deployment is bounded to `min=0`, `max=1`, one CPU and 512 MiB. Every deploy first performs
a real Gemini call and then runs the end-to-end live smoke gate requiring Google ADK receipts,
exact stale-evidence blast radius, blocked action, preserved Scout checkpoint, selective
three-agent rerun, and final `VERIFIED` action state.

Until those real receipts exist, **Cloud Run, hosted judge URL, and live Gemini remain PENDING**.

## Security and cost posture

- no secrets in source, receipts, or UI;
- bounded controlled demo inputs;
- deterministic fail-closed trust/policy gates;
- side-effect idempotency keys;
- no automatic fallback from Google execution to fake/local output;
- exact-project bootstrap guard before cloud mutation;
- keyless GitHub deployment design via Workload Identity Federation;
- Cloud Run scale-to-zero target with max one instance;
- owner-funded spend is not assumed;
- extra Gemini Enterprise Agent Platform services are not claimed until entitlement and real
  invocation are verified.

## Current evidence classes

| Gate | Status semantics |
|---|---|
| Deterministic DAG / recovery / API tests | executable local + remote CI evidence |
| Google ADK construction | remote CI evidence with installed ADK dependency |
| Synthetic 100-agent scale receipt | deterministic CI evidence, not 100 Gemini calls |
| Isolated Google Cloud project | created; billing/live runtime still pending |
| Live Gemini / Vertex execution | requires real Google credentials/project and receipt |
| Cloud Run deployment | requires authenticated owner bootstrap and smoke receipt |
| Browser visual acceptance | separate hosted/browser gate |
| Gemini Enterprise Agent Platform add-ons | not part of the claimed runtime until verified |
