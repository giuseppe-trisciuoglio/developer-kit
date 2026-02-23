---
name: spring-boot-test-patterns
description: Provides comprehensive testing patterns for Spring Boot applications including unit, integration, slice, and container-based testing with JUnit 5, Mockito, Testcontainers, and performance optimization. Use when implementing robust test suites for Spring Boot applications.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring Boot Testing Patterns

## Overview

Comprehensive guidance for writing robust test suites for Spring Boot applications covering unit testing with Mockito, integration testing with Testcontainers, and performance-optimized slice testing patterns.

## When to Use

- Writing unit tests for services, repositories, or utilities
- Implementing integration tests with real databases using Testcontainers
- Setting up performance-optimized test slices (@DataJpaTest, @WebMvcTest)
- Configuring Spring Boot 3.1+ @ServiceConnection for container management
- Testing REST APIs with MockMvc, TestRestTemplate, or WebTestClient
- Optimizing test performance through context caching and container reuse

## Instructions

### Unit Testing Pattern

```java
class UserServiceTest {
    @Mock private UserRepository userRepository;
    @InjectMocks private UserService userService;

    @BeforeEach
    void setUp() { MockitoAnnotations.openMocks(this); }

    @Test
    void shouldFindUserByIdWhenExists() {
        User user = new User();
        user.setId(1L);
        user.setEmail("test@example.com");
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        Optional<User> result = userService.findById(1L);
        assertThat(result).isPresent();
        verify(userRepository, times(1)).findById(1L);
    }
}
```

### Slice Testing Pattern

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class UserRepositoryIntegrationTest {
    @Autowired private UserRepository userRepository;

    @Test
    void shouldSaveAndRetrieveUser() {
        User saved = userRepository.save(new User("test@example.com", "Test"));
        Optional<User> retrieved = userRepository.findByEmail("test@example.com");
        assertThat(retrieved).isPresent();
    }
}
```

### REST API Testing

```java
@SpringBootTest
@AutoConfigureMockMvc
public class UserControllerIntegrationTest {
    @Autowired private MockMvc mockMvc;
    @Autowired private ObjectMapper objectMapper;

    @Test
    void shouldCreateUserAndReturn201() throws Exception {
        User user = new User();
        user.setEmail("newuser@example.com");
        user.setName("New User");
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(user)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.email").value("newuser@example.com"));
    }
}
```

### Testcontainers with @ServiceConnection

```java
@SpringBootTest
@Testcontainers
class MyIntegrationTests {
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> container = new PostgreSQLContainer<>("postgres:16");
}
```

## Examples

### Unit Test with Mockito

```java
// Input: Test service method that finds user by ID
@Test
void shouldFindUserByIdWhenExists() {
    User expected = new User(1L, "test@example.com");
    when(userRepository.findById(1L)).thenReturn(Optional.of(expected));

    Optional<User> result = userService.findById(1L);

    // Output: User is found and matches expected
    assertThat(result).isPresent().contains(expected);
    verify(userRepository).findById(1L);
}
```

For complete production-ready examples, see [API Reference](./references/api-reference.md).

## Best Practices

1. **Choose the right test type**: @DataJpaTest for repos, @WebMvcTest for controllers, @SpringBootTest only for full integration
2. **Use @ServiceConnection** (Spring Boot 3.1+) over manual @DynamicPropertySource
3. **Keep tests deterministic** with explicit @BeforeEach setup
4. **Use AssertJ** for readable assertions
5. **Organize by layer** for optimal context caching
6. **Avoid @DirtiesContext** unless absolutely necessary
7. **Mock external dependencies**, use real databases

## Performance Targets

- Unit tests: < 50ms per test
- Slice tests: < 100ms per test
- Integration tests: < 500ms per test

## Constraints and Warnings

- Never use `@DirtiesContext` unless absolutely necessary (forces context rebuild)
- Avoid mixing `@MockBean` / `@MockitoBean` configurations (creates separate contexts)
- Testcontainers require Docker; ensure CI/CD pipelines have Docker support
- Do not rely on test execution order
- Do not use `@SpringBootTest` for unit tests; use plain Mockito

## References

- [API Reference](./references/api-reference.md)
- [Best Practices](./references/best-practices.md)
- [Workflow Patterns](./references/workflow-patterns.md)

## Related Skills

- `spring-boot-dependency-injection` - Unit testing with constructor injection
- `unit-test-service-layer` - Advanced service layer testing
