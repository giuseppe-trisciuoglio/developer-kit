---
allowed-tools: Read, Write, Bash, Grep, Glob
argument-hint: "[class-path]"
description: Generate comprehensive integration tests for Spring Boot classes using Testcontainers (PostgreSQL, Redis, MongoDB) with `@ServiceConnection` pattern
model: inherit
---

# Write Integration Tests for Spring Boot

You are tasked with generating a complete integration test for the Java class specified in `$1`.

## Process

### 1. Analyze Target Class
- Read the class file from `$1`
- Identify the layer (Controller, Service, Repository)
- Detect dependencies (Database, Cache, Message Queue, etc.)
- Identify external integrations

### 2. Determine Required Testcontainers
Based on dependencies, include:
- **PostgreSQL**: For JPA repositories or database operations
- **Redis**: For caching or session management
- **MongoDB**: For NoSQL operations
- **RabbitMQ/Kafka**: For messaging operations
- **Additional containers**: Based on specific dependencies

### 3. Generate Integration Test

Follow these patterns from the spring-boot-test-patterns skill:

#### Test Structure
```java
@SpringBootTest
@Testcontainers
class <ClassName>IntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"))
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Container
    @ServiceConnection
    static GenericContainer<?> redis = new GenericContainer<>(
        DockerImageName.parse("redis:7-alpine"))
        .withExposedPorts(6379);

    @Autowired
    private <TargetClass> targetClass;

    @Test
    void shouldPerformIntegrationScenario() {
        // Test implementation
    }
}
```

#### Key Requirements
1. **Use `@ServiceConnection`** for Spring Boot 3.5+ automatic wiring
2. **Static containers** for reuse across test methods
3. **Minimal context loading** - only load what's needed
4. **Real dependencies** via Testcontainers
5. **Complete scenarios** - test full workflows
6. **Proper assertions** - use AssertJ for fluent assertions
7. **Use `@MockitoBean`** (not deprecated `@MockBean`) from `org.springframework.test.context.bean.override.mockito`

#### Container Selection Guidelines
- **`@Repository`/`@DataJpaTest`**: PostgreSQL/MySQL container
- **`@Service` with caching**: Redis container
- **`@RestController`**: MockMvc + required backend containers
- **Message consumers/producers**: RabbitMQ/Kafka container
- **MongoDB repositories**: MongoDB container

### 4. Dependencies Check
Verify and add required dependencies:

**Maven:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>1.19.0</version> // Use latest stable version
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <version>1.19.0</version> // Use latest stable version
    <scope>test</scope>
</dependency>
```

**Gradle:**
```kotlin
testImplementation("org.springframework.boot:spring-boot-starter-test")
testImplementation("org.testcontainers:junit-jupiter:1.19.0")
testImplementation("org.testcontainers:postgresql:1.19.0")
```

### 5. Test Coverage
Generate tests covering:
- ✅ Happy path scenarios
- ✅ Edge cases and boundary conditions
- ✅ Error handling and validation
- ✅ Transaction rollback scenarios
- ✅ Concurrent access patterns (if applicable)

### 6. Performance Optimization
- Use static containers for JVM-level reuse
- Avoid `@DirtiesContext` unless absolutely necessary
- Group tests with similar configuration
- Target: < 500ms per integration test

## Example Patterns

### Controller Integration Test
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class UserControllerIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"));

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void shouldCreateAndRetrieveUser() {
        UserRequest request = new UserRequest("john@example.com", "John Doe");
        
        ResponseEntity<UserResponse> createResponse = restTemplate
            .postForEntity("/api/users", request, UserResponse.class);
        
        assertThat(createResponse.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(createResponse.getBody()).isNotNull();
        
        Long userId = createResponse.getBody().id();
        
        ResponseEntity<UserResponse> getResponse = restTemplate
            .getForEntity("/api/users/" + userId, UserResponse.class);
        
        assertThat(getResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(getResponse.getBody().email()).isEqualTo("john@example.com");
    }
}
```

### Controller with Mocked Service
```java
import org.springframework.test.context.bean.override.mockito.MockitoBean;

@WebMvcTest(UserController.class)
@Testcontainers
class UserControllerMockTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean  // Use @MockitoBean instead of deprecated @MockBean
    private UserService userService;

    @Test
    void shouldReturnUserWhenExists() throws Exception {
        User user = new User(1L, "john@example.com", "John Doe");
        when(userService.findById(1L)).thenReturn(Optional.of(user));

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email").value("john@example.com"));
    }
}
```

