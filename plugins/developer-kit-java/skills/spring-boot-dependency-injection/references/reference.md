# Spring Boot Dependency Injection - References

Complete API reference for dependency injection in Spring Boot applications.

## Core Interfaces and Classes

### ApplicationContext
Root interface for Spring IoC container.

```java
public interface ApplicationContext extends EnvironmentCapable, ListableBeanFactory, 
                                          HierarchicalBeanFactory, MessageSource,
                                          ApplicationEventPublisher, ResourcePatternResolver {
    
    // Get a bean by type
    <T> T getBean(Class<T> requiredType);
    
    // Get a bean by name and type
    <T> T getBean(String name, Class<T> requiredType);
    
    // Get all beans of a type
    <T> Map<String, T> getBeansOfType(Class<T> type);
    
    // Get all bean names
    String[] getBeanDefinitionNames();
}
```

### BeanFactory
Lower-level interface for accessing beans (used internally).

```java
public interface BeanFactory {
    Object getBean(String name);
    <T> T getBean(String name, Class<T> requiredType);
    <T> T getBean(Class<T> requiredType);
    Object getBean(String name, Object... args);
}
```

## Dependency Injection Annotations

### @Autowired
Auto-wire dependencies (property, constructor, or method injection).

```java
@Autowired                        // Required dependency
@Autowired(required = false)      // Optional dependency
@Autowired private UserRepository repository;  // Field injection (avoid)
```

### @Qualifier
Disambiguate when multiple beans of same type exist.

```java
@Autowired
@Qualifier("primaryDB")
private DataSource dataSource;

@Bean
@Qualifier("cache")
public CacheService cacheService() { }
```

### @Primary
Mark bean as preferred when multiple exist.

```java
@Bean
@Primary
public DataSource primaryDataSource() { }

@Bean
public DataSource secondaryDataSource() { }
```

### @Value
Inject properties and SpEL expressions.

```java
@Value("${app.name}")             // Property injection
@Value("${app.port:8080}")        // With default value
@Value("#{T(java.lang.Math).PI}") // SpEL expression
@Value("#{'${app.servers}'.split(',')}")  // Collection
private String value;
```

### @Lazy
Delay bean initialization until first access.

```java
@Bean
@Lazy
public ExpensiveBean expensiveBean() { }

@Autowired
@Lazy
private ExpensiveBean bean;  // Lazy proxy
```

### @Scope
Define bean lifecycle scope.

```java
@Scope("singleton")     // One per container (default)
@Scope("prototype")     // New instance each time
@Scope("request")       // One per HTTP request
@Scope("session")       // One per HTTP session
@Scope("application")   // One per ServletContext
@Scope("websocket")     // One per WebSocket session
```

### @Configuration
Mark class as providing bean definitions.

```java
@Configuration
public class AppConfig {
    @Bean
    public UserService userService() { }
}
```

### @Bean
Define a bean in configuration class.

```java
@Bean
public UserService userService(UserRepository repository) {
    return new UserService(repository);
}

@Bean(name = "customName")
public UserService userService() { }

@Bean(initMethod = "init", destroyMethod = "cleanup")
public UserService userService() { }
```

### @Component / @Service / @Repository / @Controller
Stereotype annotations for component scanning.

```java
@Component              // Generic Spring component
@Service               // Business logic layer
@Repository           // Data access layer
@Controller           // Web layer (MVC)
@RestController       // Web layer (REST)
public class UserService { }
```

## Conditional Bean Registration

### @ConditionalOnProperty
Create bean only if property exists.

```java
@Bean
@ConditionalOnProperty(
    name = "feature.notifications.enabled",
    havingValue = "true"
)
public NotificationService notificationService() { }

// OR if property matches any value
@ConditionalOnProperty(name = "feature.enabled")
public NotificationService notificationService() { }
```

### @ConditionalOnClass / @ConditionalOnMissingClass
Create bean based on classpath availability.

```java
@Bean
@ConditionalOnClass(RedisTemplate.class)
public CacheService cacheService() { }

@Bean
@ConditionalOnMissingClass("org.springframework.data.redis.core.RedisTemplate")
public LocalCacheService fallbackCacheService() { }
```

### @ConditionalOnBean / @ConditionalOnMissingBean
Create bean based on other beans.

```java
@Bean
@ConditionalOnBean(DataSource.class)
public UserService userService() { }

@Bean
@ConditionalOnMissingBean
public UserService defaultUserService() { }
```

### @ConditionalOnExpression
Create bean based on SpEL expression.

```java
@Bean
@ConditionalOnExpression("'${environment}'.equals('production')")
public SecurityService securityService() { }
```

## Profile-Based Configuration

### @Profile
Activate bean only in specific profiles.

