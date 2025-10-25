# Spring Boot Event-Driven Patterns - Examples

Comprehensive examples demonstrating event-driven architecture from basic local events to advanced distributed messaging.

## Example 1: Basic Domain Events

A simple product lifecycle with domain events.

```java
// Domain event
public class ProductCreatedEvent extends DomainEvent {
    private final String productId;
    private final String name;
    private final BigDecimal price;

    public ProductCreatedEvent(String productId, String name, BigDecimal price) {
        super();
        this.productId = productId;
        this.name = name;
        this.price = price;
    }

    // Getters
}

// Aggregate publishing events
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Product {
    private String id;
    private String name;
    private BigDecimal price;
    
    @Transient
    private List<DomainEvent> domainEvents = new ArrayList<>();

    public static Product create(String name, BigDecimal price) {
        Product product = new Product();
        product.id = UUID.randomUUID().toString();
        product.name = name;
        product.price = price;
        
        // Publish domain event
        product.publishEvent(new ProductCreatedEvent(product.id, name, price));
        
        return product;
    }

    protected void publishEvent(DomainEvent event) {
        domainEvents.add(event);
    }

    public List<DomainEvent> getDomainEvents() {
        return new ArrayList<>(domainEvents);
    }

    public void clearDomainEvents() {
        domainEvents.clear();
    }
}
```

---

## Example 2: Local Event Publishing

Using ApplicationEventPublisher for in-process events.

```java
// Application service
@Service
@Slf4j
@RequiredArgsConstructor
@Transactional
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ApplicationEventPublisher eventPublisher;

    public ProductResponse createProduct(CreateProductRequest request) {
        Product product = Product.create(request.getName(), request.getPrice());
        Product saved = productRepository.save(product);
        
        // Publish domain events
        saved.getDomainEvents().forEach(event -> {
            log.debug("Publishing event: {}", event.getClass().getSimpleName());
            eventPublisher.publishEvent(event);
        });
        saved.clearDomainEvents();
        
        return mapper.toResponse(saved);
    }
}

// Event listener
@Component
@Slf4j
@RequiredArgsConstructor
public class ProductEventHandler {
    private final NotificationService notificationService;
    private final InventoryService inventoryService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductCreated(ProductCreatedEvent event) {
        log.info("Handling ProductCreatedEvent");
        
        // Send notification
        notificationService.sendProductCreatedNotification(
            event.getName(), event.getPrice()
        );
        
        // Update inventory
        inventoryService.registerProduct(event.getProductId());
    }
}

// Test
@SpringBootTest
class ProductEventTest {
    @Autowired
    private ProductApplicationService productService;
    
    @MockBean
    private NotificationService notificationService;
    
    @Autowired
    private ProductRepository productRepository;

    @Test
    void shouldPublishProductCreatedEvent() {
        // Act
        productService.createProduct(
            new CreateProductRequest("Laptop", BigDecimal.valueOf(999.99))
        );

        // Assert - Event was handled
        verify(notificationService).sendProductCreatedNotification(
            "Laptop", BigDecimal.valueOf(999.99)
        );
    }
}
```

---

## Example 3: Transactional Outbox Pattern

Ensures reliable event publishing even on failures.

