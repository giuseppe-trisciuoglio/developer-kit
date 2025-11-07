# Complete Implementation Examples

This document provides complete, production-ready examples of common Camel integration patterns with Spring Boot.

## Example 1: Order Processing Microservice

Complete order processing service with REST API, Kafka integration, database persistence, and error handling.

### Dependencies

```xml
<dependencies>
    <!-- Camel -->
    <dependency>
        <groupId>org.apache.camel.springboot</groupId>
        <artifactId>camel-spring-boot-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.camel.springboot</groupId>
        <artifactId>camel-servlet-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.camel.springboot</groupId>
        <artifactId>camel-jackson-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.camel.springboot</groupId>
        <artifactId>camel-kafka-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.camel.springboot</groupId>
        <artifactId>camel-jpa-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.camel.springboot</groupId>
        <artifactId>camel-bean-validator-starter</artifactId>
    </dependency>
</dependencies>
```

### Domain Model

```java
@Entity
@Table(name = "orders")
public class Order {

    @Id
    private String id;

    private String customerId;
    private Double amount;
    private String status;

    @Enumerated(EnumType.STRING)
    private OrderPriority priority;

    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @NotNull
    @DecimalMin("0.01")
    private Double amount;

    @NotNull
    @Pattern(regexp = "^[A-Z0-9]{5,10}$")
    private String customerId;

    // Getters and setters
}

enum OrderPriority {
    LOW, NORMAL, HIGH, URGENT
}
```

### REST API Route

```java
@Component
public class OrderApiRoute extends RouteBuilder {

    @Override
    public void configure() {
        restConfiguration()
            .component("servlet")
            .bindingMode(RestBindingMode.json)
            .dataFormatProperty("prettyPrint", "true")
            .contextPath("/api")
            .apiContextPath("/api-doc")
            .apiProperty("api.title", "Order Management API")
            .apiProperty("api.version", "1.0");

        rest("/orders")
            .description("Order management endpoints")

            .post()
                .description("Create new order")
                .type(Order.class)
                .outType(Order.class)
                .to("direct:create-order")

            .get("/{id}")
                .description("Get order by ID")
                .outType(Order.class)
                .to("direct:get-order")

            .get()
                .description("List all orders")
                .outType(Order[].class)
                .to("direct:list-orders")

            .put("/{id}")
                .description("Update order")
                .type(Order.class)
                .outType(Order.class)
                .to("direct:update-order")

            .delete("/{id}")
                .description("Delete order")
                .to("direct:delete-order");
    }
}
```

### Order Processing Routes

```java
@Component
public class OrderProcessingRoute extends RouteBuilder {

    @Override
    public void configure() {
        onException(ValidationException.class)
            .handled(true)
            .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(400))
            .setHeader(Exchange.CONTENT_TYPE, constant("application/json"))
            .transform()
                .simple("{\"error\":\"${exception.message}\"}");

        onException(EntityNotFoundException.class)
            .handled(true)
            .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(404))
            .setHeader(Exchange.CONTENT_TYPE, constant("application/json"))
            .transform()
                .simple("{\"error\":\"Order not found\"}");

        onException(Exception.class)
            .handled(true)
            .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(500))
            .setHeader(Exchange.CONTENT_TYPE, constant("application/json"))
            .transform()
                .simple("{\"error\":\"Internal server error\"}");

        // Create order
        from("direct:create-order")
            .routeId("create-order")
            .log("Creating order: ${body}")
            .to("bean-validator://validate")
            .setHeader("orderId", simple("${body.id}"))
            .to("jpa:com.example.model.Order")
            .to("direct:publish-order-event")
            .to("direct:route-order");

        // Route order based on priority
        from("direct:route-order")
            .routeId("route-order")
            .choice()
                .when(simple("${body.priority} == 'URGENT'"))
                    .to("kafka:urgent-orders")
                .when(simple("${body.priority} == 'HIGH'"))
                    .to("kafka:high-priority-orders")
                .otherwise()
                    .to("kafka:standard-orders")
            .end();

        // Get order
        from("direct:get-order")
            .routeId("get-order")
            .to("jpa:com.example.model.Order?query=SELECT o FROM Order o WHERE o.id = ${header.id}")
            .choice()
                .when(simple("${body.size()} == 0"))
                    .throwException(EntityNotFoundException.class, "Order not found")
                .otherwise()
                    .transform(simple("${body[0]}"))
            .end();

        // List orders
        from("direct:list-orders")
            .routeId("list-orders")
            .to("jpa:com.example.model.Order?query=SELECT o FROM Order o");

        // Update order
        from("direct:update-order")
            .routeId("update-order")
            .to("bean-validator://validate")
            .to("jpa:com.example.model.Order")
            .to("direct:publish-order-event");

        // Delete order
        from("direct:delete-order")
            .routeId("delete-order")
            .setBody(simple("DELETE FROM Order WHERE id = '${header.id}'"))
            .to("jpa:com.example.model.Order")
            .setBody(constant("{\"status\":\"deleted\"}"));

        // Publish order events to Kafka
        from("direct:publish-order-event")
            .routeId("publish-order-event")
            .marshal().json()
            .setHeader(KafkaConstants.KEY, simple("${body.id}"))
            .to("kafka:order-events");
    }
}
```

