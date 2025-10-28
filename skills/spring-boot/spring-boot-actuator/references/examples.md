# Spring Boot Actuator Examples

## Complete Application Example

### Application Configuration

```java
@SpringBootApplication
public class MonitoringApplication {

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(MonitoringApplication.class);
        // Enable startup tracking
        app.setApplicationStartup(new BufferingApplicationStartup(2048));
        app.run(args);
    }

    @Bean
    public MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> registry.config()
            .commonTags("application", "order-service", "environment", "production");
    }
}
```

### Application Properties

```yaml
spring:
  application:
    name: order-service

info:
  app:
    name: ${spring.application.name}
    description: Order Processing Service
    version: "@project.version@"
    encoding: "@project.build.sourceEncoding@"
    java:
      version: "@java.version@"

management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus,startup"
      base-path: "/actuator"
  
  endpoint:
    health:
      show-details: when-authorized
      show-components: always
      probes:
        enabled: true
      group:
        liveness:
          include: "ping,diskSpace"
        readiness:
          include: "readinessState,db,redis,externalApi"
          show-details: always
      status:
        order: "fatal,down,out-of-service,warning,unknown,up"
        http-mapping:
          down: 503
          fatal: 503
          warning: 500
    
    info:
      enabled: true
    
    metrics:
      enabled: true
  
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: ${spring.application.name}
      region: eu-west-1

  info:
    git:
      mode: full
    build:
      enabled: true
```

## Health Indicators Examples

### Database Health Indicator

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {

    private static final Logger log = LoggerFactory.getLogger(DatabaseHealthIndicator.class);
    private final DataSource dataSource;

    public DatabaseHealthIndicator(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            long startTime = System.currentTimeMillis();
            boolean valid = connection.isValid(1000);
            long responseTime = System.currentTimeMillis() - startTime;

            if (!valid) {
                return Health.down()
                    .withDetail("database", "Connection not valid")
                    .build();
            }

            DatabaseMetaData metaData = connection.getMetaData();
            
            Health.Builder builder = Health.up()
                .withDetail("database", metaData.getDatabaseProductName())
                .withDetail("version", metaData.getDatabaseProductVersion())
                .withDetail("responseTime", responseTime + "ms");

            if (responseTime > 500) {
                builder.status("WARNING")
                    .withDetail("warning", "Slow database connection");
            }

            return builder.build();

        } catch (SQLException ex) {
            log.error("Database health check failed", ex);
            return Health.down()
                .withDetail("error", ex.getMessage())
                .withException(ex)
                .build();
        }
    }
}
```

### External API Health Indicator with Circuit Breaker

```java
@Component
public class PaymentGatewayHealthIndicator implements HealthIndicator {

    private final RestTemplate restTemplate;
    private final CircuitBreaker circuitBreaker;

    public PaymentGatewayHealthIndicator(
            RestTemplate restTemplate,
            @Qualifier("paymentCircuitBreaker") CircuitBreaker circuitBreaker) {
        this.restTemplate = restTemplate;
        this.circuitBreaker = circuitBreaker;
    }

    @Override
    public Health health() {
        CircuitBreaker.State state = circuitBreaker.getState();
        
        Health.Builder builder = Health.up()
            .withDetail("circuitBreaker", state.toString())
            .withDetail("service", "Payment Gateway");

        if (state == CircuitBreaker.State.OPEN) {
            return builder
                .down()
                .withDetail("reason", "Circuit breaker is open")
                .build();
        }

        if (state == CircuitBreaker.State.HALF_OPEN) {
            builder.status("WARNING")
                .withDetail("reason", "Circuit breaker is testing");
        }

        try {
            long startTime = System.currentTimeMillis();
            ResponseEntity<Map> response = restTemplate.getForEntity(
                "https://api.payment.com/health", 
                Map.class
            );
            long responseTime = System.currentTimeMillis() - startTime;

            return builder
                .withDetail("responseTime", responseTime + "ms")
                .withDetail("statusCode", response.getStatusCode().value())
                .build();

        } catch (Exception ex) {
            return builder
                .down()
                .withDetail("error", ex.getMessage())
                .build();
        }
    }
}
```

### Cache Health Indicator

```java
@Component
public class CacheHealthIndicator implements HealthIndicator {

    private final CacheManager cacheManager;

    public CacheHealthIndicator(CacheManager cacheManager) {
        this.cacheManager = cacheManager;
    }

