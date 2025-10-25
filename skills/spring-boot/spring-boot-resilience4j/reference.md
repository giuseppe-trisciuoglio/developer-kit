# Resilience4j Reference Documentation

## Configuration Properties Reference

### Circuit Breaker Configuration

#### Complete Properties List

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        # Health indicator registration
        registerHealthIndicator: true                              # Default: false
        
        # Sliding window configuration
        slidingWindowType: COUNT_BASED                            # COUNT_BASED or TIME_BASED
        slidingWindowSize: 100                                    # Default: 100 (calls or seconds)
        minimumNumberOfCalls: 10                                  # Default: 100
        
        # Failure thresholds
        failureRateThreshold: 50                                  # Default: 50 (percentage)
        slowCallRateThreshold: 100                                # Default: 100 (percentage)
        slowCallDurationThreshold: 60s                            # Default: 60000ms
        
        # State transition configuration
        waitDurationInOpenState: 60s                              # Default: 60000ms
        automaticTransitionFromOpenToHalfOpenEnabled: false       # Default: false
        permittedNumberOfCallsInHalfOpenState: 10                 # Default: 10
        maxWaitDurationInHalfOpenState: 0s                        # Default: 0 (unlimited)
        
        # Exception configuration
        recordExceptions:                                          # Default: empty
          - java.io.IOException
          - java.util.concurrent.TimeoutException
        ignoreExceptions:                                          # Default: empty
          - java.lang.IllegalArgumentException
          - com.myapp.BusinessException
        
        # Event monitoring
        eventConsumerBufferSize: 100                              # Default: 100
        
    instances:
      myService:
        baseConfig: default
        failureRateThreshold: 60
```

#### Circuit Breaker States

1. **CLOSED**: Normal operation, calls pass through
   - Tracks success/failure rate in sliding window
   - Transitions to OPEN when `failureRateThreshold` exceeded

2. **OPEN**: Circuit is open, calls immediately fail
   - Returns `CallNotPermittedException`
   - Waits for `waitDurationInOpenState` before transitioning
   - Can execute fallback methods if configured

3. **HALF_OPEN**: Testing if service recovered
   - Allows `permittedNumberOfCallsInHalfOpenState` test calls
   - Transitions to CLOSED if calls succeed
   - Transitions back to OPEN if calls fail

4. **DISABLED**: Circuit breaker is disabled
   - All calls pass through without monitoring

5. **FORCED_OPEN**: Manually forced to open state
   - Used for emergency circuit opening

#### Sliding Window Types

**COUNT_BASED** (Default)
- Aggregates outcome of last N calls
- `slidingWindowSize` = number of calls
- Better for services with consistent traffic

```yaml
slidingWindowType: COUNT_BASED
slidingWindowSize: 100        # Last 100 calls
minimumNumberOfCalls: 10      # Need 10 calls before calculating failure rate
```

**TIME_BASED**
- Aggregates outcome of calls in last N seconds
- `slidingWindowSize` = time in seconds
- Better for services with variable traffic

```yaml
slidingWindowType: TIME_BASED
slidingWindowSize: 10         # Last 10 seconds
minimumNumberOfCalls: 5       # Need 5 calls in window before calculating
```

#### Programmatic Configuration

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)
    .slowCallRateThreshold(50)
    .waitDurationInOpenState(Duration.ofMillis(10000))
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .permittedNumberOfCallsInHalfOpenState(3)
    .minimumNumberOfCalls(10)
    .slidingWindowType(SlidingWindowType.COUNT_BASED)
    .slidingWindowSize(100)
    .recordException(e -> e instanceof IOException)
    .recordExceptions(IOException.class, TimeoutException.class)
    .ignoreExceptions(IllegalArgumentException.class)
    .recordFailurePredicate(throwable -> {
        // Custom logic to determine if exception should be recorded
        return !(throwable instanceof BusinessException);
    })
    .build();

CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);
CircuitBreaker circuitBreaker = registry.circuitBreaker("myService");
```

### Retry Configuration

#### Complete Properties List

