#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_NUMBER="${RECOVERY_MESH_EXPECTED_PROJECT_NUMBER:-457699623691}"
SERVICE="${RECOVERY_MESH_SERVICE:-evidencebound-recovery-mesh}"
RUN_REGION="${GOOGLE_CLOUD_RUN_REGION:-europe-west1}"
RUNTIME_SA_NAME="${RECOVERY_MESH_RUNTIME_SA:-recovery-mesh-runtime}"
BUILD_SA_NAME="${RECOVERY_MESH_BUILD_SA:-recovery-mesh-build}"
DEPLOYER_SA_NAME="${RECOVERY_MESH_DEPLOYER_SA:-recovery-mesh-deployer}"
JUDGE_SECRET_NAME="${RECOVERY_MESH_JUDGE_SECRET_NAME:-recovery-mesh-judge-key}"
JUDGE_SECRET_VERSION="${RECOVERY_MESH_JUDGE_SECRET_VERSION:-1}"
POOL_ID="${RECOVERY_MESH_WIF_POOL:-github-actions}"
PROVIDER_ID="${RECOVERY_MESH_WIF_PROVIDER:-recovery-mesh}"
REPO="${RECOVERY_MESH_GITHUB_REPOSITORY:-moneyparking/evidencebound-recovery-mesh}"
REPO_ID="${RECOVERY_MESH_GITHUB_REPOSITORY_ID:-1334014784}"
REPO_OWNER="${REPO%%/*}"

[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: $PROJECT_ID" >&2
  exit 2
}
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
[ "$PROJECT_NUMBER" = "$EXPECTED_PROJECT_NUMBER" ] || {
  echo "BLOCKER=unexpected project number: $PROJECT_NUMBER" >&2
  exit 3
}

REVISION="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$RUN_REGION" --format='value(status.latestReadyRevisionName)')"
[ -n "$REVISION" ] || { echo "BLOCKER=no ready Cloud Run revision" >&2; exit 4; }
SERVICE_URL="https://${SERVICE}-${PROJECT_NUMBER}.${RUN_REGION}.run.app"
STATUS_URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$RUN_REGION" --format='value(status.url)')"

printf 'POSTDEPLOY_SERVICE_URL=%s\n' "$SERVICE_URL"
printf 'POSTDEPLOY_STATUS_URL=%s\n' "$STATUS_URL"
printf 'POSTDEPLOY_REVISION=%s\n' "$REVISION"

export RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE="$(
  gcloud secrets versions access "$JUDGE_SECRET_VERSION" \
    --secret "$JUDGE_SECRET_NAME" \
    --project "$PROJECT_ID"
)"
[ -n "$RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE" ] || {
  echo "BLOCKER=judge key unavailable" >&2
  exit 5
}
"$(dirname "$0")/smoke-cloud-run.sh" "$SERVICE_URL"
unset RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE

ensure_service_account() {
  local name="$1"
  local email="$2"
  local display_name="$3"
  if ! gcloud iam service-accounts describe "$email" --project "$PROJECT_ID" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$name" --project "$PROJECT_ID" --display-name "$display_name"
  fi
}

RUNTIME_SA="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_SA="${BUILD_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
DEPLOYER_SA="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
ensure_service_account "$DEPLOYER_SA_NAME" "$DEPLOYER_SA" "EvidenceBound Recovery Mesh GitHub deployer"

for ROLE in roles/run.sourceDeveloper roles/serviceusage.serviceUsageConsumer roles/aiplatform.user; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:${DEPLOYER_SA}" \
    --role "$ROLE" --condition=None --quiet >/dev/null
done

for TARGET_SA in "$RUNTIME_SA" "$BUILD_SA"; do
  gcloud iam service-accounts add-iam-policy-binding "$TARGET_SA" \
    --project "$PROJECT_ID" \
    --member "serviceAccount:${DEPLOYER_SA}" \
    --role roles/iam.serviceAccountUser \
    --condition=None --quiet >/dev/null
done

gcloud secrets add-iam-policy-binding "$JUDGE_SECRET_NAME" \
  --project "$PROJECT_ID" \
  --member "serviceAccount:${DEPLOYER_SA}" \
  --role roles/secretmanager.secretAccessor \
  --condition=None --quiet >/dev/null

if ! gcloud iam workload-identity-pools describe "$POOL_ID" --project "$PROJECT_ID" --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project "$PROJECT_ID" --location=global \
    --display-name "GitHub Actions" \
    --description "Keyless GitHub Actions identities for hackathon deployments"
fi

if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --project "$PROJECT_ID" --location=global \
    --workload-identity-pool="$POOL_ID" \
    --display-name "EvidenceBound Recovery Mesh" \
    --issuer-uri="https://token.actions.githubusercontent.com/" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_id=assertion.repository_id,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository_id=='${REPO_ID}' && assertion.repository_owner=='${REPO_OWNER}' && assertion.ref=='refs/heads/main'"
fi

WIF_MEMBER="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository_id/${REPO_ID}"
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER_SA" \
  --project "$PROJECT_ID" \
  --member "$WIF_MEMBER" \
  --role roles/iam.workloadIdentityUser \
  --condition=None --quiet >/dev/null

PROVIDER_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
printf 'GCP_POSTDEPLOY_FINALIZE=PASS\n'
printf 'SERVICE_URL=%s\n' "$SERVICE_URL"
printf 'CLOUD_RUN_REVISION=%s\n' "$REVISION"
printf 'GITHUB_DEPLOYER_SERVICE_ACCOUNT=%s\n' "$DEPLOYER_SA"
printf 'WORKLOAD_IDENTITY_PROVIDER=%s\n' "$PROVIDER_RESOURCE"
printf 'JUDGE_SECRET_NAME=%s\n' "$JUDGE_SECRET_NAME"
printf 'JUDGE_SECRET_VERSION=%s\n' "$JUDGE_SECRET_VERSION"
