#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
REGISTRY_LOCATION="${RECOVERY_MESH_AGENT_REGISTRY_LOCATION:-global}"
REGISTRY_SERVICE_ID="${RECOVERY_MESH_AGENT_REGISTRY_SERVICE_ID:-recovery-mesh-fleet}"
DISPLAY_NAME="${RECOVERY_MESH_AGENT_REGISTRY_DISPLAY_NAME:-EvidenceBound Recovery Mesh}"
CLOUD_RUN_SERVICE="${RECOVERY_MESH_SERVICE:-evidencebound-recovery-mesh}"
RUN_REGION="${GOOGLE_CLOUD_RUN_REGION:-europe-west1}"
EXPECTED_PROJECT_ID="evidencebound-rm-c977c1"
EXPECTED_PROJECT_NUMBER="457699623691"
API_ROOT="https://agentregistry.googleapis.com/v1"
PARENT="projects/${GOOGLE_CLOUD_PROJECT}/locations/${REGISTRY_LOCATION}"
SERVICE_RESOURCE="${PARENT}/services/${REGISTRY_SERVICE_ID}"
SERVICE_URL_API="${API_ROOT}/${SERVICE_RESOURCE}"
CREATE_REQUEST_ID="a86d3907-23ac-41d5-b253-92431ba51fcb"

for cmd in gcloud curl jq; do
  command -v "$cmd" >/dev/null || { echo "BLOCKER=${cmd} is not installed" >&2; exit 2; }
done

[ "$GOOGLE_CLOUD_PROJECT" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected Agent Registry project: $GOOGLE_CLOUD_PROJECT" >&2
  exit 3
}

# Project number is immutable and anchored in the exact WIF provider path used by the main-only
# workflow. Avoid introducing Cloud Resource Manager solely for a redundant project lookup.
PROJECT_NUMBER="$EXPECTED_PROJECT_NUMBER"
printf 'AGENT_REGISTRY_PROJECT=%s project_number=%s\n' "$GOOGLE_CLOUD_PROJECT" "$PROJECT_NUMBER"

ENABLED="$(gcloud services list --enabled --project "$GOOGLE_CLOUD_PROJECT" \
  --filter='config.name:agentregistry.googleapis.com' --format='value(config.name)')"
[ "$ENABLED" = "agentregistry.googleapis.com" ] || {
  echo "BLOCKER=agentregistry.googleapis.com is not enabled" >&2
  exit 5
}

CLOUD_RUN_URL="$(gcloud run services describe "$CLOUD_RUN_SERVICE" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$RUN_REGION" \
  --format='value(status.url)')"
[ -n "$CLOUD_RUN_URL" ] || { echo "BLOCKER=Cloud Run service URL is empty" >&2; exit 6; }

ACCESS_TOKEN="$(gcloud auth print-access-token)"
[ -n "$ACCESS_TOKEN" ] || { echo "BLOCKER=unable to obtain WIF access token" >&2; exit 10; }
AUTH_HEADER="Authorization: Bearer ${ACCESS_TOKEN}"
DESCRIPTION="Trust-aware multi-agent recovery controller. Catalogs the EvidenceBound Recovery Mesh fleet entry point; internal Statistician, Scout, Skeptic, and Orchestrator roles remain governed by the deterministic Trust Graph and fail-closed action gate."

DESIRED_JSON="$(jq -n \
  --arg name "$SERVICE_RESOURCE" \
  --arg displayName "$DISPLAY_NAME" \
  --arg description "$DESCRIPTION" \
  --arg url "$CLOUD_RUN_URL" \
  '{name:$name,displayName:$displayName,description:$description,interfaces:[{url:$url,protocolBinding:"HTTP_JSON"}],agentSpec:{type:"NO_SPEC"}}')"

rest_call() {
  local method="$1" url="$2" outfile="$3" data="${4:-}"
  local args=(-sS -o "$outfile" -w '%{http_code}' -X "$method" -H "$AUTH_HEADER" -H 'Content-Type: application/json')
  if [ -n "$data" ]; then
    args+=(--data "$data")
  fi
  curl "${args[@]}" "$url"
}

