# Resilience4j Real-World Examples

## E-Commerce Order Service

Complete example demonstrating all Resilience4j patterns in a microservices environment.

### Project Structure

```
order-service/
├── src/main/java/com/ecommerce/order/
│   ├── config/
│   │   ├── ResilienceConfig.java
│   │   └── RestTemplateConfig.java
│   ├── controller/
│   │   ├── OrderController.java
│   │   └── GlobalExceptionHandler.java
│   ├── service/
│   │   ├── OrderService.java
│   │   ├── PaymentService.java
│   │   ├── InventoryService.java
│   │   └── NotificationService.java
│   ├── domain/
│   │   ├── Order.java
│   │   ├── OrderStatus.java
│   │   └── Payment.java
└── src/main/resources/
    └── application.yml
```

### Configuration

```yaml
server:
  port: 8080

spring:
  application:
    name: order-service

resilience4j:
  circuitbreaker:
    configs:
      default:
        registerHealthIndicator: true
        slidingWindowSize: 10
        minimumNumberOfCalls: 5
        failureRateThreshold: 50
        waitDurationInOpenState: 30s
    instances:
      paymentService:
        baseConfig: default
        waitDurationInOpenState: 60s
      inventoryService:
        baseConfig: default

  retry:
    configs:
      default:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
    instances:
      paymentService:
        maxAttempts: 5
        waitDuration: 1s

  ratelimiter:
    configs:
      default:
        limitForPeriod: 100
        limitRefreshPeriod: 1s
    instances:
      emailService:
        limitForPeriod: 10
        limitRefreshPeriod: 1m

  bulkhead:
    configs:
      default:
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms
    instances:
      orderProcessing:
        maxConcurrentCalls: 5

  timelimiter:
    configs:
      default:
        timeoutDuration: 3s
    instances:
      paymentService:
        timeoutDuration: 5s

management:
  endpoints:
    web:
      exposure:
        include: '*'
  endpoint:
    health:
      show-details: always
  health:
    circuitbreakers:
      enabled: true
    ratelimiters:
      enabled: true
```

### Order Service Implementation

```java
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderService {

    private final PaymentService paymentService;
    private final InventoryService inventoryService;
    private final NotificationService notificationService;

    @Bulkhead(name = "orderProcessing", type = Bulkhead.Type.SEMAPHORE)
    @Transactional
    public Order processOrder(OrderRequest request) {
        log.info("Processing order for customer: {}", request.getCustomerId());

        Order order = createOrder(request);

        try {
            // Reserve inventory
            inventoryService.reserveInventory(order);

            // Process payment
            String paymentId = paymentService.processPayment(order).get();
            order = order.toBuilder().paymentId(paymentId).build();

            // Send confirmation (async, best effort)
            notificationService.sendOrderConfirmation(order);

            log.info("Order processed successfully: {}", order.getId());
            return order;

        } catch (Exception ex) {
            log.error("Order processing failed", ex);
            compensateFailedOrder(order);
            throw new OrderProcessingException("Failed to process order", ex);
        }
    }

    private void compensateFailedOrder(Order order) {
        try {
            inventoryService.releaseInventory(order);
            if (order.getPaymentId() != null) {
                paymentService.refundPayment(order.getPaymentId());
            }
        } catch (Exception ex) {
            log.error("Compensation failed", ex);
        }
    }
}
```

### Payment Service with Multiple Patterns

```java
@Slf4j
@Service
@RequiredArgsConstructor
public class PaymentService {

    private final PaymentClient paymentClient;

    @CircuitBreaker(name = "paymentService", fallbackMethod = "processPaymentFallback")
    @Retry(name = "paymentService")
    @TimeLimiter(name = "paymentService")
    public CompletableFuture<String> processPayment(Order order) {
        return CompletableFuture.supplyAsync(() -> {
            Payment payment = Payment.builder()
                .orderId(order.getId())
                .amount(order.getTotalAmount())
                .build();

            PaymentResponse response = paymentClient.processPayment(payment);

            if (!response.isSuccess()) {
                throw new PaymentFailedException(response.getErrorMessage());
            }

            return response.getPaymentId();
        });
    }

    private CompletableFuture<String> processPaymentFallback(
            Order order, Exception ex) {
        log.error("Payment processing failed for order: {}", order.getId(), ex);
        throw new PaymentServiceUnavailableException(
            "Payment service unavailable", ex);
    }

    @CircuitBreaker(name = "paymentService")
    @Retry(name = "paymentService")
    public void refundPayment(String paymentId) {
        paymentClient.refundPayment(paymentId);
    }
}
```

