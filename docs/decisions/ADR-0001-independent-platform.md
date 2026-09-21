# ADR-0001: BidScope is an independent platform

## Status

Accepted

## Decision

BidScope will be implemented as a new Python platform. Yuxi, Jinlin/Utopia,
and BidMaster-Pro may inform design decisions, but BidScope will not import
their application modules, share their databases, or require their services
at runtime.

## Why

- Independent releases are a hard requirement.
- The three reference projects have different data models and lifecycle rules.
- Direct composition would make upgrades and failure isolation difficult.
- A new domain model lets the platform support more than one business pack.

## Consequences

- BidScope must define its own contracts and persistence model.
- Useful capabilities are reimplemented behind stable ports.
- Data import from older systems is an explicit, one-way migration concern.
- Protocol-level interoperability may be added later without coupling internals.
