---
name: spring-boot-crud-patterns
description: REST CRUD APIs with Domain-Driven Design, feature-based architecture, Lombok integration and constructor injection patterns
category: backend
tags: [spring-boot, java, ddd, lombok, rest-api, crud, jpa, feature-architecture]
version: 1.0.0
license: MIT
author: Claude Code Development Kit
---

# Spring Boot CRUD Patterns Skill

Essential patterns for building REST CRUD APIs using Domain-Driven Design (DDD) principles with feature-based architecture, Lombok integration and Spring Boot 3.x. This skill focuses on clean separation between domain and infrastructure layers with constructor injection and immutable DTOs.

## When to Use This Skill

Use this skill when you need to:
- Build REST CRUD APIs following DDD and feature-based architecture
- Implement clean separation between domain and infrastructure layers
- Use Lombok to reduce boilerplate code effectively
- Design scalable microservices with proper boundaries
- Implement constructor injection and immutable DTOs
- Build testable applications with domain services and ports
- Follow enterprise Java patterns with Spring Boot 3.x

## Core Concepts

### Feature-Based DDD Architecture

Following Domain-Driven Design principles, the application is organized by features with clear separation between domain and infrastructure layers:

```
feature/product/
├── domain/
│   ├── model/           # Domain entities (Spring-free)
│   ├── repository/      # Domain ports (interfaces)
│   └── service/         # Domain services
├── application/
│   ├── service/         # Use cases (@Service beans)
│   └── dto/             # Immutable DTOs/records
├── presentation/
│   └── rest/            # Controllers and mappers
└── infrastructure/
    └── persistence/     # JPA adapters
```

### Domain Layer (Spring-Free)

**Domain Entity with Lombok:**

```java
// feature/product/domain/model/Product.java
@Getter
@ToString
@EqualsAndHashCode(of = "id")
@NoArgsConstructor(access = AccessLevel.PROTECTED) // JPA requirement
public class Product {
    private ProductId id;
    private String name;
    private String description;
    private Money price;
    private Stock stock;
    private ProductStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @Builder
    private Product(ProductId id, String name, String description,
                   Money price, Stock stock, ProductStatus status) {
        this.id = id;
        this.name = requireNonNull(name, "Name cannot be null");
        this.description = description;
        this.price = requireNonNull(price, "Price cannot be null");
        this.stock = requireNonNull(stock, "Stock cannot be null");
        this.status = status != null ? status : ProductStatus.ACTIVE;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();

        validateInvariants();
    }

    public static Product create(String name, String description,
                               BigDecimal priceAmount, Integer stockQuantity) {
        return Product.builder()
            .name(name)
            .description(description)
            .price(Money.of(priceAmount))
            .stock(Stock.of(stockQuantity))
            .build();
    }

    public void updateDetails(String name, String description, Money price) {
        this.name = requireNonNull(name, "Name cannot be null");
        this.description = description;
        this.price = requireNonNull(price, "Price cannot be null");
        this.updatedAt = LocalDateTime.now();
        validateInvariants();
    }

    public void decreaseStock(Integer quantity) {
        this.stock = stock.decrease(quantity);
        this.updatedAt = LocalDateTime.now();
    }

    public void discontinue() {
        this.status = ProductStatus.DISCONTINUED;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isActive() {
        return status == ProductStatus.ACTIVE;
    }

    public boolean hasLowStock(Integer threshold) {
        return stock.isLowerThan(threshold);
    }

    private void validateInvariants() {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Product name cannot be empty");
        }
        if (price.isNegative()) {
            throw new IllegalArgumentException("Price cannot be negative");
        }
        if (stock.isNegative()) {
            throw new IllegalArgumentException("Stock cannot be negative");
        }
    }
}
```

**Value Objects with Lombok:**