```yaml
resilience4j:
  retry:
    configs:
      default:
        # Retry attempts
        maxAttempts: 3                                            # Default: 3
        
        # Wait duration between retries
        waitDuration: 500ms                                       # Default: 500ms
        
        # Exponential backoff
        enableExponentialBackoff: false                           # Default: false
        exponentialBackoffMultiplier: 2                           # Default: 2
        exponentialMaxWaitDuration: 10s                           # Default: no limit
        
        # Random delay
        enableRandomizedWait: false                               # Default: false
        randomizedWaitFactor: 0.5                                 # Default: 0.5
        
        # Exception configuration
        retryExceptions:                                          # Default: empty (all)
          - java.io.IOException
          - org.springframework.web.client.ResourceAccessException
        ignoreExceptions:                                         # Default: empty
          - java.lang.IllegalArgumentException
          - com.myapp.BusinessException
        
        # Failure handling
        failAfterMaxAttempts: false                               # Default: false
        
        # Event monitoring
        eventConsumerBufferSize: 100                              # Default: 100
        
    instances:
      myService:
        baseConfig: default
        maxAttempts: 5
```

#### Wait Duration Strategies

**Fixed Wait Duration**
```yaml
waitDuration: 1000ms
```

**Exponential Backoff**
```yaml
waitDuration: 500ms
enableExponentialBackoff: true
exponentialBackoffMultiplier: 2.0
exponentialMaxWaitDuration: 10s
```
- Attempt 1: 500ms
- Attempt 2: 1000ms (500 × 2)
- Attempt 3: 2000ms (1000 × 2)
- Attempt 4: 4000ms (2000 × 2)
- Attempt 5: 8000ms (4000 × 2)
- Maximum: 10000ms

**Randomized Wait**
```yaml
waitDuration: 1000ms
enableRandomizedWait: true
randomizedWaitFactor: 0.5
```
- Wait time: between 500ms and 1500ms randomly

#### Programmatic Configuration

```java
RetryConfig config = RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(500))
    .intervalFunction(IntervalFunction.ofExponentialBackoff(
        Duration.ofMillis(500), 
        2.0
    ))
    .retryOnException(e -> e instanceof IOException)
    .retryExceptions(IOException.class, TimeoutException.class)
    .ignoreExceptions(IllegalArgumentException.class)
    .retryOnResult(response -> response == null)
    .failAfterMaxAttempts(true)
    .build();

RetryRegistry registry = RetryRegistry.of(config);
Retry retry = registry.retry("myService");
```

#### Custom Interval Function

```java
IntervalFunction intervalFn = IntervalFunction
    .of(Duration.ofMillis(500), attempt -> {
        // Custom backoff logic
        return Duration.ofMillis(500 * (long)Math.pow(2, attempt - 1));
    });

RetryConfig config = RetryConfig.custom()
    .intervalFunction(intervalFn)
    .build();
```

### Rate Limiter Configuration

#### Complete Properties List

```yaml
resilience4j:
  ratelimiter:
    configs:
      default:
        # Rate limiting
        limitForPeriod: 50                                        # Default: 50
        limitRefreshPeriod: 500ns                                 # Default: 500ns
        timeoutDuration: 5s                                       # Default: 5s
        
        # Health and monitoring
        registerHealthIndicator: true                             # Default: false
        allowHealthIndicatorToFail: true                          # Default: false
        subscribeForEvents: true                                  # Default: false
        eventConsumerBufferSize: 100                              # Default: 100
        
    instances:
      myService:
        baseConfig: default
        limitForPeriod: 10
        limitRefreshPeriod: 1s
```

#### Rate Limiter Parameters Explained

**limitForPeriod**: Maximum number of permits available during one period
**limitRefreshPeriod**: Duration of the period
**timeoutDuration**: How long a thread will wait for permission

Example configurations:

**10 requests per second**
```yaml
limitForPeriod: 10
limitRefreshPeriod: 1s
timeoutDuration: 0s           # Fail immediately if no permits
```

**100 requests per minute**
```yaml
limitForPeriod: 100
limitRefreshPeriod: 1m
timeoutDuration: 500ms        # Wait up to 500ms for permit
```

**5 requests per second with queuing**
```yaml
limitForPeriod: 5
limitRefreshPeriod: 1s
timeoutDuration: 2s           # Wait up to 2s for permit
```

#### Programmatic Configuration

```java
RateLimiterConfig config = RateLimiterConfig.custom()
    .limitRefreshPeriod(Duration.ofSeconds(1))
    .limitForPeriod(10)
    .timeoutDuration(Duration.ofMillis(500))
    .writableStackTraceEnabled(true)
    .build();

RateLimiterRegistry registry = RateLimiterRegistry.of(config);
RateLimiter rateLimiter = registry.rateLimiter("myService");
```

