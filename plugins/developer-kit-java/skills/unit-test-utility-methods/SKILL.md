---
name: unit-test-utility-methods
description: Provides patterns for unit testing utility/helper classes and static methods. Validates pure functions and helper logic. Use when verifying utility code correctness.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Utility Classes and Static Methods

## Overview

Patterns for testing utility classes and static methods using JUnit 5. Covers pure functions, edge case handling, boundary conditions, string manipulation, calculations, collections, and data validation utilities.

## When to Use

Use this skill when:
- Testing utility classes with static helper methods
- Testing pure functions with no state or side effects
- Testing string manipulation, calculation, and collection utilities
- Testing data transformation and validation helpers

Trigger phrases:
- "test utility methods"
- "test static helper methods"
- "test pure functions"
- "test string math collection utils"

## Instructions

1. **Create test class** named after the utility (e.g., StringUtilsTest)
2. **Test happy path** with valid inputs
3. **Test edge cases**: null, empty, zero, boundary conditions
4. **Test error cases**: verify proper exception throwing
5. **Use descriptive test names** (e.g., shouldCapitalizeFirstLetter)
6. **Use AssertJ assertions** for readable test code
7. **Consider @ParameterizedTest** for multiple similar scenarios

## Examples

### String Utility

```java
@Test
void shouldCapitalizeFirstLetter() {
    assertThat(StringUtils.capitalize("hello")).isEqualTo("Hello");
}

@Test
void shouldHandleNullInput() {
    assertThat(StringUtils.capitalize(null)).isNull();
}

@Test
void shouldHandleEmptyString() {
    assertThat(StringUtils.capitalize("")).isEmpty();
}
```

### Math Utility

```java
@Test
void shouldCalculatePercentage() {
    assertThat(MathUtils.percentage(25, 100)).isEqualTo(25.0);
}

@Test
void shouldHandleZeroDivisor() {
    assertThat(MathUtils.percentage(50, 0)).isZero();
}

@Test
void shouldHandleFloatingPointPrecision() {
    assertThat(MathUtils.multiply(0.1, 0.2)).isCloseTo(0.02, within(0.0001));
}
```

### Collection Utility

```java
@Test
void shouldFilterList() {
    List<Integer> even = CollectionUtils.filter(List.of(1, 2, 3, 4, 5), n -> n % 2 == 0);
    assertThat(even).containsExactly(2, 4);
}

@Test
void shouldHandleNullList() {
    assertThat(CollectionUtils.filter(null, n -> true)).isEmpty();
}
```

### Parameterized Tests

```java
@ParameterizedTest
@CsvSource({"hello,HELLO", "world,WORLD", "123ABC,123ABC"})
void shouldConvertToUpperCase(String input, String expected) {
    assertThat(StringUtils.toUpperCase(input)).isEqualTo(expected);
}
```

### Boundary Testing

```java
@Test
void shouldHandleMaxIntegerValue() {
    assertThat(MathUtils.increment(Integer.MAX_VALUE)).isEqualTo(Integer.MAX_VALUE);
}

@Test
void shouldHandleVeryLargeNumbers() {
    BigDecimal result = MathUtils.add(new BigDecimal("999999999999.99"), new BigDecimal("0.01"));
    assertThat(result).isEqualTo(new BigDecimal("1000000000000.00"));
}
```

For detailed examples covering null-safe helpers, format/parse utilities, validator utilities, and dependency-based utility testing, see [Examples](references/examples.md).

## Best Practices

- Test pure functions exclusively (no side effects or state)
- Cover happy path and edge cases (null, empty, extreme values)
- Keep tests simple and short
- Avoid mocking when not needed (only for external dependencies)
- Use @ParameterizedTest for multiple similar scenarios

## Constraints and Warnings

- Static methods cannot be mocked without PowerMock; avoid unless necessary
- Never use exact equality for floating point comparisons; use tolerance
- Decide whether utilities return null or throw exceptions, then test consistently
- Static utilities must be thread-safe

## References

- [JUnit 5 Parameterized Tests](https://junit.org/junit5/docs/current/user-guide/#writing-tests-parameterized-tests)
- [AssertJ Assertions](https://assertj.github.io/assertj-core-features-highlight.html)
