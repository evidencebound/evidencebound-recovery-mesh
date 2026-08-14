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

[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: $PROJECT_ID" >&2
  exit 2
}
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
[ "$PROJECT_NUMBER" = "$EXPECTED_PROJECT_NUMBER" ] || {
  echo "BLOCKER=unexpected project number: $PROJECT_NUMBER" >&2
  exit 3
}

printf 'AUDIT_WIF_ROLLBACK_MODE=AUDIT_IDENTITY_ONLY\n'
printf 'PROJECT_ID=%s\n' "$PROJECT_ID"

if gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" \
  --location=global \
  --workload-identity-pool="$POOL_ID" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers delete "$PROVIDER_ID" \
    --project "$PROJECT_ID" \
    --location=global \
    --workload-identity-pool="$POOL_ID" \
    --quiet
fi

if gcloud iam service-accounts describe "$AUDITOR_SA" --project "$PROJECT_ID" >/dev/null 2>&1; then
  for ROLE in \
    roles/run.viewer \
    roles/logging.viewer \
    roles/orgpolicy.policyViewer \
    roles/browser \
    roles/serviceusage.serviceUsageConsumer; do
    gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
      --member "serviceAccount:${AUDITOR_SA}" \
      --role "$ROLE" \
      --condition=None \
      --quiet >/dev/null 2>&1 || true
  done

  gcloud iam service-accounts delete "$AUDITOR_SA" \
    --project "$PROJECT_ID" \
    --quiet
fi

printf 'AUDIT_WIF_ROLLBACK=PASS\n'
printf 'SHARED_WIF_POOL_PRESERVED=%s\n' "$POOL_ID"
printf 'CLOUD_RUN_MUTATIONS=NONE\n'
printf 'BUILD_OR_DEPLOY=NONE\n'
