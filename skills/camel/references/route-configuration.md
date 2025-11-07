# Route Configuration Best Practices

This guide covers best practices for configuring Apache Camel routes in Spring Boot applications.

## Route Organization

### Single Responsibility Principle

Each RouteBuilder should have a single, well-defined responsibility.

```java
// Good: Focused on order processing
@Component
public class OrderProcessingRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("jms:queue:orders")
            .to("direct:validate-order")
            .to("direct:process-order")
            .to("direct:persist-order");
    }
}

// Good: Focused on notifications
@Component
public class NotificationRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("direct:send-notification")
            .choice()
                .when(simple("${body.type} == 'EMAIL'"))
                    .to("direct:send-email")
                .when(simple("${body.type} == 'SMS'"))
                    .to("direct:send-sms")
            .end();
    }
}

// Bad: Mixed responsibilities
@Component
public class MixedRoute extends RouteBuilder {
    @Override
    public void configure() {
        // Order processing, notifications, reporting all in one
    }
}
```

### Package Structure

```
com.example.routes/
├── api/
│   ├── OrderApiRoute.java
│   ├── ProductApiRoute.java
│   └── UserApiRoute.java
├── integration/
│   ├── KafkaConsumerRoute.java
│   ├── KafkaProducerRoute.java
│   └── JmsRoute.java
├── processing/
│   ├── OrderProcessingRoute.java
│   ├── PaymentProcessingRoute.java
│   └── InventoryRoute.java
└── config/
    ├── ErrorHandlingConfig.java
    └── ComponentConfig.java
```

## Configuration via Properties

### Property Placeholders

```yaml
# application.yml
app:
  endpoints:
    orders:
      input: jms:queue:orders
      output: kafka:processed-orders
      dead-letter: jms:queue:orders-dlq
  kafka:
    brokers: localhost:9092
  retry:
    max-attempts: 3
    delay: 2000
```

```java
@Component
public class OrderRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("{{app.endpoints.orders.input}}")
            .errorHandler(deadLetterChannel("{{app.endpoints.orders.dead-letter}}")
                .maximumRedeliveries({{app.retry.max-attempts}})
                .redeliveryDelay({{app.retry.delay}}))
            .to("direct:process")
            .to("{{app.endpoints.orders.output}}?brokers={{app.kafka.brokers}}");
    }
}
```

### Type-Safe Configuration

```java
@ConfigurationProperties(prefix = "app.routes")
@Component
public class RouteConfig {
    private EndpointConfig endpoints;
    private RetryConfig retry;
    private KafkaConfig kafka;

    // Getters and setters

    @Data
    public static class EndpointConfig {
        private String ordersInput;
        private String ordersOutput;
        private String deadLetter;
    }

    @Data
    public static class RetryConfig {
        private int maxAttempts = 3;
        private long delay = 2000;
        private double backoffMultiplier = 2.0;
    }

    @Data
    public static class KafkaConfig {
        private String brokers;
        private String consumerGroup;
    }
}

@Component
public class ConfigurableRoute extends RouteBuilder {

    @Autowired
    private RouteConfig config;

    @Override
    public void configure() {
        errorHandler(deadLetterChannel(config.getEndpoints().getDeadLetter())
            .maximumRedeliveries(config.getRetry().getMaxAttempts())
            .redeliveryDelay(config.getRetry().getDelay())
            .backOffMultiplier(config.getRetry().getBackoffMultiplier()));

        from(config.getEndpoints().getOrdersInput())
            .to("direct:process")
            .to(config.getEndpoints().getOrdersOutput() + "?brokers=" + config.getKafka().getBrokers());
    }
}
```

## Route IDs and Descriptions

### Always Use Route IDs

```java
from("jms:queue:orders")
    .routeId("order-processor")
    .description("Processes customer orders from JMS queue")
    .to("direct:validate")
    .to("direct:process");

from("kafka:events")
    .routeId("event-consumer")
    .description("Consumes events from Kafka and forwards to processing pipeline")
    .to("direct:process-event");
```

### Route ID Naming Conventions

- Use kebab-case: `order-processor`, `event-consumer`
- Be descriptive: `payment-authorization-handler` not `route1`
- Include domain context: `inventory-stock-updater`
- Avoid generic names: `processor`, `handler`

## Auto-Configuration

### Conditional Routes

```java
@Component
@ConditionalOnProperty(name = "app.routes.order-processing.enabled", havingValue = "true")
public class OrderProcessingRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("jms:queue:orders")
            .to("direct:process-order");
    }
}
```

### Profile-Specific Routes

```java
@Component
@Profile("kafka")
public class KafkaOrderRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:orders")
            .to("direct:process");
    }
}

@Component
@Profile("jms")
public class JmsOrderRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("jms:queue:orders")
            .to("direct:process");
    }
}
```

## Thread Pool Configuration

### Custom Thread Pools

```java
@Configuration
public class ThreadPoolConfig {

    @Bean
    public ThreadPoolProfile highVolumeThreadPool() {
        ThreadPoolProfile profile = new ThreadPoolProfile("highVolume");
        profile.setPoolSize(20);
        profile.setMaxPoolSize(50);
        profile.setMaxQueueSize(1000);
        profile.setKeepAliveTime(60L);
        return profile;
    }
}

@Component
public class HighVolumeRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:high-volume-events")
            .threads()
                .threadPoolProfile("highVolume")
            .to("direct:process");
    }
}
```

### SEDA Queue Configuration

```java
from("direct:async-entry")
    .to("seda:processing?concurrentConsumers=10&size=1000");

from("seda:processing")
    .threads(10, 20)
    .to("direct:heavy-processing");
```

## Startup and Shutdown Control

### Auto-Startup Configuration

```java
@Component
public class ManualStartRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("timer:scheduled?delay=10000")
            .routeId("scheduled-task")
            .autoStartup(false) // Don't start automatically
            .to("direct:task");
    }
}

@Component
public class RouteController {

    @Autowired
    private CamelContext camelContext;

    @EventListener(ApplicationReadyEvent.class)
    public void startRoutes() throws Exception {
        // Start route after application is fully initialized
        camelContext.getRouteController().startRoute("scheduled-task");
    }
}
```

### Graceful Shutdown

```yaml
camel:
  springboot:
    shutdown-timeout: 30
    shutdown-suppress-logging-on-timeout: false
    shutdown-log-inflightExchangesOnTimeout: true
```

```java
@Configuration
public class ShutdownConfig {

    @Bean
    public ShutdownStrategy shutdownStrategy() {
        DefaultShutdownStrategy strategy = new DefaultShutdownStrategy();
        strategy.setTimeout(30);
        strategy.setTimeUnit(TimeUnit.SECONDS);
        strategy.setSuppressLoggingOnTimeout(false);
        strategy.setLogInflightExchangesOnTimeout(true);
        return strategy;
    }
}
```

## Route Policies

### Scheduled Route Policy

```java
@Component
public class ScheduledRoute extends RouteBuilder {

    @Bean
    public RoutePolicy schedulePolicy() {
        CronScheduledRoutePolicy policy = new CronScheduledRoutePolicy();
        policy.setRouteStartTime("0 0 8 * * ?");  // Start at 8 AM
        policy.setRouteStopTime("0 0 18 * * ?");  // Stop at 6 PM
        return policy;
    }

    @Override
    public void configure() {
        from("file:/data/input")
            .routeId("business-hours-only")
            .routePolicy(schedulePolicy())
            .to("direct:process");
    }
}
```

### Throttling Policy

```java
from("jms:queue:high-volume")
    .routeId("throttled-consumer")
    .throttle(100).timePeriodMillis(1000)  // 100 messages per second
    .to("direct:process");
```

### Circuit Breaker Policy

```java
from("direct:protected-call")
    .circuitBreaker()
        .resilience4jConfiguration()
            .failureRateThreshold(50)
            .waitDurationInOpenState(10000)
            .slidingWindowSize(10)
        .end()
        .to("http://external-service")
    .onFallback()
        .to("direct:fallback-handler")
    .end();
```

## Component Configuration

### Global Component Configuration

