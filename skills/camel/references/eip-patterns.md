# Enterprise Integration Patterns (EIP)

Apache Camel implements the Enterprise Integration Patterns from the book by Gregor Hohpe and Bobby Woolf. This reference provides practical implementations of the most common patterns.

## Message Routing Patterns

### Content-Based Router
Routes messages to different destinations based on message content.

```java
from("direct:orders")
    .choice()
        .when(simple("${body.type} == 'PRIORITY'"))
            .to("jms:queue:priority-orders")
        .when(simple("${body.amount} > 1000"))
            .to("jms:queue:large-orders")
        .otherwise()
            .to("jms:queue:standard-orders")
    .end();
```

### Message Filter
Filters messages based on a predicate, allowing only matching messages to proceed.

```java
from("jms:queue:all-events")
    .filter(simple("${body.status} == 'ACTIVE'"))
    .to("jms:queue:active-events");
```

### Recipient List
Routes messages to multiple endpoints dynamically determined at runtime.

```java
from("direct:notify")
    .recipientList(simple("${header.destinations}"))
    .delimiter(",");

// Usage: set header 'destinations' to "jms:queue:email,jms:queue:sms,jms:queue:push"
```

### Dynamic Router
Routes messages to different endpoints based on dynamic conditions.

```java
from("direct:input")
    .dynamicRouter(method(DynamicRouterBean.class, "route"));

public class DynamicRouterBean {
    public String route(String body, @ExchangeProperties Map<String, Object> properties) {
        int invoked = (int) properties.getOrDefault("invoked", 0);
        properties.put("invoked", invoked + 1);

        if (invoked == 0) return "mock:a";
        if (invoked == 1) return "mock:b,mock:c";
        return null; // end routing
    }
}
```

### Routing Slip
Routes messages through a series of processing steps specified in the message header.

```java
from("direct:start")
    .routingSlip(header("routingSlip"))
    .delimiter(",");

// Set header 'routingSlip' to "direct:step1,direct:step2,direct:step3"
```

## Message Transformation Patterns

### Message Translator
Transforms message from one format to another.

```java
from("jms:queue:xml-orders")
    .unmarshal().jacksonXml(Order.class)
    .bean(OrderTransformer.class, "toInternalFormat")
    .marshal().json(JsonLibrary.Jackson)
    .to("kafka:internal-orders");
```

### Content Enricher
Enriches message content with additional data from external sources.

```java
from("direct:orders")
    .enrich("direct:get-customer-details", new AggregationStrategy() {
        @Override
        public Exchange aggregate(Exchange original, Exchange resource) {
            Order order = original.getIn().getBody(Order.class);
            Customer customer = resource.getIn().getBody(Customer.class);
            order.setCustomer(customer);
            original.getIn().setBody(order);
            return original;
        }
    })
    .to("jms:queue:enriched-orders");

from("direct:get-customer-details")
    .to("http://customer-service/api/customers/${body.customerId}");
```

### Normalizer
Converts messages from different formats into a canonical format.

```java
from("direct:xml-input")
    .unmarshal().jacksonXml(Order.class)
    .to("direct:normalize");

from("direct:json-input")
    .unmarshal().json(JsonLibrary.Jackson, Order.class)
    .to("direct:normalize");

from("direct:normalize")
    .bean(OrderNormalizer.class)
    .to("jms:queue:normalized-orders");
```

## Message Construction Patterns

### Message Construction
Build messages with headers, body, and properties.

```java
from("direct:start")
    .setHeader("OrderId", simple("${body.id}"))
    .setHeader("Timestamp", simple("${date:now:yyyy-MM-dd'T'HH:mm:ss}"))
    .setProperty("OriginalBody", body())
    .setBody(simple("Order ${body.id} received"))
    .to("jms:queue:orders");
```

### Claim Check
Store message content temporarily and retrieve it later.

```java
from("direct:start")
    .claimCheck(ClaimCheckOperation.Set)
    .process(exchange -> {
        // Process with lightweight message
    })
    .claimCheck(ClaimCheckOperation.Get)
    .to("direct:next");
```

## Message Splitting and Aggregation

### Splitter
Splits a single message into multiple messages.

```java
from("direct:orders")
    .split(simple("${body.items}"))
        .parallelProcessing()
        .streaming()
        .to("jms:queue:order-items")
    .end();
```

### Aggregator
Aggregates multiple messages into a single message.

```java
from("jms:queue:order-items")
    .aggregate(header("orderId"), new ArrayListAggregationStrategy())
        .completionSize(10)
        .completionTimeout(5000)
        .completionPredicate(header("lastItem").isEqualTo(true))
    .to("jms:queue:aggregated-orders");
```

