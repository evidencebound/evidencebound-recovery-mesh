from pathlib import Path


def test_live_acceptance_proves_staged_ui_and_publishes_machine_readable_status() -> None:
    workflow = Path(".github/workflows/gcp-live-acceptance.yml").read_text(
        encoding="utf-8"
    )

    assert "statuses: write" in workflow
    assert "AUTORUN_STAGE_HOLDS_MS" in workflow
    assert "holdAutorunStage('incident')" in workflow
    assert "recovery-mesh/live-acceptance" in workflow
    assert "actions/runs/${{ github.run_id }}" in workflow