```java
@Configuration
public class ComponentConfig {

    @Bean
    public KafkaComponent kafka() {
        KafkaComponent kafka = new KafkaComponent();
        kafka.setBrokers("localhost:9092");
        kafka.setAutoOffsetReset("earliest");
        return kafka;
    }

    @Bean
    public JmsComponent jms(ConnectionFactory connectionFactory) {
        JmsComponent jms = new JmsComponent();
        jms.setConnectionFactory(connectionFactory);
        jms.setConcurrentConsumers(10);
        jms.setMaxConcurrentConsumers(20);
        jms.setRequestTimeout(5000L);
        return jms;
    }

    @Bean
    public ServletComponent servlet() {
        ServletComponent servlet = new ServletComponent();
        servlet.setServletName("CamelServlet");
        return servlet;
    }
}
```

### Per-Endpoint Configuration

```java
from("kafka:orders?"
    + "brokers=localhost:9092"
    + "&groupId=order-processor"
    + "&autoOffsetReset=earliest"
    + "&maxPollRecords=500"
    + "&sessionTimeoutMs=30000"
    + "&enableAutoCommit=false"
    + "&allowManualCommit=true")
    .to("direct:process");
```

## Route Templates

### Defining Route Templates

```java
@Component
public class KafkaRouteTemplate extends RouteBuilder {
    @Override
    public void configure() {
        routeTemplate("kafka-to-direct")
            .templateParameter("topic")
            .templateParameter("groupId")
            .templateParameter("targetRoute")
            .from("kafka:{{topic}}?groupId={{groupId}}")
            .to("direct:{{targetRoute}}");
    }
}
```

### Using Route Templates

```java
@Component
public class RouteInstantiator {

    @Autowired
    private CamelContext camelContext;

    @PostConstruct
    public void createRoutes() throws Exception {
        camelContext.addRouteFromTemplate("orders-route", "kafka-to-direct")
            .parameter("topic", "orders")
            .parameter("groupId", "order-processor")
            .parameter("targetRoute", "process-order")
            .add();

        camelContext.addRouteFromTemplate("events-route", "kafka-to-direct")
            .parameter("topic", "events")
            .parameter("groupId", "event-processor")
            .parameter("targetRoute", "process-event")
            .add();
    }
}
```

## Best Practices Summary

1. **Use Meaningful Route IDs**: Every route should have a descriptive ID
2. **Externalize Configuration**: Use properties for all environment-specific values
3. **Separate Concerns**: One RouteBuilder per integration concern
4. **Type-Safe Config**: Use @ConfigurationProperties for complex configuration
5. **Document Routes**: Add descriptions to explain route purpose
6. **Control Startup**: Use autoStartup(false) for routes that need delayed start
7. **Configure Thread Pools**: Size thread pools based on workload characteristics
8. **Use Route Policies**: Apply policies for scheduling, throttling, circuit breaking
9. **Graceful Shutdown**: Configure appropriate shutdown timeouts
10. **Template Reusable Patterns**: Use route templates for common patterns

## Anti-Patterns to Avoid

### ❌ Hardcoded Values

```java
// Bad
from("kafka:orders?brokers=prod-kafka-01:9092")
    .to("http://prod-api.example.com/orders");

// Good
from("{{kafka.orders.endpoint}}")
    .to("{{api.orders.url}}");
```

### ❌ Missing Route IDs

```java
// Bad
from("jms:queue:orders")
    .to("direct:process");

// Good
from("jms:queue:orders")
    .routeId("order-consumer")
    .to("direct:process");
```

### ❌ Giant RouteBuilder Classes

```java
// Bad: 500+ lines, multiple concerns
@Component
public class AllRoutesInOne extends RouteBuilder {
    // Orders, products, users, notifications all mixed together
}

// Good: Focused, single responsibility
@Component
public class OrderRoute extends RouteBuilder { }

@Component
public class ProductRoute extends RouteBuilder { }
```

### ❌ No Error Handling

```java
// Bad
from("jms:queue:orders")
    .to("http://unreliable-service")
    .to("jms:queue:processed");

// Good
from("jms:queue:orders")
    .errorHandler(deadLetterChannel("jms:queue:dlq")
        .maximumRedeliveries(3)
        .redeliveryDelay(2000))
    .to("http://unreliable-service")
    .to("jms:queue:processed");
```

## References

- [Camel Route Configuration](https://camel.apache.org/manual/routes.html)
- [Spring Boot Configuration Properties](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config)
