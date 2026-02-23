---
name: unit-test-application-events
description: Provides patterns for testing Spring application events (ApplicationEvent) with @EventListener and ApplicationEventPublisher. Handles event publishing, listening, and async event handling in Spring Boot applications. Use when validating event-driven workflows in your Spring Boot services.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Application Events

## Overview

This skill defines test patterns for event-driven Spring Boot 3.x components.
It validates publication, listener behavior, payload correctness, and async completion.

## When to Use

Use this skill when:
- Testing `ApplicationEventPublisher` usage in services
- Testing `@EventListener` side effects and dependency calls
- Verifying event payload fields and routing assumptions
- Testing async listener completion deterministically

Trigger phrases:
- "test application events"
- "verify event publisher"
- "test event listener"
- "spring event unit test"

## Instructions

1. In publisher tests, mock `ApplicationEventPublisher` and capture emitted events.
2. Use `ArgumentCaptor` to verify event payload values.
3. Test listener classes directly by invoking listener methods.
4. Verify listener side effects on mocked dependencies.
5. For async listeners, use `CountDownLatch` or Awaitility.
6. Include failure-path tests for listener exception handling.

## Examples

```java
@Test
void shouldPublishUserCreatedEvent() {
  service.createUser("alice@example.com");

  ArgumentCaptor<UserCreatedEvent> captor = ArgumentCaptor.forClass(UserCreatedEvent.class);
  verify(eventPublisher).publishEvent(captor.capture());

  assertThat(captor.getValue().email()).isEqualTo("alice@example.com");
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Separate publisher tests from listener tests.
- Assert event payload content, not only publication occurrence.
- Keep listeners thin and delegate business logic.

## Constraints and Warnings

- `@Async` listeners need explicit test synchronization to avoid flaky assertions.
- Direct listener invocation skips framework wiring concerns and ordering semantics.
- Multiple listeners can process the same event; side effects must be idempotent.
- Transaction-bound events (`@TransactionalEventListener`) behave differently from plain listeners.

## Constraints

- Do not use external brokers for ApplicationEvent unit tests.
- Do not rely on arbitrary `Thread.sleep` for async validation.
- Keep tests deterministic and isolated.

## References

- [Examples](references/examples.md) - Complete runnable test examples
