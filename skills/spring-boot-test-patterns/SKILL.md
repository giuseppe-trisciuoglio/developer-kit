---
name: spring-boot-integration-test-patterns
description: Comprehensive integration testing for Spring Boot applications using Java, Testcontainers, Spring Boot test annotations, and best practices for slice tests, full-stack tests, and performance optimization
category: testing
tags: [spring-boot, java, integration-testing, testcontainers, junit5, spring-test, testing-best-practices, mocking, test-slices]
version: 1.0.0
language: en
license: See LICENSE
context7_library: /spring-projects/spring-boot
context7_trust_score: 7.5
---

# Spring Boot Integration Test Patterns (Java)

## Description

This skill provides comprehensive guidance for writing integration tests for Spring Boot applications using Java. It covers Spring Boot test annotations, Testcontainers, test slice patterns, and optimization techniques for database-driven, HTTP-based, and reactive applications.

## When to Use This Skill

Use this skill when:
- Writing integration tests for controllers, repositories, or services
- Testing with real databases using Testcontainers
- Configuring Spring Boot test slices (@DataJpaTest, @WebMvcTest, @WebFluxTest)
- Setting up test containers with Spring Boot 3.5+ @ServiceConnection
- Optimizing test performance by reusing contexts and containers
- Testing full-stack flows with MockMvc or TestRestTemplate
- Testing reactive applications with WebTestClient
- Implementing @DynamicPropertySource for custom test configuration
- Configuring CI/CD pipelines for integration tests with Docker
- Managing test context caching and performance

## Core Concepts

### Test Architecture Philosophy

Spring Boot integration tests are organized around three key principles:

**1. Use Test Slices for Focused Testing**

Test slices load a minimal Spring context containing only the components needed for that specific test. This significantly improves performance compared to full @SpringBootTest.

- Use `@DataJpaTest` for repository and entity testing
- Use `@WebMvcTest` for MVC controller testing
- Use `@WebFluxTest` for reactive controller testing
- Use `@JsonTest` for JSON serialization testing
- Use `@RestClientTest` for REST client testing
- Use `@SpringBootTest` for full integration testing only when necessary

**2. Leverage Spring Boot 3.5+ @ServiceConnection**

Spring Boot 3.5+ provides first-class support for Testcontainers through `@ServiceConnection`. This eliminates boilerplate code for container configuration and property mapping.

Benefits:
- Automatic lifecycle management (start/stop)
- Automatic property mapping (spring.datasource.*, etc.)
- Simplified test configuration
- Less manual setup code

**3. Optimize Context Caching**

Spring caches ApplicationContext instances based on configuration parameters. Minimize unique contexts to maximize caching:

- Group tests by profile/properties
- Reuse the same @SpringBootTest configuration across multiple test classes
- Avoid @DirtiesContext unless absolutely necessary (forces context rebuild)
- Use @DirtiesContext only on specific methods that mutate global state

### Test Method Naming

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

## Dependencies (examples)

Gradle (build.gradle.kts)

```kotlin
dependencies {
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:junit-jupiter:1.19.0")
    testImplementation("org.testcontainers:postgresql:1.19.0")
}
```

Maven (pom.xml)

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>junit-jupiter</artifactId>
  <version>1.19.0</version>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.testcontainers</groupId>
  <artifactId>postgresql</artifactId>
  <version>1.19.0</version>
  <scope>test</scope>
</dependency>
```

Adjust versions to match your project and the Testcontainers compatibility matrix.

## Full application tests (HTTP)

Example: MockMvc with @SpringBootTest (MVC stack)

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void shouldReturnUsersJson() throws Exception {
        mockMvc.perform(get("/api/users").header("Content-Type", "application/json"))
            .andExpect(status().isOk())
            .andExpect(content().contentType("application/json"));
    }
}
```

Example: TestRestTemplate with a random port (blocking, MVC)

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.ResponseEntity;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class UserRestTemplateIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void shouldReturn200AndBodyWhenGettingUsers() {
        ResponseEntity<String> response = restTemplate.getForEntity("/api/users", String.class);
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(response.getBody()).isNotNull();
    }
}
```

Example: WebTestClient for reactive stacks (WebFlux)

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.reactive.server.WebTestClient;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
public class UserWebTestClientIntegrationTest {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void shouldReturnJsonArrayWithUserId() {
        webTestClient.get().uri("/api/users")
            .exchange()
            .expectStatus().isOk()
            .expectBody()
            .jsonPath("$[0].id").exists();
    }
}
```

## Testcontainers with Spring Boot > 3.5: @ServiceConnection (preferred)

Spring Boot 3.5+ provides first-class support for wiring Testcontainers as service connections. Declare a @Bean annotated with @ServiceConnection that returns the container instance; Spring Boot will map container connection details to the appropriate spring.* properties automatically.

