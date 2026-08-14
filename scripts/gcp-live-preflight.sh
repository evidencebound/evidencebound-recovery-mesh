#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT to the existing hackathon Google Cloud project ID}"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
MODEL="${RECOVERY_MESH_MODEL:-gemini-3.5-flash}"

command -v gcloud >/dev/null || { echo "BLOCKER=gcloud CLI not installed" >&2; exit 2; }
command -v curl >/dev/null || { echo "BLOCKER=curl not installed" >&2; exit 2; }

[ "$GOOGLE_CLOUD_PROJECT" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected project id: got $GOOGLE_CLOUD_PROJECT expected $EXPECTED_PROJECT_ID" >&2
  exit 3
}

ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
[ -n "$ACCOUNT" ] || { echo "BLOCKER=no active gcloud account" >&2; exit 4; }

gcloud config set project "$GOOGLE_CLOUD_PROJECT" >/dev/null
[ "$(gcloud config get-value project 2>/dev/null)" = "$GOOGLE_CLOUD_PROJECT" ] || {
  echo "BLOCKER=gcloud project target mismatch" >&2
  exit 5
}

# Service Usage and the live Vertex call below are sufficient operational liveness checks.
# Avoid gcloud projects describe here: it adds a Cloud Resource Manager API dependency that
# is not required for the Cloud Run source-deploy path.
ENABLED="$(gcloud services list --enabled --project "$GOOGLE_CLOUD_PROJECT" \
  --filter='config.name:aiplatform.googleapis.com' --format='value(config.name)')"
[ "$ENABLED" = "aiplatform.googleapis.com" ] || {
  echo "BLOCKER=aiplatform.googleapis.com is not enabled; run first-time owner bootstrap" >&2
  exit 6
}

echo "GCP_ACCOUNT=$ACCOUNT"
echo "GCP_PROJECT=$GOOGLE_CLOUD_PROJECT"
echo "VERTEX_LOCATION=$LOCATION"
echo "MODEL=$MODEL"

# Smallest live model check before a deployment/revision. No fallback is permitted.
# Gemini 3.5 Flash thinks by default. Keep this trivial probe at minimal thinking and leave
# enough output budget for the visible answer so reasoning tokens cannot consume the entire cap.
ACCESS_TOKEN="$(gcloud auth print-access-token)"
REQUEST='{"contents":[{"role":"user","parts":[{"text":"Return exactly the word READY."}]}],"generationConfig":{"maxOutputTokens":32,"thinkingConfig":{"thinkingLevel":"minimal"}}}'
RESPONSE="$(curl --fail-with-body --silent --show-error \
  -X POST \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  "https://aiplatform.googleapis.com/v1/projects/${GOOGLE_CLOUD_PROJECT}/locations/${LOCATION}/publishers/google/models/${MODEL}:generateContent" \
  -d "$REQUEST")"

printf '%s' "$RESPONSE" | python -c '
import json,sys
x=json.load(sys.stdin)
text="".join(
    p.get("text", "")
    for c in x.get("candidates", [])
    for p in c.get("content", {}).get("parts", [])
).strip()
assert text == "READY", {"text": text, "response": x}
print("VERTEX_GEMINI_LIVE=PASS response=READY")
usage=x.get("usageMetadata", {})
if usage:
    print("VERTEX_USAGE=" + json.dumps(usage, sort_keys=True, separators=(",",":")))
'
