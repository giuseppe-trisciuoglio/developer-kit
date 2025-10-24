---
name: spring-boot-event-driven-patterns
description: Event-Driven Architecture implementation with Spring Boot, domain events, event publishing, and distributed messaging with Kafka and Spring Cloud Stream
category: backend
tags: [spring-boot, java, event-driven, eda, kafka, messaging, domain-events, microservices, spring-cloud-stream]
version: 1.0.0
license: MIT
author: Claude Code Development Kit
---

# Spring Boot Event-Driven Patterns Skill

Essential patterns for implementing Event-Driven Architecture (EDA) using Spring Boot 3.x with domain events, event publishing, distributed messaging with Kafka, and event handlers. This skill covers both local and distributed event handling with Spring Cloud Stream and transactional event listeners.

## When to Use This Skill

Use this skill when you need to:
- Implement Event-Driven Architecture in microservices
- Create and publish domain events from aggregate roots
- Handle events with transactional event listeners
- Implement distributed messaging with Kafka
- Use Spring Cloud Stream for event streaming
- Ensure event consistency with transactional outbox pattern
- Build reactive systems with event-driven workflows
- Handle asynchronous communication between services
- Implement event sourcing foundations

## Core Concepts

### Domain Events (Event-Driven Architecture)

**Domain Event Base Class:**

```java
// feature/product/domain/event/DomainEvent.java
public abstract class DomainEvent {
    private final UUID eventId;
    private final LocalDateTime occurredAt;
    private final UUID correlationId;

    protected DomainEvent() {
        this.eventId = UUID.randomUUID();
        this.occurredAt = LocalDateTime.now();
        this.correlationId = UUID.randomUUID();
    }

    protected DomainEvent(UUID correlationId) {
        this.eventId = UUID.randomUUID();
        this.occurredAt = LocalDateTime.now();
        this.correlationId = correlationId;
    }

    public UUID getEventId() {
        return eventId;
    }

    public LocalDateTime getOccurredAt() {
        return occurredAt;
    }

    public UUID getCorrelationId() {
        return correlationId;
    }
}
```

**Domain Events:**

```java
// feature/product/domain/event/ProductCreatedEvent.java
public class ProductCreatedEvent extends DomainEvent {
    private final ProductId productId;
    private final String name;
    private final BigDecimal price;
    private final Integer stock;

    public ProductCreatedEvent(ProductId productId, String name, BigDecimal price, Integer stock) {
        super();
        this.productId = productId;
        this.name = name;
        this.price = price;
        this.stock = stock;
    }

    public ProductId getProductId() {
        return productId;
    }

    public String getName() {
        return name;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public Integer getStock() {
        return stock;
    }
}

// feature/product/domain/event/ProductStockDecreatedEvent.java
public class ProductStockDecreasedEvent extends DomainEvent {
    private final ProductId productId;
    private final Integer quantity;
    private final Integer remainingStock;

    public ProductStockDecreasedEvent(ProductId productId, Integer quantity, Integer remainingStock) {
        super();
        this.productId = productId;
        this.quantity = quantity;
        this.remainingStock = remainingStock;
    }

    public ProductId getProductId() {
        return productId;
    }

    public Integer getQuantity() {
        return quantity;
    }

    public Integer getRemainingStock() {
        return remainingStock;
    }
}

// feature/product/domain/event/ProductLowStockEvent.java
public class ProductLowStockEvent extends DomainEvent {
    private final ProductId productId;
    private final Integer currentStock;
    private final Integer threshold;

    public ProductLowStockEvent(ProductId productId, Integer currentStock, Integer threshold) {
        super();
        this.productId = productId;
        this.currentStock = currentStock;
        this.threshold = threshold;
    }

    public ProductId getProductId() {
        return productId;
    }

    public Integer getCurrentStock() {
        return currentStock;
    }

    public Integer getThreshold() {
        return threshold;
    }
}

// feature/product/domain/event/ProductDiscontinuedEvent.java
public class ProductDiscontinuedEvent extends DomainEvent {
    private final ProductId productId;
    private final String reason;

    public ProductDiscontinuedEvent(ProductId productId, String reason) {
        super();
        this.productId = productId;
        this.reason = reason;
    }

    public ProductId getProductId() {
        return productId;
    }

    public String getReason() {
        return reason;
    }
}
```

### Aggregate Root with Event Publishing

**Domain Entity Publishing Events:**

