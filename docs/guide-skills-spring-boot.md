# Complete Guide to Spring Boot Skills

This comprehensive guide documents all Spring Boot skills available in the Developer Kit, organized by functional area with detailed explanations, practical examples, and best practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Spring Boot Skills](#core-spring-boot-skills)
3. [Data & Persistence Skills](#data--persistence-skills)
4. [Architecture & Design Skills](#architecture--design-skills)
5. [API & Integration Skills](#api--integration-skills)
6. [Resilience & Patterns Skills](#resilience--patterns-skills)
7. [Testing Skills](#testing-skills)
8. [Common Workflows](#common-workflows)
9. [Best Practices](#best-practices)

---

## Overview

The Spring Boot skills collection provides comprehensive patterns, workflows, and best practices for building production-ready Spring Boot applications. These skills cover everything from basic dependency injection to advanced distributed patterns like Saga and event-driven architectures.

### Skill Categories

- **Core Spring Boot**: Dependency injection, configuration, actuator, caching
- **Data & Persistence**: Spring Data JPA, Neo4j, repository patterns
- **Architecture**: CRUD patterns, event-driven design, clean architecture
- **API**: REST API standards, OpenAPI documentation
- **Resilience**: Resilience4j patterns, fault tolerance
- **Testing**: Integration testing with Testcontainers

### Technology Stack

- **Spring Boot**: 3.5.x or later
- **Java**: 17+ (with records and modern features)
- **Spring Data**: JPA, Neo4j
- **Testing**: Testcontainers 1.19.0+, JUnit 5, Mockito
- **Documentation**: OpenAPI 3.0, Swagger UI
- **Resilience**: Resilience4j for circuit breakers and retry logic

---

## Core Spring Boot Skills

### spring-boot-dependency-injection

**Purpose**: Master constructor-first dependency injection patterns for testable, framework-agnostic Spring Boot services.

**When to use:**
- Implementing new `@Service`, `@Component`, or `@Repository` classes
- Replacing legacy field injection during modernization
- Configuring optional or pluggable collaborators
- Auditing bean definitions before integration tests

**Key Patterns:**

1. **Constructor Injection (Recommended)**
```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    public User register(UserRegistrationRequest request) {
        User user = User.create(request.email(), request.name());
        userRepository.save(user);
        emailService.sendWelcome(user);
        return user;
    }
}
```

**Benefits:**
- ✅ Explicit, immutable dependencies
- ✅ Testable without Spring context
- ✅ IDE-friendly with clear contracts
- ✅ `final` fields ensure thread-safety

2. **Optional Collaborators**
```java
@Service
public class NotificationService {
    private final EmailProvider emailProvider;
    private SmsProvider smsProvider; // Optional

    public NotificationService(EmailProvider emailProvider) {
        this.emailProvider = Objects.requireNonNull(emailProvider);
    }

    @Autowired(required = false)
    public void setSmsProvider(SmsProvider smsProvider) {
        this.smsProvider = smsProvider;
    }

    public void notify(User user, String message) {
        emailProvider.send(user.getEmail(), message);
        if (smsProvider != null) {
            smsProvider.send(user.getPhone(), message);
        }
    }
}
```

3. **Bean Selection with @Qualifier**
```java
@Service
@RequiredArgsConstructor
public class PaymentService {
    @Qualifier("stripePaymentGateway")
    private final PaymentGateway paymentGateway;

    public PaymentResult processPayment(PaymentRequest request) {
        return paymentGateway.charge(request);
    }
}
```

**Best Practices:**
- Always use constructor injection for mandatory dependencies
- Mark injected fields as `final`
- Use `@RequiredArgsConstructor` from Lombok to reduce boilerplate
- Validate dependencies with `Objects.requireNonNull()` if not using Lombok
- Write unit tests that instantiate classes manually with mocks
- Use `@Qualifier` or `@Primary` to resolve bean ambiguity

**References:**
- `skills/spring-boot/spring-boot-dependency-injection/SKILL.md`
- `skills/spring-boot/spring-boot-dependency-injection/references/`

---

### spring-boot-actuator

**Purpose**: Production-ready monitoring, health checks, metrics, and management endpoints for Spring Boot applications.

**When to use:**
- Adding production monitoring and observability
- Implementing custom health checks
- Exposing application metrics
- Creating management endpoints
- Integrating with monitoring systems (Prometheus, Grafana)

**Key Features:**

1. **Health Checks**
```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    private final DataSource dataSource;

    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            if (conn.isValid(2)) {
                return Health.up()
                    .withDetail("database", "PostgreSQL")
                    .withDetail("validationQuery", "SELECT 1")
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withException(e)
                .build();
        }
        return Health.down().build();
    }
}
```

2. **Custom Metrics**
```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final MeterRegistry meterRegistry;
    private final OrderRepository orderRepository;

    public Order createOrder(CreateOrderRequest request) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            Order order = orderRepository.save(/* ... */);
            meterRegistry.counter("orders.created", 
                "status", order.getStatus()).increment();
            return order;
        } finally {
            sample.stop(meterRegistry.timer("orders.creation.time"));
        }
    }
}
```

3. **Configuration**
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
```

**Key Endpoints:**
- `/actuator/health` - Application health status
- `/actuator/health/readiness` - Kubernetes readiness probe
- `/actuator/health/liveness` - Kubernetes liveness probe
- `/actuator/metrics` - Available metrics
- `/actuator/prometheus` - Prometheus-formatted metrics
- `/actuator/info` - Application information

**Best Practices:**
- Secure actuator endpoints with Spring Security
- Use `when-authorized` for health details
- Implement custom health indicators for critical dependencies
- Export metrics to monitoring systems (Prometheus, Datadog)
- Use tags for dimensional metrics
- Monitor application-specific metrics (orders created, API latency)
- Set up alerts for critical health indicators

**References:**
- `skills/spring-boot/spring-boot-actuator/SKILL.md`
- `skills/spring-boot/spring-boot-actuator/examples.md`
- `skills/spring-boot/spring-boot-actuator/reference.md`

---

### spring-boot-cache

**Purpose**: Implement caching strategies using Spring Cache abstraction with support for multiple cache providers.

**When to use:**
- Reducing database queries for frequently accessed data
- Improving API response times
- Implementing read-through and write-through caching
- Cache invalidation strategies
- Multi-level caching (L1/L2)

**Key Patterns:**

1. **Basic Caching**
```java
@Service
@RequiredArgsConstructor
public class ProductService {
    private final ProductRepository productRepository;

    @Cacheable(value = "products", key = "#id")
    public Product findById(Long id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));
    }

    @CachePut(value = "products", key = "#result.id")
    public Product update(Long id, UpdateProductRequest request) {
        Product product = findById(id);
        product.update(request);
        return productRepository.save(product);
    }

    @CacheEvict(value = "products", key = "#id")
    public void delete(Long id) {
        productRepository.deleteById(id);
    }

    @CacheEvict(value = "products", allEntries = true)
    public void clearCache() {
        // Cache cleared
    }
}
```

2. **Conditional Caching**
```java
@Cacheable(
    value = "users", 
    key = "#email",
    condition = "#email != null",
    unless = "#result == null"
)
public User findByEmail(String email) {
    return userRepository.findByEmail(email).orElse(null);
}
```

3. **Configuration**
```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))
            .serializeKeysWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair
                    .fromSerializer(new GenericJackson2JsonRedisSerializer()));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .withCacheConfiguration("products",
                config.entryTtl(Duration.ofHours(1)))
            .build();
    }
}
```

**Cache Providers:**
- **Redis**: Distributed caching for microservices
- **Caffeine**: High-performance local cache
- **Hazelcast**: Distributed in-memory data grid
- **EhCache**: Enterprise-grade caching solution

**Best Practices:**
- Use SpEL expressions for dynamic cache keys
- Set appropriate TTL (Time To Live) for cached entries
- Implement cache warming for critical data
- Use `@CacheEvict` carefully to avoid stale data
- Monitor cache hit/miss ratios
- Consider cache size limits to prevent memory issues
- Test cache behavior with integration tests

**References:**
- `skills/spring-boot/spring-boot-cache/SKILL.md`

---

## Data & Persistence Skills

### spring-data-jpa

**Purpose**: Master Spring Data JPA patterns for database access, entity design, and repository implementation.

**When to use:**
- Implementing database persistence with JPA
- Creating custom repository queries
- Designing entity relationships
- Implementing pagination and sorting
- Optimizing database performance

**Key Patterns:**

1. **Entity Design**
```java
@Entity
@Table(name = "products")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Getter
public class ProductEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private ProductStatus status;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private CategoryEntity category;

    @OneToMany(mappedBy = "product", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<ProductImageEntity> images = new ArrayList<>();

    @Version
    private Long version; // Optimistic locking

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(nullable = false)
    private Instant updatedAt;
}
```

2. **Repository Interface**
```java
public interface ProductRepository extends JpaRepository<ProductEntity, Long> {

    // Query methods
    List<ProductEntity> findByStatus(ProductStatus status);
    
    Optional<ProductEntity> findByNameIgnoreCase(String name);
    
    Page<ProductEntity> findByCategory(CategoryEntity category, Pageable pageable);

    // Custom JPQL query
    @Query("SELECT p FROM ProductEntity p WHERE p.price BETWEEN :minPrice AND :maxPrice")
    List<ProductEntity> findByPriceRange(
        @Param("minPrice") BigDecimal minPrice,
        @Param("maxPrice") BigDecimal maxPrice
    );

    // Native query
    @Query(value = "SELECT * FROM products WHERE status = :status ORDER BY created_at DESC LIMIT :limit",
           nativeQuery = true)
    List<ProductEntity> findRecentByStatus(
        @Param("status") String status,
        @Param("limit") int limit
    );

    // Modifying query
    @Modifying
    @Query("UPDATE ProductEntity p SET p.status = :status WHERE p.id IN :ids")
    int updateStatusBatch(@Param("ids") List<Long> ids, @Param("status") ProductStatus status);
}
```

3. **Specifications for Dynamic Queries**
```java
public class ProductSpecifications {

    public static Specification<ProductEntity> hasName(String name) {
        return (root, query, cb) -> 
            name == null ? null : cb.like(cb.lower(root.get("name")), "%" + name.toLowerCase() + "%");
    }

    public static Specification<ProductEntity> hasPriceGreaterThan(BigDecimal price) {
        return (root, query, cb) -> 
            price == null ? null : cb.greaterThanOrEqualTo(root.get("price"), price);
    }

    public static Specification<ProductEntity> hasStatus(ProductStatus status) {
        return (root, query, cb) -> 
            status == null ? null : cb.equal(root.get("status"), status);
    }
}

// Usage
Specification<ProductEntity> spec = Specification
    .where(hasName(searchTerm))
    .and(hasPriceGreaterThan(minPrice))
    .and(hasStatus(ProductStatus.ACTIVE));

Page<ProductEntity> results = productRepository.findAll(spec, pageable);
```

**Best Practices:**
- Use `@ManyToOne(fetch = FetchType.LAZY)` to avoid N+1 problems
- Implement optimistic locking with `@Version` for concurrent updates
- Use `@EntityGraph` to fetch associations efficiently
- Separate domain models from JPA entities (adapter pattern)
- Use pagination for large result sets
- Implement auditing with `@CreatedDate` and `@LastModifiedDate`
- Write integration tests with Testcontainers for real database testing

**Performance Tips:**
- Use batch operations for bulk updates
- Configure hibernate statistics to monitor queries
- Enable second-level cache for frequently read entities
- Use `@QueryHints` for query optimization
- Implement database indexes for frequently queried columns

**References:**
- `skills/spring-boot/spring-data-jpa/SKILL.md`

---

### spring-data-neo4j

**Purpose**: Implement graph database patterns using Spring Data Neo4j for connected data models.

**When to use:**
- Modeling highly connected data (social networks, recommendation engines)
- Implementing graph-based queries and traversals
- Managing relationships between entities
- Building knowledge graphs

**Key Patterns:**

1. **Node Entity**
```java
@Node
@Data
public class Person {
    
    @Id @GeneratedValue
    private Long id;

    private String name;
    private String email;

    @Relationship(type = "FRIENDS_WITH", direction = Relationship.Direction.OUTGOING)
    private Set<Person> friends = new HashSet<>();

    @Relationship(type = "WORKS_AT", direction = Relationship.Direction.OUTGOING)
    private Company company;
}
```

2. **Repository with Cypher Queries**
```java
public interface PersonRepository extends Neo4jRepository<Person, Long> {

    @Query("MATCH (p:Person)-[:FRIENDS_WITH*1..2]-(friend) WHERE p.id = $personId RETURN DISTINCT friend")
    List<Person> findFriendsOfFriends(@Param("personId") Long personId);

    @Query("MATCH path = shortestPath((p1:Person {id: $from})-[*]-(p2:Person {id: $to})) RETURN length(path)")
    Optional<Integer> findDegreesOfSeparation(
        @Param("from") Long fromId,
        @Param("to") Long toId
    );
}
```

**References:**
- `skills/spring-boot/spring-data-neo4j/SKILL.md`

---

## Architecture & Design Skills

### spring-boot-crud-patterns

**Purpose**: Implement feature-aligned CRUD services with Clean Architecture and DDD principles.

**When to use:**
- Creating REST endpoints for CRUD operations
- Implementing feature-based architecture
- Separating domain, application, infrastructure, and presentation layers
- Building maintainable and testable services

**Architecture:**

```
feature/product/
├── domain/
│   ├── model/
│   │   └── Product.java              # Domain aggregate
│   └── repository/
│       └── ProductRepository.java     # Domain port (interface)
├── application/
│   ├── service/
│   │   └── ProductService.java        # Use cases
│   └── dto/
│       ├── CreateProductRequest.java  # Request DTOs
│       ├── UpdateProductRequest.java
│       └── ProductResponse.java       # Response DTOs
├── presentation/
│   └── rest/
│       ├── ProductController.java     # REST endpoints
│       └── ProductMapper.java         # DTO <-> Domain mapper
└── infrastructure/
    └── persistence/
        ├── ProductEntity.java         # JPA entity
        ├── ProductJpaRepository.java  # Spring Data repository
        └── ProductRepositoryAdapter.java # Repository implementation
```

**Implementation Example:**

1. **Domain Model (Pure Java)**
```java
public class Product {
    private final ProductId id;
    private String name;
    private Money price;
    private Stock stock;

    private Product(ProductId id, String name, Money price, Stock stock) {
        this.id = Objects.requireNonNull(id);
        this.name = validateName(name);
        this.price = Objects.requireNonNull(price);
        this.stock = Objects.requireNonNull(stock);
    }

    public static Product create(String name, Money price, int initialStock) {
        return new Product(
            ProductId.generate(),
            name,
            price,
            Stock.of(initialStock)
        );
    }

    public void updatePrice(Money newPrice) {
        if (newPrice.isLessThan(Money.ZERO)) {
            throw new IllegalArgumentException("Price cannot be negative");
        }
        this.price = newPrice;
    }

    private String validateName(String name) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Product name cannot be blank");
        }
        return name.trim();
    }
}
```

2. **Repository Port (Domain)**
```java
public interface ProductRepository {
    Product save(Product product);
    Optional<Product> findById(ProductId id);
    List<Product> findAll(Pageable pageable);
    void deleteById(ProductId id);
}
```

3. **Application Service**
```java
@Service
@Transactional
@RequiredArgsConstructor
public class ProductService {
    private final ProductRepository productRepository;
    private final ProductMapper productMapper;

