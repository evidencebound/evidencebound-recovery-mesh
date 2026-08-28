# Fortified Durable Trust Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Firestore-backed durable trust state, deterministic rehydration, a real idempotent durable action receipt, and structured Cloud Logging evidence without changing Recovery Mesh's deterministic trust authority.

**Architecture:** Introduce a narrow persistence interface with in-memory and Firestore implementations. `DemoRun` persists snapshots/events at each material state transition and uses a ledger adapter for the final action receipt; a deterministic rehydration verifier validates persisted state before judge readback. Cloud Run emits structured Flight Recorder logs and production workflows bootstrap/verify Firestore, then extend live acceptance to prove blocked-write absence, exactly-once post-recovery commit, durable readback, and Cloud Logging receipts.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, google-cloud-firestore, Google ADK 2.x, Vertex AI / Gemini 3.5 Flash, Cloud Run, Firestore, Cloud Logging, GitHub Actions/WIF.

**Spec:** `docs/superpowers/specs/2026-08-28-fortified-durable-trust-ledger-design.md`

## Global Constraints

- Persisted state is not automatically trusted state.
- Gemini must never mark checkpoints `VERIFIED`, choose blast radius, override provenance/integrity/policy checks, or authorize the final action.
- Firestore is a persistence/action-receipt service, not a trust authority.
- Controlled faults remain clearly labeled and use the same verification/recovery contracts.
- No secrets, judge key, private prompts, or raw private payloads are persisted/logged.
- Production remains bounded to Cloud Run `min=0`, `max=1`; target owner spend remains near zero.
- Do not claim Agent Runtime, Memory Bank, Model Armor, Agent Gateway, Agent Identity, or Agent Observability without separate proof.
- All ROI claims remain run-specific measured values.

---

### Task 1: Persistence contracts and deterministic rehydration