```java
// feature/product/domain/model/Product.java
@Getter
@ToString
@EqualsAndHashCode(of = "id")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Product {
    private ProductId id;
    private String name;
    private String description;
    private Money price;
    private Stock stock;
    private ProductStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    @Transient
    private List<DomainEvent> domainEvents = new ArrayList<>();

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
        this.domainEvents = new ArrayList<>();

        validateInvariants();
    }

    public static Product create(String name, String description,
                               BigDecimal priceAmount, Integer stockQuantity) {
        Product product = Product.builder()
            .name(name)
            .description(description)
            .price(Money.of(priceAmount))
            .stock(Stock.of(stockQuantity))
            .build();
        
        product.publishEvent(new ProductCreatedEvent(
            product.id, name, priceAmount, stockQuantity
        ));
        
        return product;
    }

    public void decreaseStock(Integer quantity) {
        Integer previousStock = this.stock.getQuantity();
        this.stock = stock.decrease(quantity);
        this.updatedAt = LocalDateTime.now();
        
        publishEvent(new ProductStockDecreasedEvent(
            id, quantity, this.stock.getQuantity()
        ));
        
        // Check for low stock condition
        Integer lowStockThreshold = 10;
        if (this.stock.isLowerThan(lowStockThreshold)) {
            publishEvent(new ProductLowStockEvent(
                id, this.stock.getQuantity(), lowStockThreshold
            ));
        }
    }

    public void discontinue(String reason) {
        this.status = ProductStatus.DISCONTINUED;
        this.updatedAt = LocalDateTime.now();
        
        publishEvent(new ProductDiscontinuedEvent(id, reason));
    }

    public List<DomainEvent> getDomainEvents() {
        return new ArrayList<>(domainEvents);
    }

    public void clearDomainEvents() {
        domainEvents.clear();
    }

    private void publishEvent(DomainEvent event) {
        domainEvents.add(event);
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

### Application Event Publishing

**Application Service Publishing Events:**

```java
// feature/product/application/service/ProductApplicationService.java
@Service
@Slf4j
@RequiredArgsConstructor
@Transactional
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ApplicationEventPublisher eventPublisher;
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
        
        publishDomainEvents(product);
        log.info("Product created with id: {}", id.getValue());
        
        return mapper.toResponse(product);
    }

    public void decreaseProductStock(String productId, Integer quantity) {
        log.info("Decreasing stock for product: {} by quantity: {}", productId, quantity);
        
        Product product = productRepository.findById(ProductId.of(productId))
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND,
                "Product not found with id: " + productId
            ));

        product.decreaseStock(quantity);
        productRepository.save(product);
        
        publishDomainEvents(product);
    }

    public void discontinueProduct(String productId, String reason) {
        log.info("Discontinuing product: {} with reason: {}", productId, reason);
        
        Product product = productRepository.findById(ProductId.of(productId))
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND,
                "Product not found with id: " + productId
            ));

        product.discontinue(reason);
        productRepository.save(product);
        
        publishDomainEvents(product);
    }

    private void publishDomainEvents(Product product) {
        product.getDomainEvents().forEach(event -> {
            log.debug("Publishing domain event: {}", event.getClass().getSimpleName());
            eventPublisher.publishEvent(event);
        });
        product.clearDomainEvents();
    }
}
```

### Local Event Handling with @TransactionalEventListener

**Local Event Handlers:**

```java
// feature/product/application/handler/ProductEventHandler.java
@Component
@Slf4j
@RequiredArgsConstructor
public class ProductEventHandler {
    private final NotificationService notificationService;
    private final InventoryService inventoryService;
    private final ProductAuditService auditService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductCreated(ProductCreatedEvent event) {
        log.info("Handling ProductCreatedEvent for product: {}", event.getProductId());
        
        auditService.logProductCreation(
            event.getProductId().getValue(),
            event.getName(),
            event.getPrice(),
            event.getCorrelationId()
        );
        
        notificationService.sendProductCreatedNotification(
            event.getName(),
            event.getPrice()
        );
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductStockDecreased(ProductStockDecreasedEvent event) {
        log.info("Handling ProductStockDecreasedEvent for product: {}", event.getProductId());
        
        inventoryService.recordStockDecrement(
            event.getProductId().getValue(),
            event.getQuantity()
        );
        
        auditService.logStockChange(
            event.getProductId().getValue(),
            -event.getQuantity(),
            event.getCorrelationId()
        );
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductLowStock(ProductLowStockEvent event) {
        log.warn("Handling ProductLowStockEvent for product: {} with stock: {}",
            event.getProductId(), event.getCurrentStock());
        
        notificationService.sendLowStockAlert(
            event.getProductId().getValue(),
            event.getCurrentStock(),
            event.getThreshold()
        );
        
        inventoryService.triggerReorderProcess(event.getProductId().getValue());
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductDiscontinued(ProductDiscontinuedEvent event) {
        log.info("Handling ProductDiscontinuedEvent for product: {}", event.getProductId());
        
        auditService.logProductDiscontinuation(
            event.getProductId().getValue(),
            event.getReason(),
            event.getCorrelationId()
        );
        
        notificationService.sendProductDiscontinuedNotification(event.getProductId().getValue());
    }
}
```

### Distributed Event Publishing with Kafka

**Event Publisher Configuration:**

```java
// feature/product/infrastructure/messaging/ProductEventPublisher.java
@Component
@Slf4j
@RequiredArgsConstructor
public class ProductEventPublisher {
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publishProductCreatedEvent(ProductCreatedEvent event) {
        log.info("Publishing ProductCreatedEvent to Kafka: {}", event.getProductId());
        
        kafkaTemplate.executeInTransaction(template -> {
            template.send("product-events", 
                event.getProductId().getValue(), 
                new ProductCreatedEventDto(
                    event.getEventId(),
                    event.getProductId().getValue(),
                    event.getName(),
                    event.getPrice(),
                    event.getStock(),
                    event.getOccurredAt(),
                    event.getCorrelationId()
                )
            );
            return null;
        });
    }

    public void publishProductStockDecreasedEvent(ProductStockDecreasedEvent event) {
        log.info("Publishing ProductStockDecreasedEvent to Kafka: {}", event.getProductId());
        
        kafkaTemplate.send("product-events",
            event.getProductId().getValue(),
            new ProductStockDecreasedEventDto(
                event.getEventId(),
                event.getProductId().getValue(),
                event.getQuantity(),
                event.getRemainingStock(),
                event.getOccurredAt(),
                event.getCorrelationId()
            )
        );
    }

    public void publishProductLowStockEvent(ProductLowStockEvent event) {
        log.info("Publishing ProductLowStockEvent to Kafka: {}", event.getProductId());
        
        kafkaTemplate.send("product-events",
            event.getProductId().getValue(),
            new ProductLowStockEventDto(
                event.getEventId(),
                event.getProductId().getValue(),
                event.getCurrentStock(),
                event.getThreshold(),
                event.getOccurredAt(),
                event.getCorrelationId()
            )
        );
    }

    public void publishProductDiscontinuedEvent(ProductDiscontinuedEvent event) {
        log.info("Publishing ProductDiscontinuedEvent to Kafka: {}", event.getProductId());
        
        kafkaTemplate.send("product-events",
            event.getProductId().getValue(),
            new ProductDiscontinuedEventDto(
                event.getEventId(),
                event.getProductId().getValue(),
                event.getReason(),
                event.getOccurredAt(),
                event.getCorrelationId()
            )
        );
    }
}
```

**Event DTOs for Serialization:**

```java
// feature/product/infrastructure/messaging/dto/ProductCreatedEventDto.java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ProductCreatedEventDto {
    private UUID eventId;
    private String productId;
    private String name;
    private BigDecimal price;
    private Integer stock;
    private LocalDateTime occurredAt;
    private UUID correlationId;
}

// feature/product/infrastructure/messaging/dto/ProductStockDecreasedEventDto.java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ProductStockDecreasedEventDto {
    private UUID eventId;
    private String productId;
    private Integer quantity;
    private Integer remainingStock;
    private LocalDateTime occurredAt;
    private UUID correlationId;
}

// feature/product/infrastructure/messaging/dto/ProductLowStockEventDto.java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ProductLowStockEventDto {
    private UUID eventId;
    private String productId;
    private Integer currentStock;
    private Integer threshold;
    private LocalDateTime occurredAt;
    private UUID correlationId;
}