    public ProductResponse createProduct(CreateProductRequest request) {
        Product product = Product.create(
            request.name(),
            Money.of(request.price()),
            request.initialStock()
        );
        Product saved = productRepository.save(product);
        return productMapper.toResponse(saved);
    }

    @Transactional(readOnly = true)
    public ProductResponse getProduct(Long id) {
        return productRepository.findById(ProductId.of(id))
            .map(productMapper::toResponse)
            .orElseThrow(() -> new ProductNotFoundException(id));
    }
}
```

4. **REST Controller**
```java
@RestController
@RequestMapping("/api/v1/products")
@RequiredArgsConstructor
public class ProductController {
    private final ProductService productService;

    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(
            @Valid @RequestBody CreateProductRequest request) {
        ProductResponse response = productService.createProduct(request);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(response.id())
            .toUri();
        return ResponseEntity.created(location).body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
        return ResponseEntity.ok(productService.getProduct(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> updateProduct(
            @PathVariable Long id,
            @Valid @RequestBody UpdateProductRequest request) {
        return ResponseEntity.ok(productService.updateProduct(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        productService.deleteProduct(id);
        return ResponseEntity.noContent().build();
    }
}
```

**Best Practices:**
- Keep domain logic in domain models (aggregates)
- Use value objects for type safety (Money, Email, etc.)
- Separate domain models from JPA entities
- Use DTOs (preferably Java records) for API contracts
- Apply `@Transactional` at service layer
- Return appropriate HTTP status codes (201, 200, 204)
- Implement pagination for list endpoints
- Use mappers (MapStruct or manual) for conversions

**References:**
- `skills/spring-boot/spring-boot-crud-patterns/SKILL.md`
- `skills/spring-boot/spring-boot-crud-patterns/references/examples-product-feature.md`

---

### spring-boot-event-driven-patterns

**Purpose**: Implement event-driven architecture using Spring's event publishing and handling mechanisms.

**When to use:**
- Decoupling business logic components
- Implementing domain events (DDD pattern)
- Asynchronous processing
- Audit logging and notifications
- Integration with message brokers (Kafka, RabbitMQ)

**Key Patterns:**

1. **Domain Events**
```java
public record UserRegisteredEvent(
    UUID userId,
    String email,
    String name,
    Instant timestamp
) {}
```

2. **Publishing Events**
```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public User registerUser(UserRegistrationRequest request) {
        User user = User.create(request.email(), request.name());
        User saved = userRepository.save(user);
        
        // Publish domain event
        eventPublisher.publishEvent(new UserRegisteredEvent(
            saved.getId(),
            saved.getEmail(),
            saved.getName(),
            Instant.now()
        ));
        
        return saved;
    }
}
```

3. **Event Listeners**
```java
@Component
@RequiredArgsConstructor
@Slf4j
public class UserEventListener {
    private final EmailService emailService;
    private final AuditService auditService;

    @EventListener
    public void handleUserRegistered(UserRegisteredEvent event) {
        log.info("User registered: {}", event.userId());
        emailService.sendWelcomeEmail(event.email(), event.name());
    }

    @EventListener
    @Async
    public void auditUserRegistration(UserRegisteredEvent event) {
        auditService.log("USER_REGISTERED", event);
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void notifyExternalSystem(UserRegisteredEvent event) {
        // Only called after transaction commits successfully
        externalApi.notifyUserCreated(event);
    }
}
```

4. **Async Event Processing**
```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-event-");
        executor.initialize();
        return executor;
    }
}
```

**Best Practices:**
- Use `@TransactionalEventListener` to ensure events are published only after successful transaction commits
- Apply `@Async` for non-critical event handlers
- Use immutable event objects (Java records)
- Include timestamp and correlation IDs in events
- Handle exceptions in event listeners gracefully
- Consider idempotency for event handlers
- Use dead-letter queues for failed event processing

**References:**
- `skills/spring-boot/spring-boot-event-driven-patterns/SKILL.md`

---

## API & Integration Skills

### spring-boot-rest-api-standards

**Purpose**: Implement REST API design standards and best practices for consistent, maintainable APIs.

**When to use:**
- Creating new REST endpoints
- Designing API contracts and DTOs
- Implementing error handling
- Setting up pagination, filtering, sorting
- Documenting APIs

**REST API Standards:**

1. **Resource-Based URLs**
```
✅ Good:
GET    /api/v1/users           # List users
GET    /api/v1/users/{id}      # Get user
POST   /api/v1/users           # Create user
PUT    /api/v1/users/{id}      # Update user (full)
PATCH  /api/v1/users/{id}      # Update user (partial)
DELETE /api/v1/users/{id}      # Delete user

❌ Avoid:
GET    /api/v1/getUserList
POST   /api/v1/createUser
DELETE /api/v1/removeUser
```

2. **HTTP Status Codes**
```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    @PostMapping
    public ResponseEntity<ProductResponse> create(@Valid @RequestBody CreateProductRequest request) {
        ProductResponse response = productService.create(request);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(response.id())
            .toUri();
        return ResponseEntity.created(location).body(response); // 201 Created
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> get(@PathVariable Long id) {
        return ResponseEntity.ok(productService.get(id)); // 200 OK
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> update(
            @PathVariable Long id,
            @Valid @RequestBody UpdateProductRequest request) {
        return ResponseEntity.ok(productService.update(id, request)); // 200 OK
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build(); // 204 No Content
    }
}
```

3. **DTOs with Validation**
```java
public record CreateProductRequest(
    @NotBlank(message = "Product name is required")
    @Size(min = 3, max = 100, message = "Name must be between 3 and 100 characters")
    String name,

    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.01", message = "Price must be greater than 0")
    BigDecimal price,

    @NotBlank(message = "Category is required")
    String category,

    @Size(max = 500, message = "Description cannot exceed 500 characters")
    String description
) {}
```

4. **Global Exception Handling**
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(MethodArgumentNotValidException ex) {
        Map<String, String> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .collect(Collectors.toMap(
                FieldError::getField,
                FieldError::getDefaultMessage
            ));

        ErrorResponse response = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Validation failed",
            errors,
            Instant.now()
        );

        return ResponseEntity.badRequest().body(response);
    }

    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
        ErrorResponse response = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            null,
            Instant.now()
        );

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception ex) {
        log.error("Unexpected error", ex);
        ErrorResponse response = new ErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "An unexpected error occurred",
            null,
            Instant.now()
        );

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}
```

5. **Pagination**
```java
@GetMapping
public ResponseEntity<Page<ProductResponse>> getAll(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(defaultValue = "name") String sortBy,
        @RequestParam(defaultValue = "ASC") Sort.Direction direction) {
    
    Pageable pageable = PageRequest.of(page, size, Sort.by(direction, sortBy));
    Page<ProductResponse> products = productService.findAll(pageable);
    
    return ResponseEntity.ok(products);
}
```

**Best Practices:**
- Use versioning in URLs (`/api/v1/`)
- Return proper HTTP status codes
- Implement comprehensive validation
- Use DTOs to separate API contracts from domain models
- Provide meaningful error messages
- Implement pagination for large datasets
- Include HATEOAS links for discoverability
- Document APIs with OpenAPI/Swagger

**References:**
- `skills/spring-boot/spring-boot-rest-api-standards/SKILL.md`

---

### spring-boot-openapi-documentation

**Purpose**: Generate comprehensive API documentation using OpenAPI 3.0 specification with SpringDoc.

**When to use:**
- Documenting REST APIs
- Generating interactive API documentation
- Creating API specifications for external consumers
- API versioning and evolution

**Key Patterns:**

1. **Configuration**
```java
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Product API")
                .version("1.0.0")
                .description("RESTful API for product management")
                .contact(new Contact()
                    .name("API Support")
                    .email("api@example.com")
                    .url("https://example.com/support"))
                .license(new License()
                    .name("Apache 2.0")
                    .url("https://www.apache.org/licenses/LICENSE-2.0")))
            .servers(List.of(
                new Server()
                    .url("http://localhost:8080")
                    .description("Development server"),
                new Server()
                    .url("https://api.example.com")
                    .description("Production server")
            ))
            .components(new Components()
                .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                    .type(SecurityScheme.Type.HTTP)
                    .scheme("bearer")
                    .bearerFormat("JWT")));
    }

    @Bean
    public GroupedOpenApi publicApi() {
        return GroupedOpenApi.builder()
            .group("public")
            .pathsToMatch("/api/v1/**")
            .build();
    }
}
```

2. **Controller Documentation**
```java
@RestController
@RequestMapping("/api/v1/products")
@Tag(name = "Products", description = "Product management APIs")
@SecurityRequirement(name = "bearer-jwt")
public class ProductController {

    @Operation(
        summary = "Get product by ID",
        description = "Retrieves a single product by its unique identifier"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Product found",
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = ProductResponse.class)
            )
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Product not found",
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = ErrorResponse.class)
            )
        )
    })
    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(
            @Parameter(description = "Product ID", example = "123")
            @PathVariable Long id) {
        return ResponseEntity.ok(productService.getProduct(id));
    }
}
```

3. **DTO Documentation**
```java
@Schema(description = "Product creation request")
public record CreateProductRequest(
    @Schema(description = "Product name", example = "Laptop", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank
    String name,

    @Schema(description = "Product price in USD", example = "999.99", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotNull
    @DecimalMin("0.01")
    BigDecimal price,

    @Schema(description = "Product category", example = "Electronics")
    String category
) {}
```

**Dependencies:**
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

**Access Points:**
- Swagger UI: `http://localhost:8080/swagger-ui.html`
- OpenAPI JSON: `http://localhost:8080/v3/api-docs`
- OpenAPI YAML: `http://localhost:8080/v3/api-docs.yaml`

**References:**
- `skills/spring-boot/spring-boot-openapi-documentation/SKILL.md`

---

## Resilience & Patterns Skills

### spring-boot-resilience4j

**Purpose**: Implement fault tolerance patterns (circuit breaker, retry, rate limiter) using Resilience4j.

**When to use:**
- Protecting against cascading failures
- Implementing retry logic for transient failures
- Rate limiting API calls
- Bulkhead pattern for resource isolation
- Time limiting for operations

**Key Patterns:**

1. **Circuit Breaker**
```java
@Service
@RequiredArgsConstructor
public class ExternalApiClient {
    
    @CircuitBreaker(name = "externalApi", fallbackMethod = "fallbackGetData")
    public DataResponse getData(String id) {
        return restTemplate.getForObject(
            "https://external-api.com/data/" + id,
            DataResponse.class
        );
    }

    private DataResponse fallbackGetData(String id, Exception ex) {
        log.warn("Circuit breaker fallback triggered for id: {}", id, ex);
        return DataResponse.empty();
    }
}
```

2. **Retry**
```java
@Retry(name = "database", fallbackMethod = "fallbackSave")
public Order saveOrder(Order order) {
    return orderRepository.save(order);
}

private Order fallbackSave(Order order, Exception ex) {
    log.error("Failed to save order after retries", ex);
    throw new OrderPersistenceException("Unable to save order", ex);
}
```

3. **Rate Limiter**
```java
@RateLimiter(name = "apiRateLimit")
@GetMapping("/api/data")
public ResponseEntity<DataResponse> getData() {
    return ResponseEntity.ok(dataService.getData());
}
```

4. **Configuration**
```yaml
resilience4j:
  circuitbreaker:
    instances:
      externalApi:
        sliding-window-size: 10
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
        permitted-number-of-calls-in-half-open-state: 3
        automatic-transition-from-open-to-half-open-enabled: true

  retry:
    instances:
      database:
        max-attempts: 3
        wait-duration: 1s
        exponential-backoff-multiplier: 2

  ratelimiter:
    instances:
      apiRateLimit:
        limit-for-period: 10
        limit-refresh-period: 1s
        timeout-duration: 0s
```

**Best Practices:**
- Always provide fallback methods
- Configure appropriate thresholds based on SLAs
- Monitor circuit breaker state transitions
- Use bulkhead pattern for critical resources
- Test resilience patterns thoroughly

**References:**
- `skills/spring-boot/spring-boot-resilience4j/SKILL.md`

---

### spring-boot-saga-pattern

**Purpose**: Implement distributed transaction patterns using the Saga pattern for microservices.

**When to use:**
- Managing distributed transactions across microservices
- Implementing compensating transactions
- Orchestrating complex business workflows
- Maintaining data consistency in distributed systems

**Saga Types:**

1. **Choreography-Based Saga** (Event-driven)
```java
@Service
@RequiredArgsConstructor
public class OrderSagaOrchestrator {
    private final ApplicationEventPublisher eventPublisher;

    @TransactionalEventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // Step 1: Reserve inventory
        eventPublisher.publishEvent(new ReserveInventoryCommand(event.orderId()));
    }

    @TransactionalEventListener
    public void handleInventoryReserved(InventoryReservedEvent event) {
        // Step 2: Process payment
        eventPublisher.publishEvent(new ProcessPaymentCommand(event.orderId()));
    }

    @TransactionalEventListener
    public void handlePaymentFailed(PaymentFailedEvent event) {
        // Compensating transaction: Release inventory
        eventPublisher.publishEvent(new ReleaseInventoryCommand(event.orderId()));
    }
}
```

2. **Orchestration-Based Saga** (Centralized)
```java
@Service
@RequiredArgsConstructor
public class OrderSaga {
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final ShippingService shippingService;

    @Transactional
    public void executeOrderSaga(CreateOrderRequest request) {
        SagaContext context = new SagaContext();
        
        try {
            // Step 1: Reserve inventory
            inventoryService.reserve(request.items());
            context.recordStep("inventory_reserved");

            // Step 2: Process payment
            paymentService.charge(request.payment());
            context.recordStep("payment_processed");

            // Step 3: Schedule shipping
            shippingService.schedule(request.shippingAddress());
            context.recordStep("shipping_scheduled");

        } catch (Exception e) {
            // Execute compensating transactions in reverse order
            compensate(context);
            throw new SagaExecutionException("Order saga failed", e);
        }
    }

    private void compensate(SagaContext context) {
        if (context.hasStep("shipping_scheduled")) {
            shippingService.cancel();
        }
        if (context.hasStep("payment_processed")) {
            paymentService.refund();
        }
        if (context.hasStep("inventory_reserved")) {
            inventoryService.release();
        }
    }
}
```

**Best Practices:**
- Implement idempotent operations
- Use correlation IDs to track saga execution
- Store saga state for recovery
- Implement timeout handling
- Log all saga steps for debugging
- Use event sourcing for audit trail

**References:**
- `skills/spring-boot/spring-boot-saga-pattern/SKILL.md`

---

## Testing Skills

### spring-boot-test-patterns

**Purpose**: Comprehensive testing strategies using Spring Boot Test, Testcontainers, and modern testing practices.

**When to use:**
- Writing integration tests with real dependencies
- Testing with databases, message brokers, caches
- Testing Spring Boot configuration
- End-to-end API testing

**Key Patterns:**

1. **Integration Test with Testcontainers**
```java
@SpringBootTest
@Testcontainers
class ProductServiceIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"))
        .withDatabaseName("testdb");

    @Container
    @ServiceConnection
    static GenericContainer<?> redis = new GenericContainer<>(
        DockerImageName.parse("redis:7-alpine"))
        .withExposedPorts(6379);

    @Autowired
    private ProductService productService;

    @Test
    void shouldCreateAndRetrieveProduct() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Test Product",
            BigDecimal.valueOf(99.99),
            "Electronics"
        );

        // When
        ProductResponse created = productService.create(request);
        ProductResponse retrieved = productService.getById(created.id());

        // Then
        assertThat(retrieved)
            .isNotNull()
            .satisfies(product -> {
                assertThat(product.name()).isEqualTo("Test Product");
                assertThat(product.price()).isEqualByComparingTo("99.99");
                assertThat(product.category()).isEqualTo("Electronics");
            });
    }
}
```

2. **Web Layer Test**
```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ProductService productService;

    @Test
    void shouldReturnProductWhenExists() throws Exception {
        // Given
        ProductResponse response = new ProductResponse(
            1L,
            "Test Product",
            BigDecimal.valueOf(99.99),
            "Electronics"
        );
        when(productService.getById(1L)).thenReturn(response);

        // When & Then
        mockMvc.perform(get("/api/v1/products/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.name").value("Test Product"))
            .andExpect(jsonPath("$.price").value(99.99));
    }
}
```

**Best Practices:**
- Use `@ServiceConnection` for automatic Testcontainers configuration
- Use static containers for JVM-level reuse
- Write focused tests with minimal context
- Use `@WebMvcTest`, `@DataJpaTest` for slice testing
- Prefer integration tests for critical paths
- Use `@MockitoBean` for external dependencies
- Clean up test data with `@Transactional` or explicit cleanup

**References:**
- `skills/spring-boot/spring-boot-test-patterns/SKILL.md`

---

### spring-boot-security-jwt

**Purpose**: Implement JWT-based authentication and authorization with Spring Security 6.x, including Bearer token handling, OAuth2/OIDC integration, and permission-based access control.

**When to use:**
- Building REST APIs that need stateless authentication
- Implementing single sign-on (SSO) with OAuth2/OIDC
- Securing microservices with JWT tokens
- Building applications with role-based access control (RBAC)
- Creating APIs with permission-based authorization

**Key Features:**
- JWT token generation and validation with JJWT
- Bearer token authentication with Authorization header
- OAuth2/OIDC integration for external providers
- Role-based access control (RBAC)
- Permission-based fine-grained authorization
- Token refresh mechanisms
- Secure password storage with BCrypt
- CORS configuration for SPA integration
- Security headers (CSP, X-Frame-Options, etc.)

**Common Implementation Patterns:**

1. **JWT Token Service**:
```java
@Service
@RequiredArgsConstructor
public class JwtTokenService {

    private final JwtProperties jwtProperties;
    private final long accessTokenExpiration = 3600000; // 1 hour

    public String generateAccessToken(UserDetails user) {
        Date expiryDate = new Date(System.currentTimeMillis() + accessTokenExpiration);

        return Jwts.builder()
            .setSubject(user.getUsername())
            .setIssuedAt(new Date())
            .setExpiration(expiryDate)
            .signWith(jwtProperties.getSecretKey())
            .compact();
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                .setSigningKey(jwtProperties.getSecretKey())
                .build()
                .parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
}
```

2. **Security Configuration**:
```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final AuthenticationProvider authenticationProvider;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/api/v1/public/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/v1/products/**").hasAnyRole("USER", "ADMIN")
                .requestMatchers(HttpMethod.POST, "/api/v1/products/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authenticationProvider(authenticationProvider)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

3. **Permission-Based Authorization**:
```java
@Component("permissionEvaluator")
public class CustomPermissionEvaluator implements PermissionEvaluator {

    private final UserService userService;

    @Override
    public boolean hasPermission(Authentication authentication,
                               Object targetDomainObject, Object permission) {
        if (authentication == null || !authentication.isAuthenticated()) {
            return false;
        }

        String username = authentication.getName();
        String permissionName = permission.toString();
        String resourceName = targetDomainObject.toString();

        return userService.hasPermission(username, permissionName, resourceName);
    }

    @Override
    public boolean hasPermission(Authentication authentication,
                               Serializable targetId, String targetType, Object permission) {
        // Implementation for object-level permissions
        return false;
    }
}
```

4. **OAuth2/OIDC Integration**:
```java
@Configuration
@EnableWebSecurity
public class OAuth2SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .oauth2Login(oauth2 -> oauth2
                .loginPage("/oauth2/authorization/google")
                .defaultSuccessUrl("/dashboard")
                .failureUrl("/login?error=true")
            )
            .oauth2Client(Customizer.withDefaults())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/login", "/error").permitAll()
                .anyRequest().authenticated()
            );

        return http.build();
    }
}
```

**Integration Patterns:**

- **Authentication Controller**: Handle login, registration, token refresh
- **User Details Service**: Implement custom user authentication
- **Permission System**: Domain-specific permission checking
- **Token Validation**: Centralized token validation and refresh
- **Error Handling**: Security-specific error responses

**Best Practices:**
- Use short-lived access tokens (15-60 minutes)
- Implement secure refresh token storage
- Use HTTPS for all authenticated endpoints
- Validate JWT tokens on every request
- Implement proper logout mechanisms
- Use role hierarchy for complex permissions
- Log security events for auditing
- Secure CORS configuration for SPA integration

**References:**
- `skills/spring-boot/spring-boot-security-jwt/SKILL.md`

---

## Common Workflows

### Building a Complete Feature

```bash
# 1. Define domain model (skills/spring-boot-crud-patterns)
# Create Product aggregate with business logic

# 2. Implement repository (skills/spring-data-jpa)
# Create ProductRepository interface and adapter

# 3. Create application service (skills/spring-boot-dependency-injection)
# Implement ProductService with use cases

# 4. Build REST API (skills/spring-boot-rest-api-standards)
# Create ProductController with proper endpoints

# 5. Add validation (skills/spring-boot-rest-api-standards)
# Implement DTOs with Jakarta validation

# 6. Implement caching (skills/spring-boot-cache)
# Add @Cacheable to frequently accessed methods

# 7. Add observability (skills/spring-boot-actuator)
# Configure health checks and metrics

# 8. Write tests (skills/spring-boot-test-patterns)
# Create integration tests with Testcontainers

# 9. Document API (skills/spring-boot-openapi-documentation)
# Add OpenAPI annotations

# 10. Add resilience (skills/spring-boot-resilience4j)
# Implement circuit breakers for external calls
```

---

## Best Practices

### General Principles

1. **Dependency Injection**
   - Always use constructor injection
   - Mark injected fields as `final`
   - Use `@RequiredArgsConstructor` from Lombok

2. **Architecture**
   - Follow feature-based organization
   - Separate domain, application, infrastructure, presentation
   - Keep domain logic framework-free
   - Use DTOs to separate API contracts from domain models

3. **Testing**
   - Write integration tests with Testcontainers
   - Use slice tests for focused testing
   - Aim for 80%+ test coverage
   - Test critical paths thoroughly

4. **Error Handling**
   - Use `@RestControllerAdvice` for global exception handling
   - Return consistent error responses
   - Log errors with appropriate levels
   - Don't expose sensitive information in error messages

5. **Performance**
   - Implement caching for frequently accessed data
   - Use pagination for large datasets
   - Optimize database queries
   - Monitor performance with Actuator

6. **Security**
   - Validate all inputs
   - Use HTTPS in production
   - Implement proper authentication/authorization
   - Keep dependencies up-to-date

7. **Documentation**
   - Document APIs with OpenAPI
   - Write clear README files
   - Include architecture diagrams
   - Document configuration options

---

## Spring AI Integration

Spring AI extends Spring Boot with artificial intelligence capabilities, providing seamless integration with various AI models and services. While not strictly a Spring Boot subcategory, Spring AI is closely related and often used together with Spring Boot applications.

### spring-ai-mcp-server-patterns

**Purpose**: Implement Model Context Protocol (MCP) servers with Spring AI to extend AI capabilities with custom tools, resources, and prompt templates.

**When to use:**
- Building custom AI tooling and integrations
- Creating domain-specific AI assistants
- Implementing AI-powered automation workflows
- Extending Claude Code or other AI platforms
- Building knowledge management systems

**Key Features:**
- MCP server implementation patterns
- Tool definition and exposure
- Resource management for AI context
- Prompt template engineering
- Spring AI integration patterns
- Domain-specific AI tool creation

**Common Implementation Patterns:**

1. **MCP Server Configuration**:
```java
@Configuration
@EnableMcpServer
public class McpServerConfig {

