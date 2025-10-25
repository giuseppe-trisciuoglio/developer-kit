---
name: spring-boot-saga-pattern
description: Implement distributed transactions using the Saga Pattern in Spring Boot microservices. Use when building microservices that require transaction management across multiple services, handling compensating transactions, ensuring eventual consistency, or implementing choreography or orchestration-based sagas with Spring Boot, Kafka, or Axon Framework.
version: 1.0.0
author: Developer Kit Claude Code
language: Java
framework: Spring Boot
license: MIT
---

# Spring Boot SAGA Pattern Implementation

## When to Use

Use this skill when you need to:

- Implement **distributed transactions** across multiple microservices
- Handle **transaction rollback** when a service fails in a multi-service workflow
- Ensure **eventual consistency** in microservices architecture
- Replace two-phase commit (2PC) with a more scalable solution
- Implement **compensating transactions** for failed operations
- Build resilient microservices with proper error handling
- Coordinate complex business processes spanning multiple services
- Implement either **choreography-based** or **orchestration-based** sagas

**Trigger phrases**: distributed transactions, saga pattern, compensating transactions, microservices transaction, eventual consistency, rollback across services, orchestration pattern, choreography pattern

## Overview

The **Saga Pattern** is an architectural pattern for managing distributed transactions in microservices. Instead of using a single ACID transaction across multiple databases, a saga breaks the transaction into a sequence of local transactions. Each local transaction updates its database and publishes an event or message to trigger the next step. If a step fails, the saga executes **compensating transactions** to undo the changes made by previous steps.

### Key Concepts

**Local Transactions**: Each microservice performs its own database transaction independently.

**Compensating Transactions**: Rollback operations that undo the work of previously completed transactions. Must be **idempotent** and **retryable**.

**Saga Execution Coordinator (SEC)**: Central component managing the saga flow and invoking compensating transactions when failures occur.

**Eventual Consistency**: Data becomes consistent across services over time, rather than immediately.

## Two Approaches to Implement Saga

### 1. Choreography-Based Saga

Each microservice publishes events and listens to events from other services. **No central coordinator**.

**Advantages**:
- Simple for small number of services
- Loose coupling between services
- No single point of failure

**Disadvantages**:
- Difficult to track workflow state
- Hard to troubleshoot and maintain
- Complexity grows with number of services
- Distributed source of truth

**Best for**: Greenfield microservice applications with few participants.

### 2. Orchestration-Based Saga

A **central orchestrator** manages the entire transaction flow and tells services what to do.

**Advantages**:
- Centralized visibility and monitoring
- Easier to troubleshoot and maintain
- Clear transaction flow
- Simplified error handling
- Better for complex workflows
- Faster time to market

**Disadvantages**:
- Orchestrator can become single point of failure
- Additional infrastructure component

**Best for**: Brownfield applications, complex workflows, or when centralized control is needed.

## Implementation Steps

### Step 1: Define Your Transaction Flow

Identify the sequence of operations and their compensating transactions:

```
Order Created → Payment Processed → Inventory Reserved → Shipment Prepared → Notification Sent

Compensations (reverse order):
Cancel Notification ← Cancel Shipment ← Release Inventory ← Refund Payment ← Cancel Order
```

### Step 2: Choose Implementation Approach

Select based on your requirements:
- **Choreography**: Spring Cloud Stream, Kafka, RabbitMQ
- **Orchestration**: Axon Framework, Eventuate Tram, Camunda, Apache Camel

### Step 3: Implement Services with Local Transactions

Each service handles its local transaction and publishes events or responds to commands.

### Step 4: Implement Compensating Transactions

Every forward transaction must have a corresponding compensating transaction.

### Step 5: Handle Failure Scenarios

Implement retry logic, timeouts, and dead-letter queues for failed messages.

## Best Practices

### Design Principles

1. **Idempotency**: Ensure compensating transactions can be safely executed multiple times
2. **Retryability**: Design operations to handle retries without side effects
3. **Atomicity**: Each local transaction must be atomic within its service
4. **Isolation**: Handle concurrent saga executions properly
5. **Eventual Consistency**: Accept that data will be eventually consistent, not immediately

### Service Design

- Use **constructor injection** exclusively (never field injection)
- Implement services as **stateless** components
- Store saga state in a persistent store (database, event store)
- Use **immutable DTOs** (Java records preferred)
- Separate domain logic from infrastructure concerns

### Error Handling

