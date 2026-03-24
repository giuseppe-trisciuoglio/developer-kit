# Event Handling Patterns

## Local Event Handling

### Transactional Event Listener

```java
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;
import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class ProductEventHandler {
    private final NotificationService notificationService;
    private final AuditService auditService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductCreated(ProductCreatedEvent event) {
        auditService.logProductCreation(
            event.getProductId().getValue(),
            event.getName(),
            event.getPrice(),
            event.getCorrelationId()
        );

        notificationService.sendProductCreatedNotification(event.getName());
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductStockDecreased(ProductStockDecreasedEvent event) {
        notificationService.sendStockUpdateNotification(
            event.getProductId().getValue(),
            event.getQuantity()
        );
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void onTransactionRollback(DomainEvent event) {
        log.error("Transaction rolled back for event: {}", event.getEventId());
    }
}
```

### Async Event Listener

```java
@Component
@RequiredArgsConstructor
public class AsyncEventHandler {
    private final EmailService emailService;

    @Async
    @EventListener
    public void handleOrderCreatedEvent(OrderCreatedEvent event) {
        // Executes asynchronously in a separate thread
        emailService.sendOrderConfirmationEmail(
            event.getCustomerId().getValue(),
            event.getOrderId().getValue()
        );
    }
}
```

## Kafka Event Consumption

### Kafka Listener

```java
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class ProductEventConsumer {

    private final OrderService orderService;

    @KafkaListener(
        topics = "product-events",
        groupId = "order-service",
        properties = {
            "spring.json.value.default.type=com.example.events.ProductCreatedEventDto"
        }
    )
    public void handleProductCreated(ProductCreatedEventDto event) {
        log.info("Received ProductCreatedEvent: {}", event.getProductId());

        try {
            orderService.onProductCreated(event);
        } catch (Exception e) {
            log.error("Failed to handle ProductCreatedEvent", e);
            throw e; // Re-throw to trigger retry
        }
    }

    @KafkaListener(
        topics = "product-events",
        groupId = "order-service",
        properties = {
            "spring.json.value.default.type=com.example.events.ProductStockDecreasedEventDto"
        }
    )
    public void handleProductStockDecreased(ProductStockDecreasedEventDto event) {
        log.info("Received ProductStockDecreasedEvent: {}", event.getProductId());

        orderService.onProductStockDecreased(event);
    }
}
```

### Manual Acknowledgment

```java
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;

@Component
@Slf4j
public class ManualAckConsumer {

    @KafkaListener(
        topics = "product-events",
        groupId = "order-service",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void handleWithManualAck(
        @Payload ProductCreatedEventDto event,
        @Header(KafkaHeaders.ACKNOWLEDGMENT) Acknowledgment acknowledgment
    ) {
        try {
            // Process event
            orderService.onProductCreated(event);

            // Manually acknowledge
            acknowledgment.acknowledge();

        } catch (Exception e) {
            log.error("Failed to process event", e);
            // Don't acknowledge - message will be redelivered
        }
    }
}
```

### Error Handling with Dead Letter Queue

```java
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.RetryableTopic;
import org.springframework.retry.annotation.Backoff;

@Component
@Slf4j
public class ResilientEventConsumer {

    @RetryableTopic(
        attempts = "3",
        backoff = @Backoff(delay = 1000, multiplier = 2),
        autoCreateTopics = "false",
        topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE
    )
    @KafkaListener(
        topics = "product-events",
        groupId = "order-service"
    )
    public void handleProductEvent(ProductCreatedEventDto event) {
        log.info("Processing product event: {}", event.getProductId());

        // Process event
        orderService.onProductCreated(event);
    }

    @KafkaListener(
        topics = "product-events-dlt",
        groupId = "order-service-dlt"
    )
    public void handleDeadLetterEvent(ProductCreatedEventDto event) {
        log.error("Event moved to DLT: {}", event.getProductId());

        // Log to monitoring system
        monitoringService.alertDeadLetterEvent(event);

        // Store for manual inspection
        deadLetterRepository.save(event);
    }
}
```

## Spring Cloud Stream Consumption

### Functional Consumer

