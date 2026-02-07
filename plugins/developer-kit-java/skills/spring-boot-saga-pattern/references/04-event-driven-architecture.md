# Event-Driven Architecture in Sagas

## Event Types

### Domain Events

Represent business facts that happened within a service:

```java
public record OrderCreatedEvent(
    String orderId,
    Instant createdAt,
    BigDecimal amount
) implements DomainEvent {}
```

### Integration Events

Communication between bounded contexts (microservices):

```java
public record PaymentRequestedEvent(
    String orderId,
    String paymentId,
    BigDecimal amount
) implements IntegrationEvent {}
```

### Command Events

Request for action by another service:

```java
public record ProcessPaymentCommand(
    String paymentId,
    String orderId,
    BigDecimal amount
) {}
```

## Event Versioning

Handle event schema evolution using versioning:

```java
public record OrderCreatedEventV1(
    String orderId,
    BigDecimal amount
) {}

public record OrderCreatedEventV2(
    String orderId,
    BigDecimal amount,
    String customerId,
    Instant timestamp
) {}

// Event Upcaster
public class OrderEventUpcaster implements EventUpcaster {
    @Override
    public Stream<IntermediateEventRepresentation> upcast(
        Stream<IntermediateEventRepresentation> eventStream) {

        return eventStream.map(event -> {
            if (event.getType().getName().equals("OrderCreatedEventV1")) {
                return upcastV1ToV2(event);
            }
            return event;
        });
    }
}
```

## Event Store

Store all events for audit trail and recovery:

```java
@Entity
@Table(name = "saga_events")
public class SagaEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String sagaId;

    @Column(nullable = false)
    private String eventType;

    @Column(columnDefinition = "TEXT")
    private String payload;

    @Column(nullable = false)
    private Instant timestamp;

    @Column(nullable = false)
    private Integer version;
}
```

## Event Publishing Patterns

### Outbox Pattern (Transactional)

Ensure atomic update of database and event publishing:

```java
@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final OutboxRepository outboxRepository;

    @Transactional
    public void createOrder(CreateOrderRequest request) {
        // 1. Create and save order
        Order order = new Order(...);
        orderRepository.save(order);

        // 2. Create outbox entry in same transaction
        OutboxEntry entry = new OutboxEntry(
            "OrderCreated",
            order.getId(),
            new OrderCreatedEvent(...)
        );
        outboxRepository.save(entry);
    }
}

@Component
public class OutboxPoller {

    @Scheduled(fixedDelay = 1000)
    public void pollAndPublish() {
        List<OutboxEntry> unpublished = outboxRepository.findUnpublished();

        unpublished.forEach(entry -> {
            eventPublisher.publish(entry.getEvent());
            outboxRepository.markAsPublished(entry.getId());
        });
    }
}
```

### Direct Publishing Pattern

Publish events immediately after transaction:

```java
@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final EventPublisher eventPublisher;

    @Transactional
    public void createOrder(CreateOrderRequest request) {
        Order order = new Order(...);
        orderRepository.save(order);

        // Publish event after transaction commits
        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    eventPublisher.publish(new OrderCreatedEvent(...));
                }
            }
        );
    }
}
```

## Event Sourcing

Store all state changes as events instead of current state:

**Benefits**:
- Complete audit trail
- Time-travel debugging
- Natural fit for sagas
- Event replay for recovery

**Implementation**:

```java
@Entity
public class Order {

    @Id
    private String orderId;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    private List<DomainEvent> events = new ArrayList<>();

    public void createOrder(...) {
        apply(new OrderCreatedEvent(...));
    }

    protected void apply(DomainEvent event) {
        if (event instanceof OrderCreatedEvent e) {
            this.orderId = e.orderId();
            this.status = OrderStatus.PENDING;
        }
        events.add(event);
    }

    public List<DomainEvent> getUncommittedEvents() {
        return new ArrayList<>(events);
    }

    public void clearUncommittedEvents() {
        events.clear();
    }
}
```

## Event Ordering and Consistency

### Maintain Event Order

Use partitioning to maintain order within a saga:

```java
@Bean
public ProducerFactory<String, Object> producerFactory() {
    Map<String, Object> config = new HashMap<>();
    config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
        StringSerializer.class);
    return new DefaultKafkaProducerFactory<>(config);
}

@Service
public class EventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publish(DomainEvent event) {
        // Use sagaId as key to maintain order
        kafkaTemplate.send("events", event.getSagaId(), event);
    }
}
```

### Handle Out-of-Order Events

Use saga state to detect and handle out-of-order events:

```java
@SagaEventHandler(associationProperty = "orderId")
public void handle(PaymentProcessedEvent event) {
    if (saga.getStatus() != SagaStatus.AWAITING_PAYMENT) {
        // Out of order event, ignore or queue for retry
        logger.warn("Unexpected event in state: {}", saga.getStatus());
        return;
    }
    // Process event
}
```
