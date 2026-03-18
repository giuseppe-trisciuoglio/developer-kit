# Testing Strategies for Sagas

## Unit Testing Saga Logic

Test saga behavior with Axon test fixtures:

```java
@Test
void shouldDispatchPaymentCommandWhenOrderCreated() {
    // Arrange
    String orderId = UUID.randomUUID().toString();
    String paymentId = UUID.randomUUID().toString();

    SagaTestFixture<OrderSaga> fixture = new SagaTestFixture<>(OrderSaga.class);

    // Act & Assert
    fixture
        .givenNoPriorActivity()
        .whenPublishingA(new OrderCreatedEvent(orderId, BigDecimal.TEN, "item-1"))
        .expectDispatchedCommands(new ProcessPaymentCommand(paymentId, orderId, BigDecimal.TEN));
}

@Test
void shouldCompensateWhenPaymentFails() {
    String orderId = UUID.randomUUID().toString();
    String paymentId = UUID.randomUUID().toString();

    SagaTestFixture<OrderSaga> fixture = new SagaTestFixture<>(OrderSaga.class);

    fixture
        .givenNoPriorActivity()
        .whenPublishingA(new OrderCreatedEvent(orderId, BigDecimal.TEN, "item-1"))
        .whenPublishingA(new PaymentFailedEvent(paymentId, orderId, "item-1", "Insufficient funds"))
        .expectDispatchedCommands(new CancelOrderCommand(orderId))
        .expectScheduledEventOfType(OrderSaga.class, null);
}
```

## Testing Event Publishing

Verify events are published correctly:

```java
@SpringBootTest
@WebMvcTest
class OrderServiceTest {

    @MockBean
    private EventPublisher eventPublisher;

    @InjectMocks
    private OrderService orderService;

    @Test
    void shouldPublishOrderCreatedEvent() {
        // Arrange
        CreateOrderRequest request = new CreateOrderRequest("cust-1", BigDecimal.TEN);

        // Act
        String orderId = orderService.createOrder(request);

        // Assert
        verify(eventPublisher).publish(
            argThat(event -> event instanceof OrderCreatedEvent &&
                    ((OrderCreatedEvent) event).orderId().equals(orderId))
        );
    }
}
```

## Integration Testing with Testcontainers

Test complete saga flow with real services:

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
    void shouldCompleteOrderSagaSuccessfully(@Autowired OrderService orderService,
                                             @Autowired OrderRepository orderRepository,
                                             @Autowired EventPublisher eventPublisher) {
        // Arrange
        CreateOrderRequest request = new CreateOrderRequest("cust-1", BigDecimal.TEN);

        // Act
        String orderId = orderService.createOrder(request);

        // Wait for async processing
        Thread.sleep(2000);

        // Assert
        Order order = orderRepository.findById(orderId).orElseThrow();
        assertThat(order.getStatus()).isEqualTo(OrderStatus.COMPLETED);
    }
}
```

## Testing Idempotency

Verify operations produce same results on retry:

```java
@Test
void compensationShouldBeIdempotent() {
    // Arrange
    String paymentId = "payment-123";
    Payment payment = new Payment(paymentId, "order-1", BigDecimal.TEN);
    paymentRepository.save(payment);

    // Act - First compensation
    paymentService.cancelPayment(paymentId);
    Payment firstResult = paymentRepository.findById(paymentId).orElseThrow();

    // Act - Second compensation (should be idempotent)
    paymentService.cancelPayment(paymentId);
    Payment secondResult = paymentRepository.findById(paymentId).orElseThrow();

    // Assert
    assertThat(firstResult).isEqualTo(secondResult);
    assertThat(secondResult.getStatus()).isEqualTo(PaymentStatus.CANCELLED);
    assertThat(secondResult.getVersion()).isEqualTo(firstResult.getVersion());
}
```

## Testing Concurrent Sagas

Verify saga isolation under concurrent execution:

```java
@Test
void shouldHandleConcurrentSagaExecutions() throws InterruptedException {
    // Arrange
    int numThreads = 10;
    ExecutorService executor = Executors.newFixedThreadPool(numThreads);
    CountDownLatch latch = new CountDownLatch(numThreads);

    // Act
    for (int i = 0; i < numThreads; i++) {
        final int index = i;
        executor.submit(() -> {
            try {
                CreateOrderRequest request = new CreateOrderRequest(
                    "cust-" + index,
                    BigDecimal.TEN.multiply(BigDecimal.valueOf(index))
                );
                orderService.createOrder(request);
            } finally {
                latch.countDown();
            }
        });
    }

    latch.await(10, TimeUnit.SECONDS);

    // Assert
    long createdOrders = orderRepository.count();
    assertThat(createdOrders).isEqualTo(numThreads);
}
```

## Testing Failure Scenarios

Test each failure path and compensation:

```java
@Test
void shouldCompensateWhenInventoryUnavailable() {
    // Arrange
    String orderId = UUID.randomUUID().toString();
    inventoryService.setAvailability("item-1", 0); // No inventory

    // Act
    String result = orderService.createOrder(
        new CreateOrderRequest("cust-1", BigDecimal.TEN)
    );

    // Wait for saga completion
    Thread.sleep(2000);

    // Assert
    Order order = orderRepository.findById(orderId).orElseThrow();
    assertThat(order.getStatus()).isEqualTo(OrderStatus.CANCELLED);

    // Verify payment was refunded
    Payment payment = paymentRepository.findByOrderId(orderId).orElseThrow();
    assertThat(payment.getStatus()).isEqualTo(PaymentStatus.REFUNDED);
}

