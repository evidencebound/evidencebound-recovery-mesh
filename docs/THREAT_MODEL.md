# Threat model — Fortified Enterprise Fleet

Status as of 2026-08-22: core Google Cloud security acceptance is **LIVE / VERIFIED** for the bounded hackathon deployment described here.

Recovery Mesh treats every model/tool/evidence checkpoint as potentially invalid until deterministic verification passes. This is a bounded hackathon threat model, not a claim of complete enterprise protection.

## Assets

- integrity of the Trust Graph;
- provenance of evidence/tool results;
- policy version used for authorization;
- correctness of dependency edges and parent-output digests;
- action authorization state;
- idempotency of side effects;
- auditability of invalidation and recovery history;
- private judge credential;
- Google Cloud deployment identity and supply chain.

## Trust boundaries

### Untrusted / advisory

- Gemini natural-language reasoning;
- worker structured output before schema verification;
- external evidence/tool results before digest/provenance/freshness verification;
- persisted checkpoint state before re-validation;
- controlled fault fixture payloads;
- unauthenticated internet traffic to the public Cloud Run URL.

### Deterministic authority

- checkpoint schema validation;
- output/input digest binding;
- provenance and integrity metadata checks;
- policy-version checks;
- Trust Graph dependency traversal;
- blast-radius computation;
- trust-state transitions;
- action gating and idempotency ledger.

## Threat/control matrix

| Threat | Failure mode | Implemented control | Recovery behavior |
|---|---|---|---|
| Stale/refuted evidence | downstream conclusions depend on obsolete source | evidence freshness trust break + dependency graph | block affected action, invalidate exact descendants, reuse independent checkpoints, rerun affected branch |
| Malformed/unsupported worker output | agent emits output outside contract | strict Pydantic worker schema, extra fields forbidden | fail closed at worker checkpoint; descendants become recompute/blocked |
| Prompt/tool poisoning | malicious or unsupported content enters model context | model output remains advisory; evidence/tool digests + provenance contract; deterministic verifier owns trust | poisoned checkpoint cannot self-authorize; contamination propagates only through graph descendants |
| Policy drift | state was verified under older policy | policy version bound to checkpoints + policy-drift detector | invalidate policy-dependent state; re-verify/recompute before action resumes |
| Checkpoint tampering | persisted output no longer matches recorded integrity | output digest bound to integrity metadata; verified state requires valid digest | checkpoint invalidated and dependent state recomputed |
| Dependency substitution | child is evaluated against different parent output | child input digests bind actual parent structured-output digests | mismatch fails verification; downstream action remains blocked |
| Duplicate/replayed side effect | retry publishes same action twice | side-effect key + idempotency ledger | duplicate is suppressed; conflicting replay is rejected |
| Agent attempts to override trust | model says it is safe/verified | Gemini/ADK cannot set deterministic trust state or bypass action gate | claim has no authority; gate follows verifier/graph state only |
| Unauthorized public API use | visitor tries to start/fault/recover a run | protected run/read/mutation APIs require `X-Recovery-Mesh-Judge-Key`; wrong/missing key fails `401` before model execution | rejected request creates no model-backed run |
| Judge key exposure in source/UI | testing credential becomes public | generated once, stored in Secret Manager, mounted into Cloud Run; never committed or embedded in JS; browser keeps entered value only in tab-scoped `sessionStorage` | rotate secret version/revision if exposure occurs |
| Google credential leakage | long-lived deployment secret is exposed | no service-account key; Workload Identity Federation for GitHub deploys; secret scan | revoke/bound WIF/IAM without rotating embedded keys |
| Wrong-project deployment | operator shell points at unrelated project | bootstrap pins project ID, project number, hackathon label, lifecycle and billing prerequisites | exits with `BLOCKER` before API/IAM mutation |
| Stray traffic consumes model calls | authorized or accidental repeated requests consume Gemini | process-local atomic model-call reservation guard | once exhausted, provider invocation fails closed instead of falling back |
| Unbounded cost/runtime | runaway demo deployment | Cloud Run `min=0`, `max=1`, protected APIs, bounded four-agent judge flow, synthetic rather than paid 100-agent scale test | limits accidental demo load; does not substitute for billing controls |
| Registry overreach | catalog state is mistaken for trust authority | Agent Registry is treated only as catalog/discovery control plane | Registry metadata cannot mark checkpoints VERIFIED or authorize actions |

## Judge credential boundary

The hosted service keeps the public UI and `/health` available for judge discovery. Run snapshots and every operation that creates or changes work (`start`, controlled `fault`, `recover`) require the private testing key.

The judge secret:

1. lives in Secret Manager as `recovery-mesh-judge-key:1`;
2. is accessible only to bounded identities that require it;
3. is mounted into Cloud Run as `RECOVERY_MESH_JUDGE_KEY`;
4. is absent from repository source, public UI, video, and public receipts;
5. is stored by the browser only in tab-scoped `sessionStorage` after the judge enters it.

Production smoke proved an unauthenticated `POST /api/runs` returns HTTP `401` before live model execution.

## Live model-call guard semantics

`RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET` is a bounded process-local invocation guard. Each live Google agent checkpoint reserves a unit immediately before provider invocation. Reservation is protected by a process-local lock so concurrent requests cannot oversubscribe the same process budget.

This guard is deliberately **not** described as a billing limit:

- it resets when Cloud Run starts a new process/revision;
- a failed provider call still consumes its reservation;
- it does not predict or cap token usage or currency spend;
- it does not replace Cloud Billing budgets/alerts.

## Controlled-fault policy

Controlled faults are allowed only when they are:

- visibly marked controlled fixtures;
- routed through the same verification and recovery contracts as normal failures;
- never represented as real provider incidents;
- unable to bypass the action gate;
- retained in Flight Recorder history as a distinct failure class.

Current controlled scenarios include stale evidence, malformed worker output, and policy drift.

## Verified security evidence

Current production evidence includes:

- committed-secret scan PASS;
- no service-account key in repository/runtime configuration;
- WIF deployment identity restricted to the Recovery Mesh repository/owner/`main` path;
- dedicated runtime/build/deployer service accounts;
- judge secret stored in Secret Manager and bound to runtime access;
- unauthenticated run creation returns `401` before model execution;
- stale-evidence flow blocks `publish_action` before recovery;
- idempotency/replay regression tests;
- live Google execution fails closed rather than silently using deterministic output;
- bounded process-local live model-call guard;
- Google Agent Registry Service + generated read-only Agent discovery PASS.

## Known non-claims / limitations

- No claim of “100% protection”.
- No claim that Gemini, ADK, Model Armor, Memory Bank, or another Google service detected a failure unless a real invocation proves it.
- No claim that persisted memory is immutable or inherently trusted.
- The public judge deployment uses bounded controlled data and is not a general arbitrary-tool execution endpoint.
- The process-local model-call budget is not a hard financial spending cap.
- The private judge key is demo access control, not enterprise end-user identity infrastructure.
- The live run/idempotency store is process-local and does not prove multi-week restart-surviving state.
- Firestore persistence, BigQuery export, Agent Runtime, Memory Bank, Model Armor, Agent Gateway, Agent Identity, and enterprise observability services are not claimed without a separately verified integration.

The current security claim is therefore precise: Recovery Mesh demonstrates a production-backed, protected, fail-closed recovery plane on Google Cloud with deterministic trust authority, not complete enterprise-platform coverage.
