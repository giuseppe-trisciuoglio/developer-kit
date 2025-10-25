---
name: spring-boot-dependency-injection
description: Best practices for Dependency Injection in Spring Boot. Covers constructor injection, setter injection, field injection anti-patterns, autowiring strategies, and testability patterns.
category: backend
tags: [ spring-boot, dependency-injection, constructor-injection, autowiring, best-practices, testing, java ]
version: 1.0.0
context7_library: /spring-projects/spring-framework
context7_trust_score: 9.0
language: en
license: See LICENSE
---

# Spring Boot Dependency Injection Best Practices

This skill provides comprehensive guidance on implementing Dependency Injection (DI) in Spring Boot applications with
emphasis on best practices, testability, and clean architecture. It covers IoC principles, injection types, and patterns
for writing maintainable Java code.

## When to Use This Skill

Use this skill when:

- Designing Spring components and services with clear dependency management
- Implementing constructor injection for required dependencies
- Choosing between constructor, setter, and field injection patterns
- Configuring autowiring strategies and resolving ambiguities
- Writing testable code with minimal Spring coupling
- Setting up Java configuration (@Configuration) for complex bean definitions
- Understanding Inversion of Control (IoC) container mechanics
- Reviewing code for dependency injection anti-patterns

## Core Concepts

### Inversion of Control (IoC) Principle

IoC is a principle where the control of object creation and dependency management is transferred from your code to a
framework. Instead of your code calling libraries, the framework calls your code.

**Traditional Programming (Tight Coupling):**

```java
public class Store {
    private Item item;

    public Store() {
        item = new ItemImpl1();  // Store creates its own dependency
    }
}
```

**With IoC/Dependency Injection (Loose Coupling):**

```java
public class Store {
    private final Item item;

    public Store(Item item) {  // Dependency is provided externally
        this.item = item;
    }
}
```

### Benefits of Dependency Injection

- **Loose Coupling**: Components depend on abstractions, not concrete implementations
- **Testability**: Easy to inject mock dependencies in tests
- **Flexibility**: Switch implementations without changing code
- **Modularity**: Clear component boundaries and responsibilities
- **Maintainability**: Dependencies are explicit and visible

## Spring IoC Container

The `ApplicationContext` interface represents Spring's IoC container. It is responsible for:

1. **Instantiating** beans (application components)
2. **Configuring** beans with their dependencies
3. **Assembling** beans into working application
4. **Managing** bean lifecycle (creation, initialization, destruction)

```java
// The container manages all beans and their lifecycle
@Configuration
public class AppConfig {
    @Bean
    public UserRepository userRepository() {
        return new JpaUserRepository();
    }

    @Bean
    public UserService userService(UserRepository repo) {
        // Container automatically injects UserRepository
        return new UserService(repo);
    }
}
```

## Dependency Injection Types

### 1. Constructor Injection (⭐ RECOMMENDED)

Constructor injection is the **preferred method** because it:

- Makes dependencies **mandatory and explicit**
- Enables **immutability** with `final` fields
- **Simplifies testing** (no Spring magic needed)
- Fails fast if dependency is missing
- Works well with records and value objects

**With Lombok (Recommended):**

```java

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;

    public User registerUser(CreateUserRequest request) {
        log.info("Registering user with email: {}", request.getEmail());
        User user = User.create(
                request.getName(),
                request.getEmail(),
                passwordEncoder.encode(request.getPassword())
        );
        return userRepository.save(user);
    }
}
```

Lombok's `@RequiredArgsConstructor` generates:

```java
public UserService(UserRepository userRepository,
                   EmailService emailService,
                   PasswordEncoder passwordEncoder) {
    this.userRepository = userRepository;
    this.emailService = emailService;
    this.passwordEncoder = passwordEncoder;
}
```

**Without Lombok (Explicit):**

```java

@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }

    public User create(CreateUserRequest request) {
        return userRepository.save(new User(request.getName(), request.getEmail()));
    }
}
```

**Testing Constructor-Injected Dependencies (Easy):**

```java

@Test
void testUserServiceCreation() {
    // No Spring needed - straightforward unit test
    UserRepository mockRepo = mock(UserRepository.class);
    EmailService mockEmail = mock(EmailService.class);
    PasswordEncoder mockEncoder = mock(PasswordEncoder.class);

    UserService service = new UserService(mockRepo, mockEmail, mockEncoder);

    // Test business logic directly
    User user = service.registerUser(new CreateUserRequest("test@example.com", "password"));

    verify(mockRepo).save(any(User.class));
}
```

### 2. Setter Injection (⚠️ USE FOR OPTIONAL DEPENDENCIES ONLY)

Use setter injection **only** for optional dependencies that have sensible defaults.

