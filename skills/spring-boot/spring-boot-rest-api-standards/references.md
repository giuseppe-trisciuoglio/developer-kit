# Spring Boot REST API Standards - References

Complete reference for REST API development with Spring Boot.

## HTTP Methods and Status Codes Reference

### HTTP Methods

| Method | Idempotent | Safe | Purpose | Typical Status |
|--------|-----------|------|---------|----------------|
| GET | Yes | Yes | Retrieve resource | 200, 304, 404 |
| POST | No | No | Create resource | 201, 400, 409 |
| PUT | Yes | No | Replace resource | 200, 204, 404 |
| PATCH | No | No | Partial update | 200, 204, 400 |
| DELETE | Yes | No | Remove resource | 204, 404 |
| HEAD | Yes | Yes | Like GET, no body | 200, 304, 404 |
| OPTIONS | Yes | Yes | Describe communication options | 200 |

### HTTP Status Codes

**2xx Success:**
- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST (include Location header)
- `202 Accepted` - Async processing accepted
- `204 No Content` - Successful DELETE or POST with no content
- `206 Partial Content` - Range request successful

**3xx Redirection:**
- `301 Moved Permanently` - Resource permanently moved
- `304 Not Modified` - Cache valid, use local copy
- `307 Temporary Redirect` - Temporary redirect

**4xx Client Errors:**
- `400 Bad Request` - Invalid format or parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Constraint violation or conflict
- `422 Unprocessable Entity` - Validation failed (semantic error)

**5xx Server Errors:**
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - External service unavailable
- `503 Service Unavailable` - Server temporarily down

## Spring Web Annotations Reference

### Request Mapping Annotations

```java
@RestController              // Combines @Controller + @ResponseBody
@RequestMapping("/api")      // Base URL path
@GetMapping                  // GET requests
@PostMapping                 // POST requests
@PutMapping                  // PUT requests
@PatchMapping                // PATCH requests
@DeleteMapping               // DELETE requests
```

### Parameter Binding Annotations

```java
@PathVariable                // URL path variable /{id}
@RequestParam                // Query string parameter ?page=0
@RequestParam(required=false) // Optional parameter
@RequestParam(defaultValue="10") // Default value
@RequestBody                 // Request body JSON/XML
@RequestHeader               // HTTP header value
@CookieValue                 // Cookie value
@MatrixVariable              // Matrix variable ;color=red
@Valid                       // Enable validation
```

### Response Annotations

```java
@ResponseBody                // Serialize to response body
@ResponseStatus(status=HttpStatus.CREATED)  // HTTP status
ResponseEntity<T>            // Full response control
ResponseEntity.ok(body)      // 200 OK
ResponseEntity.created(uri).body(body)  // 201 Created
ResponseEntity.noContent().build()      // 204 No Content
ResponseEntity.notFound().build()       // 404 Not Found
```

## DTO Patterns Reference

### Request DTO (using Records)

```java
public record CreateProductRequest(
    @NotBlank(message = "Name required") String name,
    @NotNull @DecimalMin("0.01") BigDecimal price,
    String description,
    @NotNull @Min(0) Integer stock
) {}
```

### Response DTO (using Records)

```java
public record ProductResponse(
    Long id,
    String name,
    BigDecimal price,
    Integer stock,
    LocalDateTime createdAt,
    LocalDateTime updatedAt
) {}
```

### Update DTO

```java
public record UpdateProductRequest(
    @NotBlank String name,
    @NotNull @DecimalMin("0.01") BigDecimal price,
    String description
) {}
```

## Validation Annotations Reference

### Common Constraints

```java
@NotNull                     // Cannot be null
@NotEmpty                    // Collection/String cannot be empty
@NotBlank                    // String cannot be null/blank
@Size(min=1, max=255)       // Length validation
@Min(value=1)               // Minimum numeric value
@Max(value=100)             // Maximum numeric value
@Positive                   // Must be positive
@Negative                   // Must be negative
@Email                      // Valid email format
@Pattern(regexp="...")      // Regex validation
@Future                     // Date must be future
@Past                       // Date must be past
@Digits(integer=5, fraction=2)  // Numeric precision
@DecimalMin("0.01")         // Decimal minimum
@DecimalMax("9999.99")      // Decimal maximum
```

