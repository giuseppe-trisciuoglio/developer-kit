---
name: spring-boot-patterns
description: Essential Spring Boot patterns with DDD architecture, Lombok integration, REST CRUD APIs and Event-Driven Architecture using feature-based structure
category: backend
tags: [spring-boot, java, ddd, lombok, rest-api, crud, event-driven, microservices, jpa, messaging, feature-architecture]
version: 1.0.0
license: MIT
author: Claude Code Development Kit
---

# Spring Boot Patterns Skill

Essential patterns for building modern Spring Boot applications following Domain-Driven Design (DDD) principles with feature-based architecture, Lombok integration, REST CRUD APIs and Event-Driven Architecture (EDA). This skill covers enterprise-grade development using Spring Boot 3.x with Java 16+ and constructor injection.

## When to Use This Skill

Use this skill when you need to:
- Build REST CRUD APIs following DDD and feature-based architecture
- Implement clean separation between domain and infrastructure layers
- Use Lombok to reduce boilerplate code effectively
- Create Event-Driven Architecture with domain events
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
        if (price.isNegativeOrZero()) {
            throw new IllegalArgumentException("Product price must be positive");
        }
    }
}

// Value Objects with Lombok
@Value
@Builder
public class ProductId {
    Long value;

    public static ProductId of(Long value) {
        return ProductId.builder().value(value).build();
    }
}

@Value
@Builder
public class Money {
    BigDecimal amount;

    public static Money of(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount cannot be negative");
        }
        return Money.builder().amount(amount).build();
    }

    public boolean isNegativeOrZero() {
        return amount.compareTo(BigDecimal.ZERO) <= 0;
    }
}

@Value
@Builder
public class Stock {
    Integer quantity;

    public static Stock of(Integer quantity) {
        if (quantity == null || quantity < 0) {
            throw new IllegalArgumentException("Stock quantity cannot be negative");
        }
        return Stock.builder().quantity(quantity).build();
    }

    public Stock decrease(Integer amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Decrease amount must be positive");
        }
        if (quantity < amount) {
            throw new IllegalArgumentException("Insufficient stock");
        }
        return Stock.of(quantity - amount);
    }

    public boolean isLowerThan(Integer threshold) {
        return quantity < threshold;
    }
}

public enum ProductStatus {
    ACTIVE, INACTIVE, DISCONTINUED
}
```

**Domain Repository Interface (Port):**

```java
// feature/product/domain/repository/ProductRepository.java
public interface ProductRepository {
    Optional<Product> findById(ProductId id);
    List<Product> findByStatus(ProductStatus status);
    List<Product> findByNameContaining(String name);
    List<Product> findLowStockProducts(Integer threshold);
    Page<Product> findAll(Pageable pageable);
    Product save(Product product);
    void deleteById(ProductId id);
    boolean existsById(ProductId id);
}

// feature/product/domain/service/ProductDomainService.java
@Slf4j
public class ProductDomainService {

    public void validateProductCreation(String name, BigDecimal price, Integer stock) {
        if (name == null || name.trim().isEmpty()) {
            throw new ProductValidationException("Product name is required");
        }
        if (price == null || price.compareTo(BigDecimal.ZERO) <= 0) {
            throw new ProductValidationException("Product price must be positive");
        }
        if (stock == null || stock < 0) {
            throw new ProductValidationException("Product stock cannot be negative");
        }
    }

    public boolean shouldReorder(Product product, Integer reorderThreshold) {
        return product.hasLowStock(reorderThreshold) && product.isActive();
    }

    public Money calculateDiscountedPrice(Product product, BigDecimal discountPercentage) {
        if (discountPercentage.compareTo(BigDecimal.ZERO) < 0 ||
            discountPercentage.compareTo(new BigDecimal("100")) > 0) {
            throw new IllegalArgumentException("Discount percentage must be between 0 and 100");
        }

        BigDecimal discount = product.getPrice().getAmount()
            .multiply(discountPercentage)
            .divide(new BigDecimal("100"), 2, RoundingMode.HALF_UP);

        return Money.of(product.getPrice().getAmount().subtract(discount));
    }
}
```

### Application Layer

**DTOs with Records and Lombok:**

```java
// feature/product/application/dto/ProductDto.java
public record CreateProductRequest(
    @NotBlank(message = "Name is required")
    String name,

    String description,

    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.0", inclusive = false, message = "Price must be positive")
    BigDecimal price,

    @NotNull(message = "Stock is required")
    @Min(value = 0, message = "Stock cannot be negative")
    Integer stock
) {}

