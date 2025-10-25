---
name: spring-boot-resilience4j
description: Implement fault tolerance and resilience patterns in Spring Boot applications using Resilience4j library. Use for circuit breaker, retry, rate limiter, bulkhead, time limiter, and fallback patterns. Apply when building resilient microservices that need to handle failures gracefully, prevent cascading failures, and manage external service dependencies.
allowed-tools: Read, Write, Edit, Bash
---

# Spring Boot Resilience4j Patterns

## When to Use

Use this skill when you need to:
- Implement circuit breaker pattern to prevent cascading failures
- Add retry logic for transient failures
- Apply rate limiting to protect services from overload
- Implement bulkhead pattern for resource isolation
- Add timeout controls with time limiter
- Build resilient microservices with fallback mechanisms
- Handle external service dependencies gracefully
- Prevent resource exhaustion in distributed systems

**Trigger phrases**: resilience4j, circuit breaker, retry pattern, rate limiter, fault tolerance, bulkhead, time limiter, fallback method, resilient microservices

## Overview

Resilience4j is a lightweight fault tolerance library designed for Java applications. It provides various patterns to handle potential failures in microservices and distributed systems, ensuring applications remain stable even when external dependencies fail.

### Core Resilience Patterns

1. **Circuit Breaker**: Prevents cascading failures by stopping requests to failing services
2. **Retry**: Automatically retries failed operations for transient errors
3. **Rate Limiter**: Controls the rate of requests to prevent service overload
4. **Bulkhead**: Limits concurrent calls to isolate resources
5. **Time Limiter**: Sets timeout thresholds for async operations
6. **Fallback**: Provides alternative responses when operations fail

## Instructions

### 1. Setup and Dependencies

#### Maven Configuration
Add these dependencies to your `pom.xml`:

```xml
<properties>
    <resilience4j.version>2.2.0</resilience4j.version>
</properties>

<dependencies>
    <!-- Resilience4j Spring Boot Integration -->
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-spring-boot2</artifactId>
        <version>${resilience4j.version}</version>
    </dependency>
    
    <!-- For Spring Boot 3.x use resilience4j-spring-boot3 -->
    <!--
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-spring-boot3</artifactId>
        <version>${resilience4j.version}</version>
    </dependency>
    -->
    
    <!-- Required for Reactive support -->
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-reactor</artifactId>
        <version>${resilience4j.version}</version>
    </dependency>
    
    <!-- Required for annotations -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-aop</artifactId>
    </dependency>
    
    <!-- For monitoring and metrics -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
</dependencies>
```

#### Gradle Configuration
Add these dependencies to your `build.gradle`:

```gradle
ext {
    resilience4jVersion = '2.2.0'
}

dependencies {
    implementation "io.github.resilience4j:resilience4j-spring-boot2:${resilience4jVersion}"
    implementation "io.github.resilience4j:resilience4j-reactor:${resilience4jVersion}"
    implementation "org.springframework.boot:spring-boot-starter-aop"
    implementation "org.springframework.boot:spring-boot-starter-actuator"
}
```

### 2. Circuit Breaker Pattern

#### Basic Usage
Apply `@CircuitBreaker` annotation to methods calling external services:

```java
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.springframework.stereotype.Service;

@Service
public class PaymentService {
    
    private final RestTemplate restTemplate;
    
    public PaymentService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    @CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
    public PaymentResponse processPayment(PaymentRequest request) {
        return restTemplate.postForObject(
            "http://payment-api/process", 
            request, 
            PaymentResponse.class
        );
    }
    
    private PaymentResponse paymentFallback(PaymentRequest request, Exception ex) {
        return PaymentResponse.builder()
            .status("PENDING")
            .message("Payment service temporarily unavailable")
            .build();
    }
}
```

#### Configuration in application.yml

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        registerHealthIndicator: true
        slidingWindowSize: 10
        minimumNumberOfCalls: 5
        failureRateThreshold: 50
        waitDurationInOpenState: 10s
        permittedNumberOfCallsInHalfOpenState: 3
        slowCallDurationThreshold: 4s
        slowCallRateThreshold: 50
        slidingWindowType: COUNT_BASED
        automaticTransitionFromOpenToHalfOpenEnabled: true
    instances:
      paymentService:
        baseConfig: default
        waitDurationInOpenState: 20s
      userService:
        baseConfig: default
        failureRateThreshold: 60
```

### 3. Retry Pattern

#### Basic Usage

```java
import io.github.resilience4j.retry.annotation.Retry;

@Service
public class ProductService {
    
    private final RestTemplate restTemplate;
    
