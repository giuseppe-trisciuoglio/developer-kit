# Compensating Transactions

## Design Principles

### Idempotency

Execute multiple times with same result:

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

### Retryability

Design operations to handle retries without side effects:

```java
@Retryable(
    value = {TransientException.class},
    maxAttempts = 3,
    backoff = @Backoff(delay = 1000, multiplier = 2)
)
public void releaseInventory(String itemId, int quantity) {
    // Use set operations for idempotency
    InventoryItem item = inventoryRepository.findById(itemId)
        .orElseThrow();

    item.increaseAvailableQuantity(quantity);
    inventoryRepository.save(item);
}
```

## Compensation Strategies

### Backward Recovery

Undo completed steps in reverse order:

```java
@SagaEventHandler(associationProperty = "orderId")
public void handle(PaymentFailedEvent event) {
    logger.error("Payment failed, initiating compensation");

    // Step 1: Cancel shipment preparation
    commandGateway.send(new CancelShipmentCommand(event.getOrderId()));

    // Step 2: Release inventory
    commandGateway.send(new ReleaseInventoryCommand(event.getOrderId()));

    // Step 3: Cancel order
    commandGateway.send(new CancelOrderCommand(event.getOrderId()));

    end();
}
```

### Forward Recovery

Retry failed operation with exponential backoff:

```java
@SagaEventHandler(associationProperty = "orderId")
public void handle(PaymentTransientFailureEvent event) {
    if (event.getRetryCount() < MAX_RETRIES) {
        // Retry payment with backoff
        ProcessPaymentCommand retryCommand = new ProcessPaymentCommand(
            event.getPaymentId(),
            event.getOrderId(),
            event.getAmount()
        );
        commandGateway.send(retryCommand);
    } else {
        // After max retries, compensate
        handlePaymentFailure(event);
    }
}
```

## Semantic Lock Pattern

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

## Compensation in Axon Framework

```java
@Saga
public class OrderSaga {

    private String orderId;
    private String paymentId;
    private String inventoryId;
    private boolean compensating = false;

    @SagaEventHandler(associationProperty = "orderId")
    public void handle(InventoryReservationFailedEvent event) {
        logger.error("Inventory reservation failed");
        compensating = true;

        // Compensate: refund payment
        RefundPaymentCommand refundCommand = new RefundPaymentCommand(
            paymentId,
            event.getOrderId(),
            event.getReservedAmount(),
            "Inventory unavailable"
        );

        commandGateway.send(refundCommand);
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentRefundedEvent event) {
        if (!compensating) return;

        logger.info("Payment refunded, cancelling order");

        // Compensate: cancel order
        CancelOrderCommand command = new CancelOrderCommand(
            event.getOrderId(),
            "Inventory unavailable - payment refunded"
        );

        commandGateway.send(command);
    }

    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCancelledEvent event) {
        logger.info("Saga completed with compensation");
    }
}
```

## Handling Compensation Failures

Handle cases where compensation itself fails:

```java
@Service
public class CompensationService {

    private final DeadLetterQueueService dlqService;

    public void handleCompensationFailure(String sagaId, String step, Exception cause) {
        logger.error("Compensation failed for saga {} at step {}", sagaId, step, cause);

        // Send to dead letter queue for manual intervention
        dlqService.send(new FailedCompensation(
            sagaId,
            step,
            cause.getMessage(),
            Instant.now()
        ));

        // Create alert for operations team
        alertingService.alert(
            "Compensation Failure",
            "Saga " + sagaId + " failed compensation at " + step
        );
    }
}
```

## Testing Compensation

Verify that compensation produces expected results:

```java
@Test
void shouldCompensateWhenPaymentFails() {
    String orderId = "order-123";
    String paymentId = "payment-456";

    // Arrange: execute payment
    Payment payment = new Payment(paymentId, orderId, BigDecimal.TEN);
    paymentRepository.save(payment);
    orderRepository.save(new Order(orderId, OrderStatus.PENDING));

    // Act: compensate
    paymentService.cancelPayment(paymentId);

    // Assert: verify idempotency
    paymentService.cancelPayment(paymentId);

    Payment result = paymentRepository.findById(paymentId).orElseThrow();
    assertThat(result.getStatus()).isEqualTo(PaymentStatus.CANCELLED);
}
```

## Common Compensation Patterns

### Inventory Release

```java
@Service
public class InventoryService {

    public void releaseInventory(String orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();

        order.getItems().forEach(item -> {
            InventoryItem inventoryItem = inventoryRepository
                .findById(item.getProductId())
                .orElseThrow();

            inventoryItem.increaseAvailableQuantity(item.getQuantity());
            inventoryRepository.save(inventoryItem);
        });
    }
}
```

### Payment Refund

```java
@Service
public class PaymentService {

    public void refundPayment(String paymentId) {
        Payment payment = paymentRepository.findById(paymentId)
            .orElseThrow();

        if (payment.getStatus() == PaymentStatus.PROCESSED) {
            payment.setStatus(PaymentStatus.REFUNDED);
            paymentGateway.refund(payment.getTransactionId());
            paymentRepository.save(payment);
        }
    }
}
```

### Order Cancellation

```java
@Service
public class OrderService {

    public void cancelOrder(String orderId, String reason) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow();

        order.setStatus(OrderStatus.CANCELLED);
        order.setCancellationReason(reason);
        order.setCancelledAt(Instant.now());

        orderRepository.save(order);
    }
}
```
