# Bean Validation Test Examples

## Example 1: Built-in constraints with violation detail assertions

```java
package com.example.validation;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

class UserRegistrationValidationTest {

    private Validator validator;

    @BeforeEach
    void setUp() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    @Test
    void shouldPassWhenRequestValid() {
        UserRegistration request = new UserRegistration("Alice", "alice@example.com", 21);

        Set<ConstraintViolation<UserRegistration>> violations = validator.validate(request);

        assertThat(violations).isEmpty();
    }

    @Test
    void shouldFailWhenEmailInvalidAndAgeBelowMinimum() {
        UserRegistration request = new UserRegistration("Alice", "invalid", 17);

        Set<ConstraintViolation<UserRegistration>> violations = validator.validate(request);

        assertThat(violations).hasSize(2);
        assertThat(violations)
                .extracting(v -> v.getPropertyPath().toString())
                .containsExactlyInAnyOrder("email", "age");
    }

    record UserRegistration(
            @NotBlank String name,
            @Email String email,
            @NotNull @Min(18) Integer age
    ) {
    }
}
```

## Example 2: Custom constraint annotation and validator

```java
package com.example.validation;

import jakarta.validation.Constraint;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Payload;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.lang.annotation.Documented;
import java.lang.annotation.Retention;
import java.lang.annotation.Target;
import java.util.Set;

import static java.lang.annotation.ElementType.FIELD;
import static java.lang.annotation.RetentionPolicy.RUNTIME;
import static org.assertj.core.api.Assertions.assertThat;

class ProductCodeConstraintTest {

    private Validator validator;

    @BeforeEach
    void setUp() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    @Test
    void shouldAcceptUppercaseProductCode() {
        ProductDto dto = new ProductDto("PRD-1234");

        Set<ConstraintViolation<ProductDto>> violations = validator.validate(dto);

        assertThat(violations).isEmpty();
    }

    @Test
    void shouldRejectInvalidProductCodeFormat() {
        ProductDto dto = new ProductDto("prd-1234");

        Set<ConstraintViolation<ProductDto>> violations = validator.validate(dto);

        assertThat(violations).hasSize(1);
        assertThat(violations.iterator().next().getMessage()).isEqualTo("must match pattern PRD-1234");
    }

    record ProductDto(@ProductCode String code) {
    }

    @Documented
    @Target(FIELD)
    @Retention(RUNTIME)
    @Constraint(validatedBy = ProductCodeValidator.class)
    @interface ProductCode {
        String message() default "must match pattern PRD-1234";
        Class<?>[] groups() default {};
        Class<? extends Payload>[] payload() default {};
    }

    static class ProductCodeValidator implements ConstraintValidator<ProductCode, String> {
        @Override
        public boolean isValid(String value, ConstraintValidatorContext context) {
            if (value == null) {
                return true;
            }
            return value.matches("PRD-\\d{4}");
        }
    }
}
```

## Example 3: Validation groups for create and update flows

```java
package com.example.validation;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

class ValidationGroupsTest {

    private Validator validator;

    @BeforeEach
    void setUp() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    @Test
    void shouldRequireIdOnlyForUpdateGroup() {
        AccountCommand command = new AccountCommand(null, "Alice");

        Set<ConstraintViolation<AccountCommand>> createViolations = validator.validate(command, OnCreate.class);
        Set<ConstraintViolation<AccountCommand>> updateViolations = validator.validate(command, OnUpdate.class);

        assertThat(createViolations).isEmpty();
        assertThat(updateViolations)
                .extracting(v -> v.getPropertyPath().toString())
                .containsExactly("id");
    }

    interface OnCreate {
    }

    interface OnUpdate {
    }

    record AccountCommand(
            @NotNull(groups = OnUpdate.class) Long id,
            @NotBlank(groups = {OnCreate.class, OnUpdate.class}) String name
    ) {
    }
}
```
