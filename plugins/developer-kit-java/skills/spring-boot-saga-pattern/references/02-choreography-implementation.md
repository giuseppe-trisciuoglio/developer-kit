# Choreography-Based Saga Implementation

## Architecture Overview

In choreography-based sagas, each service produces and listens to events. Services know what to do when they receive an event. **No central coordinator** manages the flow.

```
Service A → Event → Service B → Event → Service C
    ↓                   ↓                   ↓
  Event              Event               Event
    ↓                   ↓                   ↓
Compensation    Compensation        Compensation
```

## Event Flow

### Success Path

1. **Order Service** creates order → publishes `OrderCreated` event
2. **Payment Service** listens → processes payment → publishes `PaymentProcessed` event
3. **Inventory Service** listens → reserves inventory → publishes `InventoryReserved` event
4. **Shipment Service** listens → prepares shipment → publishes `ShipmentPrepared` event

### Failure Path (When Payment Fails)

1. **Payment Service** publishes `PaymentFailed` event
2. **Order Service** listens → cancels order → publishes `OrderCancelled` event
3. All other services respond to cancellation with cleanup

## Event Publisher

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

## Event Listener

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

## Event Classes

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

## Spring Cloud Stream Configuration

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

## Maven Dependencies

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

## Gradle Dependencies

```groovy
implementation 'org.springframework.cloud:spring-cloud-stream'
implementation 'org.springframework.cloud:spring-cloud-stream-binder-kafka'
```

## Advantages and Disadvantages

### Advantages

- **Simple** for small number of services
- **Loose coupling** between services
- **No single point of failure**
- Each service is independently deployable

### Disadvantages

- **Difficult to track workflow state** - distributed across services
- **Hard to troubleshoot** - following event flow is complex
- **Complexity grows** with number of services
- **Distributed source of truth** - saga state not centralized

## When to Use Choreography

Use choreography-based sagas when:
- Microservices are few in number (< 5 services per saga)
- Loose coupling is critical
- Team is experienced with event-driven architecture
- System can handle eventual consistency
- Workflow doesn't need centralized monitoring
