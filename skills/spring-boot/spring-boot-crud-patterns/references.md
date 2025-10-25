# Spring Boot CRUD Patterns - References

Complete API reference and resource documentation for building REST CRUD APIs with Spring Boot.

## RESTful API Operations Reference

### Standard CRUD Operations Mapping

| Operation | HTTP Method | URL Pattern | Status Code | Purpose |
|-----------|------------|------------|------------|---------|
| Create | POST | `/api/v1/products` | 201 Created | Create new resource |
| Read One | GET | `/api/v1/products/{id}` | 200 OK | Retrieve specific resource |
| Read All | GET | `/api/v1/products` | 200 OK | Retrieve all resources |
| Read Paginated | GET | `/api/v1/products?page=0&size=20` | 200 OK | Retrieve paginated resources |
| Update | PUT | `/api/v1/products/{id}` | 200 OK | Replace entire resource |
| Partial Update | PATCH | `/api/v1/products/{id}` | 200 OK | Update specific fields |
| Delete | DELETE | `/api/v1/products/{id}` | 204 No Content | Remove resource |

### HTTP Status Codes Reference

**2xx Success:**
- `200 OK` - Request successful
- `201 Created` - Resource created (include Location header)
- `202 Accepted` - Request accepted for async processing
- `204 No Content` - Successful but no content to return

**3xx Redirection:**
- `301 Moved Permanently` - Resource permanently moved
- `302 Found` - Resource temporarily moved
- `304 Not Modified` - Cached response valid

**4xx Client Errors:**
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Constraint violation (e.g., duplicate)
- `422 Unprocessable Entity` - Validation failed

**5xx Server Errors:**
- `500 Internal Server Error` - Unexpected error
- `502 Bad Gateway` - External service error
- `503 Service Unavailable` - Temporarily unavailable

## Spring Web Annotations Reference

### Controller Annotations

```java
@RestController              // Combines @Controller + @ResponseBody
@Controller                  // MVC controller returning views
@RequestMapping("/api")      // Base URL mapping for all methods
@GetMapping                  // Maps GET requests
@PostMapping                 // Maps POST requests
@PutMapping                  // Maps PUT requests
@PatchMapping                // Maps PATCH requests
@DeleteMapping               // Maps DELETE requests
@ResponseBody                // Serialize return value to response body
@ResponseStatus(HttpStatus.CREATED)  // Set response status code
```

### Request Annotations

```java
@PathVariable String id              // Extract from URL path
@RequestParam(defaultValue="0") int page  // Extract from query string
@RequestParam(required=false) String filter  // Optional parameter
@RequestBody CreateProductRequest    // Deserialize request body
@RequestHeader("Authorization")      // Extract HTTP header
@CookieValue("sessionId")            // Extract cookie value
@MatrixVariable String color         // Extract matrix variable
@Valid @RequestBody ProductRequest   // Enable validation
```

### Response Annotations

```java
ResponseEntity<T>           // Full response control
ResponseEntity.ok(body)     // 200 OK with body
ResponseEntity.created(uri).body(body)  // 201 Created
ResponseEntity.noContent().build()      // 204 No Content
ResponseEntity.notFound().build()       // 404 Not Found
ResponseEntity.status(HttpStatus.CONFLICT).body(error)  // Custom status
```

## DTO Best Practices Reference

### Request DTOs

```java
// Good - Using Java records (immutable, concise)
public record CreateProductRequest(
    @NotBlank(message = "Name required") String name,
    @NotNull BigDecimal price,
    String description,
    @Positive Integer stock
) {}

// Alternative - Using Lombok @Value (immutable)
@Value
public class CreateProductRequest {
    @NotBlank String name;
    @NotNull BigDecimal price;
    String description;
    @Positive Integer stock;
}

// Alternative - Using Lombok @Data (mutable, for compatibility)
@Data
public class CreateProductRequest {
    @NotBlank String name;
    @NotNull BigDecimal price;
    String description;
    @Positive Integer stock;
}
```

### Response DTOs

```java
// Record style
public record ProductResponse(
    String id,
    String name,
    BigDecimal price,
    Integer stock,
    LocalDateTime createdAt
) {}

// Lombok @Value style
@Value
@AllArgsConstructor
public class ProductResponse {
    String id;
    String name;
    BigDecimal price;
    Integer stock;
    LocalDateTime createdAt;
}

// Lombok @Data style
@Data
@AllArgsConstructor
public class ProductResponse {
    String id;
    String name;
    BigDecimal price;
    Integer stock;
    LocalDateTime createdAt;
}
```

## Validation Annotations Reference

### Jakarta Validation Constraints

```java
@NotNull                     // Value cannot be null
@NotEmpty                    // Collection/String cannot be empty
@NotBlank                    // String cannot be null or whitespace
@Size(min=1, max=100)       // Collection/String size range
@Min(value=1)               // Numeric minimum value
@Max(value=100)             // Numeric maximum value
@Positive                   // Must be positive
@Negative                   // Must be negative
@Email                      // Valid email format
@Pattern(regexp="^[a-z]+$") // Matches regex pattern
@Future                     // Date must be in future
@Past                       // Date must be in past
@Digits(integer=10, fraction=2)  // Numeric precision
@DecimalMin(value="0.01")   // Decimal minimum
@DecimalMax(value="9999.99") // Decimal maximum
```