```java
// Outbox entity
@Entity
@Table(name = "outbox_events")
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OutboxEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String aggregateId;
    private String eventType;
    
    @Column(columnDefinition = "TEXT")
    private String payload;
    
    private LocalDateTime createdAt;
    private LocalDateTime publishedAt;
    private Integer retryCount;
}

// Application service using outbox
@Service
@Slf4j
@RequiredArgsConstructor
@Transactional
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final OutboxEventRepository outboxRepository;
    private final ObjectMapper objectMapper;

    public ProductResponse createProduct(CreateProductRequest request) {
        Product product = Product.create(request.getName(), request.getPrice());
        Product saved = productRepository.save(product);
        
        // Store event in outbox (same transaction)
        saved.getDomainEvents().forEach(event -> {
            try {
                String payload = objectMapper.writeValueAsString(event);
                OutboxEvent outboxEvent = OutboxEvent.builder()
                    .aggregateId(saved.getId())
                    .eventType(event.getClass().getSimpleName())
                    .payload(payload)
                    .createdAt(LocalDateTime.now())
                    .retryCount(0)
                    .build();
                
                outboxRepository.save(outboxEvent);
                log.debug("Outbox event created: {}", event.getClass().getSimpleName());
            } catch (Exception e) {
                log.error("Failed to create outbox event", e);
                throw new RuntimeException(e);
            }
        });
        
        return mapper.toResponse(saved);
    }
}

// Scheduled publisher
@Component
@Slf4j
@RequiredArgsConstructor
public class OutboxEventPublisher {
    private final OutboxEventRepository outboxRepository;
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    @Scheduled(fixedDelay = 5000)
    @Transactional
    public void publishPendingEvents() {
        List<OutboxEvent> pending = outboxRepository.findByPublishedAtIsNull();
        
        for (OutboxEvent event : pending) {
            try {
                kafkaTemplate.send("product-events", 
                    event.getAggregateId(), event.getPayload());
                
                event.setPublishedAt(LocalDateTime.now());
                outboxRepository.save(event);
                
                log.info("Published outbox event: {}", event.getId());
            } catch (Exception e) {
                log.error("Failed to publish event: {}", event.getId(), e);
                event.setRetryCount(event.getRetryCount() + 1);
                outboxRepository.save(event);
            }
        }
    }
}
```

---

## Example 4: Kafka Event Publishing

Distributed event publishing with Spring Cloud Stream.

```java
// Application configuration
@Configuration
public class KafkaConfig {
    
    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }
}

// Event publisher
@Component
@Slf4j
@RequiredArgsConstructor
public class KafkaProductEventPublisher {
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publishProductCreatedEvent(ProductCreatedEvent event) {
        log.info("Publishing ProductCreatedEvent to Kafka: {}", event.getProductId());
        
        kafkaTemplate.send("product-events", 
            event.getProductId(),
            event);
    }
}

// Event consumer
@Component
@Slf4j
@RequiredArgsConstructor
public class ProductEventStreamConsumer {
    private final InventoryService inventoryService;

    @Bean
    public java.util.function.Consumer<ProductCreatedEvent> productCreatedConsumer() {
        return event -> {
            log.info("Consumed ProductCreatedEvent: {}", event.getProductId());
            inventoryService.registerProduct(event.getProductId(), event.getName());
        };
    }

    @Bean
    public java.util.function.Consumer<ProductUpdatedEvent> productUpdatedConsumer() {
        return event -> {
            log.info("Consumed ProductUpdatedEvent: {}", event.getProductId());
            inventoryService.updateProduct(event.getProductId(), event.getPrice());
        };
    }
}

// Application properties
```

**application.yml:**
```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      group-id: product-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "*"

  cloud:
    stream:
      bindings:
        productCreatedConsumer-in-0:
          destination: product-events
          group: product-inventory-service
        productUpdatedConsumer-in-0:
          destination: product-events
          group: product-inventory-service
```

---

## Example 5: Event Saga Pattern

Coordinating multiple services with events.