### Exception Handler

```java
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(CallNotPermittedException.class)
    @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
    public ErrorResponse handleCircuitOpen(CallNotPermittedException ex) {
        log.error("Circuit breaker is open", ex);
        return ErrorResponse.builder()
            .code("SERVICE_UNAVAILABLE")
            .message("Service is temporarily unavailable")
            .status(HttpStatus.SERVICE_UNAVAILABLE.value())
            .build();
    }

    @ExceptionHandler(RequestNotPermitted.class)
    @ResponseStatus(HttpStatus.TOO_MANY_REQUESTS)
    public ErrorResponse handleRateLimited(RequestNotPermitted ex) {
        return ErrorResponse.builder()
            .code("TOO_MANY_REQUESTS")
            .message("Rate limit exceeded")
            .status(HttpStatus.TOO_MANY_REQUESTS.value())
            .build();
    }

    @ExceptionHandler(BulkheadFullException.class)
    @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
    public ErrorResponse handleBulkheadFull(BulkheadFullException ex) {
        return ErrorResponse.builder()
            .code("SERVICE_BUSY")
            .message("Service at capacity")
            .status(HttpStatus.SERVICE_UNAVAILABLE.value())
            .build();
    }

    @ExceptionHandler(TimeoutException.class)
    @ResponseStatus(HttpStatus.REQUEST_TIMEOUT)
    public ErrorResponse handleTimeout(TimeoutException ex) {
        return ErrorResponse.builder()
            .code("REQUEST_TIMEOUT")
            .message("Request timed out")
            .status(HttpStatus.REQUEST_TIMEOUT.value())
            .build();
    }
}
```

## Testing Patterns

### Unit Test for Circuit Breaker

```java
@SpringBootTest
class PaymentServiceCircuitBreakerTest {

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private CircuitBreakerRegistry circuitBreakerRegistry;

    @MockBean
    private PaymentClient paymentClient;

    private CircuitBreaker circuitBreaker;

    @BeforeEach
    void setup() {
        circuitBreaker = circuitBreakerRegistry.circuitBreaker("paymentService");
        circuitBreaker.reset();
    }

    @Test
    void shouldOpenCircuitAfterFailures() {
        Order order = createTestOrder();
        when(paymentClient.processPayment(any()))
            .thenThrow(new RuntimeException("Service error"));

        // Trigger failures to exceed threshold
        for (int i = 0; i < 5; i++) {
            try {
                paymentService.processPayment(order).get();
            } catch (Exception ignored) {}
        }

        assertThat(circuitBreaker.getState())
            .isEqualTo(CircuitBreaker.State.OPEN);

        // Next call should fail immediately
        assertThatThrownBy(() -> paymentService.processPayment(order).get())
            .hasRootCauseInstanceOf(PaymentServiceUnavailableException.class);
    }
}
```

### Integration Test with WireMock

```java
@SpringBootTest
@AutoConfigureWireMock(port = 0)
class OrderServiceIntegrationTest {

    @Autowired
    private OrderService orderService;

    @Test
    void shouldRetryOnTransientFailure() {
        // First two calls fail, third succeeds
        stubFor(post("/payment/process")
            .inScenario("Retry")
            .whenScenarioStateIs(STARTED)
            .willReturn(serverError())
            .willSetStateTo("First Retry"));

        stubFor(post("/payment/process")
            .inScenario("Retry")
            .whenScenarioStateIs("First Retry")
            .willReturn(serverError())
            .willSetStateTo("Second Retry"));

        stubFor(post("/payment/process")
            .inScenario("Retry")
            .whenScenarioStateIs("Second Retry")
            .willReturn(ok().withBody("{\"paymentId\":\"PAY-123\"}")));

        Order order = orderService.processOrder(createOrderRequest());

        assertThat(order.getPaymentId()).isEqualTo("PAY-123");
        verify(exactly(3), postRequestedFor(urlEqualTo("/payment/process")));
    }
}
```

