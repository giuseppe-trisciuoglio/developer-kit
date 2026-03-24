# Custom Validators Testing Reference

## Creating Custom Constraints

### Annotation Definition

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = PhoneNumberValidator.class)
public @interface ValidPhoneNumber {
  String message() default "invalid phone number format";
  Class<?>[] groups() default {};
  Class<? extends Payload>[] payload() default {};
}
```

### Validator Implementation

```java
public class PhoneNumberValidator implements ConstraintValidator<ValidPhoneNumber, String> {
  private static final String PHONE_PATTERN = "^\\d{3}-\\d{3}-\\d{4}$";

  @Override
  public boolean isValid(String value, ConstraintValidatorContext context) {
    if (value == null) return true; // null handled by @NotNull
    return value.matches(PHONE_PATTERN);
  }
}
```

### Unit Test

```java
class PhoneNumberValidatorTest extends BaseValidationTest {

  @Test
  void shouldAcceptValidPhoneNumber() {
    Contact contact = new Contact("Alice", "555-123-4567");
    assertThat(validator.validate(contact)).isEmpty();
  }

  @Test
  void shouldRejectInvalidFormat() {
    Contact contact = new Contact("Alice", "5551234567");
    assertThat(validator.validate(contact))
      .extracting(ConstraintViolation::getMessage)
      .contains("invalid phone number format");
  }

  @Test
  void shouldAllowNull() {
    Contact contact = new Contact("Alice", null);
    assertThat(validator.validate(contact)).isEmpty();
  }
}
```

## Cross-Field Validation

### Password Match Example

```java
@PasswordsMatch
public class ChangePasswordRequest {
  private String newPassword;
  private String confirmPassword;
}

@Constraint(validatedBy = PasswordMatchValidator.class)
public @interface PasswordsMatch {
  String message() default "passwords do not match";
  Class<?>[] groups() default {};
}

public class PasswordMatchValidator
    implements ConstraintValidator<PasswordsMatch, ChangePasswordRequest> {
  @Override
  public boolean isValid(ChangePasswordRequest value, ConstraintValidatorContext context) {
    if (value == null) return true;
    return value.getNewPassword().equals(value.getConfirmPassword());
  }
}
```

### Test

```java
class PasswordValidationTest extends BaseValidationTest {

  @Test
  void shouldPassWhenPasswordsMatch() {
    var request = new ChangePasswordRequest("pass123", "pass123");
    assertThat(validator.validate(request)).isEmpty();
  }

  @Test
  void shouldFailWhenPasswordsDoNotMatch() {
    var request = new ChangePasswordRequest("pass123", "different");
    assertThat(validator.validate(request))
      .extracting(ConstraintViolation::getMessage)
      .contains("passwords do not match");
  }
}
```

## Best Practices

- Keep validators **stateless** - no instance fields
- Return `true` for `null` values - let `@NotNull` handle null checks
- Provide **clear error messages** in annotations
- Test both **valid and invalid** cases
- Verify **property path** and **message** in assertions
