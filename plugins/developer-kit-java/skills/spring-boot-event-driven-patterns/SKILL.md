---
name: spring-boot-event-driven-patterns
description: Provides Event-Driven Architecture (EDA) patterns in Spring Boot using ApplicationEvent, @EventListener, and Kafka. Use when building loosely-coupled microservices with domain events, transactional event listeners, and distributed messaging patterns.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
category: backend
tags: [spring-boot, java, event-driven, eda, kafka, messaging, domain-events, microservices, spring-cloud-stream]
version: 2.2.0
---

# Spring Boot Event-Driven Patterns

## Overview

Implement Event-Driven Architecture (EDA) patterns in Spring Boot 3.x using domain events, ApplicationEventPublisher, @TransactionalEventListener, and distributed messaging with Kafka and Spring Cloud Stream.

## When to Use

- Loose coupling between microservices through event-based communication
- Domain event publishing from aggregate roots in DDD architectures
- Transactional event listeners ensuring consistency after database commits
- Distributed messaging with Kafka for inter-service communication
- Reliability using the transactional outbox pattern
- Asynchronous communication between bounded contexts

## Instructions

### 1. Design Domain Events

Create immutable event classes extending a base DomainEvent class with eventId, occurredAt, and correlationId.

### 2. Define Event Publishing

Add ApplicationEventPublisher to services. Publish events after domain state changes complete.

### 3. Configure Transactional Listeners

Use @TransactionalEventListener with phase = AFTER_COMMIT for post-transaction event processing.

### 4. Set Up Kafka Infrastructure

Configure KafkaTemplate for publishing events. Create @KafkaListener beans for consumption.

### 5. Implement Spring Cloud Stream

Use functional Consumer bean definitions for reactive event consumption.

### 6. Handle Failure Scenarios

Implement retry with exponential backoff, dead-letter queues, and idempotent handlers.

### 7. Implement Outbox Pattern

Create OutboxEvent entity for atomic event storage. Use scheduled job to publish to broker.

## Examples

### Domain Event Base Class

```java
public abstract class DomainEvent {
    private final UUID eventId = UUID.randomUUID();
    private final LocalDateTime occurredAt = LocalDateTime.now();
    private final UUID correlationId;

    protected DomainEvent() { this.correlationId = UUID.randomUUID(); }
    protected DomainEvent(UUID correlationId) { this.correlationId = correlationId; }
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
public class ProductEventHandler {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductCreated(ProductCreatedEvent event) {
        auditService.logProductCreation(event.getProductId().getValue(), event.getName());
        notificationService.sendProductCreatedNotification(event.getName());
    }
}
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
    private String payload;
    private LocalDateTime createdAt;
    private LocalDateTime publishedAt;
    private Integer retryCount;
}

@Component
public class OutboxEventProcessor {
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
- **Keep events immutable**: All fields should be final
- **Include correlation IDs**: For tracing events across services
- **Use AFTER_COMMIT phase**: Ensures events published after successful transaction
- **Implement idempotent handlers**: Handle duplicate events gracefully
- **Implement dead-letter queues**: For events that fail processing

## Constraints and Warnings

- Events published with `@TransactionalEventListener` only fire after transaction commit
- Avoid publishing large objects in events (memory pressure and serialization issues)
- Kafka consumers must handle duplicate messages with idempotent processing
- Event ordering is not guaranteed in distributed systems
- Never perform blocking operations in event listeners on the main transaction thread

## References

- [Complete Examples](references/examples.md)
- [Detailed Implementation Patterns](references/event-driven-patterns-reference.md)