    public ProductService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    @Retry(name = "productService", fallbackMethod = "getProductFallback")
    public Product getProduct(Long productId) {
        return restTemplate.getForObject(
            "http://product-api/products/" + productId,
            Product.class
        );
    }
    
    private Product getProductFallback(Long productId, Exception ex) {
        return Product.builder()
            .id(productId)
            .name("Product temporarily unavailable")
            .available(false)
            .build();
    }
}
```

#### Configuration

```yaml
resilience4j:
  retry:
    configs:
      default:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        retryExceptions:
          - java.io.IOException
          - org.springframework.web.client.ResourceAccessException
        ignoreExceptions:
          - java.lang.IllegalArgumentException
    instances:
      productService:
        baseConfig: default
        maxAttempts: 5
        waitDuration: 1s
```

### 4. Rate Limiter Pattern

#### Basic Usage

```java
import io.github.resilience4j.ratelimiter.annotation.RateLimiter;

@Service
public class NotificationService {
    
    private final EmailClient emailClient;
    
    public NotificationService(EmailClient emailClient) {
        this.emailClient = emailClient;
    }
    
    @RateLimiter(name = "notificationService", fallbackMethod = "rateLimitFallback")
    public void sendEmail(EmailRequest request) {
        emailClient.send(request);
    }
    
    private void rateLimitFallback(EmailRequest request, Exception ex) {
        throw new RateLimitExceededException(
            "Too many email requests. Please try again later."
        );
    }
}
```

#### Configuration

```yaml
resilience4j:
  ratelimiter:
    configs:
      default:
        registerHealthIndicator: true
        limitForPeriod: 10
        limitRefreshPeriod: 1s
        timeoutDuration: 500ms
        allowHealthIndicatorToFail: true
    instances:
      notificationService:
        baseConfig: default
        limitForPeriod: 5
        limitRefreshPeriod: 1s
```

### 5. Bulkhead Pattern

#### Semaphore-Based Bulkhead

```java
import io.github.resilience4j.bulkhead.annotation.Bulkhead;

@Service
public class ReportService {
    
    private final ReportGenerator reportGenerator;
    
    public ReportService(ReportGenerator reportGenerator) {
        this.reportGenerator = reportGenerator;
    }
    
    @Bulkhead(name = "reportService", type = Bulkhead.Type.SEMAPHORE)
    public Report generateReport(ReportRequest request) {
        return reportGenerator.generate(request);
    }
}
```

#### Thread Pool-Based Bulkhead

```java
@Service
public class AnalyticsService {
    
    private final AnalyticsEngine analyticsEngine;
    
    public AnalyticsService(AnalyticsEngine analyticsEngine) {
        this.analyticsEngine = analyticsEngine;
    }
    
    @Bulkhead(name = "analyticsService", type = Bulkhead.Type.THREADPOOL)
    public CompletableFuture<AnalyticsResult> runAnalytics(AnalyticsRequest request) {
        return CompletableFuture.supplyAsync(() -> 
            analyticsEngine.analyze(request)
        );
    }
}
```

#### Configuration

```yaml
resilience4j:
  bulkhead:
    configs:
      default:
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms
    instances:
      reportService:
        baseConfig: default
        maxConcurrentCalls: 5
  
  thread-pool-bulkhead:
    configs:
      default:
        maxThreadPoolSize: 4
        coreThreadPoolSize: 2
        queueCapacity: 100
        keepAliveDuration: 20ms
    instances:
      analyticsService:
        baseConfig: default
        maxThreadPoolSize: 8
```

### 6. Time Limiter Pattern

#### Basic Usage

```java
import io.github.resilience4j.timelimiter.annotation.TimeLimiter;
import java.util.concurrent.CompletableFuture;

@Service
public class SearchService {
    
    private final SearchEngine searchEngine;
    
    public SearchService(SearchEngine searchEngine) {
        this.searchEngine = searchEngine;
    }
    
    @TimeLimiter(name = "searchService", fallbackMethod = "searchFallback")
    public CompletableFuture<SearchResults> search(SearchQuery query) {
        return CompletableFuture.supplyAsync(() -> 
            searchEngine.executeSearch(query)
        );
    }
    
    private CompletableFuture<SearchResults> searchFallback(
            SearchQuery query, Exception ex) {
        return CompletableFuture.completedFuture(
            SearchResults.empty("Search timed out")
        );
    }
}
```

#### Configuration

```yaml
resilience4j:
  timelimiter:
    configs:
      default:
        timeoutDuration: 2s
        cancelRunningFuture: true
    instances:
      searchService:
        baseConfig: default
        timeoutDuration: 3s
```

### 7. Combining Multiple Patterns

You can combine multiple patterns for comprehensive resilience:

```java
@Service
public class OrderService {
    
