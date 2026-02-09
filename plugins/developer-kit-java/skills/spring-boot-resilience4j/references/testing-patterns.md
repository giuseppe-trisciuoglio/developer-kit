# Resilience4j Testing Patterns

## Circuit Breaker Testing

### Testing State Transitions

```java
@SpringBootTest
class CircuitBreakerStateTest {

    @Autowired
    private PaymentService paymentService;

    @MockBean
    private RestTemplate restTemplate;

    @Test
    void shouldTransitionToOpenAfterFailures() {
        // Simulate repeated failures
        when(restTemplate.postForObject(anyString(), any(), eq(PaymentResponse.class)))
            .thenThrow(new HttpServerErrorException(HttpStatus.INTERNAL_SERVER_ERROR));

        // Trigger failures to exceed threshold
        for (int i = 0; i < 5; i++) {
            assertThatThrownBy(() -> paymentService.processPayment(new PaymentRequest()))
                .isInstanceOf(HttpServerErrorException.class);
        }

        // Circuit should be open - fallback executes
        PaymentResponse response = paymentService.processPayment(new PaymentRequest());
        assertThat(response.getStatus()).isEqualTo("PENDING");
    }

    @Test
    void shouldExecuteFallbackWhenCircuitOpen() {
        when(restTemplate.postForObject(anyString(), any(), eq(PaymentResponse.class)))
            .thenThrow(new RuntimeException("Service unavailable"));

        // Force failures to open circuit
        for (int i = 0; i < 5; i++) {
            try {
                paymentService.processPayment(new PaymentRequest());
            } catch (Exception ignored) {}
        }

        // Circuit is open, fallback provides response
        PaymentResponse response = paymentService.processPayment(new PaymentRequest());
        assertThat(response.getStatus()).isEqualTo("PENDING");
        assertThat(response.getMessage()).contains("temporarily unavailable");
    }
}
```

### Testing Circuit States Directly

```java
@SpringBootTest
class CircuitBreakerDirectStateTest {

    @Autowired
    private CircuitBreakerRegistry circuitBreakerRegistry;

    @Test
    void shouldManuallyOpenAndCloseCircuit() {
        CircuitBreaker circuitBreaker = circuitBreakerRegistry.circuitBreaker("paymentService");

        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.CLOSED);

        // Manually open circuit
        circuitBreaker.transitionToOpenState();
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.OPEN);

        // Manually close circuit
        circuitBreaker.transitionToClosedState();
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.CLOSED);
    }
}
```

## Retry Testing

### Testing Retry Attempts

```java
@SpringBootTest
@AutoConfigureWireMock(port = 0)
class RetryTest {

    @Autowired
    private OrderService orderService;

    @Test
    void shouldRetryOnTransientFailure() {
        // Setup: First two calls fail, third succeeds
        stubFor(post("/orders")
            .inScenario("Retry Scenario")
            .whenScenarioStateIs(STARTED)
            .willReturn(serverError())
            .willSetStateTo("First Failure"));

        stubFor(post("/orders")
            .inScenario("Retry Scenario")
            .whenScenarioStateIs("First Failure")
            .willReturn(serverError())
            .willSetStateTo("Second Failure"));

        stubFor(post("/orders")
            .inScenario("Retry Scenario")
            .whenScenarioStateIs("Second Failure")
            .willReturn(ok().withBody("""
                {"id":1,"status":"CREATED"}
                """)));

        Order order = orderService.createOrder(new OrderRequest());

        assertThat(order.getId()).isEqualTo(1L);
        assertThat(order.getStatus()).isEqualTo("CREATED");

        // Verify exactly 3 calls were made
        verify(exactly(3), postRequestedFor(urlEqualTo("/orders")));
    }

    @Test
    void shouldThrowExceptionAfterMaxRetries() {
        stubFor(post("/orders").willReturn(serverError()));

        assertThatThrownBy(() -> orderService.createOrder(new OrderRequest()))
            .isInstanceOf(Exception.class);

        // Verify retry attempts (maxAttempts = 3)
        verify(atLeast(3), postRequestedFor(urlEqualTo("/orders")));
    }
}
```

## Rate Limiter Testing

### Testing Rate Limit Enforcement

