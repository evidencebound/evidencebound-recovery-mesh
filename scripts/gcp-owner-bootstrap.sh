#!/usr/bin/env bash
set -euo pipefail

REPO="${RECOVERY_MESH_GITHUB_REPOSITORY:-moneyparking/evidencebound-recovery-mesh}"
REPO_ID="${RECOVERY_MESH_GITHUB_REPOSITORY_ID:-1334014784}"
REPO_OWNER="${REPO%%/*}"
SERVICE="${RECOVERY_MESH_SERVICE:-evidencebound-recovery-mesh}"
RUN_REGION="${GOOGLE_CLOUD_RUN_REGION:-europe-west1}"
VERTEX_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
MODEL="${RECOVERY_MESH_MODEL:-gemini-3.5-flash}"
RUNTIME_SA_NAME="${RECOVERY_MESH_RUNTIME_SA:-recovery-mesh-runtime}"
BUILD_SA_NAME="${RECOVERY_MESH_BUILD_SA:-recovery-mesh-build}"
DEPLOYER_SA_NAME="${RECOVERY_MESH_DEPLOYER_SA:-recovery-mesh-deployer}"
JUDGE_SECRET_NAME="${RECOVERY_MESH_JUDGE_SECRET_NAME:-recovery-mesh-judge-key}"
JUDGE_SECRET_VERSION="${RECOVERY_MESH_JUDGE_SECRET_VERSION:-1}"
POOL_ID="${RECOVERY_MESH_WIF_POOL:-github-actions}"
PROVIDER_ID="${RECOVERY_MESH_WIF_PROVIDER:-recovery-mesh}"
IAM_WAIT_SECONDS="${RECOVERY_MESH_IAM_PROPAGATION_WAIT_SECONDS:-30}"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_NUMBER="${RECOVERY_MESH_EXPECTED_PROJECT_NUMBER:-457699623691}"
EXPECTED_HACKATHON_LABEL="${RECOVERY_MESH_EXPECTED_HACKATHON_LABEL:-all-things-agentic-2026}"

command -v gcloud >/dev/null || { echo "BLOCKER=gcloud CLI not installed" >&2; exit 2; }
command -v python3 >/dev/null || { echo "BLOCKER=python3 not installed" >&2; exit 2; }

ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
[ -n "$ACCOUNT" ] || { echo "BLOCKER=no active gcloud account" >&2; exit 3; }

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT to the explicit hackathon Google Cloud project ID}"
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"

# Fail closed before any API/IAM mutation if Cloud Shell is pointed at an unexpected project.
[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: got $PROJECT_ID expected $EXPECTED_PROJECT_ID" >&2
  exit 4
}

PROJECT_STATE="$(gcloud projects describe "$PROJECT_ID" --format='value(lifecycleState)')"
[ "$PROJECT_STATE" = "ACTIVE" ] || { echo "BLOCKER=project is not ACTIVE: $PROJECT_STATE" >&2; exit 5; }

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
[ "$PROJECT_NUMBER" = "$EXPECTED_PROJECT_NUMBER" ] || {
  echo "BLOCKER=unexpected project number: got $PROJECT_NUMBER expected $EXPECTED_PROJECT_NUMBER" >&2
  exit 6
}

PROJECT_HACKATHON_LABEL="$(gcloud projects describe "$PROJECT_ID" --format='value(labels.hackathon)')"
[ "$PROJECT_HACKATHON_LABEL" = "$EXPECTED_HACKATHON_LABEL" ] || {
  echo "BLOCKER=unexpected/missing hackathon label: got ${PROJECT_HACKATHON_LABEL:-<empty>} expected $EXPECTED_HACKATHON_LABEL" >&2
  exit 7
}

# Billing is a hard production prerequisite. Check it before enabling APIs or creating IAM.
BILLING_ENABLED="$(
  gcloud billing projects describe "$PROJECT_ID" --format='value(billingEnabled)' 2>/dev/null \
    | tr '[:upper:]' '[:lower:]'
)"
[ "$BILLING_ENABLED" = "true" ] || {
  echo "BLOCKER=billing is not enabled for $PROJECT_ID" >&2
  exit 8
}

