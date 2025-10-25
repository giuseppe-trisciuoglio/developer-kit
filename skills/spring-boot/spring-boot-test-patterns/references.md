# Spring Boot Test Patterns - References

Complete reference for testing Spring Boot applications with best practices.

## Test Annotations Reference

### Full Application Testing

```java
@SpringBootTest                          // Load full application context
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)  // Random HTTP port
@SpringBootTest(webEnvironment = WebEnvironment.MOCK)         // Mock web environment
@AutoConfigureMockMvc                    // Provide MockMvc bean
@AutoConfigureTestDatabase               // Configure test database
@Testcontainers                          // Enable Testcontainers
@DynamicPropertySource                   // Register dynamic properties
@ActiveProfiles("test")                  // Activate test profile
@Transactional                           // Rollback after test
```

### Test Slices

```java
@DataJpaTest                             // Test data layer only
@WebMvcTest(ControllerClass.class)      // Test MVC layer only
@WebFluxTest(ControllerClass.class)     // Test WebFlux layer
@JsonTest                                // Test JSON serialization
@RestClientTest(ClientClass.class)      // Test REST client
@JsonTest                                // Test JSON mapping
```

### Testcontainer Annotations

```java
@Container                               // Mark field as container (requires @Testcontainers)
@ServiceConnection                       // Wire container to Spring Boot (3.5+)
@DynamicPropertySource                   // Register properties at runtime
@Testcontainers                          // Enable container lifecycle management
```

### Test Lifecycle

```java
@BeforeEach                              // Before each test
@AfterEach                               // After each test
@BeforeAll                               // Before all tests (static)
@AfterAll                                // After all tests (static)
@Disabled                                // Skip test
@DisplayName("description")              // Custom test name
@Tag("category")                         // Tag for filtering
```

### Test Isolation

```java
@DirtiesContext                          // Clear context after test (expensive)
@DirtiesContext(classMode = AFTER_CLASS) // Clear after entire class
```

## Test Types and When to Use

| Test Type | Tool | Use When | Duration |
|-----------|------|----------|----------|
| Unit | JUnit, Mockito | Testing domain logic | < 50ms |
| Service | Mockito, @ExtendWith | Testing application logic | < 100ms |
| Slice | @WebMvcTest, @DataJpaTest | Testing single layer | < 500ms |
| Integration | @SpringBootTest, Testcontainers | Testing full flow | < 1000ms |
| E2E | TestRestTemplate | Testing complete scenario | variable |

## Testcontainers Reference

### PostgreSQL Container

```java
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
    .withDatabaseName("testdb")
    .withUsername("test")
    .withPassword("test");

@DynamicPropertySource
static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
}
```

### MySQL Container

```java
@Container
static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
    .withDatabaseName("testdb")
    .withUsername("test")
    .withPassword("test");
```

### Kafka Container

```java
@Container
static KafkaContainer kafka = new KafkaContainer(
    DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));

@DynamicPropertySource
static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
}
```

### Redis Container

```java
@Container
static GenericContainer<?> redis = new GenericContainer<>(DockerImageName.parse("redis:7-alpine"))
    .withExposedPorts(6379);

@DynamicPropertySource
static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.redis.host", redis::getHost);
    registry.add("spring.redis.port", redis::getFirstMappedPort);
}
```

## MockMvc Reference

### Common Methods

```java
// Perform requests
mockMvc.perform(get("/path"))
mockMvc.perform(post("/path"))
mockMvc.perform(put("/path"))
mockMvc.perform(delete("/path"))
mockMvc.perform(patch("/path"))

// Add headers
.header("Authorization", "Bearer token")
.contentType(MediaType.APPLICATION_JSON)

// Add content
.content("{\"field\": \"value\"}")

// Expect status
.andExpect(status().isOk())
.andExpect(status().isCreated())
.andExpect(status().isNotFound())

// Expect content
.andExpect(content().json("{\"id\":1}"))
.andExpect(jsonPath("$.name").value("Test"))
.andExpect(jsonPath("$[0].id").exists())

// Print results
.andDo(print())
.andDo(log().all())
```

## TestRestTemplate Reference

### Common Methods

```java
// GET request
ResponseEntity<T> response = restTemplate.getForEntity("/path", T.class);
T body = restTemplate.getForObject("/path", T.class);

// POST request
ResponseEntity<T> response = restTemplate.postForEntity("/path", body, T.class);
URI location = restTemplate.postForLocation("/path", body);
T response = restTemplate.postForObject("/path", body, T.class);

// PUT request
restTemplate.put("/path", body);
ResponseEntity<T> response = restTemplate.exchange("/path", HttpMethod.PUT, entity, T.class);

// DELETE request
restTemplate.delete("/path");

// PATCH request
ResponseEntity<T> response = restTemplate.exchange("/path", HttpMethod.PATCH, entity, T.class);

// Exchange (flexible)
ResponseEntity<T> response = restTemplate.exchange(
    "/path", 
    HttpMethod.GET, 
    new HttpEntity<>(headers), 
    T.class
);
```

## Assertions Reference

### AssertJ Common Assertions