    private final OrderClient orderClient;
    
    public OrderService(OrderClient orderClient) {
        this.orderClient = orderClient;
    }
    
    @CircuitBreaker(name = "orderService")
    @Retry(name = "orderService")
    @RateLimiter(name = "orderService")
    @Bulkhead(name = "orderService")
    public Order createOrder(OrderRequest request) {
        return orderClient.createOrder(request);
    }
}
```

**Order of execution**: Retry → CircuitBreaker → RateLimiter → Bulkhead → Method

### 8. Exception Handling

Create a global exception handler for Resilience4j exceptions:

```java
import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import io.github.resilience4j.ratelimiter.RequestNotPermitted;
import io.github.resilience4j.bulkhead.BulkheadFullException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ResilienceExceptionHandler {
    
    @ExceptionHandler(CallNotPermittedException.class)
    @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
    public ErrorResponse handleCallNotPermitted(CallNotPermittedException ex) {
        return new ErrorResponse(
            "SERVICE_UNAVAILABLE",
            "Service is currently unavailable. Please try again later."
        );
    }
    
    @ExceptionHandler(RequestNotPermitted.class)
    @ResponseStatus(HttpStatus.TOO_MANY_REQUESTS)
    public ErrorResponse handleRequestNotPermitted(RequestNotPermitted ex) {
        return new ErrorResponse(
            "TOO_MANY_REQUESTS",
            "Too many requests. Please slow down."
        );
    }
    
    @ExceptionHandler(BulkheadFullException.class)
    @ResponseStatus(HttpStatus.BANDWIDTH_LIMIT_EXCEEDED)
    public ErrorResponse handleBulkheadFull(BulkheadFullException ex) {
        return new ErrorResponse(
            "CAPACITY_EXCEEDED",
            "Service capacity exceeded. Please try again later."
        );
    }
    
    @ExceptionHandler(TimeoutException.class)
    @ResponseStatus(HttpStatus.REQUEST_TIMEOUT)
    public ErrorResponse handleTimeout(TimeoutException ex) {
        return new ErrorResponse(
            "TIMEOUT",
            "Request timed out. Please try again."
        );
    }
}
```

### 9. Monitoring with Actuator

Enable actuator endpoints for monitoring in `application.yml`:

```yaml
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
  metrics:
    enabled: true
```

Access monitoring endpoints:
- Circuit Breakers: `GET /actuator/circuitbreakers`
- Circuit Breaker Events: `GET /actuator/circuitbreakerevents`
- Retry Events: `GET /actuator/retryevents`
- Rate Limiters: `GET /actuator/ratelimiters`
- Health: `GET /actuator/health`

### 10. Programmatic Configuration

For more control, configure Resilience4j programmatically:

```java
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.time.Duration;

@Configuration
public class ResilienceConfig {
    
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .slowCallRateThreshold(50)
            .waitDurationInOpenState(Duration.ofSeconds(10))
            .slowCallDurationThreshold(Duration.ofSeconds(2))
            .permittedNumberOfCallsInHalfOpenState(3)
            .minimumNumberOfCalls(5)
            .slidingWindowType(CircuitBreakerConfig.SlidingWindowType.COUNT_BASED)
            .slidingWindowSize(10)
            .recordExceptions(IOException.class, TimeoutException.class)
            .ignoreExceptions(IllegalArgumentException.class)
            .build();
            