public record UpdateProductRequest(
    @NotBlank(message = "Name is required")
    String name,

    String description,

    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.0", inclusive = false, message = "Price must be positive")
    BigDecimal price,

    @NotNull(message = "Stock is required")
    @Min(value = 0, message = "Stock cannot be negative")
    Integer stock
) {}

@Value
@Builder
public class ProductResponse {
    Long id;
    String name;
    String description;
    BigDecimal price;
    Integer stock;
    ProductStatus status;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;

    public static ProductResponse from(Product product) {
        return ProductResponse.builder()
            .id(product.getId().getValue())
            .name(product.getName())
            .description(product.getDescription())
            .price(product.getPrice().getAmount())
            .stock(product.getStock().getQuantity())
            .status(product.getStatus())
            .createdAt(product.getCreatedAt())
            .updatedAt(product.getUpdatedAt())
            .build();
    }
}

@Value
@Builder
public class PagedResponse<T> {
    List<T> content;
    int pageNumber;
    int pageSize;
    long totalElements;
    int totalPages;
    boolean last;
}
```

**Application Service (Use Cases):**

```java
// feature/product/application/service/ProductApplicationService.java
@Service
@Transactional
@RequiredArgsConstructor
@Slf4j
public class ProductApplicationService {

    private final ProductRepository productRepository;
    private final ProductDomainService productDomainService;
    private final ProductEventPublisher eventPublisher;

    @Transactional(readOnly = true)
    public Page<ProductResponse> findAllProducts(Pageable pageable) {
        Page<Product> products = productRepository.findAll(pageable);
        return products.map(ProductResponse::from);
    }

    @Transactional(readOnly = true)
    public Optional<ProductResponse> findProductById(Long id) {
        return productRepository.findById(ProductId.of(id))
            .map(ProductResponse::from);
    }

    @Transactional(readOnly = true)
    public List<ProductResponse> searchProductsByName(String name) {
        return productRepository.findByNameContaining(name)
            .stream()
            .map(ProductResponse::from)
            .toList();
    }

    public ProductResponse createProduct(CreateProductRequest request) {
        log.info("Creating product: {}", request.name());

        // Domain validation
        productDomainService.validateProductCreation(
            request.name(), request.price(), request.stock()
        );

        // Create domain entity
        Product product = Product.create(
            request.name(),
            request.description(),
            request.price(),
            request.stock()
        );

        // Save and publish event
        Product saved = productRepository.save(product);
        eventPublisher.publishProductCreated(saved);

        log.info("Product created with ID: {}", saved.getId().getValue());
        return ProductResponse.from(saved);
    }

    public Optional<ProductResponse> updateProduct(Long id, UpdateProductRequest request) {
        log.info("Updating product: {}", id);

        return productRepository.findById(ProductId.of(id))
            .map(product -> {
                Money oldPrice = product.getPrice();

                product.updateDetails(
                    request.name(),
                    request.description(),
                    Money.of(request.price())
                );

                Product updated = productRepository.save(product);
                eventPublisher.publishProductUpdated(updated, oldPrice);

                log.info("Product updated: {}", id);
                return ProductResponse.from(updated);
            });
    }

    public boolean deleteProduct(Long id) {
        log.info("Deleting product: {}", id);

        return productRepository.findById(ProductId.of(id))
            .map(product -> {
                product.discontinue();
                productRepository.save(product);
                eventPublisher.publishProductDeleted(product);

                log.info("Product deleted: {}", id);
                return true;
            })
            .orElse(false);
    }