// feature/product/infrastructure/messaging/dto/ProductDiscontinuedEventDto.java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ProductDiscontinuedEventDto {
    private UUID eventId;
    private String productId;
    private String reason;
    private LocalDateTime occurredAt;
    private UUID correlationId;
}
```

### Transactional Outbox Pattern

**Outbox Entity for Event Persistence:**

```java
// feature/product/infrastructure/persistence/OutboxEvent.java
@Entity
@Table(name = "outbox_events")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OutboxEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String aggregateId;
    private String aggregateType;
    private String eventType;
    
    @Column(columnDefinition = "TEXT")
    private String payload;
    
    private UUID correlationId;
    private LocalDateTime createdAt;
    private LocalDateTime publishedAt;
    private Integer retryCount;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        retryCount = 0;
    }
}

// feature/product/infrastructure/persistence/OutboxEventRepository.java
@Repository
public interface OutboxEventRepository extends JpaRepository<OutboxEvent, UUID> {
    List<OutboxEvent> findByPublishedAtIsNullOrderByCreatedAt();
    List<OutboxEvent> findByPublishedAtIsNullAndRetryCountLessThanOrderByCreatedAt(Integer maxRetries);
}

// feature/product/infrastructure/messaging/OutboxEventPublisher.java
@Component
@Slf4j
@RequiredArgsConstructor
public class OutboxEventPublisher {
    private final OutboxEventRepository outboxRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Transactional
    public void publishEvent(String aggregateId, String aggregateType,
                            String eventType, Object payload, UUID correlationId) {
        try {
            String payloadJson = objectMapper.writeValueAsString(payload);
            
            OutboxEvent outboxEvent = OutboxEvent.builder()
                .aggregateId(aggregateId)
                .aggregateType(aggregateType)
                .eventType(eventType)
                .payload(payloadJson)
                .correlationId(correlationId)
                .build();
            
            outboxRepository.save(outboxEvent);
            log.info("Outbox event created: {} - {}", aggregateId, eventType);
        } catch (Exception e) {
            log.error("Failed to create outbox event", e);
            throw new RuntimeException("Outbox event creation failed", e);
        }
    }

