# Spring Boot Event-Driven Patterns - References

Complete API reference for event-driven architecture in Spring Boot applications.

## Domain Event Annotations and Interfaces

### ApplicationEvent
Base class for Spring events (deprecated in newer versions in favor of plain objects).

```java
public abstract class ApplicationEvent extends EventObject {
    private final long timestamp;
    
    public ApplicationEvent(Object source) {
        super(source);
        this.timestamp = System.currentTimeMillis();
    }
    
    public long getTimestamp() {
        return timestamp;
    }
}

// Modern approach: Use plain POJOs
public record ProductCreatedEvent(String productId, String name, BigDecimal price) {}
```

### Custom Domain Event Base Class

```java
public abstract class DomainEvent {
    private final UUID eventId;
    private final LocalDateTime occurredAt;
    private final UUID correlationId;

    protected DomainEvent() {
        this.eventId = UUID.randomUUID();
        this.occurredAt = LocalDateTime.now();
        this.correlationId = UUID.randomUUID();
    }
}
```

## Event Publishing Annotations

### @EventListener
Register event listener methods.

```java
@EventListener
public void onProductCreated(ProductCreatedEvent event) { }

@EventListener(condition = "#event.productId == '123'")  // SpEL condition
public void onSpecificProduct(ProductCreatedEvent event) { }

@EventListener(classes = { ProductCreatedEvent.class, ProductUpdatedEvent.class })
public void onProductEvent(DomainEvent event) { }
```

### @TransactionalEventListener
Listen to events within transaction lifecycle.

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onProductCreated(ProductCreatedEvent event) { }

@TransactionalEventListener(phase = TransactionPhase.BEFORE_COMMIT)
public void beforeCommit(ProductCreatedEvent event) { }

@TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
public void afterRollback(ProductCreatedEvent event) { }
```

**TransactionPhase Values:**
- `BEFORE_COMMIT` - Before transaction commits
- `AFTER_COMMIT` - After successful commit (recommended)
- `AFTER_ROLLBACK` - After transaction rollback
- `AFTER_COMPLETION` - After transaction completion (success or rollback)

## Event Publishing Reference

### ApplicationEventPublisher Interface

```java
public interface ApplicationEventPublisher {
    void publishEvent(ApplicationEvent event);
    void publishEvent(Object event);  // Modern approach
}
```

### Usage Pattern

```java
@Service
@RequiredArgsConstructor
public class ProductService {
    private final ApplicationEventPublisher eventPublisher;

    public Product create(CreateProductRequest request) {
        Product product = Product.create(request);
        Product saved = repository.save(product);
        
        // Publish events
        saved.getDomainEvents().forEach(eventPublisher::publishEvent);
        saved.clearDomainEvents();
        
        return saved;
    }
}
```

## Kafka Spring Cloud Stream Reference

### Stream Binders Configuration

```yaml
spring:
  cloud:
    stream:
      kafka:
        binder:
          brokers: localhost:9092
          default-binder: kafka
          configuration:
            linger.ms: 10
            batch.size: 1024
      
      bindings:
        # Consumer binding
        productCreatedConsumer-in-0:
          destination: product-events
          group: product-service
          consumer:
            max-attempts: 3
            back-off-initial-interval: 1000
            back-off-max-interval: 10000
        
        # Producer binding
        eventPublisher-out-0:
          destination: product-events
          producer:
            partition-key-expression: headers['partitionKey']
```

### Consumer Function Binding

```java
@Configuration
public class EventConsumers {
    
    @Bean
    public java.util.function.Consumer<ProductCreatedEvent> productCreatedConsumer(
            InventoryService inventoryService) {
        return event -> {
            log.info("Consumed: {}", event);
            inventoryService.process(event);
        };
    }
    
    // Multiple consumers
    @Bean
    public java.util.function.Consumer<ProductUpdatedEvent> productUpdatedConsumer() {
        return event -> { };
    }
}

// application.yml
spring.cloud.stream.bindings.productCreatedConsumer-in-0.destination=product-events
spring.cloud.stream.bindings.productUpdatedConsumer-in-0.destination=product-events
```

### Producer Function Binding

```java
@Configuration
public class EventProducers {
    
    @Bean
    public java.util.function.Supplier<ProductCreatedEvent> eventPublisher() {
        return () -> new ProductCreatedEvent("prod-123", "Laptop", BigDecimal.TEN);
    }
}

// application.yml
spring.cloud.stream.bindings.eventPublisher-out-0.destination=product-events
```

## Transactional Outbox Pattern Reference

### Outbox Entity Schema

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    aggregate_id VARCHAR(255) NOT NULL,
    aggregate_type VARCHAR(255),
    event_type VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    correlation_id UUID,
    created_at TIMESTAMP NOT NULL,
    published_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    KEY idx_published (published_at),
    KEY idx_created (created_at)
);
```

### Implementation Pattern

```java
// In single transaction:
// 1. Update aggregate
product = repository.save(product);

// 2. Store events in outbox
product.getDomainEvents().forEach(event -> {
    outboxRepository.save(new OutboxEvent(
        aggregateId, eventType, payload, correlationId
    ));
});

// Then separately, scheduled task publishes from outbox
@Scheduled(fixedDelay = 5000)
public void publishPendingEvents() {
    List<OutboxEvent> pending = outboxRepository.findByPublishedAtIsNull();
    pending.forEach(event -> {
        kafkaTemplate.send(topic, event.getPayload());
        event.setPublishedAt(now());
    });
}
```

