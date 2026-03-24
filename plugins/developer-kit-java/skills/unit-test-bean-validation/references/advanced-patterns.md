# Advanced Validation Patterns Reference

## Validation Groups

### Defining Groups

```java
public interface CreateValidation {}
public interface UpdateValidation {}
public interface AdminValidation {}
```

### Using Groups in DTOs

```java
class UserDto {
  @NotNull(groups = CreateValidation.class)
  private String name;

  @Min(value = 0, groups = {CreateValidation.class, UpdateValidation.class})
  private int age;
}
```

### Testing Groups

```java
class ValidationGroupsTest extends BaseValidationTest {

  @Test
  void shouldRequireNameOnlyDuringCreation() {
    UserDto user = new UserDto(null, 25);

    Set<ConstraintViolation<UserDto>> violations =
        validator.validate(user, CreateValidation.class);

    assertThat(violations)
      .extracting(ConstraintViolation::getPropertyPath)
      .extracting(Path::toString)
      .contains("name");
  }

  @Test
  void shouldAllowNullNameDuringUpdate() {
    UserDto user = new UserDto(null, 25);
    assertThat(validator.validate(user, UpdateValidation.class)).isEmpty();
  }

  @Test
  void shouldValidateMultipleGroups() {
    UserDto user = new UserDto("Alice", -5);
    Set<ConstraintViolation<UserDto>> violations =
        validator.validate(user, CreateValidation.class, UpdateValidation.class);
    assertThat(violations).isNotEmpty();
  }
}
```

## Parameterized Tests

### Email Validation

```java
class EmailValidationTest extends BaseValidationTest {

  @ParameterizedTest
  @ValueSource(strings = {
    "user@example.com",
    "john.doe+tag@example.co.uk",
    "admin@subdomain.example.com"
  })
  void shouldAcceptValidEmails(String email) {
    UserDto user = new UserDto("Alice", email);
    assertThat(validator.validate(user)).isEmpty();
  }

  @ParameterizedTest
  @ValueSource(strings = {
    "invalid-email", "user@", "@example.com", "user name@example.com"
  })
  void shouldRejectInvalidEmails(String email) {
    UserDto user = new UserDto("Alice", email);
    assertThat(validator.validate(user)).isNotEmpty();
  }
}
```

### Multiple Parameters

```java
class RangeValidationTest extends BaseValidationTest {

  @ParameterizedTest
  @CsvSource({
    "0, 100, true",
    "-1, 100, false",
    "0, 0, false",
    "50, 100, true"
  })
  void shouldValidateRange(int min, int max, boolean shouldPass) {
    RangeDto dto = new RangeDto(min, max);
    var violations = validator.validate(dto);
    assertThat(violations.isEmpty()).isEqualTo(shouldPass);
  }
}
```

## Debugging Failed Tests

### When Tests Fail

1. **Check violation count**: `assertThat(violations).hasSize(n)`
2. **Inspect property path**: `violation.getPropertyPath().toString()`
3. **Verify message**: `violation.getMessage()`
4. **Check invalid value**: `violation.getInvalidValue()`

```java
@Test
void debugFailedValidation() {
  UserDto user = new UserDto("", "invalid");

  Set<ConstraintViolation<UserDto>> violations = validator.validate(user);

  // Debug output
  violations.forEach(v -> System.out.println(
    v.getPropertyPath() + ": " + v.getMessage()
  ));

  assertThat(violations).hasSize(2);
}
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ConstraintViolation` null | Object is valid or constraint doesn't fire | Check annotation parameters |
| Wrong property path | Wrong field annotated | Verify `@Constraint(validatedBy=)` |
| Null passes validation | Constraint allows null | Add `@NotNull` |
| Multiple violations | Multiple constraints fail | Use `hasSize()` to verify count |
