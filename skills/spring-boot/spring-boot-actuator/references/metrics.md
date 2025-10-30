# Metrics with Spring Boot Actuator

Spring Boot Actuator provides dependency management and auto-configuration for [Micrometer](https://micrometer.io/), an application metrics facade that supports numerous monitoring systems, including:

- AppOptics
- Atlas
- Datadog
- Dynatrace
- Elastic
- Ganglia
- Graphite
- Humio
- InfluxDB
- JMX
- KairosDB
- New Relic
- OpenTelemetry Protocol (OTLP)
- Prometheus
- Simple (in-memory)
- Google Cloud Monitoring (Stackdriver)
- StatsD
- Wavefront

> **TIP**
> 
> To learn more about Micrometer's capabilities, see its [reference documentation](https://micrometer.io/docs), in particular the [concepts section](https://micrometer.io/docs/concepts).

## Getting Started

Spring Boot auto-configures a composite `MeterRegistry` and adds a registry to the composite for each of the supported implementations that it finds on the classpath. Having a dependency on `micrometer-registry-{system}` in your runtime classpath is enough for Spring Boot to configure the registry.

Most registries share common features. For instance, you can disable a particular registry even if the Micrometer registry implementation is on the classpath. The following example disables Datadog:

```yaml
management:
  datadog:
    metrics:
      export:
        enabled: false
```

You can also disable all registries unless stated otherwise by the registry-specific property, as the following example shows:

```yaml
management:
  defaults:
    metrics:
      export:
        enabled: false
```

Spring Boot also adds any auto-configured registries to the global static composite registry on the `Metrics` class, unless you explicitly tell it not to:

```yaml
management:
  metrics:
    use-global-registry: false
```

You can register any number of `MeterRegistryCustomizer` beans to further configure the registry, such as applying common tags, before any meters are registered with the registry:

```java
@Component
public class MyMeterRegistryConfiguration {

    @Bean
    public MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> registry.config().commonTags("region", "us-east-1");
    }
}
```

You can apply customizations to particular registry implementations by being more specific about the generic type:

```java
@Component
public class MyMeterRegistryConfiguration {

    @Bean
    public MeterRegistryCustomizer<GraphiteMeterRegistry> graphiteMetricsNamingConvention() {
        return registry -> registry.config().namingConvention(this::toGraphiteConvention);
    }

    private String toGraphiteConvention(String name, Meter.Type type, String baseUnit) {
        return name.toLowerCase().replace(".", "_");
    }
}
```

Spring Boot also configures built-in instrumentation that you can control through configuration or dedicated annotation markers.

## Supported Metrics

Spring Boot provides automatic meter registration for a wide variety of technologies. In most situations, the defaults provide sensible metrics that can be published to any of the supported monitoring systems.

### JVM Metrics

JVM metrics are published under the `jvm.` meter name. The following JVM metrics are provided:

- Memory and buffer pools
- Statistics related to garbage collection
- Thread utilization
- Number of classes loaded/unloaded

### System Metrics

System metrics are published under the `system.`, `process.`, and `disk.` meter names. The following system metrics are provided:

- CPU metrics
- File descriptor metrics
- Uptime metrics
- Disk space metrics

### Application Startup Metrics

Application startup metrics are published under the `application.started.time` meter name. The following startup metrics are provided:

- Application startup time
- Application ready time

### HTTP Request Metrics

HTTP request metrics are automatically recorded for all HTTP requests. Metrics are published under the `http.server.requests` meter name.

Tags added to HTTP server request metrics:

- `method`: The request's HTTP method (e.g., `GET` or `POST`)
- `uri`: The request's URI template prior to variable substitution (e.g., `/api/person/{id}`)
- `status`: The response's HTTP status code (e.g., `200` or `500`)
- `outcome`: The request's outcome based on the status code (`SUCCESS`, `REDIRECTION`, `CLIENT_ERROR`, `SERVER_ERROR`, or `UNKNOWN`)

To customize the tags, provide a `@Bean` that implements `WebMvcTagsContributor`:

```java
@Component
public class MyWebMvcTagsContributor implements WebMvcTagsContributor {

    @Override
    public Iterable<Tag> getTags(HttpServletRequest request, 
                                 HttpServletResponse response, 
                                 Object handler, 
                                 Throwable exception) {
        return Tags.of("custom.tag", "custom-value");
    }

    @Override
    public Iterable<Tag> getLongRequestTags(HttpServletRequest request, 
                                           Object handler) {
        return Tags.of("custom.tag", "custom-value");
    }
}
```

### WebFlux Metrics

WebFlux metrics are automatically recorded for all WebFlux requests. Metrics are published under the `http.server.requests` meter name.

Tags added to WebFlux request metrics:

- `method`: The request's HTTP method
- `uri`: The request's URI template
- `status`: The response's HTTP status code
- `outcome`: The request's outcome

### Data Source Metrics

Auto-configuration enables the instrumentation of all available DataSource objects with metrics prefixed with `hikaricp.`, `tomcat.datasource.`, or `dbcp2.`.

Connection pool metrics are published under the following meter names:

- `hikaricp.connections` (HikariCP)
- `tomcat.datasource.connections` (Tomcat)
- `dbcp2.connections` (Apache DBCP2)

### Cache Metrics

Auto-configuration enables the instrumentation of all available Cache managers on startup with metrics prefixed with `cache.`. The cache instrumentation is standardized for a basic set of metrics.

Cache metrics include:

- Size
- Hit ratio
- Evictions
- Puts and misses

### Task Execution and Scheduling Metrics

Auto-configuration enables the instrumentation of all available `ThreadPoolTaskExecutor` and `ThreadPoolTaskScheduler` beans with metrics prefixed with `executor.` and `scheduler.` respectively.

Executor metrics include:

- Active threads
- Pool size
- Queue size
- Task completion

## Custom Metrics

To record your own metrics, inject `MeterRegistry` into your component:

```java
@Component
public class MyService {
    private final Counter counter;
    private final Timer timer;
    private final Gauge gauge;

    public MyService(MeterRegistry meterRegistry) {
        this.counter = Counter.builder("my.counter")
                .description("A simple counter")
                .register(meterRegistry);
        
        this.timer = Timer.builder("my.timer")
                .description("A simple timer")
                .register(meterRegistry);
        
        this.gauge = Gauge.builder("my.gauge")
                .description("A simple gauge")
                .register(meterRegistry, this, MyService::calculateGaugeValue);
    }

    public void doSomething() {
        counter.increment();
        
        Timer.Sample sample = Timer.start(meterRegistry);
        // ... do work
        sample.stop(timer);
    }
    
    private double calculateGaugeValue(MyService self) {
        return Math.random();
    }
}
```

### Using @Timed Annotation

You can use the `@Timed` annotation to time method executions:

```java
@Component
public class MyService {

    @Timed(name = "my.method.time", description = "Time taken to execute my method")
    public void timedMethod() {
        // method body
    }
}
```

For the `@Timed` annotation to work, you need to enable timing support:

```java
@Configuration
@EnableConfigurationProperties
public class TimedConfiguration {

    @Bean
    public TimedAspect timedAspect(MeterRegistry registry) {
        return new TimedAspect(registry);
    }
}
```

### Using @Counted Annotation

You can use the `@Counted` annotation to count method invocations:

```java
@Component
public class MyService {

    @Counted(name = "my.method.count", description = "Number of times my method is called")
    public void countedMethod() {
        // method body
    }
}
```

For the `@Counted` annotation to work, you need to enable counting support:

```java
@Configuration
public class CountedConfiguration {

    @Bean
    public CountedAspect countedAspect(MeterRegistry registry) {
        return new CountedAspect(registry);
    }
}
```

## Meter Filters

You can register any number of `MeterFilter` beans to control how meters are registered:

```java
@Configuration
public class MetricsConfiguration {

    @Bean
    public MeterFilter renameFilter() {
        return MeterFilter.rename("old.metric.name", "new.metric.name");
    }

    @Bean
    public MeterFilter denyFilter() {
        return MeterFilter.deny(id -> id.getName().contains("unwanted"));
    }

    @Bean
    public MeterFilter tagFilter() {
        return MeterFilter.commonTags("application", "my-app");
    }
}
```

## Metrics Endpoint

The `metrics` endpoint provides access to all the metrics collected by the application. You can view the names of all available meters by visiting `/actuator/metrics`.

To view the value of a particular meter, specify its name as a path parameter:

```
GET /actuator/metrics/jvm.memory.used
```

The response contains the meter's measurements:

```json
{
  "name": "jvm.memory.used",
  "description": "The amount of used memory",
  "baseUnit": "bytes",
  "measurements": [
    {
      "statistic": "VALUE",
      "value": 8.73E8
    }
  ],
  "availableTags": [
    {
      "tag": "area",
      "values": ["heap", "nonheap"]
    },
    {
      "tag": "id",
      "values": ["Compressed Class Space", "PS Eden Space", "PS Survivor Space"]
    }
  ]
}
```

You can drill down to a particular meter by adding query parameters:

```
GET /actuator/metrics/jvm.memory.used?tag=area:heap&tag=id:PS%20Eden%20Space
```

## Monitoring System Integration

### Prometheus

To export metrics to Prometheus, add the following dependency:

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

This exposes a `/actuator/prometheus` endpoint that presents metrics in the format expected by a Prometheus server.

Configuration example:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "prometheus"
  metrics:
    export:
      prometheus:
        enabled: true
        step: 1m
        descriptions: true
```

### Datadog

To export metrics to Datadog, add the following dependency:

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-datadog</artifactId>
</dependency>
```

Configuration:

```yaml
management:
  metrics:
    export:
      datadog:
        api-key: ${DATADOG_API_KEY}
        application-key: ${DATADOG_APP_KEY}
        uri: https://api.datadoghq.com
        step: 1m
```

### InfluxDB

To export metrics to InfluxDB, add the following dependency:

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-influx</artifactId>
</dependency>
```

Configuration:

```yaml
management:
  metrics:
    export:
      influx:
        uri: http://localhost:8086
        db: mydb
        username: ${INFLUX_USERNAME}
        password: ${INFLUX_PASSWORD}
        step: 1m
```

### New Relic

To export metrics to New Relic, add the following dependency:

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-newrelic</artifactId>
</dependency>
```

Configuration:

```yaml
management:
  metrics:
    export:
      newrelic:
        api-key: ${NEW_RELIC_API_KEY}
        account-id: ${NEW_RELIC_ACCOUNT_ID}
        step: 1m
```

### Simple Registry (In-Memory)

The simple registry is automatically configured if no other registry is found on the classpath. It stores metrics in memory and is useful for development and testing:

```yaml
management:
  metrics:
    export:
      simple:
        enabled: true
        step: 1m
```

## Performance Considerations

### Meter Cardinality

Be mindful of meter cardinality when adding tags. High-cardinality tags (like user IDs) can lead to performance issues:

```java
// Bad - high cardinality
Timer.builder("user.request.time")
    .tag("user.id", userId)  // Could be millions of different values
    .register(registry);

// Good - low cardinality
Timer.builder("user.request.time")
    .tag("user.type", userType)  // Limited number of values
    .register(registry);
```

### Sampling

For high-throughput applications, consider using sampling to reduce overhead:

```java
@Bean
public MeterFilter samplingFilter() {
    return MeterFilter.maximumExpectedValue("http.server.requests", 
                                           Duration.ofMillis(500));
}
```

### Meter Registry Configuration

Configure appropriate publishing intervals to balance between timeliness and performance:

```yaml
management:
  metrics:
    export:
      prometheus:
        step: 30s  # Adjust based on your needs
```

## Security Considerations

### Sensitive Data

Be careful not to include sensitive information in metric tags or names:

```java
// Bad - exposes sensitive data
Counter.builder("login.attempts")
    .tag("username", username)  // Could expose usernames
    .register(registry);

// Good - uses hashed or anonymized data
Counter.builder("login.attempts")
    .tag("outcome", successful ? "success" : "failure")
    .register(registry);
```

### Endpoint Security

Secure the metrics endpoint in production:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "metrics"
  endpoint:
    metrics:
      access: restricted
```

Or using Spring Security:

```java
@Configuration
public class ActuatorSecurity {

    @Bean
    public SecurityFilterChain actuatorSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .requestMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(requests -> 
                requests.anyRequest().hasRole("ACTUATOR"))
            .httpBasic(withDefaults())
            .build();
    }
}
```

## Best Practices

1. **Use meaningful meter names**: Follow naming conventions specific to your monitoring system
2. **Add appropriate tags**: Use tags to add dimensions but avoid high cardinality
3. **Monitor meter cardinality**: High cardinality can impact performance
4. **Use meter filters**: Filter out unwanted metrics or rename meters
5. **Configure appropriate publishing intervals**: Balance between timeliness and performance
6. **Secure sensitive endpoints**: Protect metrics endpoints in production
7. **Test metrics in development**: Verify metrics are collected correctly before deploying
8. **Document custom metrics**: Maintain documentation for custom metrics and their purposes