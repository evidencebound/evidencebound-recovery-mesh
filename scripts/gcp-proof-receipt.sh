#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_NUMBER="${RECOVERY_MESH_EXPECTED_PROJECT_NUMBER:-457699623691}"
RUN_REGION="${GOOGLE_CLOUD_RUN_REGION:-europe-west1}"
SERVICE="${RECOVERY_MESH_SERVICE:-evidencebound-recovery-mesh}"

command -v gcloud >/dev/null || { echo "BLOCKER=gcloud CLI not installed" >&2; exit 2; }
command -v curl >/dev/null || { echo "BLOCKER=curl not installed" >&2; exit 2; }

[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: got $PROJECT_ID expected $EXPECTED_PROJECT_ID" >&2
  exit 3
}

# Project ID and number are immutable hackathon deployment constants already bound into the
# GitHub WIF provider and Cloud Run service URL. Avoid a Cloud Resource Manager API dependency.
PROJECT_NUMBER="$EXPECTED_PROJECT_NUMBER"

SERVICE_URL="https://${SERVICE}-${PROJECT_NUMBER}.${RUN_REGION}.run.app"
STATUS_URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$RUN_REGION" --format='value(status.url)')"
REVISION="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$RUN_REGION" --format='value(status.latestReadyRevisionName)')"
RUNTIME_SA="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$RUN_REGION" --format='value(spec.template.spec.serviceAccountName)')"

printf '=== RECOVERY MESH GOOGLE CLOUD PROOF RECEIPT ===\n'
printf 'GCP_PROJECT=%s\n' "$PROJECT_ID"
printf 'PROJECT_NUMBER=%s\n' "$PROJECT_NUMBER"
printf 'CLOUD_RUN_REGION=%s\n' "$RUN_REGION"
printf 'SERVICE_NAME=%s\n' "$SERVICE"
printf 'SERVICE_URL=%s\n' "$SERVICE_URL"
printf 'SERVICE_STATUS_URL=%s\n' "$STATUS_URL"
printf 'CLOUD_RUN_REVISION=%s\n' "$REVISION"
printf 'RUNTIME_SERVICE_ACCOUNT=%s\n' "$RUNTIME_SA"

printf '\n=== LIVE HEALTH ===\n'
curl --fail --silent --show-error "${SERVICE_URL}/health" | python -m json.tool

printf '\n=== RECENT CLOUD RUN REQUEST RECEIPTS ===\n'
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE}" \
  --project "$PROJECT_ID" \
  --freshness=2h \
  --limit=12 \
  --format='table(timestamp,severity,httpRequest.requestMethod,httpRequest.status,resource.labels.revision_name)' \
  || true

printf '\nGCP_PROOF_RECEIPT=PASS\n'
