---
name: spring-boot-test-patterns
description: Provides comprehensive testing patterns for Spring Boot applications covering unit, integration, slice, and container-based testing with JUnit 5, Mockito, Testcontainers, and performance optimization. Use when writing tests, @Test methods, @MockBean mocks, or implementing test suites for Spring Boot applications.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring Boot Testing Patterns

## Overview

Comprehensive guidance for writing robust test suites for Spring Boot applications using JUnit 5, Mockito, Testcontainers, and performance-optimized slice testing patterns.

## When to Use

- Writing unit tests for services or repositories with mocked dependencies
- Implementing integration tests with real databases via Testcontainers
- Testing REST APIs with `@WebMvcTest` or MockMvc
- Configuring `@ServiceConnection` for container management in Spring Boot 3.5+

## Quick Reference

| Test Type | Annotation | Target Time | Use Case |
|-----------|------------|-------------|----------|
| **Unit Tests** | `@ExtendWith(MockitoExtension.class)` | < 50ms | Business logic without Spring context |
| **Repository Tests** | `@DataJpaTest` | < 100ms | Database operations with minimal context |
| **Controller Tests** | `@WebMvcTest` / `@WebFluxTest` | < 100ms | REST API layer testing |
| **Integration Tests** | `@SpringBootTest` | < 500ms | Full application context with containers |
| **Testcontainers** | `@ServiceConnection` / `@Testcontainers` | Varies | Real database/message broker containers |

## Core Concepts

### Test Architecture Philosophy

1. **Unit Tests** — Fast, isolated tests without Spring context (< 50ms)
2. **Slice Tests** — Minimal Spring context for specific layers (< 100ms)
3. **Integration Tests** — Full Spring context with real dependencies (< 500ms)

### Key Annotations

**Spring Boot Test:**
- `@SpringBootTest` — Full application context (use sparingly)
- `@DataJpaTest` — JPA components only (repositories, entities)
- `@WebMvcTest` — MVC layer only (controllers, `@ControllerAdvice`)
- `@WebFluxTest` — WebFlux layer only (reactive controllers)
- `@JsonTest` — JSON serialization components only

**Testcontainers:**
- `@ServiceConnection` — Wire Testcontainer to Spring Boot (3.5+)
- `@DynamicPropertySource` — Register dynamic properties at runtime
- `@Testcontainers` — Enable Testcontainers lifecycle management

## Instructions

### 1. Unit Testing Pattern

Test business logic with mocked dependencies:

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void shouldFindUserByIdWhenExists() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        Optional<User> result = userService.findById(1L);
        assertThat(result).isPresent();
        verify(userRepository).findById(1L);
    }
}
```

See [unit-testing.md](references/unit-testing.md) for advanced patterns.

### 2. Slice Testing Pattern

Use focused test slices for specific layers:

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestContainerConfig
class UserRepositoryIntegrationTest {
    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldSaveAndRetrieveUser() {
        User saved = userRepository.save(user);
        assertThat(userRepository.findByEmail("test@example.com")).isPresent();
    }
}
```

See [slice-testing.md](references/slice-testing.md) for all slice patterns.

### 3. REST API Testing Pattern

Test controllers with MockMvc:

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void shouldGetUserById() throws Exception {
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email").value("test@example.com"));
    }
}
```

### 4. Testcontainers with `@ServiceConnection`

Configure containers with Spring Boot 3.5+:

```java
@TestConfiguration
public class TestContainerConfig {
    @Bean
    @ServiceConnection
    public PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>("postgres:16-alpine");
    }
}
```

Apply with `@Import(TestContainerConfig.class)` on test classes.
See [testcontainers-setup.md](references/testcontainers-setup.md) for detailed configuration.

### 5. Add Dependencies

Include required testing dependencies:

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
```

See [test-dependencies.md](references/test-dependencies.md) for complete dependency list.

### 6. Configure CI/CD

Set up GitHub Actions for automated testing:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:20-dind
    steps:
    - uses: actions/checkout@v4
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
    - name: Run tests
      run: ./mvnw test
```

See [ci-cd-configuration.md](references/ci-cd-configuration.md) for full CI/CD patterns.

### Validation Checkpoints

After implementing tests, verify:
- Container running: `docker ps` (look for testcontainer images)
- Context loaded: check startup logs for "Started Application in X.XX seconds"
- Test isolation: run tests individually and confirm no cross-contamination

## Examples

### Full Integration Test with `@ServiceConnection`

```java
@SpringBootTest
@Import(TestContainerConfig.class)
class OrderServiceIntegrationTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldCreateOrderForExistingUser() {
        User user = userRepository.save(User.builder()
            .email("order-test@example.com")
            .build());

        Order order = orderService.createOrder(user.getId(), List.of(
            new OrderItem("SKU-001", 2)
        ));

        assertThat(order.getId()).isNotNull();
        assertThat(order.getStatus()).isEqualTo(OrderStatus.PENDING);
    }
}
```

### `@DataJpaTest` with Real Database

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestContainerConfig
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldFindByEmail() {
        userRepository.save(User.builder()
            .email("jpa-test@example.com")
            .build());
        assertThat(userRepository.findByEmail("jpa-test@example.com"))
            .isPresent();
    }
}
```

See [workflow-patterns.md](references/workflow-patterns.md) for complete end-to-end examples.

## Best Practices

- **Use the right test type**: `@DataJpaTest` for repositories, `@WebMvcTest` for controllers, `@SpringBootTest` only for full integration
- **Prefer `@ServiceConnection`** on Spring Boot 3.5+ for cleaner container management over `@DynamicPropertySource`
- **Keep tests deterministic**: Initialize all test data explicitly in `@BeforeEach`
- **Organize by layer**: Group tests by layer to maximize context caching
- **Reuse Testcontainers** at JVM level (`withReuse(true)` + `TESTCONTAINERS_REUSE_ENABLE=true`)
- **Avoid `@DirtiesContext`**: Forces context rebuild, significantly hurts performance
- **Mock external services**, use real databases only when necessary
- **Performance targets**: Unit < 50ms, Slice < 100ms, Integration < 500ms

## Constraints and Warnings

- Never use `@DirtiesContext` unless absolutely necessary (forces context rebuild)
- Avoid mixing `@MockBean` with different configurations (creates separate contexts)
- Testcontainers require Docker; ensure CI/CD pipelines have Docker support
- Do not rely on test execution order; each test must be independent
- Be cautious with `@TestPropertySource` (creates separate contexts)
- Do not use `@SpringBootTest` for unit tests; use plain Mockito instead
- Context caching can be invalidated by different `@MockBean` configurations
- Avoid static mutable state in tests (causes flaky tests)

## References

- **[test-dependencies.md](references/test-dependencies.md)** — Maven/Gradle test dependencies
- **[unit-testing.md](references/unit-testing.md)** — Unit testing with Mockito patterns
- **[slice-testing.md](references/slice-testing.md)** — Repository, controller, and JSON slice tests
- **[testcontainers-setup.md](references/testcontainers-setup.md)** — Testcontainers configuration patterns
- **[ci-cd-configuration.md](references/ci-cd-configuration.md)** — GitHub Actions, GitLab CI, Docker Compose
- **[api-reference.md](references/api-reference.md)** — Complete test annotations and utilities
- **[best-practices.md](references/best-practices.md)** — Testing patterns and optimization
- **[workflow-patterns.md](references/workflow-patterns.md)** — Complete integration test examples