@Test
void shouldHandlePaymentGatewayFailure() {
    // Arrange
    paymentGateway.setFailureRate(1.0); // 100% failure

    // Act
    String orderId = orderService.createOrder(
        new CreateOrderRequest("cust-1", BigDecimal.TEN)
    );

    // Wait for saga completion
    Thread.sleep(2000);

    // Assert
    Order order = orderRepository.findById(orderId).orElseThrow();
    assertThat(order.getStatus()).isEqualTo(OrderStatus.CANCELLED);
}
```

## Testing State Machine

Verify state transitions:

```java
@Test
void shouldTransitionStatesProperly() {
    // Arrange
    String sagaId = UUID.randomUUID().toString();
    SagaState sagaState = new SagaState(sagaId, SagaStatus.STARTED);
    sagaStateRepository.save(sagaState);

    // Act & Assert
    assertThat(sagaState.getStatus()).isEqualTo(SagaStatus.STARTED);

    sagaState.setStatus(SagaStatus.PROCESSING);
    sagaStateRepository.save(sagaState);
    assertThat(sagaStateRepository.findById(sagaId).get().getStatus())
        .isEqualTo(SagaStatus.PROCESSING);

    sagaState.setStatus(SagaStatus.COMPLETED);
    sagaStateRepository.save(sagaState);
    assertThat(sagaStateRepository.findById(sagaId).get().getStatus())
        .isEqualTo(SagaStatus.COMPLETED);
}
```

## Test Data Builders

Use builders for cleaner test code:

```java
public class OrderRequestBuilder {

    private String customerId = "cust-default";
    private BigDecimal totalAmount = BigDecimal.TEN;
    private List<OrderItem> items = new ArrayList<>();

    public OrderRequestBuilder withCustomerId(String customerId) {
        this.customerId = customerId;
        return this;
    }

    public OrderRequestBuilder withAmount(BigDecimal amount) {
        this.totalAmount = amount;
        return this;
    }

    public OrderRequestBuilder withItem(String productId, int quantity) {
        items.add(new OrderItem(productId, "Product", quantity, BigDecimal.TEN));
        return this;
    }

    public CreateOrderRequest build() {
        return new CreateOrderRequest(customerId, totalAmount, items);
    }
}

@Test
void shouldCreateOrderWithCustomization() {
    CreateOrderRequest request = new OrderRequestBuilder()
        .withCustomerId("customer-123")
        .withAmount(BigDecimal.valueOf(50))
        .withItem("product-1", 2)
        .withItem("product-2", 1)
        .build();

    String orderId = orderService.createOrder(request);
    assertThat(orderId).isNotNull();
}
```

## Performance Testing

Measure saga execution time:

```java
@Test
void shouldCompleteOrderSagaWithinTimeLimit() {
    // Arrange
    CreateOrderRequest request = new CreateOrderRequest("cust-1", BigDecimal.TEN);
    long maxDurationMs = 5000; // 5 seconds

    // Act
    Instant start = Instant.now();
    String orderId = orderService.createOrder(request);
    Instant end = Instant.now();

    // Assert
    long duration = Duration.between(start, end).toMillis();
    assertThat(duration).isLessThan(maxDurationMs);
}
```
