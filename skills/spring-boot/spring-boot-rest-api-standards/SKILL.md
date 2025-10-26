---
name: spring-boot-rest-api-standards
description: REST API design standards and best practices for Spring Boot projects. Use this skill when creating or reviewing REST endpoints, DTOs, error handling, pagination, security headers, HATEOAS and architecture patterns.
category: backend
tags: [spring-boot, rest-api, dto, validation, error-handling, pagination, hateoas, architecture, java]
version: 1.0.1
context7_library: /spring-projects/spring-boot-web
context7_trust_score: 8.0
allowed-tools: Read, Write, Bash
---

# Spring Boot REST API Standards

This skill provides comprehensive guidance for building RESTful APIs in Spring Boot applications with consistent design patterns, proper error handling, validation, and architectural best practices based on REST principles and Spring Boot conventions.

## When to Use This Skill

Use this skill when:
- Creating new REST endpoints and API routes
- Designing request/response DTOs and API contracts
- Planning HTTP methods and status codes
- Implementing error handling and validation
- Setting up pagination, filtering, and sorting
- Designing security headers and CORS policies
- Implementing HATEOAS (Hypermedia As The Engine Of Application State)
- Reviewing REST API architecture and design patterns
- Building microservices with consistent API standards
- Documenting API endpoints with clear contracts

## Core Concepts

### RESTful Design Principles

#### 1. Resource-Based URLs

**Good:**
```
GET    /users              # List all users
GET    /users/{id}         # Get specific user
POST   /users              # Create user
PUT    /users/{id}         # Update user
DELETE /users/{id}         # Delete user
```

**Bad:**
```
GET    /getUserList
POST   /createUser
GET    /user/details
DELETE /removeUser
```

#### 2. HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|-----------|------|
| GET | Retrieve resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

#### 3. HTTP Status Codes

**Success Responses:**
- `200 OK` - Request successful, returning data
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted for async processing
- `204 No Content` - Request successful, no content to return

**Redirection:**
- `301 Moved Permanently`
- `302 Found`
- `304 Not Modified`

**Client Errors:**
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Conflict (e.g., duplicate)
- `422 Unprocessable Entity` - Validation failed

**Server Errors:**
- `500 Internal Server Error` - Unexpected error
- `502 Bad Gateway` - External service error
- `503 Service Unavailable` - Temporarily down

### Request/Response Design

**Request Body Structure:**
- Keep request bodies minimal and focused
- Use consistent naming conventions (camelCase for JSON)
- Flatten deeply nested structures when possible
- Validate all incoming data

**Response Body Structure:**
- Always wrap responses in a consistent format
- Include metadata for paginated responses
- Return appropriate status codes
- Include useful headers (e.g., X-Total-Count, Cache-Control)

