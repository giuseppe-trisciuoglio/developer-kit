# Event Publishing Patterns

## Local Event Publishing

### Application Event Publisher

```java
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public ProductResponse createProduct(CreateProductRequest request) {
        Product product = Product.create(
            request.getName(),
            request.getPrice(),
            request.getStock()
        );

        productRepository.save(product);

        // Publish domain events
        product.getDomainEvents().forEach(eventPublisher::publishEvent);
        product.clearDomainEvents();

        return mapToResponse(product);
    }
}
```

## Distributed Event Publishing

### Kafka Event Publisher

```java
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class ProductEventPublisher {
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publishProductCreatedEvent(ProductCreatedEvent event) {
        ProductCreatedEventDto dto = mapToDto(event);

        kafkaTemplate.send("product-events", event.getProductId().getValue(), dto)
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    log.info("Published ProductCreatedEvent: {}", event.getProductId());
                } else {
                    log.error("Failed to publish ProductCreatedEvent", ex);
                }
            });
    }

    private ProductCreatedEventDto mapToDto(ProductCreatedEvent event) {
        return new ProductCreatedEventDto(
            event.getEventId().toString(),
            event.getProductId().getValue(),
            event.getName(),
            event.getPrice(),
            event.getStock(),
            event.getOccurredAt(),
            event.getCorrelationId().toString()
        );
    }
}
```

### Event Publisher with Retry

```java
import org.springframework.kafka.support.SendResult;
import org.springframework.util.concurrent.ListenableFutureCallback;
import org.springframework.retry.annotation.Retryable;
import org.springframework.retry.backoff.FixedBackOffPolicy;
import org.springframework.retry.policy.SimpleRetryPolicy;
import org.springframework.retry.support.RetryTemplate;

@Component
@RequiredArgsConstructor
public class ResilientEventPublisher {
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final RetryTemplate retryTemplate;

    public void publishEvent(String topic, String key, Object payload) {
        retryTemplate.execute(context -> {
            try {
                kafkaTemplate.send(topic, key, payload).get();
                return true;
            } catch (Exception e) {
                log.error("Failed to publish event to topic: {}", topic, e);
                throw new EventPublishingException("Failed to publish event", e);
            }
        });
    }

    @Bean
    public RetryTemplate retryTemplate() {
        RetryTemplate retryTemplate = new RetryTemplate();

        FixedBackOffPolicy backOffPolicy = new FixedBackOffPolicy();
        backOffPolicy.setBackOffPeriod(1000L);

        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy();
        retryPolicy.setMaxAttempts(3);

        retryTemplate.setBackOffPolicy(backOffPolicy);
        retryTemplate.setRetryPolicy(retryPolicy);

        return retryTemplate;
    }
}
```

## Spring Cloud Stream Publishing

### Functional Publisher

```java
import org.springframework.cloud.stream.function.StreamBridge;
import org.springframework.stereotype.Component;
import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class ProductEventStreamPublisher {
    private final StreamBridge streamBridge;

    public void publishProductCreatedEvent(ProductCreatedEvent event) {
        ProductCreatedEventDto dto = mapToDto(event);
        streamBridge.send("productCreated-out-0", dto);
    }

    private ProductCreatedEventDto mapToDto(ProductCreatedEvent event) {
        return new ProductCreatedEventDto(
            event.getEventId().toString(),
            event.getProductId().getValue(),
            event.getName(),
            event.getPrice(),
            event.getStock(),
            event.getOccurredAt(),
            event.getCorrelationId().toString()
        );
    }
}
```

### Producer Configuration

```yaml
spring:
  cloud:
    stream:
      bindings:
        productCreated-out-0:
          destination: product-events
          producer:
            partition-count: 3
            required-groups: order-service, inventory-service
      kafka:
        bindings:
          productCreated-out-0:
            producer:
              configuration:
                acks: all
                retries: 3
                enable.idempotence: true
```

## Event Publishing from Event Listener

### Publishing Events After Handling

```java
@Component
@RequiredArgsConstructor
public class OrderEventHandler {
    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher eventPublisher;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCreated(OrderCreatedEvent event) {
        // Process order creation
        Order order = orderRepository.findById(event.getOrderId())
            .orElseThrow();

        // Publish derived events
        eventPublisher.publishEvent(new InventoryReservationRequestedEvent(
            event.getOrderId(),
            event.getItems()
        ));

        eventPublisher.publishEvent(new PaymentRequestedEvent(
            event.getOrderId(),
            event.getTotalAmount()
        ));
    }
}
```

## Batching Events

### Batch Event Publisher

```java
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class BatchEventPublisher {
    private final List<DomainEvent> eventBuffer = new ArrayList<>();
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public synchronized void addEvent(DomainEvent event) {
        eventBuffer.add(event);

        if (eventBuffer.size() >= 100) {
            flush();
        }
    }

    @Scheduled(fixedDelay = 5000)
    public synchronized void flush() {
        if (eventBuffer.isEmpty()) {
            return;
        }

        try {
            eventBuffer.forEach(event -> {
                kafkaTemplate.send("events", event);
            });
        } finally {
            eventBuffer.clear();
        }
    }
}
```

## Event Publishing Best Practices

### 1. Publish After Transaction Commit

```java
@Transactional
public void executeBusinessOperation() {
    // Perform business logic
    aggregateRoot.performAction();

    // Save to database
    repository.save(aggregateRoot);

    // Publish events AFTER transaction commits
    TransactionSynchronizationManager.registerSynchronization(
        new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                aggregateRoot.getDomainEvents().forEach(eventPublisher::publishEvent);
                aggregateRoot.clearDomainEvents();
            }
        }
    );
}
```

### 2. Use Transactional Event Listener

```java
@Component
public class EventForwardingHandler {
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void forwardToKafka(DomainEvent event) {
        kafkaTemplate.send("events", event);
    }
}
```

### 3. Handle Publishing Failures

```java
public void publishEventWithFallback(DomainEvent event) {
    try {
        kafkaTemplate.send("events", event).get(5, TimeUnit.SECONDS);
    } catch (Exception e) {
        log.error("Failed to publish event, storing in outbox", e);
        outboxRepository.save(OutboxEvent.from(event));
    }
}
```