```java
@SpringBootTest
class RateLimiterTest {

    @Autowired
    private NotificationService notificationService;

    @Test
    void shouldRejectRequestsExceedingRateLimit() {
        // Configuration: 5 permits per second

        // First 5 requests should succeed
        for (int i = 0; i < 5; i++) {
            notificationService.sendEmail(createEmailRequest(i));
        }

        // 6th request should fail immediately (no timeout)
        assertThatThrownBy(() ->
            notificationService.sendEmail(createEmailRequest(6))
        ).isInstanceOf(RequestNotPermitted.class);
    }

    @Test
    void shouldAlowRequestsAfterWindowReset() throws InterruptedException {
        // First batch of requests
        for (int i = 0; i < 5; i++) {
            notificationService.sendEmail(createEmailRequest(i));
        }

        // Wait for refresh period (1 second)
        Thread.sleep(1100);

        // Should succeed - window has reset
        notificationService.sendEmail(createEmailRequest(5));
    }

    private EmailRequest createEmailRequest(int id) {
        return EmailRequest.builder()
            .to("user" + id + "@example.com")
            .subject("Test " + id)
            .build();
    }
}
```

## Bulkhead Testing

### Testing Semaphore Bulkhead

```java
@SpringBootTest
class BulkheadSemaphoreTest {

    @Autowired
    private ReportService reportService;

    @Test
    void shouldLimitConcurrentCalls() {
        // Configuration: maxConcurrentCalls = 5

        CountDownLatch latch = new CountDownLatch(5);
        List<CompletableFuture<Report>> futures = new ArrayList<>();

        // Submit 5 concurrent calls
        for (int i = 0; i < 5; i++) {
            futures.add(CompletableFuture.supplyAsync(() -> {
                latch.countDown();
                return reportService.generateReport(new ReportRequest());
            }));
        }

        // 6th call should be rejected
        assertThatThrownBy(() ->
            reportService.generateReport(new ReportRequest())
        ).isInstanceOf(BulkheadFullException.class);

        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
    }
}
```

### Testing Thread Pool Bulkhead

```java
@SpringBootTest
class BulkheadThreadPoolTest {

    @Autowired
    private AnalyticsService analyticsService;

    @Test
    void shouldUseThreadPoolForAsync() {
        // Configuration: threadPoolSize = 2, queueCapacity = 100

        List<CompletableFuture<AnalyticsResult>> futures = new ArrayList<>();

        for (int i = 0; i < 10; i++) {
            futures.add(analyticsService.runAnalytics(new AnalyticsRequest()));
        }

        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();

        for (CompletableFuture<AnalyticsResult> future : futures) {
            assertThat(future.join()).isNotNull();
        }
    }
}
```

## Time Limiter Testing

### Testing Timeout Enforcement

```java
@SpringBootTest
class TimeLimiterTest {

    @Autowired
    private SearchService searchService;

    @Test
    void shouldTimeoutExceededOperations() {
        // Configuration: timeoutDuration = 1s

        SearchQuery slowQuery = new SearchQuery();
        slowQuery.setSimulatedDelay(Duration.ofSeconds(2));

        assertThatThrownBy(() ->
            searchService.search(slowQuery).get()
        ).hasCauseInstanceOf(TimeoutException.class);
    }

    @Test
    void shouldReturnFallbackOnTimeout() {
        SearchQuery slowQuery = new SearchQuery();
        slowQuery.setSimulatedDelay(Duration.ofSeconds(2));

        CompletableFuture<SearchResults> result = searchService.search(slowQuery);
        SearchResults results = result.join();

        assertThat(results).isNotNull();
        assertThat(results.isTimedOut()).isTrue();
        assertThat(results.getMessage()).contains("timed out");
    }
}
```

## Fallback Method Signature Validation

### Correct Fallback Signatures

```java
@Service
public class PaymentService {

    @CircuitBreaker(name = "payment", fallbackMethod = "paymentFallback")
    public PaymentResponse processPayment(PaymentRequest request) {
        // method body
    }

    // CORRECT: Matches return type and parameters + Exception
    private PaymentResponse paymentFallback(PaymentRequest request, Exception ex) {
        // fallback logic
    }

    @Retry(name = "product")
    public Product getProduct(String productId) {
        // method body
    }

    // CORRECT: Can omit Exception parameter
    private Product getProductFallback(String productId) {
        // fallback logic
    }
}
```

### Common Fallback Signature Errors

