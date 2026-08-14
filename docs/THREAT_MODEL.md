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
- Google Cloud deployment identity and supply chain.

## Trust boundaries

### Untrusted / advisory

- Gemini natural-language reasoning;
- worker structured output before schema verification;
- external evidence/tool results before digest/provenance/freshness verification;
- persisted checkpoint state before re-validation;
- controlled fault fixture payloads.

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
| Google credential leakage | long-lived deployment secret is exposed | no service-account key; Workload Identity Federation for GitHub deploys; secret scan; generated auth files ignored | revoke/bound WIF/IAM without rotating embedded keys |
| Wrong-project deployment | operator shell points at unrelated project | bootstrap pins project ID, project number, hackathon label, ACTIVE state, billing | exits with `BLOCKER` before API/IAM mutation |
| Unbounded cost/runtime | runaway demo deployment | Cloud Run `min=0`, `max=1`, bounded four-agent judge flow, no 100-live-agent scale test | scale proof uses deterministic synthetic checkpoints instead of paid 100-agent calls |

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
- Enterprise Agent Platform add-ons remain out of the claimed architecture until entitlement and actual integration are verified.
- Production Google Cloud security acceptance remains pending until the live bootstrap and hosted smoke test succeed.

## Security acceptance evidence

Before final submission, retain receipts for:

1. committed-secret scan PASS;
2. no service-account key in repository or runtime configuration;
3. WIF provider condition restricted to exact GitHub repository ID/owner/main ref;
4. runtime service account identity shown on Cloud Run revision;
5. stale-evidence action gate BLOCKED before recovery;
6. idempotency/replay tests PASS;
7. live Google execution fails closed rather than silently using deterministic output.
