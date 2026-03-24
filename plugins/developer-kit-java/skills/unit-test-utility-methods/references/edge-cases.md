# Edge Cases and Boundary Testing

## Numeric Boundary Conditions

```java
class MathUtilsEdgeCasesTest {

    @Test
    void shouldHandleMaxInteger() {
        assertThat(MathUtils.increment(Integer.MAX_VALUE)).isEqualTo(Integer.MAX_VALUE);
    }

    @Test
    void shouldHandleMinInteger() {
        assertThat(MathUtils.decrement(Integer.MIN_VALUE)).isEqualTo(Integer.MIN_VALUE);
    }

    @Test
    void shouldHandleLargeNumbers() {
        BigDecimal result = MathUtils.add(
            new BigDecimal("999999999999.99"),
            new BigDecimal("0.01")
        );
        assertThat(result).isEqualTo(new BigDecimal("1000000000000.00"));
    }

    @Test
    void shouldHandleFloatingPointPrecision() {
        assertThat(MathUtils.multiply(0.1, 0.2))
            .isCloseTo(0.02, within(0.0001));
    }
}
```

## String Edge Cases

```java
class StringUtilsEdgeCasesTest {

    @Test
    void shouldHandleNullInput() {
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

    @Test
    void shouldHandleUnicodeCharacters() {
        assertThat(StringUtils.capitalize("über")).isEqualTo("Über");
    }

    @Test
    void shouldHandleOnlyWhitespace() {
        assertThat(StringUtils.trim("   ")).isEmpty();
    }
}
```

## Collection Edge Cases

```java
class CollectionUtilsEdgeCasesTest {

    @Test
    void shouldReturnEmptyForNullInput() {
        assertThat(CollectionUtils.filter(null, n -> true)).isEmpty();
    }

    @Test
    void shouldReturnEmptyForNoMatches() {
        List<Integer> numbers = List.of(1, 3, 5);
        assertThat(CollectionUtils.filter(numbers, n -> n % 2 == 0)).isEmpty();
    }

    @Test
    void shouldHandleEmptyCollection() {
        assertThat(CollectionUtils.join(List.of(), "-")).isEmpty();
    }

    @Test
    void shouldHandleSingleElement() {
        assertThat(CollectionUtils.join(List.of("a"), "-")).isEqualTo("a");
    }
}
```

## Validation Edge Cases

```java
class ValidatorUtilsEdgeCasesTest {

    @Test
    void shouldRejectEmptyEmail() {
        assertThat(ValidatorUtils.isValidEmail("")).isFalse();
    }

    @Test
    void shouldRejectNullEmail() {
        assertThat(ValidatorUtils.isValidEmail(null)).isFalse();
    }

    @Test
    void shouldHandleLongStrings() {
        String longString = "a".repeat(10000);
        assertThat(StringUtils.truncate(longString, 100)).hasSize(100);
    }

    @Test
    void shouldHandleSpecialCharactersInUrls() {
        assertThat(ValidatorUtils.isValidUrl("https://example.com/path?query=value"))
            .isTrue();
    }
}
```

## Floating Point Precision Rules

| Operation | Use | Example |
|-----------|-----|---------|
| Addition | `isCloseTo(delta)` | `isCloseTo(0.3, within(0.001))` |
| Comparison | `isEqualTo()` | Use `BigDecimal` for exact decimals |
| Percentage | Tolerance-based | `isCloseTo(expected, within(0.01))` |