    public boolean decreaseProductStock(Long id, Integer quantity) {
        log.info("Decreasing stock for product {}: {} units", id, quantity);

        return productRepository.findById(ProductId.of(id))
            .map(product -> {
                Integer oldStock = product.getStock().getQuantity();
                product.decreaseStock(quantity);

                Product updated = productRepository.save(product);
                eventPublisher.publishStockDecreased(updated, quantity);

                // Check for reorder if needed
                if (productDomainService.shouldReorder(updated, 10)) {
                    eventPublisher.publishReorderNeeded(updated);
                }

                log.info("Stock decreased for product {}: {} -> {}",
                    id, oldStock, updated.getStock().getQuantity());
                return true;
            })
            .orElse(false);
    }
}
```

### Infrastructure Layer (JPA Adapters)

**JPA Entity with Lombok:**

```java
// feature/product/infrastructure/persistence/ProductJpaEntity.java
@Entity
@Table(name = "products")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EntityListeners(AuditingEntityListener.class)
public class ProductJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private Integer stock;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    private ProductStatus status = ProductStatus.ACTIVE;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Version
    private Long version;

    // Conversion methods
    public static ProductJpaEntity from(Product product) {
        return ProductJpaEntity.builder()
            .id(product.getId() != null ? product.getId().getValue() : null)
            .name(product.getName())
            .description(product.getDescription())
            .price(product.getPrice().getAmount())
            .stock(product.getStock().getQuantity())
            .status(product.getStatus())
            .createdAt(product.getCreatedAt())
            .updatedAt(product.getUpdatedAt())
            .build();
    }

    public Product toDomain() {
        return Product.builder()
            .id(ProductId.of(this.id))
            .name(this.name)
            .description(this.description)
            .price(Money.of(this.price))
            .stock(Stock.of(this.stock))
            .status(this.status)
            .build();
    }
}

// JPA Repository Interface
@Repository
public interface ProductJpaRepository extends JpaRepository<ProductJpaEntity, Long> {

    List<ProductJpaEntity> findByStatus(ProductStatus status);

    List<ProductJpaEntity> findByNameContainingIgnoreCase(String name);

    @Query("SELECT p FROM ProductJpaEntity p WHERE p.stock < :threshold")
    List<ProductJpaEntity> findByStockLessThan(@Param("threshold") Integer threshold);

    Page<ProductJpaEntity> findByStatus(ProductStatus status, Pageable pageable);
}

// Repository Adapter Implementation
@Component
@RequiredArgsConstructor
@Slf4j
public class ProductRepositoryAdapter implements ProductRepository {

    private final ProductJpaRepository jpaRepository;

    @Override
    public Optional<Product> findById(ProductId id) {
        return jpaRepository.findById(id.getValue())
            .map(ProductJpaEntity::toDomain);
    }

    @Override
    public List<Product> findByStatus(ProductStatus status) {
        return jpaRepository.findByStatus(status)
            .stream()
            .map(ProductJpaEntity::toDomain)
            .toList();
    }

    @Override
    public List<Product> findByNameContaining(String name) {
        return jpaRepository.findByNameContainingIgnoreCase(name)
            .stream()
            .map(ProductJpaEntity::toDomain)
            .toList();
    }

    @Override
    public List<Product> findLowStockProducts(Integer threshold) {
        return jpaRepository.findByStockLessThan(threshold)
            .stream()
            .map(ProductJpaEntity::toDomain)
            .toList();
    }

    @Override
    public Page<Product> findAll(Pageable pageable) {
        return jpaRepository.findAll(pageable)
            .map(ProductJpaEntity::toDomain);
    }

    @Override
    public Product save(Product product) {
        ProductJpaEntity entity = ProductJpaEntity.from(product);
        ProductJpaEntity saved = jpaRepository.save(entity);
        return saved.toDomain();
    }

    @Override
    public void deleteById(ProductId id) {
        jpaRepository.deleteById(id.getValue());
    }

    @Override
    public boolean existsById(ProductId id) {
        return jpaRepository.existsById(id.getValue());
    }
}
```

### Presentation Layer (REST Controllers)

**REST Controller with Lombok:**

```java
// feature/product/presentation/rest/ProductController.java
@RestController
@RequestMapping("/api/v1/products")
@RequiredArgsConstructor
@Validated
@Slf4j
public class ProductController {

    private final ProductApplicationService productService;

