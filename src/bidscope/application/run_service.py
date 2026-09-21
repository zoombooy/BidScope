from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from bidscope.domain.runs import Run, RunCreate, RunEvent, RunStatus


class RunNotFound(LookupError):
    pass


class RunRepository:
    def __init__(self) -> None:
        self._runs: dict[UUID, Run] = {}
        self._events: dict[UUID, list[RunEvent]] = {}

    def create(self, payload: RunCreate) -> Run:
        run = Run(**payload.model_dump())
        self._runs[run.id] = run
        self._events[run.id] = []
        return run.model_copy(deep=True)

    def get(self, run_id: UUID) -> Run:
        try:
            return self._runs[run_id].model_copy(deep=True)
        except KeyError as exc:
            raise RunNotFound(str(run_id)) from exc

    def save(self, run: Run, event: RunEvent) -> Run:
        if run.id not in self._runs:
            raise RunNotFound(str(run.id))
        self._runs[run.id] = run.model_copy(deep=True)
        self._events[run.id].append(event)
        return run.model_copy(deep=True)

    def events(self, run_id: UUID) -> list[RunEvent]:
        self.get(run_id)
        return [event.model_copy(deep=True) for event in self._events[run_id]]


class RunService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    def create(self, payload: RunCreate) -> Run:
        return self.repository.create(payload)

    def get(self, run_id: UUID) -> Run:
        return self.repository.get(run_id)

    def transition(self, run_id: UUID, target: RunStatus) -> Run:
        run = self.repository.get(run_id)
        previous = run.status
        event = run.transition(target)
        event = event.model_copy(update={"payload": {"previous_status": previous.value}})
        return self.repository.save(run, event)

    def events(self, run_id: UUID) -> Iterable[RunEvent]:
        return self.repository.events(run_id)