Example TestConfiguration that exposes a PostgreSQL container via @ServiceConnection:

```java
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

@TestConfiguration
public class TestContainerConfig {

    @Bean
    @ServiceConnection
    public PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>(DockerImageName.parse("postgres:16-alpine"))
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
        // Do not call start(); Spring Boot will manage lifecycle for @ServiceConnection beans
    }
}
```

Usage: import or include this configuration in your tests to let Spring Boot automatically configure spring.datasource.* and other connection properties.

## Fallback: DynamicPropertySource and shared container

If you need explicit control or run on Boot < 3.5, use a shared container singleton and register properties with @DynamicPropertySource.

```java
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

public class SharedContainers {
    static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>(DockerImageName.parse("postgres:16-alpine"))
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @BeforeAll
    static void startAll() {
        POSTGRES.start();
    }

    @AfterAll
    static void stopAll() {
        POSTGRES.stop();
    }

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
    }
}
```

Alternatively, register the above properties from a test class companion-like static section.

## Slice tests with Testcontainers

When using slice tests such as @DataJpaTest, avoid replacing the datasource with an in-memory database if you intend to use Testcontainers. Use:

```java
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.context.annotation.Import;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestContainerConfig.class) // or rely on @ServiceConnection
public class MyRepositoryIntegrationTest {
    // repository tests
}
```

## API Reference

### Test Annotations

**Spring Boot Test Annotations:**
- `@SpringBootTest`: Load full application context (use sparingly)
- `@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)`: Full test with random HTTP port
- `@SpringBootTest(webEnvironment = WebEnvironment.MOCK)`: Full test with mock web environment
- `@DataJpaTest`: Load only JPA components (repositories, entities)
- `@WebMvcTest`: Load only MVC layer (controllers, @ControllerAdvice)
- `@WebFluxTest`: Load only WebFlux layer (reactive controllers)
- `@JsonTest`: Load only JSON serialization components
- `@RestClientTest`: Load only REST client components
- `@AutoConfigureMockMvc`: Provide MockMvc bean in @SpringBootTest
- `@AutoConfigureWebTestClient`: Provide WebTestClient bean for WebFlux tests
- `@AutoConfigureTestDatabase`: Control test database configuration

**Testcontainer Annotations:**
- `@ServiceConnection`: Wire Testcontainer to Spring Boot test (Spring Boot 3.5+)
- `@DynamicPropertySource`: Register dynamic properties at runtime
- `@Container`: Mark field as Testcontainer (requires @Testcontainers)
- `@Testcontainers`: Enable Testcontainers lifecycle management

**Test Lifecycle Annotations:**
- `@BeforeEach`: Run before each test method
- `@AfterEach`: Run after each test method
- `@BeforeAll`: Run once before all tests in class (must be static)
- `@AfterAll`: Run once after all tests in class (must be static)
- `@DisplayName`: Custom test name for reports
- `@Disabled`: Skip test
- `@Tag`: Tag tests for selective execution

**Test Isolation Annotations:**
- `@DirtiesContext`: Clear Spring context after test (forces rebuild)
- `@DirtiesContext(classMode = ClassMode.AFTER_CLASS)`: Clear after entire class

### Common Test Utilities

**MockMvc Methods:**
- `mockMvc.perform(get("/path"))`: Perform GET request
- `mockMvc.perform(post("/path")).contentType(MediaType.APPLICATION_JSON)`: POST with content type
- `.andExpect(status().isOk())`: Assert HTTP status
- `.andExpect(content().contentType("application/json"))`: Assert content type
- `.andExpect(jsonPath("$.field").value("expected"))`: Assert JSON path value

**TestRestTemplate Methods:**
- `restTemplate.getForEntity("/path", String.class)`: GET request
- `restTemplate.postForEntity("/path", body, String.class)`: POST request
- `response.getStatusCode()`: Get HTTP status
- `response.getBody()`: Get response body

**WebTestClient Methods (Reactive):**
- `webTestClient.get().uri("/path").exchange()`: Perform GET request
- `.expectStatus().isOk()`: Assert status
- `.expectBody().jsonPath("$.field").isEqualTo(value)`: Assert JSON

## Performance & stability tips

- Reuse Spring contexts: aim to keep tests grouped by the same profile/config to benefit from Spring's context caching.
- Reuse containers: start containers once per JVM where feasible. Use shared singletons for integration tests that do not require strict isolation.
- Prefer @ServiceConnection on Boot 3.5+ for simpler lifecycle and property mapping.
- Use @DirtiesContext only when absolutely necessary (it forces context rebuilds and slows the suite).
- Keep tests deterministic: initialize the database state explicitly in each test (fixtures or SQL scripts) and avoid relying on previous test order.

