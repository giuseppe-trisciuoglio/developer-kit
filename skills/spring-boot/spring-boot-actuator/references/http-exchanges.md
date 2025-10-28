# HTTP Exchanges

You can enable recording of HTTP exchanges by providing a bean of type `HttpExchangeRepository` in your application's configuration. For convenience, Spring Boot offers `InMemoryHttpExchangeRepository`, which, by default, stores the last 100 request-response exchanges. `InMemoryHttpExchangeRepository` is limited compared to tracing solutions, and we recommend using it only for development environments. For production environments, we recommend using a production-ready tracing or observability solution, such as Zipkin or OpenTelemetry. Alternatively, you can create your own `HttpExchangeRepository`.

You can use the `httpexchanges` endpoint to obtain information about the request-response exchanges that are stored in the `HttpExchangeRepository`.

## Basic Configuration

### In-Memory Repository (Development)

```java
@Configuration
public class HttpExchangesConfiguration {

    @Bean
    public InMemoryHttpExchangeRepository httpExchangeRepository() {
        return new InMemoryHttpExchangeRepository();
    }
}
```

### Custom Repository Size

```java
@Configuration
public class HttpExchangesConfiguration {

    @Bean
    public InMemoryHttpExchangeRepository httpExchangeRepository() {
        return new InMemoryHttpExchangeRepository(1000); // Store last 1000 exchanges
    }
}
```

## Custom HTTP Exchange Recording

To customize the items that are included in each recorded exchange, use the `management.httpexchanges.recording.include` configuration property:

```yaml
management:
  httpexchanges:
    recording:
      include:
        - request-headers
        - response-headers
        - cookie-headers
        - authorization-header
        - principal
        - remote-address
        - session-id
        - time-taken
```

Available options:
- `request-headers`: Include request headers
- `response-headers`: Include response headers  
- `cookie-headers`: Include cookie headers
- `authorization-header`: Include authorization header
- `principal`: Include principal information
- `remote-address`: Include remote address
- `session-id`: Include session ID
- `time-taken`: Include request processing time

## Custom HTTP Exchange Repository

### Database-backed Repository

```java
@Entity
@Table(name = "http_exchanges")
public class HttpExchangeEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "timestamp")
    private Instant timestamp;
    
    @Column(name = "method")
    private String method;
    
    @Column(name = "uri", length = 2000)
    private String uri;
    
    @Column(name = "status")
    private Integer status;
    
    @Column(name = "time_taken")
    private Long timeTaken;
    
    @Column(name = "principal")
    private String principal;
    
    @Column(name = "remote_address")
    private String remoteAddress;
    
    @Column(name = "session_id")
    private String sessionId;
    
    @Lob
    @Column(name = "request_headers")
    private String requestHeaders;
    
    @Lob
    @Column(name = "response_headers")
    private String responseHeaders;
    
    // Constructors, getters, setters
}

@Repository
public interface HttpExchangeEntityRepository extends JpaRepository<HttpExchangeEntity, Long> {
    
    List<HttpExchangeEntity> findTop100ByOrderByTimestampDesc();
    
    @Modifying
    @Query("DELETE FROM HttpExchangeEntity h WHERE h.timestamp < :cutoff")
    void deleteOlderThan(@Param("cutoff") Instant cutoff);
}

@Component
public class DatabaseHttpExchangeRepository implements HttpExchangeRepository {

    private final HttpExchangeEntityRepository repository;
    private final ObjectMapper objectMapper;

    public DatabaseHttpExchangeRepository(HttpExchangeEntityRepository repository) {
        this.repository = repository;
        this.objectMapper = new ObjectMapper();
    }

    @Override
    public List<HttpExchange> findAll() {
        return repository.findTop100ByOrderByTimestampDesc()
                .stream()
                .map(this::toHttpExchange)
                .collect(Collectors.toList());
    }

    @Override
    public void add(HttpExchange httpExchange) {
        HttpExchangeEntity entity = toEntity(httpExchange);
        repository.save(entity);
    }

    private HttpExchangeEntity toEntity(HttpExchange exchange) {
        HttpExchangeEntity entity = new HttpExchangeEntity();
        entity.setTimestamp(exchange.getTimestamp());
        
        HttpExchange.Request request = exchange.getRequest();
        entity.setMethod(request.getMethod());
        entity.setUri(request.getUri().toString());
        entity.setPrincipal(exchange.getPrincipal() != null ? 
                          exchange.getPrincipal().getName() : null);
        entity.setRemoteAddress(request.getRemoteAddress());
        
        if (exchange.getResponse() != null) {
            entity.setStatus(exchange.getResponse().getStatus());
        }
        
        entity.setTimeTaken(exchange.getTimeTaken() != null ? 
                          exchange.getTimeTaken().toMillis() : null);
        
        try {
            entity.setRequestHeaders(objectMapper.writeValueAsString(request.getHeaders()));
            if (exchange.getResponse() != null) {
                entity.setResponseHeaders(objectMapper.writeValueAsString(
                    exchange.getResponse().getHeaders()));
            }
        } catch (Exception e) {
            // Handle serialization error
        }
        
        return entity;
    }

    private HttpExchange toHttpExchange(HttpExchangeEntity entity) {
        // Implement conversion from entity to HttpExchange
        // This is complex due to HttpExchange being immutable
        // Consider using a builder pattern or reflection
        return null; // Simplified for brevity
    }

    @Scheduled(fixedRate = 3600000) // Clean up every hour
    public void cleanup() {
        Instant cutoff = Instant.now().minus(Duration.ofDays(7));
        repository.deleteOlderThan(cutoff);
    }
}
```

