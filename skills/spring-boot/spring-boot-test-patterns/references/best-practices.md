# Spring Boot Testing Best Practices

## Choose the Right Test Type

Select the most efficient test annotation for your use case:

```java
// Use @DataJpaTest for repository-only tests (fastest)
@DataJpaTest
public class UserRepositoryTest { }

// Use @WebMvcTest for controller-only tests
@WebMvcTest(UserController.class)
public class UserControllerTest { }

// Use @SpringBootTest only for full integration testing
@SpringBootTest
public class UserServiceFullIntegrationTest { }
```

## Use @ServiceConnection for Container Management (Spring Boot 3.5+)

Prefer `@ServiceConnection` over manual `@DynamicPropertySource` for cleaner code:

```java
// Good - Spring Boot 3.5+
@TestConfiguration
public class TestConfig {
    @Bean
    @ServiceConnection
    public PostgreSQLContainer<?> postgres() {
        return new PostgreSQLContainer<>(DockerImageName.parse("postgres:16-alpine"));
    }
}

// Avoid - Manual property registration
@DynamicPropertySource
static void registerProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
    // ... more properties
}
```

## Keep Tests Deterministic

Always initialize test data explicitly and never depend on test execution order:

```java
// Good - Explicit setup
@BeforeEach
void setUp() {
    userRepository.deleteAll();
    User user = new User();
    user.setEmail("test@example.com");
    userRepository.save(user);
}

// Avoid - Depending on other tests
@Test
void testUserExists() {
    // Assumes previous test created a user
    Optional<User> user = userRepository.findByEmail("test@example.com");
    assertThat(user).isPresent();
}
```

## Use Transactional Tests Carefully

Mark test classes with `@Transactional` for automatic rollback, but understand the implications:

```java
@SpringBootTest
@Transactional  // Automatically rolls back after each test
public class UserControllerIntegrationTest {

    @Test
    void shouldCreateUser() throws Exception {
        // Changes will be rolled back after test
        mockMvc.perform(post("/api/users")....)
            .andExpect(status().isCreated());
    }
}
```

**Note**: Be aware that `@Transactional` test behavior may differ from production due to lazy loading and flush semantics.

## Organize Tests by Layer

Group related tests in separate classes to optimize context caching:

```java
// Repository tests (uses @DataJpaTest)
public class UserRepositoryTest { }

// Controller tests (uses @WebMvcTest)
public class UserControllerTest { }

// Service tests (uses mocks, no context)
public class UserServiceTest { }

// Full integration tests (uses @SpringBootTest)
public class UserFullIntegrationTest { }
```

## Use Meaningful Assertions

Leverage AssertJ for readable, fluent assertions:

```java
// Good - Clear, readable assertions
assertThat(user.getEmail())
    .isEqualTo("test@example.com");

assertThat(users)
    .hasSize(3)
    .contains(expectedUser);

assertThatThrownBy(() -> userService.save(invalidUser))
    .isInstanceOf(ValidationException.class)
    .hasMessageContaining("Email is required");

// Avoid - JUnit assertions
assertEquals("test@example.com", user.getEmail());
assertTrue(users.size() == 3);
```

## Mock External Dependencies

Mock external services but use real databases for integration tests:

```java
// Good - Mock external services, use real DB
@SpringBootTest
@TestContainerConfig.class
public class OrderServiceTest {

    @MockBean
    private EmailService emailService;

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void shouldSendConfirmationEmail() {
        // Use real database, mock email service
        Order order = new Order();
        orderService.createOrder(order);

        verify(emailService, times(1)).sendConfirmation(order);
    }
}

// Avoid - Mocking the database layer
@Test
void shouldCreateOrder() {
    when(orderRepository.save(any())).thenReturn(mockOrder);
    // Tests don't verify actual database behavior
}
```

## Use Test Fixtures for Common Data

Create reusable test data builders:

```java
public class UserTestFixture {
    public static User validUser() {
        User user = new User();
        user.setEmail("test@example.com");
        user.setName("Test User");
        return user;
    }

    public static User userWithEmail(String email) {
        User user = validUser();
        user.setEmail(email);
        return user;
    }
}

// Usage in tests
@Test
void shouldSaveUser() {
    User user = UserTestFixture.validUser();
    userRepository.save(user);
    assertThat(userRepository.count()).isEqualTo(1);
}
```

## Document Complex Test Scenarios

Use `@DisplayName` and comments for complex test logic:

```java
@Test
@DisplayName("Should validate email format and reject duplicates with proper error message")
void shouldValidateEmailBeforePersisting() {
    // Given: Two users with the same email
    User user1 = new User();
    user1.setEmail("test@example.com");
    userRepository.save(user1);

    User user2 = new User();
    user2.setEmail("test@example.com");  // Duplicate email

    // When: Attempting to save duplicate
    // Then: Should throw exception with clear message
    assertThatThrownBy(() -> {
        userRepository.save(user2);
        userRepository.flush();
    })
    .isInstanceOf(DataIntegrityViolationException.class)
    .hasMessageContaining("unique constraint");
}
```

## Avoid Common Pitfalls

```java
// Avoid: Using @DirtiesContext without reason (forces context rebuild)
@SpringBootTest
@DirtiesContext  // DON'T USE unless absolutely necessary
public class ProblematicTest { }

// Avoid: Mixing multiple profiles in same test suite
@SpringBootTest(properties = "spring.profiles.active=dev,test,prod")
public class MultiProfileTest { }

// Avoid: Starting containers manually
@SpringBootTest
public class ManualContainerTest {
    static {
        PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>();
        postgres.start();  // Avoid - use @ServiceConnection instead
    }
}

// Good: Consistent configuration, minimal context switching
@SpringBootTest
@TestContainerConfig
public class ProperTest { }
```

## Test Naming Conventions

Convention: Use descriptive method names that start with `should` or `test` to make test intent explicit.

**Naming Rules:**
- **Prefix**: Start with `should` or `test` to clearly indicate test purpose
- **Structure**: Use camelCase for readability (no underscores)
- **Clarity**: Name should indicate what is being tested and the expected outcome
- **Example pattern**: `should[ExpectedBehavior]When[Condition]()`

**Examples:**
```
shouldReturnUsersJson()
shouldThrowNotFoundWhenIdDoesntExist()
shouldPropagateExceptionOnPersistenceError()
shouldSaveAndRetrieveUserFromDatabase()
shouldValidateEmailFormatBeforePersisting()
```

Apply these rules consistently across all integration test methods.