    @Override
    public Health health() {
        Collection<String> cacheNames = cacheManager.getCacheNames();
        
        Map<String, Object> cacheDetails = new HashMap<>();
        boolean allHealthy = true;

        for (String cacheName : cacheNames) {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache != null) {
                try {
                    // Test cache operations
                    cache.put("health-check", "test");
                    String value = cache.get("health-check", String.class);
                    cache.evict("health-check");
                    
                    cacheDetails.put(cacheName, "UP");
                } catch (Exception ex) {
                    cacheDetails.put(cacheName, "DOWN: " + ex.getMessage());
                    allHealthy = false;
                }
            }
        }

        Health.Builder builder = allHealthy ? Health.up() : Health.down();
        return builder
            .withDetail("caches", cacheDetails)
            .withDetail("totalCaches", cacheNames.size())
            .build();
    }
}
```

### Reactive Health Indicator

```java
@Component
public class ReactiveExternalServiceHealthIndicator implements ReactiveHealthIndicator {

    private final WebClient webClient;

    public ReactiveExternalServiceHealthIndicator(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
            .baseUrl("https://api.example.com")
            .build();
    }

    @Override
    public Mono<Health> health() {
        return webClient
            .get()
            .uri("/health")
            .retrieve()
            .toBodilessEntity()
            .map(response -> Health.up()
                .withDetail("statusCode", response.getStatusCode().value())
                .withDetail("service", "External API")
                .build())
            .timeout(Duration.ofSeconds(2))
            .onErrorResume(TimeoutException.class, ex -> 
                Mono.just(Health.down()
                    .withDetail("error", "Timeout after 2 seconds")
                    .build()))
            .onErrorResume(ex -> 
                Mono.just(Health.down()
                    .withDetail("error", ex.getMessage())
                    .build()));
    }
}
```

## Custom Endpoints Examples

### Application Statistics Endpoint

```java
@Component
@Endpoint(id = "appstats")
public class AppStatisticsEndpoint {

    private final UserRepository userRepository;
    private final OrderRepository orderRepository;
    private final MeterRegistry meterRegistry;

    public AppStatisticsEndpoint(
            UserRepository userRepository,
            OrderRepository orderRepository,
            MeterRegistry meterRegistry) {
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
        this.meterRegistry = meterRegistry;
    }

    @ReadOperation
    public Map<String, Object> getStatistics() {
        Map<String, Object> stats = new HashMap<>();
        
        // User statistics
        stats.put("users", Map.of(
            "total", userRepository.count(),
            "active", userRepository.countByStatus("ACTIVE"),
            "inactive", userRepository.countByStatus("INACTIVE")
        ));
        
        // Order statistics
        stats.put("orders", Map.of(
            "total", orderRepository.count(),
            "pending", orderRepository.countByStatus("PENDING"),
            "completed", orderRepository.countByStatus("COMPLETED"),
            "cancelled", orderRepository.countByStatus("CANCELLED")
        ));
        
        // JVM statistics
        stats.put("jvm", Map.of(
            "memoryUsed", getMetricValue("jvm.memory.used"),
            "memoryMax", getMetricValue("jvm.memory.max"),
            "threadCount", getMetricValue("jvm.threads.live")
        ));
        
        stats.put("timestamp", Instant.now());
        
        return stats;
    }

    @ReadOperation
    public Map<String, Object> getStatisticsByType(@Selector String type) {
        return switch (type.toLowerCase()) {
            case "users" -> Map.of(
                "total", userRepository.count(),
                "byStatus", userRepository.countByStatusGrouped()
            );
            case "orders" -> Map.of(
                "total", orderRepository.count(),
                "byStatus", orderRepository.countByStatusGrouped()
            );
            default -> Map.of("error", "Unknown type: " + type);
        };
    }

    private Double getMetricValue(String meterName) {
        return meterRegistry.find(meterName)
            .gauge()
            .map(Gauge::value)
            .orElse(0.0);
    }
}
```

### Feature Flags Endpoint

```java
@Component
@Endpoint(id = "features")
public class FeatureFlagsEndpoint {

    private final Map<String, FeatureFlag> features = new ConcurrentHashMap<>();
    private final ApplicationEventPublisher eventPublisher;

    public FeatureFlagsEndpoint(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
        initializeDefaultFeatures();
    }

    private void initializeDefaultFeatures() {
        features.put("dark-mode", new FeatureFlag(true, "Dark mode UI"));
        features.put("new-checkout", new FeatureFlag(false, "New checkout flow"));
        features.put("ai-recommendations", new FeatureFlag(false, "AI-powered recommendations"));
    }

    @ReadOperation
    public Map<String, FeatureFlag> getAllFeatures() {
        return features;
    }

    @ReadOperation
    public FeatureFlag getFeature(@Selector String name) {
        return features.get(name);
    }

