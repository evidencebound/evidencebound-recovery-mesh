# Threat model — Fortified Enterprise Fleet

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
| Unauthorized public API use | visitor tries to start/fault/recover a run | run/read/mutation APIs require `X-Recovery-Mesh-Judge-Key`; live mode without configured secret fails 503; wrong/missing key fails 401 before model execution | no run/model call is created for rejected request |
| Judge key exposure in source/UI | testing credential becomes public | generated once at bootstrap, stored in Secret Manager, mounted as Cloud Run secret; never committed or embedded in JS; browser keeps entered value only in tab-scoped `sessionStorage` | rotate secret version/revision if exposure occurs |
| Google credential leakage | long-lived deployment secret is exposed | no service-account key; Workload Identity Federation for GitHub deploys; secret scan; generated auth files ignored | revoke/bound WIF/IAM without rotating embedded keys |
| Wrong-project deployment | operator shell points at unrelated project | bootstrap pins project ID, project number, hackathon label, ACTIVE state, billing | exits with `BLOCKER` before API/IAM mutation |
| Stray traffic consumes model calls | authorized or accidental repeated requests consume Gemini | live Google executor shares a process-local atomic model-call budget; deployment default is 64 reservations per process | once exhausted, provider invocation is rejected before the call; workflow fails closed rather than silently falling back |
| Unbounded cost/runtime | runaway demo deployment | Cloud Run `min=0`, `max=1`, protected action APIs, bounded four-agent judge flow, process-local live-call guard, no 100-live-agent scale test | scale proof uses deterministic synthetic checkpoints instead of paid 100-agent calls |

## Judge credential boundary

The hosted service keeps the UI and `/healthz` public for simple judge discovery. The run snapshot endpoint and every operation that can create work (`start`, controlled `fault`, `recover`) require a private testing key.

The first owner bootstrap:

1. enables Secret Manager only after exact-project and billing checks;
2. generates a random URL-safe key once;
3. creates `recovery-mesh-judge-key:1` without printing the value;
4. grants the runtime service account accessor only to that secret;
5. mounts version `1` into Cloud Run as `RECOVERY_MESH_JUDGE_KEY`;
6. grants the bounded GitHub deployer accessor to that one secret only so deployment smoke can test the protected API.

The smoke gate also proves an unauthenticated `POST /api/runs` returns HTTP `401` before it runs the live agent flow.

## Live model-call guard semantics

`RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET` defaults to `64` for the Cloud Run deployment. Every live Google agent checkpoint reserves one unit immediately before the provider invocation. Reservation is protected by a process-local lock, so concurrent requests cannot oversubscribe a single process budget.

This guard is intentionally described as a **process-local invocation bound**, not a billing limit:

- it resets if Cloud Run starts a new process/revision;
- a failed provider call still consumes its reservation, which is the safer fail-closed behavior;
- it does not predict or cap token usage or currency spend;
- it does not replace Cloud Billing budgets/alerts or account-level controls.

The bound is meant to reduce accidental/stray demo traffic while leaving enough headroom for repeated judge and recording flows.

## Controlled-fault policy

Controlled faults are allowed only when all of these are true:

- visibly marked `controlled=true` / controlled fixture provenance;
- routed through the same verification and recovery contracts as normal failures;
- never represented as a real provider incident;
- never bypass the action gate;
- retained in Flight Recorder history as a distinct failure class.

## Known non-claims / limitations

- No claim of “100% protection”.
- No claim that Gemini, ADK, Model Armor, Memory Bank, or another Google service detected a failure unless a real invocation proves it.
- No claim that persisted memory is immutable or inherently trusted.
- The public judge deployment uses bounded demo data and is not a general arbitrary-tool execution endpoint.
- The process-local model-call budget is not a hard financial spending cap.
- The private judge key is demo access control, not end-user identity/authorization infrastructure.
- Enterprise Agent Platform add-ons remain out of the claimed architecture until entitlement and actual integration are verified.
- Production Google Cloud security acceptance remains pending until the live bootstrap and hosted smoke test succeed.

## Security acceptance evidence

Before final submission, retain receipts for:

1. committed-secret scan PASS;
2. no service-account key in repository or runtime configuration;
3. WIF provider condition restricted to exact GitHub repository ID/owner/main ref;
4. runtime service account identity shown on Cloud Run revision;
5. judge secret stored in Secret Manager and bound to runtime identity;
6. unauthenticated run creation returns `401` in production smoke;
7. stale-evidence action gate BLOCKED before recovery;
8. idempotency/replay tests PASS;
9. live Google execution fails closed rather than silently using deterministic output;
10. process-local live model-call budget regression test PASS.