print_error_and_exit() {
  local context="$1" code="$2" file="$3" exit_code="$4"
  local message reason
  message="$(jq -r '.error.message // "unknown API error"' "$file" 2>/dev/null || echo 'unknown API error')"
  reason="$(jq -r '.error.details[]? | select(."@type"=="type.googleapis.com/google.rpc.ErrorInfo") | .reason' "$file" 2>/dev/null | head -n1 || true)"
  echo "BLOCKER=${context} http=${code} reason=${reason:-unknown} message=${message}" >&2
  exit "$exit_code"
}

wait_operation() {
  local operation_file="$1" context="$2"
  local operation_name operation_url code done message
  operation_name="$(jq -r '.name // ""' "$operation_file")"
  [ -n "$operation_name" ] || {
    echo "BLOCKER=${context} returned no long-running operation name" >&2
    exit 19
  }
  operation_url="${API_ROOT}/${operation_name}"
  for _ in $(seq 1 60); do
    code="$(rest_call GET "$operation_url" /tmp/agent-registry-operation-state.json)"
    [ "$code" = "200" ] || print_error_and_exit "${context} operation lookup failed" "$code" /tmp/agent-registry-operation-state.json 20
    done="$(jq -r '.done // false' /tmp/agent-registry-operation-state.json)"
    if [ "$done" = "true" ]; then
      if jq -e '.error' /tmp/agent-registry-operation-state.json >/dev/null 2>&1; then
        message="$(jq -r '.error.message // "unknown long-running operation error"' /tmp/agent-registry-operation-state.json)"
        echo "BLOCKER=${context} operation failed message=${message}" >&2
        exit 21
      fi
      printf 'AGENT_REGISTRY_OPERATION=PASS name=%s\n' "$operation_name"
      return 0
    fi
    sleep 5
  done
  echo "BLOCKER=${context} operation did not complete within bounded 300s window name=${operation_name}" >&2
  exit 22
}

GET_CODE="$(rest_call GET "$SERVICE_URL_API" /tmp/agent-registry-service-before.json)"
if [ "$GET_CODE" = "200" ]; then
  CURRENT_DISPLAY="$(jq -r '.displayName // ""' /tmp/agent-registry-service-before.json)"
  CURRENT_DESCRIPTION="$(jq -r '.description // ""' /tmp/agent-registry-service-before.json)"
  CURRENT_URL="$(jq -r '.interfaces[0].url // ""' /tmp/agent-registry-service-before.json)"
  CURRENT_BINDING="$(jq -r '.interfaces[0].protocolBinding // ""' /tmp/agent-registry-service-before.json)"
  CURRENT_TYPE="$(jq -r '.agentSpec.type // ""' /tmp/agent-registry-service-before.json)"
  if [ "$CURRENT_DISPLAY" = "$DISPLAY_NAME" ] && \
     [ "$CURRENT_DESCRIPTION" = "$DESCRIPTION" ] && \
     [ "$CURRENT_URL" = "$CLOUD_RUN_URL" ] && \
     [ "$CURRENT_BINDING" = "HTTP_JSON" ] && \
     [ "$CURRENT_TYPE" = "NO_SPEC" ]; then
    REGISTRY_OPERATION=existing
  else
    PATCH_URL="${SERVICE_URL_API}?updateMask=displayName,description,interfaces,agentSpec"
    PATCH_CODE="$(rest_call PATCH "$PATCH_URL" /tmp/agent-registry-operation.json "$DESIRED_JSON")"
    [ "$PATCH_CODE" = "200" ] || print_error_and_exit "Agent Registry Service update denied or failed" "$PATCH_CODE" /tmp/agent-registry-operation.json 12
    wait_operation /tmp/agent-registry-operation.json "Agent Registry Service update"
    REGISTRY_OPERATION=updated
  fi
elif [ "$GET_CODE" = "404" ]; then
  CREATE_URL="${API_ROOT}/${PARENT}/services?serviceId=${REGISTRY_SERVICE_ID}&requestId=${CREATE_REQUEST_ID}"
  CREATE_CODE="$(rest_call POST "$CREATE_URL" /tmp/agent-registry-operation.json "$DESIRED_JSON")"
  if [ "$CREATE_CODE" = "200" ]; then
    wait_operation /tmp/agent-registry-operation.json "Agent Registry Service create"
    REGISTRY_OPERATION=created
  elif [ "$CREATE_CODE" = "409" ]; then
    REGISTRY_OPERATION=existing
  else
    print_error_and_exit "Agent Registry Service create denied or failed" "$CREATE_CODE" /tmp/agent-registry-operation.json 11
  fi