**Files:**
- Create: `src/recovery_mesh/persistence.py`
- Create: `tests/test_persistence.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces `RunStore`, `InMemoryRunStore`, `FirestoreRunStore`, `ActionReceiptStore`, `RehydrationReceipt`, `store_from_environment()`, and `verify_persisted_snapshot(snapshot, action_receipt)`.
- `RunStore.save_run_snapshot(run_id: str, snapshot: dict[str, Any]) -> None`
- `RunStore.load_run_snapshot(run_id: str) -> dict[str, Any] | None`
- `RunStore.append_event(event: FlightEvent) -> None`
- `ActionReceiptStore.commit(key: str, payload: Any, *, run_id: str) -> SideEffectReceipt`
- `ActionReceiptStore.get(key: str) -> SideEffectReceipt | None`

- [ ] **Step 1: Add failing unit tests** for in-memory save/load, dependency-digest rehydration, fail-closed policy mismatch, idempotent same-payload receipt, and conflicting-payload rejection.
- [ ] **Step 2: Add `google-cloud-firestore>=2.21,<3`** to project dependencies and typed import handling.
- [ ] **Step 3: Implement `InMemoryRunStore` and `RehydrationReceipt`** with no network dependency.
- [ ] **Step 4: Implement `verify_persisted_snapshot()`** to validate checkpoint IDs/dependencies/statuses, parent input digests, policy consistency, and action receipt binding without ever upgrading status.
- [ ] **Step 5: Implement `FirestoreRunStore`** using ADC, collections `recovery_mesh_runs` and `recovery_mesh_action_receipts`, and event subcollections. Use Firestore transaction/create semantics for idempotency.
- [ ] **Step 6: Implement `store_from_environment()`**: deterministic mode defaults to memory; live Google mode requires explicit `RECOVERY_MESH_PERSISTENCE_MODE=firestore` for durable production acceptance and fails closed when configured Firestore initialization fails.
- [ ] **Step 7: Run `pytest tests/test_persistence.py -v`, `ruff check`, and `mypy src/recovery_mesh`.**

### Task 2: Runtime persistence, durable action receipt, and structured event logging

**Files:**
- Modify: `src/recovery_mesh/recovery.py`
- Modify: `src/recovery_mesh/flight_recorder.py`
- Modify: `src/recovery_mesh/runtime.py`
- Modify: `tests/test_recovery.py`
- Modify: `tests/test_runtime.py`
- Create: `tests/test_durable_runtime.py`

**Interfaces:**
- `RecoveryEngine.resume_action(..., ledger: ActionReceiptStore)` accepts both memory and Firestore ledgers.
- `DemoRun(..., store: RunStore | None = None)` persists baseline/fault/recovery snapshots and events.
- `DemoRun.durable_snapshot()` loads and verifies persisted state.

- [ ] **Step 1: Write failing runtime tests** proving baseline snapshot persistence, blocked action has no durable receipt, recovery writes exactly one receipt, duplicate recover/commit suppression, and durable readback passes rehydration.
- [ ] **Step 2: Generalize `SideEffectLedger.commit()` signature** to accept optional `run_id` while preserving existing tests and deterministic behavior.
- [ ] **Step 3: Inject `RunStore` into `DemoRun`** and persist after baseline construction, fault planning, and recovery completion.
- [ ] **Step 4: Persist each `FlightEvent`** from `_record()` and emit a structured JSON log line with bounded event fields.
- [ ] **Step 5: Use the store's action-receipt ledger in production** so `publish_action` becomes a real Firestore receipt only after dependencies verify.
- [ ] **Step 6: Expose persistence and action-receipt metadata in snapshots** without secrets/private evidence.
- [ ] **Step 7: Run focused and full unit suites.**

### Task 3: Protected durable-read API and UI evidence surface

**Files:**
- Modify: `src/recovery_mesh/api.py`
- Modify: `static/index.html`
- Modify: `static/app.js`
- Modify: `static/styles.css`
- Modify: `tests/test_api.py`
- Modify: `tests/test_flight_recorder_ui.py`

**Interfaces:**
- `GET /api/durable-runs/{run_id}` protected by judge key.
- `/health.persistence` reports `{provider, durable, project}`.
- Run UI displays a compact `DURABLE TRUST LEDGER` proof row: provider, persisted state, action receipt state, rehydration result.

- [ ] **Step 1: Add failing API tests** for health persistence metadata, protected durable read, missing durable run, and fail-closed untrusted rehydration.
- [ ] **Step 2: Add persistence provider initialization at API startup/request boundary** without exposing credentials.
- [ ] **Step 3: Add durable-run endpoint** returning persisted snapshot + rehydration receipt + bounded action receipt metadata.
- [ ] **Step 4: Add compact UI proof surface** that renders `PERSISTED`, `ACTION BLOCKED / NO RECEIPT`, then `REHYDRATED / RECEIPT COMMITTED` from real snapshot fields.
- [ ] **Step 5: Extend UI contract tests and `node --check static/app.js`.**

### Task 4: GCP bootstrap/deployment for Firestore

**Files:**
- Create: `scripts/gcp-firestore-bootstrap.sh`
- Modify: `scripts/deploy-cloud-run.sh`
- Modify: `.github/workflows/deploy-cloud-run.yml`
- Create: `tests/test_firestore_deploy_contract.py`

**Interfaces:**
- Bootstrap enables `firestore.googleapis.com` and verifies/creates `(default)` database idempotently.
- Runtime SA is verified to have `roles/datastore.user`; deployer may grant it only if existing WIF permissions allow.
- Cloud Run receives `RECOVERY_MESH_PERSISTENCE_MODE=firestore`.

- [ ] **Step 1: Add contract tests** requiring Firestore API/database bootstrap, runtime env, and least-privilege role references.
- [ ] **Step 2: Implement idempotent bootstrap** with `gcloud firestore databases describe '(default)'`; create only when absent, default region `eur3` unless current project policy forces another supported location.
- [ ] **Step 3: Verify/grant runtime `roles/datastore.user`** using project IAM only if missing; fail closed with an exact blocker when deployer lacks permission.
- [ ] **Step 4: Update Cloud Run deployment env** and print Firestore proof receipt without secrets.
- [ ] **Step 5: Run shell/contract tests.**

### Task 5: Production smoke, durable readback, and Cloud Logging proof

**Files:**
- Modify: `scripts/smoke-cloud-run.sh`
- Modify: `scripts/gcp-proof-receipt.sh`
- Modify: `.github/workflows/gcp-live-acceptance.yml`
- Modify: `tests/test_smoke_harness.py`
- Modify: `tests/test_live_acceptance_workflow.py`

**Interfaces:**
- Smoke output adds `FIRESTORE_BASELINE_PERSISTED=PASS`, `BLOCKED_ACTION_RECEIPT_ABSENT=PASS`, `DURABLE_ACTION_RECEIPT=PASS`, `DURABLE_REHYDRATION=PASS`.
- Cloud proof queries Cloud Logging for the actual live run id and required event types.

- [ ] **Step 1: Extend contract tests** for all new receipts.
- [ ] **Step 2: After baseline creation, call durable-read endpoint** and prove persisted/rehydrated state.
- [ ] **Step 3: After fault, prove `publish_action` remains BLOCKED and durable receipt absent.**
- [ ] **Step 4: After recovery, prove exactly one matching durable receipt and trusted durable readback.**
- [ ] **Step 5: Query Cloud Logging** for `run_id` and required event types; do not call this Agent Observability.
- [ ] **Step 6: Publish machine-readable acceptance status only on complete success.**

### Task 6: Judge positioning, architecture, and reproducibility docs

**Files:**
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/JUDGE_TESTING_INSTRUCTIONS.md`
- Modify: `docs/JUDGE_ACCEPTANCE.md`
- Modify: `docs/DEVPOST_SUBMISSION_MATRIX.md`
- Modify: `docs/PROOF_OF_ACTION_VIDEO.md`

