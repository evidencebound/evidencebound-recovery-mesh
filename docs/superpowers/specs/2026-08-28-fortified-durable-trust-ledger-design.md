# Fortified Durable Trust Ledger Design

## Goal

Strengthen EvidenceBound Recovery Mesh for the All Things Agentic 2026 **Fortified Enterprise Fleet** category by adding a durable Google Cloud persistence boundary, restart-safe trust rehydration, a real idempotent Google Cloud action receipt, and structured Cloud Logging evidence while preserving EvidenceBound's deterministic authority model.

## Core invariant

**Persisted state is not automatically trusted state.** A checkpoint loaded from durable storage is only reusable after Recovery Mesh re-verifies the fields that bind its trust context: output digest/integrity digest, dependency digests, evidence/tool digests, policy version, provenance, and verification state. Persistence may preserve bytes and history; it never grants `VERIFIED` authority.

## Scope

### In scope

- Firestore-backed durable run ledger for checkpoints, events, run metadata, recovery benchmark, and action receipts.
- A storage abstraction with deterministic in-memory implementation for local/tests and Firestore implementation for production.
- Cross-process/cross-session readback of a completed run through a protected API path.
- Deterministic rehydration validation before persisted checkpoints are reported as reusable/trusted.
- A real durable `publish_action` receipt committed to Firestore only after the action dependency gate passes.
- Idempotency enforced by Firestore transaction/create semantics so duplicate resume attempts do not duplicate the side effect.
- Structured Flight Recorder logging to standard Python logging, producing Cloud Run / Cloud Logging JSON-visible event fields.
- `/health` and run snapshots expose persistence provider and durable-state status without revealing secrets.
- Live smoke/acceptance proves: Firestore durable state active, trust break blocks the durable action receipt, selective recovery commits exactly one durable receipt, the run can be loaded from durable storage, and structured recovery events are emitted.
- README, architecture, judge instructions, Devpost description/submission answers, and demo plan are synchronized only with integrations proven by live acceptance.
- Judge workload is framed as an enterprise football-performance/match-intelligence operations workflow as an “unlikely hero” example, without claiming live SignalReview/provider data or copying pre-existing production code.

### Out of scope

- Google Agent Runtime, Memory Bank, Model Armor, Agent Gateway, or Agent Identity unless separately verified.
- Claiming Firestore makes data trusted, immutable, or cryptographically tamper-proof.
- Durable exactly-once semantics for arbitrary external systems; the verified claim is bounded to the Firestore action receipt used by the demo.
- Multi-week elapsed-time testing. The implementation provides cross-session persistence/re-verification semantics; documentation must distinguish this from literally observing a weeks-long run.
- Replacing the deterministic blast-radius/action authority with Gemini or any Google service.

## Architecture

### Storage boundary

Create `src/recovery_mesh/persistence.py` with a narrow `RunStore` protocol. It supports:

- `save_run_snapshot(run_id, snapshot)`
- `load_run_snapshot(run_id)`
- `append_event(event)`
- `commit_action_receipt(side_effect_key, payload)`
- `get_action_receipt(side_effect_key)`
- provider metadata

`InMemoryRunStore` is deterministic and used in local/test mode. `FirestoreRunStore` uses Application Default Credentials and database `(default)` in project `GOOGLE_CLOUD_PROJECT`.

Firestore layout is bounded and judge-readable:

- `recovery_mesh_runs/{run_id}` — latest complete public snapshot and trust-ledger metadata.
- `recovery_mesh_runs/{run_id}/events/{event_id}` — append-only Flight Recorder event documents.
- `recovery_mesh_action_receipts/{sha256(side_effect_key)}` — idempotent verified action receipt.

No private judge key, prompt payload, raw private evidence, or secrets are persisted.

### Rehydration semantics

A persisted snapshot is validated by a deterministic rehydration verifier before it is returned through the durable-read API. At minimum:

1. every checkpoint has a known `checkpoint_id`, known state, and required digest fields;
2. `output_digest` is present and matches the persisted integrity digest when that digest is stored;
3. every dependency reference resolves to another persisted checkpoint;
4. a checkpoint marked `VERIFIED` may be reported reusable only when its recorded dependency digests match the current persisted parent output digests and its policy version equals the persisted active policy version;
5. the action checkpoint may only be considered resumed when the durable action receipt exists and matches the action side-effect key/payload digest;
6. any failed rehydration check returns a fail-closed durable state (`trusted=false`) and never upgrades a checkpoint to `VERIFIED`.

The current live in-process `DemoRun` remains authoritative during an active run. Firestore is a durable evidence/state boundary, not an alternate trust engine.

