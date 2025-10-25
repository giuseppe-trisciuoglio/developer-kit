# Spring Boot SAGA Pattern - Examples

## Table of Contents

1. [E-Commerce Order Processing](#e-commerce-order-processing)
2. [Food Delivery Application](#food-delivery-application)
3. [Travel Booking System](#travel-booking-system)
4. [Banking Transfer System](#banking-transfer-system)
5. [Microservices Choreography Example](#microservices-choreography-example)
6. [Microservices Orchestration Example](#microservices-orchestration-example)

---

## E-Commerce Order Processing

Complete example of an order processing system using orchestration-based saga with Axon Framework.

### Architecture Overview

```
Order Service → Payment Service → Inventory Service → Shipment Service → Notification Service
     ↓               ↓                  ↓                   ↓                    ↓
  Compensation   Compensation      Compensation        Compensation         Compensation
```

### Project Structure

```
e-commerce-saga/
├── order-service/
│   ├── domain/
│   │   ├── model/
│   │   │   └── Order.java
│   │   ├── event/
│   │   │   ├── OrderCreatedEvent.java
│   │   │   └── OrderCancelledEvent.java
│   │   └── command/
│   │       ├── CreateOrderCommand.java
│   │       └── CancelOrderCommand.java
│   └── saga/
│       └── OrderSaga.java
├── payment-service/
│   ├── domain/
│   │   ├── model/
│   │   │   └── Payment.java
│   │   ├── event/
│   │   │   ├── PaymentProcessedEvent.java
│   │   │   └── PaymentFailedEvent.java
│   │   └── command/
│   │       ├── ProcessPaymentCommand.java
│   │       └── RefundPaymentCommand.java
│   └── aggregate/
│       └── PaymentAggregate.java
├── inventory-service/
├── shipment-service/
└── notification-service/
```

### Domain Models

#### Order Entity

```java
@Entity
@Table(name = "orders")
public class Order {
    
    @Id
    private String orderId;
    
    @Column(nullable = false)
    private String customerId;
    
    @Column(nullable = false)
    private BigDecimal totalAmount;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private OrderStatus status;
    
    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();
    
    @Column(nullable = false)
    private Instant createdAt;
    
    private Instant completedAt;
    
    @Version
    private Long version;
    
    // Constructor
    public Order() {
    }
    
    public Order(String orderId, String customerId, BigDecimal totalAmount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.totalAmount = totalAmount;
        this.status = OrderStatus.PENDING;
        this.createdAt = Instant.now();
    }
    
    // Business methods
    public void markAsProcessing() {
        if (this.status != OrderStatus.PENDING) {
            throw new IllegalStateException("Order must be pending to mark as processing");
        }
        this.status = OrderStatus.PROCESSING;
    }
    
    public void markAsCompleted() {
        if (this.status != OrderStatus.PROCESSING) {
            throw new IllegalStateException("Order must be processing to complete");
        }
        this.status = OrderStatus.COMPLETED;
        this.completedAt = Instant.now();
    }
    
    public void cancel() {
        if (this.status == OrderStatus.COMPLETED) {
            throw new IllegalStateException("Cannot cancel completed order");
        }
        this.status = OrderStatus.CANCELLED;
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public String getCustomerId() { return customerId; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public OrderStatus getStatus() { return status; }
    public List<OrderItem> getItems() { return items; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getCompletedAt() { return completedAt; }
}

public enum OrderStatus {
    PENDING,
    PROCESSING,
    COMPLETED,
    CANCELLED,
    FAILED
}
```

#### Order Item

```java
@Entity
@Table(name = "order_items")
public class OrderItem {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String productId;
    
    @Column(nullable = false)
    private String productName;
    
    @Column(nullable = false)
    private Integer quantity;
    
    @Column(nullable = false)
    private BigDecimal unitPrice;
    
    @Column(nullable = false)
    private BigDecimal totalPrice;
    
    // Constructors
    public OrderItem() {
    }
    
    public OrderItem(String productId, String productName, 
                     Integer quantity, BigDecimal unitPrice) {
        this.productId = productId;
        this.productName = productName;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
        this.totalPrice = unitPrice.multiply(BigDecimal.valueOf(quantity));
    }
    
    // Getters
    public Long getId() { return id; }
    public String getProductId() { return productId; }
    public String getProductName() { return productName; }
    public Integer getQuantity() { return quantity; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public BigDecimal getTotalPrice() { return totalPrice; }
}
```

### Commands and Events

#### Order Commands

```java
public record CreateOrderCommand(
    @TargetAggregateIdentifier String orderId,
    String customerId,
    List<OrderItemDTO> items,
    BigDecimal totalAmount
) {}

public record CancelOrderCommand(
    @TargetAggregateIdentifier String orderId,
    String reason
) {}

public record CompleteOrderCommand(
    @TargetAggregateIdentifier String orderId
) {}
```

#### Order Events

```java
public record OrderCreatedEvent(
    String orderId,
    String customerId,
    List<OrderItemDTO> items,
    BigDecimal totalAmount,
    Instant timestamp
) {}

public record OrderCancelledEvent(
    String orderId,
    String reason,
    Instant timestamp
) {}

public record OrderCompletedEvent(
    String orderId,
    Instant timestamp
) {}
```

#### Payment Commands

```java
public record ProcessPaymentCommand(
    @TargetAggregateIdentifier String paymentId,
    String orderId,
    String customerId,
    BigDecimal amount,
    PaymentMethod paymentMethod
) {}

public record RefundPaymentCommand(
    @TargetAggregateIdentifier String paymentId,
    String orderId,
    BigDecimal amount,
    String reason
) {}
```

#### Payment Events

```java
public record PaymentProcessedEvent(
    String paymentId,
    String orderId,
    String customerId,
    BigDecimal amount,
    Instant timestamp
) {}

public record PaymentFailedEvent(
    String paymentId,
    String orderId,
    String reason,
    Instant timestamp
) {}

public record PaymentRefundedEvent(
    String paymentId,
    String orderId,
    BigDecimal amount,
    Instant timestamp
) {}
```

### Order Saga Implementation

```java
@Saga
public class OrderSaga {
    
    private static final Logger logger = LoggerFactory.getLogger(OrderSaga.class);
    
    @Autowired
    private transient CommandGateway commandGateway;
    
    private String orderId;
    private String paymentId;
    private String shipmentId;
    private boolean compensating = false;
    
    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCreatedEvent event) {
        this.orderId = event.orderId();
        logger.info("Order saga started for orderId: {}", orderId);
        
        // Generate payment ID
        this.paymentId = UUID.randomUUID().toString();
        
        // Send process payment command
        ProcessPaymentCommand command = new ProcessPaymentCommand(
            paymentId,
            event.orderId(),
            event.customerId(),
            event.totalAmount(),
            new PaymentMethod("CREDIT_CARD", Map.of())
        );
        
        commandGateway.send(command, (commandMessage, commandResultMessage) -> {
            if (commandResultMessage.isExceptional()) {
                logger.error("Payment command failed for orderId: {}", orderId);
                // Handle command failure
            }
        });
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentProcessedEvent event) {
        logger.info("Payment processed for orderId: {}", event.orderId());
        
        if (compensating) {
            logger.info("Saga is compensating, skipping inventory reservation");
            return;
        }
        
        // Send reserve inventory command
        ReserveInventoryCommand command = new ReserveInventoryCommand(
            event.orderId(),
            event.orderId() // Assuming items are tracked by orderId
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(InventoryReservedEvent event) {
        logger.info("Inventory reserved for orderId: {}", event.orderId());
        
        if (compensating) {
            logger.info("Saga is compensating, skipping shipment preparation");
            return;
        }
        
        // Generate shipment ID
        this.shipmentId = UUID.randomUUID().toString();
        
        // Send prepare shipment command
        PrepareShipmentCommand command = new PrepareShipmentCommand(
            shipmentId,
            event.orderId(),
            event.orderId() // Assuming shipment details tracked by orderId
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(ShipmentPreparedEvent event) {
        logger.info("Shipment prepared for orderId: {}", event.orderId());
        
        if (compensating) {
            logger.info("Saga is compensating, skipping notification");
            return;
        }
        
        // Send notification command
        SendNotificationCommand command = new SendNotificationCommand(
            event.orderId(),
            "ORDER_CONFIRMED",
            "Your order has been confirmed and is being prepared for shipment."
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(NotificationSentEvent event) {
        logger.info("Notification sent for orderId: {}", event.orderId());
        
        // Complete the order
        CompleteOrderCommand command = new CompleteOrderCommand(event.orderId());
        commandGateway.send(command);
    }
    
    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCompletedEvent event) {
        logger.info("Order saga completed for orderId: {}", event.orderId());
    }
    
    // Compensation handlers
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentFailedEvent event) {
        logger.error("Payment failed for orderId: {}, reason: {}", 
            event.orderId(), event.reason());
        
        compensating = true;
        
        // Cancel the order
        CancelOrderCommand command = new CancelOrderCommand(
            event.orderId(),
            "Payment failed: " + event.reason()
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(InventoryReservationFailedEvent event) {
        logger.error("Inventory reservation failed for orderId: {}, reason: {}", 
            event.orderId(), event.reason());
        
        compensating = true;
        
        // Refund payment
        RefundPaymentCommand refundCommand = new RefundPaymentCommand(
            paymentId,
            event.orderId(),
            event.amount(),
            "Inventory unavailable"
        );
        
        commandGateway.send(refundCommand);
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentRefundedEvent event) {
        logger.info("Payment refunded for orderId: {}", event.orderId());
        
        // Cancel the order
        CancelOrderCommand command = new CancelOrderCommand(
            event.orderId(),
            "Inventory unavailable - payment refunded"
        );
        
        commandGateway.send(command);
    }
    
    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCancelledEvent event) {
        logger.info("Order saga ended with cancellation for orderId: {}", 
            event.orderId());
    }
}
```

### Payment Aggregate

```java
@Aggregate
public class PaymentAggregate {
    
    @AggregateIdentifier
    private String paymentId;
    
    private String orderId;
    private BigDecimal amount;
    private PaymentStatus status;
    
    public PaymentAggregate() {
    }
    
    @CommandHandler
    public PaymentAggregate(ProcessPaymentCommand command) {
        // Validate payment
        if (command.amount().compareTo(BigDecimal.ZERO) <= 0) {
            apply(new PaymentFailedEvent(
                command.paymentId(),
                command.orderId(),
                "Invalid payment amount",
                Instant.now()
            ));
            return;
        }
        
        // Simulate payment gateway call
        boolean paymentSuccessful = processPaymentWithGateway(command);
        
        if (paymentSuccessful) {
            apply(new PaymentProcessedEvent(
                command.paymentId(),
                command.orderId(),
                command.customerId(),
                command.amount(),
                Instant.now()
            ));
        } else {
            apply(new PaymentFailedEvent(
                command.paymentId(),
                command.orderId(),
                "Payment gateway declined",
                Instant.now()
            ));
        }
    }
    
    @EventSourcingHandler
    public void on(PaymentProcessedEvent event) {
        this.paymentId = event.paymentId();
        this.orderId = event.orderId();
        this.amount = event.amount();
        this.status = PaymentStatus.PROCESSED;
    }
    
    @EventSourcingHandler
    public void on(PaymentFailedEvent event) {
        this.paymentId = event.paymentId();
        this.orderId = event.orderId();
        this.status = PaymentStatus.FAILED;
    }
    
    @CommandHandler
    public void handle(RefundPaymentCommand command) {
        if (this.status != PaymentStatus.PROCESSED) {
            throw new IllegalStateException("Can only refund processed payments");
        }
        
        apply(new PaymentRefundedEvent(
            command.paymentId(),
            command.orderId(),
            command.amount(),
            Instant.now()
        ));
    }
    
    @EventSourcingHandler
    public void on(PaymentRefundedEvent event) {
        this.status = PaymentStatus.REFUNDED;
    }
    
    private boolean processPaymentWithGateway(ProcessPaymentCommand command) {
        // Simulate payment gateway integration
        // In real implementation, call actual payment gateway API
        try {
            // Simulate network delay
            Thread.sleep(100);
            
            // 90% success rate for demonstration
            return Math.random() > 0.1;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }
}

enum PaymentStatus {
    PENDING,
    PROCESSED,
    FAILED,
    REFUNDED
}
```

### Inventory Aggregate

```java
@Aggregate
public class InventoryAggregate {
    
    @AggregateIdentifier
    private String inventoryId;
    
    private String orderId;
    private Map<String, Integer> reservedItems = new HashMap<>();
    
    public InventoryAggregate() {
    }
    
    @CommandHandler
    public InventoryAggregate(ReserveInventoryCommand command) {
        // Check inventory availability
        boolean available = checkInventoryAvailability(command.items());
        
        if (available) {
            apply(new InventoryReservedEvent(
                UUID.randomUUID().toString(),
                command.orderId(),
                command.items(),
                Instant.now()
            ));
        } else {
            apply(new InventoryReservationFailedEvent(
                command.orderId(),
                "Insufficient inventory",
                BigDecimal.ZERO, // Would calculate from order
                Instant.now()
            ));
        }
    }
    
    @EventSourcingHandler
    public void on(InventoryReservedEvent event) {
        this.inventoryId = event.inventoryId();
        this.orderId = event.orderId();
        this.reservedItems = event.items();
    }
    
    @CommandHandler
    public void handle(ReleaseInventoryCommand command) {
        apply(new InventoryReleasedEvent(
            this.inventoryId,
            command.orderId(),
            this.reservedItems,
            Instant.now()
        ));
    }
    
    @EventSourcingHandler
    public void on(InventoryReleasedEvent event) {
        this.reservedItems.clear();
    }
    
    private boolean checkInventoryAvailability(Map<String, Integer> items) {
        // In real implementation, check actual inventory database
        // For demonstration, 95% availability
        return Math.random() > 0.05;
    }
}
```

### Order Service Implementation

```java
@Service
public class OrderService {
    
    private final CommandGateway commandGateway;
    private final OrderRepository orderRepository;
    
    public OrderService(CommandGateway commandGateway, 
                       OrderRepository orderRepository) {
        this.commandGateway = commandGateway;
        this.orderRepository = orderRepository;
    }
    
    public String createOrder(CreateOrderRequest request) {
        String orderId = UUID.randomUUID().toString();
        
        // Create order entity
        Order order = new Order(
            orderId,
            request.customerId(),
            request.totalAmount()
        );
        
        // Add order items
        request.items().forEach(item -> {
            order.getItems().add(new OrderItem(
                item.productId(),
                item.productName(),
                item.quantity(),
                item.unitPrice()
            ));
        });
        
        // Save order
        orderRepository.save(order);
        
        // Send create order command to start saga
        CreateOrderCommand command = new CreateOrderCommand(
            orderId,
            request.customerId(),
            request.items(),
            request.totalAmount()
        );
        
        commandGateway.send(command);
        
        return orderId;
    }
    
    public OrderDTO getOrder(String orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        
        return OrderDTO.fromEntity(order);
    }
}
```

### REST Controller

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    private final OrderService orderService;
    
    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }
    
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @Valid @RequestBody CreateOrderRequest request) {
        
        String orderId = orderService.createOrder(request);
        
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(new OrderResponse(orderId, "Order created successfully"));
    }
    
    @GetMapping("/{orderId}")
    public ResponseEntity<OrderDTO> getOrder(@PathVariable String orderId) {
        OrderDTO order = orderService.getOrder(orderId);
        return ResponseEntity.ok(order);
    }
}
```

### Configuration

#### Application Properties

```properties
# Application
spring.application.name=order-service
server.port=8080

# Database
spring.datasource.url=jdbc:postgresql://localhost:5432/orderdb
spring.datasource.username=orderuser
spring.datasource.password=orderpass
spring.jpa.hibernate.ddl-auto=update
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect

# Axon Configuration
axon.axonserver.servers=localhost:8124
axon.serializer.general=jackson
axon.serializer.events=jackson
axon.serializer.messages=jackson

# Actuator
management.endpoints.web.exposure.include=health,metrics,info,prometheus
management.endpoint.health.show-details=always
management.metrics.export.prometheus.enabled=true
```

#### Maven Dependencies

```xml
<dependencies>
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    
    <!-- Axon Framework -->
    <dependency>
        <groupId>org.axonframework</groupId>
        <artifactId>axon-spring-boot-starter</artifactId>
        <version>4.9.0</version>
    </dependency>
    
    <!-- Database -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>
    
    <!-- Monitoring -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-registry-prometheus</artifactId>
    </dependency>
    
    <!-- Testing -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.axonframework</groupId>
        <artifactId>axon-test</artifactId>
        <version>4.9.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

---

## Food Delivery Application

Choreography-based saga example using Spring Cloud Stream and Kafka.

### Architecture

```
Order Service
     ↓ (publishes OrderCreatedEvent)
Restaurant Service
     ↓ (publishes OrderAcceptedEvent / OrderRejectedEvent)
Payment Service
     ↓ (publishes PaymentSuccessEvent / PaymentFailedEvent)
Delivery Service
     ↓ (publishes DeliveryAssignedEvent / DeliveryFailedEvent)
Notification Service
```

### Domain Events

```java
// Order Events
public record OrderCreatedEvent(
    String orderId,
    String customerId,
    String restaurantId,
    List<FoodItem> items,
    BigDecimal totalAmount,
    DeliveryAddress deliveryAddress,
    Instant timestamp
) {}

public record OrderCancelledEvent(
    String orderId,
    String reason,
    Instant timestamp
) {}

// Restaurant Events
public record OrderAcceptedEvent(
    String orderId,
    String restaurantId,
    int estimatedPreparationTime,
    Instant timestamp
) {}

public record OrderRejectedEvent(
    String orderId,
    String restaurantId,
    String reason,
    Instant timestamp
) {}

// Payment Events
public record PaymentSuccessEvent(
    String orderId,
    String paymentId,
    BigDecimal amount,
    Instant timestamp
) {}

public record PaymentFailedEvent(
    String orderId,
    String paymentId,
    String reason,
    Instant timestamp
) {}

// Delivery Events
public record DeliveryAssignedEvent(
    String orderId,
    String deliveryPersonId,
    String deliveryPersonName,
    Instant estimatedDeliveryTime,
    Instant timestamp
) {}

public record DeliveryFailedEvent(
    String orderId,
    String reason,
    Instant timestamp
) {}
```

### Order Service

```java
@Service
public class FoodOrderService {
    
    private final StreamBridge streamBridge;
    private final OrderRepository orderRepository;
    
    public FoodOrderService(StreamBridge streamBridge,
                           OrderRepository orderRepository) {
        this.streamBridge = streamBridge;
        this.orderRepository = orderRepository;
    }
    
    public String createOrder(CreateFoodOrderRequest request) {
        String orderId = UUID.randomUUID().toString();
        
        // Create and save order
        FoodOrder order = new FoodOrder(
            orderId,
            request.customerId(),
            request.restaurantId(),
            request.items(),
            calculateTotal(request.items()),
            request.deliveryAddress()
        );
        
        orderRepository.save(order);
        
        // Publish order created event
        OrderCreatedEvent event = new OrderCreatedEvent(
            orderId,
            request.customerId(),
            request.restaurantId(),
            request.items(),
            order.getTotalAmount(),
            request.deliveryAddress(),
            Instant.now()
        );
        
        streamBridge.send("order-events", event);
        
        return orderId;
    }
    
    @Bean
    public Consumer<OrderRejectedEvent> handleOrderRejected() {
        return event -> {
            FoodOrder order = orderRepository.findById(event.orderId())
                .orElseThrow();
            
            order.cancel("Restaurant rejected: " + event.reason());
            orderRepository.save(order);
            
            // Publish cancellation event
            OrderCancelledEvent cancelEvent = new OrderCancelledEvent(
                event.orderId(),
                event.reason(),
                Instant.now()
            );
            
            streamBridge.send("order-events", cancelEvent);
        };
    }
    
    @Bean
    public Consumer<PaymentFailedEvent> handlePaymentFailed() {
        return event -> {
            FoodOrder order = orderRepository.findById(event.orderId())
                .orElseThrow();
            
            order.cancel("Payment failed: " + event.reason());
            orderRepository.save(order);
            
            // Notify restaurant to cancel preparation
            RestaurantCancelOrderEvent cancelEvent = 
                new RestaurantCancelOrderEvent(
                    event.orderId(),
                    "Payment failed",
                    Instant.now()
                );
            
            streamBridge.send("restaurant-events", cancelEvent);
        };
    }
    
    private BigDecimal calculateTotal(List<FoodItem> items) {
        return items.stream()
            .map(item -> item.price().multiply(BigDecimal.valueOf(item.quantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
```

### Restaurant Service

```java
@Service
public class RestaurantService {
    
    private final StreamBridge streamBridge;
    private final RestaurantRepository restaurantRepository;
    
    public RestaurantService(StreamBridge streamBridge,
                            RestaurantRepository restaurantRepository) {
        this.streamBridge = streamBridge;
        this.restaurantRepository = restaurantRepository;
    }
    
    @Bean
    public Consumer<OrderCreatedEvent> handleOrderCreated() {
        return event -> {
            Restaurant restaurant = restaurantRepository
                .findById(event.restaurantId())
                .orElseThrow();
            
            // Check if restaurant can accept order
            if (restaurant.canAcceptOrder(event.items())) {
                // Accept order
                int preparationTime = restaurant.estimatePreparationTime(event.items());
                
                OrderAcceptedEvent acceptedEvent = new OrderAcceptedEvent(
                    event.orderId(),
                    event.restaurantId(),
                    preparationTime,
                    Instant.now()
                );
                
                streamBridge.send("restaurant-events", acceptedEvent);
                
                // Start preparing order
                restaurant.startPreparingOrder(event.orderId(), event.items());
                restaurantRepository.save(restaurant);
                
            } else {
                // Reject order
                OrderRejectedEvent rejectedEvent = new OrderRejectedEvent(
                    event.orderId(),
                    event.restaurantId(),
                    "Items unavailable or restaurant closed",
                    Instant.now()
                );
                
                streamBridge.send("restaurant-events", rejectedEvent);
            }
        };
    }
    
    @Bean
    public Consumer<RestaurantCancelOrderEvent> handleCancelOrder() {
        return event -> {
            Restaurant restaurant = restaurantRepository
                .findByOrderId(event.orderId())
                .orElse(null);
            
            if (restaurant != null) {
                restaurant.cancelOrderPreparation(event.orderId());
                restaurantRepository.save(restaurant);
            }
        };
    }
}
```

### Payment Service

```java
@Service
public class FoodPaymentService {
    
    private final StreamBridge streamBridge;
    private final PaymentGateway paymentGateway;
    
    public FoodPaymentService(StreamBridge streamBridge,
                             PaymentGateway paymentGateway) {
        this.streamBridge = streamBridge;
        this.paymentGateway = paymentGateway;
    }
    
    @Bean
    public Consumer<OrderAcceptedEvent> handleOrderAccepted() {
        return event -> {
            String paymentId = UUID.randomUUID().toString();
            
            try {
                // Process payment
                PaymentResult result = paymentGateway.processPayment(
                    paymentId,
                    event.orderId(),
                    getOrderAmount(event.orderId())
                );
                
                if (result.isSuccess()) {
                    PaymentSuccessEvent successEvent = new PaymentSuccessEvent(
                        event.orderId(),
                        paymentId,
                        result.amount(),
                        Instant.now()
                    );
                    
                    streamBridge.send("payment-events", successEvent);
                } else {
                    PaymentFailedEvent failedEvent = new PaymentFailedEvent(
                        event.orderId(),
                        paymentId,
                        result.errorMessage(),
                        Instant.now()
                    );
                    
                    streamBridge.send("payment-events", failedEvent);
                }
            } catch (Exception e) {
                PaymentFailedEvent failedEvent = new PaymentFailedEvent(
                    event.orderId(),
                    paymentId,
                    "Payment processing error: " + e.getMessage(),
                    Instant.now()
                );
                
                streamBridge.send("payment-events", failedEvent);
            }
        };
    }
    
    private BigDecimal getOrderAmount(String orderId) {
        // Fetch order amount from order service or database
        return BigDecimal.valueOf(50.00); // Placeholder
    }
}
```

### Delivery Service

```java
@Service
public class DeliveryService {
    
    private final StreamBridge streamBridge;
    private final DeliveryPersonRepository deliveryPersonRepository;
    
    public DeliveryService(StreamBridge streamBridge,
                          DeliveryPersonRepository deliveryPersonRepository) {
        this.streamBridge = streamBridge;
        this.deliveryPersonRepository = deliveryPersonRepository;
    }
    
    @Bean
    public Consumer<PaymentSuccessEvent> handlePaymentSuccess() {
        return event -> {
            // Find available delivery person
            DeliveryPerson deliveryPerson = 
                deliveryPersonRepository.findAvailableNearby()
                    .orElse(null);
            
            if (deliveryPerson != null) {
                // Assign delivery
                deliveryPerson.assignOrder(event.orderId());
                deliveryPersonRepository.save(deliveryPerson);
                
                Instant estimatedDelivery = Instant.now()
                    .plus(30, ChronoUnit.MINUTES);
                
                DeliveryAssignedEvent assignedEvent = new DeliveryAssignedEvent(
                    event.orderId(),
                    deliveryPerson.getId(),
                    deliveryPerson.getName(),
                    estimatedDelivery,
                    Instant.now()
                );
                
                streamBridge.send("delivery-events", assignedEvent);
            } else {
                // No delivery person available
                DeliveryFailedEvent failedEvent = new DeliveryFailedEvent(
                    event.orderId(),
                    "No delivery person available",
                    Instant.now()
                );
                
                streamBridge.send("delivery-events", failedEvent);
            }
        };
    }
}
```

### Notification Service

```java
@Service
public class NotificationService {
    
    private final EmailService emailService;
    private final SmsService smsService;
    
    public NotificationService(EmailService emailService, 
                              SmsService smsService) {
        this.emailService = emailService;
        this.smsService = smsService;
    }
    
    @Bean
    public Consumer<OrderAcceptedEvent> handleOrderAccepted() {
        return event -> {
            String message = String.format(
                "Your order #%s has been accepted by the restaurant. " +
                "Estimated preparation time: %d minutes",
                event.orderId(),
                event.estimatedPreparationTime()
            );
            
            sendNotification(event.orderId(), message);
        };
    }
    
    @Bean
    public Consumer<PaymentSuccessEvent> handlePaymentSuccess() {
        return event -> {
            String message = String.format(
                "Payment of $%.2f for order #%s processed successfully",
                event.amount(),
                event.orderId()
            );
            
            sendNotification(event.orderId(), message);
        };
    }
    
    @Bean
    public Consumer<DeliveryAssignedEvent> handleDeliveryAssigned() {
        return event -> {
            String message = String.format(
                "Your order #%s has been assigned to delivery person %s. " +
                "Estimated delivery: %s",
                event.orderId(),
                event.deliveryPersonName(),
                event.estimatedDeliveryTime()
            );
            
            sendNotification(event.orderId(), message);
        };
    }
    
    @Bean
    public Consumer<OrderCancelledEvent> handleOrderCancelled() {
        return event -> {
            String message = String.format(
                "Your order #%s has been cancelled. Reason: %s",
                event.orderId(),
                event.reason()
            );
            
            sendNotification(event.orderId(), message);
        };
    }
    
    private void sendNotification(String orderId, String message) {
        // Get customer contact info from order
        // Send email and SMS
        emailService.sendEmail(orderId, message);
        smsService.sendSms(orderId, message);
    }
}
```

### Spring Cloud Stream Configuration

```yaml
spring:
  cloud:
    stream:
      bindings:
        # Order Service
        order-events:
          destination: food-order-events
          contentType: application/json
        
        # Restaurant Service
        restaurant-events:
          destination: food-restaurant-events
          contentType: application/json
        
        # Payment Service
        payment-events:
          destination: food-payment-events
          contentType: application/json
        
        # Delivery Service
        delivery-events:
          destination: food-delivery-events
          contentType: application/json
      
      kafka:
        binder:
          brokers: localhost:9092
          auto-create-topics: true
        
        bindings:
          order-events:
            producer:
              configuration:
                acks: all
                retries: 3
          
          restaurant-events:
            consumer:
              configuration:
                max-poll-records: 10
```

---

## Travel Booking System

Complex orchestration example with multiple compensations.

### Architecture

```
Flight Booking → Hotel Booking → Car Rental → Payment → Confirmation
     ↓                ↓              ↓           ↓            ↓
Cancel Flight   Cancel Hotel   Cancel Car   Refund      Cancel All
```

### Travel Saga

```java
@Saga
public class TravelBookingSaga {
    
    @Autowired
    private transient CommandGateway commandGateway;
    
    private String bookingId;
    private String flightReservationId;
    private String hotelReservationId;
    private String carRentalReservationId;
    private String paymentId;
    private boolean compensating = false;
    
    @StartSaga
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(TravelBookingStartedEvent event) {
        this.bookingId = event.bookingId();
        
        // Step 1: Book flight
        this.flightReservationId = UUID.randomUUID().toString();
        
        BookFlightCommand command = new BookFlightCommand(
            flightReservationId,
            event.bookingId(),
            event.flightDetails()
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(FlightBookedEvent event) {
        if (compensating) return;
        
        // Step 2: Book hotel
        this.hotelReservationId = UUID.randomUUID().toString();
        
        BookHotelCommand command = new BookHotelCommand(
            hotelReservationId,
            event.bookingId(),
            event.hotelDetails()
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(HotelBookedEvent event) {
        if (compensating) return;
        
        // Step 3: Rent car
        this.carRentalReservationId = UUID.randomUUID().toString();
        
        RentCarCommand command = new RentCarCommand(
            carRentalReservationId,
            event.bookingId(),
            event.carRentalDetails()
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(CarRentedEvent event) {
        if (compensating) return;
        
        // Step 4: Process payment
        this.paymentId = UUID.randomUUID().toString();
        
        ProcessTravelPaymentCommand command = new ProcessTravelPaymentCommand(
            paymentId,
            event.bookingId(),
            calculateTotalAmount()
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(TravelPaymentProcessedEvent event) {
        if (compensating) return;
        
        // Step 5: Confirm booking
        ConfirmTravelBookingCommand command = new ConfirmTravelBookingCommand(
            event.bookingId()
        );
        
        commandGateway.send(command);
    }
    
    @EndSaga
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(TravelBookingConfirmedEvent event) {
        // Saga completed successfully
    }
    
    // Compensation handlers
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(FlightBookingFailedEvent event) {
        compensating = true;
        
        CancelTravelBookingCommand command = new CancelTravelBookingCommand(
            event.bookingId(),
            "Flight booking failed: " + event.reason()
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(HotelBookingFailedEvent event) {
        compensating = true;
        
        // Cancel flight
        CancelFlightCommand cancelFlight = new CancelFlightCommand(
            flightReservationId,
            event.bookingId()
        );
        
        commandGateway.send(cancelFlight);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(FlightCancelledEvent event) {
        if (!compensating) return;
        
        // After flight cancelled, cancel entire booking
        CancelTravelBookingCommand command = new CancelTravelBookingCommand(
            event.bookingId(),
            "Hotel booking failed - flight cancelled"
        );
        
        commandGateway.send(command);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(CarRentalFailedEvent event) {
        compensating = true;
        
        // Cancel hotel
        CancelHotelCommand cancelHotel = new CancelHotelCommand(
            hotelReservationId,
            event.bookingId()
        );
        
        commandGateway.send(cancelHotel);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(HotelCancelledEvent event) {
        if (!compensating) return;
        
        // Cancel flight
        CancelFlightCommand cancelFlight = new CancelFlightCommand(
            flightReservationId,
            event.bookingId()
        );
        
        commandGateway.send(cancelFlight);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(TravelPaymentFailedEvent event) {
        compensating = true;
        
        // Cancel car rental
        CancelCarRentalCommand cancelCar = new CancelCarRentalCommand(
            carRentalReservationId,
            event.bookingId()
        );
        
        commandGateway.send(cancelCar);
    }
    
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(CarRentalCancelledEvent event) {
        if (!compensating) return;
        
        // Cancel hotel
        CancelHotelCommand cancelHotel = new CancelHotelCommand(
            hotelReservationId,
            event.bookingId()
        );
        
        commandGateway.send(cancelHotel);
    }
    
    @EndSaga
    @SagaEventHandler(associationProperty = "bookingId")
    public void handle(TravelBookingCancelledEvent event) {
        // Saga ended with cancellation
    }
    
    private BigDecimal calculateTotalAmount() {
        // Calculate total from all bookings
        return BigDecimal.valueOf(1500.00); // Placeholder
    }
}
```

This examples file demonstrates practical implementations of the Saga Pattern in various scenarios. Each example shows:

1. Complete domain models
2. Commands and events
3. Saga coordination logic
4. Compensation transactions
5. Service implementations
6. Configuration and dependencies

The examples progress from simple to complex, showing both choreography and orchestration approaches with realistic business scenarios.
