# Auditing with Spring Boot Actuator

Once Spring Security is in play, Spring Boot Actuator has a flexible audit framework that publishes events (by default, "authentication success", "failure" and "access denied" exceptions). This feature can be very useful for reporting and for implementing a lock-out policy based on authentication failures.

You can enable auditing by providing a bean of type `AuditEventRepository` in your application's configuration. For convenience, Spring Boot offers an `InMemoryAuditEventRepository`. `InMemoryAuditEventRepository` has limited capabilities, and we recommend using it only for development environments. For production environments, consider creating your own alternative `AuditEventRepository` implementation.

## Basic Audit Configuration

### In-Memory Audit Repository (Development)

```java
@Configuration
public class AuditConfiguration {

    @Bean
    public AuditEventRepository auditEventRepository() {
        return new InMemoryAuditEventRepository();
    }
}
```

### Database Audit Repository (Production)

```java
@Entity
@Table(name = "audit_events")
public class PersistentAuditEvent {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "principal", nullable = false)
    private String principal;
    
    @Column(name = "audit_event_type", nullable = false)
    private String auditEventType;
    
    @Column(name = "audit_event_date", nullable = false)
    private Instant auditEventDate;
    
    @ElementCollection
    @MapKeyColumn(name = "name")
    @Column(name = "value")
    @CollectionTable(name = "audit_event_data", 
                    joinColumns = @JoinColumn(name = "event_id"))
    private Map<String, String> data = new HashMap<>();
    
    // Constructors, getters, setters
}

@Repository
public class CustomAuditEventRepository implements AuditEventRepository {

    private final PersistentAuditEventRepository repository;

    public CustomAuditEventRepository(PersistentAuditEventRepository repository) {
        this.repository = repository;
    }

    @Override
    public void add(AuditEvent event) {
        PersistentAuditEvent persistentEvent = new PersistentAuditEvent();
        persistentEvent.setPrincipal(event.getPrincipal());
        persistentEvent.setAuditEventType(event.getType());
        persistentEvent.setAuditEventDate(event.getTimestamp());
        persistentEvent.setData(event.getData());
        repository.save(persistentEvent);
    }

    @Override
    public List<AuditEvent> find(String principal, Instant after, String type) {
        List<PersistentAuditEvent> events = repository.findByPrincipalAndAuditEventDateAfterAndAuditEventType(
                principal, after, type);
        return events.stream()
                .map(this::convertToAuditEvent)
                .collect(Collectors.toList());
    }

    private AuditEvent convertToAuditEvent(PersistentAuditEvent persistentEvent) {
        return new AuditEvent(persistentEvent.getAuditEventDate(),
                             persistentEvent.getPrincipal(),
                             persistentEvent.getAuditEventType(),
                             persistentEvent.getData());
    }
}
```

## Custom Auditing

### Custom Audit Events

You can publish custom audit events using `AuditEventRepository`:

```java
@Service
public class UserService {

    private final AuditEventRepository auditEventRepository;
    private final UserRepository userRepository;

    public UserService(AuditEventRepository auditEventRepository,
                      UserRepository userRepository) {
        this.auditEventRepository = auditEventRepository;
        this.userRepository = userRepository;
    }

    public User createUser(CreateUserRequest request) {
        User user = userRepository.save(request.toUser());
        
        // Publish audit event
        Map<String, String> data = new HashMap<>();
        data.put("userId", user.getId().toString());
        data.put("username", user.getUsername());
        data.put("email", user.getEmail());
        
        AuditEvent event = new AuditEvent(getCurrentUsername(), "USER_CREATED", data);
        auditEventRepository.add(event);
        
        return user;
    }

    public void deleteUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException(userId));
        
        userRepository.delete(user);
        
        // Publish audit event
        Map<String, String> data = new HashMap<>();
        data.put("userId", userId.toString());
        data.put("username", user.getUsername());
        
        AuditEvent event = new AuditEvent(getCurrentUsername(), "USER_DELETED", data);
        auditEventRepository.add(event);
    }

    private String getCurrentUsername() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null ? auth.getName() : "system";
    }
}
```

### Custom Audit Event Publisher

