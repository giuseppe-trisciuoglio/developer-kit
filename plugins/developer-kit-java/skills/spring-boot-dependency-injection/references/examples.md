# Spring Boot Dependency Injection - Examples

Comprehensive examples demonstrating dependency injection patterns, from basic to advanced scenarios.

## Example 1: Constructor Injection (Recommended)

The preferred pattern for mandatory dependencies.

```java
// With Lombok @RequiredArgsConstructor (RECOMMENDED)
@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;

    public User registerUser(CreateUserRequest request) {
        log.info("Registering user: {}", request.getEmail());
        
        User user = User.builder()
            .email(request.getEmail())
            .name(request.getName())
            .password(passwordEncoder.encode(request.getPassword()))
            .build();
        
        User saved = userRepository.save(user);
        emailService.sendWelcomeEmail(saved.getEmail());
        
        return saved;
    }
}

// Without Lombok (Explicit)
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository,
                      EmailService emailService,
                      PasswordEncoder passwordEncoder) {
        this.userRepository = Objects.requireNonNull(userRepository);
        this.emailService = Objects.requireNonNull(emailService);
        this.passwordEncoder = Objects.requireNonNull(passwordEncoder);
    }

    public User registerUser(CreateUserRequest request) {
        // Implementation
    }
}
```

### Test (Easy - No Spring Needed)

```java
@Test
void shouldRegisterUserAndSendEmail() {
    // Arrange - Create mocks manually
    UserRepository mockRepository = mock(UserRepository.class);
    EmailService mockEmailService = mock(EmailService.class);
    PasswordEncoder mockEncoder = mock(PasswordEncoder.class);
    
    UserService service = new UserService(mockRepository, mockEmailService, mockEncoder);
    
    User user = User.builder().email("test@example.com").build();
    when(mockRepository.save(any())).thenReturn(user);
    when(mockEncoder.encode("password")).thenReturn("encoded");

    // Act
    User result = service.registerUser(new CreateUserRequest("test@example.com", "Test", "password"));

    // Assert
    assertThat(result.getEmail()).isEqualTo("test@example.com");
    verify(mockEmailService).sendWelcomeEmail("test@example.com");
}
```

---

## Example 2: Setter Injection for Optional Dependencies

Use setter injection ONLY for optional dependencies with sensible defaults.

```java
@Service
public class ReportService {
    private final ReportRepository reportRepository;
    private EmailService emailService;  // Optional
    private CacheService cacheService;   // Optional

    // Constructor for mandatory dependency
    public ReportService(ReportRepository reportRepository) {
        this.reportRepository = Objects.requireNonNull(reportRepository);
    }

    // Setters for optional dependencies
    @Autowired(required = false)
    public void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }

    @Autowired(required = false)
    public void setCacheService(CacheService cacheService) {
        this.cacheService = cacheService;
    }

    public Report generateReport(ReportRequest request) {
        Report report = reportRepository.create(request.getTitle());

        // Use optional services if available
        if (emailService != null) {
            emailService.sendReport(report);
        }

        if (cacheService != null) {
            cacheService.cache(report);
        }

        return report;
    }
}
```

---

## Example 3: Configuration with Multiple Bean Definitions

```java
@Configuration
public class AppConfig {

    // Bean 1: Database
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

    // Bean 2: Transaction Manager (depends on DataSource)
    @Bean
    public JpaTransactionManager transactionManager(EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }

    // Bean 3: Repository (depends on DataSource via JPA)
    @Bean
    public UserRepository userRepository(UserJpaRepository jpaRepository) {
        return new UserRepositoryAdapter(jpaRepository);
    }

    // Bean 4: Service (depends on Repository)
    @Bean
    public UserService userService(UserRepository repository) {
        return new UserService(repository);
    }
}
```

---

## Example 4: Resolving Ambiguities with @Qualifier

```java
@Configuration
public class DataSourceConfig {
    
    @Bean(name = "primaryDB")
    public DataSource primaryDataSource() {
        return new HikariDataSource();
    }

    @Bean(name = "secondaryDB")
    public DataSource secondaryDataSource() {
        return new HikariDataSource();
    }
}

@Service
public class MultiDatabaseService {
    private final DataSource primaryDataSource;
    private final DataSource secondaryDataSource;

    // Using @Qualifier to resolve ambiguity
    public MultiDatabaseService(
            @Qualifier("primaryDB") DataSource primary,
            @Qualifier("secondaryDB") DataSource secondary) {
        this.primaryDataSource = primary;
        this.secondaryDataSource = secondary;
    }

    public void performOperation() {
        // Use primary for writes
        executeUpdate(primaryDataSource);
        
        // Use secondary for reads
        executeQuery(secondaryDataSource);
    }
}

// Alternative: Using @Primary
@Configuration
public class PrimaryDataSourceConfig {
    
    @Bean
    @Primary  // This bean is preferred when multiple exist
    public DataSource primaryDataSource() {
        return new HikariDataSource();
    }

    @Bean
    public DataSource secondaryDataSource() {
        return new HikariDataSource();
    }
}
```

---

## Example 5: Conditional Bean Registration