    @GetMapping
    public PagedResponse<ProductResponse> getAllProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "id") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir) {

        Sort sort = sortDir.equalsIgnoreCase("desc")
            ? Sort.by(sortBy).descending()
            : Sort.by(sortBy).ascending();

        Pageable pageable = PageRequest.of(page, size, sort);
        Page<ProductResponse> products = productService.findAllProducts(pageable);

        return PagedResponse.<ProductResponse>builder()
            .content(products.getContent())
            .pageNumber(products.getNumber())
            .pageSize(products.getSize())
            .totalElements(products.getTotalElements())
            .totalPages(products.getTotalPages())
            .last(products.isLast())
            .build();
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
        return productService.findProductById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/search")
    public List<ProductResponse> searchProducts(@RequestParam String name) {
        return productService.searchProductsByName(name);
    }

    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(
            @Valid @RequestBody CreateProductRequest request) {

        ProductResponse created = productService.createProduct(request);

        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(created.getId())
            .toUri();

        return ResponseEntity.created(location).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> updateProduct(
            @PathVariable Long id,
            @Valid @RequestBody UpdateProductRequest request) {

        return productService.updateProduct(id, request)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        boolean deleted = productService.deleteProduct(id);
        return deleted
            ? ResponseEntity.noContent().build()
            : ResponseEntity.notFound().build();
    }

    @PatchMapping("/{id}/stock/decrease")
    public ResponseEntity<Void> decreaseStock(
            @PathVariable Long id,
            @RequestParam Integer quantity) {

        boolean decreased = productService.decreaseProductStock(id, quantity);
        return decreased
            ? ResponseEntity.ok().build()
            : ResponseEntity.badRequest().build();
    }
}
```

### Event-Driven Architecture (EDA) Pattern

EDA enables loose coupling between components and supports scalable, resilient applications following domain events.

**Domain Events with Lombok:**

```java
// feature/product/domain/event/DomainEvent.java
@Getter
@ToString
@EqualsAndHashCode(of = "eventId")
public abstract class DomainEvent {
    private final String eventId;
    private final LocalDateTime occurredOn;
    private final String eventType;

    protected DomainEvent(String eventType) {
        this.eventId = UUID.randomUUID().toString();
        this.occurredOn = LocalDateTime.now();
        this.eventType = eventType;
    }
}

// Product Domain Events
@Getter
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = true)
public class ProductCreatedEvent extends DomainEvent {
    private final Long productId;
    private final String productName;
    private final BigDecimal price;
    private final Integer initialStock;

    public ProductCreatedEvent(Product product) {
        super("ProductCreated");
        this.productId = product.getId().getValue();
        this.productName = product.getName();
        this.price = product.getPrice().getAmount();
        this.initialStock = product.getStock().getQuantity();
    }
}

@Getter
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = true)
public class ProductUpdatedEvent extends DomainEvent {
    private final Long productId;
    private final String productName;
    private final BigDecimal oldPrice;
    private final BigDecimal newPrice;

    public ProductUpdatedEvent(Product product, Money oldPrice) {
        super("ProductUpdated");
        this.productId = product.getId().getValue();
        this.productName = product.getName();
        this.oldPrice = oldPrice.getAmount();
        this.newPrice = product.getPrice().getAmount();
    }
}

@Getter
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = true)
public class StockDecreasedEvent extends DomainEvent {
    private final Long productId;
    private final Integer quantityDecreased;
    private final Integer remainingStock;

    public StockDecreasedEvent(Product product, Integer quantityDecreased) {
        super("StockDecreased");
        this.productId = product.getId().getValue();
        this.quantityDecreased = quantityDecreased;
        this.remainingStock = product.getStock().getQuantity();
    }
}

@Getter
@ToString(callSuper = true)
@EqualsAndHashCode(callSuper = true)
public class ReorderNeededEvent extends DomainEvent {
    private final Long productId;
    private final String productName;
    private final Integer currentStock;

