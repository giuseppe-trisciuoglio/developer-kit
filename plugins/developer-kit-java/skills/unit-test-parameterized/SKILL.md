---
name: unit-test-parameterized
description: Provides parameterized testing patterns with @ParameterizedTest, @ValueSource, @CsvSource. Enables running a single test method with multiple input combinations. Use when testing multiple scenarios with similar logic.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Parameterized Unit Tests with JUnit 5

## Overview

This skill defines data-driven test patterns with JUnit 5 parameterized tests.
It reduces duplication while improving coverage across multiple input combinations.

## When to Use

Use this skill when:
- Running one assertion flow against many values
- Testing boundary values and invalid input matrices
- Validating enum-driven behavior across states
- Reusing structured test data with `@MethodSource`

Trigger phrases:
- "parameterized junit test"
- "value source csv source"
- "methodsource test data"
- "data driven unit test"

## Instructions

1. Add `junit-jupiter-params` to test dependencies.
2. Choose source by complexity: `@ValueSource`, `@CsvSource`, `@MethodSource`, `@EnumSource`.
3. Keep method signatures aligned with source argument count and types.
4. Use descriptive display names for readable test output.
5. Group scenarios only when assertion logic is truly identical.
6. Extract reusable `ArgumentsProvider` for shared complex datasets.

## Examples

```java
@ParameterizedTest
@CsvSource({"100,0.10,10", "80,0.20,16"})
void shouldCalculateTax(String net, String rate, String expected) {
  BigDecimal tax = new BigDecimal(net).multiply(new BigDecimal(rate));
  assertThat(tax.setScale(0, RoundingMode.HALF_UP))
    .isEqualByComparingTo(new BigDecimal(expected));
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Keep each parameterized test centered on one behavior.
- Prefer explicit, readable datasets over random data generation.
- Add separate non-parameterized tests for one-off exceptional behavior.

## Constraints and Warnings

- Large parameter matrices can hide failing scenarios and reduce readability.
- Implicit type conversion in CSV sources can produce subtle parsing errors.
- Null handling requires dedicated sources (`@NullSource`, `@NullAndEmptySource`).
- Parameter order mistakes can create false-positive assertions.

## Constraints

- Do not rely on execution order of parameterized invocations.
- Do not combine unrelated scenario categories in one parameterized test.
- Keep examples compatible with JUnit 5 and AssertJ.

## References

- [Examples](references/examples.md) - Complete runnable test examples
