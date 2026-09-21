from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from bidscope.api.main import app
from bidscope.application.run_service import RunRepository, RunService
from bidscope.domain.runs import InvalidRunTransition, RunCreate, RunStatus


def make_service() -> RunService:
    return RunService(RunRepository())


def test_run_starts_created_and_records_transitions() -> None:
    service = make_service()
    run = service.create(
        RunCreate(
            project_id=uuid4(),
            task_type="document_review",
            goal="检查文档完整性",
            requested_by="user-001",
        )
    )

    assert run.status is RunStatus.CREATED
    updated = service.transition(run.id, RunStatus.VALIDATING)

    assert updated.status is RunStatus.VALIDATING
    assert updated.version == 1
    assert len(list(service.events(run.id))) == 1


def test_run_cannot_skip_governed_steps() -> None:
    service = make_service()
    run = service.create(
        RunCreate(
            project_id=uuid4(),
            task_type="document_review",
            goal="检查文档完整性",
            requested_by="user-001",
        )
    )

    with pytest.raises(InvalidRunTransition):
        service.transition(run.id, RunStatus.COMPLETED)


def test_http_contract_creates_and_reads_a_run() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/runs",
        json={
            "project_id": str(uuid4()),
            "task_type": "document_review",
            "goal": "检查文档完整性",
            "requested_by": "user-001",
        },
    )

    assert response.status_code == 202
    run_id = response.json()["id"]
    assert client.get(f"/api/v1/runs/{run_id}").status_code == 200
    assert client.get(f"/api/v1/runs/{run_id}/events").json() == []
