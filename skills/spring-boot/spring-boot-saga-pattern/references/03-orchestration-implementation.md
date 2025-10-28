# Orchestration-Based Saga Implementation

## Architecture Overview

A **central orchestrator** (Saga Coordinator) manages the entire transaction flow, sending commands to services and handling responses.

```
         Saga Orchestrator
         /     |      \
    Service A  Service B  Service C
```

## Orchestrator Responsibilities

1. **Command Dispatch**: Send commands to services
2. **Response Handling**: Process service responses
3. **State Management**: Track saga execution state
4. **Compensation Coordination**: Trigger compensating transactions on failure
5. **Timeout Management**: Handle service timeouts
6. **Retry Logic**: Manage retry attempts

## Axon Framework Implementation

### Saga Class

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

### Aggregate for Order Service

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

### Aggregate for Payment Service

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

## Axon Configuration

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

## Maven Dependencies for Axon

```xml
<dependency>
    <groupId>org.axonframework</groupId>
    <artifactId>axon-spring-boot-starter</artifactId>
    <version>4.9.0</version> // Use latest stable version
</dependency>
```

## Advantages and Disadvantages

### Advantages

- **Centralized visibility** - easy to see workflow status
- **Easier to troubleshoot** - single place to analyze flow
- **Clear transaction flow** - orchestrator defines sequence
- **Simplified error handling** - centralized compensation logic
- **Better for complex workflows** - easier to manage many steps

### Disadvantages

- **Orchestrator becomes single point of failure** - can be mitigated with clustering
- **Additional infrastructure component** - more complexity in deployment
- **Potential tight coupling** - if orchestrator knows too much about services

## Eventuate Tram Sagas

Eventuate Tram is an alternative to Axon for orchestration-based sagas:

```xml
<dependency>
    <groupId>io.eventuate.tram.sagas</groupId>
    <artifactId>eventuate-tram-sagas-spring-starter</artifactId>
    <version>0.28.0</version> // Use latest stable version
</dependency>
```

## Camunda for BPMN-Based Orchestration

Use Camunda when visual workflow design is beneficial:

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

## When to Use Orchestration

Use orchestration-based sagas when:
- Building brownfield applications with existing microservices
- Handling complex workflows with many steps
- Centralized control and monitoring is critical
- Organization wants clear visibility into saga execution
- Need for human intervention in workflow