```java

@Service
public class ReportService {
    private final ReportRepository reportRepository;
    private EmailService emailService; // Optional

    // Constructor injection for mandatory dependency
    public ReportService(ReportRepository reportRepository) {
        this.reportRepository = reportRepository;
    }

    // Setter for optional dependency
    @Autowired(required = false)
    public void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }

    public Report generateReport(ReportRequest request) {
        Report report = reportRepository.create(request.getTitle());

        // Email is optional
        if (emailService != null) {
            emailService.sendReport(report);
        }

        return report;
    }
}
```

### 3. Field Injection (❌ AVOID)

Field injection should be **avoided** because it:

- Hides dependencies (not visible in constructor)
- Makes unit testing difficult (requires Spring context)
- Enables mutable state (missing `final`)
- Violates single responsibility if too many injected fields
- Doesn't work with records or final fields

**❌ Bad Pattern - Do Not Use:**

```java

@Service
public class BadUserService {
    @Autowired
    private UserRepository userRepository;  // ❌ Hidden dependency

    @Autowired
    private EmailService emailService;      // ❌ Mutable state

    public User create(CreateUserRequest request) {
        return userRepository.save(new User(request.getName()));
    }
}
```

**Problems with Above Code:**

1. Dependencies are not visible in the class signature
2. Cannot instantiate without Spring (no-arg constructor)
3. Hard to test without Spring context
4. Mutable fields allow runtime modification
5. No clear contract of what the class needs

## Autowiring Strategies

Spring supports different autowiring modes. Set the `autowire` attribute in XML or use `@Autowired` with specific
matching strategies:

### 1. byType (Default) - ⭐ RECOMMENDED

```java
// Matches bean by type (interface or class)
@Service
public class UserService {
    private final UserRepository userRepository;

    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

**Spring Configuration:**

```xml

<bean id="userService" class="com.example.UserService" autowire="byType"/>
```

### 2. byName

```java
// Matches bean by parameter name
@Service
public class PaymentService {
    private final PaymentGateway paymentGateway;

    @Autowired
    public PaymentService(PaymentGateway paymentGateway) {
        // Bean name "paymentGateway" must match
        this.paymentGateway = paymentGateway;
    }
}
```

### 3. constructor

```java
// Spring selects the appropriate constructor
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final NotificationService notificationService;

    @Autowired
    public OrderService(OrderRepository orderRepository,
                        NotificationService notificationService) {
        this.orderRepository = orderRepository;
        this.notificationService = notificationService;
    }
}
```

### Resolving Ambiguities

When multiple beans of the same type exist, use `@Qualifier`:

```java

@Configuration
public class DataSourceConfig {
    @Bean(name = "primaryDataSource")
    public DataSource primaryDataSource() {
        return new HikariDataSource();
    }

    @Bean(name = "secondaryDataSource")
    public DataSource secondaryDataSource() {
        return new HikariDataSource();
    }
}

@Service
public class DatabaseService {
    private final DataSource primaryDataSource;
    private final DataSource secondaryDataSource;

    public DatabaseService(
            @Qualifier("primaryDataSource") DataSource primary,
            @Qualifier("secondaryDataSource") DataSource secondary) {
        this.primaryDataSource = primary;
        this.secondaryDataSource = secondary;
    }
}
```

## Java Configuration (@Configuration)

Modern Spring prefers Java configuration over XML:

### Basic Bean Definition

```java

@Configuration
public class AppConfig {

    @Bean
    public UserRepository userRepository() {
        return new JpaUserRepository();
    }

    @Bean
    public UserService userService(UserRepository userRepository) {
        // Constructor injection - Spring automatically provides dependency
        return new UserService(userRepository);
    }
}
```

### Complex Bean Configuration

```java

@Configuration
public class DatabaseConfig {

    @Bean
    public DataSource dataSource(
            @Value("${spring.datasource.url}") String url,
            @Value("${spring.datasource.username}") String username,
            @Value("${spring.datasource.password}") String password) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(url);
        config.setUsername(username);
        config.setPassword(password);
        config.setMaximumPoolSize(20);
        return new HikariDataSource(config);
    }

    @Bean
    public JpaTransactionManager transactionManager(EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }
}
```

### Conditional Beans

```java

@Configuration
public class FeatureConfig {

    @Bean
    @ConditionalOnProperty(name = "feature.notifications.enabled", havingValue = "true")
    public NotificationService notificationService() {
        return new EmailNotificationService();
    }

    @Bean
    @ConditionalOnMissingBean(NotificationService.class)
    public NotificationService defaultNotificationService() {
        return new NoOpNotificationService();
    }
}
```

## Component Scanning and Annotation-Based Configuration

### Auto-Discovery with Stereotypes

```java
// @Component is the generic stereotype
@Component
public class GenericComponent {
}

