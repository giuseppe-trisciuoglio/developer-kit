# Boundary Conditions Testing - Detailed Examples

## Floating Point Boundary Testing

### Precision and Special Values

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
    assertThat(Double.NaN).isNotEqualTo(Double.NaN); // NaN != NaN
  }

  @Test
  void shouldHandleVerySmallAndLargeNumbers() {
    double tiny = Double.MIN_VALUE;
    double huge = Double.MAX_VALUE;
    assertThat(tiny).isGreaterThan(0);
    assertThat(huge).isPositive();
  }

  @Test
  void shouldHandleZeroInDivision() {
    double result = 1.0 / 0.0;
    assertThat(result).isEqualTo(Double.POSITIVE_INFINITY);

    double result2 = -1.0 / 0.0;
    assertThat(result2).isEqualTo(Double.NEGATIVE_INFINITY);

    double result3 = 0.0 / 0.0;
    assertThat(result3).isNaN();
  }
}
```

## Date/Time Boundary Testing

### Min/Max Dates and Edge Cases

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
    assertThat(LocalDate.of(2024, 2, 29)).isEqualTo(leapYearEnd);
  }

  @Test
  void shouldHandleInvalidDateInNonLeapYear() {
    assertThatThrownBy(() -> LocalDate.of(2023, 2, 29))
      .isInstanceOf(DateTimeException.class);
  }

  @Test
  void shouldHandleYearBoundaries() {
    LocalDate newYear = LocalDate.of(2024, 1, 1);
    LocalDate lastDay = LocalDate.of(2024, 12, 31);
    assertThat(newYear).isBefore(lastDay);
  }

  @Test
  void shouldHandleMidnightBoundary() {
    LocalTime midnight = LocalTime.MIDNIGHT;
    LocalTime almostMidnight = LocalTime.of(23, 59, 59);
    assertThat(almostMidnight).isBefore(midnight);
  }
}
```

## Array Index Boundary Testing

### First, Last, and Out of Bounds

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
    assertThatThrownBy(() -> {
      int value = array[-1];
    }).isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }

  @Test
  void shouldThrowOnOutOfBoundsIndex() {
    int[] array = {1, 2, 3};
    assertThatThrownBy(() -> {
      int value = array[10];
    }).isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }

  @Test
  void shouldHandleEmptyArray() {
    int[] empty = {};
    assertThat(empty.length).isZero();
    assertThatThrownBy(() -> {
      int value = empty[0];
    }).isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }
}
```

## Concurrent and Thread Boundary Testing

### Null and Race Conditions

```java
import java.util.concurrent.*;

class ConcurrentBoundaryTest {

  @Test
  void shouldHandleNullInConcurrentMap() {
    ConcurrentHashMap<String, String> map = new ConcurrentHashMap<>();
    map.put("key", "value");
    assertThat(map.get("nonexistent")).isNull();
  }

  @Test
  void shouldHandleConcurrentModification() {
    List<Integer> list = new CopyOnWriteArrayList<>(List.of(1, 2, 3, 4, 5));
    // Should not throw ConcurrentModificationException
    for (int num : list) {
      if (num == 3) {
        list.add(6);
      }
    }
    assertThat(list).hasSize(6);
  }

  @Test
  void shouldHandleEmptyBlockingQueue() throws InterruptedException {
    BlockingQueue<String> queue = new LinkedBlockingQueue<>();
    assertThat(queue.poll()).isNull();
  }
}
```

## Parameterized Boundary Testing

### Multiple Boundary Cases

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class ParameterizedBoundaryTest {

  @ParameterizedTest
  @CsvSource({
    "null,            false", // null
    "'',              false", // empty
    "'   ',           false", // whitespace
    "a,               true",  // single char
    "abc,             true"   // normal
  })
  void shouldValidateStringBoundaries(String input, boolean expected) {
    boolean result = StringValidator.isValid(input);
    assertThat(result).isEqualTo(expected);
  }

  @ParameterizedTest
  @ValueSource(ints = {Integer.MIN_VALUE, 0, 1, -1, Integer.MAX_VALUE})
  void shouldHandleNumericBoundaries(int value) {
    assertThat(value).isNotNull();
  }
}
```