    @WriteOperation
    public void updateFeature(
            @Selector String name,
            @Nullable Boolean enabled,
            @Nullable String description) {
        
        features.compute(name, (key, existing) -> {
            if (existing == null) {
                existing = new FeatureFlag(false, "");
            }
            
            if (enabled != null) {
                existing.setEnabled(enabled);
            }
            if (description != null) {
                existing.setDescription(description);
            }
            
            return existing;
        });

        eventPublisher.publishEvent(new FeatureFlagChangedEvent(name, features.get(name)));
    }

    @DeleteOperation
    public void deleteFeature(@Selector String name) {
        FeatureFlag removed = features.remove(name);
        if (removed != null) {
            eventPublisher.publishEvent(new FeatureFlagDeletedEvent(name));
        }
    }

    public static class FeatureFlag {
        private boolean enabled;
        private String description;
        private Instant lastModified = Instant.now();

        public FeatureFlag() {}

        public FeatureFlag(boolean enabled, String description) {
            this.enabled = enabled;
            this.description = description;
        }

        // Getters and setters
        public boolean isEnabled() { return enabled; }
        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
            this.lastModified = Instant.now();
        }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        public Instant getLastModified() { return lastModified; }
    }
}
```

### Cache Management Endpoint

```java
@Component
@Endpoint(id = "caches")
public class CacheManagementEndpoint {

    private final CacheManager cacheManager;

    public CacheManagementEndpoint(CacheManager cacheManager) {
        this.cacheManager = cacheManager;
    }

    @ReadOperation
    public Map<String, Object> getCaches() {
        Collection<String> cacheNames = cacheManager.getCacheNames();
        Map<String, Object> result = new HashMap<>();
        
        result.put("totalCaches", cacheNames.size());
        result.put("caches", cacheNames);
        
        return result;
    }

    @ReadOperation
    public Map<String, Object> getCache(@Selector String cacheName) {
        Cache cache = cacheManager.getCache(cacheName);
        if (cache == null) {
            return Map.of("error", "Cache not found: " + cacheName);
        }

        return Map.of(
            "name", cacheName,
            "type", cache.getClass().getSimpleName()
        );
    }

    @DeleteOperation
    public void clearCache(@Selector String cacheName) {
        Cache cache = cacheManager.getCache(cacheName);
        if (cache != null) {
            cache.clear();
        }
    }

    @WriteOperation
    public void clearAllCaches() {
        cacheManager.getCacheNames()
            .forEach(name -> {
                Cache cache = cacheManager.getCache(name);
                if (cache != null) {
                    cache.clear();
                }
            });
    }
}
```

## Custom Info Contributors

### Detailed Application Info

```java
@Component
public class DetailedApplicationInfoContributor implements InfoContributor {

    private final Environment environment;
    private final UserRepository userRepository;
    private final OrderRepository orderRepository;

    public DetailedApplicationInfoContributor(
            Environment environment,
            UserRepository userRepository,
            OrderRepository orderRepository) {
        this.environment = environment;
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
    }

    @Override
    public void contribute(Info.Builder builder) {
        // Runtime information
        Runtime runtime = Runtime.getRuntime();
        builder.withDetail("runtime", Map.of(
            "processors", runtime.availableProcessors(),
            "freeMemory", runtime.freeMemory(),
            "totalMemory", runtime.totalMemory(),
            "maxMemory", runtime.maxMemory(),
            "uptime", ManagementFactory.getRuntimeMXBean().getUptime()
        ));

        // Active profiles
        builder.withDetail("profiles", List.of(environment.getActiveProfiles()));

        // Database statistics
        builder.withDetail("database", Map.of(
            "users", Map.of(
                "total", userRepository.count(),
                "active", userRepository.countByStatus("ACTIVE")
            ),
            "orders", Map.of(
                "total", orderRepository.count(),
                "pending", orderRepository.countByStatus("PENDING"),
                "completed", orderRepository.countByStatus("COMPLETED")
            )
        ));

        // Deployment information
        builder.withDetail("deployment", Map.of(
            "environment", environment.getProperty("app.environment", "unknown"),
            "region", environment.getProperty("app.region", "unknown"),
            "instance", getHostname()
        ));
    }

    private String getHostname() {
        try {
            return InetAddress.getLocalHost().getHostName();
        } catch (Exception e) {
            return "unknown";
        }
    }
}
```

### Dependency Version Info

```java
@Component
public class DependencyVersionInfoContributor implements InfoContributor {

