from __future__ import annotations

import os
import secrets
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .execution import AgentExecutionError, ExecutionUnavailable, executor_from_environment
from .runtime import DemoRun, UnsupportedScenario

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
_JUDGE_KEY_HEADER = "X-Recovery-Mesh-Judge-Key"
_LIVE_MODES = {"google", "google_adk", "vertex", "vertex_adk"}

app = FastAPI(title="EvidenceBound Recovery Mesh", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_runs: dict[str, DemoRun] = {}
_lock = Lock()


def _judge_access_required() -> bool:
    expected = os.getenv("RECOVERY_MESH_JUDGE_KEY", "").strip()
    mode = os.getenv("RECOVERY_MESH_EXECUTION_MODE", "deterministic").strip().lower()
    return bool(expected) or mode in _LIVE_MODES


def _require_judge_access(
    supplied_key: str | None = Header(default=None, alias=_JUDGE_KEY_HEADER),
) -> None:
    expected = os.getenv("RECOVERY_MESH_JUDGE_KEY", "").strip()
    mode = os.getenv("RECOVERY_MESH_EXECUTION_MODE", "deterministic").strip().lower()
    if not expected:
        if mode in _LIVE_MODES:
            raise HTTPException(
                status_code=503,
                detail="judge access key is not configured; live action endpoints fail closed",
            )
        return
    if supplied_key is None or not secrets.compare_digest(supplied_key, expected):
        raise HTTPException(status_code=401, detail="valid judge access key required")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, object]:
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
        "judge_access_required": _judge_access_required(),
        "judge_key_header": _JUDGE_KEY_HEADER,
    }


@app.post("/api/runs", dependencies=[Depends(_require_judge_access)])
def create_run() -> dict[str, object]:
    try:
        run = DemoRun()
    except (ExecutionUnavailable, AgentExecutionError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    with _lock:
        _runs[run.run_id] = run
    return run.snapshot()


@app.get("/api/runs/{run_id}", dependencies=[Depends(_require_judge_access)])
def get_run(run_id: str) -> dict[str, object]:
    return _get_run(run_id).snapshot()


@app.post(
    "/api/runs/{run_id}/fault/{scenario}",
    dependencies=[Depends(_require_judge_access)],
)
def inject_fault(run_id: str, scenario: str) -> dict[str, object]:
    run = _get_run(run_id)
    try:
        run.inject_fault(scenario)
    except UnsupportedScenario as exc:
        raise HTTPException(status_code=400, detail=f"unsupported scenario: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return run.snapshot()


@app.post("/api/runs/{run_id}/recover", dependencies=[Depends(_require_judge_access)])
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
