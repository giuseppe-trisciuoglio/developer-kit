# Exception Documentation

## Global Exception Handler

### Comprehensive Exception Handler

```java
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import io.swagger.v3.oas.annotations.Operation;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BookNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    @Operation(hidden = true)
    public ErrorResponse handleBookNotFound(BookNotFoundException ex) {
        return new ErrorResponse("BOOK_NOT_FOUND", ex.getMessage());
    }

    @ExceptionHandler(ValidationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    @Operation(hidden = true)
    public ErrorResponse handleValidation(ValidationException ex) {
        return new ErrorResponse("VALIDATION_ERROR", ex.getMessage());
    }

    @ExceptionHandler(AccessDeniedException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    @Operation(hidden = true)
    public ErrorResponse handleAccessDenied(AccessDeniedException ex) {
        return new ErrorResponse("ACCESS_DENIED", "Insufficient permissions");
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    @Operation(hidden = true)
    public ErrorResponse handleGeneric(Exception ex) {
        return new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred");
    }
}
```

### Error Response Schema

```java
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import java.util.List;

@Schema(description = "Standard error response")
public record ErrorResponse(
    @Schema(description = "Error code", example = "BOOK_NOT_FOUND")
    String code,

    @Schema(description = "Human-readable error message", example = "Book with ID 123 not found")
    String message,

    @Schema(description = "Additional error details")
    List<ValidationError> details,

    @Schema(description = "Error timestamp", example = "2024-01-15T10:30:00Z")
    LocalDateTime timestamp,

    @Schema(description = "Request path that caused the error", example = "/api/books/123")
    String path
) {
    public ErrorResponse(String code, String message) {
        this(code, message, List.of(), LocalDateTime.now(), "");
    }

    @Schema(description = "Validation error detail")
    public record ValidationError(
        @Schema(description = "Field name", example = "title")
        String field,

        @Schema(description = "Error message", example = "Title is required")
        String message
    ) {}
}
```

## Document-Specific Error Responses

### API Response with Error Codes

```java
@Operation(
    summary = "Get book by ID",
    responses = {
        @ApiResponse(
            responseCode = "200",
            description = "Book found",
            content = @Content(schema = @Schema(implementation = Book.class))
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Book not found",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Unauthorized",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Internal server error",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
        )
    }
)
@GetMapping("/{id}")
public Book getBook(@PathVariable Long id) {
    return repository.findById(id).orElseThrow(() -> new BookNotFoundException(id));
}
```

### Custom Error Response Examples

```java
@Operation(
    summary = "Create book",
    responses = {
        @ApiResponse(
            responseCode = "201",
            description = "Book created"
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Validation failed",
            content = @Content(
                schema = @Schema(implementation = ErrorResponse.class),
                examples = @ExampleObject(
                    value = """
                    {
                        "code": "VALIDATION_ERROR",
                        "message": "Validation failed",
                        "details": [
                            {"field": "title", "message": "Title is required"},
                            {"field": "isbn", "message": "Invalid ISBN format"}
                        ],
                        "timestamp": "2024-01-15T10:30:00Z",
                        "path": "/api/books"
                    }
                    """
                )
            )
        )
    }
)
@PostMapping
public Book createBook(@Valid @RequestBody Book book) {
    return repository.save(book);
}
```

## Problem Details for HTTP APIs

### RFC 7807 Problem Details

```java
@Schema(description = "RFC 7807 Problem Details")
public record ProblemDetail(
    @Schema(description = "Problem type URI", example = "https://example.com/probs/book-not-found")
    String type,

    @Schema(description = "Short problem title", example = "Book Not Found")
    String title,

    @Schema(description = "HTTP status code", example = "404")
    int status,

    @Schema(description = "Detailed problem description", example = "Book with ID 123 does not exist")
    String detail,

    @Schema(description = "Instance identifier", example = "/api/books/123")
    String instance
) {}

@RestControllerAdvice
public class ProblemDetailExceptionHandler {

    @ExceptionHandler(BookNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    @Operation(hidden = true)
    public ProblemDetail handleNotFound(BookNotFoundException ex) {
        return new ProblemDetail(
            "https://example.com/probs/book-not-found",
            "Book Not Found",
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            "/api/books/" + ex.getId()
        );
    }
}
```

## Document Constraint Violations

### Bean Validation Error Documentation

```java
@Schema(description = "Constraint violation detail")
public record ConstraintViolation(
    @Schema(description = "Invalid field", example = "title")
    String field,

    @Schema(description = "Constraint that failed", example = "NotBlank")
    String constraint,

    @Schema(description = "Error message", example = "must not be blank")
    String message,

    @Schema(description = "Invalid value", example = "null")
    String rejectedValue
) {}

@Schema(description = "Validation error response")
public record ValidationErrorResponse(
    @Schema(description = "Error code", example = "VALIDATION_FAILED")
    String code,

    @Schema(description = "Validation errors")
    List<ConstraintViolation> violations,

    @Schema(description = "Total number of violations", example = "2")
    int violationCount,

    @Schema(description = "Timestamp", example = "2024-01-15T10:30:00Z")
    LocalDateTime timestamp
) {}
```

## Business Exception Documentation

### Custom Business Exceptions

```java
public class InsufficientStockException extends RuntimeException {
    private final Long bookId;
    private final int requested;
    private final int available;

    public InsufficientStockException(Long bookId, int requested, int available) {
        super(String.format("Insufficient stock for book %d: requested=%d, available=%d",
            bookId, requested, available));
        this.bookId = bookId;
        this.requested = requested;
        this.available = available;
    }

    // Getters...
}

@ExceptionHandler(InsufficientStockException.class)
@ResponseStatus(HttpStatus.CONFLICT)
@Operation(hidden = true)
public ErrorResponse handleInsufficientStock(InsufficientStockException ex) {
    return new ErrorResponse(
        "INSUFFICIENT_STOCK",
        String.format("Only %d copies available, %d requested", ex.getAvailable(), ex.getRequested()),
        Map.of(
            "bookId", ex.getBookId(),
            "requested", ex.getRequested(),
            "available", ex.getAvailable()
        )
    );
}
```

## Exception Handling Best Practices

1. **Hide exception handlers from docs**: Use `@Operation(hidden = true)`
2. **Document error responses**: Include all possible error codes in `@ApiResponse`
3. **Use consistent error format**: Standard error response structure
4. **Provide actionable messages**: Help users understand and fix errors
5. **Include request ID**: For tracing and support
6. **Don't expose sensitive data**: Sanitize exception messages
7. **Use appropriate HTTP status codes**: Follow HTTP semantics

```java
@Schema(description = "Error response with request tracking")
public record ErrorResponse(
    String code,
    String message,
    Object details,
    LocalDateTime timestamp,
    String path,
    @Schema(description = "Request ID for support", example = "abc-123-xyz")
    String requestId
) {}
```