    @Override
    public void contribute(Info.Builder builder) {
        Map<String, String> versions = new HashMap<>();
        
        // Spring versions
        versions.put("spring-boot", SpringBootVersion.getVersion());
        versions.put("spring-framework", SpringVersion.getVersion());
        
        // Java version
        versions.put("java", System.getProperty("java.version"));
        versions.put("java-vendor", System.getProperty("java.vendor"));
        
        // Other dependencies (if available)
        addVersionIfPresent(versions, "hibernate", "org.hibernate.Version", "getVersionString");
        addVersionIfPresent(versions, "jackson", "com.fasterxml.jackson.core.Version", "versionString");
        
        builder.withDetail("dependencies", versions);
    }

    private void addVersionIfPresent(Map<String, String> versions, String key, 
                                      String className, String methodName) {
        try {
            Class<?> clazz = Class.forName(className);
            Object versionInstance = clazz.getDeclaredConstructor().newInstance();
            String version = (String) clazz.getMethod(methodName).invoke(versionInstance);
            versions.put(key, version);
        } catch (Exception e) {
            // Dependency not present or version not accessible
        }
    }
}
```

## Metrics Examples

### Service Metrics

```java
@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final MeterRegistry meterRegistry;
    private final Counter orderCreatedCounter;
    private final Counter orderFailedCounter;
    private final Timer orderProcessingTimer;
    private final DistributionSummary orderAmountSummary;

    public OrderService(OrderRepository orderRepository, MeterRegistry meterRegistry) {
        this.orderRepository = orderRepository;
        this.meterRegistry = meterRegistry;

        // Counters
        this.orderCreatedCounter = Counter.builder("orders.created")
            .description("Total number of orders created")
            .tag("service", "order")
            .register(meterRegistry);

        this.orderFailedCounter = Counter.builder("orders.failed")
            .description("Total number of failed orders")
            .tag("service", "order")
            .register(meterRegistry);

        // Timer for processing duration
        this.orderProcessingTimer = Timer.builder("order.processing.time")
            .description("Order processing duration")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(meterRegistry);

        // Distribution summary for order amounts
        this.orderAmountSummary = DistributionSummary.builder("order.amount")
            .description("Order amount distribution")
            .baseUnit("EUR")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(meterRegistry);

        // Gauge for pending orders
        Gauge.builder("orders.pending", orderRepository, repo -> repo.countByStatus("PENDING"))
            .description("Number of pending orders")
            .register(meterRegistry);
    }

    public Order createOrder(OrderRequest request) {
        return orderProcessingTimer.record(() -> {
            try {
                Order order = processOrder(request);
                orderCreatedCounter.increment();
                orderAmountSummary.record(order.getTotalAmount());
                
                // Tag by payment method
                Counter.builder("orders.created.by.payment")
                    .tag("paymentMethod", order.getPaymentMethod())
                    .register(meterRegistry)
                    .increment();
                
                return order;
            } catch (Exception ex) {
                orderFailedCounter.increment();
                throw ex;
            }
        });
    }

    private Order processOrder(OrderRequest request) {
        // Implementation
        return new Order();
    }
}
```

### Custom Metrics with Tags

```java
@Service
public class MetricsService {

    private final MeterRegistry registry;

    public MetricsService(MeterRegistry registry) {
        this.registry = registry;
    }

    public void recordHttpRequest(String method, String endpoint, int statusCode, long duration) {
        Timer.builder("http.requests")
            .tag("method", method)
            .tag("endpoint", endpoint)
            .tag("status", String.valueOf(statusCode))
            .register(registry)
            .record(duration, TimeUnit.MILLISECONDS);
    }

    public void recordDatabaseQuery(String query, long duration, boolean success) {
        Timer.builder("db.queries")
            .tag("query", query)
            .tag("success", String.valueOf(success))
            .register(registry)
            .record(duration, TimeUnit.MILLISECONDS);
    }

    public void trackCacheHit(String cacheName, boolean hit) {
        Counter.builder("cache.operations")
            .tag("cache", cacheName)
            .tag("result", hit ? "hit" : "miss")
            .register(registry)
            .increment();
    }

    public void recordBusinessMetric(String metricName, double value, Map<String, String> tags) {
        DistributionSummary.Builder builder = DistributionSummary.builder(metricName);
        tags.forEach(builder::tag);
        builder.register(registry).record(value);
    }
}
```

## Security Configuration Examples

### Complete Security Setup

```java
@Configuration
@EnableWebSecurity
public class ActuatorSecurityConfiguration {