### Filtered HTTP Exchange Repository

```java
@Component
public class FilteredHttpExchangeRepository implements HttpExchangeRepository {

    private final HttpExchangeRepository delegate;
    private final Set<String> excludePaths;
    private final Set<String> excludeUserAgents;

    public FilteredHttpExchangeRepository(HttpExchangeRepository delegate) {
        this.delegate = delegate;
        this.excludePaths = Set.of("/actuator/health", "/actuator/metrics", "/favicon.ico");
        this.excludeUserAgents = Set.of("kube-probe", "ELB-HealthChecker");
    }

    @Override
    public List<HttpExchange> findAll() {
        return delegate.findAll();
    }

    @Override
    public void add(HttpExchange httpExchange) {
        if (shouldRecord(httpExchange)) {
            delegate.add(httpExchange);
        }
    }

    private boolean shouldRecord(HttpExchange exchange) {
        String path = exchange.getRequest().getUri().getPath();
        
        // Skip health check and monitoring endpoints
        if (excludePaths.contains(path)) {
            return false;
        }
        
        // Skip requests from monitoring tools
        String userAgent = exchange.getRequest().getHeaders().getFirst("User-Agent");
        if (userAgent != null && excludeUserAgents.stream().anyMatch(userAgent::contains)) {
            return false;
        }
        
        // Skip successful static resource requests
        if (path.startsWith("/static/") || path.startsWith("/css/") || path.startsWith("/js/")) {
            return exchange.getResponse() == null || exchange.getResponse().getStatus() >= 400;
        }
        
        return true;
    }
}
```

## Async HTTP Exchange Recording

### Async Repository Wrapper

```java
@Component
public class AsyncHttpExchangeRepository implements HttpExchangeRepository {

    private final HttpExchangeRepository delegate;
    private final TaskExecutor taskExecutor;

    public AsyncHttpExchangeRepository(HttpExchangeRepository delegate, 
                                     @Qualifier("httpExchangeTaskExecutor") TaskExecutor taskExecutor) {
        this.delegate = delegate;
        this.taskExecutor = taskExecutor;
    }

    @Override
    public List<HttpExchange> findAll() {
        return delegate.findAll();
    }

    @Override
    public void add(HttpExchange httpExchange) {
        taskExecutor.execute(() -> {
            try {
                delegate.add(httpExchange);
            } catch (Exception e) {
                // Log error but don't let it affect the main request
                log.error("Failed to record HTTP exchange", e);
            }
        });
    }
}

@Configuration
public class HttpExchangeTaskExecutorConfiguration {

    @Bean("httpExchangeTaskExecutor")
    public TaskExecutor httpExchangeTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(1);
        executor.setMaxPoolSize(2);
        executor.setQueueCapacity(1000);
        executor.setThreadNamePrefix("http-exchange-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.DiscardOldestPolicy());
        executor.initialize();
        return executor;
    }
}
```

## HTTP Exchanges Endpoint

### Accessing HTTP Exchanges

```
GET /actuator/httpexchanges
```

Response format:

