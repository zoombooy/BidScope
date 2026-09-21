# BidScope

BidScope is an independent, evidence-first agent workbench for complex business tasks.
It is a new project. Yuxi, Jinlin/Utopia, and BidMaster-Pro are reference material only;
they are not runtime dependencies and their databases are not shared.

## Current milestone

Milestone 0 establishes the control-plane contract:

- Python 3.11+ and FastAPI service boundary.
- Durable-run state model and guarded state transitions.
- REST endpoints for creating and inspecting runs.
- An explicit AgentScope adapter boundary for the future Python agent runtime.
- Architecture and decision records for the independent platform.

The current run API intentionally does not claim that an Agent has completed work.
A run is created in `created` and must be advanced by a future Harness worker.

## Local development

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,runtime]"
uvicorn bidscope.api.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for the API contract.

The included Compose file is a development scaffold. It starts PostgreSQL,
Redis and MinIO for the next milestones, while Milestone 0 still uses an
in-memory run repository. For local overrides, copy `.env.example` to `.env`;
the Compose file also works without that optional file.

## Design boundary

```text
Portal -> Platform API -> Harness control plane -> AgentScope runtime
                         |                    |
                         |                    +-> typed tools / MCP adapters
                         +-> project, task, approval, artifact services

Knowledge Engine is an independent service boundary. It owns documents,
versions, evidence, indexes, ontology and citations; the platform never
reads its tables directly.
```

See [docs/architecture.md](docs/architecture.md) and
[docs/decisions/ADR-0001-independent-platform.md](docs/decisions/ADR-0001-independent-platform.md).