**Example Response Wrapper:**
```json
{
  "status": "success",
  "code": 200,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Endpoint Design

### Basic CRUD Endpoints

```java
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserService userService;

    @GetMapping
    public ResponseEntity<Page<UserResponse>> getAllUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int pageSize) {
        log.debug("Fetching users page {} size {}", page, pageSize);
        Page<UserResponse> users = userService.getAll(page, pageSize);
        return ResponseEntity.ok(users);
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(userService.getById(id));
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        UserResponse created = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        return ResponseEntity.ok(userService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## Request/Response Objects

### DTOs (Data Transfer Objects)

```java
// Request DTO - for receiving data from client
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import jakarta.validation.constraints.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateUserRequest {

    @NotBlank(message = "User name cannot be blank")
    private String name;

    @Email(message = "Valid email required")
    private String email;

    // Lombok generates getters/setters
}

// Response DTO - for sending data to client
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserResponse {
    private Long id;
    private String name;
    private String email;
    private LocalDateTime createdAt;

    // Lombok generates getters/setters/constructors
}

// Update Request DTO
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class UpdateUserRequest {
    private String name;
    private String email;

    // Lombok generates getters/setters
}
```

### Validation

Use Jakarta Bean Validation (previously javax.validation):

```java
import lombok.Data;
import lombok.NoArgsConstructor;
import jakarta.validation.constraints.*;

@Data
@NoArgsConstructor
public class UserRequest {

    @NotBlank(message = "Name is required")
    private String name;

    @Email(message = "Valid email required")
    private String email;

    @Min(value = 18, message = "Must be at least 18")
    @Max(value = 120, message = "Invalid age")
    private Integer age;

    @Size(min = 8, max = 100, message = "Password must be 8-100 characters")
    private String password;

    // Lombok generates getters and setters
}
```

## Error Handling

### Standardized Error Response

```java
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {
    private int status;
    private String error;
    private String message;
    private String path;
    private LocalDateTime timestamp = LocalDateTime.now();

    // Lombok generates constructors/getters/setters
}
```

### Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NoHandlerFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFoundException(NoHandlerFoundException ex, WebRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.NOT_FOUND.value(),
                HttpStatus.NOT_FOUND.getReasonPhrase(),
                "Resource not found",
                request.getDescription(false).replaceFirst("uri=", "")
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.NOT_FOUND);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(MethodArgumentNotValidException ex, WebRequest request) {
        String errors = ex.getBindingResult().getFieldErrors().stream()
                .map(f -> f.getField() + ": " + f.getDefaultMessage())
                .collect(Collectors.joining(", "));

        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                HttpStatus.BAD_REQUEST.getReasonPhrase(),
                "Validation failed: " + errors,
                request.getDescription(false).replaceFirst("uri=", "")
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleAllExceptions(Exception ex, WebRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                HttpStatus.INTERNAL_SERVER_ERROR.getReasonPhrase(),
                "An unexpected error occurred",
                request.getDescription(false).replaceFirst("uri=", "")
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

### Throwing Errors from Service

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository repository;

    public UserResponse getById(Long id) {
        log.debug("Looking for user with id {}", id);
        User user = repository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "User with ID " + id + " not found"));
        return toResponse(user);
    }

    public UserResponse create(CreateUserRequest request) {
        Optional<User> existing = repository.findByEmail(request.getEmail());
        if (existing.isPresent()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "User with this email already exists");
        }
        User user = new User();
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        User saved = repository.save(user);
        return toResponse(saved);
    }

    // helper to convert entity to response
    private UserResponse toResponse(User user) {
        return new UserResponse(user.getId(), user.getName(), user.getEmail(), user.getCreatedAt());
    }
}
```

## Pagination and Filtering

### Pagination

```java
@GetMapping
public ResponseEntity<Page<UserResponse>> listUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int pageSize,
        @RequestParam(defaultValue = "createdAt") String sortBy,
        @RequestParam(defaultValue = "DESC") String sortDirection) {
    Pageable pageable = PageRequest.of(page, pageSize, Sort.Direction.valueOf(sortDirection), sortBy);
    Page<User> pageResult = userService.getAll(pageable);
    Page<UserResponse> response = pageResult.map(this::toResponse);
    return ResponseEntity.ok(response);
}
```

Response format:
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "createdAt": "2024-01-15T10:30:00"
    }
  ],
  "meta": {
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 45,
    "totalPages": 5,
    "last": false,
    "first": true
  }
}
```

### Filtering

```java
@GetMapping("/search")
public ResponseEntity<Page<UserResponse>> searchUsers(
        @RequestParam(required = false) String name,
        @RequestParam(required = false) String email,
        @RequestParam(defaultValue = "0") int page) {
    return ResponseEntity.ok(userService.search(name, email, page));
}
```

## Content Negotiation

### Accept Headers

```java
@GetMapping(produces = {MediaType.APPLICATION_JSON_VALUE, "application/xml"})
public ResponseEntity<UserResponse> getUser() {
    // Client can request JSON or XML via Accept header
}
```

## Versioning (Optional)

If API versioning is needed:

### URL Versioning
```
GET /v1/users
GET /v2/users
```

### Header Versioning
```
GET /users
Accept: application/vnd.myapi.v1+json
```

## Security Headers

Include security headers in responses:

```java
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/users/**").permitAll()
                .anyRequest().authenticated()
            )
            .headers(headers -> headers
                .contentSecurityPolicy("default-src 'self'")
                .frameOptions(frame -> frame.deny())
            );
        return http.build();
    }
}
```

## API Documentation

Document endpoints with Javadoc comments:

```java
/**
 * Retrieves a user by id.
 *
 * @param id the user id
 * @return ResponseEntity containing a UserResponse
 * @throws ResponseStatusException with 404 if the user is not found
 *
 * Example response:
 * {
 *   "id": 1,
 *   "name": "John Doe",
 *   "email": "john@example.com",
 *   "createdAt": "2024-01-15T10:30:00"
 * }
 */
@GetMapping("/{id}")
public ResponseEntity<UserResponse> getUserById(@PathVariable Long id)
```

## Response Headers

Include useful headers in responses:

```java
@GetMapping("/{id}")
public ResponseEntity<UserResponse> getUser(@PathVariable Long id) {
    UserResponse user = userService.getById(id);
    return ResponseEntity.ok()
            .header("X-Total-Count", String.valueOf(userService.count()))
            .header("Cache-Control", "no-cache")
            .body(user);
}
```

## HATEOAS (Optional)

For more advanced APIs, consider HATEOAS links:

```java
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserResponseWithLinks {
    private Long id;
    private String name;
    private Map<String, String> _links;

    // Lombok generates constructors/getters/setters
}

@GetMapping("/{id}")
public ResponseEntity<UserResponseWithLinks> getUserWithLinks(@PathVariable Long id) {
    UserResponse user = userService.getById(id);
    Map<String, String> links = Map.of(
            "self", "/users/" + id,
            "all", "/users",
            "create", "/users"
    );
    return ResponseEntity.ok(new UserResponseWithLinks(user.getId(), user.getName(), links));
}
```

## API Reference

### Common Spring Web Annotations

**Controller and Mapping Annotations:**
- `@RestController`: Defines a controller that returns JSON responses
- `@Controller`: Defines an MVC controller returning views
- `@RequestMapping`: Maps HTTP requests to handler methods
- `@GetMapping`: Maps GET requests (shorthand for @RequestMapping(method=GET))
- `@PostMapping`: Maps POST requests
- `@PutMapping`: Maps PUT requests
- `@PatchMapping`: Maps PATCH requests
- `@DeleteMapping`: Maps DELETE requests

**Request Parameter Annotations:**
- `@PathVariable`: Extracts path variables from URI (e.g., /users/{id})
- `@RequestParam`: Extracts query parameters (e.g., ?page=0&size=10)
- `@RequestBody`: Deserializes request body to object
- `@RequestHeader`: Extracts HTTP header values
- `@CookieValue`: Extracts cookie values
- `@MatrixVariable`: Extracts matrix variables from URI

**Response Annotations:**
- `@ResponseStatus`: Sets HTTP response status code
- `@ResponseBody`: Serializes return value to response body
- `ResponseEntity<T>`: Wraps response body with status and headers

**Validation Annotations (Jakarta):**
- `@Valid`: Enables validation for a parameter
- `@NotNull`: Field cannot be null
- `@NotEmpty`: Collection/String cannot be empty
- `@NotBlank`: String cannot be blank
- `@Size`: Collection/String size validation
- `@Min/@Max`: Numeric value range
- `@Email`: Email format validation
- `@Pattern`: Regex pattern validation

### HTTP Status Code Reference

**2xx Success:**
- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST (resource created)
- `202 Accepted`: Request accepted for async processing
- `204 No Content`: Successful DELETE (no content to return)

**3xx Redirection:**
- `301 Moved Permanently`: Resource permanently moved
- `302 Found`: Resource temporarily moved
- `304 Not Modified`: Cached response still valid

**4xx Client Errors:**
- `400 Bad Request`: Invalid request syntax or parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource does not exist
- `409 Conflict`: Request conflicts with current state
- `422 Unprocessable Entity`: Validation errors

**5xx Server Errors:**
- `500 Internal Server Error`: Unexpected server error
- `502 Bad Gateway`: External service error
- `503 Service Unavailable`: Server temporarily unavailable

## Architecture & Design (Recommended Patterns)

These REST API standards should align with the project's reviewer guidance and follow well-known architectural patterns to improve maintainability, testability and clarity.