### Durable action receipt

Refactor `SideEffectLedger` behind a small commit interface so `RecoveryEngine.resume_action()` can accept either in-memory or Firestore-backed ledgers.

The production Firestore ledger performs an atomic create/transaction:

- first commit writes receipt with side-effect key, payload digest, run id, committed timestamp;
- same key + same digest returns `duplicate_suppressed=true`;
- same key + different digest fails closed with `RecoveryInvariantError`.

During a trust break no Firestore receipt exists. Only after all action parents return to `VERIFIED` may `resume_action()` write it.

### Structured Cloud Logging

`DemoRun._record()` emits one structured JSON log line per `FlightEvent` through a dedicated logger. Fields include `run_id`, `event_id`, `event_type`, `checkpoint_id`, and bounded event data. Cloud Run captures stdout/stderr into Cloud Logging.

Do not call this “Agent Observability” unless the official Agent Observability product is separately integrated. The verified claim is **structured Cloud Logging receipts from Cloud Run**.

### API

- `GET /health` adds `persistence: {provider, durable, project}`.
- `POST /api/runs` persists the baseline snapshot.
- fault/recover endpoints persist the updated snapshot after each state transition.
- `GET /api/durable-runs/{run_id}` (judge-key protected) loads Firestore state and returns `rehydration` evidence with `trusted`, checked checkpoint count, and failures.
- optional `GET /api/action-receipts/{run_id}` or embedding in durable-run readback exposes only the bounded receipt metadata needed for judging.

All state-changing/read-run endpoints remain protected by the existing judge-key gate.

## Google Cloud deployment

Production deployment adds:

- dependency `google-cloud-firestore`;
- `RECOVERY_MESH_PERSISTENCE_MODE=firestore`;
- runtime service account permission `roles/datastore.user` scoped to the project;
- Firestore API enabled;
- Firestore `(default)` database created only if absent, in a supported low-cost region compatible with the project. Bootstrap is idempotent and fails closed if the deployer lacks entitlement/permission.

The deployment remains Cloud Run `min=0`, `max=1` and cost-bounded. No paid high-throughput resources are created.

## Acceptance gates

A production acceptance run must prove all of the following from actual responses/logs:

1. `/health` -> Google ADK / Gemini 3.5 Flash and Firestore durable provider.
2. unauthenticated state mutation -> `401`.
3. fresh baseline persists to Firestore.
4. controlled `stale_evidence` trust break -> `publish_action = BLOCKED`.
5. durable action receipt is absent while blocked.
6. exact blast radius retains Scout as reusable and schedules only affected branch.
7. recovery reruns Statistician/Skeptic/Orchestrator only.
8. final action -> `VERIFIED`.
9. exactly one durable action receipt exists after recovery.
10. durable run readback passes deterministic rehydration validation.
11. restart/readback semantics are verified by reading the run through the Firestore-backed API after removing it from the process-local hot store or from a fresh process/revision when feasible.
12. Cloud Logging query returns structured `TRUST_BREAK_DETECTED`, `ACTION_BLOCKED`, `CHECKPOINT_REUSED`, `CHECKPOINT_REVERIFIED`, and `RECOVERY_COMPLETED` receipts for the live run.
13. existing benchmark continues to report run-specific measured model calls/input tokens without universal savings claims.
14. full unit/contract/security/idempotency/CI/container-build gates remain green.

## Judge/demo presentation

The final demo should minimize generic slides. Preferred evidence order:

1. Google Cloud Console/Cloud Shell: project, Cloud Run current revision, Firestore database, Agent Registry, live health.
2. One continuous hands-off Flight Recorder run: baseline -> trust break -> exact blast radius -> blocked action -> Scout reuse -> selective recompute -> verified recovery.
3. Google-owned proof immediately after: Firestore run/action receipt and Cloud Logging events for the same run id.
4. Architecture diagram only as a brief explanatory frame.

The demo must clearly label controlled faults and must not represent fixture sports data as live provider truth.

## Submission positioning

Primary category remains **Fortified Enterprise Fleet**. Recovery Mesh is positioned as the fleet-integrity and selective-recovery control plane for institutional multi-agent systems. The bounded judge workload represents an “unlikely hero” enterprise user: a football performance/match-intelligence operations analyst whose autonomous agent fleet must not publish a recommendation based on stale or poisoned evidence.

The central innovation remains domain-general: detect trust break -> exact blast radius -> block unsafe action -> reuse still-verifiable work -> recompute affected branch -> re-verify -> resume exactly once.