gcloud config set project "$PROJECT_ID" >/dev/null
RUNTIME_SA="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_SA="${BUILD_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
DEPLOYER_SA="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

printf 'OWNER_ACCOUNT=%s\n' "$ACCOUNT"
printf 'GCP_PROJECT=%s\n' "$PROJECT_ID"
printf 'PROJECT_NUMBER=%s\n' "$PROJECT_NUMBER"
printf 'PROJECT_HACKATHON_LABEL=%s\n' "$PROJECT_HACKATHON_LABEL"
printf 'BILLING_ENABLED=true\n'
printf 'RUN_REGION=%s\n' "$RUN_REGION"
printf 'VERTEX_LOCATION=%s\n' "$VERTEX_LOCATION"
printf 'MODEL=%s\n' "$MODEL"

# API enablement is a one-time owner/bootstrap responsibility. Runtime and CI identities do
# not receive Service Usage Admin.
gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  serviceusage.googleapis.com \
  secretmanager.googleapis.com \
  --project "$PROJECT_ID"

ensure_service_account() {
  local name="$1"
  local email="$2"
  local display_name="$3"
  if ! gcloud iam service-accounts describe "$email" --project "$PROJECT_ID" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$name" \
      --project "$PROJECT_ID" \
      --display-name "$display_name"
  fi
}

ensure_service_account "$RUNTIME_SA_NAME" "$RUNTIME_SA" "EvidenceBound Recovery Mesh runtime"
ensure_service_account "$BUILD_SA_NAME" "$BUILD_SA" "EvidenceBound Recovery Mesh build"

# Runtime identity: Gemini/Vertex invocation only at project scope.
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${RUNTIME_SA}" \
  --role roles/aiplatform.user \
  --condition=None \
  --quiet >/dev/null

# User-specified build identity: Cloud Run source build only. This avoids relying on a broad
# default Compute Engine service account.
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${BUILD_SA}" \
  --role roles/run.builder \
  --condition=None \
  --quiet >/dev/null

# Generate the judge API key exactly once and keep it in Secret Manager. Never print the value.
if ! gcloud secrets describe "$JUDGE_SECRET_NAME" --project "$PROJECT_ID" >/dev/null 2>&1; then
  JUDGE_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  printf '%s' "$JUDGE_KEY" | gcloud secrets create "$JUDGE_SECRET_NAME" \
    --project "$PROJECT_ID" \
    --data-file=- \
    --replication-policy=automatic \
    --labels=app=evidencebound-recovery-mesh,hackathon=all-things-agentic-2026 \
    >/dev/null
  unset JUDGE_KEY
fi

JUDGE_SECRET_STATE="$(
  gcloud secrets versions describe "$JUDGE_SECRET_VERSION" \
    --secret "$JUDGE_SECRET_NAME" \
    --project "$PROJECT_ID" \
    --format='value(state)' 2>/dev/null || true
)"
[ "$JUDGE_SECRET_STATE" = "ENABLED" ] || {
  echo "BLOCKER=judge secret version ${JUDGE_SECRET_VERSION} is not ENABLED" >&2
  exit 9
}

gcloud secrets add-iam-policy-binding "$JUDGE_SECRET_NAME" \
  --project "$PROJECT_ID" \
  --member "serviceAccount:${RUNTIME_SA}" \
  --role roles/secretmanager.secretAccessor \
  --condition=None \
  --quiet >/dev/null

# First-deployment smoke receives the secret through this process environment only. The value
# is neither printed nor committed; Cloud Run itself references the same Secret Manager version.
export RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE="$(
  gcloud secrets versions access "$JUDGE_SECRET_VERSION" \
    --secret "$JUDGE_SECRET_NAME" \
    --project "$PROJECT_ID"
)"
export RECOVERY_MESH_JUDGE_SECRET_NAME="$JUDGE_SECRET_NAME"
export RECOVERY_MESH_JUDGE_SECRET_VERSION="$JUDGE_SECRET_VERSION"

