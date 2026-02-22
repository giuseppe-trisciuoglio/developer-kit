---
name: unit-test-bean-validation
description: Provides patterns for unit testing Jakarta Bean Validation (@Valid, @NotNull, @Min, @Max, etc.) with custom validators and constraint violations. Validates logic without Spring context. Use when ensuring data integrity and validation rules are correct.
category: testing
tags: [junit-5, validation, bean-validation, jakarta-validation, constraints]
version: 2.2.0
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Bean Validation and Custom Validators

## Overview

Patterns for unit testing Jakarta Bean Validation annotations and custom validator implementations using JUnit 5. Covers built-in constraints (@NotNull, @Email, @Min, @Max), custom validators, cross-field validation, validation groups, and parameterized testing.

## When to Use

- Testing Jakarta Bean Validation (@NotNull, @Email, @Min, etc.)
- Testing custom @Constraint validators
- Verifying constraint violation error messages
- Testing cross-field validation logic
- Want fast validation tests without Spring context

## Instructions

1. **Add dependencies**: jakarta.validation-api and hibernate-validator
2. **Create Validator**: `Validation.buildDefaultValidatorFactory().getValidator()` in @BeforeEach
3. **Test valid scenarios**: Verify valid objects pass without violations
4. **Test each constraint**: Focused tests for individual validation rules
5. **Extract violation details**: Assert property path, message, and invalid value
6. **Test custom validators**: Dedicated tests for each custom constraint
7. **Use parameterized tests**: @ParameterizedTest for multiple invalid inputs
8. **Test validation groups**: Verify conditional validation

## Examples

### Basic Validation Test

```java
class UserValidationTest {
    private Validator validator;

    @BeforeEach
    void setUp() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    @Test
    void shouldPassWithValidUser() {
        Set<ConstraintViolation<User>> violations = validator.validate(
            new User("Alice", "alice@example.com", 25));
        assertThat(violations).isEmpty();
    }

    @Test
    void shouldFailWhenNameIsNull() {
        Set<ConstraintViolation<User>> violations = validator.validate(
            new User(null, "alice@example.com", 25));
        assertThat(violations).hasSize(1)
            .extracting(ConstraintViolation::getMessage)
            .contains("must not be blank");
    }
}
```

### Custom Validator Test

```java
@Test
void shouldAcceptValidPhoneNumber() {
    Set<ConstraintViolation<Contact>> violations = validator.validate(
        new Contact("Alice", "555-123-4567"));
    assertThat(violations).isEmpty();
}

@Test
void shouldRejectInvalidFormat() {
    Set<ConstraintViolation<Contact>> violations = validator.validate(
        new Contact("Alice", "5551234567"));
    assertThat(violations).extracting(ConstraintViolation::getMessage)
        .contains("invalid phone number format");
}
```

### Parameterized Email Validation

```java
@ParameterizedTest
@ValueSource(strings = {"invalid-email", "user@", "@example.com"})
void shouldRejectInvalidEmails(String email) {
    Set<ConstraintViolation<UserDto>> violations = validator.validate(
        new UserDto("Alice", email));
    assertThat(violations).isNotEmpty();
}
```

### Validation Groups

```java
@Test
void shouldRequireNameOnlyDuringCreation() {
    UserDto user = new UserDto(null, 25);
    Set<ConstraintViolation<UserDto>> violations =
        validator.validate(user, CreateValidation.class);
    assertThat(violations).extracting(v -> v.getPropertyPath().toString())
        .contains("name");
}

@Test
void shouldAllowNullNameDuringUpdate() {
    Set<ConstraintViolation<UserDto>> violations =
        validator.validate(new UserDto(null, 25), UpdateValidation.class);
    assertThat(violations).isEmpty();
}
```

## Best Practices

- Validate at unit test level before testing service/controller layers
- Test both valid and invalid cases for every constraint
- Test edge cases: null, empty string, whitespace-only strings
- Keep validator logic simple; complex validation belongs in service tests
- Custom validators must be stateless

## Constraints and Warnings

- Most constraints ignore null by default (except @NotNull); combine with @NotNull for mandatory fields
- Validator instances are thread-safe and can be shared
- Use @Valid on nested objects to enable cascading validation
- Validation has overhead; don't over-validate in critical paths

## References

- [Jakarta Bean Validation Spec](https://jakarta.ee/specifications/bean-validation/)
- [Hibernate Validator Documentation](https://hibernate.org/validator/)