### Service with Cache Integration Test
```java
@SpringBootTest
@Testcontainers
class UserServiceIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"));

    @Container
    @ServiceConnection
    static GenericContainer<?> redis = new GenericContainer<>(
        DockerImageName.parse("redis:7-alpine"))
        .withExposedPorts(6379);

    @Autowired
    private UserService userService;

    @Autowired
    private CacheManager cacheManager;

    @Test
    void shouldCacheUserAfterFirstRetrieval() {
        User user = userService.createUser("test@example.com", "Test User");
        
        // First call - hits database
        User firstCall = userService.findById(user.getId());
        assertThat(firstCall).isNotNull();
        
        // Verify cached
        Cache userCache = cacheManager.getCache("users");
        assertThat(userCache.get(user.getId())).isNotNull();
        
        // Second call - hits cache
        User secondCall = userService.findById(user.getId());
        assertThat(secondCall).isEqualTo(firstCall);
    }
}
```

### Repository Integration Test
```java
@DataJpaTest
@Testcontainers
class UserRepositoryIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"));

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldFindUsersByEmailDomain() {
        userRepository.save(new User("john@example.com", "John"));
        userRepository.save(new User("jane@example.com", "Jane"));
        userRepository.save(new User("bob@another.com", "Bob"));
        
        List<User> exampleUsers = userRepository.findByEmailEndingWith("@example.com");
        
        assertThat(exampleUsers).hasSize(2);
        assertThat(exampleUsers)
            .extracting(User::getEmail)
            .containsExactlyInAnyOrder("john@example.com", "jane@example.com");
    }
}
```

## Output

1. Create test file in `src/test/java` matching package structure
2. Name: `<ClassName>IntegrationTest.java`
3. Include all necessary imports
4. Add appropriate Testcontainers based on dependencies
5. Implement comprehensive test scenarios
6. Add comments explaining complex scenarios

## Verification

After generating the test:
1. Verify all imports are correct
2. Check Testcontainer versions match project dependencies
3. Ensure `@ServiceConnection` is used (Spring Boot 3.5+)
4. Validate test completeness against requirements
5. Run the test: `./mvnw test -Dtest=<ClassName>IntegrationTest`

## Best Practices

- ✅ Use static containers for performance
- ✅ Prefer `@ServiceConnection` over `@DynamicPropertySource`
- ✅ Use `@MockitoBean` instead of deprecated `@MockBean` (from `org.springframework.test.context.bean.override.mockito`)
- ✅ Test complete workflows, not isolated methods
- ✅ Use meaningful test method names describing scenarios
- ✅ Add `@Transactional` on test methods for automatic rollback
- ✅ Use AssertJ for fluent, readable assertions
- ❌ Avoid `@DirtiesContext` unless absolutely necessary
- ❌ Don't mix unit test patterns in integration tests
- ❌ Don't hardcode ports or URLs

## Available Skills Reference

This command leverages the following skills available in the repository:

### Testing Skills
- **spring-boot-test-patterns** - Core integration testing patterns with Testcontainers and @ServiceConnection
- **unit-test-controller-layer** - REST controller testing with MockMvc
- **unit-test-service-layer** - Service layer testing with Mockito
- **unit-test-caching** - Testing cache behaviors with Redis
- **unit-test-json-serialization** - Testing JSON serialization/deserialization
- **unit-test-exception-handler** - Testing `@ControllerAdvice` exception handlers
- **unit-test-wiremock-rest-api** - Testing external REST APIs with WireMock
- **unit-test-scheduled-async** - Testing `@Scheduled` and `@Async` methods
- **unit-test-security-authorization** - Testing Spring Security and authorization

### Spring Boot Skills
- **spring-boot-rest-api-standards** - REST API design patterns to test
- **spring-boot-crud-patterns** - CRUD operation patterns to test
- **spring-boot-cache** - Caching strategies with Spring Cache
- **spring-boot-dependency-injection** - Constructor injection patterns
- **spring-boot-event-driven-patterns** - Event-driven architecture testing
- **spring-data-jpa** - JPA repository patterns

### Usage
When analyzing the target class, Claude will automatically reference these skills to:
- Determine the appropriate test strategy based on layer (Controller/Service/Repository)
- Select the correct Testcontainers based on dependencies
- Apply framework-specific testing patterns
- Generate comprehensive test scenarios covering all edge cases
- Use `@MockitoBean` for mocking dependencies (replaces deprecated `@MockBean`)

### Important Notes
- **`@MockitoBean` vs `@MockBean`**: Spring Framework 6.2+ introduces `@MockitoBean` from `org.springframework.test.context.bean.override.mockito` package. The old `@MockBean` from `org.springframework.boot.test.mock.mockito` is deprecated.
- **Package import**: Always use `import org.springframework.test.context.bean.override.mockito.MockitoBean;`
- **Reference**: [Spring Framework MockitoBean Documentation](https://docs.spring.io/spring-framework/reference/6.2/testing/annotations/integration-spring/annotation-mockitobean.html)

---

**Target class:** `$ARGUMENTS`

Analyze the class and generate a comprehensive integration test following the patterns above.

## Execution Instructions

**Agent Selection**: To execute this task, use the following agent with fallback:
- Primary: `spring-boot-unit-testing-expert`
- If not available: Use `developer-kit:spring-boot-unit-testing-expert` or fallback to `general-purpose` agent with `spring-boot-test-patterns` skill
