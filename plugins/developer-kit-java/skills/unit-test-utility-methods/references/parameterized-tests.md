# Parameterized Tests for Utility Methods

Use `@ParameterizedTest` for testing multiple similar inputs efficiently.

## ValueSource - Single Parameter

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", "null", "  \t  "})
void shouldConsiderFalsyValuesAsEmpty(String input) {
    assertThat(StringUtils.isEmpty(input)).isTrue();
}
```

## CsvSource - Multiple Parameters

```java
@ParameterizedTest
@CsvSource({
    "hello, HELLO",
    "world, WORLD",
    "test, TEST",
    "123abc, 123ABC"
})
void shouldConvertToUpperCase(String input, String expected) {
    assertThat(StringUtils.toUpperCase(input)).isEqualTo(expected);
}
```

## CsvSource - Email Validation

```java
@ParameterizedTest
@CsvSource({
    "user@example.com, true",
    "test@domain.org, true",
    "invalid-email, false",
    '", false',
    "no-at-sign.com, false"
})
void shouldValidateEmailsCorrectly(String email, boolean expected) {
    assertThat(ValidatorUtils.isValidEmail(email)).isEqualTo(expected);
}
```

## MethodSource - Complex Objects

```java
static Stream<Arguments> stringTransformationCases() {
    return Stream.of(
        Arguments.of("hello", "hello-world", "hello-world"),
        Arguments.of("Hello World", "hello_world", "hello_world"),
        Arguments.of("Test@123", "test123", "test123")
    );
}

@ParameterizedTest
@MethodSource("stringTransformationCases")
void shouldTransformStringsCorrectly(String input, String separator, String expected) {
    assertThat(StringUtils.toSlug(input, separator)).isEqualTo(expected);
}
```

## Null and Empty Sources

```java
@ParameterizedTest
@NullSource
@EmptySource
void shouldHandleNullAndEmpty(String input) {
    assertThat(StringUtils.isBlank(input)).isTrue();
}

@ParameterizedTest
@NullAndEmptySource
void shouldHandleNullEmptyAndBlank(String input) {
    assertThat(StringUtils.isBlank(input)).isTrue();
}
```
