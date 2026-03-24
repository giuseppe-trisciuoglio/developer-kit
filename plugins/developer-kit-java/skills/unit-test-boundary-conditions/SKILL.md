---
name: unit-test-boundary-conditions
description: Provides edge case, corner case, boundary condition, and limit testing patterns for Java unit tests. Validates minimum/maximum values, null cases, empty collections, numeric overflow/underflow, floating-point precision, and off-by-one scenarios using JUnit 5 and AssertJ. Use when writing .java test files to ensure code handles limits, corner cases, and special inputs correctly.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Boundary Conditions and Edge Cases

## Overview

Systematic patterns for testing boundary conditions, corner cases, and limit values in Java using JUnit 5. Covers numeric boundaries, string edge cases, collection states, floating-point precision, date/time limits, and off-by-one scenarios.

## When to Use

- Numeric min/max limits, null/empty/whitespace inputs
- Overflow/underflow validation, collection boundaries
- Off-by-one errors, floating-point precision

## Instructions

1. **Identify boundaries**: List numeric limits (MIN_VALUE, MAX_VALUE, zero), string states (null, empty, whitespace), collection sizes (0, 1, many)
2. **Apply parameterized tests**: Use `@ParameterizedTest` with `@ValueSource` or `@CsvSource` for multiple boundary values
3. **Test both sides of boundaries**: Cover values just below, at, and just above each boundary
4. **Run tests after adding each boundary category** to catch issues early
5. **Verify floating-point precision**: Use `isCloseTo(expected, within(tolerance))` with AssertJ
6. **Test collection states**: Explicitly test empty (0), single (1), and many (>1) element scenarios
7. **Handle overflow/underflow**: Use `Math.addExact()` and `Math.subtractExact()` to detect arithmetic overflow
8. **Test date/time edges**: Verify leap years, month boundaries, timezone transitions
9. **Iterate based on failures**: When a boundary test fails, analyze the error to discover additional untested boundaries; add test cases for the newly discovered edge conditions

## Examples

Requires: `junit-jupiter`, `junit-jupiter-params`, `assertj-core`.

## Integer Boundary Testing

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.assertj.core.api.Assertions.*;

class IntegerBoundaryTest {

  @ParameterizedTest
  @ValueSource(ints = {Integer.MIN_VALUE, Integer.MIN_VALUE + 1, 0, Integer.MAX_VALUE - 1, Integer.MAX_VALUE})
  void shouldHandleIntegerBoundaries(int value) {
    assertThat(value).isNotNull();
  }

  @Test
  void shouldDetectIntegerOverflow() {
    assertThatThrownBy(() -> Math.addExact(Integer.MAX_VALUE, 1))
      .isInstanceOf(ArithmeticException.class);
  }

  @Test
  void shouldDetectIntegerUnderflow() {
    assertThatThrownBy(() -> Math.subtractExact(Integer.MIN_VALUE, 1))
      .isInstanceOf(ArithmeticException.class);
  }

  @Test
  void shouldHandleZeroEdge() {
    int result = MathUtils.divide(0, 5);
    assertThat(result).isZero();

    assertThatThrownBy(() -> MathUtils.divide(5, 0))
      .isInstanceOf(ArithmeticException.class);
  }
}
```

## String Boundary Testing

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class StringBoundaryTest {

  @ParameterizedTest
  @ValueSource(strings = {"", " ", "  ", "\t", "\n"})
  void shouldRejectEmptyAndWhitespace(String input) {
    boolean result = StringUtils.isNotBlank(input);
    assertThat(result).isFalse();
  }

  @Test
  void shouldHandleNullString() {
    String result = StringUtils.trim(null);
    assertThat(result).isNull();
  }

  @Test
  void shouldHandleSingleCharacter() {
    assertThat(StringUtils.capitalize("a")).isEqualTo("A");
    assertThat(StringUtils.trim("x")).isEqualTo("x");
  }

  @Test
  void shouldHandleVeryLongString() {
    String longString = "x".repeat(1000000);

    assertThat(longString.length()).isEqualTo(1000000);
    assertThat(StringUtils.isNotBlank(longString)).isTrue();
  }
}
```

## Collection Boundary Testing

```java
class CollectionBoundaryTest {

  @Test
  void shouldHandleEmptyList() {
    List<String> empty = List.of();

    assertThat(empty).isEmpty();
    assertThat(CollectionUtils.first(empty)).isNull();
    assertThat(CollectionUtils.count(empty)).isZero();
  }

  @Test
  void shouldHandleSingleElementList() {
    List<String> single = List.of("only");

    assertThat(single).hasSize(1);
    assertThat(CollectionUtils.first(single)).isEqualTo("only");
    assertThat(CollectionUtils.last(single)).isEqualTo("only");
  }

  @Test
  void shouldHandleLargeList() {
    List<Integer> large = new ArrayList<>();
    for (int i = 0; i < 100000; i++) {
      large.add(i);
    }

    assertThat(large).hasSize(100000);
    assertThat(CollectionUtils.first(large)).isZero();
    assertThat(CollectionUtils.last(large)).isEqualTo(99999);
  }

  @Test
  void shouldHandleNullInCollection() {
    List<String> withNull = new ArrayList<>(List.of("a", null, "c"));

    assertThat(withNull).contains(null);
    assertThat(CollectionUtils.filterNonNull(withNull)).hasSize(2);
  }
}
```

