# BidScope Architecture Baseline

## Positioning

BidScope is an independent platform for evidence-first business work. It is
not a runtime composition of Yuxi, Jinlin/Utopia, or BidMaster-Pro. Those
projects are reference material only. BidScope owns its own data model,
workflow state, agent runtime adapter, knowledge engine boundary, and release
process.

## Runtime boundaries

```text
Portal -> Platform API -> Harness control plane -> Harness worker
                                      |              |
                                      |              +-> AgentScope 2.x adapter
                                      |              +-> typed internal tools
                                      |              +-> MCP adapters at the boundary
                                      +-> project/task/approval/artifact services

Knowledge API -> ingest workers -> parser/chunker/indexer -> knowledge stores
```

The knowledge engine is an independent service boundary. Platform services
must use its API and must not query knowledge tables directly.

## Source-of-truth rules

| Area | Source of truth |
|---|---|
| Projects, tasks and approvals | Platform database |
| Run and step state | Harness database tables |
| Documents, versions and evidence | Knowledge database |
| Original files and artifacts | Object storage |
| Search indexes | Rebuildable projections |
| Agent traces | Observability store; not business truth |
| Audit records | Append-only platform audit store |

## Harness invariants

1. An Agent cannot mark a run completed directly.
2. Every side effect is represented by a typed command and an audit event.
3. A run can be resumed from the last committed step.
4. A retry is idempotent by `run_id`, `step_id`, and command key.
5. Evidence is required before a knowledge-grounded result can be published.
6. Approval is required before a result changes formal business state.

## Initial deployment shape

The first deployment is a modular FastAPI control plane plus independent
workers. It is not split into many microservices until measured load or team
ownership requires it.

```text
platform-api x N
harness-worker x N
ingest-worker x N
scheduler x 1..N
knowledge-api x N
postgres / redis / object-storage
```
