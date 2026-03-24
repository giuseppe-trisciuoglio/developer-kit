# Transactional Outbox Pattern

## Outbox Entity

### Basic Outbox Event

```java
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

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

    @Column(nullable = false)
    private String aggregateId;

    @Column(nullable = false)
    private String aggregateType;

    @Column(nullable = false)
    private String eventType;

    @Lob
    @Column(nullable = false)
    private String payload;

    @Column(nullable = false)
    private UUID correlationId;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    private LocalDateTime publishedAt;

    @Column(nullable = false)
    @Builder.Default
    private Integer retryCount = 0;

    private String errorMessage;

    private LocalDateTime lastAttemptAt;
}
```

### Outbox Repository

```java
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface OutboxEventRepository extends JpaRepository<OutboxEvent, UUID> {

    List<OutboxEvent> findByPublishedAtNullOrderByCreatedAtAsc();

    List<OutboxEvent> findByPublishedAtNullAndRetryCountLessThanOrderByCreatedAtAsc(Integer maxRetries);

    @Query("""
        SELECT e FROM OutboxEvent e
        WHERE e.publishedAt IS NULL
        AND e.retryCount < :maxRetries
        AND (e.lastAttemptAt IS NULL OR e.lastAttemptAt < :threshold)
        ORDER BY e.createdAt ASC
    """)
    List<OutboxEvent> findPendingEvents(
        Integer maxRetries,
        LocalDateTime threshold
    );
}
```

## Outbox Event Creation

### Save Outbox Event with Aggregate

```java
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class OrderApplicationService {
    private final OrderRepository orderRepository;
    private final OutboxEventRepository outboxRepository;
    private final ObjectMapper objectMapper;

    @Transactional
    public OrderResponse createOrder(CreateOrderRequest request) {
        Order order = Order.create(
            request.getCustomerId(),
            request.getItems()
        );

        orderRepository.save(order);

        // Create outbox events atomically with order
        order.getDomainEvents().forEach(domainEvent -> {
            try {
                OutboxEvent outboxEvent = OutboxEvent.builder()
                    .aggregateId(order.getId().getValue())
                    .aggregateType("Order")
                    .eventType(domainEvent.getClass().getSimpleName())
                    .payload(objectMapper.writeValueAsString(domainEvent))
                    .correlationId(domainEvent.getCorrelationId())
                    .createdAt(LocalDateTime.now())
                    .build();

                outboxRepository.save(outboxEvent);
            } catch (JsonProcessingException e) {
                throw new EventSerializationException("Failed to serialize event", e);
            }
        });

        order.clearDomainEvents();

        return mapToResponse(order);
    }
}
```

## Outbox Event Processor

### Scheduled Event Publisher

```java
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class OutboxEventProcessor {
    private final OutboxEventRepository outboxRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Scheduled(fixedDelay = 5000)
    @Transactional
    public void processPendingEvents() {
        List<OutboxEvent> pendingEvents = outboxRepository.findByPublishedAtNullOrderByCreatedAtAsc();

        for (OutboxEvent event : pendingEvents) {
            try {
                publishEvent(event);
                event.setPublishedAt(LocalDateTime.now());
                outboxRepository.save(event);

                log.info("Published outbox event: {}", event.getId());

            } catch (Exception e) {
                handlePublishFailure(event, e);
            }
        }
    }

    private void publishEvent(OutboxEvent event) throws JsonProcessingException {
        String topic = determineTopic(event.getEventType());

        kafkaTemplate.send(
            topic,
            event.getAggregateId(),
            event.getPayload()
        ).get(5, TimeUnit.SECONDS);
    }

    private void handlePublishFailure(OutboxEvent event, Exception e) {
        log.error("Failed to publish outbox event: {}", event.getId(), e);

        event.setRetryCount(event.getRetryCount() + 1);
        event.setLastAttemptAt(LocalDateTime.now());
        event.setErrorMessage(e.getMessage());

        outboxRepository.save(event);

        if (event.getRetryCount() >= 3) {
            log.error("Max retries exceeded for event: {}", event.getId());
            // Send alert to monitoring system
        }
    }

    private String determineTopic(String eventType) {
        return switch (eventType) {
            case "OrderCreatedEvent", "OrderPaidEvent" -> "order-events";
            case "ProductCreatedEvent", "ProductStockDecreasedEvent" -> "product-events";
            default -> "default-events";
        };
    }
}
```

### Idempotent Event Publisher