```java
@Component
public class AuditEventPublisher {

    private final AuditEventRepository auditEventRepository;

    public AuditEventPublisher(AuditEventRepository auditEventRepository) {
        this.auditEventRepository = auditEventRepository;
    }

    public void publishEvent(String type, Map<String, String> data) {
        String principal = getCurrentPrincipal();
        AuditEvent event = new AuditEvent(principal, type, data);
        auditEventRepository.add(event);
    }

    public void publishSecurityEvent(String type, String details) {
        Map<String, String> data = new HashMap<>();
        data.put("details", details);
        data.put("timestamp", Instant.now().toString());
        data.put("source", "security");
        publishEvent(type, data);
    }

    public void publishBusinessEvent(String type, String entityId, String action) {
        Map<String, String> data = new HashMap<>();
        data.put("entityId", entityId);
        data.put("action", action);
        data.put("timestamp", Instant.now().toString());
        publishEvent(type, data);
    }

    private String getCurrentPrincipal() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null ? auth.getName() : "anonymous";
    }
}
```

## Method-Level Auditing

### Using AOP for Automatic Auditing

```java
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface Auditable {
    String value() default "";
    String type() default "";
    boolean includeArgs() default false;
    boolean includeResult() default false;
}

@Aspect
@Component
public class AuditableAspect {

    private final AuditEventPublisher auditEventPublisher;

    public AuditableAspect(AuditEventPublisher auditEventPublisher) {
        this.auditEventPublisher = auditEventPublisher;
    }

    @Around("@annotation(auditable)")
    public Object auditMethod(ProceedingJoinPoint joinPoint, Auditable auditable) throws Throwable {
        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String auditType = auditable.type().isEmpty() ? 
                          className + "." + methodName : auditable.type();

        Map<String, String> data = new HashMap<>();
        data.put("method", methodName);
        data.put("class", className);

        if (auditable.includeArgs()) {
            Object[] args = joinPoint.getArgs();
            for (int i = 0; i < args.length; i++) {
                data.put("arg" + i, String.valueOf(args[i]));
            }
        }

        try {
            Object result = joinPoint.proceed();
            
            if (auditable.includeResult() && result != null) {
                data.put("result", String.valueOf(result));
            }
            
            data.put("status", "success");
            auditEventPublisher.publishEvent(auditType, data);
            
            return result;
        } catch (Exception ex) {
            data.put("status", "failure");
            data.put("error", ex.getMessage());
            auditEventPublisher.publishEvent(auditType, data);
            throw ex;
        }
    }
}
```

### Usage Example

```java
@Service
public class OrderService {

    @Auditable(type = "ORDER_CREATED", includeArgs = true)
    public Order createOrder(CreateOrderRequest request) {
        // Order creation logic
        return new Order();
    }

    @Auditable(type = "ORDER_CANCELLED", includeResult = true)
    public Order cancelOrder(Long orderId) {
        // Order cancellation logic
        return cancelledOrder;
    }

    @Auditable(type = "PAYMENT_PROCESSED")
    public PaymentResult processPayment(PaymentRequest request) {
        // Payment processing logic
        return new PaymentResult();
    }
}
```

## Security Audit Events

### Authentication Events

Spring Boot automatically publishes authentication events when using Spring Security:

- `AUTHENTICATION_SUCCESS`
- `AUTHENTICATION_FAILURE`
- `ACCESS_DENIED`

### Custom Security Events

```java
@Component
public class SecurityAuditService {

    private final AuditEventPublisher auditEventPublisher;

    public SecurityAuditService(AuditEventPublisher auditEventPublisher) {
        this.auditEventPublisher = auditEventPublisher;
    }

    @EventListener
    public void handleAuthenticationSuccess(AuthenticationSuccessEvent event) {
        Map<String, String> data = new HashMap<>();
        data.put("username", event.getAuthentication().getName());
        data.put("authorities", event.getAuthentication().getAuthorities().toString());
        data.put("source", getClientIP());
        
        auditEventPublisher.publishEvent("AUTHENTICATION_SUCCESS", data);
    }

    @EventListener
    public void handleAuthenticationFailure(AbstractAuthenticationFailureEvent event) {
        Map<String, String> data = new HashMap<>();
        data.put("username", event.getAuthentication().getName());
        data.put("exception", event.getException().getClass().getSimpleName());
        data.put("message", event.getException().getMessage());
        data.put("source", getClientIP());
        
        auditEventPublisher.publishEvent("AUTHENTICATION_FAILURE", data);
    }

    @EventListener
    public void handleAccessDenied(AuthorizationDeniedEvent event) {
        Map<String, String> data = new HashMap<>();
        data.put("username", event.getAuthentication().getName());
        data.put("resource", event.getAuthorizationDecision().toString());
        data.put("source", getClientIP());
        
        auditEventPublisher.publishEvent("ACCESS_DENIED", data);
    }

    private String getClientIP() {
        RequestAttributes requestAttributes = RequestContextHolder.getRequestAttributes();
        if (requestAttributes instanceof ServletRequestAttributes) {
            HttpServletRequest request = ((ServletRequestAttributes) requestAttributes).getRequest();
            return request.getRemoteAddr();
        }
        return "unknown";
    }
}
```

