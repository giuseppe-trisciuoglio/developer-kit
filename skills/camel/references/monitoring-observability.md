# Monitoring and Observability

Production-ready Camel applications require comprehensive monitoring and observability. This guide covers metrics, health checks, tracing, and integration with monitoring systems.

## Spring Boot Actuator Integration

### Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-micrometer-starter</artifactId>
</dependency>
```

### Configuration

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus,camelroutes,camelroutecontroller
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true
  metrics:
    export:
      prometheus:
        enabled: true

camel:
  springboot:
    jmx-enabled: true
    name: integration-service
  metrics:
    enabled: true
```

## Camel-Specific Actuator Endpoints

### Route Information

**Endpoint:** `/actuator/camelroutes`

Returns detailed information about all Camel routes.

```json
{
  "routes": [
    {
      "id": "order-processor",
      "description": "Process customer orders",
      "uptime": "2h 15m",
      "uptimeMillis": 8100000,
      "status": "Started"
    }
  ]
}
```

### Route Controller

**Endpoint:** `/actuator/camelroutecontroller`

Control route lifecycle (start, stop, suspend, resume).

```bash
# Stop a route
curl -X POST http://localhost:8080/actuator/camelroutecontroller/order-processor/stop

# Start a route
curl -X POST http://localhost:8080/actuator/camelroutecontroller/order-processor/start

# Get route status
curl http://localhost:8080/actuator/camelroutecontroller/order-processor
```

## Health Checks

### Camel Route Health Indicators

```java
@Component
public class CustomRouteHealthCheck extends RouteHealthCheck {

    public CustomRouteHealthCheck() {
        super("order-processor-health");
        getConfiguration().setEnabled(true);
    }

    @Override
    protected void doCheck(HealthCheckResultBuilder builder, Map<String, Object> options) {
        builder.up();
        builder.detail("routes.running", camelContext.getRoutesSize());
        builder.detail("routes.started", camelContext.getRunningRoutes());
    }
}
```

### Custom Health Indicators

```java
@Component
public class IntegrationHealthIndicator implements HealthIndicator {

    @Autowired
    private CamelContext camelContext;

    @Override
    public Health health() {
        long runningRoutes = camelContext.getRoutes().stream()
            .filter(route -> route.getRouteController().getRouteStatus(route.getId()).isStarted())
            .count();

        long totalRoutes = camelContext.getRoutesSize();

        if (runningRoutes == totalRoutes) {
            return Health.up()
                .withDetail("routes.total", totalRoutes)
                .withDetail("routes.running", runningRoutes)
                .build();
        } else {
            return Health.down()
                .withDetail("routes.total", totalRoutes)
                .withDetail("routes.running", runningRoutes)
                .withDetail("routes.stopped", totalRoutes - runningRoutes)
                .build();
        }
    }
}
```

### Readiness and Liveness Probes

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        readiness:
          include: readinessState,camel
        liveness:
          include: livenessState,ping
```

```bash
# Kubernetes liveness probe
curl http://localhost:8080/actuator/health/liveness

# Kubernetes readiness probe
curl http://localhost:8080/actuator/health/readiness
```

## Metrics and Monitoring

### Micrometer Integration

Camel automatically exposes metrics via Micrometer.

**Key Metrics:**
- `camel.route.exchanges.total` - Total number of exchanges processed
- `camel.route.exchanges.failed` - Number of failed exchanges
- `camel.route.processing.time` - Processing time histogram
- `camel.route.external.redeliveries` - Number of redeliveries

### Custom Metrics in Routes

```java
from("jms:queue:orders")
    .routeId("order-processor")
    .to("micrometer:counter:orders.received?tags=route=order-processor,type=inbound")
    .process(orderProcessor)
    .to("micrometer:timer:orders.processing.time")
    .to("jms:queue:processed")
    .to("micrometer:counter:orders.processed?tags=route=order-processor,type=outbound");
```

### Prometheus Metrics

```java
@Configuration
public class MetricsConfig {