### Custom Validation

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = PositivePriceValidator.class)
public @interface PositivePrice {
    String message() default "Price must be positive";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class PositivePriceValidator implements ConstraintValidator<PositivePrice, BigDecimal> {
    @Override
    public boolean isValid(BigDecimal value, ConstraintValidatorContext context) {
        return value != null && value.compareTo(BigDecimal.ZERO) > 0;
    }
}

// Usage
public record ProductRequest(
    @PositivePrice BigDecimal price
) {}
```

## Domain-Driven Design (DDD) Layers Reference

### Typical Feature Structure

```
feature/product/
├── domain/
│   ├── model/
│   │   ├── Product.java           # Aggregate root
│   │   ├── ProductId.java         # Value object
│   │   ├── Money.java             # Value object
│   │   └── Stock.java             # Value object
│   ├── repository/
│   │   └── ProductRepository.java # Domain port (interface)
│   └── service/
│       └── ProductDomainService.java  # Pure business logic
├── application/
│   ├── service/
│   │   └── ProductApplicationService.java  # Use cases
│   ├── dto/
│   │   ├── CreateProductRequest.java
│   │   ├── UpdateProductRequest.java
│   │   └── ProductResponse.java
│   └── mapper/
│       └── ProductMapper.java
├── presentation/
│   └── rest/
│       ├── ProductController.java
│       └── ProductErrorHandler.java
└── infrastructure/
    └── persistence/
        ├── ProductJpaRepository.java    # Spring Data interface
        ├── ProductRepositoryAdapter.java # Adapter implementation
        ├── ProductJpaEntity.java        # JPA entity
        └── ProductEntityMapper.java     # Entity mappers
```

### Layer Responsibilities

| Layer | Responsibility | Examples |
|-------|---|---|
| **Domain** | Pure business logic, no Spring | Entities, value objects, repository interfaces |
| **Application** | Use cases, orchestration | Application services, DTOs, mappers |
| **Presentation** | HTTP interface, serialization | Controllers, request/response handling |
| **Infrastructure** | Technical implementations | JPA repositories, database adapters |

## Mapper Patterns Reference

### Bidirectional Mapping

```java
@Component
public class ProductMapper {
    
    // Domain → Response DTO
    public ProductResponse toResponse(Product domain) {
        return new ProductResponse(
            domain.getId().getValue(),
            domain.getName(),
            domain.getPrice().getAmount(),
            domain.getStock().getQuantity(),
            domain.getCreatedAt()
        );
    }
    
    // Request DTO → Domain
    public Product toDomain(CreateProductRequest request) {
        return Product.create(
            request.name(),
            request.description(),
            request.price(),
            request.stockQuantity()
        );
    }
    
    // Domain → Entity
    public ProductJpaEntity toEntity(Product domain) {
        return ProductJpaEntity.builder()
            .id(domain.getId().getValue())
            .name(domain.getName())
            // ... other fields
            .build();
    }
    