### Bulkhead Configuration

#### Semaphore Bulkhead

```yaml
resilience4j:
  bulkhead:
    configs:
      default:
        # Concurrency limits
        maxConcurrentCalls: 25                                    # Default: 25
        maxWaitDuration: 0ms                                      # Default: 0
        
        # Event monitoring
        eventConsumerBufferSize: 100                              # Default: 100
        
    instances:
      myService:
        baseConfig: default
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms
```

**Programmatic Configuration**
```java
BulkheadConfig config = BulkheadConfig.custom()
    .maxConcurrentCalls(10)
    .maxWaitDuration(Duration.ofMillis(100))
    .writableStackTraceEnabled(true)
    .build();

BulkheadRegistry registry = BulkheadRegistry.of(config);
Bulkhead bulkhead = registry.bulkhead("myService");
```

#### Thread Pool Bulkhead

```yaml
resilience4j:
  thread-pool-bulkhead:
    configs:
      default:
        # Thread pool sizing
        maxThreadPoolSize: 4                                      # Default: Runtime.availableProcessors()
        coreThreadPoolSize: 2                                     # Default: Runtime.availableProcessors() - 1
        queueCapacity: 100                                        # Default: 100
        keepAliveDuration: 20ms                                   # Default: 20ms
        
        # Stack trace
        writableStackTraceEnabled: true                           # Default: true
        
    instances:
      myService:
        baseConfig: default
        maxThreadPoolSize: 8
        coreThreadPoolSize: 4
        queueCapacity: 200
```

**Programmatic Configuration**
```java
ThreadPoolBulkheadConfig config = ThreadPoolBulkheadConfig.custom()
    .maxThreadPoolSize(8)
    .coreThreadPoolSize(4)
    .queueCapacity(200)
    .keepAliveDuration(Duration.ofMillis(20))
    .writableStackTraceEnabled(true)
    .build();

ThreadPoolBulkheadRegistry registry = ThreadPoolBulkheadRegistry.of(config);
ThreadPoolBulkhead bulkhead = registry.bulkhead("myService");
```

### Time Limiter Configuration

#### Complete Properties List

```yaml
resilience4j:
  timelimiter:
    configs:
      default:
        # Timeout configuration
        timeoutDuration: 1s                                       # Default: 1s
        cancelRunningFuture: true                                 # Default: true
        
    instances:
      myService:
        baseConfig: default
        timeoutDuration: 3s
```

#### Programmatic Configuration

```java
TimeLimiterConfig config = TimeLimiterConfig.custom()
    .timeoutDuration(Duration.ofSeconds(3))
    .cancelRunningFuture(true)
    .build();

TimeLimiterRegistry registry = TimeLimiterRegistry.of(config);
TimeLimiter timeLimiter = registry.timeLimiter("myService");
```

## Annotation Reference

### @CircuitBreaker

```java
@CircuitBreaker(
    name = "serviceName",                    // Required: Instance name from config
    fallbackMethod = "fallbackMethodName"    // Optional: Fallback method name
)
```

**Fallback Method Signature Requirements:**
```java
// Original method
@CircuitBreaker(name = "service", fallbackMethod = "fallback")
public String getData(Long id) { }

// Fallback method - must match return type and parameters + Exception
public String fallback(Long id, Exception ex) { }

// Or without exception parameter (less common)
public String fallback(Long id) { }
```

### @Retry

```java
@Retry(
    name = "serviceName",                    // Required: Instance name from config
    fallbackMethod = "fallbackMethodName"    // Optional: Fallback method name
)
```

### @RateLimiter

```java
@RateLimiter(
    name = "serviceName",                    // Required: Instance name from config
    fallbackMethod = "fallbackMethodName"    // Optional: Fallback method name
)
```

### @Bulkhead

```java
@Bulkhead(
    name = "serviceName",                    // Required: Instance name from config
    fallbackMethod = "fallbackMethodName",   // Optional: Fallback method name
    type = Bulkhead.Type.SEMAPHORE          // Optional: SEMAPHORE or THREADPOOL
)
```

### @TimeLimiter

```java
@TimeLimiter(
    name = "serviceName",                    // Required: Instance name from config
    fallbackMethod = "fallbackMethodName"    // Optional: Fallback method name
)
```