        return CircuitBreakerRegistry.of(config);
    }
}
```

## Best Practices

### Circuit Breaker
1. **Choose appropriate thresholds**: Set `failureRateThreshold` based on acceptable error rates (typically 50-70%)
2. **Configure sliding window**: Use `COUNT_BASED` for low traffic, `TIME_BASED` for high traffic
3. **Set wait duration wisely**: Allow enough time for services to recover (10-60 seconds)
4. **Always provide fallbacks**: Ensure graceful degradation with meaningful fallback responses
5. **Monitor state transitions**: Track circuit state changes for operational insights

### Retry
1. **Use exponential backoff**: Prevent overwhelming recovering services
2. **Limit retry attempts**: Typically 3-5 attempts is sufficient
3. **Retry only transient errors**: Use `retryExceptions` to specify retryable exceptions
4. **Avoid retrying client errors**: Don't retry 4xx errors, only 5xx and network errors
5. **Combine with circuit breaker**: Prevent unnecessary retries when service is down

### Rate Limiter
1. **Set realistic limits**: Base limits on actual service capacity
2. **Use appropriate refresh periods**: Match your service's natural rhythm (1s-1min)
3. **Configure timeout duration**: Allow requests to wait briefly for permits
4. **Provide clear error messages**: Help clients understand rate limiting
5. **Monitor rate limiter metrics**: Track rejected requests and adjust limits

### Bulkhead
1. **Choose correct bulkhead type**: Semaphore for sync calls, ThreadPool for async
2. **Size appropriately**: Calculate based on expected concurrent load
3. **Set reasonable wait durations**: Avoid long waits that block threads
4. **Use with circuit breaker**: Prevent resource exhaustion during failures
5. **Monitor queue saturation**: Track bulkhead fullness for capacity planning

### Time Limiter
1. **Set realistic timeouts**: Based on P99 latency of your services
2. **Always cancel futures**: Set `cancelRunningFuture: true` to free resources
3. **Use with async methods**: Only works with CompletableFuture or reactive types
4. **Provide timeout fallbacks**: Return meaningful responses on timeout
5. **Consider downstream timeouts**: Ensure timeouts align across service chains

### General
1. **Use constructor injection**: Never field injection for Resilience4j dependencies
2. **Test resilience patterns**: Simulate failures in integration tests
3. **Configure health indicators**: Enable monitoring for all patterns
4. **Use meaningful instance names**: Name instances after services they protect
5. **Document fallback behavior**: Make fallback logic clear and predictable
6. **Combine patterns strategically**: Use multiple patterns together for comprehensive resilience
7. **Monitor and tune**: Continuously adjust configurations based on production metrics
8. **Handle exceptions globally**: Use @ControllerAdvice for consistent error responses

## Testing Resilience Patterns

### Circuit Breaker Testing

```java
@SpringBootTest
class PaymentServiceTest {
    
    @Autowired
    private PaymentService paymentService;
    
    @MockBean
    private RestTemplate restTemplate;
    
    @Test
    void shouldOpenCircuitAfterFailureThreshold() {
        // Simulate failures
        when(restTemplate.postForObject(anyString(), any(), eq(PaymentResponse.class)))
            .thenThrow(new HttpServerErrorException(HttpStatus.INTERNAL_SERVER_ERROR));
        
        // Trigger circuit breaker
        for (int i = 0; i < 5; i++) {
            assertThatThrownBy(() -> paymentService.processPayment(new PaymentRequest()))
                .isInstanceOf(HttpServerErrorException.class);
        }
        
        // Circuit should be open, fallback should execute
        PaymentResponse response = paymentService.processPayment(new PaymentRequest());
        assertThat(response.getStatus()).isEqualTo("PENDING");
    }
}
```

### Integration Testing with WireMock

```java
@SpringBootTest
@AutoConfigureWireMock(port = 0)
class OrderServiceIntegrationTest {
    
    @Autowired
    private OrderService orderService;
    
    @Test
    void shouldRetryOnTransientFailure() {
        // First two calls fail, third succeeds
        stubFor(post("/orders")
            .inScenario("Retry")
            .whenScenarioStateIs(STARTED)
            .willReturn(serverError())
            .willSetStateTo("First Retry"));
            
        stubFor(post("/orders")
            .inScenario("Retry")
            .whenScenarioStateIs("First Retry")
            .willReturn(serverError())
            .willSetStateTo("Second Retry"));
            
        stubFor(post("/orders")
            .inScenario("Retry")
            .whenScenarioStateIs("Second Retry")
            .willReturn(ok().withBody("{\"id\":1,\"status\":\"CREATED\"}")));
        
        Order order = orderService.createOrder(new OrderRequest());
        assertThat(order.getId()).isEqualTo(1L);
        
        // Verify exactly 3 calls were made
        verify(exactly(3), postRequestedFor(urlEqualTo("/orders")));
    }
}
```

## Common Pitfalls

1. **Not providing fallback methods**: Always implement fallbacks for better user experience
2. **Incorrect fallback signatures**: Fallback methods must match original method signature plus Exception parameter
3. **Blocking in reactive code**: Don't use blocking calls within reactive patterns
4. **Misconfigured sliding windows**: Too small windows cause premature circuit opening
5. **Ignoring metrics**: Not monitoring pattern effectiveness leads to poor tuning
6. **Over-aggressive timeouts**: Too short timeouts cause unnecessary failures
7. **Missing AOP dependency**: Annotations won't work without spring-boot-starter-aop
8. **Combining conflicting patterns**: Be careful when stacking multiple patterns

## References

- @reference.md - Comprehensive configuration reference and API details
- @examples.md - Real-world examples and advanced use cases
- [Resilience4j Documentation](https://resilience4j.readme.io/)
- [Spring Boot Actuator](/skills/spring-boot-actuator/SKILL.md)
- [Spring Boot Test Patterns](/skills/spring-boot-test-patterns/SKILL.md)
