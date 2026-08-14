#!/usr/bin/env bash
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
BILLING_ACCOUNT="${RECOVERY_MESH_BILLING_ACCOUNT:-014CCF-9ABDCB-526D33}"
DISPLAY_NAME="${RECOVERY_MESH_BUDGET_DISPLAY_NAME:-EvidenceBound Recovery Mesh hackathon}"
BUDGET_AMOUNT="${RECOVERY_MESH_BUDGET_AMOUNT:-5}"
EXPECTED_PROJECT_ID="${RECOVERY_MESH_EXPECTED_PROJECT_ID:-evidencebound-rm-c977c1}"
EXPECTED_PROJECT_NUMBER="${RECOVERY_MESH_EXPECTED_PROJECT_NUMBER:-457699623691}"

command -v gcloud >/dev/null || { echo "BLOCKER=gcloud CLI not installed" >&2; exit 2; }

[ "$GOOGLE_CLOUD_PROJECT" = "$EXPECTED_PROJECT_ID" ] || {
  echo "BLOCKER=unexpected budget project: $GOOGLE_CLOUD_PROJECT" >&2
  exit 3
}
PROJECT_NUMBER="$(gcloud projects describe "$GOOGLE_CLOUD_PROJECT" --format='value(projectNumber)')"
[ "$PROJECT_NUMBER" = "$EXPECTED_PROJECT_NUMBER" ] || {
  echo "BLOCKER=unexpected budget project number: $PROJECT_NUMBER" >&2
  exit 4
}

LINKED_BILLING_ACCOUNT="$(
  gcloud billing projects describe "$GOOGLE_CLOUD_PROJECT" \
    --format='value(billingAccountName)' | sed 's#^billingAccounts/##'
)"
BILLING_ENABLED="$(
  gcloud billing projects describe "$GOOGLE_CLOUD_PROJECT" \
    --format='value(billingEnabled)' | tr '[:upper:]' '[:lower:]'
)"
[ "$BILLING_ENABLED" = "true" ] || {
  echo "BLOCKER=billing is not enabled for $GOOGLE_CLOUD_PROJECT" >&2
  exit 5
}
[ "$LINKED_BILLING_ACCOUNT" = "$BILLING_ACCOUNT" ] || {
  echo "BLOCKER=project is linked to billing account $LINKED_BILLING_ACCOUNT, expected $BILLING_ACCOUNT" >&2
  exit 6
}

# Avoid duplicate budgets on repeated owner/bootstrap sessions. We deliberately do not mutate an
# existing budget because its thresholds/amount may have been changed manually in Cloud Billing.
EXISTING="$(
  gcloud billing budgets list \
    --billing-account "$BILLING_ACCOUNT" \
    --filter="displayName=\"${DISPLAY_NAME}\"" \
    --format='value(name)' \
    --limit=1 2>/dev/null || true
)"
if [ -n "$EXISTING" ]; then
  printf 'BUDGET_ALERT=EXISTS budget=%s\n' "$EXISTING"
  gcloud billing budgets describe "$EXISTING" --billing-account "$BILLING_ACCOUNT"
  exit 0
fi

# Amount is intentionally specified without a currency suffix so Cloud Billing uses the billing
# account currency. This is an alert threshold, not a hard cap or automatic shutdown mechanism.
gcloud billing budgets create \
  --billing-account "$BILLING_ACCOUNT" \
  --display-name "$DISPLAY_NAME" \
  --budget-amount "$BUDGET_AMOUNT" \
  --filter-projects "projects/${GOOGLE_CLOUD_PROJECT}" \
  --calendar-period month \
  --threshold-rule percent=0.50 \
  --threshold-rule percent=0.90 \
  --threshold-rule percent=1.00 \
  --quiet

CREATED="$(
  gcloud billing budgets list \
    --billing-account "$BILLING_ACCOUNT" \
    --filter="displayName=\"${DISPLAY_NAME}\"" \
    --format='value(name)' \
    --limit=1
)"
[ -n "$CREATED" ] || { echo "BLOCKER=budget was not observable after create" >&2; exit 7; }
printf 'BUDGET_ALERT=PASS budget=%s amount_in_billing_account_currency=%s thresholds=50%%,90%%,100%%\n' \
  "$CREATED" "$BUDGET_AMOUNT"
printf 'BUDGET_ALERT_NOTE=alerts_only_not_a_hard_spend_cap\n'
