---
globs: "**/*.java"
---
# Rule: Java Error Handling

## Context
Establish a consistent error handling strategy for Java applications, ensuring meaningful error reporting, proper exception hierarchies, and clean recovery patterns.

## Guidelines

### Exception Hierarchy
- Create a base `BusinessException` extending `RuntimeException` for all domain-specific errors
- Create specific exceptions for each error domain (e.g., `OrderNotFoundException`, `PaymentDeclinedException`)
- Use **unchecked exceptions** (extending `RuntimeException`) for business logic errors
- Reserve **checked exceptions** only for truly recoverable situations that callers must handle
- Include meaningful error messages and relevant context (IDs, parameters)

### Global Exception Handling
- Use `@RestControllerAdvice` with `@ExceptionHandler` for centralized error handling
- Return a standardized error response format (RFC 7807 Problem Details recommended)
- Map exceptions to appropriate HTTP status codes:
  - `404 Not Found` — resource not found
  - `400 Bad Request` — validation errors, malformed input
  - `409 Conflict` — business rule violations, duplicate resources
  - `422 Unprocessable Entity` — semantically invalid input
  - `500 Internal Server Error` — unexpected errors only

### Error Response Format
```json
{
  "type": "https://api.example.com/errors/order-not-found",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order with ID 12345 was not found",
  "instance": "/api/orders/12345"
}
```

### Best Practices
- **Never** catch and silently swallow exceptions
- **Never** use exceptions for control flow
- Log exceptions at the appropriate level: `ERROR` for unexpected failures, `WARN` for business rule violations
- Include the original exception as the cause when wrapping: `throw new BusinessException("msg", cause)`
- Use `@Valid` and Jakarta Bean Validation instead of manual validation with thrown exceptions
- Prefer `Optional.orElseThrow()` over null checks when fetching entities
- Do not expose stack traces or internal details in API error responses

## Examples

### ✅ Good
```java
// Base exception
public abstract class BusinessException extends RuntimeException {
    protected BusinessException(String message) {
        super(message);
    }
    protected BusinessException(String message, Throwable cause) {
        super(message, cause);
    }
}

// Specific exception
public class OrderNotFoundException extends BusinessException {
    public OrderNotFoundException(Long orderId) {
        super("Order with ID %d was not found".formatted(orderId));
    }
}

// Service usage
public Order findById(Long id) {
    return orderRepository.findById(id)
        .orElseThrow(() -> new OrderNotFoundException(id));
}

// Global handler
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    public ResponseEntity<ProblemDetail> handleNotFound(OrderNotFoundException ex) {
        var problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Order Not Found");
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(problem);
    }
}
```

### ❌ Bad
```java
// Catching and ignoring
try {
    processOrder(order);
} catch (Exception e) {
    // silently ignored
}

// Using exceptions for control flow
try {
    return orderRepository.findById(id).get();
} catch (NoSuchElementException e) {
    return null;  // returning null instead of proper exception
}

// Generic exception without context
throw new RuntimeException("Error");
```
