---
name: unit-test-parameterized
description: Provides parameterized testing patterns with JUnit 5, generates data-driven unit tests using @ParameterizedTest, @ValueSource, @CsvSource, @MethodSource. Creates tests that run the same logic with multiple input values. Use when writing data-driven Java tests, multiple test cases from single method, or boundary value analysis.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Parameterized Unit Tests with JUnit 5

## Overview

Provides patterns for parameterized unit tests in Java using JUnit 5. Covers `@ValueSource`, `@CsvSource`, `@MethodSource`, `@EnumSource`, `@ArgumentsSource`, and custom display names. Reduces test duplication by running the same test logic with multiple input values.

## When to Use

- Writing JUnit tests with multiple input combinations
- Implementing data-driven tests in Java
- Running same test with different values (boundary analysis)
- Testing multiple scenarios from single test method

## Instructions

1. **Add dependency**: Ensure `junit-jupiter-params` is on test classpath (included in `junit-jupiter`)
2. **Choose source**: `@ValueSource` for simple values, `@CsvSource` for tabular data, `@MethodSource` for complex objects
3. **Match parameters**: Test method parameters must match data source types
4. **Set display names**: Use `name = "{0}..."` for readable output
5. **Validate**: Run `./gradlew test --info` or `mvn test` and verify all parameter combinations execute

## Examples

### Maven / Gradle Dependency

JUnit 5 parameterized tests require `junit-jupiter` (includes params). Add `assertj-core` for assertions:

```xml
<!-- Maven -->
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
```

```kotlin
// Gradle
testImplementation("org.junit.jupiter:junit-jupiter")
```

### `@ValueSource` — Simple Values

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.assertj.core.api.Assertions.*;

@ParameterizedTest
@ValueSource(strings = {"hello", "world", "test"})
void shouldCapitalizeAllStrings(String input) {
  assertThat(StringUtils.capitalize(input)).isNotEmpty();
}

@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 4, 5})
void shouldBePositive(int number) {
  assertThat(number).isPositive();
}

@ParameterizedTest
@ValueSource(ints = {Integer.MIN_VALUE, -1, 0, 1, Integer.MAX_VALUE})
void shouldHandleBoundaryValues(int value) {
  assertThat(Math.incrementExact(value)).isGreaterThan(value);
}
```

### `@CsvSource` — Tabular Data

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

@ParameterizedTest
@CsvSource({
  "alice@example.com, true",
  "bob@gmail.com,     true",
  "invalid-email,     false",
  "user@,             false",
  "@example.com,       false"
})
void shouldValidateEmailAddresses(String email, boolean expected) {
  assertThat(UserValidator.isValidEmail(email)).isEqualTo(expected);
}
```

### `@MethodSource` — Complex Data

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import java.util.stream.Stream;

@ParameterizedTest
@MethodSource("additionTestCases")
void shouldAddNumbersCorrectly(int a, int b, int expected) {
  assertThat(Calculator.add(a, b)).isEqualTo(expected);
}

static Stream<Arguments> additionTestCases() {
  return Stream.of(
    Arguments.of(1, 2, 3),
    Arguments.of(0, 0, 0),
    Arguments.of(-1, 1, 0),
    Arguments.of(100, 200, 300)
  );
}
```

### `@EnumSource` — Enum Values

```java
@ParameterizedTest
@EnumSource(Status.class)
void shouldHandleAllStatuses(Status status) {
  assertThat(status).isNotNull();
}

@ParameterizedTest
@EnumSource(value = Status.class, names = {"ACTIVE", "INACTIVE"})
void shouldHandleSpecificStatuses(Status status) {
  assertThat(status).isIn(Status.ACTIVE, Status.INACTIVE);
}
```

### Custom Display Names

```java
@ParameterizedTest(name = "Discount of {0}% should be calculated correctly")
@ValueSource(ints = {5, 10, 15, 20})
void shouldApplyDiscount(int discountPercent) {
  double result = DiscountCalculator.apply(100.0, discountPercent);
  assertThat(result).isEqualTo(100.0 * (1 - discountPercent / 100.0));
}
```

### Custom `ArgumentsProvider`

```java
class RangeValidatorProvider implements ArgumentsProvider {
  @Override
  public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
    return Stream.of(
      Arguments.of(0, 0, 100, true),
      Arguments.of(50, 0, 100, true),
      Arguments.of(-1, 0, 100, false),
      Arguments.of(101, 0, 100, false)
    );
  }
}

@ParameterizedTest
@ArgumentsSource(RangeValidatorProvider.class)
void shouldValidateRange(int value, int min, int max, boolean expected) {
  assertThat(RangeValidator.isInRange(value, min, max)).isEqualTo(expected);
}
```

### Error Condition Testing

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", null})
void shouldThrowExceptionForInvalidInput(String input) {
  assertThatThrownBy(() -> Parser.parse(input))
    .isInstanceOf(IllegalArgumentException.class);
}
```

## Best Practices

- Use descriptive display names: `name = "{0}..."` for readable output
- Test boundary values: include min, max, zero, and edge cases
- Keep test logic focused: single assertion per parameter set
- Use `@MethodSource` for complex objects, `@CsvSource` for tabular data
- Organize test data logically — group related scenarios together

## Constraints and Warnings

- **Parameter count must match**: Number of parameters from source must match test method signature
- **`@ValueSource` limitation**: Only supports primitives, strings, and enums — not objects or null directly
- **CSV escaping**: Strings with commas must use single quotes in `@CsvSource`
- **`@MethodSource` visibility**: Factory methods must be static in the same test class
- **Display name placeholders**: Use `{0}`, `{1}`, etc. to reference parameters
- **Execution count**: Each parameter set runs as a separate test invocation

## References

- [JUnit 5 Parameterized Tests](https://junit.org/junit5/docs/current/user-guide/#writing-tests-parameterized-tests)
- [`@ParameterizedTest` API](https://junit.org/junit5/docs/current/api/org.junit.jupiter.params/org/junit/jupiter/params/ParameterizedTest.html)