// @Service indicates application service layer
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
}

// @Repository indicates data access layer
@Repository
public class UserJpaRepository implements UserRepository {
}

// @Controller indicates presentation layer (MVC)
@Controller
public class UserViewController {
}

// @RestController indicates REST API layer
@RestController
@RequestMapping("/api/users")
public class UserRestController {
}
```

### Package Scanning Configuration

```java

@Configuration
@ComponentScan(basePackages = {
        "com.example.users",
        "com.example.products",
        "com.example.orders"
})
public class AppConfig {
}
```

## Lazy Initialization

By default, Spring creates all singleton beans at startup. For performance optimization, use lazy initialization:

### Annotation-Based

```java

@Service
@Lazy
public class ExpensiveService {
    public ExpensiveService() {
        log.info("ExpensiveService initialized (lazy)");
    }
}
```

### XML Configuration

```xml

<bean id="expensiveService" class="com.example.ExpensiveService" lazy-init="true"/>
```

**Trade-offs:**

- ✅ Faster startup time
- ❌ Errors discovered later (when bean first accessed)
- ⚠️ Use only for seldom-used beans

## Profiles and Environment-Specific Configuration

```java

@Configuration
@Profile("production")
public class ProductionConfig {

    @Bean
    public DataSource dataSource() {
        // Production database configuration
        return new HikariDataSource();
    }
}

@Configuration
@Profile("test")
public class TestConfig {

    @Bean
    public DataSource dataSource() {
        // In-memory test database
        return new EmbeddedDatabaseBuilder()
                .setType(EmbeddedDatabaseType.H2)
                .build();
    }
}
```

Activate profiles:

```bash
# Via environment variable
export SPRING_PROFILES_ACTIVE=production

# Via application.properties
spring.profiles.active=production

# Via test annotation
@SpringBootTest
@ActiveProfiles("test")
class UserServiceTest {
}
```

## Testing with Dependency Injection

### Unit Testing (No Spring)

```java
class UserServiceTest {

    private UserService userService;
    private UserRepository mockUserRepository;
    private EmailService mockEmailService;

    @BeforeEach
    void setUp() {
        // Create mocks
        mockUserRepository = mock(UserRepository.class);
        mockEmailService = mock(EmailService.class);

        // Inject mocks manually (no Spring needed)
        userService = new UserService(mockUserRepository, mockEmailService);
    }

    @Test
    void shouldCreateUserAndSendWelcomeEmail() {
        // Given
        CreateUserRequest request = new CreateUserRequest("john@example.com", "John");
        when(mockUserRepository.save(any(User.class)))
                .thenReturn(new User(1L, "john@example.com", "John"));

        // When
        User created = userService.registerUser(request);

        // Then
        assertEquals("John", created.getName());
        verify(mockEmailService).sendWelcomeEmail(any(User.class));
    }
}
```

### Integration Testing with Spring

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
    void shouldCreateUserInDatabase() {
        // Given
        CreateUserRequest request = new CreateUserRequest("jane@example.com", "Jane");

        // When
        User created = userService.registerUser(request);

        // Then
        Optional<User> fetched = userRepository.findById(created.getId());
        assertTrue(fetched.isPresent());
        assertEquals("Jane", fetched.get().getName());
    }
}
```

### Slice Testing for Specific Layers

```java
// Test REST layer only (no business logic or database)
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void shouldReturnUserById() throws Exception {
        User user = new User(1L, "john@example.com", "John");
        when(userService.getById(1L)).thenReturn(user);

        mockMvc.perform(get("/api/users/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("John"));
    }
}

// Test data layer only (with embedded database)
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldFindUserByEmail() {
        User user = new User(null, "john@example.com", "John");
        User saved = userRepository.save(user);

        Optional<User> found = userRepository.findByEmail("john@example.com");
        assertTrue(found.isPresent());
        assertEquals(saved.getId(), found.get().getId());
    }
}
```

## Common Anti-Patterns to Avoid

### 1. Service Locator Pattern (❌ Avoid)

```java
// ❌ Bad: Service locator pattern
@Service
public class BadUserService {
    @Autowired
    private ApplicationContext context; // Hidden dependency on container

    public void processUser(Long userId) {
        UserRepository repo = context.getBean(UserRepository.class);
        User user = repo.findById(userId).orElseThrow();
        // ...
    }
}
```

**Better: Constructor injection**

```java

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    public void processUser(Long userId) {
        User user = userRepository.findById(userId).orElseThrow();
    }
}
```

### 2. Circular Dependencies (❌ Avoid)

```java
// ❌ Bad: Circular dependency
@Service
public class UserService {
    private final OrderService orderService;

    public UserService(OrderService orderService) {
        this.orderService = orderService;
    }
}

@Service
public class OrderService {
    private final UserService userService;

    public OrderService(UserService userService) {
        this.userService = userService;
    }
}
```