    @Bean
    public SecurityFilterChain actuatorSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(auth -> auth
                // Public health check (for load balancers)
                .requestMatchers(EndpointRequest.to(HealthEndpoint.class)).permitAll()
                
                // Info endpoint for authenticated users
                .requestMatchers(EndpointRequest.to(InfoEndpoint.class)).authenticated()
                
                // Read-only metrics for monitoring role
                .requestMatchers(HttpMethod.GET, "/actuator/metrics/**")
                    .hasAnyRole("MONITOR", "ADMIN")
                
                // Prometheus endpoint for monitoring tools
                .requestMatchers(EndpointRequest.to("prometheus"))
                    .hasRole("MONITOR")
                
                // Write operations only for admin
                .requestMatchers(HttpMethod.POST, "/actuator/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.DELETE, "/actuator/**").hasRole("ADMIN")
                
                // Everything else requires admin
                .anyRequest().hasRole("ADMIN")
            )
            .httpBasic(Customizer.withDefaults())
            .build();
    }

    @Bean
    public UserDetailsService actuatorUsers() {
        UserDetails monitor = User.builder()
            .username("monitor")
            .password("{noop}monitor-password")
            .roles("MONITOR")
            .build();

        UserDetails admin = User.builder()
            .username("admin")
            .password("{noop}admin-password")
            .roles("ADMIN", "MONITOR")
            .build();

        return new InMemoryUserDetailsManager(monitor, admin);
    }
}
```

### IP-Based Access Control

```java
@Configuration
public class IpBasedActuatorSecurity {

    @Bean
    public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
        return http
            .securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(request -> 
                    isFromAllowedIp(request.getRemoteAddr())
                ).permitAll()
                .anyRequest().denyAll()
            )
            .build();
    }

    private boolean isFromAllowedIp(String remoteAddr) {
        // Allow localhost and specific IPs
        return remoteAddr.equals("127.0.0.1") ||
               remoteAddr.equals("0:0:0:0:0:0:0:1") ||
               remoteAddr.startsWith("10.0.0.");
    }
}
```

## Testing Examples

### Health Indicator Tests

```java
@SpringBootTest
class DatabaseHealthIndicatorTest {

    @Autowired
    private DatabaseHealthIndicator healthIndicator;

    @MockBean
    private DataSource dataSource;

    @Test
    void shouldReturnUpWhenDatabaseIsHealthy() throws Exception {
        Connection connection = mock(Connection.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.isValid(1000)).thenReturn(true);

        DatabaseMetaData metaData = mock(DatabaseMetaData.class);
        when(connection.getMetaData()).thenReturn(metaData);
        when(metaData.getDatabaseProductName()).thenReturn("PostgreSQL");

        Health health = healthIndicator.health();

        assertThat(health.getStatus()).isEqualTo(Status.UP);
        assertThat(health.getDetails()).containsKey("database");
    }

    @Test
    void shouldReturnDownWhenDatabaseConnectionFails() throws Exception {
        when(dataSource.getConnection()).thenThrow(new SQLException("Connection failed"));

        Health health = healthIndicator.health();

        assertThat(health.getStatus()).isEqualTo(Status.DOWN);
        assertThat(health.getDetails()).containsKey("error");
    }
}
```

### Endpoint Tests

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class ActuatorEndpointIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void healthEndpointShouldBeAccessible() throws Exception {
        mockMvc.perform(get("/actuator/health"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("UP"));
    }

    @Test
    void metricsEndpointShouldListAvailableMetrics() throws Exception {
        mockMvc.perform(get("/actuator/metrics"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.names").isArray())
            .andExpect(jsonPath("$.names[*]", hasItem("jvm.memory.used")));
    }

    @Test
    void customEndpointShouldWork() throws Exception {
        mockMvc.perform(get("/actuator/features"))
            .andExpect(status().isOk())
            .andExpect(content().contentType(MediaType.APPLICATION_JSON));
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void securedEndpointShouldRequireAuthentication() throws Exception {
        mockMvc.perform(post("/actuator/features/test")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"enabled\":true}"))
            .andExpect(status().isOk());
    }
}
```

## Kubernetes Integration Example

### Deployment with Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: order-service:1.0.0
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8081
          name: management
        
        env:
        - name: MANAGEMENT_SERVER_PORT
          value: "8081"
        - name: MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE
          value: "health,info,prometheus"
        
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: management
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: management
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
  ports:
  - name: http
    port: 8080
    targetPort: http
  - name: management
    port: 8081
    targetPort: management
```

### ServiceMonitor for Prometheus Operator

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: order-service-metrics
  labels:
    app: order-service
spec:
  selector:
    matchLabels:
      app: order-service
  endpoints:
  - port: management
    path: /actuator/prometheus
    interval: 30s
    scrapeTimeout: 10s
```