### Password Change Auditing

```java
@Service
public class PasswordService {

    private final AuditEventPublisher auditEventPublisher;
    private final PasswordEncoder passwordEncoder;

    public PasswordService(AuditEventPublisher auditEventPublisher,
                          PasswordEncoder passwordEncoder) {
        this.auditEventPublisher = auditEventPublisher;
        this.passwordEncoder = passwordEncoder;
    }

    public void changePassword(String oldPassword, String newPassword) {
        String username = getCurrentUsername();
        
        try {
            // Validate old password
            if (!isCurrentPassword(oldPassword)) {
                Map<String, String> data = new HashMap<>();
                data.put("username", username);
                data.put("reason", "invalid_old_password");
                auditEventPublisher.publishEvent("PASSWORD_CHANGE_FAILED", data);
                throw new InvalidPasswordException("Invalid old password");
            }

            // Change password
            updatePassword(newPassword);

            // Audit success
            Map<String, String> data = new HashMap<>();
            data.put("username", username);
            auditEventPublisher.publishEvent("PASSWORD_CHANGED", data);

        } catch (Exception ex) {
            Map<String, String> data = new HashMap<>();
            data.put("username", username);
            data.put("error", ex.getMessage());
            auditEventPublisher.publishEvent("PASSWORD_CHANGE_ERROR", data);
            throw ex;
        }
    }

    private boolean isCurrentPassword(String password) {
        // Implementation
        return true;
    }

    private void updatePassword(String newPassword) {
        // Implementation
    }

    private String getCurrentUsername() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null ? auth.getName() : "anonymous";
    }
}
```

## Audit Events Endpoint

The `/actuator/auditevents` endpoint exposes audit events:

```
GET /actuator/auditevents
GET /actuator/auditevents?principal=user&after=2023-01-01T00:00:00Z&type=USER_CREATED
```

Response format:

```json
{
  "events": [
    {
      "timestamp": "2023-12-01T10:30:00Z",
      "principal": "admin",
      "type": "USER_CREATED",
      "data": {
        "userId": "123",
        "username": "newuser",
        "email": "user@example.com"
      }
    }
  ]
}
```

## Production Configuration

### Secure Audit Endpoint

```java
@Configuration
public class AuditSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain auditSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .requestMatcher(EndpointRequest.to("auditevents"))
            .authorizeHttpRequests(requests -> 
                requests.anyRequest().hasRole("AUDITOR"))
            .httpBasic(withDefaults())
            .build();
    }
}
```

### Audit Configuration

```yaml
management:
  endpoint:
    auditevents:
      enabled: true
      cache:
        time-to-live: 10s
  endpoints:
    web:
      exposure:
        include: "auditevents"

# Custom audit properties
audit:
  retention-days: 90
  max-events-per-request: 100
  sensitive-data-masking: true
```

## Best Practices

1. **Data Sensitivity**: Never include sensitive data (passwords, tokens) in audit events
2. **Performance**: Consider async processing for high-volume audit events
3. **Retention**: Implement audit data retention policies
4. **Security**: Secure the audit endpoint and audit data storage
5. **Monitoring**: Monitor audit system health and performance
6. **Compliance**: Ensure audit events meet regulatory requirements
7. **Immutability**: Ensure audit events cannot be modified after creation

### Async Audit Processing

```java
@Configuration
@EnableAsync
public class AsyncAuditConfiguration {

    @Bean
    public TaskExecutor auditTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(5);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("audit-");
        executor.initialize();
        return executor;
    }
}

@Service
public class AsyncAuditEventRepository implements AuditEventRepository {

    private final AuditEventRepository delegate;

    public AsyncAuditEventRepository(AuditEventRepository delegate) {
        this.delegate = delegate;
    }

    @Override
    @Async("auditTaskExecutor")
    public void add(AuditEvent event) {
        delegate.add(event);
    }

    @Override
    public List<AuditEvent> find(String principal, Instant after, String type) {
        return delegate.find(principal, after, type);
    }
}
```