---
name: unit-test-exception-handler
description: Provides patterns for unit testing `@ExceptionHandler` and `@ControllerAdvice` in Spring Boot applications. Validates error response formatting, mocks exceptions, verifies HTTP status codes, tests field-level validation errors, and asserts custom error payloads. Use when writing Spring exception handler tests, REST API error tests, or mocking controller advice.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing ExceptionHandler and ControllerAdvice

## Overview

This skill provides patterns for writing unit tests for Spring Boot exception handlers. It covers testing `@ExceptionHandler` methods in `@ControllerAdvice` classes using MockMvc, including HTTP status assertions, JSON response validation, field-level validation error testing, and mocking handler dependencies.

## When to Use

- Writing unit tests for `@ExceptionHandler` methods
- Testing `@ControllerAdvice` global exception handling
- Validating REST API error response formatting
- Mocking exceptions in controller tests
- Testing field-level validation error responses
- Asserting custom error payloads and HTTP status codes

## Instructions

1. **Create a test controller** that throws specific exceptions to trigger each `@ExceptionHandler`
2. **Register ControllerAdvice** via `setControllerAdvice()` on `MockMvcBuilders.standaloneSetup()`
3. **Assert HTTP status codes** with `.andExpect(status().isXxx())`
4. **Verify error response fields** using `jsonPath("$.field")` matchers
5. **Test validation errors** by sending invalid payloads and checking `MethodArgumentNotValidException` produces field-level details
6. **Debug failures** with `.andDo(print())` — if handler not invoked, verify `setControllerAdvice()` is called and exception type matches

## Examples

### Exception Handler and Error DTO

```java
@ControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(ResourceNotFoundException.class)
  @ResponseStatus(HttpStatus.NOT_FOUND)
  public ErrorResponse handleNotFound(ResourceNotFoundException ex) {
    return new ErrorResponse(404, "Not Found", ex.getMessage());
  }

  @ExceptionHandler(ValidationException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ErrorResponse handleValidation(ValidationException ex) {
    return new ErrorResponse(400, "Bad Request", ex.getMessage());
  }

  @ExceptionHandler(MethodArgumentNotValidException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ValidationErrorResponse handleMethodArgumentNotValid(MethodArgumentNotValidException ex) {
    Map<String, String> errors = new HashMap<>();
    ex.getBindingResult().getFieldErrors().forEach(e -> errors.put(e.getField(), e.getDefaultMessage()));
    return new ValidationErrorResponse(400, "Validation Failed", errors);
  }
}

public record ErrorResponse(int status, String error, String message) {}
public record ValidationErrorResponse(int status, String error, Map<String, String> errors) {}
```

### Unit Test

```java
@ExtendWith(MockitoExtension.class)
class GlobalExceptionHandlerTest {

  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    GlobalExceptionHandler handler = new GlobalExceptionHandler();
    mockMvc = MockMvcBuilders.standaloneSetup(new TestController())
        .setControllerAdvice(handler)
        .build();
  }

  @Test
  void shouldReturn404WhenResourceNotFound() throws Exception {
    mockMvc.perform(get("/api/users/999"))
        .andExpect(status().isNotFound())
        .andExpect(jsonPath("$.status").value(404))
        .andExpect(jsonPath("$.error").value("Not Found"))
        .andExpect(jsonPath("$.message").value("User not found"));
  }

  @Test
  void shouldReturn400WithFieldErrorsOnValidationFailure() throws Exception {
    mockMvc.perform(post("/api/users")
        .contentType("application/json")
        .content("{\"name\":\"\",\"email\":\"invalid\"}"))
        .andExpect(status().isBadRequest())
        .andExpect(jsonPath("$.status").value(400))
        .andExpect(jsonPath("$.errors.name").value("must not be blank"))
        .andExpect(jsonPath("$.errors.email").value("must be a valid email"));
  }
}

@RestController
@RequestMapping("/api")
class TestController {
  @GetMapping("/users/{id}") public User getUser(@PathVariable Long id) {
    throw new ResourceNotFoundException("User not found");
  }
  @PostMapping("/users") public User createUser(@RequestBody @Valid User user) {
    throw new ValidationException("Validation failed");
  }
}
```

## Best Practices

- Test each `@ExceptionHandler` method independently with a dedicated exception throw
- Register exactly one `@ControllerAdvice` instance via `setControllerAdvice()` — never skip it
- Assert all fields in the error response body, not just the HTTP status
- For validation errors, verify both the field name key and the error message value
- Use `MockMvcBuilders.standaloneSetup()` for isolated handler tests without full Spring context
- Log assertion failures: chain `.andDo(print())` to print request/response when a test fails

## Common Pitfalls

- Handler not invoked: ensure `setControllerAdvice()` is called on the builder
- JsonPath mismatch: use `.andDo(print())` to inspect actual response structure
- Status is 200: missing `@ResponseStatus` on the handler method
- Duplicate handlers: `@Order` controls precedence; more specific exception types take priority
- Testing handler logic instead of behavior: mock external dependencies, test only the response transformation

## Constraints and Warnings

- **`@ExceptionHandler` specificity**: more specific exception types are matched first; `Exception.class` catches all unmatched types
- **`@ResponseStatus` default**: without `@ResponseStatus` or returning `ResponseEntity`, HTTP status defaults to 200
- **Global vs local scope**: `@ExceptionHandler` in `@ControllerAdvice` is global; declared in a controller it is local only to that controller
- **Logging side effects**: handlers that log should be verified with `verify(mockLogger).logXxx(...)`
- **Localization**: when using `MessageSource`, test with different `Locale` values to confirm message resolution
- **Security context**: `AuthorizationException` handlers can access `SecurityContextHolder` — test that context is correctly evaluated
