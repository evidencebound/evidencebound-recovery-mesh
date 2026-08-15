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

command -v gcloud >/dev/null || { echo "BLOCKER=gcloud CLI not installed" >&2; exit 2; }

[ "$GOOGLE_CLOUD_PROJECT" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected Agent Registry project: $GOOGLE_CLOUD_PROJECT" >&2
  exit 3
}

# The project number is immutable and already anchored in the exact WIF provider path used by
# the main-only workflow. Do not call `gcloud projects describe` here: that adds an unrelated
# Cloud Resource Manager API dependency to a bounded Agent Registry control-plane operation.
PROJECT_NUMBER="$EXPECTED_PROJECT_NUMBER"
printf 'AGENT_REGISTRY_PROJECT=%s project_number=%s\n' "$GOOGLE_CLOUD_PROJECT" "$PROJECT_NUMBER"

ENABLED="$(gcloud services list --enabled --project "$GOOGLE_CLOUD_PROJECT" \
  --filter='config.name:agentregistry.googleapis.com' --format='value(config.name)')"
[ "$ENABLED" = "agentregistry.googleapis.com" ] || {
  echo "BLOCKER=agentregistry.googleapis.com is not enabled" >&2
  exit 5
}

SERVICE_URL="$(gcloud run services describe "$CLOUD_RUN_SERVICE" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$RUN_REGION" \
  --format='value(status.url)')"
[ -n "$SERVICE_URL" ] || { echo "BLOCKER=Cloud Run service URL is empty" >&2; exit 6; }

DESCRIPTION="Trust-aware multi-agent recovery controller. Catalogs the EvidenceBound Recovery Mesh fleet entry point; internal Statistician, Scout, Skeptic, and Orchestrator roles remain governed by the deterministic Trust Graph and fail-closed action gate."
INTERFACE="url=${SERVICE_URL},protocolBinding=http-json"

if gcloud agent-registry services describe "$REGISTRY_SERVICE_ID" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "$REGISTRY_LOCATION" >/dev/null 2>&1; then
  gcloud agent-registry services update "$REGISTRY_SERVICE_ID" \
    --project "$GOOGLE_CLOUD_PROJECT" \
    --location "$REGISTRY_LOCATION" \
    --display-name "$DISPLAY_NAME" \
    --description "$DESCRIPTION" \
    --agent-spec-type no-spec \
    --interfaces "$INTERFACE" \
    --quiet >/dev/null
  REGISTRY_OPERATION=updated
else
  gcloud agent-registry services create "$REGISTRY_SERVICE_ID" \
    --project "$GOOGLE_CLOUD_PROJECT" \
    --location "$REGISTRY_LOCATION" \
    --display-name "$DISPLAY_NAME" \
    --description "$DESCRIPTION" \
    --agent-spec-type no-spec \
    --interfaces "$INTERFACE" \
    --quiet >/dev/null
  REGISTRY_OPERATION=created
fi

SERVICE_RESOURCE="$(gcloud agent-registry services describe "$REGISTRY_SERVICE_ID" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "$REGISTRY_LOCATION" \
  --format='value(name)')"
[ -n "$SERVICE_RESOURCE" ] || { echo "BLOCKER=Agent Registry Service not observable" >&2; exit 7; }

# Manual registration projects the writable Service into a read-only Agent. Allow a bounded
# propagation window and fail rather than claiming discoverability from the write alone.
AGENT_RESOURCE=""
for _ in $(seq 1 12); do
  AGENT_RESOURCE="$(gcloud agent-registry agents list \
    --project "$GOOGLE_CLOUD_PROJECT" \
    --location "$REGISTRY_LOCATION" \
    --filter="displayName=\"${DISPLAY_NAME}\"" \
    --format='value(name)' \
    --limit=1 2>/dev/null || true)"
  [ -n "$AGENT_RESOURCE" ] && break
  sleep 5
done
[ -n "$AGENT_RESOURCE" ] || {
  echo "BLOCKER=Agent Registry Service exists but discoverable Agent projection was not observed" >&2
  exit 8
}

printf 'AGENT_REGISTRY=PASS operation=%s location=%s\n' "$REGISTRY_OPERATION" "$REGISTRY_LOCATION"
printf 'AGENT_REGISTRY_SERVICE=%s\n' "$SERVICE_RESOURCE"
printf 'AGENT_REGISTRY_AGENT=%s\n' "$AGENT_RESOURCE"
printf 'AGENT_REGISTRY_INTERFACE=%s\n' "$SERVICE_URL"
