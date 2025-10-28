# Saga Pattern Definition

## What is a Saga?

A **Saga** is a sequence of local transactions where each transaction updates data within a single service. Each local transaction publishes an event or message that triggers the next local transaction in the saga. If a local transaction fails, the saga executes compensating transactions to undo the changes made by preceding transactions.

## Key Characteristics

**Distributed Transactions**: Spans multiple microservices, each with its own database.

**Local Transactions**: Each service performs its own ACID transaction.

**Event-Driven**: Services communicate through events or commands.

**Compensations**: Rollback mechanism using compensating transactions.

**Eventual Consistency**: System reaches a consistent state over time.

## Saga vs Two-Phase Commit (2PC)

| Feature | Saga Pattern | Two-Phase Commit |
|---------|-------------|------------------|
| Locking | No distributed locks | Requires locks during commit |
| Performance | Better performance | Performance bottleneck |
| Scalability | Highly scalable | Limited scalability |
| Complexity | Business logic complexity | Protocol complexity |
| Failure Handling | Compensating transactions | Automatic rollback |
| Isolation | Lower isolation | Full isolation |
| NoSQL Support | Yes | No |
| Microservices Fit | Excellent | Poor |

## ACID vs BASE

**ACID** (Traditional Databases):
- **A**tomicity: All or nothing
- **C**onsistency: Valid state transitions
- **I**solation: Concurrent transactions don't interfere
- **D**urability: Committed data persists

**BASE** (Saga Pattern):
- **B**asically **A**vailable: System is available most of the time
- **S**oft state: State may change over time
- **E**ventual consistency: System becomes consistent eventually

## When to Use Saga Pattern

Use the saga pattern when:
- Building distributed transactions across multiple microservices
- Needing to replace 2PC with a more scalable solution
- Services need to maintain eventual consistency
- Handling long-running processes spanning multiple services
- Implementing compensating transactions for failed operations

## When NOT to Use Saga Pattern

Avoid the saga pattern when:
- Single service transactions (use local ACID transactions)
- Strong consistency is required immediately
- Simple CRUD operations without cross-service dependencies
- Low transaction volume with simple flows
- Team lacks experience with distributed systems

## Migration Path

Many organizations migrate from traditional monolithic systems or 2PC-based systems to sagas:

1. **From Monolith to Saga**: Identify transaction boundaries, extract services gradually, implement sagas incrementally
2. **From 2PC to Saga**: Analyze existing 2PC transactions, design compensating transactions, implement sagas in parallel, monitor and compare results before full migration
