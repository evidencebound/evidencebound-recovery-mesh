from pathlib import Path


def test_live_smoke_proves_firestore_absence_exactly_once_and_rehydration() -> None:
    smoke = Path("scripts/smoke-cloud-run.sh").read_text(encoding="utf-8")

    assert 'persistence["provider"]=="firestore"' in smoke
    assert 'persistence["durable"] is True' in smoke
    assert '"${URL}/api/durable-runs/${RUN_ID}"' in smoke
    assert "DURABLE_BASELINE=PASS" in smoke
    assert "DURABLE_BLOCKED=PASS" in smoke
    assert "DURABLE_RECOVERY=PASS" in smoke
    assert "firestore.googleapis.com/v1/projects/${GOOGLE_CLOUD_PROJECT}" in smoke
    assert "recovery_mesh_action_receipts" in smoke
    assert "FIRESTORE_BLOCKED_RECEIPT_COUNT=PASS count=0" in smoke
    assert "FIRESTORE_RECOVERED_RECEIPT_COUNT=PASS count=1" in smoke


def test_live_acceptance_propagates_same_run_id_to_cloud_proof() -> None:
    workflow = Path(".github/workflows/gcp-live-acceptance.yml").read_text(encoding="utf-8")

    assert "run_id: ${{ steps.acceptance.outputs.run_id }}" in workflow
    assert 'printf \'run_id=%s\\n\' "$RUN_ID" >> "$GITHUB_OUTPUT"' in workflow
    assert "RECOVERY_MESH_PROOF_RUN_ID: ${{ needs.live-judge-flow.outputs.run_id }}" in workflow


def test_cloud_proof_filters_causal_events_to_exact_acceptance_run() -> None:
    proof = Path("scripts/gcp-proof-receipt.sh").read_text(encoding="utf-8")

    assert "RECOVERY_MESH_PROOF_RUN_ID" in proof
    assert "jsonPayload.run_id" in proof
    assert '"$PROOF_RUN_ID"' in proof
    assert "recovery_mesh_flight_recorder" in proof
    assert "TRUST_BREAK_DETECTED" in proof
    assert "ACTION_BLOCKED" in proof
    assert "CHECKPOINT_REUSED" in proof
    assert "RECOVERY_COMPLETED" in proof
    assert "EXACT_RUN_CLOUD_LOGGING=PASS" in proof
