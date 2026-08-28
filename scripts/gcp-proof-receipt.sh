#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_NUMBER="${RECOVERY_MESH_EXPECTED_PROJECT_NUMBER:-457699623691}"
RUN_REGION="${GOOGLE_CLOUD_RUN_REGION:-europe-west1}"
SERVICE="${RECOVERY_MESH_SERVICE:-evidencebound-recovery-mesh}"
PROOF_RUN_ID="${RECOVERY_MESH_PROOF_RUN_ID:-}"
LOG_ATTEMPTS="${RECOVERY_MESH_LOG_PROOF_ATTEMPTS:-8}"
LOG_SLEEP_SECONDS="${RECOVERY_MESH_LOG_PROOF_SLEEP_SECONDS:-8}"

command -v gcloud >/dev/null || { echo "BLOCKER=gcloud CLI not installed" >&2; exit 2; }
command -v curl >/dev/null || { echo "BLOCKER=curl not installed" >&2; exit 2; }

[ "$PROJECT_ID" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: got $PROJECT_ID expected $EXPECTED_PROJECT_ID" >&2
  exit 3
}
[ -n "$PROOF_RUN_ID" ] || {
  echo "BLOCKER=RECOVERY_MESH_PROOF_RUN_ID is required for exact-run Cloud Logging proof" >&2
  exit 4
}
[[ "$PROOF_RUN_ID" =~ ^run-[a-zA-Z0-9_-]+$ ]] || {
  echo "BLOCKER=invalid proof run id: $PROOF_RUN_ID" >&2
  exit 5
}
[[ "$LOG_ATTEMPTS" =~ ^[1-9][0-9]*$ ]] || {
  echo "BLOCKER=RECOVERY_MESH_LOG_PROOF_ATTEMPTS must be positive" >&2
  exit 6
}
[[ "$LOG_SLEEP_SECONDS" =~ ^[0-9]+$ ]] || {
  echo "BLOCKER=RECOVERY_MESH_LOG_PROOF_SLEEP_SECONDS must be non-negative" >&2
  exit 7
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
printf 'PROOF_RUN_ID=%s\n' "$PROOF_RUN_ID"

printf '\n=== LIVE HEALTH ===\n'
curl --fail --silent --show-error "${SERVICE_URL}/health" | python -m json.tool

printf '\n=== EXACT ACCEPTANCE RUN CLOUD LOGGING ===\n'
printf -v RUN_FILTER 'jsonPayload.run_id="%s"' "$PROOF_RUN_ID"
printf -v TEXT_FILTER 'textPayload:"%s"' "$PROOF_RUN_ID"
LOG_FILTER="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${SERVICE}\" AND (${RUN_FILTER} OR ${TEXT_FILTER})"
LOGS_OK=0
for ATTEMPT in $(seq 1 "$LOG_ATTEMPTS"); do
  gcloud logging read "$LOG_FILTER" \
    --project "$PROJECT_ID" \
    --freshness=2h \
    --limit=200 \
    --order=asc \
    --format=json > /tmp/recovery-mesh-exact-run-logs.json || true

  if python3 - /tmp/recovery-mesh-exact-run-logs.json "$PROOF_RUN_ID" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
run_id = sys.argv[2]
entries = json.loads(path.read_text(encoding="utf-8") or "[]")
required = {
    "TRUST_BREAK_DETECTED",
    "ACTION_BLOCKED",
    "CHECKPOINT_REUSED",
    "RECOVERY_COMPLETED",
}
events = []
for entry in entries:
    if not isinstance(entry, dict):
        continue
    payload = entry.get("jsonPayload")
    if not isinstance(payload, dict):
        text = entry.get("textPayload")
        if isinstance(text, str):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
            payload = parsed if isinstance(parsed, dict) else None
    if not isinstance(payload, dict):
        continue
    if payload.get("component") != "recovery_mesh_flight_recorder":
        continue
    if payload.get("run_id") != run_id:
        continue
    event_type = payload.get("event_type")
    if isinstance(event_type, str):
        events.append(event_type)

seen = set(events)
missing = sorted(required - seen)
if missing:
    print(f"EXACT_RUN_CLOUD_LOGGING_WAIT missing={','.join(missing)}")
    raise SystemExit(1)
print("EXACT_RUN_CLOUD_LOGGING=PASS run_id={} events={}".format(run_id, ",".join(events)))
PY
  then
    LOGS_OK=1
    break
  fi
  if [ "$ATTEMPT" -lt "$LOG_ATTEMPTS" ]; then
    sleep "$LOG_SLEEP_SECONDS"
  fi
done
[ "$LOGS_OK" = "1" ] || {
  echo "BLOCKER=exact-run Cloud Logging did not contain the complete causal recovery sequence" >&2
  exit 8
}

printf '\n=== EXACT RUN LOG EXCERPT ===\n'
gcloud logging read "$LOG_FILTER" \
  --project "$PROJECT_ID" \
  --freshness=2h \
  --limit=40 \
  --order=asc \
  --format='table(timestamp,jsonPayload.event_id,jsonPayload.event_type,jsonPayload.checkpoint_id,jsonPayload.message)' \
  || true

printf '\nGCP_PROOF_RECEIPT=PASS\n'
