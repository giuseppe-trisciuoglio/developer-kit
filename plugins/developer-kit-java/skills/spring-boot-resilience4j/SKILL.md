---
name: spring-boot-resilience4j
description: This skill should be used when implementing fault tolerance and resilience patterns in Spring Boot applications using the Resilience4j library. Apply this skill to add circuit breaker, retry, rate limiter, bulkhead, time limiter, and fallback mechanisms to prevent cascading failures, handle transient errors, and manage external service dependencies gracefully in microservices architectures.
allowed-tools: Read, Write, Edit, Bash
category: backend
tags: [spring-boot, resilience4j, circuit-breaker, fault-tolerance, retry, bulkhead, rate-limiter]
version: 2.2.0
---

# Spring Boot Resilience4j Patterns

## Overview

Resilience4j is a lightweight fault tolerance library for Java 8+ providing circuit breakers, rate limiters, retry mechanisms, bulkheads, and time limiters. This skill covers integrating Resilience4j with Spring Boot 3.x to build resilient microservices.

## When to Use

- Preventing cascading failures with circuit breaker pattern
- Retrying transient failures with exponential backoff
- Rate limiting to protect from overload
- Isolating resources with bulkhead pattern
- Adding timeout controls with time limiter
- Combining multiple patterns for comprehensive fault tolerance

## Instructions

### 1. Setup Dependencies

```xml
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot3</artifactId>
    <version>2.2.0</version>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

### 2. Circuit Breaker

```java
@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
public PaymentResponse processPayment(PaymentRequest request) {
    return restTemplate.postForObject("http://payment-api/process", request, PaymentResponse.class);
}

private PaymentResponse paymentFallback(PaymentRequest request, Exception ex) {
    return PaymentResponse.builder().status("PENDING").message("Service unavailable").build();
}
```

### 3. Retry

```java
@Retry(name = "productService", fallbackMethod = "getProductFallback")
public Product getProduct(Long productId) {
    return restTemplate.getForObject("http://product-api/products/" + productId, Product.class);
}
```

### 4. Rate Limiter

```java
@RateLimiter(name = "notificationService", fallbackMethod = "rateLimitFallback")
public void sendEmail(EmailRequest request) { emailClient.send(request); }
```

### 5. Bulkhead

```java
@Bulkhead(name = "reportService", type = Bulkhead.Type.SEMAPHORE)
public Report generateReport(ReportRequest request) {
    return reportGenerator.generate(request);
}
```

### 6. Time Limiter

```java
@TimeLimiter(name = "searchService", fallbackMethod = "searchFallback")
public CompletableFuture<SearchResults> search(SearchQuery query) {
    return CompletableFuture.supplyAsync(() -> searchEngine.executeSearch(query));
}
```

### 7. Combining Patterns

```java
@CircuitBreaker(name = "orderService")
@Retry(name = "orderService")
@RateLimiter(name = "orderService")
@Bulkhead(name = "orderService")
public Order createOrder(OrderRequest request) {
    return orderClient.createOrder(request);
}
```

Execution order: Retry -> CircuitBreaker -> RateLimiter -> Bulkhead -> Method

## Examples

### Configuration

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
  retry:
    configs:
      default:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
  ratelimiter:
    configs:
      default:
        limitForPeriod: 10
        limitRefreshPeriod: 1s
        timeoutDuration: 500ms
  timelimiter:
    configs:
      default:
        timeoutDuration: 2s
```

### Exception Handling

```java
@RestControllerAdvice
public class ResilienceExceptionHandler {
    @ExceptionHandler(CallNotPermittedException.class)
    @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
    public ErrorResponse handleCircuitOpen(CallNotPermittedException ex) {
        return new ErrorResponse("SERVICE_UNAVAILABLE", "Service currently unavailable");
    }

    @ExceptionHandler(RequestNotPermitted.class)
    @ResponseStatus(HttpStatus.TOO_MANY_REQUESTS)
    public ErrorResponse handleRateLimited(RequestNotPermitted ex) {
        return new ErrorResponse("TOO_MANY_REQUESTS", "Rate limit exceeded");
    }
}
```

## Best Practices

- **Always provide fallback methods** with meaningful responses
- **Use exponential backoff** for retries (multiplier: 2)
- **Set failure threshold** between 50-70%
- **Use constructor injection** exclusively
- **Enable health indicators** for all patterns
- **Retry only transient errors** (5xx, network timeouts); skip 4xx
- **Monitor and adjust** based on production behavior

## Constraints and Warnings

- Fallback methods must have the same signature plus optional Exception parameter
- Retry operations should be idempotent (may execute multiple times)
- Do not use circuit breakers for operations that must always complete
- Rate limiters can cause thread blocking; configure appropriate wait durations
- Be cautious with @Retry on non-idempotent POST requests

## References

- [Configuration Reference](references/configuration-reference.md)
- [Testing Patterns](references/testing-patterns.md)
- [Examples](references/examples.md)
- [Resilience4j Documentation](https://resilience4j.readme.io/)