**Interfaces:**
- Docs distinguish verified Firestore/Cloud Logging from unverified GEAP services.
- Fortified framing includes the football performance/match-intelligence operations analyst “unlikely hero” while keeping the system domain-general.

- [ ] **Step 1: Update architecture and current scope only after live proof exists.**
- [ ] **Step 2: Add Firestore rehydration and Cloud Logging reproduction commands.**
- [ ] **Step 3: Update judge acceptance matrix with exact workflow/revision/run receipts from the new deployment.**
- [ ] **Step 4: Rewrite Proof-of-Action plan around Google-owned evidence + one continuous hands-off run.**

### Task 7: CI, deploy, live acceptance, and Devpost synchronization

**Files:**
- Modify: `.github/ci.trigger` or existing trigger file only if needed to force CI/deploy after merge.
- Devpost project fields via connector after production proof.

**Interfaces:**
- Merge only after PR CI is green.
- Trigger production deployment on `main`, then live acceptance.
- Update Devpost `built_with`, description, Cloud service answer (Firestore only after verified), testing instructions/submission fields as available, and video only after new public V3 exists.

- [ ] **Step 1: Run full CI on feature branch and review diff.**
- [ ] **Step 2: Merge only on GREEN.**
- [ ] **Step 3: Trigger/observe Cloud Run deploy and Firestore bootstrap.**
- [ ] **Step 4: Run live acceptance and capture exact revision/run/Firestore/Cloud Logging receipts.**
- [ ] **Step 5: If GCP entitlement/IAM blocks Firestore, stop and report exact blocker/owner action; do not claim integration.**
- [ ] **Step 6: Synchronize repo docs and Devpost only from verified production truth.**
- [ ] **Step 7: Final readback of Devpost, repo main, CI, deployment, and judge flow.**

## Self-review

- Spec coverage: persistence, rehydration, durable action, logging, UI, GCP, acceptance, docs, Devpost, and demo are all mapped to tasks.
- No unsupported GEAP product claims are introduced.
- Firestore database/role creation is explicitly fail-closed because current deployer entitlement is not yet proven.
- Production docs/Devpost are deliberately deferred until after live acceptance so no planned integration is presented as live.