**Important**: TimeLimiter only works with `CompletableFuture<T>` or reactive types (`Mono<T>`, `Flux<T>`)

### Combining Annotations

Order of execution (from outer to inner):
1. `@Retry`
2. `@CircuitBreaker`
3. `@RateLimiter`
4. `@TimeLimiter`
5. `@Bulkhead`
6. Actual method call

```java
@Retry(name = "service")
@CircuitBreaker(name = "service", fallbackMethod = "fallback")
@RateLimiter(name = "service")
@Bulkhead(name = "service", type = Bulkhead.Type.THREADPOOL)
public CompletableFuture<Result> complexOperation() {
    // Method implementation
}
```

## Exception Reference

### CircuitBreaker Exceptions

**CallNotPermittedException**
- Thrown when circuit breaker is in OPEN or FORCED_OPEN state
- Indicates circuit is protecting the service
- Should return HTTP 503 (Service Unavailable)

```java
@ExceptionHandler(CallNotPermittedException.class)
@ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
public ErrorResponse handleCallNotPermitted(CallNotPermittedException ex) {
    return new ErrorResponse("Circuit breaker is open");
}
```

### Retry Exceptions

**MaxRetriesExceededException**
- Thrown when `failAfterMaxAttempts: true` and all retries exhausted
- Contains the last exception that caused the failure
- Should return appropriate HTTP status based on underlying exception

### RateLimiter Exceptions

**RequestNotPermitted**
- Thrown when rate limit is exceeded and no permits available
- Should return HTTP 429 (Too Many Requests)

```java
@ExceptionHandler(RequestNotPermitted.class)
@ResponseStatus(HttpStatus.TOO_MANY_REQUESTS)
public ErrorResponse handleRequestNotPermitted(RequestNotPermitted ex) {
    return new ErrorResponse("Rate limit exceeded");
}
```

### Bulkhead Exceptions

**BulkheadFullException**
- Thrown when bulkhead is full and `maxWaitDuration` exceeded
- Should return HTTP 509 (Bandwidth Limit Exceeded) or 503

```java
@ExceptionHandler(BulkheadFullException.class)
@ResponseStatus(HttpStatus.BANDWIDTH_LIMIT_EXCEEDED)
public ErrorResponse handleBulkheadFull(BulkheadFullException ex) {
    return new ErrorResponse("Service capacity exceeded");
}
```

### TimeLimiter Exceptions

**TimeoutException**
- Thrown when operation exceeds `timeoutDuration`
- Should return HTTP 408 (Request Timeout)

```java
@ExceptionHandler(TimeoutException.class)
@ResponseStatus(HttpStatus.REQUEST_TIMEOUT)
public ErrorResponse handleTimeout(TimeoutException ex) {
    return new ErrorResponse("Request timed out");
}
```

## Actuator Endpoints Reference

### Health Endpoints

**Circuit Breaker Health**
```
GET /actuator/health/circuitBreakers
```

Response when circuit is CLOSED:
```json
{
  "status": "UP",
  "components": {
    "circuitBreakers": {
      "status": "UP",
      "details": {
        "myService": {
          "status": "UP",
          "details": {
            "state": "CLOSED",
            "failureRate": "0.0%",
            "slowCallRate": "0.0%",
            "bufferedCalls": 10,
            "failedCalls": 0,
            "slowCalls": 0,
            "notPermittedCalls": 0
          }
        }
      }
    }
  }
}
```

**Rate Limiter Health**
```
GET /actuator/health/rateLimiters
```

### Metrics Endpoints

**Circuit Breakers List**
```
GET /actuator/circuitbreakers
```
Response:
```json
{
  "circuitBreakers": ["myService", "anotherService"]
}
```

**Circuit Breaker Events**
```
GET /actuator/circuitbreakerevents
GET /actuator/circuitbreakerevents/{name}
GET /actuator/circuitbreakerevents/{name}/{eventType}
```

Event types: `SUCCESS`, `ERROR`, `IGNORED_ERROR`, `NOT_PERMITTED`, `STATE_TRANSITION`

**Retry Events**
```
GET /actuator/retryevents
GET /actuator/retryevents/{name}
GET /actuator/retryevents/{name}/{eventType}
```

Event types: `SUCCESS`, `ERROR`, `RETRY`, `IGNORED_ERROR`