    @Bean
    public MeterRegistryCustomizer<PrometheusMeterRegistry> metricsCommonTags() {
        return registry -> registry.config()
            .commonTags(
                "application", "integration-service",
                "environment", System.getenv().getOrDefault("ENV", "dev")
            );
    }
}
```

**Prometheus Scrape Configuration:**

```yaml
scrape_configs:
  - job_name: 'camel-integration'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['localhost:8080']
```

### Grafana Dashboard Queries

**Total Messages Processed:**
```promql
rate(camel_route_exchanges_total[5m])
```

**Error Rate:**
```promql
rate(camel_route_exchanges_failed_total[5m]) / rate(camel_route_exchanges_total[5m])
```

**Average Processing Time:**
```promql
rate(camel_route_processing_time_seconds_sum[5m]) / rate(camel_route_processing_time_seconds_count[5m])
```

**95th Percentile Processing Time:**
```promql
histogram_quantile(0.95, rate(camel_route_processing_time_seconds_bucket[5m]))
```

## Distributed Tracing

### OpenTelemetry Integration

**Dependencies:**

```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-opentelemetry-starter</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
```

**Configuration:**

```yaml
camel:
  opentelemetry:
    enabled: true
    service-name: integration-service
    exporter:
      otlp:
        endpoint: http://localhost:4317

management:
  tracing:
    sampling:
      probability: 1.0
```

**Java Configuration:**

```java
@Configuration
public class TracingConfig {

    @Bean
    public OpenTelemetry openTelemetry() {
        return AutoConfiguredOpenTelemetrySdk.initialize()
            .getOpenTelemetrySdk();
    }

    @Bean
    public CamelOpenTelemetryTracer camelTracer(OpenTelemetry openTelemetry) {
        CamelOpenTelemetryTracer tracer = new CamelOpenTelemetryTracer();
        tracer.setOpenTelemetry(openTelemetry);
        tracer.setEncoding(true);
        tracer.setTraceProcessors(true);
        return tracer;
    }
}
```

### Trace Correlation

```java
from("jms:queue:orders")
    .setHeader("X-Trace-Id", simple("${exchangeId}"))
    .log("Processing order with trace ID: ${header.X-Trace-Id}")
    .to("http://order-service/api/orders")
    .to("jms:queue:processed");
```

## Logging

### Structured Logging with Logback

**logback-spring.xml:**

```xml
<configuration>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeMdcKeyName>camel.routeId</includeMdcKeyName>
            <includeMdcKeyName>camel.exchangeId</includeMdcKeyName>
            <includeMdcKeyName>camel.breadcrumbId</includeMdcKeyName>
        </encoder>
    </appender>

    <logger name="org.apache.camel" level="INFO"/>
    <logger name="com.example.routes" level="DEBUG"/>

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
    </root>
</configuration>
```

### MDC Logging in Routes

```java
from("jms:queue:orders")
    .routeId("order-processor")
    .process(exchange -> {
        MDC.put("orderId", exchange.getIn().getHeader("orderId", String.class));
        MDC.put("customerId", exchange.getIn().getHeader("customerId", String.class));
    })
    .log("Processing order for customer")
    .to("direct:process")
    .process(exchange -> {
        MDC.remove("orderId");
        MDC.remove("customerId");
    });
```

### Route-Specific Logging

```java
from("direct:order-processor")
    .routeId("order-processor")
    .log(LoggingLevel.INFO, "Received order: ${body.id}")
    .choice()
        .when(simple("${body.amount} > 1000"))
            .log(LoggingLevel.WARN, "Large order detected: ${body.id} - ${body.amount}")
        .otherwise()
            .log(LoggingLevel.DEBUG, "Standard order: ${body.id}")
    .end()
    .to("direct:next");
```

## JMX Monitoring

### Enable JMX

```yaml
camel:
  springboot:
    jmx-enabled: true

management:
  endpoints:
    jmx:
      exposure:
        include: "*"
