# Spring Boot SAGA Pattern - Reference Documentation

## Table of Contents

1. [Saga Pattern Overview](#saga-pattern-overview)
2. [Choreography-Based Saga](#choreography-based-saga)
3. [Orchestration-Based Saga](#orchestration-based-saga)
4. [Spring Boot Integration](#spring-boot-integration)
5. [Saga Frameworks](#saga-frameworks)
6. [Event-Driven Architecture](#event-driven-architecture)
7. [Compensating Transactions](#compensating-transactions)
8. [State Management](#state-management)
9. [Error Handling and Retry](#error-handling-and-retry)
10. [Testing Strategies](#testing-strategies)

---

## Saga Pattern Overview

### Definition

A **Saga** is a sequence of local transactions where each transaction updates data within a single service. Each local transaction publishes an event or message that triggers the next local transaction in the saga. If a local transaction fails, the saga executes compensating transactions to undo the changes made by preceding transactions.

### Key Characteristics

**Distributed Transactions**: Spans multiple microservices, each with its own database.

**Local Transactions**: Each service performs its own ACID transaction.

**Event-Driven**: Services communicate through events or commands.

**Compensations**: Rollback mechanism using compensating transactions.

**Eventual Consistency**: System reaches a consistent state over time.

### Saga vs Two-Phase Commit (2PC)

| Feature | Saga Pattern | Two-Phase Commit |
|---------|-------------|------------------|
| Locking | No distributed locks | Requires locks during commit |
| Performance | Better performance | Performance bottleneck |
| Scalability | Highly scalable | Limited scalability |
| Complexity | Business logic complexity | Protocol complexity |
| Failure Handling | Compensating transactions | Automatic rollback |
| Isolation | Lower isolation | Full isolation |
| NoSQL Support | Yes | No |
| Microservices Fit | Excellent | Poor |

### ACID vs BASE

**ACID** (Traditional Databases):
- **A**tomicity: All or nothing
- **C**onsistency: Valid state transitions
- **I**solation: Concurrent transactions don't interfere
- **D**urability: Committed data persists

**BASE** (Saga Pattern):
- **B**asically **A**vailable: System is available most of the time
- **S**oft state: State may change over time
- **E**ventual consistency: System becomes consistent eventually

---

## Choreography-Based Saga

### Architecture

Each service produces and listens to events. Services know what to do when they receive an event.

```
Service A → Event → Service B → Event → Service C
    ↓                   ↓                   ↓
  Event              Event               Event
    ↓                   ↓                   ↓
Compensation    Compensation        Compensation
```

### Event Flow

**Success Flow**:
1. Order Service creates order → publishes `OrderCreated` event
2. Payment Service listens → processes payment → publishes `PaymentProcessed` event
3. Inventory Service listens → reserves inventory → publishes `InventoryReserved` event
4. Shipment Service listens → prepares shipment → publishes `ShipmentPrepared` event

**Failure Flow** (Payment fails):
1. Payment Service publishes `PaymentFailed` event
2. Order Service listens → cancels order → publishes `OrderCancelled` event

### Implementation Components

#### Event Publisher

```java
@Component
public class OrderEventPublisher {
    private final StreamBridge streamBridge;
    
    public OrderEventPublisher(StreamBridge streamBridge) {
        this.streamBridge = streamBridge;
    }
    
    public void publishOrderCreatedEvent(String orderId, BigDecimal amount, String itemId) {
        OrderCreatedEvent event = new OrderCreatedEvent(orderId, amount, itemId);
        streamBridge.send("orderCreated-out-0", 
            MessageBuilder
                .withPayload(event)
                .setHeader(MessageHeaders.CONTENT_TYPE, MimeTypeUtils.APPLICATION_JSON)
                .build());
    }
}
```

#### Event Listener

```java
@Component
public class PaymentEventListener {
    
    @Bean
    public Consumer<OrderCreatedEvent> handleOrderCreatedEvent() {
        return event -> processPayment(event.getOrderId());
    }
    
    private void processPayment(String orderId) {
        // Payment processing logic
    }
}
```

#### Event Classes

```java
public record OrderCreatedEvent(
    String orderId,
    BigDecimal amount,
    String itemId
) {}

public record PaymentProcessedEvent(
    String paymentId,
    String orderId,
    String itemId
) {}

public record PaymentFailedEvent(
    String paymentId,
    String orderId,
    String itemId,
    String reason
) {}
```

### Spring Cloud Stream Configuration

```yaml
spring:
  cloud:
    stream:
      bindings:
        orderCreated-out-0:
          destination: order-events
        paymentProcessed-out-0:
          destination: payment-events
        paymentFailed-out-0:
          destination: payment-events
      kafka:
        binder:
          brokers: localhost:9092
```

### Maven Dependencies

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-stream</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-stream-binder-kafka</artifactId>
</dependency>
```

### Gradle Dependencies

```groovy
implementation 'org.springframework.cloud:spring-cloud-stream'
implementation 'org.springframework.cloud:spring-cloud-stream-binder-kafka'
```

---

## Orchestration-Based Saga

### Architecture

A central **Saga Orchestrator** coordinates the entire transaction flow, sending commands to services and handling responses.

```
         Saga Orchestrator
         /     |      \
    Service A  Service B  Service C
```

### Orchestrator Responsibilities

1. **Command Dispatch**: Sends commands to services
2. **Response Handling**: Processes service responses
3. **State Management**: Tracks saga execution state
4. **Compensation Coordination**: Triggers compensating transactions on failure
5. **Timeout Management**: Handles service timeouts
6. **Retry Logic**: Manages retry attempts

### Axon Framework Implementation

#### Saga Class

```java
@Saga
public class OrderSaga {
    
    @Autowired
    private transient CommandGateway commandGateway;
    
    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCreatedEvent event) {
        String paymentId = UUID.randomUUID().toString();
        ProcessPaymentCommand command = new ProcessPaymentCommand(
            paymentId, 
            event.getOrderId(), 
            event.getAmount(), 
            event.getItemId()
        );
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentProcessedEvent event) {
        ReserveInventoryCommand command = new ReserveInventoryCommand(
            event.getOrderId(), 
            event.getItemId()
        );
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentFailedEvent event) {
        CancelOrderCommand command = new CancelOrderCommand(event.getOrderId());
        commandGateway.send(command);
        end();
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(InventoryReservedEvent event) {
        PrepareShipmentCommand command = new PrepareShipmentCommand(
            event.getOrderId(), 
            event.getItemId()
        );
        commandGateway.send(command);
    }
    
    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCompletedEvent event) {
        // Saga completed successfully
    }
}
```

#### Aggregate for Order Service

```java
@Aggregate
public class OrderAggregate {
    
    @AggregateIdentifier
    private String orderId;
    
    private OrderStatus status;
    
    public OrderAggregate() {
    }
    
    @CommandHandler
    public OrderAggregate(CreateOrderCommand command) {
        apply(new OrderCreatedEvent(
            command.getOrderId(), 
            command.getAmount(), 
            command.getItemId()
        ));
    }
    
    @EventSourcingHandler
    public void on(OrderCreatedEvent event) {
        this.orderId = event.getOrderId();
        this.status = OrderStatus.PENDING;
    }
    
    @CommandHandler
    public void handle(CancelOrderCommand command) {
        apply(new OrderCancelledEvent(command.getOrderId()));
    }
    
    @EventSourcingHandler
    public void on(OrderCancelledEvent event) {
        this.status = OrderStatus.CANCELLED;
    }
}
```

#### Aggregate for Payment Service

```java
@Aggregate
public class PaymentAggregate {
    
    @AggregateIdentifier
    private String paymentId;
    
    public PaymentAggregate() {
    }
    
    @CommandHandler
    public PaymentAggregate(ProcessPaymentCommand command) {
        this.paymentId = command.getPaymentId();
        
        if (command.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            apply(new PaymentFailedEvent(
                command.getPaymentId(),
                command.getOrderId(),
                command.getItemId(),
                "Payment amount must be greater than zero"
            ));
        } else {
            apply(new PaymentProcessedEvent(
                command.getPaymentId(),
                command.getOrderId(),
                command.getItemId()
            ));
        }
    }
}
```

### Axon Configuration

```yaml
axon:
  serializer:
    general: jackson
    events: jackson
    messages: jackson
  eventhandling:
    processors:
      order-processor:
        mode: tracking
        source: eventBus
  axonserver:
    enabled: false
```

### Maven Dependencies for Axon

```xml
<dependency>
    <groupId>org.axonframework</groupId>
    <artifactId>axon-spring-boot-starter</artifactId>
    <version>4.9.0</version>
</dependency>
```

---

## Spring Boot Integration

### Application Configuration

```java
@SpringBootApplication
@EnableScheduling
public class SagaApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(SagaApplication.class, args);
    }
}
```

### Kafka Configuration

```java
@Configuration
public class KafkaConfig {
    
    @Bean
    public NewTopic orderTopic() {
        return new NewTopic("order-events", 3, (short) 1);
    }
    
    @Bean
    public NewTopic paymentTopic() {
        return new NewTopic("payment-events", 3, (short) 1);
    }
    
    @Bean
    public NewTopic inventoryTopic() {
        return new NewTopic("inventory-events", 3, (short) 1);
    }
}
```

### Properties Configuration

```properties
# Application
spring.application.name=saga-service

# Kafka
spring.kafka.bootstrap-servers=localhost:9092
spring.kafka.consumer.group-id=saga-group
spring.kafka.consumer.auto-offset-reset=earliest
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.springframework.kafka.support.serializer.JsonDeserializer
spring.kafka.consumer.properties.spring.json.trusted.packages=*
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer

# Database
spring.datasource.url=jdbc:postgresql://localhost:5432/sagadb
spring.datasource.username=saga
spring.datasource.password=saga
spring.jpa.hibernate.ddl-auto=update
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect

# Actuator
management.endpoints.web.exposure.include=health,metrics,prometheus
management.endpoint.health.show-details=always
```

---

## Saga Frameworks

### Axon Framework

**Type**: Orchestration-based

**Features**:
- Event sourcing support
- CQRS pattern implementation
- Saga state management
- Automatic compensation
- Built-in retry mechanisms

**Use When**:
- Complex domain logic
- Event sourcing is beneficial
- CQRS pattern is needed
- Mature framework is required

### Eventuate Tram Sagas

**Type**: Orchestration-based

**Features**:
- Database-per-service support
- Transactional messaging
- Saga orchestration DSL
- Multiple messaging platforms

**Use When**:
- Existing JPA-based services
- Transactional outbox pattern needed
- Multiple message brokers support required

### Camunda

**Type**: BPMN-based orchestration

**Features**:
- Visual workflow design
- BPMN 2.0 standard
- Human tasks support
- Complex workflow modeling

**Use When**:
- Business process modeling needed
- Visual workflow design preferred
- Human approval steps required
- Complex orchestration logic

### Apache Camel Saga EIP

**Type**: Enterprise Integration Pattern

**Features**:
- Saga EIP implementation
- Multiple protocol support
- Route-based compensation
- Integration with multiple systems

**Use When**:
- Enterprise integration scenarios
- Multiple protocol support needed
- Existing Camel infrastructure

---

## Event-Driven Architecture

### Event Types

**Domain Events**: Represent business facts that happened
```java
public record OrderCreatedEvent(
    String orderId,
    Instant createdAt,
    BigDecimal amount
) implements DomainEvent {}
```

**Integration Events**: Communication between bounded contexts
```java
public record PaymentRequestedEvent(
    String orderId,
    String paymentId,
    BigDecimal amount
) implements IntegrationEvent {}
```

**Command Events**: Request for action
```java
public record ProcessPaymentCommand(
    String paymentId,
    String orderId,
    BigDecimal amount
) {}
```

### Event Versioning

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

### Event Store

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

---

## Compensating Transactions

### Design Principles

**Idempotency**: Execute multiple times with same result
```java
public void cancelPayment(String paymentId) {
    Payment payment = paymentRepository.findById(paymentId)
        .orElse(null);
    
    if (payment == null) {
        // Already cancelled or doesn't exist
        return;
    }
    
    if (payment.getStatus() == PaymentStatus.CANCELLED) {
        // Already cancelled, idempotent
        return;
    }
    
    payment.setStatus(PaymentStatus.CANCELLED);
    paymentRepository.save(payment);
    
    // Refund logic here
}
```

**Retryability**: Safe to retry on failure
```java
@Retryable(
    value = {TransientException.class},
    maxAttempts = 3,
    backoff = @Backoff(delay = 1000, multiplier = 2)
)
public void releaseInventory(String itemId, int quantity) {
    // Implementation
}
```

### Compensation Strategies

**Backward Recovery**: Undo completed steps
```java
@SagaEventHandler(associationProperty = "orderId")
public void handle(PaymentFailedEvent event) {
    // Step 1: Cancel shipment preparation
    commandGateway.send(new CancelShipmentCommand(event.getOrderId()));
    
    // Step 2: Release inventory
    commandGateway.send(new ReleaseInventoryCommand(event.getOrderId()));
    
    // Step 3: Cancel order
    commandGateway.send(new CancelOrderCommand(event.getOrderId()));
    
    end();
}
```

**Forward Recovery**: Retry failed operation
```java
@SagaEventHandler(associationProperty = "orderId")
public void handle(PaymentTransientFailureEvent event) {
    if (event.getRetryCount() < MAX_RETRIES) {
        // Retry payment
        ProcessPaymentCommand retryCommand = new ProcessPaymentCommand(
            event.getPaymentId(),
            event.getOrderId(),
            event.getAmount()
        );
        commandGateway.send(retryCommand);
    } else {
        // Compensate
        handlePaymentFailure(event);
    }
}
```

### Semantic Lock Pattern

Prevent concurrent modifications during saga execution:

```java
@Entity
public class Order {
    @Id
    private String orderId;
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
    
    @Version
    private Long version;
    
    private Instant lockedUntil;
    
    public boolean tryLock(Duration lockDuration) {
        if (isLocked()) {
            return false;
        }
        this.lockedUntil = Instant.now().plus(lockDuration);
        return true;
    }
    
    public boolean isLocked() {
        return lockedUntil != null && 
               Instant.now().isBefore(lockedUntil);
    }
    
    public void unlock() {
        this.lockedUntil = null;
    }
}
```

---

## State Management

### Saga State

```java
@Entity
@Table(name = "saga_state")
public class SagaState {
    
    @Id
    private String sagaId;
    
    @Enumerated(EnumType.STRING)
    private SagaStatus status;
    
    @Column(columnDefinition = "TEXT")
    private String currentStep;
    
    @Column(columnDefinition = "TEXT")
    private String compensationSteps;
    
    private Instant startedAt;
    private Instant completedAt;
    
    @Version
    private Long version;
}

public enum SagaStatus {
    STARTED,
    PROCESSING,
    COMPENSATING,
    COMPLETED,
    FAILED,
    CANCELLED
}
```

### State Machine with Spring Statemachine

```java
@Configuration
@EnableStateMachine
public class SagaStateMachineConfig 
    extends StateMachineConfigurerAdapter<SagaStatus, SagaEvent> {
    
    @Override
    public void configure(
        StateMachineStateConfigurer<SagaStatus, SagaEvent> states) 
        throws Exception {
        
        states
            .withStates()
            .initial(SagaStatus.STARTED)
            .states(EnumSet.allOf(SagaStatus.class))
            .end(SagaStatus.COMPLETED)
            .end(SagaStatus.FAILED);
    }
    
    @Override
    public void configure(
        StateMachineTransitionConfigurer<SagaStatus, SagaEvent> transitions) 
        throws Exception {
        
        transitions
            .withExternal()
                .source(SagaStatus.STARTED)
                .target(SagaStatus.PROCESSING)
                .event(SagaEvent.ORDER_CREATED)
            .and()
            .withExternal()
                .source(SagaStatus.PROCESSING)
                .target(SagaStatus.COMPLETED)
                .event(SagaEvent.ALL_STEPS_COMPLETED)
            .and()
            .withExternal()
                .source(SagaStatus.PROCESSING)
                .target(SagaStatus.COMPENSATING)
                .event(SagaEvent.STEP_FAILED)
            .and()
            .withExternal()
                .source(SagaStatus.COMPENSATING)
                .target(SagaStatus.FAILED)
                .event(SagaEvent.COMPENSATION_COMPLETED);
    }
}
```

---

## Error Handling and Retry

### Retry Configuration

```java
@Configuration
@EnableRetry
public class RetryConfig {
    
    @Bean
    public RetryTemplate retryTemplate() {
        RetryTemplate retryTemplate = new RetryTemplate();
        
        FixedBackOffPolicy backOffPolicy = new FixedBackOffPolicy();
        backOffPolicy.setBackOffPeriod(2000L);
        retryTemplate.setBackOffPolicy(backOffPolicy);
        
        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy();
        retryPolicy.setMaxAttempts(3);
        retryTemplate.setRetryPolicy(retryPolicy);
        
        return retryTemplate;
    }
}
```

### Circuit Breaker with Resilience4j

```java
@Configuration
public class CircuitBreakerConfig {
    
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .waitDurationInOpenState(Duration.ofMillis(1000))
            .slidingWindowSize(2)
            .build();
        
        return CircuitBreakerRegistry.of(config);
    }
}

@Service
public class PaymentService {
    
    private final CircuitBreaker circuitBreaker;
    
    public PaymentService(CircuitBreakerRegistry registry) {
        this.circuitBreaker = registry.circuitBreaker("payment");
    }
    
    public PaymentResult processPayment(PaymentRequest request) {
        return circuitBreaker.executeSupplier(
            () -> callPaymentGateway(request)
        );
    }
}
```

### Dead Letter Queue

```java
@Configuration
public class DeadLetterQueueConfig {
    
    @Bean
    public NewTopic deadLetterTopic() {
        return new NewTopic("saga-dlq", 1, (short) 1);
    }
}

@Component
public class SagaErrorHandler implements ConsumerAwareErrorHandler {
    
    private final KafkaTemplate<String, Object> kafkaTemplate;
    
    @Override
    public void handle(Exception thrownException, 
                      List<ConsumerRecord<?, ?>> records,
                      Consumer<?, ?> consumer, 
                      MessageListenerContainer container) {
        
        records.forEach(record -> {
            kafkaTemplate.send("saga-dlq", record.key(), record.value());
        });
    }
}
```

---

## Testing Strategies

### Unit Testing Saga

```java
@Test
void shouldCompensateWhenPaymentFails() {
    // Given
    OrderSaga saga = new OrderSaga();
    FixtureConfiguration<OrderSaga> fixture = new SagaTestFixture<>(OrderSaga.class);
    
    String orderId = UUID.randomUUID().toString();
    String paymentId = UUID.randomUUID().toString();
    
    // When
    fixture
        .givenNoPriorActivity()
        .whenPublishingA(new OrderCreatedEvent(orderId, BigDecimal.TEN, "item-1"))
        .expectDispatchedCommands(new ProcessPaymentCommand(paymentId, orderId, BigDecimal.TEN));
    
    // Then - payment fails
    fixture
        .whenPublishingA(new PaymentFailedEvent(paymentId, orderId, "item-1", "Insufficient funds"))
        .expectDispatchedCommands(new CancelOrderCommand(orderId));
}
```

### Integration Testing with Testcontainers

```java
@SpringBootTest
@Testcontainers
class SagaIntegrationTest {
    
    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.4.0")
    );
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        "postgres:15-alpine"
    );
    
    @DynamicPropertySource
    static void overrideProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
    
    @Test
    void shouldCompleteOrderSagaSuccessfully() {
        // Test implementation
    }
}
```

### Testing Idempotency

```java
@Test
void compensationShouldBeIdempotent() {
    String paymentId = "payment-123";
    
    // Execute compensation first time
    paymentService.cancelPayment(paymentId);
    Payment firstResult = paymentRepository.findById(paymentId).orElseThrow();
    
    // Execute compensation second time
    paymentService.cancelPayment(paymentId);
    Payment secondResult = paymentRepository.findById(paymentId).orElseThrow();
    
    // Should produce same result
    assertThat(firstResult).isEqualTo(secondResult);
    assertThat(secondResult.getStatus()).isEqualTo(PaymentStatus.CANCELLED);
}
```

---

## Monitoring and Observability

### Micrometer Metrics

```java
@Component
public class SagaMetrics {
    
    private final Counter sagaStarted;
    private final Counter sagaCompleted;
    private final Counter sagaFailed;
    private final Timer sagaDuration;
    
    public SagaMetrics(MeterRegistry registry) {
        this.sagaStarted = Counter.builder("saga.started")
            .description("Number of sagas started")
            .register(registry);
            
        this.sagaCompleted = Counter.builder("saga.completed")
            .description("Number of sagas completed successfully")
            .register(registry);
            
        this.sagaFailed = Counter.builder("saga.failed")
            .description("Number of sagas failed")
            .register(registry);
            
        this.sagaDuration = Timer.builder("saga.duration")
            .description("Saga execution duration")
            .register(registry);
    }
    
    public void recordSagaStart() {
        sagaStarted.increment();
    }
    
    public void recordSagaCompletion(Duration duration) {
        sagaCompleted.increment();
        sagaDuration.record(duration);
    }
    
    public void recordSagaFailure() {
        sagaFailed.increment();
    }
}
```

### Distributed Tracing

```java
@Configuration
public class TracingConfig {
    
    @Bean
    public Tracer tracer() {
        return new Tracer.Builder()
            .spanReporter(new ZipkinSpanReporter())
            .build();
    }
}

@Service
public class OrderService {
    
    @Autowired
    private Tracer tracer;
    
    public void createOrder(OrderRequest request) {
        Span span = tracer.newTrace().name("create-order").start();
        try (Tracer.SpanInScope ws = tracer.withSpanInScope(span)) {
            // Order creation logic
            span.tag("orderId", request.getOrderId());
        } finally {
            span.finish();
        }
    }
}
```

### Health Checks

```java
@Component
public class SagaHealthIndicator implements HealthIndicator {
    
    private final SagaStateRepository sagaStateRepository;
    
    @Override
    public Health health() {
        long stuckSagas = sagaStateRepository.countStuckSagas(
            Duration.ofMinutes(30)
        );
        
        if (stuckSagas > 10) {
            return Health.down()
                .withDetail("stuckSagas", stuckSagas)
                .build();
        }
        
        return Health.up()
            .withDetail("stuckSagas", stuckSagas)
            .build();
    }
}
```

---

## Performance Considerations

### Batch Processing

```java
@Service
public class BatchSagaProcessor {
    
    @Scheduled(fixedDelay = 5000)
    public void processPendingSagas() {
        List<SagaState> pendingSagas = sagaStateRepository
            .findByStatus(SagaStatus.PROCESSING, PageRequest.of(0, 100));
        
        pendingSagas.forEach(this::processSaga);
    }
}
```

### Parallel Execution

```java
@SagaEventHandler(associationProperty = "orderId")
public void handle(PaymentProcessedEvent event) {
    // Execute inventory and notification in parallel
    CompletableFuture.allOf(
        CompletableFuture.runAsync(() -> 
            commandGateway.send(new ReserveInventoryCommand(event.getOrderId()))
        ),
        CompletableFuture.runAsync(() -> 
            commandGateway.send(new SendNotificationCommand(event.getOrderId()))
        )
    ).join();
}
```

### Database Optimization

```sql
-- Index for saga state queries
CREATE INDEX idx_saga_state_status ON saga_state(status);
CREATE INDEX idx_saga_state_started_at ON saga_state(started_at);

-- Index for event store queries
CREATE INDEX idx_saga_events_saga_id ON saga_events(saga_id);
CREATE INDEX idx_saga_events_timestamp ON saga_events(timestamp);
```

---

## Security Best Practices

### Message Authentication

```java
@Configuration
public class MessageSecurityConfig {
    
    @Bean
    public MessageSigningInterceptor messageSigningInterceptor() {
        return new MessageSigningInterceptor(secretKey);
    }
}

public class MessageSigningInterceptor implements ProducerInterceptor<String, Object> {
    
    @Override
    public ProducerRecord<String, Object> onSend(ProducerRecord<String, Object> record) {
        String signature = computeSignature(record.value());
        Headers headers = record.headers();
        headers.add("signature", signature.getBytes(StandardCharsets.UTF_8));
        return record;
    }
}
```

### Audit Logging

```java
@Aspect
@Component
public class SagaAuditAspect {
    
    @Around("@annotation(SagaOperation)")
    public Object auditSagaOperation(ProceedingJoinPoint joinPoint) throws Throwable {
        String sagaId = extractSagaId(joinPoint);
        String operation = joinPoint.getSignature().getName();
        
        auditLog.info("Saga operation started: sagaId={}, operation={}", 
            sagaId, operation);
        
        try {
            Object result = joinPoint.proceed();
            auditLog.info("Saga operation completed: sagaId={}, operation={}", 
                sagaId, operation);
            return result;
        } catch (Exception e) {
            auditLog.error("Saga operation failed: sagaId={}, operation={}, error={}", 
                sagaId, operation, e.getMessage());
            throw e;
        }
    }
}
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Lost Messages

**Problem**: Messages get lost due to broker failures.

**Solution**: Use persistent messages and acknowledgments.

```java
@Bean
public ProducerFactory<String, Object> producerFactory() {
    Map<String, Object> config = new HashMap<>();
    config.put(ProducerConfig.ACKS_CONFIG, "all");
    config.put(ProducerConfig.RETRIES_CONFIG, 3);
    config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
    return new DefaultKafkaProducerFactory<>(config);
}
```

### Pitfall 2: Duplicate Processing

**Problem**: Same message processed multiple times.

**Solution**: Implement idempotency with deduplication.

```java
@Service
public class DeduplicationService {
    
    private final Set<String> processedMessageIds = ConcurrentHashMap.newKeySet();
    
    public boolean isDuplicate(String messageId) {
        return !processedMessageIds.add(messageId);
    }
}
```

### Pitfall 3: Saga State Inconsistency

**Problem**: Saga state doesn't match actual service states.

**Solution**: Use event sourcing or state reconciliation.

```java
@Scheduled(fixedDelay = 60000)
public void reconcileSagaStates() {
    List<SagaState> processingSagas = 
        sagaStateRepository.findByStatus(SagaStatus.PROCESSING);
    
    processingSagas.forEach(saga -> {
        if (isActuallyCompleted(saga)) {
            saga.setStatus(SagaStatus.COMPLETED);
            sagaStateRepository.save(saga);
        }
    });
}
```

---

## Additional Resources

- [Microservices.io - Saga Pattern](https://microservices.io/patterns/data/saga.html)
- [Axon Framework Documentation](https://docs.axoniq.io/reference-guide/)
- [Spring Cloud Stream Reference](https://spring.io/projects/spring-cloud-stream)
- [Eventuate Tram Documentation](https://eventuate.io/docs/manual/eventuate-tram/latest/)
- [Camunda Platform](https://docs.camunda.org/)
- [Apache Camel Saga EIP](https://camel.apache.org/components/latest/eips/saga-eip.html)