Key principles:
- Prefer a feature-based (or DDD-inspired) module structure for each domain/feature (example tree below). Keep domain logic free of Spring dependencies when possible.
- Use constructor injection for all Spring beans (prefer Lombok's @RequiredArgsConstructor to reduce boilerplate).
- Keep controllers thin: they should adapt HTTP requests to application use-cases and delegate to application services.
- Implement Repository as a domain port (interface) and provide a separate infrastructure adapter (e.g. JPA) that implements it.
- Prefer immutable DTOs where possible (Java records on modern JDKs) or Lombok @Value/@Data for brevity. Use dedicated mappers to convert between domain and DTOs.
- Use Optional in repository returns to express absent values explicitly.
- Keep classes small and single-responsibility; aim for files under ~300 lines.
- Use meaningful logging with Lombok's @Slf4j, but avoid logging sensitive data.
- Write unit tests for domain and application layers and lightweight integration tests for controllers; see `junit-test-patterns/SKILL.md` for testing guidance.

Example feature tree (recommended):
```
users/
├── domain/
│   ├── model/         # domain entities and domain logic
│   ├── repository/    # domain port (interface)
│   └── service/       # domain services
├── application/
│   ├── service/       # application use-cases (Spring @Service)
│   └── dto/           # immutable DTOs / records
├── presentation/
│   └── rest/          # controllers, request/response mappers
└── infrastructure/
    └── persistence/   # JPA repositories and mappers (adapters)
```

Controller → Application Service example (preferred):
```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final CreateUserService createUserService; // application use-case
    private final UserMapper mapper; // maps between DTO and command/domain

    @PostMapping
    public ResponseEntity<UserDto> create(@Valid @RequestBody CreateUserRequest req) {
        CreateUserCommand cmd = mapper.toCommand(req);
        UserDto dto = createUserService.createUser(cmd);
        return ResponseEntity.status(HttpStatus.CREATED).body(dto);
    }
}
```

Repository port / Adapter example:
```java
public interface UserRepository {
    Optional<User> findById(UserId id);
    void save(User user);
}

@Repository
@RequiredArgsConstructor
public class JpaUserRepository implements UserRepository {
    private final SpringDataUserRepository repo;

    public Optional<User> findById(UserId id) {
        return repo.findById(id.value()).map(UserMapper::toDomain);
    }

    public void save(User user) {
        repo.save(UserMapper.toEntity(user));
    }
}
```

DTO guidance:
- For simple immutable transfer objects prefer Java records (JDK 16+). Example: `public record CreateUserRequest(@NotBlank String name) {}`
- If records are not available, use Lombok @Value (immutable) or @Data for mutable DTOs.
- Keep validation annotations on DTOs (Jakarta Validation) and map validated DTOs into domain-friendly commands.

Testing and CI:
- Unit-test domain and application logic without Spring (fast tests).
- Use slice or WebMvc tests for controllers and a small set of integration tests with embedded database for critical flows.
- Refer to `junit-test-patterns/SKILL.md` for recommended test patterns.

## Workflow Patterns

### Complete REST API CRUD Pattern

This pattern demonstrates a full-featured REST API with proper layering:

**Entity with Validation:**
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Name is required")
    private String name;

    @Email(message = "Valid email required")
    @Column(unique = true)
    private String email;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

**Service with Transaction Management:**
```java
@Service
@Transactional
@RequiredArgsConstructor
@Slf4j
public class UserService {
    private final UserRepository userRepository;

    @Transactional(readOnly = true)
    public Page<User> findAll(Pageable pageable) {
        log.debug("Fetching users page {} size {}", pageable.getPageNumber(), pageable.getPageSize());
        return userRepository.findAll(pageable);
    }

    @Transactional(readOnly = true)
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }

    public User create(User user) {
        log.info("Creating new user with email: {}", user.getEmail());
        return userRepository.save(user);
    }

    public User update(Long id, User userDetails) {
        return userRepository.findById(id)
            .map(user -> {
                user.setName(userDetails.getName());
                user.setEmail(userDetails.getEmail());
                return userRepository.save(user);
            })
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "User not found"));
    }

    public void delete(Long id) {
        if (!userRepository.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "User not found");
        }
        userRepository.deleteById(id);
    }
}
```

**Controller with Proper HTTP Methods:**
```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {
    private final UserService userService;

    @GetMapping
    public ResponseEntity<Page<User>> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return ResponseEntity.ok(userService.findAll(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<User> getById(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<User> create(@Valid @RequestBody User user) {
        User created = userService.create(user);
        return ResponseEntity.status(HttpStatus.CREATED)
            .header("Location", "/api/users/" + created.getId())
            .body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<User> update(@PathVariable Long id, @Valid @RequestBody User user) {
        return ResponseEntity.ok(userService.update(id, user));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

### Exception Handling Pattern

**Global Exception Handler:**
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ErrorResponse> handleResponseStatusException(
            ResponseStatusException ex,
            WebRequest request) {
        ErrorResponse error = new ErrorResponse(
            ex.getStatusCode().value(),
            ex.getStatusCode().toString(),
            ex.getReason(),
            request.getDescription(false).replace("uri=", ""),
            LocalDateTime.now()
        );
        return new ResponseEntity<>(error, ex.getStatusCode());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(
            MethodArgumentNotValidException ex,
            WebRequest request) {
        String errors = ex.getBindingResult().getFieldErrors().stream()
            .map(f -> f.getField() + ": " + f.getDefaultMessage())
            .collect(Collectors.joining(", "));

        ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Validation Error",
            errors,
            request.getDescription(false).replace("uri=", ""),
            LocalDateTime.now()
        );
        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGlobalException(
            Exception ex,
            WebRequest request) {
        log.error("Unexpected error occurred", ex);
        ErrorResponse error = new ErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "Internal Server Error",
            "An unexpected error occurred",
            request.getDescription(false).replace("uri=", ""),
            LocalDateTime.now()
        );
        return new ResponseEntity<>(error, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

## Best Practices

### 1. Always Use Constructor Injection
Prefer constructor injection over field injection for better testability and explicit dependencies. This is the recommended pattern for mandatory dependencies.

```java
// Good - Constructor injection with Lombok
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    public User registerUser(CreateUserRequest request) {
        User user = User.create(request.getName(), request.getEmail());
        return userRepository.save(user);
    }
}

