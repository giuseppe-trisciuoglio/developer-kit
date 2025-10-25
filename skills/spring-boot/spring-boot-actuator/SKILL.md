---
name: spring-boot-actuator
description: Expert knowledge on Spring Boot Actuator for production-ready monitoring, health checks, metrics, and management endpoints. Use when implementing or troubleshooting Actuator endpoints, custom health indicators, metrics collection, or production monitoring features.
allowed-tools: Read, Write, Bash
---

# Spring Boot Actuator Patterns

## When to Use

Use this skill when:
- Implementing production monitoring with Spring Boot Actuator
- Creating custom health indicators or endpoints
- Configuring health checks for Kubernetes/Cloud environments
- Setting up metrics collection and export
- Troubleshooting application startup performance
- Customizing the /info endpoint
- Securing Actuator endpoints
- Implementing liveness and readiness probes

## Core Concepts

### What is Actuator?

Spring Boot Actuator brings production-ready features to applications:
- **Monitoring**: Health checks, metrics, application info
- **Management**: Remote application management via HTTP/JMX
- **Diagnostics**: Thread dumps, heap dumps, startup tracking
- **Metrics**: Integration with Micrometer for various monitoring systems

### Key Benefits

- Production-grade monitoring without custom implementation
- Technology-agnostic (works with MVC and WebFlux)
- Extensible through custom endpoints and indicators
- Secure by default with Spring Security integration

## Dependencies

### Maven

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
}
```

## Endpoint Configuration

### Enable and Expose Endpoints

By default, only `/health` and `/info` are exposed:

```yaml
# Expose all endpoints
management:
  endpoints:
    web:
      exposure:
        include: "*"

# Expose specific endpoints
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"

# Expose all except specific ones
management:
  endpoints:
    web:
      exposure:
        include: "*"
        exclude: "env,beans"
```

### Endpoint Security

**Permit all Actuator endpoints** (behind firewall):

```java
@Configuration
public class ActuatorSecurityConfiguration {

