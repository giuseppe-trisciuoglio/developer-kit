# Parameterized Boundary Testing Reference

## Multiple Boundary Cases

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

class ParameterizedBoundaryTest {

  @ParameterizedTest
  @CsvSource({
    "null,            false",
    "'',              false",
    "'   ',           false",
    "a,               true",
    "abc,             true"
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

  static Stream<Arguments> edgeCaseProvider() {
    return Stream.of(
      Arguments.of(Integer.MIN_VALUE, "min"),
      Arguments.of(-1, "negative"),
      Arguments.of(0, "zero"),
      Arguments.of(1, "positive"),
      Arguments.of(Integer.MAX_VALUE, "max")
    );
  }

  @ParameterizedTest
  @MethodSource("edgeCaseProvider")
  void shouldTestAllEdgeCases(int value, String description) {
    assertThat(value).isNotNull();
  }
}
```

## Off-By-One Testing

```java
class OffByOneBoundaryTest {

  @ParameterizedTest
  @CsvSource({
    "-1, false",
    "0,  true",
    "1,  true",
    "99, true",
    "100, false",
    "101, false"
  })
  void shouldValidateRangeBoundaries(int value, boolean expected) {
    boolean inRange = value >= 0 && value <= 100;
    assertThat(inRange).isEqualTo(expected);
  }

  @Test
  void shouldHandleArrayIndexOffByOne() {
    int[] array = {1, 2, 3};

    assertThat(array.length).isEqualTo(3);
    assertThat(array[0]).isEqualTo(1);
    assertThat(array[array.length - 1]).isEqualTo(3);
  }
}
```
