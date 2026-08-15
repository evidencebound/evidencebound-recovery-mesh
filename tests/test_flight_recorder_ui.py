from pathlib import Path


def test_flight_recorder_uses_cloud_run_safe_health_path() -> None:
    app_js = Path("static/app.js").read_text(encoding="utf-8")
    assert "fetch('/health')" in app_js
    assert "/healthz" not in app_js


def test_judge_autorun_retries_after_key_is_stored() -> None:
    app_js = Path("static/app.js").read_text(encoding="utf-8")
    assert "pendingAutorun" in app_js
    assert "await runAutorun();" in app_js
    assert "state.pendingAutorun = {scenario, recover:" in app_js


def test_live_benchmark_exposes_exact_token_counts() -> None:
    app_js = Path("static/app.js").read_text(encoding="utf-8")
    assert "Full restart input tokens" in app_js
    assert "Selective input tokens" in app_js
    assert "Input tokens saved" in app_js


def test_recovered_graph_keeps_causal_break_and_reuse_visible() -> None:
    app_js = Path("static/app.js").read_text(encoding="utf-8")
    judge_css = Path("static/judge.css").read_text(encoding="utf-8")
    assert "TRUST BREAK" in app_js
    assert "REUSED" in app_js
    assert "historical-break" in app_js
    assert ".node.historical-break" in judge_css