    @Scheduled(fixedDelay = 5000)
    @Transactional
    public void publishPendingEvents() {
        List<OutboxEvent> pendingEvents = outboxRepository.findByPublishedAtIsNullOrderByCreatedAt();
        
        for (OutboxEvent event : pendingEvents) {
            try {
                kafkaTemplate.send("product-events", event.getAggregateId(), event.getPayload());
                
                event.setPublishedAt(LocalDateTime.now());
                outboxRepository.save(event);
                
                log.info("Outbox event published: {}", event.getId());
            } catch (Exception e) {
                log.error("Failed to publish outbox event: {}", event.getId(), e);
                event.setRetryCount(event.getRetryCount() + 1);
                outboxRepository.save(event);
            }
        }
    }
}
```

### Event Consumer with Spring Cloud Stream

**Stream Consumer Configuration:**

```java
// feature/order/infrastructure/messaging/ProductEventStreamConsumer.java
@Component
@Slf4j
@RequiredArgsConstructor
public class ProductEventStreamConsumer {
    private final OrderService orderService;

    @Bean
    public java.util.function.Consumer<ProductCreatedEventDto> productCreatedConsumer() {
        return event -> {
            log.info("Consumed ProductCreatedEvent: {}", event.getProductId());
            orderService.onProductCreated(event);
        };
    }

    @Bean
    public java.util.function.Consumer<ProductStockDecreasedEventDto> productStockDecreasedConsumer() {
        return event -> {
            log.info("Consumed ProductStockDecreasedEvent: {}", event.getProductId());
            orderService.onProductStockDecreased(event);
        };
    }

    @Bean
    public java.util.function.Consumer<ProductLowStockEventDto> productLowStockConsumer() {
        return event -> {
            log.info("Consumed ProductLowStockEvent: {}", event.getProductId());
            orderService.onProductLowStock(event);
        };
    }

    @Bean
    public java.util.function.Consumer<ProductDiscontinuedEventDto> productDiscontinuedConsumer() {
        return event -> {
            log.info("Consumed ProductDiscontinuedEvent: {}", event.getProductId());
            orderService.onProductDiscontinued(event);
        };
    }
}

// Application properties
# spring.cloud.stream.bindings.productCreatedConsumer-in-0.destination=product-events
# spring.cloud.stream.bindings.productStockDecreasedConsumer-in-0.destination=product-events
# spring.cloud.stream.kafka.binder.configuration.isolation.level=read_committed
```

## Testing Event-Driven Patterns

### Unit Tests for Domain Events

```java
// feature/product/domain/model/ProductEventTest.java
class ProductEventTest {