**Better: Extract shared logic or use events**

```java
// Use domain events for decoupling
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final ApplicationEventPublisher eventPublisher;

    public User registerUser(CreateUserRequest request) {
        User user = User.create(request.getName(), request.getEmail());
        User saved = userRepository.save(user);

        // Publish event instead of calling OrderService directly
        eventPublisher.publishEvent(new UserRegisteredEvent(saved.getId()));

        return saved;
    }
}

@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;

    @EventListener
    public void onUserRegistered(UserRegisteredEvent event) {
        // Create welcome order for new user
        orderRepository.createWelcomeOrder(event.getUserId());
    }
}
```

### 3. Too Many Dependencies (❌ Violation of SRP)

```java
// ❌ Bad: Too many dependencies
@Service
public class MegaUserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final SmsService smsService;
    private final AnalyticsService analyticsService;
    private final PaymentService paymentService;
    private final NotificationService notificationService;

    public MegaUserService(UserRepository ur, EmailService es, SmsService ss,
                           AnalyticsService as, PaymentService ps,
                           NotificationService ns) {
        // Constructor with 6 dependencies...
    }
}
```

**Better: Split into focused services**

```java

@Service
@RequiredArgsConstructor
public class UserRegistrationService {
    private final UserRepository userRepository;
    private final UserNotificationService notificationService;

    public User registerUser(CreateUserRequest request) {
        User user = User.create(request.getName(), request.getEmail());
        User saved = userRepository.save(user);
        notificationService.sendWelcomeNotification(saved);
        return saved;
    }
}

@Service
@RequiredArgsConstructor
public class UserNotificationService {
    private final EmailService emailService;
    private final SmsService smsService;

    public void sendWelcomeNotification(User user) {
        emailService.send(user.getEmail(), "Welcome!");
        if (user.hasPhoneNumber()) {
            smsService.send(user.getPhoneNumber(), "Welcome!");
        }
    }
}
```

## Best Practices Summary

| Practice                            | Recommendation                 | Why                                   |
|-------------------------------------|--------------------------------|---------------------------------------|
| **Constructor Injection**           | ✅ Always for mandatory deps    | Explicit, immutable, testable         |
| **Setter Injection**                | ⚠️ Only for optional deps      | Clear that dependency is optional     |
| **Field Injection**                 | ❌ Never                        | Hidden, untestable, mutable           |
| **@Autowired on Constructor**       | ✅ Spring 4.3+ (often implicit) | Makes intent clear                    |
| **Lombok @RequiredArgsConstructor** | ✅ Recommended                  | Reduces boilerplate                   |
| **Circular Dependencies**           | ❌ Avoid                        | Use events or refactor                |
| **Too Many Dependencies**           | ❌ Avoid                        | Violates SRP, extract services        |
| **Service Locator**                 | ❌ Avoid                        | Hides dependencies                    |
| **Lazy Initialization**             | ⚠️ Use sparingly               | Trade-off: startup vs error detection |
| **@Primary / @Qualifier**           | ✅ Use to resolve ambiguity     | Clear when multiple beans exist       |

## Related Skills

- **spring-boot-rest-api-standards/SKILL.md** — REST endpoint patterns with constructor injection
- **spring-boot-crud-patterns/SKILL.md** — CRUD APIs with DDD and constructor injection
- **junit-test-patterns/SKILL.md** — Unit and integration testing patterns
- **spring-boot-test-patterns/SKILL.md** — Testcontainers and integration test setup

## Summary

This skill emphasizes **constructor injection as the primary dependency injection pattern** in Spring Boot applications:

### Key Takeaways:

1. **Use Constructor Injection** for all mandatory dependencies
    - Makes dependencies explicit and visible
    - Enables immutability with `final` fields
    - Simplifies testing (no Spring magic needed)
    - Use Lombok's `@RequiredArgsConstructor` to reduce boilerplate

2. **Use Setter Injection** only for optional dependencies
    - Mark with `@Autowired(required = false)`
    - Provide sensible defaults

3. **Avoid Field Injection** completely
    - Hides dependencies
    - Makes testing difficult
    - Violates immutability principle

4. **Write Testable Code**
    - Unit test without Spring context
    - Inject mocks manually in tests
    - Use slice tests for specific layers

5. **Choose byType Autowiring** (Spring default)
    - Most intuitive and least error-prone
    - Use `@Qualifier` to resolve ambiguities

6. **Apply SOLID Principles**
    - Keep services focused (Single Responsibility)
    - Inject only what you need
    - Use events for decoupling complex interactions

This comprehensive approach ensures applications are maintainable, testable, and follow Spring Framework best practices.
