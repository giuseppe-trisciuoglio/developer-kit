# Spring Web Annotations Reference

## Controller and Mapping Annotations

### @RestController
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    // Returns JSON responses automatically
}
```

### @Controller
```java
@Controller
@RequestMapping("/users")
public class UserController {
    // Returns view names for MVC applications
}
```

### @RequestMapping
```java
// Class level
@RequestMapping("/api")
@RequestMapping(path = "/api", method = RequestMethod.GET)

// Method level
@RequestMapping("/users")
@RequestMapping(path = "/users", method = RequestMethod.POST)
```

### HTTP Method Annotations

```java
@GetMapping("/users")
public List<User> getUsers() { ... }

@PostMapping("/users")
public User createUser(@RequestBody User user) { ... }

@PutMapping("/users/{id}")
public User updateUser(@PathVariable Long id, @RequestBody User user) { ... }

@PatchMapping("/users/{id}")
public User patchUser(@PathVariable Long id, @RequestBody User user) { ... }

@DeleteMapping("/users/{id}")
public void deleteUser(@PathVariable Long id) { ... }

@HeadMapping("/users/{id}")
public ResponseEntity<Void> headUser(@PathVariable Long id) { ... }

@OptionsMapping("/users")
public ResponseEntity<Void> optionsUsers() { ... }
```

## Parameter Binding Annotations

### @PathVariable
```java
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) { ... }

// Multiple path variables
@GetMapping("/users/{userId}/orders/{orderId}")
public Order getOrder(@PathVariable Long userId, @PathVariable Long orderId) { ... }

// Custom variable name
@GetMapping("/users/{userId}")
public User getUser(@PathVariable("userId") Long id) { ... }
```

### @RequestParam
```java
@GetMapping("/users")
public List<User> getUsers(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size,
    @RequestParam(required = false) String name,
    @RequestParam(defaultValue = "createdAt") String sortBy,
    @RequestParam(defaultValue = "DESC") String sortDirection) {
    // Handle pagination, filtering, and sorting
}
```

### @RequestBody
```java
@PostMapping("/users")
public User createUser(@RequestBody User user) { ... }

// With validation
@PostMapping("/users")
public User createUser(@Valid @RequestBody User user) { ... }
```

### @RequestHeader
```java
@GetMapping("/users")
public List<User> getUsers(@RequestHeader("Authorization") String authHeader) { ... }

// Multiple headers
@PostMapping("/users")
public User createUser(
    @RequestBody User user,
    @RequestHeader("X-Custom-Header") String customHeader) { ... }
```

### @CookieValue
```java
@GetMapping("/users")
public List<User> getUsers(@CookieValue("JSESSIONID") String sessionId) { ... }
```

### @MatrixVariable
```java
@GetMapping("/users/{id}")
public User getUser(
    @PathVariable Long id,
    @MatrixVariable(pathVar = "id", required = false) Map<String, String> params) {
    // Handle matrix variables: /users/123;name=John;age=30
}
```

## Response Annotations

### @ResponseStatus
```java
@PostMapping("/users")
@ResponseStatus(HttpStatus.CREATED)
public User createUser(@RequestBody User user) { ... }
```

### @ResponseBody
```java
@Controller
public class UserController {
    @GetMapping("/users")
    @ResponseBody
    public List<User> getUsers() { ... }
}
```

### ResponseEntity
```java
@GetMapping("/users/{id}")
public ResponseEntity<User> getUser(@PathVariable Long id) {
    return userRepository.findById(id)
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build());
}

@PostMapping("/users")
public ResponseEntity<User> createUser(@RequestBody User user) {
    User created = userService.create(user);
    return ResponseEntity.status(HttpStatus.CREATED)
        .header("Location", "/api/users/" + created.getId())
        .body(created);
}
```

## Content Negotiation

### Produces and Consumes
```java
@GetMapping(value = "/users", produces = MediaType.APPLICATION_JSON_VALUE)
public List<User> getUsers() { ... }

@PostMapping(value = "/users", consumes = MediaType.APPLICATION_JSON_VALUE)
public User createUser(@RequestBody User user) { ... }

// Multiple media types
@GetMapping(value = "/users", produces = {
    MediaType.APPLICATION_JSON_VALUE,
    MediaType.APPLICATION_XML_VALUE
})
public List<User> getUsers() { ... }
```

### @RequestBody with Content-Type
```java
@PostMapping(value = "/users", consumes = "application/json")
public User createUserJson(@RequestBody User user) { ... }

@PostMapping(value = "/users", consumes = "application/xml")
public User createUserXml(@RequestBody User user) { ... }
```

## Validation Annotations

### @Valid
```java
@PostMapping("/users")
public User createUser(@Valid @RequestBody User user) { ... }

// Validates individual parameters
@GetMapping("/users")
public User getUser(
    @Valid @Pattern(regexp = "^[a-zA-Z0-9]+$") @PathVariable String id) { ... }
```

### Jakarta Bean Validation Annotations
```java
public class UserRequest {
    @NotBlank(message = "Name is required")
    private String name;

    @Email(message = "Valid email required")
    private String email;

    @Size(min = 8, max = 100, message = "Password must be 8-100 characters")
    private String password;

    @Min(value = 18, message = "Must be at least 18")
    @Max(value = 120, message = "Invalid age")
    private Integer age;

    @Pattern(regexp = "^[A-Z][a-z]+$", message = "Invalid name format")
    private String firstName;

    @NotEmpty(message = "At least one role required")
    private Set<String> roles = new HashSet<>();

    @Future(message = "Date must be in the future")
    private LocalDate futureDate;

    @Past(message = "Date must be in the past")
    private LocalDate birthDate;

    @Positive(message = "Value must be positive")
    private Double positiveValue;

    @PositiveOrZero(message = "Value must be positive or zero")
    private Double nonNegativeValue;
}
```

## Specialized Annotations

### @RestControllerAdvice
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(
            MethodArgumentNotValidException ex) {
        // Handle validation errors globally
    }
}
```

### @ExceptionHandler
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NoHandlerFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(NoHandlerFoundException ex) {
        return ResponseEntity.notFound().build();
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception ex) {
        return ResponseEntity.internalServerError().build();
    }
}
```

### @CrossOrigin
```java
@CrossOrigin(origins = "http://localhost:3000")
@RestController
@RequestMapping("/api/users")
public class UserController {
    // Enable CORS for specific origin
}

// Or at method level
@CrossOrigin(origins = "*", methods = {RequestMethod.GET, RequestMethod.POST})
@GetMapping("/users")
public List<User> getUsers() { ... }
```

## Async Processing

### @Async
```java
@Service
public class AsyncService {

    @Async
    public CompletableFuture<User> processUser(User user) {
        // Long-running operation
        return CompletableFuture.completedFuture(processedUser);
    }
}

@RestController
public class UserController {

    @GetMapping("/users/{id}/async")
    public CompletableFuture<ResponseEntity<User>> getUserAsync(@PathVariable Long id) {
        return userService.processUser(id)
            .thenApply(ResponseEntity::ok)
            .exceptionally(ex -> ResponseEntity.notFound().build());
    }
}
```