### Custom Validation

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UniqueEmailValidator.class)
public @interface UniqueEmail {
    String message() default "Email already exists";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class UniqueEmailValidator implements ConstraintValidator<UniqueEmail, String> {
    @Autowired
    private UserRepository repository;

    @Override
    public boolean isValid(String email, ConstraintValidatorContext context) {
        return !repository.existsByEmail(email);
    }
}
```

## Pagination Reference

### Pageable Request Building

```java
// Basic pagination
Pageable pageable = PageRequest.of(page, size);

// With sorting
Sort sort = Sort.by("createdAt").descending();
Pageable pageable = PageRequest.of(page, size, sort);

// Multiple sort fields
Sort sort = Sort.by("status").ascending()
    .and(Sort.by("createdAt").descending());
Pageable pageable = PageRequest.of(page, size, sort);
```

### Pagination Response Format

```json
{
  "content": [
    { "id": 1, "name": "Product 1" },
    { "id": 2, "name": "Product 2" }
  ],
  "pageable": {
    "offset": 0,
    "pageNumber": 0,
    "pageSize": 20,
    "paged": true
  },
  "totalElements": 100,
  "totalPages": 5,
  "last": false,
  "size": 20,
  "number": 0,
  "numberOfElements": 20,
  "first": true,
  "empty": false
}
```

## Error Response Format

### Standardized Error Response

```json
{
  "status": 400,
  "error": "Bad Request",
  "message": "Validation failed: name: Name is required",
  "path": "/api/v1/products",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Global Exception Handler Pattern

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex) {
        // Handle validation errors
    }
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex) {
        // Handle not found
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception ex) {
        // Handle generic exceptions
    }
}
```

## Content Negotiation

### Accept Header Examples

```
Accept: application/json              # JSON response
Accept: application/xml               # XML response
Accept: application/vnd.api+json     # JSON:API standard
Accept: text/csv                     # CSV response
```

### Controller Implementation

```java
@GetMapping(produces = {MediaType.APPLICATION_JSON_VALUE, "application/xml"})
public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
    // Supports both JSON and XML
    return ResponseEntity.ok(productService.findById(id));
}
```

## Pagination Best Practices

```java
// Limit maximum page size
@GetMapping
public ResponseEntity<Page<ProductResponse>> getAll(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") 
        @Max(value = 100, message = "Max page size is 100") int size) {
    
    Pageable pageable = PageRequest.of(page, size);
    return ResponseEntity.ok(productService.findAll(pageable));
}
```

## Maven Dependencies

```xml
<!-- Spring Web -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- Validation -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>

<!-- Data JPA (for Pageable) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<!-- Lombok -->
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
</dependency>
```

## Testing REST APIs

### MockMvc Testing

```java
@SpringBootTest
@AutoConfigureMockMvc
class ProductControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void shouldCreateProduct() throws Exception {
        mockMvc.perform(post("/api/v1/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"Test\",\"price\":10.00}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists());
    }
}
```

### TestRestTemplate Testing

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ProductIntegrationTest {
    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void shouldFetchProduct() {
        ResponseEntity<ProductResponse> response = restTemplate.getForEntity(
            "/api/v1/products/1", ProductResponse.class);
        
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }
}
```

## Related Skills

- **spring-boot-crud-patterns/SKILL.md** - CRUD operations following REST principles
- **spring-boot-dependency-injection/SKILL.md** - Dependency injection in controllers
- **spring-boot-test-patterns/SKILL.md** - Testing REST APIs
- **spring-boot-exception-handling/SKILL.md** - Global error handling

## External Resources

### Official Documentation
- [Spring Web MVC Documentation](https://docs.spring.io/spring-framework/reference/web/webmvc.html)
- [Spring REST Documentation](https://spring.io/guides/gs/rest-service/)
- [REST API Best Practices](https://restfulapi.net/)

### Related Standards
- [JSON:API Specification](https://jsonapi.org/)
- [OpenAPI Specification](https://www.openapis.org/)
- [RFC 7231 - HTTP Semantics](https://tools.ietf.org/html/rfc7231)

### Books
- "RESTful Web Services" by Leonard Richardson & Sam Ruby
- "Spring in Action" (latest edition)
