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


def test_hands_off_autorun_renders_each_live_stage_before_recovery() -> None:
    app_js = Path("static/app.js").read_text(encoding="utf-8")
    baseline_render = "render(run);\n    await holdAutorunStage('baseline');"
    incident_render = "render(run);\n    await holdAutorunStage('incident');"
    recovery_call = "run = await request(`/api/runs/${run.run_id}/recover`, {method:'POST'});"
    assert baseline_render in app_js
    assert incident_render in app_js
    assert app_js.index(baseline_render) < app_js.index(incident_render) < app_js.index(recovery_call)


def test_hands_off_autorun_exposes_recover_query_mode() -> None:
    app_js = Path("static/app.js").read_text(encoding="utf-8")
    assert "const AUTORUN_STAGE_HOLDS_MS" in app_js
    assert "recover: p.get('recover') === '1'" in app_js
    assert "await holdAutorunStage('recovered');" in app_js


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