```java
@Configuration
@Profile("production")
public class ProductionConfig { }

@Bean
@Profile({"dev", "test"})
public TestDataLoader testDataLoader() { }

@Bean
@Profile("!production")  // All profiles except production
public DebugService debugService() { }
```

**Activate profiles:**
```properties
# application.properties
spring.profiles.active=production

# application-production.properties
# Profile-specific property file
spring.datasource.url=jdbc:postgresql://prod-db:5432/prod
```

## Component Scanning

### @ComponentScan
Configure component scanning.

```java
@Configuration
@ComponentScan(basePackages = {"com.example.users", "com.example.products"})
public class AppConfig { }

@Configuration
@ComponentScan(
    basePackages = "com.example",
    excludeFilters = @ComponentScan.Filter(
        type = FilterType.REGEX,
        pattern = "com\\.example\\.internal\\..*"
    )
)
public class AppConfig { }
```

### Filter Types
- `FilterType.ANNOTATION` - By annotation
- `FilterType.ASSIGNABLE_TYPE` - By class type
- `FilterType.ASPECTJ` - By AspectJ pattern
- `FilterType.REGEX` - By regex pattern
- `FilterType.CUSTOM` - Custom filter

## Injection Points

### Constructor Injection (Recommended)

```java
@Service
@RequiredArgsConstructor  // Lombok generates constructor
public class UserService {
    private final UserRepository repository;  // Final field
    private final EmailService emailService;
}

// Explicit
@Service
public class UserService {
    private final UserRepository repository;
    
    public UserService(UserRepository repository) {
        this.repository = Objects.requireNonNull(repository);
    }
}
```

### Setter Injection (Optional Dependencies Only)

```java
@Service
public class UserService {
    private final UserRepository repository;
    private EmailService emailService;  // Optional
    
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
    
    @Autowired(required = false)
    public void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```

### Field Injection (❌ Avoid)

```java
// ❌ NOT RECOMMENDED
@Service
public class UserService {
    @Autowired
    private UserRepository repository;  // Hidden dependency
    
    @Autowired
    private EmailService emailService;  // Mutable state
}
```

## Circular Dependency Resolution

### Problem: Circular Dependencies

```java
// ❌ WILL FAIL
@Service
public class UserService {
    private final OrderService orderService;
    
    public UserService(OrderService orderService) {
        this.orderService = orderService;  // Circular!
    }
}

@Service
public class OrderService {
    private final UserService userService;
    
    public OrderService(UserService userService) {
        this.userService = userService;  // Circular!
    }
}
```

### Solution 1: Setter Injection

```java
@Service
public class UserService {
    private final UserRepository userRepository;
    private OrderService orderService;  // Optional
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    @Autowired(required = false)
    public void setOrderService(OrderService orderService) {
        this.orderService = orderService;
    }
}
```

### Solution 2: Event-Driven (Recommended)

```java
public class UserRegisteredEvent extends ApplicationEvent {
    private final String userId;
    
    public UserRegisteredEvent(Object source, String userId) {
        super(source);
        this.userId = userId;
    }
}

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final ApplicationEventPublisher eventPublisher;
    
    public User registerUser(CreateUserRequest request) {
        User user = userRepository.save(User.create(request));
        eventPublisher.publishEvent(new UserRegisteredEvent(this, user.getId()));
        return user;
    }
}

@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    
    @EventListener
    public void onUserRegistered(UserRegisteredEvent event) {
        orderRepository.createWelcomeOrder(event.getUserId());
    }
}
```

### Solution 3: Refactor to Separate Concerns

```java
// Shared service without circular dependency
@Service
@RequiredArgsConstructor
public class UserOrderService {
    private final UserRepository userRepository;
    private final OrderRepository orderRepository;
}

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserOrderService userOrderService;
}

@Service
@RequiredArgsConstructor
public class OrderService {
    private final UserOrderService userOrderService;
}
```

## ObjectProvider for Flexibility

### ObjectProvider Interface

```java
public interface ObjectProvider<T> extends ObjectFactory<T>, Iterable<T> {
    T getObject();
    T getObject(Object... args);
    T getIfAvailable();
    T getIfAvailable(Supplier<T> defaultSupplier);
    void ifAvailable(Consumer<T> consumer);
    void ifAvailableOrElse(Consumer<T> consumer, Runnable emptyRunnable);
    <X> ObjectProvider<X> map(Function<? super T, ? extends X> mapper);
    <X> ObjectProvider<X> flatMap(Function<? super T, ObjectProvider<X>> mapper);
    Optional<T> getIfUnique();
    Optional<T> getIfUnique(Supplier<T> defaultSupplier);
}
```

### Usage Example