```java
// feature/product/domain/model/Money.java
@Value
@RequiredArgsConstructor(staticName = "of")
public class Money {
    @NonNull BigDecimal amount;
    String currency;

    public Money(BigDecimal amount) {
        this.amount = requireNonNull(amount, "Amount cannot be null");
        this.currency = "EUR";
    }

    public boolean isNegative() {
        return amount.compareTo(BigDecimal.ZERO) < 0;
    }

    public Money add(Money other) {
        return Money.of(amount.add(other.amount), currency);
    }
}

// feature/product/domain/model/Stock.java
@Value
@RequiredArgsConstructor(staticName = "of")
public class Stock {
    @NonNull Integer quantity;

    public boolean isLowerThan(Integer threshold) {
        return quantity < threshold;
    }

    public boolean isNegative() {
        return quantity < 0;
    }

    public Stock decrease(Integer amount) {
        if (amount < 0) {
            throw new IllegalArgumentException("Cannot decrease by negative amount");
        }
        if (quantity - amount < 0) {
            throw new IllegalArgumentException("Insufficient stock");
        }
        return Stock.of(quantity - amount);
    }
}

// feature/product/domain/model/ProductId.java
@Value
@RequiredArgsConstructor(staticName = "of")
public class ProductId {
    @NonNull String value;

    public static ProductId random() {
        return ProductId.of(UUID.randomUUID().toString());
    }
}
```

### Repository Pattern (Domain Port)

**Domain Repository Interface:**

```java
// feature/product/domain/repository/ProductRepository.java
public interface ProductRepository {
    ProductId save(Product product);
    Optional<Product> findById(ProductId id);
    void delete(ProductId id);
    List<Product> findAll();
    List<Product> findAllActive();
}
```

**Infrastructure Adapter with Spring Data:**

```java
// feature/product/infrastructure/persistence/ProductJpaRepository.java
@Repository
public interface ProductJpaRepository extends JpaRepository<ProductJpaEntity, String> {
    List<ProductJpaEntity> findByStatus(String status);
}

// feature/product/infrastructure/persistence/ProductRepositoryAdapter.java
@RequiredArgsConstructor
@Component
public class ProductRepositoryAdapter implements ProductRepository {
    private final ProductJpaRepository jpaRepository;
    private final ProductEntityMapper mapper;

    @Override
    public ProductId save(Product product) {
        ProductJpaEntity entity = mapper.toEntity(product);
        ProductJpaEntity saved = jpaRepository.save(entity);
        return ProductId.of(saved.getId());
    }

    @Override
    public Optional<Product> findById(ProductId id) {
        return jpaRepository.findById(id.getValue())
            .map(mapper::toDomain);
    }

    @Override
    public void delete(ProductId id) {
        jpaRepository.deleteById(id.getValue());
    }

    @Override
    public List<Product> findAll() {
        return jpaRepository.findAll().stream()
            .map(mapper::toDomain)
            .collect(toList());
    }

    @Override
    public List<Product> findAllActive() {
        return jpaRepository.findByStatus("ACTIVE").stream()
            .map(mapper::toDomain)
            .collect(toList());
    }
}
```

### Application Layer (Use Cases)

**Application Service with Constructor Injection:**

```java
// feature/product/application/service/ProductApplicationService.java
@Service
@Slf4j
@RequiredArgsConstructor
@Transactional
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ProductMapper mapper;

    public ProductResponse createProduct(CreateProductRequest request) {
        log.info("Creating product: {}", request.getName());
        
        Product product = Product.create(
            request.getName(),
            request.getDescription(),
            request.getPrice(),
            request.getStockQuantity()
        );

        ProductId id = productRepository.save(product);
        log.info("Product created with id: {}", id.getValue());
        
        return mapper.toResponse(product);
    }

    public ProductResponse updateProduct(String id, UpdateProductRequest request) {
        log.info("Updating product: {}", id);
        
        Product product = productRepository.findById(ProductId.of(id))
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND,
                "Product not found with id: " + id
            ));

        product.updateDetails(
            request.getName(),
            request.getDescription(),
            Money.of(request.getPrice())
        );

        productRepository.save(product);
        return mapper.toResponse(product);
    }

    public ProductResponse findProductById(String id) {
        return productRepository.findById(ProductId.of(id))
            .map(mapper::toResponse)
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND,
                "Product not found with id: " + id
            ));
    }

    public List<ProductResponse> listAllProducts() {
        return productRepository.findAll().stream()
            .map(mapper::toResponse)
            .collect(toList());
    }

    public List<ProductResponse> listActiveProducts() {
        return productRepository.findAllActive().stream()
            .map(mapper::toResponse)
            .collect(toList());
    }

    public void deleteProduct(String id) {
        log.info("Deleting product: {}", id);
        productRepository.delete(ProductId.of(id));
    }
}
```