```java
// Equality
assertThat(actual).isEqualTo(expected)
assertThat(actual).isNotEqualTo(expected)

// Null checks
assertThat(actual).isNull()
assertThat(actual).isNotNull()

// Collections
assertThat(list).hasSize(3)
assertThat(list).isEmpty()
assertThat(list).isNotEmpty()
assertThat(list).contains(item1, item2)
assertThat(list).containsExactly(item1, item2)

// Strings
assertThat(text).isBlank()
assertThat(text).isNotBlank()
assertThat(text).contains("substring")
assertThat(text).startsWith("prefix")

// Numbers
assertThat(num).isPositive()
assertThat(num).isNegative()
assertThat(num).isGreaterThan(10)
assertThat(num).isBetween(1, 100)

// Objects
assertThat(obj).hasFieldOrProperty("fieldName")
assertThat(obj).hasFieldOrPropertyWithValue("field", value)

// Exceptions
assertThatThrownBy(() -> method())
    .isInstanceOf(Exception.class)
    .hasMessage("message")

// Optional
assertThat(optional).isPresent()
assertThat(optional).isEmpty()
assertThat(optional).contains(value)
```

## Mocking Reference

### Mockito Methods

```java
// Create mocks
Mock<T> mock = mock(T.class);

// Setup return values
when(mock.method()).thenReturn(value);
when(mock.method(any())).thenReturn(value);
when(mock.method(eq("specific"))).thenReturn(value);

// Setup exceptions
when(mock.method()).thenThrow(new Exception("error"));

// Verification
verify(mock).method();
verify(mock, times(2)).method();
verify(mock, never()).method();
verify(mock, atLeast(1)).method();
verify(mock, atMost(3)).method();

// Capture arguments
ArgumentCaptor<T> captor = ArgumentCaptor.forClass(T.class);
verify(mock).method(captor.capture());
T capturedValue = captor.getValue();

// Reset mock
reset(mock);
```

## Spring Boot Test Properties

### application-test.properties

```properties
# Use in-memory H2 database
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect

# Disable specific features
spring.jpa.show-sql=false
spring.jpa.hibernate.ddl-auto=create-drop

# Logging
logging.level.com.example=DEBUG
logging.level.org.springframework.web=WARN

# Disable cache for tests
spring.cache.type=none

# Disable security
spring.security.enabled=false
```

## Test Data Fixtures

### Builder Pattern

```java
public class ProductTestFixture {
    public static Product validProduct() {
        return Product.builder()
            .id(1L)
            .name("Test Product")
            .price(BigDecimal.TEN)
            .stock(100)
            .build();
    }

    public static Product productWithName(String name) {
        return validProduct().toBuilder()
            .name(name)
            .build();
    }
}

// Usage
Product product = ProductTestFixture.validProduct();
Product customProduct = ProductTestFixture.productWithName("Custom");
```

## Performance Optimization Tips

### Context Reuse

```java
// Good: Same configuration reused
@SpringBootTest
@ActiveProfiles("test")
class Test1 { }

@SpringBootTest
@ActiveProfiles("test")
class Test2 { }

// Avoid: Different configurations create new contexts
@SpringBootTest(properties = "key=value1")
class Test1 { }

@SpringBootTest(properties = "key=value2")
class Test2 { }
```

### Container Reuse

```java
// Good: Shared container
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

// Reused across all test methods in class
// Testcontainer creates once, reuses for multiple tests
```

## Maven Dependencies

```xml
<!-- Spring Boot Test -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>

<!-- Testcontainers -->
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

## Gradle Dependencies

```gradle
dependencies {
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.testcontainers:junit-jupiter:1.19.0'
    testImplementation 'org.testcontainers:postgresql:1.19.0'
}
```

## Running Tests

```bash
# Maven - Run all tests
mvn test

# Maven - Run specific test class
mvn test -Dtest=ProductServiceTest

# Maven - Run specific test method
mvn test -Dtest=ProductServiceTest#shouldCreateProduct

# Gradle - Run all tests
./gradlew test

# Gradle - Run specific test class
./gradlew test --tests ProductServiceTest

# Gradle - Run tests with tag
./gradlew test --tests '*Integration*'
```

## Related Skills

- **spring-boot-crud-patterns/SKILL.md** - Code to test
- **spring-boot-rest-api-standards/SKILL.md** - REST API testing
- **spring-boot-dependency-injection/SKILL.md** - Testing with DI

## External Resources

### Official Documentation
- [Spring Boot Testing](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing)
- [Testcontainers Documentation](https://testcontainers.com/)
- [Mockito Documentation](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html)

### Best Practices
- [Testing Best Practices](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-Testing-Best-Practices)
- [Integration Testing Guide](https://www.baeldung.com/integration-testing-in-spring)

### Tools
- [AssertJ](https://assertj.github.io/assertj-core-features-highlight.html)
- [JUnit 5](https://junit.org/junit5/docs/current/user-guide/)
- [TestRestTemplate API](https://docs.spring.io/spring-boot/docs/current/api/org/springframework/boot/test/web/client/TestRestTemplate.html)
