---
name: unit-test-bean-validation
description: Provides patterns for unit testing Jakarta Bean Validation (@Valid, @NotNull, @Min, @Max, etc.) with custom validators and constraint violations. Validates logic without Spring context. Use when ensuring data integrity and validation rules are correct.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Bean Validation and Custom Validators

## Overview

This skill defines tests for Jakarta Bean Validation in Spring Boot 3.x projects.
It covers built-in constraints, custom constraints, and group-based validation.

## When to Use

Use this skill when:
- Testing `@NotNull`, `@Email`, `@Size`, `@Min`, and `@Max`
- Testing custom `@Constraint` validators
- Verifying violation message, property path, and invalid value
- Testing validation groups for create and update flows

Trigger phrases:
- "test bean validation"
- "custom constraint validator test"
- "validate dto constraints"
- "jakarta validation unit test"

## Instructions

1. Build `Validator` using `Validation.buildDefaultValidatorFactory()`.
2. Write one focused test per rule and failure mode.
3. Assert violation count, property path, and message content.
4. Test valid objects to prevent false positives.
5. Use parameterized tests for sets of invalid inputs.
6. Validate groups explicitly with `validator.validate(target, Group.class)`.

## Examples

```java
@Test
void shouldRejectInvalidEmail() {
  Validator v = Validation.buildDefaultValidatorFactory().getValidator();
  UserDto dto = new UserDto("Alice", "invalid-email");

  Set<ConstraintViolation<UserDto>> violations = v.validate(dto);

  assertThat(violations).hasSize(1);
  assertThat(violations.iterator().next().getPropertyPath().toString()).isEqualTo("email");
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Keep violation assertions explicit and contract-oriented.
- Test boundary values directly (min, max, empty, null).
- Separate syntax-validity tests from business-rule tests.

## Constraints and Warnings

- Constraint messages can vary with locale and message bundle configuration.
- Custom validators must be stateless to avoid cross-test side effects.
- Group sequence behavior can hide later violations if earlier groups fail.
- Null-handling differs by constraint type (`@NotNull` vs format constraints).

## Constraints

- Do not require full Spring context for basic validation unit tests.
- Do not depend on localized messages unless locale is fixed in the test.
- Keep examples compatible with Jakarta Validation and JUnit 5.

## References

- [Examples](references/examples.md) - Complete runnable test examples