    public ReorderNeededEvent(Product product) {
        super("ReorderNeeded");
        this.productId = product.getId().getValue();
        this.productName = product.getName();
        this.currentStock = product.getStock().getQuantity();
    }
}
```

**Event Publisher:**

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class ProductEventPublisher {

    private final ApplicationEventPublisher applicationEventPublisher;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publishProductCreated(Product product) {
        ProductCreatedEvent event = new ProductCreatedEvent(product);

        // Publish locally (same JVM)
        applicationEventPublisher.publishEvent(event);

        // Publish to external systems (Kafka)
        publishToKafka("product-events", event);

        log.info("Published ProductCreated event for product: {}", product.getId().getValue());
    }

    public void publishProductUpdated(Product product, Money oldPrice) {
        ProductUpdatedEvent event = new ProductUpdatedEvent(product, oldPrice);

        applicationEventPublisher.publishEvent(event);
        publishToKafka("product-events", event);

        log.info("Published ProductUpdated event for product: {}", product.getId().getValue());
    }

    public void publishProductDeleted(Product product) {
        // Similar implementation
    }

    public void publishStockDecreased(Product product, Integer quantity) {
        StockDecreasedEvent event = new StockDecreasedEvent(product, quantity);

        applicationEventPublisher.publishEvent(event);
        publishToKafka("stock-events", event);

        log.info("Published StockDecreased event for product: {}", product.getId().getValue());
    }

    public void publishReorderNeeded(Product product) {
        ReorderNeededEvent event = new ReorderNeededEvent(product);

        applicationEventPublisher.publishEvent(event);
        publishToKafka("reorder-events", event);

        log.info("Published ReorderNeeded event for product: {}", product.getId().getValue());
    }

    private void publishToKafka(String topic, DomainEvent event) {
        try {
            kafkaTemplate.send(topic, event.getEventId(), event);
        } catch (Exception e) {
            log.error("Failed to publish event to Kafka: {}", event, e);
            // Consider implementing retry logic or dead letter queue
        }
    }
}
```

**Event Listeners:**

```java
// Local event listener (same JVM)
@Component
@RequiredArgsConstructor
@Slf4j
public class ProductEventListener {

    private final EmailNotificationService emailService;
    private final AnalyticsService analyticsService;

    @Async
    @EventListener
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleProductCreated(ProductCreatedEvent event) {
        log.info("Handling ProductCreated event: {}", event.getProductId());

        // Send notification
        emailService.sendProductCreatedNotification(event);

        // Update analytics
        analyticsService.trackProductCreation(event);

        // Update search index
        // searchIndexService.indexProduct(event);
    }

    @Async
    @EventListener
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleStockDecreased(StockDecreasedEvent event) {
        log.info("Handling StockDecreased event for product: {}", event.getProductId());

        if (event.getRemainingStock() < 5) {
            log.warn("Critical stock level for product {}: {} units remaining",
                event.getProductId(), event.getRemainingStock());

            // Send alert notification
            emailService.sendLowStockAlert(event);
        }

        // Update dashboard metrics
        analyticsService.updateStockMetrics(event);
    }

    @Async
    @EventListener
    public void handleReorderNeeded(ReorderNeededEvent event) {
        log.info("Handling ReorderNeeded event for product: {}", event.getProductId());

        // Trigger automated reorder process
        // reorderService.initiateReorder(event.getProductId());

        // Notify purchasing department
        emailService.sendReorderNotification(event);
    }
}

// Kafka event listener (external systems)
@Component
@RequiredArgsConstructor
@Slf4j
public class ProductKafkaListener {

    private final InventoryService inventoryService;
    private final PricingService pricingService;

    @KafkaListener(topics = "product-events", groupId = "inventory-service")
    public void handleProductEvent(ProductCreatedEvent event) {
        log.info("Received ProductCreated event from Kafka: {}", event.getProductId());

        // Update external inventory system
        inventoryService.syncProductCreation(event);
    }

    @KafkaListener(topics = "product-events", groupId = "pricing-service")
    public void handleProductUpdated(ProductUpdatedEvent event) {
        log.info("Received ProductUpdated event from Kafka: {}", event.getProductId());

        // Update pricing history
        pricingService.recordPriceChange(event);
    }

    @KafkaListener(topics = "stock-events", groupId = "warehouse-service")
    public void handleStockEvent(StockDecreasedEvent event) {
        log.info("Received StockDecreased event from Kafka: {}", event.getProductId());

        // Update warehouse management system
        // warehouseService.updateStockLevels(event);
    }
}
```