```

### JMX Metrics

Connect with JConsole or VisualVM to monitor:
- Route statistics (exchanges, failures, processing time)
- Thread pools
- Component metrics
- Endpoint statistics

### Custom MBeans

```java
@Component
@ManagedResource(description = "Order Processing Stats")
public class OrderProcessingStats {

    private final AtomicLong ordersProcessed = new AtomicLong();
    private final AtomicLong ordersFailed = new AtomicLong();

    @ManagedAttribute(description = "Total Orders Processed")
    public long getOrdersProcessed() {
        return ordersProcessed.get();
    }

    @ManagedAttribute(description = "Total Orders Failed")
    public long getOrdersFailed() {
        return ordersFailed.get();
    }

    @ManagedOperation(description = "Reset Statistics")
    public void resetStats() {
        ordersProcessed.set(0);
        ordersFailed.set(0);
    }

    public void incrementProcessed() {
        ordersProcessed.incrementAndGet();
    }

    public void incrementFailed() {
        ordersFailed.incrementAndGet();
    }
}
```

## Event Notifications

### Route Event Notifications

```java
@Component
public class RouteEventNotifier extends EventNotifierSupport {

    private static final Logger log = LoggerFactory.getLogger(RouteEventNotifier.class);

    @Override
    public void notify(CamelEvent event) {
        if (event instanceof CamelEvent.RouteStartedEvent) {
            CamelEvent.RouteStartedEvent routeEvent = (CamelEvent.RouteStartedEvent) event;
            log.info("Route started: {}", routeEvent.getRoute().getId());
        } else if (event instanceof CamelEvent.RouteStoppedEvent) {
            CamelEvent.RouteStoppedEvent routeEvent = (CamelEvent.RouteStoppedEvent) event;
            log.warn("Route stopped: {}", routeEvent.getRoute().getId());
        } else if (event instanceof CamelEvent.ExchangeFailedEvent) {
            CamelEvent.ExchangeFailedEvent failedEvent = (CamelEvent.ExchangeFailedEvent) event;
            log.error("Exchange failed on route: {}", failedEvent.getExchange().getFromRouteId());
        }
    }

    @Override
    public boolean isEnabled(CamelEvent event) {
        return event instanceof CamelEvent.RouteEvent ||
               event instanceof CamelEvent.ExchangeFailedEvent;
    }
}
```

## Performance Monitoring

### Route Performance Metrics

```java
from("timer:stats?period=60000")
    .routeId("route-statistics")
    .process(exchange -> {
        CamelContext context = exchange.getContext();
        context.getRoutes().forEach(route -> {
            String routeId = route.getId();
            MBeanServer server = exchange.getContext().getManagementStrategy()
                .getManagementAgent().getMBeanServer();

            try {
                ObjectName objectName = new ObjectName(
                    "org.apache.camel:context=" + context.getName() +
                    ",type=routes,name=\"" + routeId + "\""
                );

                Long exchangesTotal = (Long) server.getAttribute(objectName, "ExchangesTotal");
                Long exchangesFailed = (Long) server.getAttribute(objectName, "ExchangesFailed");
                Long meanProcessingTime = (Long) server.getAttribute(objectName, "MeanProcessingTime");

                log.info("Route {}: total={}, failed={}, avgTime={}ms",
                    routeId, exchangesTotal, exchangesFailed, meanProcessingTime);
            } catch (Exception e) {
                log.error("Error reading JMX metrics for route: {}", routeId, e);
            }
        });
    });
```

### Throughput Monitoring

```java
from("jms:queue:high-volume")
    .routeId("high-volume-processor")
    .to("micrometer:counter:messages.received")
    .throttle(1000).timePeriodMillis(1000) // Track if throttling occurs
    .to("micrometer:counter:messages.processed")
    .to("direct:process");