```java
@Component
@RequiredArgsConstructor
public class IdempotentOutboxProcessor {
    private final OutboxEventRepository outboxRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Scheduled(fixedDelay = 5000)
    @Transactional
    public void processPendingEvents() {
        LocalDateTime threshold = LocalDateTime.now().minusMinutes(5);
        List<OutboxEvent> pendingEvents = outboxRepository.findPendingEvents(3, threshold);

        for (OutboxEvent event : pendingEvents) {
            if (shouldProcessEvent(event)) {
                publishEvent(event);
            }
        }
    }

    private boolean shouldProcessEvent(OutboxEvent event) {
        // Don't process if recently attempted
        if (event.getLastAttemptAt() != null &&
            event.getLastAttemptAt().isAfter(LocalDateTime.now().minusMinutes(1))) {
            return false;
        }

        return true;
    }

    private void publishEvent(OutboxEvent event) {
        try {
            kafkaTemplate.send(
                determineTopic(event.getEventType()),
                event.getAggregateId(),
                event.getPayload()
            ).get();

            event.setPublishedAt(LocalDateTime.now());
            outboxRepository.save(event);

        } catch (Exception e) {
            event.setRetryCount(event.getRetryCount() + 1);
            event.setLastAttemptAt(LocalDateTime.now());
            event.setErrorMessage(e.getMessage());
            outboxRepository.save(event);
        }
    }
}
```

## Cleanup Strategy

### Purge Published Events

```java
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.transaction.annotation.Transactional;

@Component
@RequiredArgsConstructor
public class OutboxCleanupService {
    private final OutboxEventRepository outboxRepository;

    @Scheduled(cron = "0 0 2 * * ?") // 2 AM daily
    @Transactional
    public void purgePublishedEvents() {
        LocalDateTime cutoff = LocalDateTime.now().minusDays(7);

        List<OutboxEvent> eventsToDelete = outboxRepository
            .findByPublishedAtBeforeAndPublishedAtIsNotNull(cutoff);

        outboxRepository.deleteAll(eventsToDelete);

        log.info("Purged {} published outbox events", eventsToDelete.size());
    }
}
```

### Archive Old Events

```java
@Scheduled(cron = "0 0 3 * * ?") // 3 AM daily
@Transactional
public void archivePublishedEvents() {
    LocalDateTime cutoff = LocalDateTime.now().minusDays(30);

    List<OutboxEvent> eventsToArchive = outboxRepository
        .findByPublishedAtBeforeAndPublishedAtIsNotNull(cutoff);

    // Move to archive table or external storage
    archiveService.archiveEvents(eventsToArchive);

    outboxRepository.deleteAll(eventsToArchive);

    log.info("Archived {} outbox events", eventsToArchive.size());
}
```

## Outbox Pattern Variations

### Optimistic Locking

```java
@Entity
@Table(name = "outbox_events")
@Getter
@Setter
public class OutboxEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Version
    private Long version;

    // ... other fields
}

@Component
public class OptimisticLockingProcessor {
    @Transactional
    public void processEvent(OutboxEvent event) {
        try {
            publishEvent(event);

            event.setPublishedAt(LocalDateTime.now());
            outboxRepository.save(event);

        } catch (ObjectOptimisticLockingFailureException e) {
            log.warn("Concurrent modification detected for event: {}", event.getId());
            // Retry after delay
        }
    }
}
```

### Batch Processing

```java
@Component
public class BatchOutboxProcessor {
    private static final int BATCH_SIZE = 100;

    @Scheduled(fixedDelay = 5000)
    @Transactional
    public void processPendingEvents() {
        int page = 0;
        List<OutboxEvent> batch;

        do {
            Pageable pageable = PageRequest.of(page, BATCH_SIZE);
            batch = outboxRepository.findByPublishedAtNullOrderByCreatedAtAsc(pageable);

            if (!batch.isEmpty()) {
                publishBatch(batch);
            }

            page++;
        } while (batch.size() == BATCH_SIZE);
    }

    private void publishBatch(List<OutboxEvent> batch) {
        batch.forEach(event -> {
            try {
                publishEvent(event);
                event.setPublishedAt(LocalDateTime.now());
            } catch (Exception e) {
                event.setRetryCount(event.getRetryCount() + 1);
                event.setErrorMessage(e.getMessage());
            }
        });

        outboxRepository.saveAll(batch);
    }
}
```

## Monitoring and Alerts

### Outbox Metrics

```java
@Component
@RequiredArgsConstructor
public class OutboxMetricsReporter {
    private final OutboxEventRepository outboxRepository;
    private final MeterRegistry meterRegistry;

    @Scheduled(fixedDelay = 60000)
    public void reportMetrics() {
        long pendingCount = outboxRepository.countByPublishedAtNull();
        long failedCount = outboxRepository.countByRetryCountGreaterThanEqual(3);

        meterRegistry.gauge("outbox.pending.events", pendingCount);
        meterRegistry.gauge("outbox.failed.events", failedCount);

        if (pendingCount > 1000) {
            log.warn("High outbox backlog: {} pending events", pendingCount);
        }

        if (failedCount > 100) {
            log.error("Many failed outbox events: {}", failedCount);
            // Send alert
        }
    }
}
```