elif [ "$GET_CODE" = "403" ]; then
  print_error_and_exit "Agent Registry Service read denied" "$GET_CODE" /tmp/agent-registry-service-before.json 13
else
  print_error_and_exit "Agent Registry Service lookup failed" "$GET_CODE" /tmp/agent-registry-service-before.json 14
fi

# A successful manual registration must result in an observable read-only Agent. Prefer the
# Service's output-only registryResource, but also query the consumer-side Agent list because
# the read-only projection can become discoverable before the Service representation reflects
# registryResource. Both paths still require a successful Agent GET before PASS.
AGENT_RESOURCE=""
DISCOVERY_PATH=""
for _ in $(seq 1 60); do
  CODE="$(rest_call GET "$SERVICE_URL_API" /tmp/agent-registry-service.json)"
  if [ "$CODE" = "200" ]; then
    AGENT_RESOURCE="$(jq -r '.registryResource // ""' /tmp/agent-registry-service.json)"
    if [ -n "$AGENT_RESOURCE" ]; then
      DISCOVERY_PATH=service-registry-resource
      break
    fi
  elif [ "$CODE" = "403" ]; then
    print_error_and_exit "Agent Registry Service observation denied" "$CODE" /tmp/agent-registry-service.json 15
  fi

  LIST_CODE="$(rest_call GET "${API_ROOT}/${PARENT}/agents?pageSize=100" /tmp/agent-registry-agents.json)"
  if [ "$LIST_CODE" = "200" ]; then
    MATCH_COUNT="$(jq --arg display "$DISPLAY_NAME" '[.agents[]? | select(.displayName == $display)] | length' /tmp/agent-registry-agents.json)"
    if [ "$MATCH_COUNT" = "1" ]; then
      AGENT_RESOURCE="$(jq -r --arg display "$DISPLAY_NAME" '.agents[]? | select(.displayName == $display) | .name' /tmp/agent-registry-agents.json | head -n1)"
      DISCOVERY_PATH=agent-list
      break
    elif [ "$MATCH_COUNT" -gt 1 ]; then
      echo "BLOCKER=multiple Agent Registry Agents share displayName=${DISPLAY_NAME}; discovery is ambiguous" >&2
      exit 23
    fi
  elif [ "$LIST_CODE" = "403" ]; then
    print_error_and_exit "Agent Registry Agent list denied" "$LIST_CODE" /tmp/agent-registry-agents.json 24
  fi
  sleep 5
done
[ -n "$AGENT_RESOURCE" ] || {
  echo "BLOCKER=Agent Registry Service did not produce a discoverable Agent within bounded 300s window" >&2
  exit 8
}
case "$AGENT_RESOURCE" in
  projects/*/locations/*/agents/*) ;;
  *) echo "BLOCKER=discovered resource is not an Agent resource: $AGENT_RESOURCE" >&2; exit 16 ;;
esac

AGENT_CODE="$(rest_call GET "${API_ROOT}/${AGENT_RESOURCE}" /tmp/agent-registry-agent.json)"
[ "$AGENT_CODE" = "200" ] || print_error_and_exit "Agent Registry read-only Agent verification failed" "$AGENT_CODE" /tmp/agent-registry-agent.json 17
VERIFIED_AGENT_NAME="$(jq -r '.name // ""' /tmp/agent-registry-agent.json)"
VERIFIED_AGENT_DISPLAY="$(jq -r '.displayName // ""' /tmp/agent-registry-agent.json)"
[ "$VERIFIED_AGENT_NAME" = "$AGENT_RESOURCE" ] || {
  echo "BLOCKER=Agent Registry Agent response did not match discovered resource" >&2
  exit 18
}
[ "$VERIFIED_AGENT_DISPLAY" = "$DISPLAY_NAME" ] || {
  echo "BLOCKER=Agent Registry Agent display name did not match expected fleet entry" >&2
  exit 25
}

printf 'AGENT_REGISTRY=PASS operation=%s location=%s transport=rest-v1 discovery=%s\n' "$REGISTRY_OPERATION" "$REGISTRY_LOCATION" "$DISCOVERY_PATH"
printf 'AGENT_REGISTRY_SERVICE=%s\n' "$SERVICE_RESOURCE"
printf 'AGENT_REGISTRY_AGENT=%s\n' "$AGENT_RESOURCE"
printf 'AGENT_REGISTRY_INTERFACE=%s\n' "$CLOUD_RUN_URL"
