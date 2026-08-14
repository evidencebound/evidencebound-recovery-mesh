#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
RUN_REGION="${GOOGLE_CLOUD_RUN_REGION:-europe-west1}"
VERTEX_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
SERVICE="${RECOVERY_MESH_SERVICE:-evidencebound-recovery-mesh}"
MODEL="${RECOVERY_MESH_MODEL:-gemini-3.5-flash}"
LIVE_MODEL_CALL_BUDGET="${RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET:-64}"
JUDGE_SECRET_NAME="${RECOVERY_MESH_JUDGE_SECRET_NAME:-recovery-mesh-judge-key}"
JUDGE_SECRET_VERSION="${RECOVERY_MESH_JUDGE_SECRET_VERSION:-1}"
RUNTIME_SA_NAME="${RECOVERY_MESH_RUNTIME_SA:-recovery-mesh-runtime}"
BUILD_SA_NAME="${RECOVERY_MESH_BUILD_SA:-recovery-mesh-build}"
RUNTIME_SA="${RUNTIME_SA_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"
BUILD_SA="${BUILD_SA_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"
BUILD_SA_RESOURCE="projects/${GOOGLE_CLOUD_PROJECT}/serviceAccounts/${BUILD_SA}"

[[ "$LIVE_MODEL_CALL_BUDGET" =~ ^[1-9][0-9]*$ ]] || {
  echo "BLOCKER=RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET must be a positive integer" >&2
  exit 4
}
[[ "$JUDGE_SECRET_VERSION" =~ ^[1-9][0-9]*$ ]] || {
  echo "BLOCKER=RECOVERY_MESH_JUDGE_SECRET_VERSION must be a positive integer" >&2
  exit 5
}

"$(dirname "$0")/gcp-live-preflight.sh"

if [ -z "${RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE:-}" ]; then
  export RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE="$(
    gcloud secrets versions access "$JUDGE_SECRET_VERSION" \
      --secret "$JUDGE_SECRET_NAME" \
      --project "$GOOGLE_CLOUD_PROJECT"
  )"
fi
[ -n "$RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE" ] || {
  echo "BLOCKER=judge key unavailable for protected production smoke" >&2
  exit 6
}

PUBLIC_ARGS=()
if [ "${RECOVERY_MESH_PUBLIC_BOOTSTRAP:-0}" = "1" ]; then
  # Public UI/health, application-level protection on run/mutation endpoints.
  # Force internet ingress and keep the run.app URL enabled so project/org defaults cannot
  # silently turn a judge-facing service into a network-hidden HTTP 404.
  PUBLIC_ARGS+=(--ingress all --default-url --no-invoker-iam-check)
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
  --update-secrets "RECOVERY_MESH_JUDGE_KEY=${JUDGE_SECRET_NAME}:${JUDGE_SECRET_VERSION}" \
  --labels "app=evidencebound-recovery-mesh,hackathon=all-things-agentic-2026" \
  --quiet

URL="$(gcloud run services describe "$SERVICE" --project "$GOOGLE_CLOUD_PROJECT" --region "$RUN_REGION" --format='value(status.url)')"
REVISION="$(gcloud run services describe "$SERVICE" --project "$GOOGLE_CLOUD_PROJECT" --region "$RUN_REGION" --format='value(status.latestReadyRevisionName)')"
printf 'SERVICE_URL=%s\n' "$URL"
printf 'CLOUD_RUN_REVISION=%s\n' "$REVISION"
printf 'RUNTIME_SERVICE_ACCOUNT=%s\n' "$RUNTIME_SA"
printf 'BUILD_SERVICE_ACCOUNT=%s\n' "$BUILD_SA"
printf 'LIVE_MODEL_CALL_BUDGET_PER_PROCESS=%s\n' "$LIVE_MODEL_CALL_BUDGET"
printf 'JUDGE_ACCESS=SECRET_MANAGER_PROTECTED\n'
"$(dirname "$0")/smoke-cloud-run.sh" "$URL"
unset RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE
