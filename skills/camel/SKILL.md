---
name: camel-spring-boot
description: Build enterprise integration solutions with Apache Camel and Spring Boot. Configure routes, implement EIP patterns, handle errors, and deploy production-ready message-driven architectures.
allowed-tools: Read, Write, Bash, Grep
category: integration
tags: [apache-camel, spring-boot, integration, eip, messaging, routes, enterprise-integration]
version: 1.0.0
context7_library: /websites/camel_apache_org
context7_trust_score: 8.0
---

# Apache Camel Spring Boot Skill

## Overview
- Build robust enterprise integration solutions using Apache Camel's routing engine and Spring Boot's auto-configuration.
- Implement Enterprise Integration Patterns (EIP) for message transformation, routing, orchestration, and error handling.
- Leverage Camel's extensive component ecosystem (280+ connectors) for seamless system integration.
- Deploy production-ready integration services with health checks, metrics, and observability.

## When to Use
- Trigger: "create camel route" – Bootstrap a new Camel route for message processing or system integration.
- Trigger: "integrate systems with camel" – Connect disparate systems using Camel components and routes.
- Trigger: "implement eip pattern" – Apply Enterprise Integration Patterns like Content-Based Router, Splitter, Aggregator.
- Trigger: "configure camel error handling" – Set up error handlers, retry policies, and dead letter channels.
- Trigger: "test camel routes" – Implement unit and integration tests for Camel routes using CamelTestSupport.

## Quick Start
1. Add Camel Spring Boot starter dependency.
   ```xml
   <!-- Maven -->
   <dependency>
       <groupId>org.apache.camel.springboot</groupId>
       <artifactId>camel-spring-boot-starter</artifactId>
       <version>4.8.1</version>
   </dependency>
   ```
   ```gradle
   // Gradle
   dependencies {
       implementation "org.apache.camel.springboot:camel-spring-boot-starter:4.8.1"
   }
   ```
2. Create your first route and verify it starts successfully on application startup.

## Implementation Workflow

### 1. Define Camel Routes
- Extend `RouteBuilder` and override `configure()` to define message flows.
- Use DSL methods like `from()`, `to()`, `choice()`, `split()`, `aggregate()` to build routes.
- Apply route IDs and descriptions for monitoring and debugging: `.routeId("order-processor").description("Process customer orders")`.
- Organize routes logically: one RouteBuilder per business domain or integration concern.

### 2. Configure Components and Endpoints
- Add component-specific starters (e.g., `camel-kafka-starter`, `camel-jms-starter`, `camel-rest-starter`).
- Configure endpoints via `application.properties` or `application.yml` for environment-specific settings.
- Use property placeholders in route URIs: `from("kafka:{{kafka.topic.orders}}?brokers={{kafka.brokers}}")`.
- Consult `references/components-reference.md` for component URI syntax and options.

### 3. Implement Enterprise Integration Patterns
- **Content-Based Router**: Route messages based on content using `choice()` and `when()`.
- **Message Transformation**: Transform message formats with `transform()`, `marshal()`, `unmarshal()`.
- **Splitter**: Process collections by splitting messages into individual items.
- **Aggregator**: Combine related messages into a single aggregated message.
- **Wire Tap**: Send a copy of the message to a secondary endpoint without affecting the main flow.
- Detailed pattern implementations available in `references/eip-patterns.md`.

### 4. Handle Errors and Exceptions
- Configure global error handlers with `errorHandler(deadLetterChannel("jms:queue:dead-letter"))`.
- Apply route-specific error handling with `onException()` for fine-grained control.
- Implement retry policies with exponential backoff: `maximumRedeliveries(3).redeliveryDelay(1000).backOffMultiplier(2)`.
- Use `doTry().doCatch().doFinally()` for inline exception handling within routes.
- See `references/error-handling.md` for comprehensive error handling strategies.

### 5. Test Routes Thoroughly
- Use `camel-test-spring-junit5` for Spring-aware Camel route testing.
- Apply `@CamelSpringBootTest` and `@MockEndpoints` to isolate routes during testing.
- Implement `ProducerTemplate` to send test messages and `ConsumerTemplate` to verify outputs.
- Validate message transformations, routing decisions, and error handling paths.
- Review test patterns in `references/testing-strategies.md`.

### 6. Monitor and Observe
- Enable Camel management and JMX metrics via `camel.springboot.jmx-enabled=true`.
- Integrate with Spring Boot Actuator for health endpoints and route metrics.
- Configure route-level metrics with Micrometer for Prometheus or other monitoring systems.
- Use Camel Tracer for debugging message flows: `camel.springboot.tracing=true`.
- Consult `references/monitoring-observability.md` for production observability setup.

## Examples

### Basic – Simple File Polling Route
```java
@Component
public class FilePollerRoute extends RouteBuilder {

    @Override
    public void configure() {
        from("file:{{input.directory}}?noop=true")
            .routeId("file-poller")
            .log("Processing file: ${header.CamelFileName}")
            .to("file:{{output.directory}}");
    }
}
```
```yaml
# application.yml
input:
  directory: /data/input
output:
  directory: /data/output
```

### Intermediate – REST API with Content-Based Routing
```java
@Component
public class OrderApiRoute extends RouteBuilder {

    @Override
    public void configure() {
        restConfiguration()
            .component("servlet")
            .bindingMode(RestBindingMode.json);

        rest("/orders")
            .post().type(Order.class)
            .to("direct:process-order");

        from("direct:process-order")
            .routeId("order-processor")
            .choice()
                .when(simple("${body.priority} == 'HIGH'"))
                    .to("jms:queue:high-priority-orders")
                .when(simple("${body.amount} > 1000"))
                    .to("jms:queue:large-orders")
                .otherwise()
                    .to("jms:queue:standard-orders")
            .end()
            .setBody(constant("Order accepted"))
            .setHeader("Content-Type", constant("application/json"));
    }
}
```

### Advanced – Kafka Consumer with Error Handling and Aggregation
```java
@Component
public class EventAggregationRoute extends RouteBuilder {

    @Override
    public void configure() {
        onException(JsonProcessingException.class)
            .handled(true)
            .log(LoggingLevel.ERROR, "Invalid JSON: ${exception.message}")
            .to("kafka:{{kafka.topic.errors}}");

        from("kafka:{{kafka.topic.events}}?brokers={{kafka.brokers}}&groupId=event-aggregator")
            .routeId("event-aggregator")
            .unmarshal().json(JsonLibrary.Jackson, Event.class)
            .aggregate(simple("${body.customerId}"), new EventAggregationStrategy())
                .completionSize(10)
                .completionTimeout(5000)
            .marshal().json()
            .to("kafka:{{kafka.topic.aggregated}}?brokers={{kafka.brokers}}")
            .log("Aggregated events for customer: ${body.customerId}");
    }
}
```
```java
public class EventAggregationStrategy implements AggregationStrategy {

    @Override
    public Exchange aggregate(Exchange oldExchange, Exchange newExchange) {
        if (oldExchange == null) {
            return newExchange;
        }
        Event oldEvent = oldExchange.getIn().getBody(Event.class);
        Event newEvent = newExchange.getIn().getBody(Event.class);

        AggregatedEvent aggregated = new AggregatedEvent();
        aggregated.setCustomerId(newEvent.getCustomerId());
        aggregated.addEvent(oldEvent);
        aggregated.addEvent(newEvent);

        oldExchange.getIn().setBody(aggregated);
        return oldExchange;
    }
}
```

More comprehensive examples available in `references/examples.md`.

## Best Practices
- Keep SKILL.md concise and delegate detailed documentation to `references/` for context efficiency.
- Design routes with single responsibility: one route per integration flow or business process.
- Use meaningful route IDs and descriptions for operational visibility.
- Apply property placeholders for all environment-specific configuration.
- Implement idempotent consumers for exactly-once message processing semantics.
- Configure circuit breakers and timeout policies to prevent cascade failures.
- Test routes in isolation using mocks and ensure comprehensive coverage of error paths.
- Monitor route throughput, error rates, and processing times in production.

## Constraints
- Avoid creating overly complex routes; split into multiple routes for clarity.
- Do not perform blocking I/O operations in routes without proper threading configuration.
- Ensure proper transaction boundaries when working with transactional resources (JMS, database).
- Maintain compatibility with Camel 4.x conventions; version 3.x has different component configurations.
- Limit in-memory aggregation sizes to prevent OutOfMemory errors; use persistent stores for large batches.
- Configure appropriate thread pool sizes to match workload characteristics and resource limits.

## Reference Materials
- [Enterprise Integration Patterns](references/eip-patterns.md)
- [Component configurations and URI syntax](references/components-reference.md)
- [Error handling strategies](references/error-handling.md)
- [Testing strategies and examples](references/testing-strategies.md)
- [Monitoring and observability](references/monitoring-observability.md)
- [Implementation examples](references/examples.md)
- [Route configuration best practices](references/route-configuration.md)
- [Data formats and transformation](references/data-formats.md)
- [Transaction management](references/transactions.md)
- [Performance tuning](references/performance-tuning.md)

## Validation Checklist
- Confirm `mvn spring-boot:run` or `./gradlew bootRun` starts the application and all routes successfully.
- Verify routes are registered via `/actuator/camelroutes` endpoint (requires camel-spring-boot-starter-actuator).
- Test message flow end-to-end with sample data to validate routing logic and transformations.
- Verify error handling by simulating exceptions and confirming messages reach dead letter channels.
- Monitor route metrics under load to ensure throughput meets performance requirements.
- Run integration tests in CI/CD pipeline to catch regression issues early.