export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
export GOOGLE_CLOUD_RUN_REGION="$RUN_REGION"
export GOOGLE_CLOUD_LOCATION="$VERTEX_LOCATION"
export RECOVERY_MESH_MODEL="$MODEL"
export RECOVERY_MESH_SERVICE="$SERVICE"
export RECOVERY_MESH_BUILD_SA="$BUILD_SA_NAME"

"$(dirname "$0")/gcp-live-preflight.sh"

# Cloud Run/Cloud Build IAM changes can take time to propagate. Keep the wait bounded and
# configurable instead of hiding repeated deployment retries.
if [ "$IAM_WAIT_SECONDS" -gt 0 ]; then
  printf 'IAM_PROPAGATION_WAIT_SECONDS=%s\n' "$IAM_WAIT_SECONDS"
  sleep "$IAM_WAIT_SECONDS"
fi

# Public GET access is an owner-only first-deployment action. State-changing/run APIs remain
# protected by the application-level judge key stored in Secret Manager.
export RECOVERY_MESH_PUBLIC_BOOTSTRAP=1
"$(dirname "$0")/deploy-cloud-run.sh"
unset RECOVERY_MESH_PUBLIC_BOOTSTRAP RECOVERY_MESH_JUDGE_KEY_FOR_SMOKE

# Establish keyless GitHub -> Google Cloud deployment auth after the first live deployment.
ensure_service_account "$DEPLOYER_SA_NAME" "$DEPLOYER_SA" "EvidenceBound Recovery Mesh GitHub deployer"

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

# The CI deployer may attach only the two bounded service identities it needs: runtime and build.
for TARGET_SA in "$RUNTIME_SA" "$BUILD_SA"; do
  gcloud iam service-accounts add-iam-policy-binding "$TARGET_SA" \
    --project "$PROJECT_ID" \
    --member "serviceAccount:${DEPLOYER_SA}" \
    --role roles/iam.serviceAccountUser \
    --condition=None \
    --quiet >/dev/null
done

# Keyless deploy CI may read only the dedicated judge secret so it can execute the protected
# production smoke test after deployment.
gcloud secrets add-iam-policy-binding "$JUDGE_SECRET_NAME" \
  --project "$PROJECT_ID" \
  --member "serviceAccount:${DEPLOYER_SA}" \
  --role roles/secretmanager.secretAccessor \
  --condition=None \
  --quiet >/dev/null

if ! gcloud iam workload-identity-pools describe "$POOL_ID" \
  --project "$PROJECT_ID" --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --display-name "GitHub Actions" \
    --description "Keyless GitHub Actions identities for hackathon deployments"
fi

if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --project "$PROJECT_ID" \
    --location=global \
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
  --condition=None \
  --quiet >/dev/null

PROVIDER_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
SERVICE_URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$RUN_REGION" --format='value(status.url)')"
REVISION="$(gcloud run services describe "$SERVICE" --project "$PROJECT_ID" --region "$RUN_REGION" --format='value(status.latestReadyRevisionName)')"

printf 'GCP_OWNER_BOOTSTRAP=PASS\n'
printf 'SERVICE_URL=%s\n' "$SERVICE_URL"
printf 'CLOUD_RUN_REVISION=%s\n' "$REVISION"
printf 'RUNTIME_SERVICE_ACCOUNT=%s\n' "$RUNTIME_SA"
printf 'BUILD_SERVICE_ACCOUNT=%s\n' "$BUILD_SA"
printf 'GITHUB_DEPLOYER_SERVICE_ACCOUNT=%s\n' "$DEPLOYER_SA"
printf 'WORKLOAD_IDENTITY_PROVIDER=%s\n' "$PROVIDER_RESOURCE"
printf 'JUDGE_SECRET_NAME=%s\n' "$JUDGE_SECRET_NAME"
printf 'JUDGE_SECRET_VERSION=%s\n' "$JUDGE_SECRET_VERSION"
printf 'JUDGE_KEY_RETRIEVE_COMMAND=gcloud secrets versions access %s --secret=%s --project=%s\n' "$JUDGE_SECRET_VERSION" "$JUDGE_SECRET_NAME" "$PROJECT_ID"
printf 'GITHUB_REPOSITORY=%s\n' "$REPO"
printf 'GITHUB_REPOSITORY_ID=%s\n' "$REPO_ID"