// Good - Constructor injection explicit
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}

// Bad - Field injection (avoid)
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;  // Hidden dependency, hard to test
    
    @Autowired
    private EmailService emailService;      // Mutable state
}
```

**See:** `spring-boot-dependency-injection/SKILL.md` for comprehensive DI patterns and testing strategies.

### 2. Use DTOs for API Boundaries
Never expose entities directly in API responses. Use DTOs to separate API contracts from domain models.

```java
// DTO
public record UserResponse(Long id, String name, String email, LocalDateTime createdAt) {}

// In controller
return ResponseEntity.ok(userService.findById(id)
    .map(user -> new UserResponse(user.getId(), user.getName(), user.getEmail(), user.getCreatedAt()))
    .orElse(null));
```

### 3. Validate Input Early
Use Jakarta Validation annotations to validate input at the controller boundary.

```java
@PostMapping
public ResponseEntity<User> create(@Valid @RequestBody User user) {
    // Validation happens automatically before method execution
    return ResponseEntity.status(HttpStatus.CREATED).body(userService.create(user));
}
```

### 4. Use ResponseEntity for Flexible Responses
Use ResponseEntity to have full control over status codes and headers.

```java
return ResponseEntity.status(HttpStatus.CREATED)
    .header("X-Custom-Header", "value")
    .body(created);
```

### 5. Implement Proper Error Handling
Use @RestControllerAdvice for centralized exception handling across all controllers.

### 6. Use Pagination for Large Datasets
Always paginate GET endpoints that might return many results.

```java
@GetMapping
public ResponseEntity<Page<User>> getAll(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size) {
    Pageable pageable = PageRequest.of(page, size);
    return ResponseEntity.ok(userService.findAll(pageable));
}
```

### 7. Use Logging with @Slf4j
Add meaningful logs for debugging, but never log sensitive information.

```java
@Slf4j
@Service
public class UserService {
    public User create(User user) {
        log.info("Creating user with email: {}", user.getEmail());
        return userRepository.save(user);
    }
}
```

### 8. Use Transactions Appropriately
Mark service methods with @Transactional and use readOnly=true for query methods.

```java
@Transactional(readOnly = true)
public Optional<User> findById(Long id) {
    return userRepository.findById(id);
}