**Async Configuration:**

```java
@Configuration
@EnableAsync
@RequiredArgsConstructor
public class AsyncConfig {

    @Bean(name = "taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(8);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("product-async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }

    @Bean(name = "eventExecutor")
    public Executor eventExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(4);
        executor.setQueueCapacity(50);
        executor.setThreadNamePrefix("event-");
        executor.initialize();
        return executor;
    }
}
```

## Build Configuration

### Maven Configuration with Lombok

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.5.6</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>spring-boot-ddd-patterns</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>17</java.version>
        <lombok.version>1.18.30</lombok.version>
        <spring-kafka.version>3.0.12</spring-kafka.version>
        <testcontainers.version>1.19.0</testcontainers.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>

        <!-- Kafka for EDA -->
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka</artifactId>
        </dependency>

        <!-- Lombok for reducing boilerplate -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${lombok.version}</version>
            <scope>provided</scope>
        </dependency>

        <!-- Database -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>

        <!-- Test dependencies -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>kafka</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.flywaydb</groupId>
                <artifactId>flyway-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### Gradle Configuration with Lombok

```gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
    id 'org.flywaydb.flyway' version '9.22.3'
}

group = 'com.example'
version = '1.0.0'
sourceCompatibility = '17'

configurations {
    compileOnly {
        extendsFrom annotationProcessor
    }
}

repositories {
    mavenCentral()
}

ext {
    set('lombokVersion', '1.18.30')
    set('springKafkaVersion', '3.0.12')
    set('testcontainersVersion', '1.19.0')
}

dependencies {
    // Spring Boot Starters
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'

    // Kafka for EDA
    implementation 'org.springframework.kafka:spring-kafka'

    // Lombok for reducing boilerplate
    compileOnly "org.projectlombok:lombok:${lombokVersion}"
    annotationProcessor "org.projectlombok:lombok:${lombokVersion}"
    testCompileOnly "org.projectlombok:lombok:${lombokVersion}"
    testAnnotationProcessor "org.projectlombok:lombok:${lombokVersion}"

    // Database
    runtimeOnly 'org.postgresql:postgresql'
    implementation 'org.flywaydb:flyway-core'

    // Test dependencies
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.kafka:spring-kafka-test'
    testImplementation 'org.testcontainers:junit-jupiter'
    testImplementation 'org.testcontainers:postgresql'
    testImplementation 'org.testcontainers:kafka'
}

dependencyManagement {
    imports {
        mavenBom "org.testcontainers:testcontainers-bom:${testcontainersVersion}"
    }
}

tasks.named('test') {
    useJUnitPlatform()
}
```

## Testing Patterns with DDD and Lombok

### Unit Testing Domain Layer

```java
@ExtendWith(MockitoExtension.class)
class ProductDomainServiceTest {

    private ProductDomainService productDomainService;

    @BeforeEach
    void setUp() {
        productDomainService = new ProductDomainService();
    }

    @Test
    void shouldValidateProductCreation() {
        // Given
        String name = "Test Product";
        BigDecimal price = new BigDecimal("99.99");
        Integer stock = 10;

        // When & Then - Should not throw exception
        assertDoesNotThrow(() ->
            productDomainService.validateProductCreation(name, price, stock)
        );
    }

    @Test
    void shouldThrowExceptionWhenProductNameIsEmpty() {
        // Given
        String name = "";
        BigDecimal price = new BigDecimal("99.99");
        Integer stock = 10;

        // When & Then
        assertThatThrownBy(() ->
            productDomainService.validateProductCreation(name, price, stock)
        ).isInstanceOf(ProductValidationException.class)
         .hasMessage("Product name is required");
    }
}

@ExtendWith(MockitoExtension.class)
class ProductTest {

    @Test
    void shouldCreateProductWithValidData() {
        // Given
        String name = "Test Product";
        String description = "Test Description";
        BigDecimal price = new BigDecimal("99.99");
        Integer stock = 10;

        // When
        Product product = Product.create(name, description, price, stock);

        // Then
        assertThat(product.getName()).isEqualTo(name);
        assertThat(product.getDescription()).isEqualTo(description);
        assertThat(product.getPrice().getAmount()).isEqualTo(price);
        assertThat(product.getStock().getQuantity()).isEqualTo(stock);
        assertThat(product.getStatus()).isEqualTo(ProductStatus.ACTIVE);
        assertThat(product.getCreatedAt()).isNotNull();
    }

    @Test
    void shouldDecreaseStockSuccessfully() {
        // Given
        Product product = Product.create("Test", "Desc", new BigDecimal("10"), 20);

        // When
        product.decreaseStock(5);

        // Then
        assertThat(product.getStock().getQuantity()).isEqualTo(15);
    }

    @Test
    void shouldThrowExceptionWhenDecreasingMoreThanAvailableStock() {
        // Given
        Product product = Product.create("Test", "Desc", new BigDecimal("10"), 5);

        // When & Then
        assertThatThrownBy(() -> product.decreaseStock(10))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("Insufficient stock");
    }
}
```

