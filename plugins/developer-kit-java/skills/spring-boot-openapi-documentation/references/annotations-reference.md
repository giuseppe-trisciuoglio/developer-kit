# SpringDoc OpenAPI Annotations Reference

## Core Annotations

### `@Tag`

Groups operations under a logical tag.

```java
// Controller level
@RestController
@Tag(name = "Book", description = "Book management APIs")
public class BookController { }

// With external docs
@Tag(
    name = "Public APIs",
    description = "Publicly accessible endpoints",
    externalDocs = @ExternalDocumentation(
        description = "Public API Guide",
        url = "https://docs.example.com/public"
    )
)
```

**Attributes:**
- `name`: Tag identifier
- `description`: Tag description
- `externalDocs`: External documentation reference

### `@Operation`

Describes a single API operation.

```java
@Operation(
    summary = "Get book by ID",
    description = "Retrieve detailed information about a specific book",
    operationId = "getBookById",
    deprecated = false,
    hidden = false,
    tags = {"Book"},
    externalDocs = @ExternalDocumentation(
        description = "Book API Guide",
        url = "https://docs.example.com/book"
    )
)
```

**Attributes:**
- `summary`: Short summary (< 120 chars)
- `description`: Detailed description
- `operationId`: Unique operation ID
- `deprecated`: Mark as deprecated
- `hidden`: Hide from documentation
- `tags`: Override default tags
- `security`: Security requirements
- `responses`: Response definitions
- `parameters`: Parameter definitions

### `@ApiResponse` / `@ApiResponses`

Documents HTTP response codes.

```java
@ApiResponses(value = {
    @ApiResponse(
        responseCode = "200",
        description = "Successfully retrieved",
        content = @Content(
            schema = @Schema(implementation = Book.class),
            mediaType = "application/json"
        )
    ),
    @ApiResponse(
        responseCode = "404",
        description = "Resource not found",
        content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
})
```

**Attributes:**
- `responseCode`: HTTP status code
- `description`: Response description
- `content`: Response content schema
- `headers`: Response headers
- `extensions`: Custom extensions

### `@Parameter`

Documents operation parameters.

```java
public Book getBook(
    @Parameter(
        description = "Book ID",
        required = true,
        example = "1",
        deprecated = false,
        hidden = false,
        allowEmptyValue = false,
        allowReserved = true,
        schema = @Schema(type = "integer", format = "int64"),
        content = @Content(
            schema = @Schema(implementation = Book.class),
            examples = @ExampleObject(value = "1")
        )
    )
    @PathVariable Long id
) { }
```

