---
name: unit-test-utility-methods
description: Provides patterns for unit testing utility/helper classes and static methods. Validates pure functions and helper logic. Use when verifying utility code correctness.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Utility Classes and Static Methods

## Overview

This skill defines unit test patterns for static helpers and pure utility functions.
It focuses on deterministic outputs, edge-case coverage, and concise assertions.

## When to Use

Use this skill when:
- Testing static helper methods
- Testing pure transformation logic with no side effects
- Validating string, math, collection, and date utility behavior
- Verifying null, empty, and boundary handling

Trigger phrases:
- "test utility methods"
- "test static helpers"
- "pure function unit test"
- "helper class edge cases"

## Instructions

1. Test utility methods directly without Spring context.
2. Cover happy path, edge path, and invalid input path.
3. Use parameterized tests for repetitive value matrices.
4. Assert thrown exceptions with exact type and message when relevant.
5. Verify idempotency for normalization and formatting helpers.
6. Keep test names behavior-based and explicit.

## Examples

```java
@Test
void shouldCapitalizeFirstLetter() {
  assertThat(TextUtils.capitalize("hello")).isEqualTo("Hello");
}

@Test
void shouldHandleNullInput() {
  assertThat(TextUtils.capitalize(null)).isNull();
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Keep utilities cohesive by domain and free from hidden dependencies.
- Include boundary tests for numeric and collection helpers.
- Assert exact outputs for formatting-sensitive methods.

## Constraints and Warnings

- Static helpers that depend on time, locale, or timezone need controlled test fixtures.
- Shared mutable static state can create test-order coupling.
- Floating-point assertions require tolerances to avoid precision false failures.
- Utility tests should avoid mocking unless wrapping external APIs.

## Constraints

- Do not use integration scaffolding for pure utility tests.
- Do not mix unrelated utility domains in one test class.
- Keep examples compatible with JUnit 5 and AssertJ.

## References

- [Examples](references/examples.md) - Complete runnable test examples