```java
@Service
public class FlexibleService {
    private final ObjectProvider<CacheService> cacheProvider;
    
    public FlexibleService(ObjectProvider<CacheService> cacheProvider) {
        this.cacheProvider = cacheProvider;
    }
    
    public void process() {
        // Safely handle optional bean
        cacheProvider.ifAvailable(cache -> cache.invalidate());
        
        // Get with fallback
        CacheService cache = cacheProvider.getIfAvailable(() -> new NoOpCache());
        
        // Iterate if multiple beans exist
        cacheProvider.forEach(cache -> cache.initialize());
    }
}
```

## Bean Lifecycle Hooks

### InitializingBean / DisposableBean

```java
@Component
public class ResourceManager implements InitializingBean, DisposableBean {
    
    @Override
    public void afterPropertiesSet() throws Exception {
        // Called after constructor and property injection
        System.out.println("Bean initialized");
    }
    
    @Override
    public void destroy() throws Exception {
        // Called when context shutdown
        System.out.println("Bean destroyed");
    }
}
```

### @PostConstruct / @PreDestroy

```java
@Component
public class ResourceManager {
    
    @PostConstruct
    public void init() {
        // Called after constructor and injection
        System.out.println("Bean initialized");
    }
    
    @PreDestroy
    public void cleanup() {
        // Called before bean destroyed
        System.out.println("Bean destroyed");
    }
}
```

### @Bean with initMethod and destroyMethod

```java
@Configuration
public class AppConfig {
    
    @Bean(initMethod = "init", destroyMethod = "cleanup")
    public ResourceManager resourceManager() {
        return new ResourceManager();
    }
}

public class ResourceManager {
    public void init() {
        System.out.println("Initialized");
    }
    
    public void cleanup() {
        System.out.println("Cleaned up");
    }
}
```

## Testing Patterns

### Unit Test (No Spring)

```java
class UserServiceTest {
    private UserRepository mockRepository;
    private UserService service;
    
    @BeforeEach
    void setUp() {
        mockRepository = mock(UserRepository.class);
        service = new UserService(mockRepository);  // Manual injection
    }
    
    @Test
    void shouldFetchUser() {
        User user = new User(1L, "Test");
        when(mockRepository.findById(1L)).thenReturn(Optional.of(user));
        
        User result = service.getUser(1L);
        assertThat(result).isEqualTo(user);
    }
}
```

### Integration Test (With Spring)

```java
@SpringBootTest
@ActiveProfiles("test")
class UserServiceIntegrationTest {
    @Autowired
    private UserService userService;
    
    @Autowired
    private UserRepository userRepository;
    
    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }
    
    @Test
    void shouldFetchUserFromDatabase() {
        User user = User.create("test@example.com");
        userRepository.save(user);
        
        User retrieved = userService.getUser(user.getId());
        assertThat(retrieved.getEmail()).isEqualTo("test@example.com");
    }
}
```

### Slice Test

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean  // Mock the service
    private UserService userService;
    
    @Test
    void shouldReturnUser() throws Exception {
        User user = new User(1L, "Test");
        when(userService.getUser(1L)).thenReturn(user);
        
        mockMvc.perform(get("/users/1"))
            .andExpect(status().isOk());
    }
}
```

## Best Practices Summary

| Practice | Recommendation | Why |
|----------|---|---|
| Constructor injection | ✅ Mandatory | Explicit, immutable, testable |
| Setter injection | ⚠️ Optional deps | Clear optionality |
| Field injection | ❌ Never | Hidden, untestable |
| @Autowired on constructor | ✅ Implicit (4.3+) | Clear intent |
| Lombok @RequiredArgsConstructor | ✅ Recommended | Reduces boilerplate |
| Circular dependencies | ❌ Avoid | Use events instead |
| Too many dependencies | ❌ Avoid | SRP violation |
| @Lazy for expensive beans | ✅ Appropriate | Faster startup |
| Profiles for environments | ✅ Recommended | Environment-specific config |
| @Value for properties | ✅ Recommended | Type-safe injection |

## External Resources

### Official Documentation
- [Spring IoC Container](https://docs.spring.io/spring-framework/reference/core/beans.html)
- [Spring Boot Auto-Configuration](https://docs.spring.io/spring-boot/docs/current/reference/html/using.html#using.auto-configuration)
- [Conditional Bean Registration](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.developing-auto-configuration.condition-annotations)

### Related Skills
- **spring-boot-crud-patterns/SKILL.md** - DI in CRUD applications
- **spring-boot-test-patterns/SKILL.md** - Testing with DI
- **spring-boot-rest-api-standards/SKILL.md** - REST layer with DI

### Books
- "Spring in Action" (latest edition)
- "Spring Microservices in Action"

### Articles
- [Baeldung Spring Dependency Injection](https://www.baeldung.com/spring-dependency-injection)
- [Martin Fowler IoC](https://www.martinfowler.com/articles/injection.html)