### Configuration

```yaml
spring:
  application:
    name: order-service
  datasource:
    url: jdbc:postgresql://localhost:5432/orders
    username: postgres
    password: secret
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false

camel:
  component:
    kafka:
      brokers: localhost:9092
    servlet:
      mapping:
        context-path: /api/*

management:
  endpoints:
    web:
      exposure:
        include: health,metrics,camelroutes
```

## Example 2: File-Based ETL Pipeline

Extract data from CSV files, transform, and load into database with error handling and audit logging.

### Route Implementation

```java
@Component
public class EtlPipelineRoute extends RouteBuilder {

    @Override
    public void configure() {
        // Error handling
        errorHandler(deadLetterChannel("direct:failed-files")
            .maximumRedeliveries(3)
            .redeliveryDelay(5000)
            .useOriginalMessage());

        onException(Exception.class)
            .handled(false)
            .to("direct:log-error")
            .to("file:/data/error?fileName=${header.CamelFileName}.error");

        // Main ETL pipeline
        from("file:/data/input?move=.processed&moveFailed=.failed&include=.*\\.csv$")
            .routeId("csv-etl-pipeline")
            .log("Processing file: ${header.CamelFileName}")
            .to("direct:audit-start")
            .unmarshal().csv()
            .split(body())
                .streaming()
                .parallelProcessing()
                .to("direct:transform-row")
                .to("direct:validate-row")
                .to("direct:load-row")
            .end()
            .to("direct:audit-complete")
            .log("Completed processing: ${header.CamelFileName}");

        // Transform CSV row to domain object
        from("direct:transform-row")
            .routeId("transform-row")
            .process(exchange -> {
                @SuppressWarnings("unchecked")
                List<String> row = exchange.getIn().getBody(List.class);

                Customer customer = new Customer();
                customer.setId(row.get(0));
                customer.setName(row.get(1));
                customer.setEmail(row.get(2));
                customer.setPhone(row.get(3));

                exchange.getIn().setBody(customer);
            });

        // Validate row
        from("direct:validate-row")
            .routeId("validate-row")
            .to("bean-validator://validate");

        // Load into database
        from("direct:load-row")
            .routeId("load-row")
            .to("jpa:com.example.model.Customer");

        // Audit logging
        from("direct:audit-start")
            .routeId("audit-start")
            .process(exchange -> {
                AuditLog audit = new AuditLog();
                audit.setFileName(exchange.getIn().getHeader(Exchange.FILE_NAME, String.class));
                audit.setStartTime(LocalDateTime.now());
                audit.setStatus("PROCESSING");
                exchange.setProperty("auditLog", audit);
            })
            .to("jpa:com.example.model.AuditLog");

        from("direct:audit-complete")
            .routeId("audit-complete")
            .process(exchange -> {
                AuditLog audit = exchange.getProperty("auditLog", AuditLog.class);
                audit.setEndTime(LocalDateTime.now());
                audit.setStatus("COMPLETED");
            })
            .to("jpa:com.example.model.AuditLog");

        // Error logging
        from("direct:log-error")
            .routeId("log-error")
            .log(LoggingLevel.ERROR, "Error processing file: ${header.CamelFileName} - ${exception.message}")
            .to("sql:INSERT INTO error_log (file_name, error_message, timestamp) VALUES (:#${header.CamelFileName}, :#${exception.message}, :#${date:now})");

        // Failed files handler
        from("direct:failed-files")
            .routeId("failed-files-handler")
            .log("File processing failed after retries: ${header.CamelFileName}")
            .to("file:/data/failed");
    }
}
```

