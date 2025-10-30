# Resilience4j Configuration Reference

## Circuit Breaker Configuration

### Complete Properties List

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        registerHealthIndicator: true                              # Default: false
        slidingWindowType: COUNT_BASED                            # COUNT_BASED or TIME_BASED
        slidingWindowSize: 100                                    # Default: 100 (calls or seconds)
        minimumNumberOfCalls: 10                                  # Default: 100
        failureRateThreshold: 50                                  # Default: 50 (percentage)
        slowCallRateThreshold: 100                                # Default: 100 (percentage)
        slowCallDurationThreshold: 60s                            # Default: 60000ms
        waitDurationInOpenState: 60s                              # Default: 60000ms
        automaticTransitionFromOpenToHalfOpenEnabled: false       # Default: false
        permittedNumberOfCallsInHalfOpenState: 10                 # Default: 10
        maxWaitDurationInHalfOpenState: 0s                        # Default: 0 (unlimited)
        recordExceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
        ignoreExceptions:
          - java.lang.IllegalArgumentException
        eventConsumerBufferSize: 100                              # Default: 100
    instances:
      myService:
        baseConfig: default
        failureRateThreshold: 60
```

### Circuit Breaker States

1. **CLOSED**: Normal operation, calls pass through
2. **OPEN**: Circuit is open, calls immediately fail with `CallNotPermittedException`
3. **HALF_OPEN**: Testing if service recovered, allows limited test calls
4. **DISABLED**: Circuit breaker disabled, all calls pass through
5. **FORCED_OPEN**: Manually forced to open state for emergency situations

### Sliding Window Types

**COUNT_BASED** (Default)
- Aggregates outcome of last N calls
- Better for services with consistent traffic
- `slidingWindowSize` = number of calls to track

**TIME_BASED**
- Aggregates outcome of calls in last N seconds
- Better for services with variable traffic
- `slidingWindowSize` = time in seconds

## Retry Configuration

### Complete Properties List

```yaml
resilience4j:
  retry:
    configs:
      default:
        maxAttempts: 3                                            # Default: 3
        waitDuration: 500ms                                       # Default: 500ms
        enableExponentialBackoff: false                           # Default: false
        exponentialBackoffMultiplier: 2                           # Default: 2
        exponentialMaxWaitDuration: 10s                           # Default: no limit
        enableRandomizedWait: false                               # Default: false
        randomizedWaitFactor: 0.5                                 # Default: 0.5
        retryExceptions:
          - java.io.IOException
          - org.springframework.web.client.ResourceAccessException
        ignoreExceptions:
          - java.lang.IllegalArgumentException
        failAfterMaxAttempts: false                               # Default: false
        eventConsumerBufferSize: 100                              # Default: 100
    instances:
      myService:
        baseConfig: default
        maxAttempts: 5
```

### Exponential Backoff Example

```yaml
waitDuration: 500ms
enableExponentialBackoff: true
exponentialBackoffMultiplier: 2.0
exponentialMaxWaitDuration: 10s
```

Attempt waits:
- Attempt 1: 500ms
- Attempt 2: 1000ms (500 × 2)
- Attempt 3: 2000ms (1000 × 2)
- Attempt 4: 4000ms (2000 × 2)
- Attempt 5: 8000ms (4000 × 2)
- Maximum: 10000ms

## Rate Limiter Configuration

### Complete Properties List

```yaml
resilience4j:
  ratelimiter:
    configs:
      default:
        limitForPeriod: 50                                        # Default: 50
        limitRefreshPeriod: 500ns                                 # Default: 500ns
        timeoutDuration: 5s                                       # Default: 5s
        registerHealthIndicator: true                             # Default: false
        allowHealthIndicatorToFail: true                          # Default: false
    instances:
      myService:
        baseConfig: default
        limitForPeriod: 10
        limitRefreshPeriod: 1s
```

### Common Rate Limit Patterns

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

## Bulkhead Configuration

### Semaphore Bulkhead

```yaml
resilience4j:
  bulkhead:
    configs:
      default:
        maxConcurrentCalls: 25                                    # Default: 25
        maxWaitDuration: 0ms                                      # Default: 0
        eventConsumerBufferSize: 100                              # Default: 100
    instances:
      myService:
        baseConfig: default
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms
```

### Thread Pool Bulkhead

```yaml
resilience4j:
  thread-pool-bulkhead:
    configs:
      default:
        maxThreadPoolSize: 4                                      # Default: Runtime.availableProcessors()
        coreThreadPoolSize: 2                                     # Default: Runtime.availableProcessors() - 1
        queueCapacity: 100                                        # Default: 100
        keepAliveDuration: 20ms                                   # Default: 20ms
        writableStackTraceEnabled: true                           # Default: true
    instances:
      myService:
        baseConfig: default
        maxThreadPoolSize: 8
        coreThreadPoolSize: 4
        queueCapacity: 200
