# Error Handling and Exception Management

Apache Camel provides comprehensive error handling capabilities to build resilient integration solutions. This reference covers error handling strategies, retry policies, and dead letter channels.

## Error Handler Types

### 1. DefaultErrorHandler

The default error handler used by Camel routes. Supports redelivery and basic error handling.

```java
from("direct:start")
    .errorHandler(defaultErrorHandler()
        .maximumRedeliveries(3)
        .redeliveryDelay(1000)
        .retryAttemptedLogLevel(LoggingLevel.WARN))
    .to("http://unreliable-service");
```

### 2. Dead Letter Channel

Routes failed messages to a dead letter queue/endpoint after exhausting retries.

```java
from("jms:queue:orders")
    .errorHandler(deadLetterChannel("jms:queue:dead-letter")
        .maximumRedeliveries(3)
        .redeliveryDelay(2000)
        .logStackTrace(true)
        .useOriginalMessage())
    .to("direct:process-order");
```

### 3. No Error Handler

Disables error handling, allowing exceptions to propagate.

```java
from("direct:no-retry")
    .errorHandler(noErrorHandler())
    .to("http://external-service");
```

### 4. Logging Error Handler

Logs errors without redelivery attempts.

```java
from("direct:log-only")
    .errorHandler(loggingErrorHandler())
    .to("http://service");
```

## Redelivery Policies

### Basic Redelivery

```java
errorHandler(defaultErrorHandler()
    .maximumRedeliveries(5)
    .redeliveryDelay(1000));
```

### Exponential Backoff

```java
errorHandler(defaultErrorHandler()
    .maximumRedeliveries(5)
    .redeliveryDelay(1000)
    .backOffMultiplier(2.0)
    .maximumRedeliveryDelay(60000)); // Cap at 60 seconds
```

**Retry delays:** 1s → 2s → 4s → 8s → 16s → 32s (capped at 60s)

### Custom Redelivery Delay Pattern

```java
errorHandler(defaultErrorHandler()
    .maximumRedeliveries(4)
    .delayPattern("1000:5000;3000:10000")); // 1s for first 5 attempts, then 3s for next 10
```

### Conditional Redelivery

```java
errorHandler(defaultErrorHandler()
    .maximumRedeliveries(3)
    .retryWhile(simple("${header.retryCount} < 5"))
    .redeliveryDelay(2000));
```

### Async Delayed Redelivery

Frees up thread during retry delay.

```java
errorHandler(defaultErrorHandler()
    .maximumRedeliveries(3)
    .redeliveryDelay(5000)
    .asyncDelayedRedelivery()); // Non-blocking delay
```

## Exception Handling with onException

### Basic Exception Handling

```java
onException(IOException.class)
    .handled(true)
    .log("IO Exception occurred: ${exception.message}")
    .to("jms:queue:io-errors");

onException(ValidationException.class)
    .handled(true)
    .setHeader("error", simple("${exception.message}"))
    .to("direct:validation-error-handler");

from("jms:queue:orders")
    .to("direct:process-order");
```

### Exception Hierarchy

More specific exceptions should be defined first.

```java
onException(FileNotFoundException.class)
    .handled(true)
    .log("File not found: ${exception.message}")
    .to("direct:file-not-found");

onException(IOException.class)
    .handled(true)
    .log("IO error: ${exception.message}")
    .to("direct:io-error");

onException(Exception.class)
    .handled(true)
    .log("General error: ${exception.message}")
    .to("jms:queue:errors");
```

### Retry Specific Exceptions

```java
onException(HttpOperationFailedException.class)
    .handled(true)
    .maximumRedeliveries(5)
    .redeliveryDelay(2000)
    .backOffMultiplier(2)
    .retryAttemptedLogLevel(LoggingLevel.WARN)
    .retriesExhaustedLogLevel(LoggingLevel.ERROR)
    .to("jms:queue:http-failures");
```

### Conditional Exception Handling

```java
onException(HttpOperationFailedException.class)
    .onWhen(simple("${exception.statusCode} == 503"))
    .maximumRedeliveries(3)
    .redeliveryDelay(5000)
    .to("direct:retry-later");

onException(HttpOperationFailedException.class)
    .onWhen(simple("${exception.statusCode} >= 400 && ${exception.statusCode} < 500"))
    .handled(true)
    .to("jms:queue:client-errors");
```

### Access Original Exception

```java
onException(Exception.class)
    .handled(true)
    .process(exchange -> {
        Exception cause = exchange.getProperty(Exchange.EXCEPTION_CAUGHT, Exception.class);
        log.error("Error processing message", cause);
        exchange.getIn().setBody("Error: " + cause.getMessage());
    })
    .to("jms:queue:errors");
```

