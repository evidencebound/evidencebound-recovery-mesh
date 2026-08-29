from pathlib import Path


def test_video_v2_capture_is_continuous_and_hands_off_after_unlock() -> None:
    workflow = Path(".github/workflows/judge-video-capture.yml").read_text(
        encoding="utf-8"
    )

    assert "recordVideo" in workflow
    assert "?autorun=stale_evidence&recover=1" in workflow
    assert "video-v2-live-segment.webm" in workflow
    assert "#saveJudgeKey" in workflow
    assert "#startRun').click" not in workflow
    assert "#recover').click" not in workflow
    assert "button[data-fault=\"stale_evidence\"]').click" not in workflow


def test_video_v2_capture_publishes_machine_readable_receipt() -> None:
    workflow = Path(".github/workflows/judge-video-capture.yml").read_text(
        encoding="utf-8"
    )

    assert "statuses: write" in workflow
    assert "recovery-mesh/video-v2-capture" in workflow
    assert "actions/runs/${{ github.run_id }}" in workflow