## Advanced Scenarios

### Reactive WebFlux Example

```java
@Service
@RequiredArgsConstructor
public class ReactiveProductService {

    private final WebClient webClient;
    private final CircuitBreaker circuitBreaker;
    private final Retry retry;

    public Mono<Product> getProduct(String productId) {
        return webClient.get()
            .uri("/products/{id}", productId)
            .retrieve()
            .bodyToMono(Product.class)
            .transformDeferred(CircuitBreakerOperator.of(circuitBreaker))
            .transformDeferred(RetryOperator.of(retry))
            .onErrorResume(throwable ->
                Mono.just(Product.unavailable(productId))
            );
    }
}
```

### Custom Resilience Configuration

```java
@Configuration
@Slf4j
public class ResilienceConfig {

    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .waitDurationInOpenState(Duration.ofSeconds(30))
            .slowCallDurationThreshold(Duration.ofSeconds(2))
            .permittedNumberOfCallsInHalfOpenState(3)
            .minimumNumberOfCalls(5)
            .slidingWindowSize(10)
            .build();

        CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);

        // Register event consumer
        registry.getEventPublisher()
            .onEntryAdded(event ->
                log.info("CircuitBreaker added: {}",
                    event.getAddedEntry().getName())
            );

        return registry;
    }

    @Bean
    public RegistryEventConsumer<CircuitBreaker> circuitBreakerEventConsumer() {
        return new RegistryEventConsumer<>() {
            @Override
            public void onEntryAddedEvent(EntryAddedEvent<CircuitBreaker> event) {
                CircuitBreaker cb = event.getAddedEntry();
                cb.getEventPublisher()
                    .onStateTransition(e ->
                        log.warn("CircuitBreaker {} state changed: {} -> {}",
                            cb.getName(),
                            e.getStateTransition().getFromState(),
                            e.getStateTransition().getToState())
                    )
                    .onError(e ->
                        log.error("CircuitBreaker {} error: {}",
                            cb.getName(),
                            e.getThrowable().getMessage())
                    );
            }

            @Override
            public void onEntryRemovedEvent(EntryRemovedEvent<CircuitBreaker> event) {
                log.info("CircuitBreaker removed: {}",
                    event.getRemovedEntry().getName());
            }

            @Override
            public void onEntryReplacedEvent(EntryReplacedEvent<CircuitBreaker> event) {
                log.info("CircuitBreaker replaced: {}",
                    event.getNewEntry().getName());
            }
        };
    }
}
```

### Monitoring and Metrics

```java
@RestController
@RequestMapping("/api/monitoring")
@RequiredArgsConstructor
public class ResilienceMonitoringController {

    private final CircuitBreakerRegistry circuitBreakerRegistry;

    @GetMapping("/circuit-breakers")
    public List<CircuitBreakerStatus> getStatus() {
        return circuitBreakerRegistry.getAllCircuitBreakers().stream()
            .map(this::toStatus)
            .collect(Collectors.toList());
    }

    private CircuitBreakerStatus toStatus(CircuitBreaker cb) {
        CircuitBreaker.Metrics metrics = cb.getMetrics();

        return CircuitBreakerStatus.builder()
            .name(cb.getName())
            .state(cb.getState().name())
            .failureRate(metrics.getFailureRate())
            .slowCallRate(metrics.getSlowCallRate())
            .numberOfBufferedCalls(metrics.getNumberOfBufferedCalls())
            .numberOfFailedCalls(metrics.getNumberOfFailedCalls())
            .numberOfSuccessfulCalls(metrics.getNumberOfSuccessfulCalls())
            .build();
    }
}

@Value
@Builder
class CircuitBreakerStatus {
    String name;
    String state;
    float failureRate;
    float slowCallRate;
    int numberOfBufferedCalls;
    int numberOfFailedCalls;
    int numberOfSuccessfulCalls;
}
```

See testing-patterns.md for comprehensive testing strategies and configuration-reference.md for complete configuration options.