## DoTry-DoCatch-DoFinally

Inline exception handling within routes, similar to try-catch blocks.

### Basic Try-Catch

```java
from("direct:start")
    .doTry()
        .to("http://unreliable-service")
        .to("direct:success")
    .doCatch(HttpOperationFailedException.class)
        .log("HTTP error: ${exception.message}")
        .to("direct:http-error")
    .doCatch(Exception.class)
        .log("General error: ${exception.message}")
        .to("direct:general-error")
    .doFinally()
        .log("Processing completed")
    .end();
```

### Try-Catch with Conditional Logic

```java
from("direct:process")
    .doTry()
        .to("http://external-api")
        .choice()
            .when(simple("${body.status} == 'success'"))
                .to("direct:success")
            .otherwise()
                .to("direct:warning")
        .end()
    .doCatch(SocketTimeoutException.class)
        .log("Timeout occurred, using cached data")
        .to("direct:cache-lookup")
    .doCatch(Exception.class)
        .log("Error: ${exception.message}")
        .to("direct:error-handler")
    .doFinally()
        .to("direct:cleanup")
    .end();
```

### Nested Try-Catch

```java
from("direct:complex")
    .doTry()
        .to("direct:step1")
        .doTry()
            .to("http://api")
        .doCatch(HttpOperationFailedException.class)
            .to("direct:fallback-api")
        .end()
        .to("direct:step2")
    .doCatch(Exception.class)
        .to("direct:global-error")
    .doFinally()
        .to("direct:audit")
    .end();
```

## Advanced Error Handling Patterns

### Circuit Breaker

Prevent cascading failures by breaking the circuit after threshold failures.

**Using Resilience4j:**

```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-resilience4j-starter</artifactId>
</dependency>
```

```java
from("direct:protected")
    .circuitBreaker()
        .resilience4jConfiguration()
            .failureRateThreshold(50)
            .waitDurationInOpenState(10000)
            .slidingWindowSize(10)
        .end()
        .to("http://unreliable-service")
    .onFallback()
        .log("Circuit breaker activated, using fallback")
        .setBody(constant("Service temporarily unavailable"))
    .end();
```

### Timeout Handling

```java
from("direct:timed")
    .circuitBreaker()
        .resilience4jConfiguration()
            .timeoutEnabled(true)
            .timeoutDuration(5000)
        .end()
        .to("http://slow-service")
    .onFallback()
        .log("Timeout occurred")
        .to("direct:timeout-handler")
    .end();
```

### Bulkhead Pattern

Limit concurrent calls to prevent resource exhaustion.

```java
from("direct:limited")
    .circuitBreaker()
        .resilience4jConfiguration()
            .bulkheadEnabled(true)
            .bulkheadMaxConcurrentCalls(10)
        .end()
        .to("http://resource-intensive-service")
    .end();
```

### Custom Error Response

```java
onException(ValidationException.class)
    .handled(true)
    .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(400))
    .setHeader(Exchange.CONTENT_TYPE, constant("application/json"))
    .transform()
        .simple("{ \"error\": \"${exception.message}\", \"timestamp\": \"${date:now:ISO_8601}\" }");
```

### Rollback Transaction on Error

```java
onException(Exception.class)
    .handled(true)
    .markRollbackOnly()
    .to("jms:queue:rollback-notifications");

from("jms:queue:orders?transacted=true")
    .transacted()
    .to("sql:INSERT INTO orders...")
    .to("jms:queue:order-notifications");
```

## Error Handling Best Practices

### 1. Use Dead Letter Channels

Always configure a dead letter channel for critical routes.

```java
@Configuration
public class ErrorHandlingConfig {

    @Bean
    public RouteBuilder errorHandlerRoute() {
        return new RouteBuilder() {
            @Override
            public void configure() {
                errorHandler(deadLetterChannel("direct:dead-letter")
                    .maximumRedeliveries(3)
                    .redeliveryDelay(2000)
                    .backOffMultiplier(2)
                    .useOriginalMessage()
                    .logExhausted(true)
                    .logRetryAttempted(true));
            }
        };
    }
}
```

### 2. Preserve Original Message

```java
errorHandler(deadLetterChannel("jms:queue:DLQ")
    .useOriginalMessage() // Preserve original message before transformations
    .logStackTrace(true));
```

### 3. Add Error Metadata

