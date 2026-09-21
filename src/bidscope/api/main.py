from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, HTTPException, status

from bidscope.application.run_service import RunNotFound, RunRepository, RunService
from bidscope.domain.runs import Run, RunCreate, RunEvent, RunStatus

app = FastAPI(title="BidScope API", version="0.1.0")
run_service = RunService(RunRepository())


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "bidscope-api"}


@app.post("/api/v1/runs", response_model=Run, status_code=status.HTTP_202_ACCEPTED, tags=["runs"])
async def create_run(payload: RunCreate) -> Run:
    return run_service.create(payload)


@app.get("/api/v1/runs/{run_id}", response_model=Run, tags=["runs"])
async def get_run(run_id: UUID) -> Run:
    try:
        return run_service.get(run_id)
    except RunNotFound as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc


@app.get("/api/v1/runs/{run_id}/events", response_model=list[RunEvent], tags=["runs"])
async def get_run_events(run_id: UUID) -> list[RunEvent]:
    try:
        return list(run_service.events(run_id))
    except RunNotFound as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc


@app.post("/api/v1/runs/{run_id}/transition/{target}", response_model=Run, tags=["internal"])
async def transition_run(run_id: UUID, target: RunStatus) -> Run:
    """Temporary control-plane endpoint; protect it before exposing a worker API."""
    try:
        return run_service.transition(run_id, target)
    except RunNotFound as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