```json
{
  "exchanges": [
    {
      "timestamp": "2023-12-01T10:30:00.123Z",
      "request": {
        "method": "GET",
        "uri": "http://localhost:8080/api/users/123",
        "headers": {
          "accept": ["application/json"],
          "user-agent": ["Mozilla/5.0..."]
        },
        "remoteAddress": "192.168.1.100"
      },
      "response": {
        "status": 200,
        "headers": {
          "content-type": ["application/json"],
          "content-length": ["256"]
        }
      },
      "principal": {
        "name": "john.doe"
      },
      "session": {
        "id": "JSESSIONID123"
      },
      "timeTaken": "PT0.025S"
    }
  ]
}
```

### Securing the Endpoint

```java
@Configuration
public class HttpExchangesSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain httpExchangesSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .requestMatcher(EndpointRequest.to("httpexchanges"))
            .authorizeHttpRequests(requests -> 
                requests.anyRequest().hasRole("ADMIN"))
            .httpBasic(withDefaults())
            .build();
    }
}
```

## Custom HTTP Exchange Information

### Including Custom Data

```java
@Component
public class CustomHttpExchangeRepository implements HttpExchangeRepository {

    private final InMemoryHttpExchangeRepository delegate;

    public CustomHttpExchangeRepository() {
        this.delegate = new InMemoryHttpExchangeRepository();
    }

    @Override
    public List<HttpExchange> findAll() {
        return delegate.findAll();
    }

    @Override
    public void add(HttpExchange httpExchange) {
        HttpExchange enrichedExchange = enrichExchange(httpExchange);
        delegate.add(enrichedExchange);
    }

    private HttpExchange enrichExchange(HttpExchange original) {
        // Add custom information to the exchange
        // Note: HttpExchange is immutable, so we need to create a wrapper
        // or use reflection to modify internal state
        
        // For demonstration, we'll just add it normally
        // In practice, you might need to create a custom implementation
        return original;
    }
}

@Component
public class HttpExchangeEnricher {

    public void enrich(HttpServletRequest request, HttpServletResponse response) {
        // Add custom attributes that can be picked up by the repository
        request.setAttribute("custom.trace.id", getTraceId());
        request.setAttribute("custom.user.role", getUserRole());
        request.setAttribute("custom.api.version", getApiVersion(request));
    }

    private String getTraceId() {
        // Get from tracing context
        return "trace-123";
    }

    private String getUserRole() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null ? auth.getAuthorities().toString() : "anonymous";
    }

    private String getApiVersion(HttpServletRequest request) {
        return request.getHeader("API-Version");
    }
}
```

## Performance Considerations

### Configuration for Production

```yaml
management:
  httpexchanges:
    recording:
      include:
        - time-taken
        - principal
        - remote-address
      # Exclude detailed headers to reduce memory usage
      exclude:
        - request-headers
        - response-headers
  endpoint:
    httpexchanges:
      enabled: false  # Disable in production for security
```

### Custom Sampling

```java
@Component
public class SamplingHttpExchangeRepository implements HttpExchangeRepository {

    private final HttpExchangeRepository delegate;
    private final Random random = new Random();
    private final double samplingRate;

    public SamplingHttpExchangeRepository(HttpExchangeRepository delegate,
                                        @Value("${app.http-exchanges.sampling-rate:0.1}") double samplingRate) {
        this.delegate = delegate;
        this.samplingRate = samplingRate;
    }

    @Override
    public List<HttpExchange> findAll() {
        return delegate.findAll();
    }

    @Override
    public void add(HttpExchange httpExchange) {
        if (random.nextDouble() < samplingRate) {
            delegate.add(httpExchange);
        }
    }
}
```

## Best Practices

1. **Production Use**: Disable HTTP exchanges endpoint in production or secure it properly
2. **Memory Management**: Use limited-size repositories to prevent memory leaks
3. **Sensitive Data**: Be careful not to log sensitive information in headers
4. **Performance**: Consider async recording for high-throughput applications
5. **Sampling**: Use sampling in production to reduce overhead
6. **Retention**: Implement cleanup policies for stored exchanges
7. **Security**: Ensure recorded data doesn't contain credentials or tokens

### Production Configuration Example

```yaml
management:
  endpoint:
    httpexchanges:
      enabled: false  # Disabled in production
  httpexchanges:
    recording:
      include:
        - time-taken
        - principal
        - remote-address
      exclude:
        - authorization-header
        - cookie-headers
        - request-headers
        - response-headers

logging:
  level:
    org.springframework.boot.actuate.web.exchanges: WARN
```