```

## Time Limiter Configuration

### Complete Properties List

```yaml
resilience4j:
  timelimiter:
    configs:
      default:
        timeoutDuration: 1s                                       # Default: 1s
        cancelRunningFuture: true                                 # Default: true
    instances:
      myService:
        baseConfig: default
        timeoutDuration: 3s
```

## Annotation Reference

### @CircuitBreaker

```java
@CircuitBreaker(
    name = "serviceName",                    // Required: Instance name from config
    fallbackMethod = "fallbackMethodName"    // Optional: Fallback method name
)

// Fallback method signature
public String fallback(Long id, Exception ex) { }
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
    name = "serviceName",
    fallbackMethod = "fallbackMethodName"
)
```

### @Bulkhead

```java
@Bulkhead(
    name = "serviceName",
    fallbackMethod = "fallbackMethodName",
    type = Bulkhead.Type.SEMAPHORE              // SEMAPHORE or THREADPOOL
)
```

### @TimeLimiter

```java
@TimeLimiter(
    name = "serviceName",
    fallbackMethod = "fallbackMethodName"
)
// Works only with CompletableFuture<T> or reactive types (Mono<T>, Flux<T>)
```

## Annotation Execution Order

When combining annotations on a method, execution order from outermost to innermost:

1. `@Retry`
2. `@CircuitBreaker`
3. `@RateLimiter`
4. `@TimeLimiter`
5. `@Bulkhead`
6. Actual method call

## Exception Reference

| Pattern | Exception | HTTP Status | Meaning |
|---------|-----------|-------------|---------|
| Circuit Breaker | `CallNotPermittedException` | 503 | Circuit is OPEN or FORCED_OPEN |
| Rate Limiter | `RequestNotPermitted` | 429 | No permits available |
| Bulkhead | `BulkheadFullException` | 503 | Bulkhead at capacity |
| Time Limiter | `TimeoutException` | 408 | Operation exceeded timeout |

## Programmatic Configuration

### Circuit Breaker

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)
    .waitDurationInOpenState(Duration.ofSeconds(10))
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .permittedNumberOfCallsInHalfOpenState(3)
    .minimumNumberOfCalls(10)
    .slidingWindowType(CircuitBreakerConfig.SlidingWindowType.COUNT_BASED)
    .slidingWindowSize(100)
    .recordExceptions(IOException.class, TimeoutException.class)
    .ignoreExceptions(IllegalArgumentException.class)
    .build();

CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);
CircuitBreaker circuitBreaker = registry.circuitBreaker("myService");
```

### Retry

```java
RetryConfig config = RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(500))
    .intervalFunction(IntervalFunction.ofExponentialBackoff(
        Duration.ofMillis(500),
        2.0
    ))
    .retryExceptions(IOException.class, TimeoutException.class)
    .ignoreExceptions(IllegalArgumentException.class)
    .build();

RetryRegistry registry = RetryRegistry.of(config);
Retry retry = registry.retry("myService");
```

## Actuator Endpoints

Access monitoring endpoints when management endpoints are enabled:

| Endpoint | Description |
|----------|-------------|
| `GET /actuator/circuitbreakers` | List all circuit breakers and states |
| `GET /actuator/circuitbreakerevents` | List circuit breaker events |
| `GET /actuator/retryevents` | List retry events |
| `GET /actuator/ratelimiters` | List rate limiters |
| `GET /actuator/bulkheads` | List bulkhead status |
| `GET /actuator/timelimiters` | List time limiters |
| `GET /actuator/metrics` | Custom resilience metrics |

## Micrometer Metrics

Resilience4j exposes the following metrics:

**Circuit Breaker Metrics**
- `resilience4j.circuitbreaker.calls{name, kind}`
- `resilience4j.circuitbreaker.state{name, state}`
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

## Version Compatibility

| Resilience4j | Spring Boot | Java | Spring Framework |
|--------------|-------------|------|------------------|
| 2.2.x        | 3.x         | 17+  | 6.x              |
| 2.1.x        | 3.x         | 17+  | 6.x              |
| 2.0.x        | 2.7.x       | 8+   | 5.3.x            |
| 1.7.x        | 2.x         | 8+   | 5.x              |

## References

- [Resilience4j Official Documentation](https://resilience4j.readme.io/)
- [Spring Boot Integration Guide](https://resilience4j.readme.io/docs/getting-started-3)
- [Micrometer Metrics Guide](https://resilience4j.readme.io/docs/micrometer)