    @Test
    void shouldPublishProductCreatedEventOnCreation() {
        // Given, When
        Product product = Product.create("Test Product", "Description", BigDecimal.TEN, 100);

        // Then
        assertThat(product.getDomainEvents()).hasSize(1);
        assertThat(product.getDomainEvents().get(0))
            .isInstanceOf(ProductCreatedEvent.class);
        
        ProductCreatedEvent event = (ProductCreatedEvent) product.getDomainEvents().get(0);
        assertThat(event.getProductId()).isEqualTo(product.getId());
        assertThat(event.getName()).isEqualTo("Test Product");
    }

    @Test
    void shouldPublishMultipleEventsOnStockDecrease() {
        // Given
        Product product = Product.create("Product", "Desc", BigDecimal.TEN, 15);
        product.clearDomainEvents();

        // When
        product.decreaseStock(10);

        // Then
        assertThat(product.getDomainEvents()).hasSize(2);
        assertThat(product.getDomainEvents().get(0))
            .isInstanceOf(ProductStockDecreasedEvent.class);
        assertThat(product.getDomainEvents().get(1))
            .isInstanceOf(ProductLowStockEvent.class);
    }

    @Test
    void shouldPublishProductDiscontinuedEvent() {
        // Given
        Product product = Product.create("Product", "Desc", BigDecimal.TEN, 100);
        product.clearDomainEvents();

        // When
        product.discontinue("End of life");

        // Then
        assertThat(product.getDomainEvents()).hasSize(1);
        assertThat(product.getDomainEvents().get(0))
            .isInstanceOf(ProductDiscontinuedEvent.class);
        
        ProductDiscontinuedEvent event = (ProductDiscontinuedEvent) product.getDomainEvents().get(0);
        assertThat(event.getReason()).isEqualTo("End of life");
    }

    @Test
    void shouldIncludeCorrelationIdInEvents() {
        // Given, When
        Product product = Product.create("Product", "Desc", BigDecimal.TEN, 100);

        // Then
        product.getDomainEvents().forEach(event -> {
            assertThat(event.getEventId()).isNotNull();
            assertThat(event.getCorrelationId()).isNotNull();
            assertThat(event.getOccurredAt()).isNotNull();
        });
    }
}
```

### Unit Tests for Event Handlers

```java
// feature/product/application/handler/ProductEventHandlerTest.java
@ExtendWith(MockitoExtension.class)
class ProductEventHandlerTest {

    @Mock
    private NotificationService notificationService;

    @Mock
    private InventoryService inventoryService;

    @Mock
    private ProductAuditService auditService;

    @InjectMocks
    private ProductEventHandler handler;

    @Test
    void shouldHandleProductCreatedEvent() {
        // Given
        ProductCreatedEvent event = new ProductCreatedEvent(
            ProductId.of("123"), "Product", BigDecimal.TEN, 100
        );

        // When
        handler.onProductCreated(event);

        // Then
        verify(auditService).logProductCreation(
            eq("123"), eq("Product"), eq(BigDecimal.TEN), any(UUID.class)
        );
        verify(notificationService).sendProductCreatedNotification(
            eq("Product"), eq(BigDecimal.TEN)
        );
    }

    @Test
    void shouldHandleProductLowStockEvent() {
        // Given
        ProductLowStockEvent event = new ProductLowStockEvent(
            ProductId.of("123"), 5, 10
        );

        // When
        handler.onProductLowStock(event);

        // Then
        verify(notificationService).sendLowStockAlert(eq("123"), eq(5), eq(10));
        verify(inventoryService).triggerReorderProcess("123");
    }
}
```

### Integration Tests with Testcontainers and Kafka

```java
// feature/product/infrastructure/messaging/KafkaEventIntegrationTest.java
@SpringBootTest
@Testcontainers
class KafkaEventIntegrationTest {

