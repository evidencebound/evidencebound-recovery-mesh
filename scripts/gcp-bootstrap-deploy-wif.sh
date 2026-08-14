#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_NUMBER="${RECOVERY_MESH_EXPECTED_PROJECT_NUMBER:-457699623691}"
POOL_ID="${RECOVERY_MESH_WIF_POOL:-github-actions}"
PROVIDER_ID="${RECOVERY_MESH_WIF_PROVIDER:-recovery-mesh}"
PROVIDER_DISPLAY_NAME="${RECOVERY_MESH_WIF_PROVIDER_DISPLAY_NAME:-Recovery Mesh deploy}"
DEPLOYER_SA_NAME="${RECOVERY_MESH_DEPLOYER_SA:-recovery-mesh-deployer}"
RUNTIME_SA_NAME="${RECOVERY_MESH_RUNTIME_SA:-recovery-mesh-runtime}"
BUILD_SA_NAME="${RECOVERY_MESH_BUILD_SA:-recovery-mesh-build}"
JUDGE_SECRET_NAME="${RECOVERY_MESH_JUDGE_SECRET_NAME:-recovery-mesh-judge-key}"
DEPLOYER_SA="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME_SA="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_SA="${BUILD_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
REPO="${RECOVERY_MESH_GITHUB_REPOSITORY:-moneyparking/evidencebound-recovery-mesh}"
REPO_ID="${RECOVERY_MESH_GITHUB_REPOSITORY_ID:-1334014784}"
REPO_OWNER="${REPO%%/*}"

[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: $PROJECT_ID" >&2
  exit 2
}
[ "${#PROVIDER_DISPLAY_NAME}" -le 32 ] || {
  echo "BLOCKER=deploy workload identity provider display name exceeds 32 characters" >&2
  exit 2
}

ACTIVE_ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
[ -n "$ACTIVE_ACCOUNT" ] || {
  echo "BLOCKER=no active gcloud account" >&2
  exit 3
}

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
[ "$PROJECT_NUMBER" = "$EXPECTED_PROJECT_NUMBER" ] || {
  echo "BLOCKER=unexpected project number: $PROJECT_NUMBER" >&2
  exit 4
}

printf 'DEPLOY_WIF_BOOTSTRAP_MODE=IAM_ONLY\n'
printf 'ACTIVE_ACCOUNT=%s\n' "$ACTIVE_ACCOUNT"
printf 'PROJECT_ID=%s\n' "$PROJECT_ID"
printf 'PROJECT_NUMBER=%s\n' "$PROJECT_NUMBER"

if ! gcloud iam service-accounts describe "$DEPLOYER_SA" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$DEPLOYER_SA_NAME" \
    --project "$PROJECT_ID" \
    --display-name "EvidenceBound Recovery Mesh GitHub deployer"
fi

# Roles required by the existing source-deploy workflow and its live preflight.
for ROLE in \
  roles/run.sourceDeveloper \
  roles/serviceusage.serviceUsageConsumer \
  roles/aiplatform.user; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:${DEPLOYER_SA}" \
    --role "$ROLE" \
    --condition=None \
    --quiet >/dev/null
done

for TARGET_SA in "$RUNTIME_SA" "$BUILD_SA"; do
  gcloud iam service-accounts add-iam-policy-binding "$TARGET_SA" \
    --project "$PROJECT_ID" \
    --member "serviceAccount:${DEPLOYER_SA}" \
    --role roles/iam.serviceAccountUser \
    --condition=None \
    --quiet >/dev/null
done

gcloud secrets add-iam-policy-binding "$JUDGE_SECRET_NAME" \
  --project "$PROJECT_ID" \
  --member "serviceAccount:${DEPLOYER_SA}" \
  --role roles/secretmanager.secretAccessor \
  --condition=None \
  --quiet >/dev/null

if ! gcloud iam workload-identity-pools describe "$POOL_ID" \
  --project "$PROJECT_ID" \
  --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --display-name "GitHub Actions" \
    --description "Keyless GitHub Actions identities for EvidenceBound Recovery Mesh"
fi

POOL_STATE=""
for ATTEMPT in 1 2 3 4 5 6; do
  POOL_STATE="$(gcloud iam workload-identity-pools describe "$POOL_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --format='value(state)' 2>/dev/null || true)"
  printf 'DEPLOY_WIF_POOL_READINESS attempt=%s state=%s\n' "$ATTEMPT" "${POOL_STATE:-UNKNOWN}"
  [ "$POOL_STATE" = "ACTIVE" ] && break
  [ "$POOL_STATE" = "DELETED" ] && {
    echo "BLOCKER=workload identity pool is deleted; restore it deliberately" >&2
    exit 5
  }
  sleep 2
done
[ "$POOL_STATE" = "ACTIVE" ] || {
  echo "BLOCKER=workload identity pool is not ACTIVE: ${POOL_STATE:-UNKNOWN}" >&2
  exit 5
}

if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" \
  --location=global \
  --workload-identity-pool="$POOL_ID" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --workload-identity-pool="$POOL_ID" \
    --display-name "$PROVIDER_DISPLAY_NAME" \
    --issuer-uri="https://token.actions.githubusercontent.com/" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_id=assertion.repository_id,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository_id=='${REPO_ID}' && assertion.repository_owner=='${REPO_OWNER}' && assertion.ref=='refs/heads/main'"
fi

PROVIDER_STATE=""
PROVIDER_DISABLED=""
for ATTEMPT in 1 2 3 4 5 6; do
  PROVIDER_STATE="$(gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --workload-identity-pool="$POOL_ID" \
    --format='value(state)' 2>/dev/null || true)"
  PROVIDER_DISABLED="$(gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --workload-identity-pool="$POOL_ID" \
    --format='value(disabled)' 2>/dev/null || true)"
  printf 'DEPLOY_WIF_PROVIDER_READINESS attempt=%s state=%s disabled=%s\n' \
    "$ATTEMPT" "${PROVIDER_STATE:-UNKNOWN}" "${PROVIDER_DISABLED:-false}"
  [ "$PROVIDER_STATE" = "ACTIVE" ] && [ "${PROVIDER_DISABLED:-False}" != "True" ] && [ "${PROVIDER_DISABLED:-false}" != "true" ] && break
  [ "$PROVIDER_STATE" = "DELETED" ] && {
    echo "BLOCKER=deploy workload identity provider is deleted; restore it deliberately" >&2
    exit 6
  }
  sleep 2
done
[ "$PROVIDER_STATE" = "ACTIVE" ] || {
  echo "BLOCKER=deploy workload identity provider is not ACTIVE: ${PROVIDER_STATE:-UNKNOWN}" >&2
  exit 6
}
case "${PROVIDER_DISABLED:-false}" in
  True|true|TRUE|1)
    echo "BLOCKER=deploy workload identity provider is disabled" >&2
    exit 6
    ;;
esac

WIF_MEMBER="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository_id/${REPO_ID}"
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER_SA" \
  --project "$PROJECT_ID" \
  --member "$WIF_MEMBER" \
  --role roles/iam.workloadIdentityUser \
  --condition=None \
  --quiet >/dev/null

PROVIDER_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
printf 'DEPLOY_WIF_BOOTSTRAP=PASS\n'
printf 'DEPLOYER_SERVICE_ACCOUNT=%s\n' "$DEPLOYER_SA"
printf 'DEPLOY_WORKLOAD_IDENTITY_PROVIDER=%s\n' "$PROVIDER_RESOURCE"
printf 'CLOUD_RUN_MUTATIONS=NONE\n'
printf 'BUILD_OR_DEPLOY=NONE\n'