## Floating-Point Boundary Testing

```java
class FloatingPointBoundaryTest {

  @Test
  void shouldHandleFloatingPointPrecision() {
    double result = 0.1 + 0.2;
    assertThat(result).isCloseTo(0.3, within(0.0001));
  }

  @Test
  void shouldHandleSpecialFloatingPointValues() {
    assertThat(Double.POSITIVE_INFINITY).isGreaterThan(Double.MAX_VALUE);
    assertThat(Double.NEGATIVE_INFINITY).isLessThan(Double.MIN_VALUE);
    assertThat(Double.NaN).isNotEqualTo(Double.NaN);
  }

  @Test
  void shouldHandleZeroInDivision() {
    assertThat(1.0 / 0.0).isEqualTo(Double.POSITIVE_INFINITY);
    assertThat(-1.0 / 0.0).isEqualTo(Double.NEGATIVE_INFINITY);
    assertThat(0.0 / 0.0).isNaN();
  }
}
```

## Date/Time Boundary Testing

```java
class DateTimeBoundaryTest {

  @Test
  void shouldHandleMinAndMaxDates() {
    LocalDate min = LocalDate.MIN;
    LocalDate max = LocalDate.MAX;

    assertThat(min).isBefore(max);
    assertThat(DateUtils.isValid(min)).isTrue();
    assertThat(DateUtils.isValid(max)).isTrue();
  }

  @Test
  void shouldHandleLeapYearBoundary() {
    LocalDate leapYearEnd = LocalDate.of(2024, 2, 29);
    assertThat(leapYearEnd).isNotNull();
  }

  @Test
  void shouldRejectInvalidDateInNonLeapYear() {
    assertThatThrownBy(() -> LocalDate.of(2023, 2, 29))
      .isInstanceOf(DateTimeException.class);
  }
}
```

## Array Index Boundary Testing

```java
class ArrayBoundaryTest {

  @Test
  void shouldHandleFirstElementAccess() {
    int[] array = {1, 2, 3, 4, 5};
    assertThat(array[0]).isEqualTo(1);
  }

  @Test
  void shouldHandleLastElementAccess() {
    int[] array = {1, 2, 3, 4, 5};
    assertThat(array[array.length - 1]).isEqualTo(5);
  }

  @Test
  void shouldThrowOnNegativeIndex() {
    int[] array = {1, 2, 3};
    assertThatThrownBy(() -> array[-1])
      .isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }

  @Test
  void shouldThrowOnOutOfBoundsIndex() {
    int[] array = {1, 2, 3};
    assertThatThrownBy(() -> array[10])
      .isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }

  @Test
  void shouldHandleEmptyArray() {
    int[] empty = {};
    assertThat(empty.length).isZero();
    assertThatThrownBy(() -> empty[0])
      .isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }
}
```

## Best Practices

- **Test at boundaries explicitly**: don't rely on random testing
- **Test null and empty separately** from valid inputs
- **Use parameterized tests** for multiple boundary cases
- **Test both sides of boundaries** (just below, at, just above)
- **Verify error messages** for invalid boundary inputs
- **Document why** specific boundaries matter for your domain
- **Test overflow/underflow** for all numeric operations

## Constraints and Warnings

- **Integer overflow**: Use `Math.addExact()` to detect silent overflow
- **Floating-point precision**: Never use exact equality; always use tolerance-based assertions
- **NaN behavior**: `NaN != NaN`; use `Float.isNaN()` or `Double.isNaN()`
- **Collection size limits**: Be mindful of memory with large test collections
- **String encoding**: Test with Unicode characters for internationalization
- **Date/time boundaries**: Account for timezone transitions and daylight saving
- **Array indexing**: Always test index 0, length-1, and out-of-bounds

## References

- [Integer.MIN_VALUE/MAX_VALUE](https://docs.oracle.com/javase/8/docs/api/java/lang/Integer.html)
- [Double.MIN_VALUE/MAX_VALUE](https://docs.oracle.com/javase/8/docs/api/java/lang/Double.html)
- [AssertJ Floating Point](https://assertj.github.io/assertj-core-features-highlight.html#assertions-on-numbers)
- [Boundary Value Analysis](https://en.wikipedia.org/wiki/Boundary-value_analysis)
- [references/concurrent-testing.md](references/concurrent-testing.md) - Thread safety patterns
- [references/parameterized-patterns.md](references/parameterized-patterns.md) - Off-by-one and parameterized examples