## Workflow Patterns

### Complete Database Integration Test Pattern

**Scenario**: Test a JPA repository with a real PostgreSQL database using Testcontainers.

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestContainerConfig.class)
public class UserRepositoryIntegrationTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldSaveAndRetrieveUserFromDatabase() {
        // Arrange
        User user = new User();
        user.setEmail("test@example.com");
        user.setName("Test User");

        // Act
        User saved = userRepository.save(user);
        userRepository.flush();

        Optional<User> retrieved = userRepository.findByEmail("test@example.com");

        // Assert
        assertThat(retrieved).isPresent();
        assertThat(retrieved.get().getName()).isEqualTo("Test User");
    }

    @Test
    void shouldThrowExceptionForDuplicateEmail() {
        // Arrange
        User user1 = new User();
        user1.setEmail("duplicate@example.com");
        user1.setName("User 1");

        User user2 = new User();
        user2.setEmail("duplicate@example.com");
        user2.setName("User 2");

        userRepository.save(user1);

        // Act & Assert
        assertThatThrownBy(() -> {
            userRepository.save(user2);
            userRepository.flush();
        }).isInstanceOf(DataIntegrityViolationException.class);
    }
}
```

### Complete REST API Integration Test Pattern

**Scenario**: Test REST controllers with full Spring context using MockMvc.

```java
@SpringBootTest
@AutoConfigureMockMvc
@Transactional
public class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void shouldCreateUserAndReturn201() throws Exception {
        User user = new User();
        user.setEmail("newuser@example.com");
        user.setName("New User");

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(user)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists())
            .andExpect(jsonPath("$.email").value("newuser@example.com"))
            .andExpect(jsonPath("$.name").value("New User"));
    }

    @Test
    void shouldReturnUserById() throws Exception {
        // Arrange
        User user = new User();
        user.setEmail("existing@example.com");
        user.setName("Existing User");
        User saved = userRepository.save(user);

        // Act & Assert
        mockMvc.perform(get("/api/users/" + saved.getId())
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email").value("existing@example.com"))
            .andExpect(jsonPath("$.name").value("Existing User"));
    }

    @Test
    void shouldReturnNotFoundForMissingUser() throws Exception {
        mockMvc.perform(get("/api/users/99999")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isNotFound());
    }

    @Test
    void shouldUpdateUserAndReturn200() throws Exception {
        // Arrange
        User user = new User();
        user.setEmail("update@example.com");
        user.setName("Original Name");
        User saved = userRepository.save(user);

        User updateData = new User();
        updateData.setName("Updated Name");

        // Act & Assert
        mockMvc.perform(put("/api/users/" + saved.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(updateData)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Updated Name"));
    }

    @Test
    void shouldDeleteUserAndReturn204() throws Exception {
        // Arrange
        User user = new User();
        user.setEmail("delete@example.com");
        user.setName("To Delete");
        User saved = userRepository.save(user);

        // Act & Assert
        mockMvc.perform(delete("/api/users/" + saved.getId()))
            .andExpect(status().isNoContent());

        assertThat(userRepository.findById(saved.getId())).isEmpty();
    }
}
```

### Service Layer Integration Test Pattern

**Scenario**: Test business logic with mocked repository.

```java
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void shouldFindUserByIdWhenExists() {
        // Arrange
        Long userId = 1L;
        User user = new User();
        user.setId(userId);
        user.setEmail("test@example.com");

        when(userRepository.findById(userId)).thenReturn(Optional.of(user));

        // Act
        Optional<User> result = userService.findById(userId);

        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getEmail()).isEqualTo("test@example.com");
        verify(userRepository, times(1)).findById(userId);
    }

    @Test
    void shouldReturnEmptyWhenUserNotFound() {
        // Arrange
        Long userId = 999L;
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        // Act
        Optional<User> result = userService.findById(userId);

        // Assert
        assertThat(result).isEmpty();
        verify(userRepository, times(1)).findById(userId);
    }

    @Test
    void shouldThrowExceptionWhenSavingInvalidUser() {
        // Arrange
        User invalidUser = new User();
        invalidUser.setEmail("invalid-email");

        when(userRepository.save(invalidUser))
            .thenThrow(new DataIntegrityViolationException("Invalid email"));

        // Act & Assert
        assertThatThrownBy(() -> userService.save(invalidUser))
            .isInstanceOf(DataIntegrityViolationException.class);
    }
}
```

### Reactive WebFlux Integration Test Pattern

**Scenario**: Test WebFlux controllers with WebTestClient.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
public class ReactiveUserControllerIntegrationTest {

    @Autowired
    private WebTestClient webTestClient;

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void shouldReturnUserAsJsonReactive() {
        // Arrange
        User user = new User();
        user.setEmail("reactive@example.com");
        user.setName("Reactive User");
        User saved = userRepository.save(user);

        // Act & Assert
        webTestClient.get()
            .uri("/api/users/" + saved.getId())
            .exchange()
            .expectStatus().isOk()
            .expectBody()
            .jsonPath("$.email").isEqualTo("reactive@example.com")
            .jsonPath("$.name").isEqualTo("Reactive User");
    }

    @Test
    void shouldReturnArrayOfUsers() {
        // Arrange
        User user1 = new User();
        user1.setEmail("user1@example.com");
        user1.setName("User 1");

        User user2 = new User();
        user2.setEmail("user2@example.com");
        user2.setName("User 2");

        userRepository.saveAll(List.of(user1, user2));

        // Act & Assert
        webTestClient.get()
            .uri("/api/users")
            .exchange()
            .expectStatus().isOk()
            .expectBodyList(User.class)
            .hasSize(2);
    }
}
```