**Rate Limiter Events**
```
GET /actuator/ratelimiters
GET /actuator/ratelimiterevents
GET /actuator/ratelimiterevents/{name}
```

**Bulkhead Events**
```
GET /actuator/bulkheads
GET /actuator/bulkheadevents
GET /actuator/bulkheadevents/{name}
```

**Time Limiter Events**
```
GET /actuator/timelimiters
GET /actuator/timelimiterevents
GET /actuator/timelimiterevents/{name}
```

### Micrometer Metrics

Resilience4j exposes metrics to Micrometer:

**Circuit Breaker Metrics**
- `resilience4j.circuitbreaker.calls{name, kind}`
- `resilience4j.circuitbreaker.state{name, state}`
- `resilience4j.circuitbreaker.buffered.calls{name, kind}`
- `resilience4j.circuitbreaker.failure.rate{name}`
- `resilience4j.circuitbreaker.slow.call.rate{name}`

**Retry Metrics**
- `resilience4j.retry.calls{name, kind}`

**Rate Limiter Metrics**
- `resilience4j.ratelimiter.available.permissions{name}`
- `resilience4j.ratelimiter.waiting_threads{name}`

**Bulkhead Metrics**
- `resilience4j.bulkhead.available.concurrent.calls{name}`
- `resilience4j.bulkhead.max.allowed.concurrent.calls{name}`

**Time Limiter Metrics**
- `resilience4j.timelimiter.calls{name, kind}`

## Event Monitoring

### Event Consumer Configuration

```java
@Configuration
public class ResilienceEventConfig {
    
    @Bean
    public EventConsumerRegistry<CircuitBreakerEvent> circuitBreakerEventConsumerRegistry() {
        return new EventConsumerRegistry<>();
    }
    
    @EventListener
    public void onCircuitBreakerEvent(CircuitBreakerOnStateTransitionEvent event) {
        logger.info("Circuit Breaker {} transitioned from {} to {}",
            event.getCircuitBreakerName(),
            event.getStateTransition().getFromState(),
            event.getStateTransition().getToState()
        );
    }
    
    @EventListener
    public void onRetryEvent(RetryOnRetryEvent event) {
        logger.warn("Retry attempt {} for {}",
            event.getNumberOfRetryAttempts(),
            event.getName()
        );
    }
}
```

### Programmatic Event Consumption

```java
CircuitBreaker circuitBreaker = circuitBreakerRegistry.circuitBreaker("myService");

circuitBreaker.getEventPublisher()
    .onStateTransition(event -> 
        logger.info("State transition: {}", event.getStateTransition())
    )
    .onSuccess(event -> 
        logger.debug("Call succeeded")
    )
    .onError(event -> 
        logger.error("Call failed: {}", event.getThrowable())
    )
    .onCallNotPermitted(event -> 
        logger.warn("Call not permitted")
    );

Retry retry = retryRegistry.retry("myService");

retry.getEventPublisher()
    .onRetry(event -> 
        logger.info("Retry attempt: {}", event.getNumberOfRetryAttempts())
    )
    .onError(event -> 
        logger.error("Retry failed after {} attempts", 
            event.getNumberOfRetryAttempts())
    );
```

## Reactive Support

### WebFlux Integration

```java
@Service
public class ReactiveUserService {
    
    private final WebClient webClient;
    private final CircuitBreakerRegistry circuitBreakerRegistry;
    private final RetryRegistry retryRegistry;
    
    public Mono<User> getUser(String userId) {
        CircuitBreaker circuitBreaker = circuitBreakerRegistry
            .circuitBreaker("userService");
        Retry retry = retryRegistry.retry("userService");
        
        return webClient.get()
            .uri("/users/{id}", userId)
            .retrieve()
            .bodyToMono(User.class)
            .transformDeferred(CircuitBreakerOperator.of(circuitBreaker))
            .transformDeferred(RetryOperator.of(retry))
            .onErrorResume(throwable -> 
                Mono.just(User.defaultUser())
            );
    }
}
```

### Reactor Decorators

```java
import io.github.resilience4j.reactor.circuitbreaker.operator.CircuitBreakerOperator;
import io.github.resilience4j.reactor.retry.RetryOperator;
import io.github.resilience4j.reactor.ratelimiter.operator.RateLimiterOperator;

public Flux<Data> streamData() {
    return dataSource.stream()
        .transformDeferred(CircuitBreakerOperator.of(circuitBreaker))
        .transformDeferred(RetryOperator.of(retry))
        .transformDeferred(RateLimiterOperator.of(rateLimiter));
}
```

