---
name: unit-test-utility-methods
description: Provides patterns for testing utility classes, static methods, and helper functions. Validates pure functions, null handling, edge cases, and boundary conditions. Generates AssertJ assertions and @ParameterizedTest for string utils, math utils, validators, and collection helpers. Use when testing utils, test helpers, helper functions, static methods, or verifying utility code correctness.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Utility Classes and Static Methods

## Overview

This skill generates tests for utility classes with static helper methods and pure functions. It provides patterns for testing null handling, edge cases, boundary conditions, and common utilities like string manipulation, calculations, data validation, and collections. Pure functions require no mocking.

## When to Use

Use this skill when:
- Writing tests for utility/helper classes with static methods
- Testing pure functions with no state or side effects
- Testing string manipulation, formatting, or transformation utilities
- Testing calculation, conversion, or math helper functions
- Testing data validation and formatter utilities
- Verifying null/empty input handling in utility code
- Testing collections or array helper methods

## Instructions

1. **Create test class**: Name it after the utility (e.g., `StringUtilsTest`)
2. **Test happy path**: Valid inputs with expected outputs
3. **Test edge cases**: null, empty, whitespace, single elements
4. **Test boundary conditions**: max/min values, large numbers, precision
5. **Use descriptive names**: `shouldCapitalizeFirstLetter` instead of `test1`
6. **Use AssertJ**: For readable, chainable assertions
7. **Use `@ParameterizedTest`**: For multiple similar inputs (see `references/parameterized-tests.md`)
8. **Avoid mocking**: Pure utilities need no mocks

## Examples

### Basic Static Utility Test

```java
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class StringUtilsTest {

    @Test
    void shouldCapitalizeFirstLetter() {
        assertThat(StringUtils.capitalize("hello")).isEqualTo("Hello");
    }

    @Test
    void shouldReturnNullForNullInput() {
        assertThat(StringUtils.capitalize(null)).isNull();
    }

    @Test
    void shouldHandleEmptyString() {
        assertThat(StringUtils.capitalize("")).isEmpty();
    }

    @Test
    void shouldHandleSingleCharacter() {
        assertThat(StringUtils.capitalize("a")).isEqualTo("A");
    }
}
```

### Comprehensive Example: isEmpty Implementation

```java
// Input: public static boolean isEmpty(String str)
//   { return str == null || str.trim().isEmpty(); }

class StringUtilsTest {

    @Test
    void shouldReturnTrueForNullString() {
        assertThat(StringUtils.isEmpty(null)).isTrue();
    }

    @Test
    void shouldReturnTrueForEmptyString() {
        assertThat(StringUtils.isEmpty("")).isTrue();
    }

    @Test
    void shouldReturnTrueForWhitespaceOnly() {
        assertThat(StringUtils.isEmpty("   ")).isTrue();
    }

    @Test
    void shouldReturnFalseForNonEmptyString() {
        assertThat(StringUtils.isEmpty("hello")).isFalse();
    }
}
```

### Null-Safe Utility

```java
class NullSafeUtilsTest {

    @Test
    void shouldReturnDefaultWhenNull() {
        assertThat(NullSafeUtils.getOrDefault(null, "default")).isEqualTo("default");
    }

    @Test
    void shouldReturnValueWhenNotNull() {
        assertThat(NullSafeUtils.getOrDefault("value", "default")).isEqualTo("value");
    }

    @Test
    void shouldReturnFalseWhenBlank() {
        assertThat(NullSafeUtils.isNotBlank(null)).isFalse();
        assertThat(NullSafeUtils.isNotBlank("   ")).isFalse();
    }
}
```

### Math/Calculation Utility

```java
class MathUtilsTest {

    @Test
    void shouldCalculatePercentage() {
        assertThat(MathUtils.percentage(25, 100)).isEqualTo(25.0);
    }

    @Test
    void shouldHandleZeroDivisor() {
        assertThat(MathUtils.percentage(50, 0)).isZero();
    }

    @Test
    void shouldRoundToDecimalPlaces() {
        assertThat(MathUtils.round(3.14159, 2)).isEqualTo(3.14);
    }

    @Test
    void shouldHandleFloatingPointWithTolerance() {
        assertThat(MathUtils.multiply(0.1, 0.2))
            .isCloseTo(0.02, within(0.0001));
    }
}
```

### Collection Utility

```java
class CollectionUtilsTest {

    @Test
    void shouldFilterList() {
        List<Integer> result = CollectionUtils.filter(List.of(1, 2, 3, 4), n -> n % 2 == 0);
        assertThat(result).containsExactly(2, 4);
    }

    @Test
    void shouldHandleNullList() {
        assertThat(CollectionUtils.filter(null, n -> true)).isEmpty();
    }

    @Test
    void shouldJoinWithSeparator() {
        assertThat(CollectionUtils.join(List.of("a", "b", "c"), "-")).isEqualTo("a-b-c");
    }

    @Test
    void shouldDeduplicateList() {
        assertThat(CollectionUtils.deduplicate(List.of("a", "b", "a")))
            .containsExactlyInAnyOrder("a", "b");
    }
}
```

### Data Validation Utility

```java
class ValidatorUtilsTest {

    @Test
    void shouldValidateEmailFormat() {
        assertThat(ValidatorUtils.isValidEmail("user@example.com")).isTrue();
        assertThat(ValidatorUtils.isValidEmail("invalid")).isFalse();
    }

    @Test
    void shouldValidateUrlFormat() {
        assertThat(ValidatorUtils.isValidUrl("https://example.com")).isTrue();
        assertThat(ValidatorUtils.isValidUrl("not a url")).isFalse();
    }

    @Test
    void shouldValidateCreditCard() {
        assertThat(ValidatorUtils.isValidCreditCard("4532015112830366")).isTrue();
        assertThat(ValidatorUtils.isValidCreditCard("1234567890123456")).isFalse();
    }
}
```

### Utility with Clock Dependency (Rare)

```java
@ExtendWith(MockitoExtension.class)
class DateUtilsTest {

    @Mock
    private Clock clock;

    @Test
    void shouldGetDateFromClock() {
        when(clock.instant()).thenReturn(Instant.parse("2024-01-15T10:00:00Z"));
        assertThat(DateUtils.today(clock)).isEqualTo(LocalDate.of(2024, 1, 15));
    }
}
```

## Best Practices

- **Test pure functions exclusively** - no side effects or state dependency
- **Cover happy path and edge cases** - null, empty, whitespace, extreme values
- **Use descriptive test names** - `shouldReturnNullWhenInputIsNull`
- **Use `@ParameterizedTest`** for multiple similar inputs (see `references/parameterized-tests.md`)
- **Test boundary conditions** - min/max values, overflow, precision
- **Avoid mocking pure functions** - only mock external dependencies like Clock
- **Keep tests independent** - no order dependency between tests

## Constraints and Warnings

- **No mocking static methods**: Use reflection utilities only when absolutely necessary
- **Pure function requirement**: Stateful utilities are harder to test; prefer immutability
- **Floating point precision**: Never use exact equality; use `isCloseTo(delta)`
- **Null handling consistency**: Decide whether utility returns null or throws; test accordingly
- **Thread safety**: Static utilities must be thread-safe; verify concurrent behavior separately
- **Immutable inputs**: Document whether utilities modify input parameters
- **Edge cases reference**: See `references/edge-cases.md` for boundary testing patterns