**Attributes:**
- `description`: Parameter description
- `required`: Whether required (default: inferred)
- `example`: Example value
- `deprecated`: Mark as deprecated
- `hidden`: Hide from docs
- `allowEmptyValue`: Allow empty string
- `allowReserved`: Allow reserved characters (:/?#[]@!$&'()*+,;=)
- `schema`: Parameter schema
- `content`: Parameter content
- `explode`: Explode array/object parameters
- `style`: Parameter style (matrix, label, form, simple, spaceDelimited, pipeDelimited, deepObject)

### `@RequestBody` (OpenAPI)

Documents request body (not to be confused with Spring's `@RequestBody`).

```java
@PostMapping
public Book create(
    @io.swagger.v3.oas.annotations.parameters.RequestBody(
        description = "Book to create",
        required = true,
        content = @Content(
            schema = @Schema(implementation = Book.class),
            examples = @ExampleObject(
                name = "Example Book",
                value = "{\"title\": \"Clean Code\", \"author\": \"Robert C. Martin\"}"
            )
        )
    )
    @Valid @RequestBody Book book
) { }
```

### `@Schema`

Documents model schemas.

```java
@Schema(
    description = "Book entity",
    name = "Book",
    type = "object",
    required = true,
    requiredMode = Schema.RequiredMode.REQUIRED,
    nullable = false,
    readOnly = false,
    writeOnly = false,
    example = "{\"id\": 1, \"title\": \"Clean Code\"}",
    externalDocs = @ExternalDocumentation(
        description = "Book Model Docs",
        url = "https://docs.example.com/book-model"
    ),
    implementation = Book.class,
    not = Book.class,
    oneOf = {Book.class, Magazine.class},
    anyOf = {Book.class, Magazine.class},
    allOf = {BaseEntity.class}
)
public class Book { }

// Field level
@Schema(
    description = "Book title",
    example = "Clean Code",
    required = true,
    minLength = 1,
    maxLength = 200,
    pattern = "^[a-zA-Z0-9 ]*$",
    type = "string",
    format = "string",
    allowableValues = {"Fiction", "Non-Fiction", "Technical"},
    defaultValue = "Untitled",
    accessMode = Schema.AccessMode.READ_ONLY,
    hidden = false
)
private String title;
```

**Attributes:**
- `description`: Field description
- `example`: Example value
- `required`: Whether required
- `type`: Data type (string, number, integer, boolean, array, object)
- `format`: Data format (e.g., email, date, date-time, uuid)
- `minimum`/`maximum`: Numeric constraints
- `minLength`/`maxLength`: String length constraints
- `pattern`: Regex pattern
- `allowableValues`: Enumerated values
- `defaultValue`: Default value
- `readOnly`: Read-only property
- `writeOnly`: Write-only property
- `accessMode`: READ_ONLY, WRITE_ONLY, READ_WRITE
- `hidden`: Hide from documentation
- `implementation`: Implementation class for generics
- `nullable`: Whether nullable
- `deprecated`: Mark as deprecated

### `@SecurityRequirement`

Applies security requirements.

```java
// Controller level
@SecurityRequirement(name = "bearer-jwt")
@RestController
public class BookController { }

// Operation level
@Operation(
    summary = "Secure endpoint",
    security = @SecurityRequirement(name = "bearer-jwt")
)

// Multiple security schemes (OR logic)
@Operation(
    security = {
        @SecurityRequirement(name = "bearer-jwt"),
        @SecurityRequirement(name = "api-key")
    }
)

// No security (override)
@Operation(security = {})
```

### `@Hidden`

Hides from documentation.

```java
// Hide endpoint
@Operation(hidden = true)
@GetMapping("/internal")
public String internal() { }

// Hide entire controller
@Hidden
@RestController
public class InternalController { }
```

### `@ParameterObject`

Documents complex objects as parameters.

```java
@GetMapping("/paginated")
public Page<Book> getPaginated(
    @ParameterObject Pageable pageable
) { }

// Works with Spring Data Pageable, custom filter objects
```

## Validation Annotations (Auto-Documented)

### Standard Bean Validation

```java
@NotNull           // Required field
@NotBlank          // Required, non-empty string
@NotEmpty          // Required, non-empty collection
@Size(min=1, max=200)  // String/collection length
@Min(0)            // Numeric minimum
@Max(1000)         // Numeric maximum
@DecimalMin("0.0") // Decimal minimum
@DecimalMax("999.99") // Decimal maximum
@Pattern(regex="^[A-Z].*") // Regex pattern
@Email             // Email validation
@Past              // Date in the past
@PastOrPresent     // Date today or in the past
@Future            // Date in the future
@FutureOrPresent   // Date today or in the future
@Positive          // Positive number
@PositiveOrZero    // Positive or zero
@Negative          // Negative number
@NegativeOrZero    // Negative or zero
@AssertTrue        // Must be true
@AssertFalse       // Must be false
```

## Advanced Annotations

### `@ArraySchema`

Documents array schemas.

```java
@Schema(
    description = "List of books",
    implementation = Book[].class
)
List<Book> books;

// Using ArraySchema
@ArraySchema(
    schema = @Schema(implementation = Book.class),
    arraySchema = @Schema(
        description = "Array of books",
        minItems = 0,
        maxItems = 100,
        uniqueItems = false
    )
)
List<Book> books;
```

### `@Content`

Detailed content documentation.

```java
@Content(
    mediaType = "application/json",
    schema = @Schema(implementation = Book.class),
    examples = {
        @ExampleObject(
            name = "Example 1",
            value = "{\"title\": \"Clean Code\"}",
            summary = "Simple example"
        ),
        @ExampleObject(
            name = "Example 2",
            value = "{\"title\": \"Effective Java\"}",
            summary = "Another example",
            externalValue = "https://example.com/book-example.json"
        )
    }
)
```

### `@ExampleObject`

Example values.

```java
@ExampleObject(
    name = "Book Example",
    value = "{\"id\": 1, \"title\": \"Clean Code\"}",
    summary = "A simple book example",
    externalValue = "https://example.com/examples/book.json"
)
```

### `@ExternalDocumentation`

External documentation references.

```java
@ExternalDocumentation(
    description = "Detailed API documentation",
    url = "https://docs.example.com/api"
)
```

## Composition Annotations

### `@DiscriminatorObject`

For polymorphic types.

```java
@Schema(
    discriminatorProperty = "type",
    discriminatorMapping = {
        @DiscriminatorMapping(value = "book", schema = Book.class),
        @DiscriminatorMapping(value = "magazine", schema = Magazine.class)
    }
)
public abstract class Publication { }
```

## Annotation Best Practices

1. **Use descriptive summaries**: Keep under 120 characters
2. **Provide detailed descriptions**: Explain behavior and use cases
3. **Document all response codes**: Include 2xx, 4xx, 5xx
4. **Add examples**: Provide realistic request/response examples
5. **Leverage validation**: Let Bean Validation annotations auto-document constraints
6. **Group logically**: Use `@Tag` to organize related endpoints
7. **Be consistent**: Use similar annotation patterns across controllers
8. **Hide internal endpoints**: Use `@Hidden` or separate API groups
9. **Document security**: Apply `@SecurityRequirement` appropriately
10. **Document complex types**: Use `@Schema` for nested objects and generics