## Example 3: Event-Driven Microservice Integration

Integrate multiple microservices using Kafka event streams with Saga pattern for distributed transactions.

### Saga Orchestrator

```java
@Component
public class OrderSagaRoute extends RouteBuilder {

    @Override
    public void configure() {
        // Saga orchestration
        from("kafka:order-created?groupId=saga-orchestrator")
            .routeId("order-saga-orchestrator")
            .unmarshal().json(JsonLibrary.Jackson, OrderCreatedEvent.class)
            .to("direct:reserve-inventory")
            .to("direct:process-payment")
            .to("direct:ship-order")
            .to("direct:complete-order");

        // Reserve inventory step
        from("direct:reserve-inventory")
            .routeId("reserve-inventory")
            .setHeader("sagaStep", constant("RESERVE_INVENTORY"))
            .marshal().json()
            .to("kafka:inventory-reservation-requests")
            .to("direct:wait-for-inventory-response");

        from("kafka:inventory-reservation-responses?groupId=saga-orchestrator")
            .routeId("inventory-response-handler")
            .choice()
                .when(simple("${body.status} == 'RESERVED'"))
                    .to("direct:inventory-reserved")
                .otherwise()
                    .to("direct:compensate-order")
            .end();

        // Process payment step
        from("direct:process-payment")
            .routeId("process-payment")
            .setHeader("sagaStep", constant("PROCESS_PAYMENT"))
            .marshal().json()
            .to("kafka:payment-requests")
            .to("direct:wait-for-payment-response");

        from("kafka:payment-responses?groupId=saga-orchestrator")
            .routeId("payment-response-handler")
            .choice()
                .when(simple("${body.status} == 'PAID'"))
                    .to("direct:payment-processed")
                .otherwise()
                    .to("direct:compensate-inventory")
                    .to("direct:compensate-order")
            .end();

        // Ship order step
        from("direct:ship-order")
            .routeId("ship-order")
            .setHeader("sagaStep", constant("SHIP_ORDER"))
            .marshal().json()
            .to("kafka:shipping-requests");

        // Complete order
        from("direct:complete-order")
            .routeId("complete-order")
            .process(exchange -> {
                OrderCreatedEvent order = exchange.getIn().getBody(OrderCreatedEvent.class);
                order.setStatus("COMPLETED");
            })
            .marshal().json()
            .to("kafka:order-completed");

        // Compensation routes
        from("direct:compensate-inventory")
            .routeId("compensate-inventory")
            .log("Compensating inventory reservation")
            .to("kafka:inventory-compensation-requests");

        from("direct:compensate-order")
            .routeId("compensate-order")
            .log("Compensating order")
            .process(exchange -> {
                OrderCreatedEvent order = exchange.getIn().getBody(OrderCreatedEvent.class);
                order.setStatus("CANCELLED");
            })
            .marshal().json()
            .to("kafka:order-cancelled");
    }
}
```

## Example 4: API Gateway with Rate Limiting

API gateway that routes requests to multiple backend services with rate limiting, caching, and circuit breakers.

### Gateway Route

