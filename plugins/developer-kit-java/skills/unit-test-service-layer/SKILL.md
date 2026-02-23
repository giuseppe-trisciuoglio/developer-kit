---
name: unit-test-service-layer
description: Provides patterns for unit testing service layer with Mockito. Validates business logic in isolation by mocking dependencies. Use when testing service behaviors and business logic without database or external services.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Service Layer with Mockito

## Overview

This skill defines isolated unit-testing patterns for Spring service classes.
Focus on business rules and orchestration while mocking repositories, gateways, and publishers.

## When to Use

Use this skill when:
- Testing business decisions in `@Service` classes
- Verifying interactions with repositories and external clients
- Testing orchestration across multiple dependencies
- Validating domain exceptions and fallback logic

Trigger phrases:
- "test service class"
- "mock repository in unit test"
- "verify service business logic"
- "mockito service layer"

## Instructions

1. Use `@ExtendWith(MockitoExtension.class)` for pure unit tests.
2. Use `@Mock` for collaborators and `@InjectMocks` for the service under test.
3. Arrange deterministic inputs and mock outputs with `when(...).thenReturn(...)`.
4. Assert return values and state transitions with precise assertions.
5. Verify interactions with `verify(...)`, including `times(...)` and `never()`.
6. Use `ArgumentCaptor` where outbound arguments matter.

## Examples

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
  @Mock OrderRepository repo;
  @InjectMocks OrderService service;

  @Test
  void shouldLoadOrder() {
    when(repo.findById(10L)).thenReturn(Optional.of(new Order(10L)));
    Order result = service.requireOrder(10L);
    assertThat(result.id()).isEqualTo(10L);
    verify(repo).findById(10L);
  }
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Assert both method outcome and dependency interactions for orchestration logic.
- Keep fixtures minimal and explicit to reduce brittle tests.
- Use behavior-driven test names that describe service outcomes.

## Constraints and Warnings

- Do not mock the class under test; mock only collaborators.
- Over-verifying call order can create fragile tests unless order is business-critical.
- `@InjectMocks` field injection may hide constructor issues; prefer constructor-first design.
- Service unit tests should not depend on transaction proxies or Spring AOP behavior.

## Constraints

- Do not call real databases, queues, or HTTP endpoints in service unit tests.
- Do not assert framework internals outside service responsibilities.
- Keep tests independent and deterministic.

## References

- [Examples](references/examples.md) - Complete runnable test examples
