#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
RUN_REGION="${GOOGLE_CLOUD_RUN_REGION:-europe-west1}"
VERTEX_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
SERVICE="${RECOVERY_MESH_SERVICE:-evidencebound-recovery-mesh}"
MODEL="${RECOVERY_MESH_MODEL:-gemini-3.5-flash}"
LIVE_MODEL_CALL_BUDGET="${RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET:-64}"
RUNTIME_SA_NAME="${RECOVERY_MESH_RUNTIME_SA:-recovery-mesh-runtime}"
BUILD_SA_NAME="${RECOVERY_MESH_BUILD_SA:-recovery-mesh-build}"
RUNTIME_SA="${RUNTIME_SA_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"
BUILD_SA="${BUILD_SA_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"
BUILD_SA_RESOURCE="projects/${GOOGLE_CLOUD_PROJECT}/serviceAccounts/${BUILD_SA}"

[[ "$LIVE_MODEL_CALL_BUDGET" =~ ^[1-9][0-9]*$ ]] || {
  echo "BLOCKER=RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET must be a positive integer" >&2
  exit 4
}

# First-time API/IAM/WIF setup is intentionally separated into gcp-owner-bootstrap.sh so the
# recurring deploy identity cannot mutate project IAM or enable services.
"$(dirname "$0")/gcp-live-preflight.sh"

PUBLIC_ARGS=()
if [ "${RECOVERY_MESH_PUBLIC_BOOTSTRAP:-0}" = "1" ]; then
  # Current Cloud Run guidance recommends disabling the Invoker IAM check for a public service.
  # This requires an owner/admin permission and is therefore never used by recurring CI.
  PUBLIC_ARGS+=(--no-invoker-iam-check)
fi

gcloud run deploy "$SERVICE" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$RUN_REGION" \
  --source . \
  --build-service-account "$BUILD_SA_RESOURCE" \
  --service-account "$RUNTIME_SA" \
  "${PUBLIC_ARGS[@]}" \
  --min 0 \
  --max 1 \
  --concurrency 20 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=${VERTEX_LOCATION},RECOVERY_MESH_MODEL=${MODEL},RECOVERY_MESH_EXECUTION_MODE=google_adk,RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET=${LIVE_MODEL_CALL_BUDGET}" \
  --labels "app=evidencebound-recovery-mesh,hackathon=all-things-agentic-2026"

URL="$(gcloud run services describe "$SERVICE" --project "$GOOGLE_CLOUD_PROJECT" --region "$RUN_REGION" --format='value(status.url)')"
REVISION="$(gcloud run services describe "$SERVICE" --project "$GOOGLE_CLOUD_PROJECT" --region "$RUN_REGION" --format='value(status.latestReadyRevisionName)')"
printf 'SERVICE_URL=%s\n' "$URL"
printf 'CLOUD_RUN_REVISION=%s\n' "$REVISION"
printf 'RUNTIME_SERVICE_ACCOUNT=%s\n' "$RUNTIME_SA"
printf 'BUILD_SERVICE_ACCOUNT=%s\n' "$BUILD_SA"
printf 'LIVE_MODEL_CALL_BUDGET_PER_PROCESS=%s\n' "$LIVE_MODEL_CALL_BUDGET"
"$(dirname "$0")/smoke-cloud-run.sh" "$URL"