## Best Practices

### 1. Choose the Right Test Type

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

**Performance guideline**: Unit tests should complete in <50ms, integration tests <500ms.

### 2. Use @ServiceConnection for Container Management (Spring Boot 3.5+)

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

### 3. Keep Tests Deterministic

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

### 4. Use Transactional Tests Carefully

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

### 5. Organize Tests by Layer

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

### 6. Use Meaningful Assertions

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

### 7. Mock External Dependencies

Mock external services but use real databases for integration tests:

```java
// Good - Mock external services, use real DB
@SpringBootTest
@Import(TestContainerConfig.class)
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

### 8. Use Test Fixtures for Common Data

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

### 9. Document Complex Test Scenarios

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

### 10. Avoid Common Pitfalls

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
@Import(TestContainerConfig.class)
public class ProperTest { }
```

## CI considerations

- Docker must be available in CI to run Testcontainers. Use a runner with Docker support (or a VM-based runner) and increase timeouts where necessary.
- Consider using lighter database images (alpine variants) but validate compatibility.
- Cache the Gradle/Maven build and avoid rebuilding containers in each job when possible.

## Test execution

Maven

```bash
./mvnw -DskipTests=false test
```

Gradle

```bash
./gradlew test
```

## Summary

This skill covers comprehensive integration testing patterns for Spring Boot applications using Java, enabling you to write reliable, performant tests across the entire application stack.

**Key Concepts Covered:**

1. **Test Architecture**: Understanding test slices (@DataJpaTest, @WebMvcTest, @WebFluxTest), Spring context caching, and when to use full @SpringBootTest
2. **Core Annotations**: Spring Boot test annotations, Testcontainers configuration, lifecycle management
3. **API Reference**: Complete reference of test annotations, MockMvc utilities, TestRestTemplate methods, and WebTestClient APIs
4. **Workflow Patterns**: Complete integration test examples for repositories, REST APIs, services, and reactive applications
5. **Best Practices**: Choosing test types, using @ServiceConnection, keeping tests deterministic, proper mocking, and avoiding common pitfalls

**Technology Stack:**
- Spring Boot 3.5+ with @ServiceConnection support
- Testcontainers 1.19.0+ for container management
- JUnit 5 Jupiter for test execution
- Mockito for mocking dependencies
- AssertJ for fluent assertions

**Test Execution:**
```bash
# Maven
./mvnw -DskipTests=false test

# Gradle
./gradlew test
```

**Performance Goals:**
- Unit tests: < 50ms each
- Integration tests: < 500ms each
- Maximize context caching by grouping tests with same configuration
- Reuse Testcontainers at JVM level

**Key Principles:**
1. Use test slices for focused, fast tests
2. Prefer @ServiceConnection on Spring Boot 3.5+
3. Keep tests deterministic with explicit setup
4. Mock external dependencies, use real databases
5. Avoid @DirtiesContext unless absolutely necessary
6. Organize tests by layer to optimize context reuse

This skill enables you to build a comprehensive test suite that validates Spring Boot applications reliably while maintaining fast feedback loops for development.

## Appendix: Common pitfalls

- Do not mix many different active profiles in the same test suite; this leads to many cached contexts and high memory usage.
- If a test requires a non-default port or property set, prefer to create a narrow test class that documents why a different context is required.
- Remember to keep Testcontainers versions compatible with your JDK and platform.
- Avoid starting Testcontainers manually; let Spring Boot manage their lifecycle with @ServiceConnection or @Testcontainers.
- Do not rely on test execution order; initialize test data in @BeforeEach or setUp methods.
- Never mock repository/database layers in integration tests; use real containers for accurate testing.