### Presentation Layer (REST Controller)

**REST Controller with Request/Response DTOs:**

```java
// feature/product/presentation/rest/ProductController.java
@RestController
@RequestMapping("/products")
@RequiredArgsConstructor
@Slf4j
public class ProductController {
    private final ProductApplicationService productService;

    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(
        @Valid @RequestBody CreateProductRequest request) {
        ProductResponse response = productService.createProduct(request);
        return ResponseEntity
            .created(URI.create("/products/" + response.getId()))
            .body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable String id) {
        return ResponseEntity.ok(productService.findProductById(id));
    }

    @GetMapping
    public ResponseEntity<List<ProductResponse>> listProducts(
        @RequestParam(defaultValue = "false") boolean activeOnly) {
        List<ProductResponse> products = activeOnly
            ? productService.listActiveProducts()
            : productService.listAllProducts();
        return ResponseEntity.ok(products);
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> updateProduct(
        @PathVariable String id,
        @Valid @RequestBody UpdateProductRequest request) {
        ProductResponse response = productService.updateProduct(id, request);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable String id) {
        productService.deleteProduct(id);
        return ResponseEntity.noContent().build();
    }
}
```

**Request/Response DTOs with Records:**

```java
// feature/product/application/dto/CreateProductRequest.java
public record CreateProductRequest(
    @NotBlank String name,
    @NotNull BigDecimal price,
    String description,
    @NotNull Integer stockQuantity
) {}

// feature/product/application/dto/UpdateProductRequest.java
public record UpdateProductRequest(
    @NotBlank String name,
    @NotNull BigDecimal price,
    String description
) {}

// feature/product/application/dto/ProductResponse.java
public record ProductResponse(
    String id,
    String name,
    String description,
    BigDecimal price,
    Integer stock,
    String status,
    LocalDateTime createdAt,
    LocalDateTime updatedAt
) {}
```

**Entity Mapper:**

```java
// feature/product/application/mapper/ProductMapper.java
@Component
public class ProductMapper {
    public ProductResponse toResponse(Product product) {
        return new ProductResponse(
            product.getId().getValue(),
            product.getName(),
            product.getDescription(),
            product.getPrice().getAmount(),
            product.getStock().getQuantity(),
            product.getStatus().name(),
            product.getCreatedAt(),
            product.getUpdatedAt()
        );
    }

    public ProductJpaEntity toEntity(Product product) {
        return ProductJpaEntity.builder()
            .id(product.getId().getValue())
            .name(product.getName())
            .description(product.getDescription())
            .price(product.getPrice().getAmount())
            .stock(product.getStock().getQuantity())
            .status(product.getStatus().name())
            .createdAt(product.getCreatedAt())
            .updatedAt(product.getUpdatedAt())
            .build();
    }

    public Product toDomain(ProductJpaEntity entity) {
        return Product.builder()
            .id(ProductId.of(entity.getId()))
            .name(entity.getName())
            .description(entity.getDescription())
            .price(Money.of(entity.getPrice()))
            .stock(Stock.of(entity.getStock()))
            .status(ProductStatus.valueOf(entity.getStatus()))
            .build();
    }
}
```

### JPA Entity

**Persistent Entity:**