```java
@Component
public class ApiGatewayRoute extends RouteBuilder {

    @Override
    public void configure() {
        // Rate limiting using Caffeine cache
        from("servlet:/gateway/*")
            .routeId("api-gateway")
            .to("direct:rate-limit")
            .to("direct:authenticate")
            .to("direct:route-request");

        // Rate limiting
        from("direct:rate-limit")
            .routeId("rate-limiter")
            .process(exchange -> {
                String clientId = exchange.getIn().getHeader("X-Client-ID", String.class);
                if (clientId == null) {
                    throw new UnauthorizedException("Missing client ID");
                }

                // Check rate limit (implement using Caffeine or Redis)
                RateLimiter rateLimiter = exchange.getContext()
                    .getRegistry()
                    .lookupByNameAndType("rateLimiter", RateLimiter.class);

                if (!rateLimiter.tryAcquire(clientId)) {
                    exchange.getIn().setHeader(Exchange.HTTP_RESPONSE_CODE, 429);
                    throw new TooManyRequestsException("Rate limit exceeded");
                }
            });

        // Authentication
        from("direct:authenticate")
            .routeId("authenticator")
            .process(exchange -> {
                String token = exchange.getIn().getHeader("Authorization", String.class);
                if (token == null || !token.startsWith("Bearer ")) {
                    throw new UnauthorizedException("Invalid or missing token");
                }

                // Validate token (JWT validation, etc.)
                String jwt = token.substring(7);
                // ... validation logic
            });

        // Route to backend services
        from("direct:route-request")
            .routeId("request-router")
            .choice()
                .when(header(Exchange.HTTP_PATH).startsWith("/users"))
                    .to("direct:user-service")
                .when(header(Exchange.HTTP_PATH).startsWith("/orders"))
                    .to("direct:order-service")
                .when(header(Exchange.HTTP_PATH).startsWith("/products"))
                    .to("direct:product-service")
                .otherwise()
                    .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(404))
                    .setBody(constant("{\"error\":\"Not found\"}"))
            .end();

        // User service with circuit breaker and caching
        from("direct:user-service")
            .routeId("user-service-proxy")
            .circuitBreaker()
                .resilience4jConfiguration()
                    .failureRateThreshold(50)
                    .waitDurationInOpenState(10000)
                    .slidingWindowSize(10)
                .end()
                .to("direct:check-cache")
                .choice()
                    .when(header("CacheHit").isEqualTo(true))
                        .log("Cache hit for ${header.CamelHttpPath}")
                    .otherwise()
                        .to("http://user-service:8081${header.CamelHttpPath}")
                        .to("direct:update-cache")
                .end()
            .onFallback()
                .log("Circuit breaker activated for user service")
                .setHeader(Exchange.HTTP_RESPONSE_CODE, constant(503))
                .setBody(constant("{\"error\":\"Service temporarily unavailable\"}"))
            .end();

        // Cache check
        from("direct:check-cache")
            .routeId("cache-checker")
            .process(exchange -> {
                String cacheKey = exchange.getIn().getHeader(Exchange.HTTP_PATH, String.class);
                // Check cache (Redis, Caffeine, etc.)
                Object cachedValue = getCachedValue(cacheKey);
                if (cachedValue != null) {
                    exchange.getIn().setHeader("CacheHit", true);
                    exchange.getIn().setBody(cachedValue);
                } else {
                    exchange.getIn().setHeader("CacheHit", false);
                }
            });

        // Cache update
        from("direct:update-cache")
            .routeId("cache-updater")
            .process(exchange -> {
                String cacheKey = exchange.getIn().getHeader(Exchange.HTTP_PATH, String.class);
                Object value = exchange.getIn().getBody();
                // Update cache with TTL
                updateCache(cacheKey, value, 300); // 5 minutes TTL
            });
    }

    private Object getCachedValue(String key) {
        // Implement cache lookup
        return null;
    }

    private void updateCache(String key, Object value, int ttlSeconds) {
        // Implement cache update
    }
}
```

## Example 5: Batch Processing with Aggregation