```java
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;
import java.util.function.Consumer;

@Component
@RequiredArgsConstructor
public class ProductEventStreamConsumer {
    private final OrderService orderService;

    @Bean
    public Consumer<ProductCreatedEventDto> productCreated() {
        return event -> {
            log.info("Received ProductCreatedEvent: {}", event.getProductId());
            orderService.onProductCreated(event);
        };
    }

    @Bean
    public Consumer<ProductStockDecreasedEventDto> productStockDecreased() {
        return event -> {
            log.info("Received ProductStockDecreasedEvent: {}", event.getProductId());
            orderService.onProductStockDecreased(event);
        };
    }
}
```

### Consumer with Error Handling

```java
import org.springframework.context.annotation.Bean;
import org.springframework.messaging.Message;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.stereotype.Component;

@Component
public class ErrorHandlingConsumer {

    @Bean
    public Consumer<Message<ProductCreatedEventDto>> productCreatedWithRetry() {
        return message -> {
            try {
                ProductCreatedEventDto event = message.getPayload();
                orderService.onProductCreated(event);
            } catch (Exception e) {
                log.error("Failed to process event", e);

                // Send to dead letter topic
                throw new RuntimeException("Failed to process event", e);
            }
        };
    }
}
```

## Event Handler Best Practices

### 1. Idempotent Handlers

```java
@Component
@RequiredArgsConstructor
public class IdempotentEventHandler {
    private final ProcessedEventRepository processedEventRepository;

    public void handleProductCreated(ProductCreatedEventDto event) {
        // Check if event was already processed
        if (processedEventRepository.existsByEventId(event.getEventId())) {
            log.info("Event already processed: {}", event.getEventId());
            return;
        }

        // Process event
        orderService.onProductCreated(event);

        // Mark as processed
        processedEventRepository.save(new ProcessedEvent(event.getEventId()));
    }
}
```

### 2. Event Handler with Validation

```java
@Component
public class ValidatingEventHandler {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCreated(OrderCreatedEvent event) {
        // Validate event
        if (event.getItems().isEmpty()) {
            throw new InvalidEventException("Order items cannot be empty");
        }

        if (event.getTotalAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidEventException("Total amount must be positive");
        }

        // Process valid event
        inventoryService.reserveItems(event.getItems());
        paymentService.charge(event.getTotalAmount());
    }
}
```

### 3. Event Handler with Circuit Breaker

```java
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;

@Component
@RequiredArgsConstructor
public class ResilientEventHandler {
    private final ExternalServiceClient externalServiceClient;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    @CircuitBreaker(
        name = "externalService",
        fallbackMethod = "handleExternalServiceFailure"
    )
    public void handleOrderCreated(OrderCreatedEvent event) {
        externalServiceClient.notifyOrderCreated(event);
    }

    private void handleExternalServiceFailure(OrderCreatedEvent event, Exception ex) {
        log.error("External service unavailable for event: {}", event.getOrderId(), ex);

        // Store event for later retry
        outboxRepository.save(OutboxEvent.from(event));
    }
}
```

### 4. Event Handler with Timeout

```java
import org.springframework.transaction.annotation.Transactional;
import java.util.concurrent.TimeUnit;

@Component
public class TimeoutEventHandler {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCreated(OrderCreatedEvent event) {
        ExecutorService executor = Executors.newSingleThreadExecutor();

        try {
            Future<?> future = executor.submit(() -> {
                notificationService.sendOrderConfirmation(event);
            });

            future.get(5, TimeUnit.SECONDS); // Timeout after 5 seconds

        } catch (TimeoutException e) {
            log.error("Notification timed out for order: {}", event.getOrderId());
            // Handle timeout appropriately
        } catch (Exception e) {
            log.error("Failed to send notification", e);
            throw new EventHandlingException("Failed to handle event", e);
        } finally {
            executor.shutdown();
        }
    }
}
```

### 5. Batch Event Processing

```java
import org.springframework.scheduling.annotation.Scheduled;
import java.util.List;

@Component
public class BatchEventHandler {
    private final List<DomainEvent> eventBuffer = new ArrayList<>();

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void bufferEvent(DomainEvent event) {
        synchronized (eventBuffer) {
            eventBuffer.add(event);

            if (eventBuffer.size() >= 100) {
                processBatch();
            }
        }
    }

    @Scheduled(fixedDelay = 5000)
    public synchronized void processBatch() {
        if (eventBuffer.isEmpty()) {
            return;
        }

        List<DomainEvent> batch = new ArrayList<>(eventBuffer);
        eventBuffer.clear();

        // Process batch
        batchProcessor.process(batch);
    }
}
```
