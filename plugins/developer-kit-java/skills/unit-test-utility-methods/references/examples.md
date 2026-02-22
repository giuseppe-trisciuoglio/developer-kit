# Utility Method Testing - Detailed Examples

## Null-Safe Helpers

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
  void shouldReturnFalseWhenNullOrBlank() {
    assertThat(NullSafeUtils.isNotBlank(null)).isFalse();
    assertThat(NullSafeUtils.isNotBlank("   ")).isFalse();
  }
}
```

## Format and Parse Utilities

```java
class FormatUtilsTest {

  @Test
  void shouldFormatCurrency() {
    assertThat(FormatUtils.formatCurrency(1234.56)).isEqualTo("$1,234.56");
  }

  @Test
  void shouldFormatDate() {
    LocalDate date = LocalDate.of(2024, 1, 15);
    assertThat(FormatUtils.formatDate(date, "yyyy-MM-dd")).isEqualTo("2024-01-15");
  }

  @Test
  void shouldSlugifyString() {
    assertThat(FormatUtils.sluggify("Hello World! 123")).isEqualTo("hello-world-123");
  }
}
```

## Validator Utilities

```java
class ValidatorUtilsTest {

  @Test
  void shouldValidateEmail() {
    assertThat(ValidatorUtils.isValidEmail("user@example.com")).isTrue();
    assertThat(ValidatorUtils.isValidEmail("invalid-email")).isFalse();
  }

  @Test
  void shouldValidateUrl() {
    assertThat(ValidatorUtils.isValidUrl("https://example.com")).isTrue();
    assertThat(ValidatorUtils.isValidUrl("not a url")).isFalse();
  }
}
```

## Parameterized Scenarios

```java
class StringUtilsParameterizedTest {

  @ParameterizedTest
  @ValueSource(strings = {"", " ", "   "})
  void shouldTreatBlankAsEmpty(String input) {
    assertThat(StringUtils.isEmpty(input)).isTrue();
  }

  @ParameterizedTest
  @CsvSource({"hello,HELLO", "world,WORLD", "123ABC,123ABC"})
  void shouldConvertToUpperCase(String input, String expected) {
    assertThat(StringUtils.toUpperCase(input)).isEqualTo(expected);
  }
}
```

## Utility with Dependency (Rare Case)

```java
@ExtendWith(MockitoExtension.class)
class DateUtilsTest {

  @Mock
  private Clock clock;

  @Test
  void shouldGetCurrentDateFromClock() {
    when(clock.instant()).thenReturn(Instant.parse("2024-01-15T10:30:00Z"));

    LocalDate result = DateUtils.today(clock);

    assertThat(result).isEqualTo(LocalDate.of(2024, 1, 15));
  }
}
```
