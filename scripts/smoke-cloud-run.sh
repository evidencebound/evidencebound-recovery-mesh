#!/usr/bin/env bash
set -euo pipefail
URL="${1:?Usage: smoke-cloud-run.sh https://service.run.app}"
: "${RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE:?Protected smoke requires RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE}"
: "${GOOGLE_CLOUD_PROJECT:?Durable smoke requires GOOGLE_CLOUD_PROJECT}"

protected_curl() {
  # Feed the credential through curl config stdin so the secret is not present in the curl argv.
  printf 'header = "X-Recovery-Mesh-Judge-Key: %s"\n' "$RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE" \
    | curl --config - "$@"
}

firestore_receipt_count() {
  local run_id="$1"
  local access_token query_json response_json
  access_token="$(gcloud auth print-access-token)"
  [ -n "$access_token" ] || {
    echo "BLOCKER=unable to obtain deployer access token for Firestore readback" >&2
    return 1
  }
  query_json="$(python3 - "$run_id" <<'PY'
import json
import sys

run_id = sys.argv[1]
print(json.dumps({
    "structuredQuery": {
        "from": [{"collectionId": "recovery_mesh_action_receipts"}],
        "where": {
            "fieldFilter": {
                "field": {"fieldPath": "run_id"},
                "op": "EQUAL",
                "value": {"stringValue": run_id},
            }
        },
    }
}))
PY
)"
  response_json="$(printf '%s' "$query_json" | curl --fail --silent --show-error \
    --request POST \
    --header "Authorization: Bearer ${access_token}" \
    --header 'Content-Type: application/json' \
    --data-binary @- \
    "https://firestore.googleapis.com/v1/projects/${GOOGLE_CLOUD_PROJECT}/databases/(default)/documents:runQuery")"
  unset access_token
  printf '%s' "$response_json" | python3 -c '
import json,sys
rows=json.load(sys.stdin)
print(sum(1 for row in rows if isinstance(row,dict) and "document" in row))
'
}

HEALTH_JSON="$(curl --fail --silent --show-error "${URL}/health")"
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
persistence=x["persistence"]
assert persistence["provider"]=="firestore", persistence
assert persistence["durable"] is True, persistence
print("HEALTH=PASS provider={} model={} persistence={} durable=true judge_access=protected".format(execution["provider"], execution["model"], persistence["provider"]))
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
persistence=x["persistence"]
assert persistence["provider"] == "firestore", persistence
assert persistence["durable"] is True, persistence
print("LIVE_ADK_BASELINE=PASS agents=4 persistence=firestore")
'

DURABLE_BASELINE_JSON="$(protected_curl --fail --silent --show-error "${URL}/api/durable-runs/${RUN_ID}")"
printf '%s' "$DURABLE_BASELINE_JSON" | python -c '
import json,sys
x=json.load(sys.stdin)
s=x["snapshot"]
assert s["run_id"] == sys.argv[1], s.get("run_id")
assert s["persistence"]["provider"] == "firestore", s["persistence"]
assert s["persistence"]["durable"] is True, s["persistence"]
assert x["action_receipt"] is None, x["action_receipt"]
assert x["rehydration"]["trusted"] is True, x["rehydration"]
print("DURABLE_BASELINE=PASS persisted=same_run receipt=absent rehydration=trusted")
' "$RUN_ID"

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

DURABLE_BLOCKED_JSON="$(protected_curl --fail --silent --show-error "${URL}/api/durable-runs/${RUN_ID}")"
printf '%s' "$DURABLE_BLOCKED_JSON" | python -c '
import json,sys
x=json.load(sys.stdin)
s=x["snapshot"]
states={c["checkpoint_id"]: c["status"] for c in s["checkpoints"]}
assert states["publish_action"] == "BLOCKED", states
assert x["action_receipt"] is None, x["action_receipt"]
assert s["action_receipt"] is None, s["action_receipt"]
assert x["rehydration"]["trusted"] is True, x["rehydration"]
print("DURABLE_BLOCKED=PASS action=BLOCKED receipt=absent persisted_trust=validated")
'
BLOCKED_RECEIPT_COUNT="$(firestore_receipt_count "$RUN_ID")"
[ "$BLOCKED_RECEIPT_COUNT" = "0" ] || {
  echo "BLOCKER=Firestore contained ${BLOCKED_RECEIPT_COUNT} action receipts while publish_action was BLOCKED" >&2
  exit 8
}
printf 'FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0 run_id=%s\n' "$RUN_ID"

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
    print("MODEL_CALLS full_restart={} selective={}".format(b["full_restart_model_calls"], b["selective_recovery_model_calls"]))
if b.get("full_restart_input_tokens") is not None and b.get("selective_recovery_input_tokens") is not None:
    print("INPUT_TOKENS full_restart={} selective={}".format(b["full_restart_input_tokens"], b["selective_recovery_input_tokens"]))
'

DURABLE_RECOVERED_JSON="$(protected_curl --fail --silent --show-error "${URL}/api/durable-runs/${RUN_ID}")"
printf '%s' "$DURABLE_RECOVERED_JSON" | python -c '
import json,sys
x=json.load(sys.stdin)
s=x["snapshot"]
assert s["run_id"] == sys.argv[1], s.get("run_id")
assert x["action_receipt"] is not None, x["action_receipt"]
assert s["action_receipt"] is not None, s["action_receipt"]
assert x["action_receipt"]["payload_digest"] == s["action_receipt"]["payload_digest"], x
assert x["rehydration"]["trusted"] is True, x["rehydration"]
assert x["rehydration"]["failures"] == [], x["rehydration"]
print("DURABLE_RECOVERY=PASS receipt=present rehydration=trusted")
' "$RUN_ID"
RECOVERED_RECEIPT_COUNT="$(firestore_receipt_count "$RUN_ID")"
[ "$RECOVERED_RECEIPT_COUNT" = "1" ] || {
  echo "BLOCKER=expected exactly one Firestore action receipt after recovery, got ${RECOVERED_RECEIPT_COUNT}" >&2
  exit 9
}
printf 'FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1 run_id=%s\n' "$RUN_ID"

printf 'RUN_ID=%s\n' "$RUN_ID"
printf 'JUDGE_URL=%s/\n' "$URL"
printf 'JUDGE_FLOW=enter private Devpost testing key, then Start fleet -> stale_evidence -> recover\n'
