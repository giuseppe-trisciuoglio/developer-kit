# ADR Examples

## Example 1

**Path:** `docs/architecture/adr/0003-adopt-postgresql-for-primary-database.md`

```markdown
# ADR-0003: Adopt PostgreSQL for the Primary Database

## Status
Accepted

## Context
The application has outgrown SQLite for concurrent writes and operational visibility. We need stronger transactional guarantees, better backup tooling, and a database that can support production traffic growth.

## Decision
Adopt PostgreSQL as the primary relational database for all new production deployments.

## Consequences
PostgreSQL improves concurrency, operational tooling, and long-term scalability. It also introduces additional infrastructure and migration complexity compared with SQLite.
```

## Example 2

**Path:** `docs/architecture/adr/0004-introduce-event-driven-order-processing.md`

```markdown
# ADR-0004: Introduce Event-Driven Order Processing

## Status
Proposed

## Context
Synchronous order processing is increasing latency in the checkout flow and makes retries difficult when downstream services are degraded.

## Decision
Introduce an event-driven workflow for order fulfillment so checkout can publish an order event and downstream processors can handle fulfillment asynchronously.

## Consequences
This change should reduce user-facing latency and improve resilience. It also adds messaging infrastructure, operational monitoring needs, and eventual-consistency trade-offs.
```

## Naming Tips

- Prefer action-oriented titles such as "Adopt", "Introduce", "Standardize", or "Migrate"
- Keep filenames short but descriptive
- Reuse the repository's numbering pattern if ADRs already exist