- Implement **circuit breakers** for service calls
- Use **dead-letter queues** for failed messages
- Log all saga events for debugging and monitoring
- Implement **timeout mechanisms** for long-running sagas
- Design **semantic locks** to prevent concurrent updates

### Testing

- Test happy path scenarios
- Test each failure scenario and its compensation
- Test concurrent saga executions
- Test idempotency of compensating transactions
- Use Testcontainers for integration testing

### Monitoring and Observability

- Track saga execution status and duration
- Monitor compensation transaction execution
- Alert on stuck or failed sagas
- Use distributed tracing (Spring Cloud Sleuth, Zipkin)
- Implement health checks for saga coordinators

## Technology Stack

**Spring Boot 3.x** with the following dependencies:

**Messaging**:
- Spring Cloud Stream
- Apache Kafka / RabbitMQ
- Spring AMQP

**Saga Frameworks**:
- Axon Framework (Orchestration)
- Eventuate Tram Sagas (Orchestration)
- Camunda (BPMN-based orchestration)
- Apache Camel (EIP-based)

**Persistence**:
- Spring Data JPA
- Event Sourcing (optional)
- Transactional Outbox Pattern

**Monitoring**:
- Spring Boot Actuator
- Micrometer
- Distributed Tracing (Sleuth + Zipkin)

## Common Patterns

### Transactional Outbox Pattern

Ensures atomic update of database and message publishing:

1. Insert business entity and outbox message in same transaction
2. Background process polls outbox table
3. Publishes messages to message broker
4. Marks messages as published

### Event Sourcing

Store events instead of current state:
- All state changes are stored as events
- Current state is derived from event stream
- Natural fit for saga pattern
- Provides audit trail

### Saga State Machine

Model saga as a state machine:
- Define states (PENDING, PROCESSING, COMPLETED, COMPENSATING, FAILED)
- Define transitions between states
- Handle timeouts and retries
- Persist state for recovery

## Anti-Patterns to Avoid

❌ **Tight Coupling**: Services directly calling each other instead of using events
❌ **Missing Compensations**: Not implementing compensating transactions for every step
❌ **Non-Idempotent Operations**: Compensations that cannot be safely retried
❌ **Synchronous Sagas**: Waiting synchronously for each step (defeats the purpose)
❌ **Lost Messages**: Not handling message delivery failures
❌ **No Monitoring**: Running sagas without visibility into their status
❌ **Shared Database**: Using same database across multiple services
❌ **Ignoring Network Failures**: Not handling partial failures gracefully

## When NOT to Use Saga Pattern

- Single service transactions (use local ACID transactions)
- Strong consistency is required (consider monolith or shared database)
- Simple CRUD operations without cross-service dependencies
- Low transaction volume with simple flows
- Team lacks experience with distributed systems

## Migration Strategy

### From Monolith to Saga

1. Identify transaction boundaries in monolith
2. Extract services one at a time
3. Implement saga for cross-service transactions
4. Use Strangler Fig pattern for gradual migration
5. Keep monolith database initially, migrate data later

### From 2PC to Saga

1. Analyze existing 2PC transactions
2. Design compensating transactions
3. Implement saga incrementally
4. Run both approaches in parallel initially
5. Monitor and compare results
6. Switch to saga when confident

## Security Considerations

- **Authenticate and authorize** all service-to-service communications
- Use **message encryption** for sensitive data in events
- Implement **audit logging** for all saga executions
- Apply **rate limiting** to prevent abuse
- Validate **message signatures** to prevent tampering
- Use **secrets management** for credentials (not hardcoded)

## Performance Optimization

- Use **asynchronous processing** for all saga steps
- Implement **batch processing** for high-volume scenarios
- Consider **parallel execution** for independent steps
- Use **caching** for frequently accessed reference data
- Optimize **database queries** in each service
- Implement **connection pooling** for databases and message brokers

## Troubleshooting Guide

**Saga stuck in progress**:
- Check for failed services
- Review timeout configurations
- Verify message broker connectivity
- Check for deadlocks in databases

**Compensation not executing**:
- Verify compensating transaction is idempotent
- Check saga coordinator logs
- Ensure proper error handling in services
- Review retry configuration

**Data inconsistency**:
- Check for race conditions
- Review saga isolation level
- Verify compensating transactions executed
- Check for partial failures

## References

- [Saga Pattern - Microservices.io](references.md#saga-pattern-definition)
- [Implementation Examples](examples.md)
- Spring Boot SAGA implementations
- Axon Framework documentation
- Eventuate framework guides

## Version History

- **1.0.0** (2024-01): Initial release with choreography and orchestration patterns