```java
onException(Exception.class)
    .handled(true)
    .process(exchange -> {
        Exception cause = exchange.getProperty(Exchange.EXCEPTION_CAUGHT, Exception.class);
        exchange.getIn().setHeader("error.message", cause.getMessage());
        exchange.getIn().setHeader("error.class", cause.getClass().getName());
        exchange.getIn().setHeader("error.timestamp", System.currentTimeMillis());
        exchange.getIn().setHeader("error.routeId", exchange.getFromRouteId());
    })
    .to("jms:queue:errors");
```

### 4. Implement Alerting

```java
onException(CriticalException.class)
    .handled(true)
    .to("direct:send-alert")
    .to("jms:queue:critical-errors");

from("direct:send-alert")
    .setHeader("subject", constant("Critical Error in Integration Service"))
    .setBody(simple("Error: ${exception.message}\nRoute: ${routeId}"))
    .to("smtp://alert@example.com");
```

### 5. Separate Error Handling Routes

```java
@Component
public class MainRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("jms:queue:orders")
            .to("direct:process-order");
    }
}

@Component
public class ErrorHandlingRoute extends RouteBuilder {
    @Override
    public void configure() {
        onException(ValidationException.class)
            .handled(true)
            .to("direct:validation-error");

        onException(Exception.class)
            .handled(true)
            .to("direct:general-error");

        from("direct:validation-error")
            .log("Validation error: ${exception.message}")
            .to("jms:queue:validation-errors");

        from("direct:general-error")
            .log("General error: ${exception.message}")
            .to("jms:queue:general-errors");
    }
}
```

## Testing Error Handling

### Simulate Failures

```java
@CamelSpringBootTest
@SpringBootTest
class ErrorHandlingTest {

    @Produce("direct:start")
    ProducerTemplate producer;

    @EndpointInject("mock:error")
    MockEndpoint errorEndpoint;

    @Test
    void testErrorHandling() throws Exception {
        errorEndpoint.expectedMessageCount(1);
        errorEndpoint.expectedHeaderReceived("error.message", "Simulated failure");

        producer.sendBody("test message");

        errorEndpoint.assertIsSatisfied();
    }
}
```

### Mock Endpoints for Testing

```java
@Override
public void configure() {
    onException(Exception.class)
        .handled(true)
        .to("mock:error");

    from("direct:start")
        .process(exchange -> {
            throw new Exception("Simulated failure");
        });
}
```

## Common Error Scenarios

### HTTP Service Failures

```java
onException(HttpOperationFailedException.class)
    .onWhen(simple("${exception.statusCode} == 429")) // Rate limit
    .maximumRedeliveries(5)
    .redeliveryDelay(60000); // Wait 1 minute

onException(HttpOperationFailedException.class)
    .onWhen(simple("${exception.statusCode} >= 500")) // Server errors
    .maximumRedeliveries(3)
    .redeliveryDelay(5000)
    .backOffMultiplier(2);

onException(HttpOperationFailedException.class)
    .onWhen(simple("${exception.statusCode} >= 400 && ${exception.statusCode} < 500")) // Client errors
    .handled(true)
    .to("direct:client-error-handler");
```

### Database Connection Failures

```java
onException(SQLException.class)
    .maximumRedeliveries(3)
    .redeliveryDelay(10000)
    .onRedelivery(exchange -> {
        log.warn("Retrying database operation, attempt: {}",
            exchange.getIn().getHeader(Exchange.REDELIVERY_COUNTER));
    })
    .to("direct:db-error");
```

### Message Parsing Failures

```java
onException(JsonProcessingException.class, MarshalException.class)
    .handled(true)
    .log(LoggingLevel.ERROR, "Failed to parse message: ${exception.message}")
    .setBody(simple("${body}")) // Keep original body
    .to("jms:queue:parse-errors");
```

## Monitoring Failed Messages

### Track Error Metrics

```java
onException(Exception.class)
    .handled(true)
    .to("micrometer:counter:errors.total?tags=route=${routeId}")
    .to("direct:error-handler");
```

### Error Dashboard Route

```java
from("timer:errorStats?period=60000")
    .to("sql:SELECT route_id, COUNT(*) as error_count FROM error_log WHERE timestamp > ? GROUP BY route_id:#${date:now-1h}")
    .log("Error statistics: ${body}")
    .to("direct:metrics-aggregator");
```

## References

- [Camel Error Handling](https://camel.apache.org/manual/error-handler.html)
- [Exception Clause](https://camel.apache.org/components/latest/eips/onException-eip.html)
- [Circuit Breaker](https://camel.apache.org/components/latest/eips/circuitBreaker-eip.html)
- [Dead Letter Channel](https://camel.apache.org/components/latest/eips/dead-letter-channel.html)
