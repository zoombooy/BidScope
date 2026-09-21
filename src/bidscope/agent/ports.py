from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AgentRequest:
    run_id: str
    agent_id: str
    instruction: str
    context: dict[str, str]


@dataclass(frozen=True)
class AgentEvent:
    type: str
    payload: dict[str, str]


class AgentRuntime(Protocol):
    async def run(self, request: AgentRequest) -> AsyncIterator[AgentEvent]:
        """Run one governed agent step and yield observable events."""
