#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
MODE="${RECOVERY_MESH_FIRESTORE_BOOTSTRAP_MODE:-verify}"
FIRESTORE_LOCATION="${RECOVERY_MESH_FIRESTORE_LOCATION:-${GOOGLE_CLOUD_RUN_REGION:-europe-west1}}"
DATABASE_ID="${RECOVERY_MESH_FIRESTORE_DATABASE:-'(default)'}"
RUNTIME_SA_NAME="${RECOVERY_MESH_RUNTIME_SA:-recovery-mesh-runtime}"
DEPLOYER_SA_NAME="${RECOVERY_MESH_DEPLOYER_SA:-recovery-mesh-deployer}"
RUNTIME_SA="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
DEPLOYER_SA="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"

command -v gcloud >/dev/null || {
  echo "BLOCKER=gcloud CLI not installed" >&2
  exit 2
}
[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: $PROJECT_ID" >&2
  exit 3
}
case "$MODE" in
  provision|verify) ;;
  *)
    echo "BLOCKER=RECOVERY_MESH_FIRESTORE_BOOTSTRAP_MODE must be provision or verify" >&2
    exit 4
    ;;
esac

if [ "$MODE" = "provision" ]; then
  # One-time owner/bootstrap path. Normal GitHub deploys never receive Service Usage Admin,
  # Datastore Owner, or project IAM mutation permissions.
  gcloud services enable firestore.googleapis.com --project "$PROJECT_ID"

  if ! gcloud firestore databases describe \
    --database "$DATABASE_ID" \
    --project "$PROJECT_ID" >/dev/null 2>&1; then
    gcloud firestore databases create \
      --database="$DATABASE_ID" \
      --location="$FIRESTORE_LOCATION" \
      --edition=standard \
      --type=firestore-native \
      --project "$PROJECT_ID" \
      --quiet
  fi

  # Runtime gets only the data-plane role required by Recovery Mesh persistence.
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:${RUNTIME_SA}" \
    --role roles/datastore.user \
    --condition=None \
    --quiet >/dev/null

  # GitHub deployer gets metadata read only so ordinary deploys can verify the database
  # before enabling Firestore mode. It cannot create databases or mutate Firestore data.
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:${DEPLOYER_SA}" \
    --role roles/datastore.viewer \
    --condition=None \
    --quiet >/dev/null
fi

# Both paths finish by reading the authoritative database. In normal deploy mode this is
# deliberately read-only and fails closed if the one-time owner bootstrap was not completed.
if ! DATABASE_JSON="$(gcloud firestore databases describe \
  --database "$DATABASE_ID" \
  --project "$PROJECT_ID" \
  --format=json 2>/dev/null)"; then
  cat >&2 <<EOF
BLOCKER=Firestore default database is unavailable or current deploy identity lacks metadata read access.
OWNER_ACTION=Run RECOVERY_MESH_FIRESTORE_BOOTSTRAP_MODE=provision GOOGLE_CLOUD_PROJECT=${PROJECT_ID} GOOGLE_CLOUD_RUN_REGION=${FIRESTORE_LOCATION} ./scripts/gcp-firestore-bootstrap.sh with the project owner/admin account, then rerun deployment.
EOF
  exit 5
fi

python3 - "$DATABASE_JSON" "$DATABASE_ID" "$FIRESTORE_LOCATION" <<'PY'
import json
import sys

data = json.loads(sys.argv[1])
expected_id = sys.argv[2]
expected_location = sys.argv[3]
name = str(data.get("name", ""))
location = str(data.get("locationId", ""))
database_type = str(data.get("type", ""))
edition = str(data.get("edition", ""))

if not name.endswith(f"/databases/{expected_id}"):
    raise SystemExit(f"BLOCKER=unexpected Firestore database resource: {name}")
if location and location != expected_location:
    raise SystemExit(
        f"BLOCKER=Firestore location mismatch: got {location} expected {expected_location}"
    )
if database_type and database_type not in {"FIRESTORE_NATIVE", "firestore-native"}:
    raise SystemExit(f"BLOCKER=unexpected Firestore database type: {database_type}")
if edition and edition not in {"STANDARD", "standard"}:
    raise SystemExit(f"BLOCKER=unexpected Firestore edition: {edition}")
print(f"FIRESTORE_DATABASE_RESOURCE={name}")
print(f"FIRESTORE_DATABASE_LOCATION={location or expected_location}")
PY

printf 'FIRESTORE_DATABASE=READY\n'
printf 'FIRESTORE_RUNTIME_SERVICE_ACCOUNT=%s\n' "$RUNTIME_SA"
printf 'FIRESTORE_DEPLOYER_SERVICE_ACCOUNT=%s\n' "$DEPLOYER_SA"
if [ "$MODE" = "provision" ]; then
  printf 'FIRESTORE_RUNTIME_IAM=READY\n'
  printf 'FIRESTORE_DEPLOYER_IAM=READ_ONLY_READY\n'
else
  printf 'FIRESTORE_RUNTIME_IAM=DEFERRED_TO_LIVE_DATA_PLANE_CHECK\n'
  printf 'FIRESTORE_DEPLOYER_IAM=READ_ONLY_VERIFIED\n'
fi
printf 'FIRESTORE_BOOTSTRAP_MODE=%s\n' "$MODE"