```java
// feature/product/infrastructure/persistence/ProductJpaEntity.java
@Entity
@Table(name = "products")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProductJpaEntity {
    @Id
    private String id;
    
    private String name;
    private String description;
    
    @Column(precision = 10, scale = 2)
    private BigDecimal price;
    
    private Integer stock;
    private String status;
    
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

## Testing CRUD Operations

### Unit Tests for Domain Layer

```java
// feature/product/domain/model/ProductTest.java
class ProductTest {

    @Test
    void shouldCreateProductSuccessfully() {
        // Given
        String name = "Test Product";
        String description = "A test product";
        BigDecimal price = new BigDecimal("99.99");
        Integer stock = 100;

        // When
        Product product = Product.create(name, description, price, stock);

        // Then
        assertThat(product.getName()).isEqualTo(name);
        assertThat(product.getPrice().getAmount()).isEqualTo(price);
        assertThat(product.getStock().getQuantity()).isEqualTo(stock);
        assertThat(product.isActive()).isTrue();
    }

    @Test
    void shouldFailCreatingProductWithNullName() {
        // Given, When, Then
        assertThatThrownBy(() -> Product.create(null, "desc", BigDecimal.TEN, 10))
            .isInstanceOf(NullPointerException.class);
    }

    @Test
    void shouldDecreaseStockSuccessfully() {
        // Given
        Product product = Product.create("Product", "Desc", BigDecimal.TEN, 100);

        // When
        product.decreaseStock(30);

        // Then
        assertThat(product.getStock().getQuantity()).isEqualTo(70);
    }

    @Test
    void shouldThrowExceptionWhenDecreasingMoreThanAvailable() {
        // Given
        Product product = Product.create("Product", "Desc", BigDecimal.TEN, 10);

        // When, Then
        assertThatThrownBy(() -> product.decreaseStock(20))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("Insufficient stock");
    }
}
```

### Unit Tests for Application Service

```java
// feature/product/application/service/ProductApplicationServiceTest.java
@ExtendWith(MockitoExtension.class)
class ProductApplicationServiceTest {

    @Mock
    private ProductRepository productRepository;

    @Mock
    private ProductMapper mapper;

    @InjectMocks
    private ProductApplicationService service;

    private ProductResponse productResponse;

    @BeforeEach
    void setUp() {
        productResponse = new ProductResponse(
            "123", "Product", "Desc", BigDecimal.TEN, 100, "ACTIVE", LocalDateTime.now(), LocalDateTime.now()
        );
    }

