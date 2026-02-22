---
name: unit-test-exception-handler
description: Provides patterns for unit testing @ExceptionHandler and @ControllerAdvice for global exception handling. Use when validating error response formatting and HTTP status codes.
category: testing
tags: [junit-5, exception-handler, controller-advice, error-handling, mockmvc]
version: 2.2.0
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing ExceptionHandler and ControllerAdvice

## Overview

This skill provides patterns for unit testing @ExceptionHandler methods and @ControllerAdvice classes using MockMvc. It covers testing exception-to-error-response transformations, HTTP status codes, error message formatting, validation error handling, and custom permission evaluators without full integration test overhead.

## When to Use

Use this skill when:
- Testing @ExceptionHandler methods in @ControllerAdvice
- Testing exception-to-error-response transformations
- Verifying HTTP status codes for different exception types
- Testing error message formatting and localization
- Want fast exception handler tests without full integration tests

Trigger phrases:
- "test controller advice"
- "test exception handler"
- "mockmvc exception tests"
- "validate error response format"

## Instructions

1. **Create test controllers**: Create simple test controllers that throw exceptions to test handler behavior
2. **Register ControllerAdvice**: Use `setControllerAdvice()` when building MockMvc to register exception handlers
3. **Test all exception types**: Verify each @ExceptionHandler method handles its specific exception type
4. **Verify HTTP status codes**: Use @ResponseStatus assertions to verify correct status codes
5. **Test error response structure**: Verify error responses contain all required fields (timestamp, status, error, message)
6. **Test validation errors**: Verify MethodArgumentNotValidException produces field-level error details
7. **Test logging and side effects**: Verify exception handlers log errors or perform other side effects
8. **Use mock controllers**: Throw exceptions from mock controllers to trigger exception handlers

## Examples

## Setup: Exception Handler Testing

### Maven
```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### Gradle
```kotlin
dependencies {
  implementation("org.springframework.boot:spring-boot-starter-web")
  testImplementation("org.springframework.boot:spring-boot-starter-test")
  testImplementation("org.assertj:assertj-core")
}
```

## Basic Pattern: Global Exception Handler

### Create Exception Handler

```java
// Global exception handler
@ControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(ResourceNotFoundException.class)
  @ResponseStatus(HttpStatus.NOT_FOUND)
  public ErrorResponse handleResourceNotFound(ResourceNotFoundException ex) {
    return new ErrorResponse(
      HttpStatus.NOT_FOUND.value(),
      "Resource not found",
      ex.getMessage()
    );
  }

  @ExceptionHandler(ValidationException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ErrorResponse handleValidationException(ValidationException ex) {
    return new ErrorResponse(
      HttpStatus.BAD_REQUEST.value(),
      "Validation failed",
      ex.getMessage()
    );
  }
}

// Error response DTO
public record ErrorResponse(
  int status,
  String error,
  String message
) {}
```

### Unit Test Exception Handler

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class GlobalExceptionHandlerTest {

  @InjectMocks
  private GlobalExceptionHandler exceptionHandler;

  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    mockMvc = MockMvcBuilders
      .standaloneSetup(new TestController())
      .setControllerAdvice(exceptionHandler)
      .build();
  }

  @Test
  void shouldReturnNotFoundWhenResourceNotFoundException() throws Exception {
    mockMvc.perform(get("/api/users/999"))
      .andExpect(status().isNotFound())
      .andExpect(jsonPath("$.status").value(404))
      .andExpect(jsonPath("$.error").value("Resource not found"))
      .andExpect(jsonPath("$.message").value("User not found"));
  }

  @Test
  void shouldReturnBadRequestWhenValidationException() throws Exception {
    mockMvc.perform(post("/api/users")
        .contentType("application/json")
        .content("{\"name\":\"\"}"))
      .andExpect(status().isBadRequest())
      .andExpect(jsonPath("$.status").value(400))
      .andExpect(jsonPath("$.error").value("Validation failed"));
  }
}

// Test controller that throws exceptions
@RestController
@RequestMapping("/api")
class TestController {

  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id) {
    throw new ResourceNotFoundException("User not found");
  }
}
```

For detailed examples covering multiple exception types, error response structure verification, validation error handling (MethodArgumentNotValidException), and exception handlers with custom logic (localization, logging), see [Examples](references/examples.md).

## Best Practices

- **Test all exception handlers** with real exception throws
- **Verify HTTP status codes** for each exception type
- **Test error response structure** to ensure consistency
- **Verify logging** is triggered appropriately
- **Use mock controllers** to throw exceptions in tests
- **Test both happy and error paths**
- **Keep error messages user-friendly** and consistent

## Common Pitfalls

- Not testing the full request path (use MockMvc with controller)
- Forgetting to include `@ControllerAdvice` in MockMvc setup
- Not verifying all required fields in error response
- Testing handler logic instead of exception handling behavior
- Not testing edge cases (null exceptions, unusual messages)

## Constraints and Warnings

- **@ControllerAdvice execution order**: Multiple @ControllerAdvice handlers can be ordered with @Order annotation
- **Exception handler specificity**: More specific exception types take precedence over generic handlers
- **ResponseStatus required**: Without @ResponseStatus or returning ResponseEntity, status defaults to 200
- **Global vs local handlers**: @ExceptionHandler in @ControllerAdvice is global; in controller it's local to that controller
- **Logging considerations**: Exception handlers should log exceptions at appropriate levels before returning responses
- **Message localization**: When using localized messages, test with different locales
- **Security context**: Exception handlers have access to security context for authentication/authorization errors

## Troubleshooting

**Exception handler not invoked**: Ensure controller is registered with MockMvc and actually throws the exception.

**JsonPath matchers not matching**: Use `.andDo(print())` to see actual response structure.

**Status code mismatch**: Verify `@ResponseStatus` annotation on handler method.

## References

- [Spring ControllerAdvice Documentation](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/bind/annotation/ControllerAdvice.html)
- [Spring ExceptionHandler](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/bind/annotation/ExceptionHandler.html)
- [MockMvc Testing](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/test/web/servlet/MockMvc.html)