### Integration Testing with Testcontainers

```java
@SpringBootTest
@Testcontainers
@Transactional
class ProductApplicationServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @Container
    static KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.4.0"));

    @Autowired
    private ProductApplicationService productService;

    @Autowired
    private TestRestTemplate restTemplate;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Test
    void shouldCreateAndRetrieveProduct() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Integration Test Product",
            "Test Description",
            new BigDecimal("149.99"),
            20
        );

        // When
        ProductResponse created = productService.createProduct(request);

        // Then
        assertThat(created.getName()).isEqualTo("Integration Test Product");
        assertThat(created.getPrice()).isEqualTo(new BigDecimal("149.99"));

        // Verify retrieval
        Optional<ProductResponse> retrieved = productService.findProductById(created.getId());
        assertThat(retrieved).isPresent();
        assertThat(retrieved.get().getName()).isEqualTo("Integration Test Product");
    }
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

### 3. Event-Driven Best Practices

**Event Design:**
- Events should be immutable and contain all necessary data
- Use past-tense naming (ProductCreated, not CreateProduct)
- Include correlation IDs for tracing

**Event Handling:**
- Use `@TransactionalEventListener` for database consistency
- Implement idempotency in event handlers
- Handle failures gracefully with retry mechanisms

## Configuration Examples

### Application Properties for DDD Application

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

# Enable JPA Auditing
spring.jpa.properties.hibernate.integration.envers.enabled=false

# Flyway for database migrations
spring.flyway.baseline-on-migrate=true
spring.flyway.locations=classpath:db/migration
spring.flyway.validate-on-migrate=true

# Kafka Configuration
spring.kafka.bootstrap-servers=${KAFKA_SERVERS:localhost:9092}
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer
spring.kafka.producer.properties.spring.json.add.type.headers=false

spring.kafka.consumer.group-id=product-service
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.springframework.kafka.support.serializer.JsonDeserializer
spring.kafka.consumer.properties.spring.json.trusted.packages=*
spring.kafka.consumer.properties.spring.json.use.type.headers=false

# Actuator for monitoring
management.endpoints.web.exposure.include=health,info,metrics,prometheus
management.endpoint.health.show-details=always
management.endpoint.health.probes.enabled=true

# Logging Configuration
logging.level.com.example=INFO
logging.level.org.springframework.kafka=WARN
logging.level.org.springframework.transaction=DEBUG
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n
```

## Summary

This Spring Boot Patterns skill with DDD and Lombok provides:

1. **Feature-based DDD Architecture** with clean separation between domain, application, and infrastructure layers
2. **Lombok Integration** for reducing boilerplate code while maintaining readability
3. **Spring-free Domain Layer** with pure business logic and domain entities
4. **Complete REST CRUD API** following hexagonal architecture principles
5. **Event-Driven Architecture** with domain events and both local and distributed event handling
6. **Comprehensive Testing** strategies for all layers including domain, application, and integration tests
7. **Production-ready Configurations** with proper database setup, Kafka integration, and monitoring

These patterns enable you to build scalable, maintainable, and testable Spring Boot applications following modern enterprise development practices with Domain-Driven Design principles.