## Maven Dependencies

```xml
<!-- Local Events (Spring Framework core) -->
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-context</artifactId>
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

<!-- Jackson for JSON -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>

<dependency>
    <groupId>com.fasterxml.jackson.datatype</groupId>
    <artifactId>jackson-datatype-jsr310</artifactId>
</dependency>
```

## Gradle Dependencies

```gradle
dependencies {
    // Local Events
    implementation 'org.springframework:spring-context'

    // Kafka
    implementation 'org.springframework.kafka:spring-kafka'

    // Spring Cloud Stream
    implementation 'org.springframework.cloud:spring-cloud-stream:4.0.4'
    implementation 'org.springframework.cloud:spring-cloud-stream-binder-kafka:4.0.4'

    // Jackson
    implementation 'com.fasterxml.jackson.core:jackson-databind'
    implementation 'com.fasterxml.jackson.datatype:jackson-datatype-jsr310'
}
```

## Event Ordering Guarantees

### Kafka Partition Key Strategy

```java
// Events with same product must be in same partition
kafkaTemplate.send(topic, 
    productId,  // Key: ensures ordering per product
    event);     // Value

// Consumer configuration
spring.kafka.consumer.properties.isolation.level=read_committed
spring.cloud.stream.kafka.binder.configuration.isolation.level=read_committed
```

## Error Handling Patterns

### Retry with Backoff

```yaml
spring:
  cloud:
    stream:
      bindings:
        eventConsumer-in-0:
          consumer:
            max-attempts: 3
            back-off-initial-interval: 1000      # 1 second
            back-off-max-interval: 10000         # 10 seconds
            back-off-multiplier: 2.0             # Exponential
            default-retryable: true
            retryable-exceptions:
              com.example.RetryableException: true
```

### Dead Letter Topic (DLT)

```yaml
spring:
  cloud:
    stream:
      kafka:
        bindings:
          eventConsumer-in-0:
            consumer:
              enable-dlq: true
              dlq-name: product-events.dlq
              dlq-producer-properties:
                linger.ms: 5
```

## Idempotency Patterns

### Idempotent Consumer

```java
@Component
public class IdempotentEventHandler {
    private final IdempotencyKeyRepository idempotencyRepository;
    private final EventProcessingService eventService;

    @EventListener
    public void handle(DomainEvent event) throws Exception {
        String idempotencyKey = event.getEventId().toString();
        
        // Check if already processed
        if (idempotencyRepository.exists(idempotencyKey)) {
            log.info("Event already processed: {}", idempotencyKey);
            return;
        }
        
        try {
            // Process event
            eventService.process(event);
            
            // Mark as processed
            idempotencyRepository.save(new IdempotencyKey(idempotencyKey));
        } catch (Exception e) {
            log.error("Event processing failed: {}", idempotencyKey, e);
            throw e;
        }
    }
}
```

## Testing Event-Driven Systems

### Local Event Testing

```java
@SpringBootTest
class EventDrivenTest {
    @Autowired
    private ApplicationEventPublisher eventPublisher;
    
    @MockBean
    private EventHandler handler;

    @Test
    void shouldHandleEvent() {
        // Arrange
        ProductCreatedEvent event = new ProductCreatedEvent("123", "Laptop", BigDecimal.TEN);

        // Act
        eventPublisher.publishEvent(event);

        // Assert
        verify(handler).onProductCreated(event);
    }
}
```

### Kafka Testing with Testcontainers

```java
@SpringBootTest
@Testcontainers
class KafkaEventTest {
    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));

    @DynamicPropertySource
    static void setupProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @Test
    void shouldPublishEventToKafka() throws Exception {
        ProductCreatedEvent event = new ProductCreatedEvent("123", "Laptop", BigDecimal.TEN);
        kafkaTemplate.send("product-events", "123", event).get(5, TimeUnit.SECONDS);
        
        // Verify consumption
    }
}
```

## Monitoring and Observability

### Spring Boot Actuator Metrics

```properties
# Enable metrics
management.endpoints.web.exposure.include=metrics,health

# Kafka metrics
kafka.controller.metrics.topic.under_replication_count
kafka.log.leader_election.latency.avg
```

### Custom Event Metrics

```java
@Component
@RequiredArgsConstructor
public class EventMetrics {
    private final MeterRegistry meterRegistry;

    public void recordEventPublished(String eventType) {
        meterRegistry.counter("events.published", "type", eventType).increment();
    }

    public void recordEventProcessed(String eventType, long durationMs) {
        meterRegistry.timer("events.processed", "type", eventType).record(durationMs, TimeUnit.MILLISECONDS);
    }

    public void recordEventFailed(String eventType) {
        meterRegistry.counter("events.failed", "type", eventType).increment();
    }
}
```

## Related Skills

- **spring-boot-crud-patterns** - Domain events in CRUD operations
- **spring-boot-rest-api-standards** - Event notifications via webhooks
- **spring-boot-test-patterns** - Testing event-driven systems
- **spring-boot-dependency-injection** - Dependency injection in event handlers

## External Resources

### Official Documentation
- [Spring ApplicationContext](https://docs.spring.io/spring-framework/reference/core/beans/context-introduction.html)
- [Spring Cloud Stream](https://spring.io/projects/spring-cloud-stream)
- [Kafka Spring Integration](https://docs.spring.io/spring-kafka/docs/current/reference/html/)

### Patterns and Best Practices
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Saga Pattern](https://microservices.io/patterns/data/saga.html)
- [Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html)
