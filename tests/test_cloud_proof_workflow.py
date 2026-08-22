from pathlib import Path


def test_cloud_proof_runs_non_executable_script_through_bash() -> None:
    workflow = Path(".github/workflows/gcp-live-acceptance.yml").read_text(
        encoding="utf-8"
    )

    assert "run: bash ./scripts/gcp-proof-receipt.sh" in workflow