### Scatter-Gather
Broadcasts a message to multiple recipients and aggregates responses.

```java
from("direct:price-quote")
    .multicast(new LowestPriceAggregationStrategy())
        .parallelProcessing()
        .to("http://supplier-a/quote", "http://supplier-b/quote", "http://supplier-c/quote")
    .end()
    .to("jms:queue:best-price");
```

### Resequencer
Reorders messages based on a sequence identifier.

```java
from("jms:queue:unordered")
    .resequence(header("sequenceNumber"))
        .batch()
        .size(100)
        .timeout(3000)
    .to("jms:queue:ordered");
```

## Endpoint Patterns

### Wire Tap
Sends a copy of the message to a secondary destination without affecting the main flow.

```java
from("direct:orders")
    .wireTap("jms:queue:order-audit")
    .to("jms:queue:order-processing");
```

### Multicast
Sends the same message to multiple endpoints simultaneously.

```java
from("direct:notification")
    .multicast()
        .parallelProcessing()
        .to("direct:email", "direct:sms", "direct:push")
    .end();
```

### Loop
Processes a message multiple times in a loop.

```java
from("direct:retry-processor")
    .loop(3)
        .copy()
        .to("http://external-service")
        .delay(1000)
    .end();
```

## Throttling and Sampling

### Throttler
Limits the number of messages processed per time period.

```java
from("jms:queue:high-volume")
    .throttle(100).timePeriodMillis(1000)
    .to("http://rate-limited-api");
```

### Delayer
Delays message processing by a specified time.

```java
from("direct:delayed-processing")
    .delay(5000)
    .to("jms:queue:processing");
```

### Sampling
Samples messages at regular intervals.

```java
from("direct:metrics")
    .sample(1, TimeUnit.SECONDS)
    .to("direct:metrics-aggregator");
```

## Idempotent Consumer

Ensures messages are processed only once by tracking message IDs.

```java
from("jms:queue:orders")
    .idempotentConsumer(
        header("MessageId"),
        MemoryIdempotentRepository.memoryIdempotentRepository(200)
    )
    .to("direct:process-order");
```

With persistent repository:

```java
@Bean
public IdempotentRepository idempotentRepository(DataSource dataSource) {
    JdbcMessageIdRepository repository = new JdbcMessageIdRepository(dataSource, "myProcessor");
    return repository;
}

// In route:
from("jms:queue:orders")
    .idempotentConsumer(header("MessageId"))
    .messageIdRepositoryRef("idempotentRepository")
    .to("direct:process-order");
```

## Transaction Patterns

### Transactional Client
Ensures message processing within a transaction boundary.

```java
from("jms:queue:orders?transacted=true")
    .transacted()
    .to("sql:INSERT INTO orders VALUES (:#${body.id}, :#${body.amount})")
    .to("jms:queue:order-confirmation");
```

## Best Practices

1. **Choose the Right Pattern**: Select patterns based on integration requirements, not complexity.
2. **Combine Patterns**: EIP patterns work well together; combine them to solve complex scenarios.
3. **Keep Routes Simple**: Break complex patterns into multiple routes for maintainability.
4. **Use Parallel Processing**: Leverage `.parallelProcessing()` for splitter and multicast when appropriate.
5. **Handle Errors**: Always implement error handling with patterns that can fail.
6. **Monitor Performance**: Track pattern execution times and throughput in production.
7. **Test Thoroughly**: Unit test each pattern implementation with various input scenarios.

## Common Pattern Combinations

### Order Processing with Validation, Enrichment, and Routing
```java
from("jms:queue:raw-orders")
    .routeId("order-processing-pipeline")
    // Validate
    .filter(method(OrderValidator.class))
    // Enrich with customer data
    .enrich("direct:customer-lookup", new CustomerEnrichmentStrategy())
    // Route based on content
    .choice()
        .when(simple("${body.amount} > 10000"))
            .to("jms:queue:premium-orders")
        .otherwise()
            .to("jms:queue:standard-orders")
    .end()
    // Audit all processed orders
    .wireTap("direct:audit");
```

### High-Volume Event Processing with Aggregation and Throttling
```java
from("kafka:events")
    // Sample high-volume stream
    .sample(100, TimeUnit.MILLISECONDS)
    // Aggregate events
    .aggregate(header("userId"), new EventAggregationStrategy())
        .completionSize(50)
        .completionTimeout(5000)
    // Throttle to prevent overwhelming downstream
    .throttle(10).timePeriodMillis(1000)
    .to("http://analytics-service");
```

## References

- [Enterprise Integration Patterns Book](https://www.enterpriseintegrationpatterns.com/)
- [Apache Camel EIP Documentation](https://camel.apache.org/components/latest/eips/enterprise-integration-patterns.html)