    @Bean
    public McpServerProperties mcpServerProperties() {
        McpServerProperties props = new McpServerProperties();
        props.setServerName("spring-boot-assistant");
        props.setVersion("1.0.0");
        return props;
    }
}
```

2. **Tool Implementation**:
```java
@Component
@McpTool(name = "database_query", description = "Execute database queries safely")
public class DatabaseQueryTool {

    private final JdbcTemplate jdbcTemplate;

    public DatabaseQueryTool(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @McpToolParameter
    public String execute(@RequestParam String query,
                         @RequestParam(defaultValue = "100") int limit) {
        // Safe query execution with validation
        return jdbcTemplate.queryForList(query, Map.class).stream()
            .limit(limit)
            .toString();
    }
}
```

3. **Resource Management**:
```java
@Component
@McpResource(name = "application_config", description = "Application configuration data")
public class ConfigResource {

    private final Environment environment;

    public ConfigResource(Environment environment) {
        this.environment = environment;
    }

    public Map<String, Object> getConfig() {
        return Map.of(
            "activeProfiles", environment.getActiveProfiles(),
            "properties", extractRelevantProperties()
        );
    }
}
```

**Integration with Spring Boot:**
- Auto-configuration for MCP servers
- Integration with Spring Security
- Configuration management
- Actuator endpoints for monitoring
- Error handling and logging

**References:**
- `skills/spring-ai/spring-ai-mcp-server-patterns/SKILL.md`
- [Spring AI Official Documentation](https://spring.io/projects/spring-ai)

---

## References

- [Contributing Guide](../CONTRIBUTING.md)
- [README](../README.md)

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-08  