```java
@Configuration
public class OptionalFeatureConfig {

    // Only create if feature is enabled
    @Bean
    @ConditionalOnProperty(name = "feature.notifications.enabled", havingValue = "true")
    public NotificationService notificationService() {
        return new EmailNotificationService();
    }

    // Fallback if no other bean exists
    @Bean
    @ConditionalOnMissingBean(NotificationService.class)
    public NotificationService defaultNotificationService() {
        return new NoOpNotificationService();
    }

    // Only create if class is on classpath
    @Bean
    @ConditionalOnClass(RedisTemplate.class)
    public CacheService cacheService() {
        return new RedisCacheService();
    }
}

@Service
public class OrderService {
    private final NotificationService notificationService;

    public OrderService(NotificationService notificationService) {
        this.notificationService = notificationService;  // Works regardless of implementation
    }

    public void createOrder(Order order) {
        // Always works, but behavior depends on enabled features
        notificationService.sendConfirmation(order);
    }
}
```

---

## Example 6: Profiles and Environment-Specific Configuration

```java
@Configuration
@Profile("production")
public class ProductionConfig {

    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://prod-db:5432/production");
        config.setMaximumPoolSize(30);
        config.setMaxLifetime(1800000);  // 30 minutes
        return new HikariDataSource(config);
    }

    @Bean
    public SecurityService securityService() {
        return new StrictSecurityService();
    }
}

@Configuration
@Profile("test")
public class TestConfig {

    @Bean
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .addScript("classpath:schema.sql")
            .addScript("classpath:test-data.sql")
            .build();
    }

    @Bean
    public SecurityService securityService() {
        return new PermissiveSecurityService();
    }
}

@Configuration
@Profile("development")
public class DevelopmentConfig {

    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/dev");
        return new HikariDataSource(config);
    }

    @Bean
    public SecurityService securityService() {
        return new DebugSecurityService();
    }
}
```

**Usage:**
```bash
export SPRING_PROFILES_ACTIVE=production
# or in application.properties:
# spring.profiles.active=production
```

---

## Example 7: Lazy Initialization

```java
@Configuration
public class ExpensiveResourceConfig {

    @Bean
    @Lazy  // Created only when first accessed
    public ExpensiveService expensiveService() {
        System.out.println("ExpensiveService initialized (lazy)");
        return new ExpensiveService();
    }

    @Bean
    public NormalService normalService(ExpensiveService expensive) {
        // ExpensiveService not created yet
        return new NormalService(expensive);  // Lazy proxy injected here
    }
}

@SpringBootTest
class LazyInitializationTest {
    @Test
    void shouldInitializeExpensiveServiceLazy() {
        ApplicationContext context = new AnnotationConfigApplicationContext(ExpensiveResourceConfig.class);
        
        // ExpensiveService not initialized yet
        assertThat(context.getBean(NormalService.class)).isNotNull();
        
        // Now ExpensiveService is initialized
        ExpensiveService service = context.getBean(ExpensiveService.class);
        assertThat(service).isNotNull();
    }
}
```

---

## Example 8: Circular Dependency Resolution with Events

```java
// ❌ BAD - Circular dependency
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

// ✅ GOOD - Use events to decouple
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
        // Create welcome order when user registers
        Order welcomeOrder = Order.createWelcomeOrder(event.getUserId());
        orderRepository.save(welcomeOrder);
    }
}
```

---

## Example 9: Component Scanning

```java
@Configuration
@ComponentScan(basePackages = {
    "com.example.users",
    "com.example.products",
    "com.example.orders"
})
public class AppConfig {
}

// Alternative: Exclude packages
@Configuration
@ComponentScan(basePackages = "com.example",
    excludeFilters = @ComponentScan.Filter(type = FilterType.REGEX,
        pattern = "com\\.example\\.internal\\..*"))
public class AppConfig {
}

// Auto-discovered by Spring Boot
@SpringBootApplication  // Implies @ComponentScan("package.of.main.class")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

---

## Example 10: Testing with Constructor Injection

```java
// ❌ Service with field injection (hard to test)
@Service
public class BadUserService {
    @Autowired
    private UserRepository userRepository;
    
    public User getUser(Long id) {
        return userRepository.findById(id).orElse(null);
    }
}

@Test
void testBadService() {
    // Must use Spring to test this
    UserService service = new BadUserService();
    // Can't inject mocks without reflection or Spring
}

// ✅ Service with constructor injection (easy to test)
@Service
@RequiredArgsConstructor
public class GoodUserService {
    private final UserRepository userRepository;
    
    public User getUser(Long id) {
        return userRepository.findById(id).orElse(null);
    }
}

@Test
void testGoodService() {
    // Can test directly without Spring
    UserRepository mockRepository = mock(UserRepository.class);
    UserService service = new GoodUserService(mockRepository);
    
    User mockUser = new User(1L, "Test");
    when(mockRepository.findById(1L)).thenReturn(Optional.of(mockUser));
    
    User result = service.getUser(1L);
    assertThat(result.getName()).isEqualTo("Test");
}

// Integration test
@SpringBootTest
@ActiveProfiles("test")
class UserServiceIntegrationTest {
    @Autowired
    private UserService userService;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    void shouldFetchUserFromDatabase() {
        User user = User.create("test@example.com");
        userRepository.save(user);
        
        User retrieved = userService.getUser(user.getId());
        assertThat(retrieved.getEmail()).isEqualTo("test@example.com");
    }
}
```

These examples cover constructor injection (recommended), setter injection (optional dependencies), configuration, testing patterns, and common best practices for dependency injection in Spring Boot.
