#!/usr/bin/env bash
set -euo pipefail
URL="${1:?Usage: smoke-cloud-run.sh https://service.run.app}"
: "${RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE:?Protected smoke requires RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE}"

protected_curl() {
  # Feed the credential through curl config stdin so the secret is not present in the curl argv.
  printf 'header = "X-Recovery-Mesh-Judge-Key: %s"\n' "$RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE" \
    | curl --config - "$@"
}

HEALTH_JSON="$(curl --fail --silent --show-error "${URL}/healthz")"
printf '%s' "$HEALTH_JSON" | python -c '
import json,sys
x=json.load(sys.stdin)
assert x["status"]=="ok", x
assert x["judge_access_required"] is True, x
assert x["judge_key_header"] == "X-Recovery-Mesh-Judge-Key", x
execution=x["execution"]
assert execution["provider"]=="google_adk_vertex", execution
assert execution["live_google"] is True, execution
assert execution["model"] in {"gemini-3.5-flash","gemini-3.6-flash"}, execution
print(f"HEALTH=PASS provider={execution[\"provider\"]} model={execution[\"model\"]} judge_access=protected")
'

UNAUTHORIZED_STATUS="$(curl --silent --output /dev/null --write-out '%{http_code}' -X POST "${URL}/api/runs")"
[ "$UNAUTHORIZED_STATUS" = "401" ] || {
  echo "BLOCKER=unprotected run endpoint returned HTTP ${UNAUTHORIZED_STATUS}, expected 401" >&2
  exit 7
}
printf 'JUDGE_API_AUTH=PASS unauthenticated_post=401\n'

BASELINE_JSON="$(protected_curl --fail --silent --show-error -X POST "${URL}/api/runs")"
RUN_ID="$(printf '%s' "$BASELINE_JSON" | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')"
printf '%s' "$BASELINE_JSON" | python -c '
import json,sys
x=json.load(sys.stdin)
execution=x["execution"]
assert execution["live_google"] is True, execution
assert len(execution["baseline"]) == 4, execution["baseline"]
assert all(r["provider"] == "google_adk_vertex" for r in execution["baseline"]), execution["baseline"]
assert all(r["model"] in {"gemini-3.5-flash","gemini-3.6-flash"} for r in execution["baseline"]), execution["baseline"]
assert all(r["invocation_ids"] for r in execution["baseline"]), execution["baseline"]
print("LIVE_ADK_BASELINE=PASS agents=4")
'

FAULT_JSON="$(protected_curl --fail --silent --show-error -X POST "${URL}/api/runs/${RUN_ID}/fault/stale_evidence")"
printf '%s' "$FAULT_JSON" | python -c '
import json,sys
x=json.load(sys.stdin)
b=x["active_blast_radius"]
assert b["invalidated_source"] == "history_snapshot", b
assert b["blocked_action_nodes"] == ["publish_action"], b
assert set(b["recomputation_set"]) == {"history_snapshot","statistician","skeptic","orchestrator"}, b
assert "scout" in b["reusable_checkpoints"], b
states={c["checkpoint_id"]: c["status"] for c in x["checkpoints"]}
assert states["publish_action"] == "BLOCKED", states
assert states["scout"] == "VERIFIED", states
print("TRUST_BREAK=PASS blocked=publish_action reused=scout")
'

RECOVERED_JSON="$(protected_curl --fail --silent --show-error -X POST "${URL}/api/runs/${RUN_ID}/recover")"
printf '%s' "$RECOVERED_JSON" | python -c '
import json,sys
x=json.load(sys.stdin)
assert x["active_blast_radius"] is None, x["active_blast_radius"]
states={c["checkpoint_id"]: c["status"] for c in x["checkpoints"]}
assert states["publish_action"] == "VERIFIED", states
recovery=x["execution"]["recovery"]
assert [r["checkpoint_id"] for r in recovery] == ["statistician","skeptic","orchestrator"], recovery
assert all(r["provider"] == "google_adk_vertex" for r in recovery), recovery
b=x["benchmark"]
assert b["full_restart_agent_executions"] == 4, b
assert b["selective_recovery_agent_executions"] == 3, b
assert b["reused_agent_checkpoints"] == 1, b
assert b["measurement_class"].startswith("google_adk_live"), b
print("SELECTIVE_RECOVERY=PASS rerun=3 reused=1 final_action=VERIFIED")
if b.get("full_restart_model_calls") is not None and b.get("selective_recovery_model_calls") is not None:
    print(f"MODEL_CALLS full_restart={b[\"full_restart_model_calls\"]} selective={b[\"selective_recovery_model_calls\"]}")
if b.get("full_restart_input_tokens") is not None and b.get("selective_recovery_input_tokens") is not None:
    print(f"INPUT_TOKENS full_restart={b[\"full_restart_input_tokens\"]} selective={b[\"selective_recovery_input_tokens\"]}")
'

printf 'RUN_ID=%s\n' "$RUN_ID"
printf 'JUDGE_URL=%s/\n' "$URL"
printf 'JUDGE_FLOW=enter private Devpost testing key, then Start fleet -> stale_evidence -> recover\n'
