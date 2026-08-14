#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_NUMBER="${RECOVERY_MESH_EXPECTED_PROJECT_NUMBER:-457699623691}"
POOL_ID="${RECOVERY_MESH_AUDIT_WIF_POOL:-github-actions}"
PROVIDER_ID="${RECOVERY_MESH_AUDIT_WIF_PROVIDER:-recovery-mesh-audit}"
AUDITOR_SA_NAME="${RECOVERY_MESH_AUDITOR_SA:-recovery-mesh-auditor}"
AUDITOR_SA="${AUDITOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
REPO="${RECOVERY_MESH_GITHUB_REPOSITORY:-moneyparking/evidencebound-recovery-mesh}"
REPO_ID="${RECOVERY_MESH_GITHUB_REPOSITORY_ID:-1334014784}"
REPO_OWNER="${REPO%%/*}"

[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: $PROJECT_ID" >&2
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

printf 'AUDIT_WIF_BOOTSTRAP_MODE=IAM_ONLY\n'
printf 'ACTIVE_ACCOUNT=%s\n' "$ACTIVE_ACCOUNT"
printf 'PROJECT_ID=%s\n' "$PROJECT_ID"
printf 'PROJECT_NUMBER=%s\n' "$PROJECT_NUMBER"

if ! gcloud iam service-accounts describe "$AUDITOR_SA" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$AUDITOR_SA_NAME" \
    --project "$PROJECT_ID" \
    --display-name "EvidenceBound Recovery Mesh read-only auditor"
fi

# Least-privilege project reads required by the audit workflow:
# Cloud Run service/revision metadata, Policy Denied logs, effective org policy,
# project ancestry, and API quota attribution for gcloud reads.
for ROLE in \
  roles/run.viewer \
  roles/logging.viewer \
  roles/orgpolicy.policyViewer \
  roles/browser \
  roles/serviceusage.serviceUsageConsumer; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:${AUDITOR_SA}" \
    --role "$ROLE" \
    --condition=None \
    --quiet >/dev/null
done

if ! gcloud iam workload-identity-pools describe "$POOL_ID" \
  --project "$PROJECT_ID" \
  --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --display-name "GitHub Actions" \
    --description "Keyless GitHub Actions identities for EvidenceBound Recovery Mesh"
fi

POOL_STATE="$(gcloud iam workload-identity-pools describe "$POOL_ID" \
  --project "$PROJECT_ID" \
  --location=global \
  --format='value(state)' 2>/dev/null || true)"
[ "$POOL_STATE" != "DELETED" ] || {
  echo "BLOCKER=workload identity pool is deleted; restore it deliberately before audit" >&2
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
    --display-name "Recovery Mesh audit" \
    --issuer-uri="https://token.actions.githubusercontent.com/" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_id=assertion.repository_id,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository_id=='${REPO_ID}' && assertion.repository_owner=='${REPO_OWNER}' && assertion.ref=='refs/heads/main'"
fi

PROVIDER_STATE="$(gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" \
  --location=global \
  --workload-identity-pool="$POOL_ID" \
  --format='value(state)' 2>/dev/null || true)"
[ "$PROVIDER_STATE" = "ACTIVE" ] || {
  echo "BLOCKER=audit workload identity provider is not ACTIVE: ${PROVIDER_STATE:-UNKNOWN}" >&2
  exit 6
}

WIF_MEMBER="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository_id/${REPO_ID}"
gcloud iam service-accounts add-iam-policy-binding "$AUDITOR_SA" \
  --project "$PROJECT_ID" \
  --member "$WIF_MEMBER" \
  --role roles/iam.workloadIdentityUser \
  --condition=None \
  --quiet >/dev/null

PROVIDER_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
printf 'AUDIT_WIF_BOOTSTRAP=PASS\n'
printf 'AUDITOR_SERVICE_ACCOUNT=%s\n' "$AUDITOR_SA"
printf 'AUDIT_WORKLOAD_IDENTITY_PROVIDER=%s\n' "$PROVIDER_RESOURCE"
printf 'CLOUD_RUN_MUTATIONS=NONE\n'
printf 'BUILD_OR_DEPLOY=NONE\n'