    @Test
    void shouldCreateProductSuccessfully() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Product", BigDecimal.TEN, "Desc", 100
        );
        Product product = Product.create(request.name(), request.price(), request.description(), request.stockQuantity());
        
        when(mapper.toResponse(any(Product.class))).thenReturn(productResponse);
        when(productRepository.save(any(Product.class))).thenReturn(ProductId.of("123"));

        // When
        ProductResponse response = service.createProduct(request);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.name()).isEqualTo("Product");
        verify(productRepository).save(any(Product.class));
    }

    @Test
    void shouldFindProductByIdSuccessfully() {
        // Given
        String productId = "123";
        Product product = Product.create("Product", "Desc", BigDecimal.TEN, 100);
        
        when(productRepository.findById(ProductId.of(productId)))
            .thenReturn(Optional.of(product));
        when(mapper.toResponse(product)).thenReturn(productResponse);

        // When
        ProductResponse response = service.findProductById(productId);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.name()).isEqualTo(productResponse.name());
    }

    @Test
    void shouldThrowExceptionWhenProductNotFound() {
        // Given
        when(productRepository.findById(any())).thenReturn(Optional.empty());

        // When, Then
        assertThatThrownBy(() -> service.findProductById("invalid"))
            .isInstanceOf(ResponseStatusException.class);
    }

    @Test
    void shouldListAllProductsSuccessfully() {
        // Given
        List<Product> products = List.of(
            Product.create("Product1", "Desc1", BigDecimal.TEN, 100),
            Product.create("Product2", "Desc2", BigDecimal.TWENTY, 50)
        );
        
        when(productRepository.findAll()).thenReturn(products);
        when(mapper.toResponse(any())).thenReturn(productResponse);

        // When
        List<ProductResponse> responses = service.listAllProducts();

        // Then
        assertThat(responses).hasSize(2);
        verify(productRepository).findAll();
    }

    @Test
    void shouldDeleteProductSuccessfully() {
        // Given
        String productId = "123";

        // When
        service.deleteProduct(productId);

        // Then
        verify(productRepository).delete(ProductId.of(productId));
    }
}
```

### Integration Tests with Testcontainers

```java
// feature/product/presentation/rest/ProductControllerIntegrationTest.java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class ProductControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private ProductRepository productRepository;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void shouldCreateProductViaRestApi() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Integration Test Product", BigDecimal.valueOf(149.99), "Test Desc", 50
        );

        // When
        ResponseEntity<ProductResponse> response = restTemplate.postForEntity(
            "/products",
            request,
            ProductResponse.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().name()).isEqualTo("Integration Test Product");
        assertThat(response.getHeaders().getLocation()).isNotNull();
    }

    @Test
    void shouldRetrieveProductByIdViaRestApi() {
        // Given
        Product product = Product.create(
            "Integration Test Product",
            "Test Description",
            new BigDecimal("149.99"),
            50
        );
        ProductId productId = productRepository.save(product);

        // When
        ResponseEntity<ProductResponse> response = restTemplate.getForEntity(
            "/products/" + productId.getValue(),
            ProductResponse.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().name()).isEqualTo("Integration Test Product");
    }

    @Test
    void shouldUpdateProductViaRestApi() {
        // Given
        Product product = Product.create("Original", "Original Desc", BigDecimal.TEN, 100);
        ProductId productId = productRepository.save(product);
        
        UpdateProductRequest request = new UpdateProductRequest(
            "Updated", BigDecimal.TWENTY, "Updated Desc"
        );

        // When
        ResponseEntity<ProductResponse> response = restTemplate.exchange(
            "/products/" + productId.getValue(),
            HttpMethod.PUT,
            new HttpEntity<>(request),
            ProductResponse.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().name()).isEqualTo("Updated");
    }

    @Test
    void shouldDeleteProductViaRestApi() {
        // Given
        Product product = Product.create("To Delete", "Desc", BigDecimal.TEN, 100);
        ProductId productId = productRepository.save(product);

        // When
        ResponseEntity<Void> response = restTemplate.exchange(
            "/products/" + productId.getValue(),
            HttpMethod.DELETE,
            null,
            Void.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NO_CONTENT);
    }

    @Test
    void shouldListProductsViaRestApi() {
        // Given
        productRepository.save(Product.create("Product1", "Desc1", BigDecimal.TEN, 100));
        productRepository.save(Product.create("Product2", "Desc2", BigDecimal.TWENTY, 50));

        // When
        ResponseEntity<ProductResponse[]> response = restTemplate.getForEntity(
            "/products",
            ProductResponse[].class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).hasLengthGreaterThanOrEqualTo(2);
    }

    @Test
    void shouldReturnNotFoundForInvalidProductId() {
        // When
        ResponseEntity<String> response = restTemplate.getForEntity(
            "/products/invalid-id",
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void shouldValidateCreateProductRequest() {
        // Given - request with invalid data
        CreateProductRequest request = new CreateProductRequest(
            "", // empty name
            new BigDecimal("-10"), // negative price
            "Desc",
            -5 // negative stock
        );

        // When
        ResponseEntity<String> response = restTemplate.postForEntity(
            "/products",
            request,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
    }
}
```

## Build Configuration

### Maven Dependencies

```xml
<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Spring Data JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- Database -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>1.18.30</version>
        <scope>provided</scope>
    </dependency>

    <!-- Validation -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>

    <!-- Testing -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>

    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers</artifactId>
        <version>1.19.0</version>
        <scope>test</scope>
    </dependency>

    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <version>1.19.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### Gradle Dependencies

```gradle
dependencies {
    // Spring Boot Web
    implementation 'org.springframework.boot:spring-boot-starter-web'

    // Spring Data JPA
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'

    // Database
    runtimeOnly 'org.postgresql:postgresql'

    // Lombok
    compileOnly 'org.projectlombok:lombok:1.18.30'
    annotationProcessor 'org.projectlombok:lombok:1.18.30'

    // Validation
    implementation 'org.springframework.boot:spring-boot-starter-validation'

    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.testcontainers:testcontainers:1.19.0'
    testImplementation 'org.testcontainers:postgresql:1.19.0'
}
```

## Best Practices

### 1. DDD Architecture Guidelines

**Separation of Concerns:**
- Domain layer remains Spring-free and contains pure business logic
- Infrastructure layer handles persistence and external integrations
- Application layer orchestrates use cases using domain services

**Value Objects:**
- Use `@Value` with Lombok for immutable value objects
- Implement validation in value object constructors
- Favor composition over primitives (Money, ProductId, Stock)

### 2. Lombok Best Practices

**Recommended Annotations:**
- `@RequiredArgsConstructor` for constructor injection
- `@Getter` and `@Setter` only when needed
- `@Value` for immutable DTOs and value objects
- `@Builder` for complex object creation
- `@Slf4j` for logging

**Avoid:**
- `@Data` on JPA entities (use `@Getter`/`@Setter` instead)
- `@AllArgsConstructor` on domain entities (use `@Builder`)
- `@EqualsAndHashCode` without carefully considering which fields to include

### 3. CRUD Best Practices

**Constructor Injection:**
- Always use constructor injection with `@RequiredArgsConstructor`
- Never use field injection with `@Autowired`
- Dependencies are explicit and testable

**Immutable DTOs:**
- Use Java records for DTOs (Java 16+)
- Implement validation at record level
- Separate request and response DTOs

**Error Handling:**
- Use `ResponseStatusException` for REST errors
- Provide meaningful error messages
- Return appropriate HTTP status codes

**Pagination (Optional):**
```java
@GetMapping
public ResponseEntity<Page<ProductResponse>> listProducts(
    @PageableDefault(size = 20) Pageable pageable) {
    Page<Product> products = productRepository.findAll(pageable);
    return ResponseEntity.ok(
        products.map(mapper::toResponse)
    );
}
```

## Configuration Examples

### Application Properties for CRUD Application

```properties
# Server Configuration
server.port=8080
server.servlet.context-path=/api

# Database Configuration
spring.datasource.url=jdbc:postgresql://localhost:5432/productdb
spring.datasource.username=${DB_USERNAME:postgres}
spring.datasource.password=${DB_PASSWORD:password}

# JPA Configuration with proper DDL
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
spring.jpa.properties.hibernate.jdbc.batch_size=20
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true

# Flyway for database migrations
spring.flyway.baseline-on-migrate=true
spring.flyway.locations=classpath:db/migration
spring.flyway.validate-on-migrate=true

# Actuator for monitoring
management.endpoints.web.exposure.include=health,info,metrics,prometheus
management.endpoint.health.show-details=always
management.endpoint.health.probes.enabled=true

# Logging Configuration
logging.level.com.example=INFO
logging.level.org.springframework.web=DEBUG
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n
```

## Summary

This Spring Boot CRUD Patterns skill provides:

1. **Feature-based DDD Architecture** with clean separation between domain, application, and infrastructure layers
2. **Lombok Integration** for reducing boilerplate code while maintaining readability
3. **Spring-free Domain Layer** with pure business logic and domain entities
4. **Complete REST CRUD API** following hexagonal architecture principles
5. **Comprehensive Testing** strategies for all layers including domain, application, and integration tests
6. **Production-ready Configurations** with proper database setup and monitoring

These patterns enable you to build scalable, maintainable, and testable Spring Boot applications following modern enterprise development practices with Domain-Driven Design principles.