## Kotlin Support

### Extension Functions

```kotlin
suspend fun <T> CircuitBreaker.executeSuspendFunction(
    block: suspend () -> T
): T = suspendCoroutine { cont ->
    val decoratedBlock = CircuitBreaker.decorateSupplier(this) { 
        runBlocking { block() } 
    }
    try {
        cont.resume(decoratedBlock.get())
    } catch (e: Exception) {
        cont.resumeWithException(e)
    }
}
```

### Coroutine Integration

```kotlin
@Service
class UserService(
    private val circuitBreakerRegistry: CircuitBreakerRegistry,
    private val httpClient: HttpClient
) {
    private val circuitBreaker = circuitBreakerRegistry.circuitBreaker("userService")
    
    suspend fun getUser(id: String): User = withContext(Dispatchers.IO) {
        circuitBreaker.executeSuspendFunction {
            httpClient.get("/users/$id")
        }
    }
}
```

## Testing Utilities

### Test Configuration

```yaml
# application-test.yml
resilience4j:
  circuitbreaker:
    instances:
      test-service:
        registerHealthIndicator: false
        slidingWindowSize: 5
        minimumNumberOfCalls: 3
        failureRateThreshold: 50
        waitDurationInOpenState: 100ms
        
  retry:
    instances:
      test-service:
        maxAttempts: 2
        waitDuration: 10ms
```

### Triggering Circuit States

```java
@TestConfiguration
public class ResilienceTestConfig {
    
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        return CircuitBreakerRegistry.ofDefaults();
    }
    
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
}
```

## Performance Considerations

### Memory Usage

**Circuit Breaker**
- COUNT_BASED: O(slidingWindowSize) per instance
- TIME_BASED: O(slidingWindowSize × calls per second) per instance

**Retry**: Minimal overhead, only state tracking

**Rate Limiter**: O(1) per instance

**Bulkhead**
- Semaphore: O(1) per instance
- ThreadPool: O(queueCapacity) per instance

### Thread Safety

All Resilience4j components are thread-safe and designed for concurrent use.

### Overhead Benchmarks

Typical overhead per call:
- Circuit Breaker: 1-5 microseconds
- Retry: 0.5-2 microseconds (when no retry needed)
- Rate Limiter: 2-10 microseconds
- Bulkhead (Semaphore): 1-3 microseconds
- Bulkhead (ThreadPool): 50-200 microseconds
- Time Limiter: 10-50 microseconds

## Migration Guide

### From Hystrix to Resilience4j

**Hystrix Command**
```java
public class UserCommand extends HystrixCommand<User> {
    protected User run() {
        return userService.getUser();
    }
    
    protected User getFallback() {
        return User.defaultUser();
    }
}
```

**Resilience4j Equivalent**
```java
@CircuitBreaker(name = "userService", fallbackMethod = "getUserFallback")
public User getUser() {
    return userService.getUser();
}

private User getUserFallback(Exception ex) {
    return User.defaultUser();
}
```

### Configuration Mapping

| Hystrix | Resilience4j CircuitBreaker |
|---------|----------------------------|
| circuitBreaker.requestVolumeThreshold | minimumNumberOfCalls |
| circuitBreaker.errorThresholdPercentage | failureRateThreshold |
| circuitBreaker.sleepWindowInMilliseconds | waitDurationInOpenState |
| metrics.rollingStats.timeInMilliseconds | slidingWindowSize (TIME_BASED) |
| metrics.rollingStats.numBuckets | (not directly comparable) |

## Version Compatibility

| Resilience4j | Spring Boot | Java | Spring Framework |
|--------------|-------------|------|------------------|
| 2.2.x        | 3.x         | 17+  | 6.x              |
| 2.1.x        | 3.x         | 17+  | 6.x              |
| 2.0.x        | 2.7.x       | 8+   | 5.3.x            |
| 1.7.x        | 2.x         | 8+   | 5.x              |

## Additional Resources

- [Official Documentation](https://resilience4j.readme.io/)
- [GitHub Repository](https://github.com/resilience4j/resilience4j)
- [Spring Boot Integration Guide](https://resilience4j.readme.io/docs/getting-started-3)
- [Micrometer Metrics](https://resilience4j.readme.io/docs/micrometer)
