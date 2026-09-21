from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class RunStatus(StrEnum):
    CREATED = "created"
    VALIDATING = "validating"
    PLANNING = "planning"
    WAITING_INPUT = "waiting_input"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class InvalidRunTransition(ValueError):
    """Raised when a run attempts to skip a governed lifecycle transition."""


TERMINAL_STATUSES = {
    RunStatus.COMPLETED,
    RunStatus.FAILED,
    RunStatus.CANCELLED,
}


ALLOWED_TRANSITIONS: dict[RunStatus, frozenset[RunStatus]] = {
    RunStatus.CREATED: frozenset({RunStatus.VALIDATING, RunStatus.CANCELLED}),
    RunStatus.VALIDATING: frozenset(
        {RunStatus.PLANNING, RunStatus.WAITING_INPUT, RunStatus.FAILED}
    ),
    RunStatus.PLANNING: frozenset(
        {RunStatus.EXECUTING, RunStatus.WAITING_INPUT, RunStatus.FAILED}
    ),
    RunStatus.WAITING_INPUT: frozenset({RunStatus.PLANNING, RunStatus.CANCELLED}),
    RunStatus.EXECUTING: frozenset(
        {
            RunStatus.WAITING_APPROVAL,
            RunStatus.VERIFYING,
            RunStatus.FAILED,
            RunStatus.PAUSED,
        }
    ),
    RunStatus.WAITING_APPROVAL: frozenset(
        {RunStatus.EXECUTING, RunStatus.VERIFYING, RunStatus.CANCELLED}
    ),
    RunStatus.VERIFYING: frozenset({RunStatus.COMMITTING, RunStatus.FAILED, RunStatus.PAUSED}),
    RunStatus.COMMITTING: frozenset({RunStatus.PUBLISHING, RunStatus.FAILED}),
    RunStatus.PUBLISHING: frozenset({RunStatus.COMPLETED, RunStatus.FAILED}),
    RunStatus.COMPLETED: frozenset(),
    RunStatus.FAILED: frozenset({RunStatus.PLANNING, RunStatus.CANCELLED}),
    RunStatus.PAUSED: frozenset({RunStatus.EXECUTING, RunStatus.CANCELLED}),
    RunStatus.CANCELLED: frozenset(),
}


class RunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: UUID
    task_type: str = Field(min_length=1, max_length=100)
    goal: str = Field(min_length=1, max_length=20_000)
    requested_by: str = Field(min_length=1, max_length=200)
    metadata: dict[str, str] = Field(default_factory=dict)


class RunEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    run_id: UUID
    type: str
    status: RunStatus
    created_at: datetime
    payload: dict[str, str] = Field(default_factory=dict)


class Run(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    task_type: str
    goal: str
    requested_by: str
    status: RunStatus = RunStatus.CREATED
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, str] = Field(default_factory=dict)
    version: int = 0

    def transition(self, target: RunStatus) -> RunEvent:
        previous = self.status
        if target not in ALLOWED_TRANSITIONS[previous]:
            raise InvalidRunTransition(f"{previous} -> {target} is not allowed")
        self.status = target
        self.version += 1
        self.updated_at = utc_now()
        return RunEvent(
            id=self.version,
            run_id=self.id,
            type="run.status_changed",
            status=target,
            created_at=self.updated_at,
            payload={"previous_status": previous.value},
        )