    @Bean
    public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
        http.requestMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
        return http.build();
    }
}
```

**Restrict to specific role**:

```java
@Bean
public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
    http.requestMatcher(EndpointRequest.toAnyEndpoint())
        .authorizeHttpRequests(auth -> auth.anyRequest().hasRole("ENDPOINT_ADMIN"));
    return http.build();
}
```

**Mixed security** (public /health, secured others):

```java
@Bean
public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
    return http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/actuator/health/**").permitAll()
            .requestMatchers("/actuator/**").hasRole("ADMIN")
            .anyRequest().authenticated()
        )
        .build();
}
```

### Custom Base Path

```yaml
# Change base path from /actuator to /management
management:
  endpoints:
    web:
      base-path: "/management"

# Disable base path completely
management:
  endpoints:
    web:
      base-path: "/"
      path-mapping:
        health: "healthcheck"
```

### Separate Management Port

```yaml
# Run actuator on different port
management:
  server:
    port: 8081

# Disable HTTP endpoints completely
management:
  server:
    port: -1
```

## Health Indicators

### Built-in Health Indicators

Spring Boot auto-configures health indicators based on dependencies:

- **DiskSpaceHealthIndicator**: Disk space monitoring
- **PingHealthIndicator**: Basic application ping
- **DataSourceHealthIndicator**: Database connectivity (when using JDBC)
- **CassandraHealthIndicator**: Cassandra status
- **MongoHealthIndicator**: MongoDB status
- **RedisHealthIndicator**: Redis connectivity
- **ElasticsearchHealthIndicator**: Elasticsearch status

### Custom Health Indicator

```java
@Component
public class CustomServiceHealthIndicator implements HealthIndicator {

    private final ExternalService externalService;

    public CustomServiceHealthIndicator(ExternalService externalService) {
        this.externalService = externalService;
    }

    @Override
    public Health health() {
        try {
            long responseTime = externalService.ping();
            
            if (responseTime < 100) {
                return Health.up()
                    .withDetail("service", "ExternalAPI")
                    .withDetail("responseTime", responseTime + "ms")
                    .withDetail("status", "Fast")
                    .build();
            } else if (responseTime < 500) {
                return Health.status("WARNING")
                    .withDetail("responseTime", responseTime + "ms")
                    .withDetail("status", "Slow")
                    .build();
            } else {
                return Health.outOfService()
                    .withDetail("responseTime", responseTime + "ms")
                    .withDetail("reason", "Service too slow")
                    .build();
            }
        } catch (Exception ex) {
            return Health.down()
                .withDetail("error", ex.getMessage())
                .withException(ex)
                .build();
        }
    }
}
```

### Reactive Health Indicator

For WebFlux applications:

```java
@Component
public class ReactiveServiceHealthIndicator implements ReactiveHealthIndicator {

    private final WebClient webClient;

    public ReactiveServiceHealthIndicator(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("https://api.example.com").build();
    }

    @Override
    public Mono<Health> health() {
        return webClient.get()
            .uri("/health")
            .retrieve()
            .toBodilessEntity()
            .map(response -> Health.up()
                .withDetail("statusCode", response.getStatusCode().value())
                .build())
            .onErrorResume(ex -> Mono.just(Health.down()
                .withDetail("error", ex.getMessage())
                .build()));
    }
}
```

### Health Configuration

```yaml
management:
  endpoint:
    health:
      # Show details: never, when-authorized, always
      show-details: always
      show-components: always
      
      # Disable specific indicator
      enabled:
        diskspace: false
        
      # Custom status mappings
      status:
        order: "fatal,down,out-of-service,warning,unknown,up"
        http-mapping:
          down: 503
          fatal: 503
          out-of-service: 503
          warning: 500
```

### Health Groups

Create custom health groups for different purposes:

```yaml
management:
  endpoint:
    health:
      group:
        # Liveness probe - basic checks
        liveness:
          include: "ping,diskSpace"
          show-details: always
          
        # Readiness probe - includes dependencies
        readiness:
          include: "readinessState,db,redis"
          show-details: when-authorized
          
        # Custom group
        database:
          include: "db"
          show-details: always
          status:
            http-mapping:
              up: 207
```

**Access health groups**:
- `/actuator/health/liveness`
- `/actuator/health/readiness`
- `/actuator/health/database`

### Kubernetes Probes

```yaml
# application.yml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        liveness:
          include: "livenessState"
        readiness:
          include: "readinessState,db,redis"
```

**Kubernetes deployment**:

```yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

**Expose on main port**:

```yaml
management:
  endpoint:
    health:
      probes:
        add-additional-paths: true
```

This exposes `/livez` and `/readyz` on main server port.

### Disable Health Indicator

```java
@Component
@ConditionalOnEnabledHealthIndicator("custom")
public class CustomHealthIndicator implements HealthIndicator {
    // Implementation
}
```

```yaml
management:
  health:
    custom:
      enabled: false
```

## Custom Info Endpoint

### Static Properties

```yaml
info:
  app:
    name: "My Spring Boot Application"
    description: "Production API Service"
    version: "1.0.0"
    encoding: "UTF-8"
    java:
      version: "@java.version@"
```

### Environment Variables

```yaml
info:
  java-vendor: "${java.specification.vendor}"
  os-name: "${os.name}"
  spring-version: "${spring-framework.version}"
```

### Git Information

Add Maven plugin:

```xml
<plugin>
    <groupId>pl.project13.maven</groupId>
    <artifactId>git-commit-id-plugin</artifactId>
</plugin>
```

Configuration:

```yaml
management:
  info:
    git:
      mode: full  # or "simple"
      enabled: true
```

### Build Information

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals>
                <goal>build-info</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### Custom Info Contributor

```java
@Component
public class ApplicationInfoContributor implements InfoContributor {

    private final UserRepository userRepository;
    private final OrderRepository orderRepository;

    public ApplicationInfoContributor(
            UserRepository userRepository,
            OrderRepository orderRepository) {
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
    }

    @Override
    public void contribute(Info.Builder builder) {
        Map<String, Object> stats = Map.of(
            "users", Map.of(
                "total", userRepository.count(),
                "active", userRepository.countByStatus("ACTIVE")
            ),
            "orders", Map.of(
                "total", orderRepository.count(),
                "pending", orderRepository.countByStatus("PENDING")
            ),
            "uptime", ManagementFactory.getRuntimeMXBean().getUptime()
        );
        
        builder.withDetail("statistics", stats);
    }
}
```

## Metrics

### Available Metrics

Common metrics exposed by default:
- **JVM**: `jvm.memory.used`, `jvm.memory.max`, `jvm.gc.pause`
- **CPU**: `system.cpu.usage`, `process.cpu.usage`
- **HTTP**: `http.server.requests`
- **Database**: `jdbc.connections.active`, `jdbc.connections.max`
- **Tomcat**: `tomcat.sessions.active.max`

### Query Metrics

```bash
# List all metrics
curl http://localhost:8080/actuator/metrics

# Get specific metric
curl http://localhost:8080/actuator/metrics/jvm.memory.used

# Filter by tags
curl "http://localhost:8080/actuator/metrics/jvm.memory.used?tag=area:heap"
```

### Custom Metrics with Micrometer

```java
@Service
public class OrderService {

    private final MeterRegistry meterRegistry;
    private final Counter orderCounter;
    private final Timer orderProcessingTimer;

    public OrderService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.orderCounter = Counter.builder("orders.created")
            .description("Total number of orders created")
            .tag("service", "order")
            .register(meterRegistry);
            
        this.orderProcessingTimer = Timer.builder("order.processing.time")
            .description("Order processing duration")
            .register(meterRegistry);
    }

    public Order createOrder(OrderRequest request) {
        return orderProcessingTimer.record(() -> {
            Order order = processOrder(request);
            orderCounter.increment();
            
            // Record gauge
            meterRegistry.gauge("orders.pending", 
                orderRepository.countByStatus("PENDING"));
                
            return order;
        });
    }
}
```

### Metrics Export

**Prometheus**:

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
```

**Datadog**:

```yaml
management:
  datadog:
    metrics:
      export:
        enabled: true
        api-key: "${DATADOG_API_KEY}"
        uri: "https://api.datadoghq.eu"
        step: "30s"
```

## Custom Endpoints

### Create Custom Endpoint

```java
@Component
@Endpoint(id = "features")
public class FeaturesEndpoint {

    private final Map<String, Feature> features = new ConcurrentHashMap<>();

    @ReadOperation
    public Map<String, Feature> features() {
        return features;
    }

    @ReadOperation
    public Feature feature(@Selector String name) {
        return features.get(name);
    }

    @WriteOperation
    public void configureFeature(@Selector String name, Feature feature) {
        features.put(name, feature);
    }

    @DeleteOperation
    public void deleteFeature(@Selector String name) {
        features.remove(name);
    }

    public static class Feature {
        private boolean enabled;
        private String description;

        // Getters and setters
        public boolean isEnabled() { return enabled; }
        public void setEnabled(boolean enabled) { this.enabled = enabled; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
    }
}
```

**Operations map to HTTP methods**:
- `@ReadOperation` → GET
- `@WriteOperation` → POST
- `@DeleteOperation` → DELETE

**Usage**:
```bash
# List all features
curl http://localhost:8080/actuator/features

# Get specific feature
curl http://localhost:8080/actuator/features/dark-mode

# Configure feature
curl -X POST http://localhost:8080/actuator/features/dark-mode \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"description":"Dark mode UI"}'

# Delete feature
curl -X DELETE http://localhost:8080/actuator/features/dark-mode
```

### Web-Specific Endpoint

```java
@Component
@WebEndpoint(id = "appstatus")
public class AppStatusWebEndpoint {

    @ReadOperation
    public WebEndpointResponse<Map<String, Object>> status() {
        Map<String, Object> status = new HashMap<>();
        status.put("status", "RUNNING");
        status.put("timestamp", System.currentTimeMillis());
        
        return new WebEndpointResponse<>(status, 200);
    }
}
```

### Extend Existing Endpoint

```java
@Component
@EndpointWebExtension(endpoint = InfoEndpoint.class)
public class CustomInfoWebEndpointExtension {

    private final InfoEndpoint delegate;

    public CustomInfoWebEndpointExtension(InfoEndpoint delegate) {
        this.delegate = delegate;
    }

    @ReadOperation
    public WebEndpointResponse<Map<String, Object>> info() {
        Map<String, Object> info = this.delegate.info();
        
        // Add custom logic
        String version = (String) info.get("version");
        if (version != null && version.contains("SNAPSHOT")) {
            return new WebEndpointResponse<>(info, 503);
        }
        
        return new WebEndpointResponse<>(info, 200);
    }
}
```

## Startup Tracking

### Enable Startup Tracking

```java
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(Application.class);
        app.setApplicationStartup(new BufferingApplicationStartup(2048));
        app.run(args);
    }
}
```

### Configuration

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "startup"
```

### Query Startup Information

```bash
# Get startup metrics (POST clears buffer)
curl -X POST http://localhost:8080/actuator/startup | jq

# Filter on bean instantiation
curl -X POST http://localhost:8080/actuator/startup | \
  jq '[.timeline.events | sort_by(.duration) | reverse[] | 
      select(.startupStep.name | match("spring.beans.instantiate")) | 
      {beanName: .startupStep.tags[0].value, duration: .duration}]'
```

### Custom Startup Instrumentation

```java
@Configuration
public class StartupConfiguration {

    @Bean
    public BufferingApplicationStartup applicationStartup() {
        BufferingApplicationStartup startup = new BufferingApplicationStartup(2048);
        
        // Filter specific steps
        startup.addFilter(step -> 
            step.getName().matches("spring.beans.instantiate")
        );
        
        return startup;
    }
}
```

## Advanced Patterns

### Conditional Endpoint Access

```yaml
management:
  endpoints:
    access:
      default: none  # Opt-in by default
  endpoint:
    health:
      access: unrestricted
    info:
      access: read-only
    metrics:
      access: read-only
```

### Sanitize Sensitive Data

```yaml
management:
  endpoint:
    env:
      show-values: when-authorized
      roles: "admin"
    configprops:
      show-values: never
```

### Cache Endpoint Results

```yaml
management:
  endpoint:
    beans:
      cache:
        time-to-live: "10s"
```

### Custom Health Status

```java
public class CustomHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        // Custom status
        return Health.status("DEGRADED")
            .withDetail("reason", "High load")
            .build();
    }
}
```

```yaml
management:
  endpoint:
    health:
      status:
        order: "down,degraded,up"
        http-mapping:
          degraded: 200  # or 207 for partial success
```

## Best Practices

### Security

1. **Never expose sensitive endpoints** without authentication
2. **Use separate management port** for production
3. **Implement role-based access** for write operations
4. **Sanitize environment variables** in /env endpoint
5. **Disable endpoints** not needed in production

### Performance

1. **Use health groups** instead of full health check
2. **Cache expensive health checks** with TTL
3. **Filter startup events** to reduce memory usage
4. **Limit metrics cardinality** (avoid unbounded tags)
5. **Use read-only access** where possible

### Monitoring

1. **Separate liveness from readiness** probes
2. **Include external dependencies** in readiness only
3. **Set appropriate timeouts** for health checks
4. **Monitor startup time** to detect performance regressions
5. **Export metrics to monitoring systems** (Prometheus, Datadog)

### Development

1. **Enable all endpoints** in development
2. **Use startup tracking** to optimize boot time
3. **Create custom endpoints** for debugging
4. **Add detailed health information** for troubleshooting
5. **Test health indicators** independently

## Common Patterns

### Health Check Hierarchy

```java
@Component
public class DatabaseClusterHealthIndicator implements HealthIndicator {

    private final List<DataSource> dataSources;

    @Override
    public Health health() {
        Health.Builder builder = Health.up();
        
        for (int i = 0; i < dataSources.size(); i++) {
            try {
                DataSource ds = dataSources.get(i);
                ds.getConnection().isValid(1000);
                builder.withDetail("node-" + i, "UP");
            } catch (Exception ex) {
                builder.down().withDetail("node-" + i, "DOWN");
            }
        }
        
        return builder.build();
    }
}
```

### Circuit Breaker Integration

```java
@Component
public class ExternalApiHealthIndicator implements HealthIndicator {

    private final CircuitBreaker circuitBreaker;
    private final ExternalApiClient client;

    @Override
    public Health health() {
        CircuitBreaker.State state = circuitBreaker.getState();
        
        if (state == CircuitBreaker.State.OPEN) {
            return Health.down()
                .withDetail("circuitBreaker", "OPEN")
                .build();
        }
        
        try {
            client.ping();
            return Health.up()
                .withDetail("circuitBreaker", state.toString())
                .build();
        } catch (Exception ex) {
            return Health.down(ex).build();
        }
    }
}
```

### Business Metrics

```java
@Service
public class MetricsService {

    private final MeterRegistry registry;

    public MetricsService(MeterRegistry registry) {
        this.registry = registry;
    }

    public void recordUserLogin(String userType) {
        registry.counter("user.login", "type", userType).increment();
    }

    public void recordOrderAmount(double amount, String currency) {
        registry.summary("order.amount", "currency", currency)
            .record(amount);
    }

    public void trackActiveConnections(Supplier<Integer> supplier) {
        registry.gauge("connections.active", supplier);
    }
}
```

## Troubleshooting

### Endpoints Not Visible

```yaml
# Verify exposure
management:
  endpoints:
    web:
      exposure:
        include: "*"
```

### Health Details Hidden

```yaml
# Show details
management:
  endpoint:
    health:
      show-details: always
      show-components: always
```

### Security Blocking Access

```java
// Check security configuration
@Bean
public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
    http.requestMatcher(EndpointRequest.toAnyEndpoint())
        .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
    return http.build();
}
```

### Startup Endpoint Empty

Ensure `BufferingApplicationStartup` is configured in main method.

### Custom Indicator Not Working

1. Verify `@Component` annotation
2. Check class implements `HealthIndicator`
3. Ensure not disabled in configuration
4. Check for exceptions in health() method

## References

- [Spring Boot Actuator Official Documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html)
- [Micrometer Documentation](https://micrometer.io/docs)
- [Spring Boot Actuator API](https://docs.spring.io/spring-boot/docs/current/actuator-api/htmlsingle/)