```java
@CircuitBreaker(name = "service", fallbackMethod = "fallback")
public String processData(Long id) { }

// WRONG: Missing parameter
public String fallback(Exception ex) { }

// WRONG: Wrong return type
public void fallback(Long id, Exception ex) { }

// WRONG: Wrong parameter type
public String fallback(String id, Exception ex) { }

// CORRECT:
public String fallback(Long id, Exception ex) { }
```

## Integration Testing Configuration

### Test Configuration Profile

```yaml
# application-test.yml
resilience4j:
  circuitbreaker:
    instances:
      testService:
        registerHealthIndicator: false
        slidingWindowSize: 5
        minimumNumberOfCalls: 3
        failureRateThreshold: 50
        waitDurationInOpenState: 100ms

  retry:
    instances:
      testService:
        maxAttempts: 2
        waitDuration: 10ms

  ratelimiter:
    instances:
      testService:
        limitForPeriod: 10
        limitRefreshPeriod: 1s
        timeoutDuration: 10ms
```

### Test Helper Methods

```java
@TestConfiguration
public class ResilienceTestConfig {

    public static void openCircuitBreaker(CircuitBreaker circuitBreaker) {
        circuitBreaker.transitionToOpenState();
    }

    public static void closeCircuitBreaker(CircuitBreaker circuitBreaker) {
        circuitBreaker.transitionToClosedState();
    }

    public static void simulateFailures(
            CircuitBreaker circuitBreaker,
            int numberOfFailures) {
        for (int i = 0; i < numberOfFailures; i++) {
            try {
                circuitBreaker.executeSupplier(() -> {
                    throw new RuntimeException("Simulated failure");
                });
            } catch (Exception ignored) {}
        }
    }

    public static void resetCircuitBreaker(CircuitBreaker circuitBreaker) {
        circuitBreaker.transitionToClosedState();
    }
}
```

## Common Testing Mistakes

### Mistake 1: Not Waiting for Sliding Window

```java
// WRONG: Circuit might not open yet
for (int i = 0; i < 3; i++) {
    try { service.call(); } catch (Exception e) {}
}
assertThat(circuit.getState()).isEqualTo(CircuitBreaker.State.OPEN); // May fail!

// CORRECT: Exceed minimumNumberOfCalls before checking
for (int i = 0; i < 5; i++) {  // minimumNumberOfCalls = 5
    try { service.call(); } catch (Exception e) {}
}
assertThat(circuit.getState()).isEqualTo(CircuitBreaker.State.OPEN);
```

### Mistake 2: Incorrect Fallback Method Access

```java
// WRONG: Fallback method is private, not accessible by AOP
@CircuitBreaker(name = "service", fallbackMethod = "fallback")
public String process(String data) { }

private String fallback(String data, Exception ex) { }  // Private - won't work!

// CORRECT: Package-private or protected
protected String fallback(String data, Exception ex) { }
```

### Mistake 3: Not Mocking External Dependencies

```java
// WRONG: Circuit breaker might open due to real network calls
@SpringBootTest
class ServiceTest {
    @Autowired
    private ServiceWithCircuitBreaker service;

    // Missing @MockBean for external service

    @Test
    void test() {
        // Real network calls - unpredictable
    }
}

// CORRECT: Mock external dependencies
@SpringBootTest
class ServiceTest {
    @Autowired
    private ServiceWithCircuitBreaker service;

    @MockBean
    private ExternalService externalService;

    @Test
    void test() {
        when(externalService.call()).thenThrow(new RuntimeException());
        // Predictable failure
    }
}
```

## Performance Considerations

### Memory Usage in Tests

- **COUNT_BASED sliding window**: Stores last N call outcomes in memory
- **TIME_BASED sliding window**: May require more memory for high-throughput services
- Use smaller `slidingWindowSize` in tests to reduce memory footprint

### Timeout Configuration for Tests

```yaml
resilience4j:
  timelimiter:
    instances:
      testService:
        timeoutDuration: 2s    # Longer timeout for slower CI/CD environments

  circuitbreaker:
    instances:
      testService:
        waitDurationInOpenState: 100ms  # Shorter for faster test execution
```

### Avoiding Test Flakiness

- Set deterministic timeouts based on CI/CD environment
- Use `@ActiveProfiles("test")` for test-specific configurations
- Reset circuit breaker state between tests when needed
- Mock external services consistently