from("timer:throughput?period=5000")
    .routeId("throughput-monitor")
    .process(exchange -> {
        MeterRegistry registry = exchange.getContext()
            .getRegistry()
            .lookupByType(MeterRegistry.class)
            .iterator()
            .next();

        Counter received = registry.counter("messages.received");
        Counter processed = registry.counter("messages.processed");

        log.info("Throughput - Received: {}, Processed: {}",
            received.count(), processed.count());
    });
```

## Alerting

### Health-Based Alerts

```java
@Component
public class RouteHealthMonitor {

    @Autowired
    private CamelContext camelContext;

    @Scheduled(fixedRate = 30000)
    public void checkRouteHealth() {
        camelContext.getRoutes().forEach(route -> {
            ServiceStatus status = camelContext.getRouteController()
                .getRouteStatus(route.getId());

            if (!status.isStarted()) {
                sendAlert("Route " + route.getId() + " is not running");
            }
        });
    }

    private void sendAlert(String message) {
        // Send alert via email, Slack, PagerDuty, etc.
        log.error("ALERT: {}", message);
    }
}
```

### Metric-Based Alerts

```java
@Component
public class ErrorRateMonitor {

    @Autowired
    private MeterRegistry meterRegistry;

    @Scheduled(fixedRate = 60000)
    public void checkErrorRate() {
        Counter total = meterRegistry.counter("camel.route.exchanges.total", "route", "order-processor");
        Counter failed = meterRegistry.counter("camel.route.exchanges.failed", "route", "order-processor");

        double errorRate = (failed.count() / total.count()) * 100;

        if (errorRate > 5.0) { // Alert if error rate exceeds 5%
            sendAlert(String.format("High error rate detected: %.2f%%", errorRate));
        }
    }

    private void sendAlert(String message) {
        log.error("ALERT: {}", message);
    }
}
```

## Monitoring Best Practices

1. **Expose Relevant Endpoints**: Only expose necessary actuator endpoints in production
2. **Secure Management Endpoints**: Use authentication and restrict access
3. **Set Appropriate Sampling**: Balance tracing detail with performance impact
4. **Monitor Key Metrics**: Focus on throughput, error rates, and processing times
5. **Set Up Alerts**: Proactively detect and respond to issues
6. **Use Structured Logging**: Facilitate log aggregation and analysis
7. **Regular Health Checks**: Implement readiness and liveness probes
8. **Dashboard Visibility**: Create dashboards for real-time monitoring
9. **Retain Metrics History**: Store metrics for trend analysis
10. **Test Monitoring**: Verify monitoring and alerting in pre-production

## Example: Complete Observability Setup

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus,camelroutes
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: ${spring.application.name}
      environment: ${ENVIRONMENT:dev}

camel:
  springboot:
    jmx-enabled: true
    name: ${spring.application.name}
  opentelemetry:
    enabled: true
  metrics:
    enabled: true

logging:
  level:
    org.apache.camel: INFO
    com.example: DEBUG
  pattern:
    console: "%d{ISO8601} [%thread] %-5level %logger{36} - routeId=%X{camel.routeId} exchangeId=%X{camel.exchangeId} - %msg%n"
```

```java
@Component
public class MonitoredRoute extends RouteBuilder {

    @Override
    public void configure() {
        from("jms:queue:orders")
            .routeId("monitored-order-processor")
            .to("micrometer:counter:orders.received")
            .log("Processing order: ${body.id}")
            .to("micrometer:timer:orders.processing?action=start")
            .to("direct:process-order")
            .to("micrometer:timer:orders.processing?action=stop")
            .to("micrometer:counter:orders.processed")
            .to("jms:queue:processed-orders");

        onException(Exception.class)
            .handled(true)
            .to("micrometer:counter:orders.failed")
            .log(LoggingLevel.ERROR, "Order processing failed: ${exception.message}")
            .to("jms:queue:failed-orders");
    }
}
```

## References

- [Camel Micrometer](https://camel.apache.org/components/latest/micrometer-component.html)
- [Spring Boot Actuator](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html)
- [OpenTelemetry](https://opentelemetry.io/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
