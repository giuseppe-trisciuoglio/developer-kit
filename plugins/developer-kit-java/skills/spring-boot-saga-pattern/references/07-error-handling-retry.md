# Error Handling and Retry Strategies

## Retry Configuration

Use Spring Retry for automatic retry logic:

```java
@Configuration
@EnableRetry
public class RetryConfig {

    @Bean
    public RetryTemplate retryTemplate() {
        RetryTemplate retryTemplate = new RetryTemplate();

        FixedBackOffPolicy backOffPolicy = new FixedBackOffPolicy();
        backOffPolicy.setBackOffPeriod(2000L); // 2 second delay

        ExponentialBackOffPolicy exponentialBackOff = new ExponentialBackOffPolicy();
        exponentialBackOff.setInitialInterval(1000L);
        exponentialBackOff.setMultiplier(2.0);
        exponentialBackOff.setMaxInterval(10000L);

        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy();
        retryPolicy.setMaxAttempts(3);

        retryTemplate.setBackOffPolicy(exponentialBackOff);
        retryTemplate.setRetryPolicy(retryPolicy);

        return retryTemplate;
    }
}
```

## Retry with @Retryable

```java
@Service
public class OrderService {

    @Retryable(
        value = {TransientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public void processOrder(String orderId) {
        // Order processing logic
    }

    @Recover
    public void recover(TransientException ex, String orderId) {
        logger.error("Order processing failed after retries: {}", orderId, ex);
        // Fallback logic
    }
}
```

## Circuit Breaker with Resilience4j

Prevent cascading failures:

```java
@Configuration
public class CircuitBreakerConfig {

    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)  // Open after 50% failures
            .waitDurationInOpenState(Duration.ofMillis(1000))
            .slidingWindowSize(2)      // Check last 2 calls
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

    private PaymentResult callPaymentGateway(PaymentRequest request) {
        // Call external payment gateway
        return new PaymentResult(...);
    }
}
```

## Dead Letter Queue

Handle failed messages:

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
            logger.error("Processing failed for message: {}", record.key());
            kafkaTemplate.send("saga-dlq", record.key(), record.value());
        });
    }
}
```

## Timeout Handling

Define and enforce timeout policies:

```java
@Service
public class TimeoutHandler {

    private final SagaStateRepository sagaStateRepository;
    private static final Duration STEP_TIMEOUT = Duration.ofSeconds(30);

    @Scheduled(fixedDelay = 5000)
    public void checkForTimeouts() {
        Instant timeoutThreshold = Instant.now().minus(STEP_TIMEOUT);

        List<SagaState> timedOutSagas = sagaStateRepository
            .findByStatusAndUpdatedAtBefore(SagaStatus.PROCESSING, timeoutThreshold);

        timedOutSagas.forEach(saga -> {
            logger.warn("Saga {} timed out at step {}",
                saga.getSagaId(), saga.getCurrentStep());
            compensateSaga(saga);
        });
    }

    private void compensateSaga(SagaState saga) {
        saga.setStatus(SagaStatus.COMPENSATING);
        sagaStateRepository.save(saga);
    }
}
```

## Exponential Backoff

Prevent overwhelming downstream services:

```java
@Service
public class BackoffService {

    public Duration calculateBackoff(int attemptNumber) {
        long baseDelay = 1000; // 1 second
        long delay = baseDelay * (long) Math.pow(2, attemptNumber - 1);
        long maxDelay = 30000; // 30 seconds

        return Duration.ofMillis(Math.min(delay, maxDelay));
    }

    @Retryable(
        value = {ServiceUnavailableException.class},
        maxAttempts = 5,
        backoff = @Backoff(
            delay = 1000,
            multiplier = 2.0,
            maxDelay = 30000
        )
    )
    public void callExternalService() {
        // External service call
    }
}
```

## Idempotent Retry

Ensure retries don't cause duplicate processing:

```java
@Service
public class IdempotentPaymentService {

    private final PaymentRepository paymentRepository;
    private final Map<String, PaymentResult> processedPayments = new ConcurrentHashMap<>();

    public PaymentResult processPayment(String paymentId, BigDecimal amount) {
        // Check if already processed
        if (processedPayments.containsKey(paymentId)) {
            return processedPayments.get(paymentId);
        }

        // Check database
        Optional<Payment> existing = paymentRepository.findById(paymentId);
        if (existing.isPresent()) {
            return new PaymentResult(existing.get());
        }

        // Process payment
        PaymentResult result = callPaymentGateway(paymentId, amount);

        // Cache and persist
        processedPayments.put(paymentId, result);
        paymentRepository.save(new Payment(paymentId, amount, result.getStatus()));

        return result;
    }
}
```

## Global Exception Handler

Centralize error handling:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(SagaExecutionException.class)
    public ResponseEntity<ErrorResponse> handleSagaError(
            SagaExecutionException ex) {

        return ResponseEntity
            .status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body(new ErrorResponse(
                "SAGA_EXECUTION_FAILED",
                ex.getMessage(),
                ex.getSagaId()
            ));
    }

    @ExceptionHandler(ServiceUnavailableException.class)
    public ResponseEntity<ErrorResponse> handleServiceUnavailable(
            ServiceUnavailableException ex) {

        return ResponseEntity
            .status(HttpStatus.SERVICE_UNAVAILABLE)
            .body(new ErrorResponse(
                "SERVICE_UNAVAILABLE",
                "Required service is temporarily unavailable"
            ));
    }

    @ExceptionHandler(TimeoutException.class)
    public ResponseEntity<ErrorResponse> handleTimeout(
            TimeoutException ex) {

        return ResponseEntity
            .status(HttpStatus.REQUEST_TIMEOUT)
            .body(new ErrorResponse(
                "REQUEST_TIMEOUT",
                "Request timed out after " + ex.getDuration()
            ));
    }
}

public record ErrorResponse(
    String code,
    String message,
    String details
) {
    public ErrorResponse(String code, String message) {
        this(code, message, null);
    }
}
```

## Monitoring Error Rates

Track failure metrics:

```java
@Component
public class SagaErrorMetrics {

    private final MeterRegistry meterRegistry;

    public SagaErrorMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    public void recordSagaFailure(String sagaType) {
        Counter.builder("saga.failure")
            .tag("type", sagaType)
            .register(meterRegistry)
            .increment();
    }

    public void recordRetry(String sagaType) {
        Counter.builder("saga.retry")
            .tag("type", sagaType)
            .register(meterRegistry)
            .increment();
    }

    public void recordTimeout(String sagaType) {
        Counter.builder("saga.timeout")
            .tag("type", sagaType)
            .register(meterRegistry)
            .increment();
    }
}
```
