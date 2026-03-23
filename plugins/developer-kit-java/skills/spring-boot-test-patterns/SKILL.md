---
name: spring-boot-test-patterns
description: Provides comprehensive testing patterns for Spring Boot applications including unit, integration, slice, and container-based testing with JUnit 5, Mockito, Testcontainers, and performance optimization. Use when implementing robust test suites for Spring Boot applications.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring Boot Testing Patterns

## Overview

Comprehensive guidance for writing robust test suites for Spring Boot applications using JUnit 5, Mockito, Testcontainers, and performance-optimized slice testing patterns.

## When to Use

- Writing unit tests for services, repositories, or utilities
- Implementing integration tests with real databases using Testcontainers
- Setting up performance-optimized test slices (`@DataJpaTest`, `@WebMvcTest`)
- Configuring Spring Boot 3.5+ `@ServiceConnection` for container management
- Testing REST APIs with MockMvc, TestRestTemplate, or WebTestClient
- Optimizing test performance through context caching and container reuse
- Setting up CI/CD pipelines for integration tests
- Implementing comprehensive test strategies for monolithic or microservices applications

## Quick Reference

| Test Type | Annotation | Target Time | Use Case |
|-----------|------------|-------------|----------|
| **Unit Tests** | `@ExtendWith(MockitoExtension.class)` | < 50ms | Business logic without Spring context |
| **Repository Tests** | `@DataJpaTest` | < 100ms | Database operations with minimal context |
| **Controller Tests** | `@WebMvcTest` / `@WebFluxTest` | < 100ms | REST API layer testing |
| **JSON Tests** | `@JsonTest` | < 50ms | Serialization/deserialization |
| **Integration Tests** | `@SpringBootTest` | < 500ms | Full application context with containers |
| **Testcontainers** | `@ServiceConnection` / `@Testcontainers` | Varies | Real database/message broker containers |

## Core Concepts

### Test Architecture Philosophy

Spring Boot testing follows a layered approach:

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

See [unit-testing.md](references/unit-testing.md) for patterns.

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

See [slice-testing.md](references/slice-testing.md) for slice patterns.

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

### 4. Testcontainers with @ServiceConnection

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

See [testcontainers-setup.md](references/testcontainers-setup.md) for configuration.

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

See [test-dependencies.md](references/test-dependencies.md) for complete setup.

### 6. Configure CI/CD

Set up GitHub Actions for automated testing:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up JDK 17
      uses: actions/setup-java@v3
    - name: Run tests
      run: ./mvnw test
```

See [ci-cd-configuration.md](references/ci-cd-configuration.md) for CI/CD patterns.

## Best Practices

- **Choose the right test type**: `@DataJpaTest` for repositories, `@WebMvcTest` for controllers, `@SpringBootTest` only for full integration
- **Use `@ServiceConnection`** on Spring Boot 3.5+ for cleaner container management
- **Keep tests deterministic**: Always initialize test data explicitly in `@BeforeEach`
- **Use meaningful assertions**: Leverage AssertJ for readable, fluent assertions
- **Organize tests by layer**: Group related tests to optimize context caching
- **Maximize context caching**: Group tests with similar configurations
- **Reuse Testcontainers**: At JVM level for better performance
- **Avoid `@DirtiesContext`**: Forces context rebuild, hurts performance
- **Mock external dependencies**: Use real databases, mock external services
- **Test performance targets**: Unit < 50ms, Slice < 100ms, Integration < 500ms

## Performance Optimization

### Context Caching

Group tests with similar configurations to maximize context reuse:

```java
@DataJpaTest
@TestContainerConfig
class UserRepositoryTest { } // Reuses same context

@DataJpaTest
@TestContainerConfig
class OrderRepositoryTest { } // Reuses same context
```

### Container Reuse

Reuse Testcontainers at JVM level:

```java
static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>()
    .withReuse(true);

@BeforeAll
static void startAll() {
    POSTGRES.start();
}
```

Enable with: `TESTCONTAINERS_REUSE_ENABLE=true`

## Performance Targets

| Test Type | Target Time | Strategy |
|-----------|-------------|----------|
| Unit tests | < 50ms | No Spring context, pure Mockito |
| Slice tests | < 100ms | Minimal context, specific layer only |
| Integration tests | < 500ms | Full context, container reuse |

## Key Principles

1. Use test slices for focused, fast tests
2. Prefer `@ServiceConnection` on Spring Boot 3.5+
3. Keep tests deterministic with explicit setup
4. Mock external dependencies, use real databases
5. Avoid `@DirtiesContext` unless absolutely necessary
6. Organize tests by layer to optimize context reuse

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

## Related Skills

- `spring-boot-dependency-injection` — Unit testing with constructor injection
- `spring-boot-rest-api-standards` — REST API patterns to test
- `spring-boot-crud-patterns` — CRUD patterns to test
- `unit-test-service-layer` — Advanced service layer testing techniques
