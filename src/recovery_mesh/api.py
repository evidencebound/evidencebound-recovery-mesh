from __future__ import annotations

from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .execution import AgentExecutionError, ExecutionUnavailable, executor_from_environment
from .runtime import DemoRun, UnsupportedScenario

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"

app = FastAPI(title="EvidenceBound Recovery Mesh", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_runs: dict[str, DemoRun] = {}
_lock = Lock()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz() -> dict[str, object]:
    try:
        executor = executor_from_environment()
        execution = {
            "provider": executor.provider_name,
            "model": executor.model_name,
            "live_google": executor.is_live_google,
        }
    except ExecutionUnavailable as exc:
        execution = {"provider": "unavailable", "error": str(exc), "live_google": False}
    return {
        "status": "ok",
        "service": "evidencebound-recovery-mesh",
        "execution": execution,
    }


@app.post("/api/runs")
def create_run() -> dict[str, object]:
    try:
        run = DemoRun()
    except (ExecutionUnavailable, AgentExecutionError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    with _lock:
        _runs[run.run_id] = run
    return run.snapshot()


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, object]:
    return _get_run(run_id).snapshot()


@app.post("/api/runs/{run_id}/fault/{scenario}")
def inject_fault(run_id: str, scenario: str) -> dict[str, object]:
    run = _get_run(run_id)
    try:
        run.inject_fault(scenario)
    except UnsupportedScenario as exc:
        raise HTTPException(status_code=400, detail=f"unsupported scenario: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return run.snapshot()


@app.post("/api/runs/{run_id}/recover")
def recover(run_id: str) -> dict[str, object]:
    run = _get_run(run_id)
    try:
        run.recover()
    except (ExecutionUnavailable, AgentExecutionError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return run.snapshot()


def _get_run(run_id: str) -> DemoRun:
    with _lock:
        run = _runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run