Process high-volume message streams with batching, aggregation, and parallel processing.

### Batch Processing Route

```java
@Component
public class BatchProcessingRoute extends RouteBuilder {

    @Override
    public void configure() {
        // Consume high-volume stream
        from("kafka:events?groupId=batch-processor&maxPollRecords=500")
            .routeId("batch-event-processor")
            .unmarshal().json(JsonLibrary.Jackson, Event.class)
            .to("seda:batch-queue?concurrentConsumers=10&size=10000");

        // Aggregate into batches
        from("seda:batch-queue")
            .routeId("batch-aggregator")
            .aggregate(constant(true), new GroupedBodyAggregationStrategy())
                .completionSize(100)
                .completionTimeout(5000)
                .parallelProcessing()
                .to("direct:process-batch");

        // Process batch
        from("direct:process-batch")
            .routeId("batch-processor")
            .log("Processing batch of ${body.size()} events")
            .split(body())
                .parallelProcessing()
                .streaming()
                .to("direct:enrich-event")
                .to("direct:transform-event")
            .end()
            .aggregate(constant(true), new GroupedBodyAggregationStrategy())
                .completionFromBatchConsumer()
                .to("direct:persist-batch");

        // Enrich events with external data
        from("direct:enrich-event")
            .routeId("event-enricher")
            .enrich("direct:lookup-user-data", (original, resource) -> {
                Event event = original.getIn().getBody(Event.class);
                UserData userData = resource.getIn().getBody(UserData.class);
                event.setUserData(userData);
                original.getIn().setBody(event);
                return original;
            });

        from("direct:lookup-user-data")
            .routeId("user-data-lookup")
            .setBody(simple("${body.userId}"))
            .to("sql:SELECT * FROM users WHERE id = :#${body}")
            .process(exchange -> {
                // Convert SQL result to UserData
            });

        // Transform events
        from("direct:transform-event")
            .routeId("event-transformer")
            .bean(EventTransformer.class, "transform");

        // Persist batch to database
        from("direct:persist-batch")
            .routeId("batch-persister")
            .transacted()
            .split(body())
                .to("jpa:com.example.model.ProcessedEvent")
            .end()
            .to("direct:publish-completion-event");

        // Publish batch completion event
        from("direct:publish-completion-event")
            .routeId("completion-publisher")
            .setBody(simple("{\"batchSize\":${body.size()},\"timestamp\":\"${date:now:ISO_8601}\"}"))
            .to("kafka:batch-completed");
    }
}

@Component
class EventTransformer {
    public ProcessedEvent transform(Event event) {
        ProcessedEvent processed = new ProcessedEvent();
        processed.setEventId(event.getId());
        processed.setTimestamp(event.getTimestamp());
        processed.setData(processData(event.getData()));
        return processed;
    }

    private String processData(String data) {
        // Transform logic
        return data;
    }
}
```

## Configuration Best Practices

### Externalized Configuration

```yaml
# application.yml
app:
  kafka:
    brokers: ${KAFKA_BROKERS:localhost:9092}
    consumer:
      group-id: ${KAFKA_CONSUMER_GROUP:default-group}
      max-poll-records: ${KAFKA_MAX_POLL_RECORDS:500}
  database:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/app}
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:secret}
  processing:
    batch-size: ${BATCH_SIZE:100}
    batch-timeout: ${BATCH_TIMEOUT:5000}
    thread-pool-size: ${THREAD_POOL_SIZE:10}

camel:
  component:
    kafka:
      brokers: ${app.kafka.brokers}
```

### Environment-Specific Profiles

```yaml
# application-dev.yml
logging:
  level:
    org.apache.camel: DEBUG
    com.example: DEBUG

# application-prod.yml
logging:
  level:
    org.apache.camel: WARN
    com.example: INFO

management:
  endpoints:
    web:
      exposure:
        include: health,metrics
```

## References

- [Camel Examples Repository](https://github.com/apache/camel-examples)
- [Spring Boot Documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/)