@Transactional
public User create(User user) {
    return userRepository.save(user);
}
```

### 9. Document Your API
Use clear method names, Javadoc comments, and consistent response formats.

### 10. Follow REST Conventions
- Use nouns for resource names, not verbs
- Use HTTP methods correctly (GET for read, POST for create, PUT for update, DELETE for delete)
- Return appropriate HTTP status codes
- Use plural resource names (/users, not /user)

## References

- `agents/spring-boot-code-review-specialist.md` — follow these review rules when authoring code.
- `spring-boot-dependency-injection/SKILL.md` — comprehensive DI patterns, constructor injection, and testing.
- `spring-boot-patterns/SKILL.md` — common patterns for the project.
- `junit-test-patterns/SKILL.md` — testing patterns and best practices.

## Lombok Integration

To consistently use Lombok across this project's Java examples and production code, add Lombok to your build and enable annotation processing in your IDE. Lombok reduces boilerplate for getters/setters, constructors, builders, and logging.

Recommended Lombok annotations
- @RequiredArgsConstructor - constructor injection for final fields
- @Data / @Value - DTO getters/setters or immutable DTOs
- @Getter / @Setter - selective accessors
- @Builder - fluent builders for complex DTOs
- @Slf4j - logger instance
- @AllArgsConstructor / @NoArgsConstructor - explicit constructors when needed

Maven (pom.xml) example
```xml
<dependency>
  <groupId>org.projectlombok</groupId>
  <artifactId>lombok</artifactId>
  <version>1.18.30</version>
  <scope>provided</scope>
</dependency>
```

Gradle (Groovy) example
```gradle
dependencies {
  compileOnly 'org.projectlombok:lombok:1.18.30'
  annotationProcessor 'org.projectlombok:lombok:1.18.30'
}
```

## Summary

This Spring Boot REST API Standards skill covers comprehensive guidance for building production-ready RESTful APIs:

### Key Topics Covered:
1. **RESTful Design Principles**: Resource-based URLs, proper HTTP methods, appropriate status codes
2. **Request/Response Design**: Consistent formatting, validation, pagination, filtering
3. **Endpoint Design**: CRUD operations, proper use of HTTP methods and status codes
4. **DTOs and Validation**: Request/response objects with Jakarta validation annotations
5. **Error Handling**: Global exception handlers with standardized error responses
6. **Pagination and Filtering**: Handling large datasets with pagination, sorting, and filtering
7. **Content Negotiation**: Supporting multiple response formats (JSON, XML)
8. **API Versioning**: URL-based and header-based versioning strategies
9. **Security Headers**: CORS, content security policy, frame options
10. **API Documentation**: Clear contracts with Javadoc comments
11. **HATEOAS**: Hypermedia links for advanced API design
12. **Architecture Patterns**: Feature-based, DDD-inspired layering with clean separation of concerns
13. **API Reference**: Common annotations and HTTP status codes
14. **Workflow Patterns**: Complete CRUD patterns and exception handling examples
15. **Best Practices**: Constructor injection, DTOs, validation, transactions, logging, pagination

### Technology Stack:
- **Java 16+** with support for records
- **Spring Boot 3.x** with Spring Web and Spring Data JPA
- **Jakarta Validation** for input validation
- **Lombok 1.18.30+** for reducing boilerplate
- **Spring Security** for authentication and authorization

### Architecture Recommendations:
Follow a feature-based, DDD-inspired structure with clear separation:
- `domain/`: Business logic and entities
- `application/`: Use cases and services
- `presentation/`: REST controllers and mappers
- `infrastructure/`: Data persistence and external integrations

All patterns emphasize:
- Constructor injection via Lombok's @RequiredArgsConstructor
- Immutable DTOs (Java records or Lombok @Value)
- Proper transaction management with @Transactional
- Centralized exception handling with @RestControllerAdvice
- Meaningful logging with @Slf4j
- Comprehensive input validation with Jakarta annotations

This skill aligns with Spring Boot best practices and the project's architectural guidelines defined in `agents/spring-boot-code-review-specialist.md`.