    @Container
    static KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));

    @Autowired
    private ProductApplicationService productService;

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @SpyBean
    private ProductEventPublisher eventPublisher;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Test
    void shouldPublishProductCreatedEventToKafka() throws InterruptedException {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Kafka Test Product", BigDecimal.valueOf(99.99), "Test", 50
        );

        // When
        ProductResponse response = productService.createProduct(request);

        // Then
        Thread.sleep(1000);
        verify(eventPublisher).publishProductCreatedEvent(any(ProductCreatedEvent.class));
        assertThat(response.getName()).isEqualTo("Kafka Test Product");
    }

    @Test
    void shouldConsumerReceivePublishedEvent() throws InterruptedException {
        // Given
        String topic = "product-events";
        ProductCreatedEventDto eventDto = new ProductCreatedEventDto(
            UUID.randomUUID(), "123", "Product", BigDecimal.TEN, 100,
            LocalDateTime.now(), UUID.randomUUID()
        );

        // When
        kafkaTemplate.send(topic, "123", eventDto);

        // Then - verify consumer receives the event
        Thread.sleep(1000);
        // Add consumer verification based on your implementation
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

    <!-- Kafka -->
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>

    <!-- Spring Cloud Stream -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-stream</artifactId>
        <version>4.0.4</version>
    </dependency>

    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-stream-binder-kafka</artifactId>
        <version>4.0.4</version>
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

    <!-- Jackson for JSON -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
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

    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>kafka</artifactId>
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

    // Kafka
    implementation 'org.springframework.kafka:spring-kafka'

    // Spring Cloud Stream
    implementation 'org.springframework.cloud:spring-cloud-stream:4.0.4'
    implementation 'org.springframework.cloud:spring-cloud-stream-binder-kafka:4.0.4'

    // Database
    runtimeOnly 'org.postgresql:postgresql'

    // Lombok
    compileOnly 'org.projectlombok:lombok:1.18.30'
    annotationProcessor 'org.projectlombok:lombok:1.18.30'

    // Jackson
    implementation 'com.fasterxml.jackson.core:jackson-databind'

    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.testcontainers:testcontainers:1.19.0'
    testImplementation 'org.testcontainers:postgresql:1.19.0'
    testImplementation 'org.testcontainers:kafka:1.19.0'
}
```

## Configuration Examples

### Application Properties for EDA Application

```properties
# Server Configuration
server.port=8080
server.servlet.context-path=/api

# Database Configuration
spring.datasource.url=jdbc:postgresql://localhost:5432/productdb
spring.datasource.username=${DB_USERNAME:postgres}
spring.datasource.password=${DB_PASSWORD:password}

# JPA Configuration
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect

# Kafka Configuration
spring.kafka.bootstrap-servers=${KAFKA_SERVERS:localhost:9092}
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer
spring.kafka.consumer.group-id=product-service
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.springframework.kafka.support.serializer.JsonDeserializer
spring.kafka.consumer.properties.spring.json.trusted.packages=*

# Spring Cloud Stream Configuration
spring.cloud.stream.kafka.binder.brokers=${KAFKA_SERVERS:localhost:9092}
spring.cloud.stream.bindings.productCreatedConsumer-in-0.destination=product-events
spring.cloud.stream.bindings.productStockDecreasedConsumer-in-0.destination=product-events
spring.cloud.stream.bindings.productLowStockConsumer-in-0.destination=product-events
spring.cloud.stream.bindings.productDiscontinuedConsumer-in-0.destination=product-events

# Actuator
management.endpoints.web.exposure.include=health,info,metrics,prometheus
management.endpoint.health.show-details=always

# Logging
logging.level.com.example=INFO
logging.level.org.springframework.kafka=WARN
```

## Best Practices

### 1. Event Design

**Event Naming:**
- Use past tense: ProductCreated, not CreateProduct
- Be specific and descriptive
- Include all necessary data in the event

**Event Immutability:**
- Events should be immutable
- Include correlation IDs for tracing
- Store timestamps for ordering

### 2. Event Handling

**Transactional Consistency:**
- Use `@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)`
- Ensures events are published after successful transaction
- Prevents orphaned events

**Idempotency:**
- Handlers should be idempotent
- Use event IDs to detect duplicates
- Handle retries gracefully

**Error Handling:**
- Implement retry mechanisms
- Use dead-letter queues for failed events
- Log all failures for debugging

### 3. Event Publishing

**Distributed Events:**
- Use outbox pattern for reliability
- Publish to Kafka for inter-service communication
- Include correlation IDs for tracing

**Local Events:**
- Use ApplicationEventPublisher for in-process events
- Use `@TransactionalEventListener` for consistency
- Keep handlers synchronous and fast

## Summary

This Spring Boot Event-Driven Patterns skill provides:

1. **Domain Events** with correlation tracking and proper event design
2. **Local Event Publishing** using ApplicationEventPublisher and @TransactionalEventListener
3. **Distributed Event Publishing** with Kafka and Spring Cloud Stream
4. **Transactional Outbox Pattern** for reliable event publishing
5. **Event Handling** with idempotency and error handling
6. **Comprehensive Testing** strategies for event-driven systems
7. **Production-ready Configurations** with Kafka integration and monitoring

These patterns enable you to build scalable, resilient event-driven microservices with Spring Boot following modern enterprise development practices.
