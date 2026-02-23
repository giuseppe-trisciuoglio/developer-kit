---
name: spring-boot-event-driven-patterns
description: Provides Event-Driven Architecture (EDA) patterns in Spring Boot using ApplicationEvent, @EventListener, and Kafka. Use when building loosely-coupled microservices with domain events, transactional event listeners, and distributed messaging patterns.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring Boot Event-Driven Patterns

## Overview

Implement Event-Driven Architecture (EDA) in Spring Boot with two complementary layers:

- Local in-process domain events using `ApplicationEventPublisher` and `@TransactionalEventListener`.
- Distributed integration events using Kafka and Spring Cloud Stream functional bindings.

This skill focuses on transactional consistency, reliable delivery (outbox), and maintainable event contracts.

## When to Use

- Loose coupling between microservices through event-based communication
- Domain event publishing from aggregate roots in DDD architectures
- Transactional event listeners ensuring consistency after database commits
- Distributed messaging with Kafka for inter-service communication
- Spring Cloud Stream functional consumers/producers (`Consumer`, `Function`, `Supplier`)
- Reliability using the transactional outbox pattern
- Asynchronous communication between bounded contexts

## Instructions

### 1. Design Domain Events

Create immutable domain events with metadata (`eventId`, `occurredAt`, `correlationId`, `eventType`, optional `version`).
Use past-tense names (`OrderCreatedEvent`) and small payloads designed for serialization.

### 2. Define Event Publishing

Collect domain events in aggregate roots, persist state changes, then publish with `ApplicationEventPublisher`.
Clear aggregate event buffers after successful publication in application services.

### 3. Configure Transactional Listeners

Use `@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)` for side effects that must run only after commit.
Use `BEFORE_COMMIT`, `AFTER_ROLLBACK`, or `AFTER_COMPLETION` only for explicit lifecycle needs.

### 4. Set Up Kafka Infrastructure

For integration events, publish to Kafka with stable topic naming and explicit keys.
Use idempotent consumers and a dead-letter strategy for poison messages.

### 5. Implement Spring Cloud Stream

Use functional bean definitions (`Consumer`, `Function`, `Supplier`) and bind channels via `spring.cloud.stream.bindings.*`.
Keep business logic outside binder wiring code.

### 6. Handle Failure Scenarios

Implement retry/backoff, dead-letter topics or queues, and idempotent handlers.
Track processing attempts and reason codes for failures.

### 7. Implement Outbox Pattern

Store outbound events in an outbox table in the same transaction as business data changes.
Publish outbox records asynchronously, mark as published on success, and increment retry counters on failure.

## Examples

### Domain Event Base Class

```java
public abstract class DomainEvent {
    private final UUID eventId = UUID.randomUUID();
    private final Instant occurredAt = Instant.now();
    private final UUID correlationId;

    protected DomainEvent() { this.correlationId = UUID.randomUUID(); }
    protected DomainEvent(UUID correlationId) { this.correlationId = correlationId; }

    public UUID getEventId() { return eventId; }
    public Instant getOccurredAt() { return occurredAt; }
    public UUID getCorrelationId() { return correlationId; }
}
```

### Application Event Publishing

```java
@Service
@RequiredArgsConstructor
@Transactional
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ApplicationEventPublisher eventPublisher;

    public ProductResponse createProduct(CreateProductRequest request) {
        Product product = Product.create(request.getName(), request.getPrice(), request.getStock());
        productRepository.save(product);
        product.getDomainEvents().forEach(eventPublisher::publishEvent);
        product.clearDomainEvents();
        return mapToResponse(product);
    }
}
```

### Transactional Event Listener

```java
@Component
@RequiredArgsConstructor
public class ProductEventHandler {
    private final AuditService auditService;
    private final NotificationService notificationService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductCreated(ProductCreatedEvent event) {
        auditService.logProductCreation(event.getProductId().getValue(), event.getName());
        notificationService.sendProductCreatedNotification(event.getName());
    }
}
```

### Spring Cloud Stream Functional Consumer

```java
@Configuration
public class ProductEventConsumers {
    @Bean
    public Consumer<ProductCreatedEvent> productCreatedConsumer(ProductProjectionService projectionService) {
        return projectionService::updateReadModel;
    }
}
```

```yaml
spring:
  cloud:
    function:
      definition: productCreatedConsumer
    stream:
      bindings:
        productCreatedConsumer-in-0:
          destination: product-events
          group: product-read-model
      kafka:
        binder:
          brokers: localhost:9092
```

### Transactional Outbox Pattern

```java
@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    private String aggregateId;
    private String eventType;
    @Column(columnDefinition = "TEXT")
    private String payload;
    private LocalDateTime createdAt;
    private LocalDateTime publishedAt;
    private int retryCount;

    public int getRetryCount() { return retryCount; }
    public void setRetryCount(int retryCount) { this.retryCount = retryCount; }
    public void setPublishedAt(LocalDateTime publishedAt) { this.publishedAt = publishedAt; }
}

@Component
@RequiredArgsConstructor
public class OutboxEventProcessor {
    private final OutboxEventRepository outboxRepository;
    private final KafkaTemplate<String, String> kafkaTemplate;

    @Scheduled(fixedDelay = 5000)
    @Transactional
    public void processPendingEvents() {
        List<OutboxEvent> pending = outboxRepository.findByPublishedAtNull();
        for (OutboxEvent event : pending) {
            try {
                kafkaTemplate.send("product-events", event.getAggregateId(), event.getPayload());
                event.setPublishedAt(LocalDateTime.now());
            } catch (Exception e) {
                event.setRetryCount(event.getRetryCount() + 1);
            }
            outboxRepository.save(event);
        }
    }
}
```

## Best Practices

- **Use past tense naming**: ProductCreated, not CreateProduct
- **Keep events immutable**: Event payloads should not change after publication
- **Version event contracts**: Add explicit versioning for external events
- **Include correlation IDs**: Support tracing across services and topics
- **Use AFTER_COMMIT for side effects**: Avoid emitting success events before commit
- **Implement idempotent handlers**: Use business keys, dedup tables, or optimistic checks
- **Route failures to DLQ**: Keep main consumer flow healthy

## Constraints and Warnings

- `@TransactionalEventListener` does not run if there is no transaction unless explicitly configured
- Listener logic runs on the caller thread by default; avoid slow or blocking operations
- `@Async` listeners run on different threads; plan for context propagation and retries
- Kafka delivery is at-least-once in common setups; duplicates must be expected
- Event ordering is partition-scoped, not global; design handlers to tolerate reordering
- Do not emit large object graphs; publish minimal event payloads

## References

- [Complete Examples](references/examples.md)
- [Detailed Implementation Patterns](references/event-driven-patterns-reference.md)