    // Entity → Domain
    public Product toDomain(ProductJpaEntity entity) {
        return Product.builder()
            .id(ProductId.of(entity.getId()))
            .name(entity.getName())
            // ... other fields
            .build();
    }
}
```

## Exception Handling Patterns Reference

### Custom Exception Hierarchy

```java
// Base exception
public abstract class ApplicationException extends RuntimeException {
    public ApplicationException(String message) {
        super(message);
    }
}

// Domain exceptions
public class ResourceNotFoundException extends ApplicationException {}
public class ValidationException extends ApplicationException {}
public class ConflictException extends ApplicationException {}
public class UnauthorizedException extends ApplicationException {}
public class ForbiddenException extends ApplicationException {}
```

### Global Exception Handler

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex, HttpServletRequest request) {
        return buildErrorResponse(HttpStatus.NOT_FOUND, ex.getMessage(), request);
    }

    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            ValidationException ex, HttpServletRequest request) {
        return buildErrorResponse(HttpStatus.BAD_REQUEST, ex.getMessage(), request);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex, HttpServletRequest request) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return buildErrorResponse(HttpStatus.BAD_REQUEST, message, request);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(
            Exception ex, HttpServletRequest request) {
        log.error("Unexpected error", ex);
        return buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, 
            "An unexpected error occurred", request);
    }

    private ResponseEntity<ErrorResponse> buildErrorResponse(
            HttpStatus status, String message, HttpServletRequest request) {
        ErrorResponse error = new ErrorResponse(
            status.value(),
            status.getReasonPhrase(),
            message,
            request.getRequestURI(),
            LocalDateTime.now()
        );
        return ResponseEntity.status(status).body(error);
    }
}
```

## Pagination and Sorting Reference

### Page Request Building

```java
// Basic pagination
Pageable pageable = PageRequest.of(0, 20);  // page 0, size 20

// With sorting
Sort sort = Sort.by("createdAt").descending();
Pageable pageable = PageRequest.of(0, 20, sort);

// Multiple sort fields
Sort sort = Sort.by("status").ascending()
    .and(Sort.by("createdAt").descending());
Pageable pageable = PageRequest.of(0, 20, sort);

// From request parameters
@RequestParam(defaultValue = "0") int page,
@RequestParam(defaultValue = "20") int size,
@RequestParam(defaultValue = "createdAt") String sortBy,
@RequestParam(defaultValue = "DESC") String sortDirection

Sort sort = Sort.by(Sort.Direction.valueOf(sortDirection), sortBy);
Pageable pageable = PageRequest.of(page, size, sort);
```

### Page Response Structure

```java
{
  "content": [
    { "id": 1, "name": "Product 1", ... },
    { "id": 2, "name": "Product 2", ... }
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
  "sort": {
    "empty": false,
    "sorted": true,
    "unsorted": false
  },
  "numberOfElements": 20,
  "first": true,
  "empty": false
}
```

## Transaction Management Reference

### @Transactional Usage Patterns

```java
// Read-only transaction
@Transactional(readOnly = true)
public Product getById(Long id) {
    return repository.findById(id).orElse(null);
}

// Write transaction with propagation
@Transactional(propagation = Propagation.REQUIRED)
public Product save(Product product) {
    return repository.save(product);
}

// Nested transaction
@Transactional(propagation = Propagation.NESTED)
public void saveNested(Product product) {
    repository.save(product);
}

// Rollback on specific exception
@Transactional(rollbackFor = {ValidationException.class})
public Product create(CreateProductRequest request) {
    // Automatic rollback on ValidationException
    return repository.save(toDomain(request));
}

// No rollback on specific exception
@Transactional(noRollbackFor = {OptimisticLockingException.class})
public Product updateWithRetry(Long id, UpdateRequest request) {
    // Won't rollback if OptimisticLockingException thrown
    return repository.save(domain);
}
```

## Testing Reference

### Test Structure

```java
// Unit test (domain layer, no Spring)
class ProductTest {
    @Test
    void shouldCreateProductWithValidData() { }
}

// Service test (mocks, no Spring)
@ExtendWith(MockitoExtension.class)
class ProductApplicationServiceTest {
    @Mock private ProductRepository repository;
    @InjectMocks private ProductApplicationService service;
}

// Slice test (minimal Spring context)
@WebMvcTest(ProductController.class)
class ProductControllerTest {
    @Autowired private MockMvc mockMvc;
    @MockBean private ProductApplicationService service;
}

// Integration test (full Spring context)
@SpringBootTest
@Testcontainers
class ProductIntegrationTest {
    @Container static PostgreSQLContainer<?> postgres = ...;
}
```

## Constructor Injection Reference

### Recommended Pattern (Lombok)

```java
@Service
@RequiredArgsConstructor  // Generates constructor from final fields
public class ProductService {
    private final ProductRepository repository;
    private final ProductMapper mapper;
    
    public Product get(Long id) {
        return repository.findById(id).orElse(null);
    }
}
```

### Explicit Pattern

```java
@Service
public class ProductService {
    private final ProductRepository repository;
    private final ProductMapper mapper;
    
    // Explicit constructor (no @Autowired needed in Spring 4.3+)
    public ProductService(ProductRepository repository, ProductMapper mapper) {
        this.repository = Objects.requireNonNull(repository);
        this.mapper = Objects.requireNonNull(mapper);
    }
}
```

### Avoid: Field Injection

```java
// ❌ AVOID - Field injection is anti-pattern
@Service
public class ProductService {
    @Autowired
    private ProductRepository repository;  // Hidden dependency, hard to test
    
    @Autowired
    private ProductMapper mapper;          // Mutable, not testable
}
```

## Feature-Based Architecture Benefits

| Benefit | Description |
|---------|---|
| **Cohesion** | Related code grouped together by domain |
| **Modularity** | Easy to understand feature boundaries |
| **Reusability** | Services can be extracted as microservices |
| **Testability** | Domain logic isolated from Spring |
| **Maintainability** | Changes localized to feature directory |
| **Scalability** | Easy to add new features without impacting existing code |

## Related Skills

- **spring-boot-dependency-injection/SKILL.md** - Constructor injection patterns and testing
- **spring-boot-rest-api-standards/SKILL.md** - REST API design principles
- **spring-boot-test-patterns/SKILL.md** - Integration testing with Testcontainers
- **junit-test-patterns/SKILL.md** - Unit testing best practices

## External Resources

### Official Documentation
- [Spring Data JPA Reference](https://spring.io/projects/spring-data-jpa)
- [Spring Web MVC Documentation](https://docs.spring.io/spring-framework/reference/web/webmvc.html)
- [Spring Boot REST API Guide](https://spring.io/guides/gs/rest-service/)

### Related Articles
- [RESTful Web Services Best Practices](https://restfulapi.net/)
- [DDD Repository Pattern](https://www.baeldung.com/spring-data-repository-query)
- [Entity-DTO Mapping with MapStruct](https://www.baeldung.com/mapstruct)

### Books and References
- "Domain-Driven Design" by Eric Evans
- "Building Microservices" by Sam Newman
- "Spring in Action" (latest edition)