```java
// Events
public class OrderPlacedEvent extends DomainEvent {
    private final String orderId;
    private final String productId;
    private final Integer quantity;
    // ...
}

public class OrderPaymentConfirmedEvent extends DomainEvent {
    private final String orderId;
    // ...
}

// Saga orchestrator
@Component
@Slf4j
@RequiredArgsConstructor
public class OrderFulfillmentSaga {
    private final OrderService orderService;
    private final PaymentService paymentService;
    private final InventoryService inventoryService;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        log.info("Starting order fulfillment saga for order: {}", event.getOrderId());
        
        try {
            // Step 1: Reserve inventory
            inventoryService.reserveStock(event.getProductId(), event.getQuantity());
            log.info("Inventory reserved for order: {}", event.getOrderId());
            
            // Step 2: Process payment
            paymentService.processPayment(event.getOrderId());
            log.info("Payment processed for order: {}", event.getOrderId());
            
            // Step 3: Publish confirmation
            eventPublisher.publishEvent(new OrderPaymentConfirmedEvent(event.getOrderId()));
            
            // Step 4: Update order status
            orderService.markAsConfirmed(event.getOrderId());
            log.info("Order confirmed: {}", event.getOrderId());
            
        } catch (PaymentFailedException e) {
            log.warn("Payment failed, releasing inventory");
            inventoryService.releaseStock(event.getProductId(), event.getQuantity());
            orderService.markAsFailed(event.getOrderId(), e.getMessage());
        }
    }
}

// Test
@SpringBootTest
class OrderFulfillmentSagaTest {
    @Autowired
    private ApplicationEventPublisher eventPublisher;
    
    @MockBean
    private InventoryService inventoryService;
    
    @MockBean
    private PaymentService paymentService;
    
    @MockBean
    private OrderService orderService;

    @Test
    void shouldCompleteOrderFulfillmentSaga() {
        // Arrange
        OrderPlacedEvent event = new OrderPlacedEvent("order-123", "product-456", 2);

        // Act
        eventPublisher.publishEvent(event);

        // Assert
        verify(inventoryService).reserveStock("product-456", 2);
        verify(paymentService).processPayment("order-123");
        verify(orderService).markAsConfirmed("order-123");
    }
}
```

---

## Example 6: Event Sourcing Foundation

Storing state changes as events.

```java
// Event store
@Repository
public interface EventStoreRepository extends JpaRepository<StoredEvent, UUID> {
    List<StoredEvent> findByAggregateIdOrderBySequenceAsc(String aggregateId);
}

// Stored event
@Entity
@Table(name = "event_store")
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StoredEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String aggregateId;
    private String eventType;
    private Integer sequence;
    
    @Column(columnDefinition = "TEXT")
    private String payload;
    
    private LocalDateTime occurredAt;
}

// Event sourcing service
@Service
@Slf4j
@RequiredArgsConstructor
public class EventSourcingService {
    private final EventStoreRepository eventStoreRepository;
    private final ObjectMapper objectMapper;

    @Transactional
    public void storeEvent(String aggregateId, DomainEvent event) {
        try {
            List<StoredEvent> existing = eventStoreRepository
                .findByAggregateIdOrderBySequenceAsc(aggregateId);
            
            Integer nextSequence = existing.isEmpty() ? 1 : 
                existing.get(existing.size() - 1).getSequence() + 1;
            
            StoredEvent storedEvent = StoredEvent.builder()
                .aggregateId(aggregateId)
                .eventType(event.getClass().getSimpleName())
                .sequence(nextSequence)
                .payload(objectMapper.writeValueAsString(event))
                .occurredAt(LocalDateTime.now())
                .build();
            
            eventStoreRepository.save(storedEvent);
            log.info("Event stored: {} for aggregate: {}", 
                event.getClass().getSimpleName(), aggregateId);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to store event", e);
        }
    }

    public List<DomainEvent> getEventHistory(String aggregateId) {
        return eventStoreRepository
            .findByAggregateIdOrderBySequenceAsc(aggregateId)
            .stream()
            .map(this::deserializeEvent)
            .collect(Collectors.toList());
    }

    private DomainEvent deserializeEvent(StoredEvent stored) {
        try {
            Class<?> eventClass = Class.forName(
                "com.example.product.domain.event." + stored.getEventType());
            return (DomainEvent) objectMapper.readValue(stored.getPayload(), eventClass);
        } catch (Exception e) {
            throw new RuntimeException("Failed to deserialize event", e);
        }
    }
}
```

These examples cover local events, transactional outbox pattern, Kafka publishing, saga coordination, and event sourcing foundations for comprehensive event-driven architecture.
