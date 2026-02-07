# Spring Boot Test API Reference

## Test Annotations

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

## Common Test Utilities

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

## Test Slices Performance Guidelines

- **Unit tests**: Complete in <50ms each
- **Integration tests**: Complete in <500ms each
- **Maximize context caching** by grouping tests with same configuration
- **Reuse Testcontainers** at JVM level where possible

## Common Test Annotations Reference

| Annotation | Purpose | When to Use |
|------------|---------|-------------|
| `@SpringBootTest` | Full application context | Full integration tests only |
| `@DataJpaTest` | JPA components only | Repository and entity tests |
| `@WebMvcTest` | MVC layer only | Controller tests |
| `@WebFluxTest` | WebFlux layer only | Reactive controller tests |
| `@ServiceConnection` | Container integration | Spring Boot 3.5+ with Testcontainers |
| `@DynamicPropertySource` | Dynamic properties | Pre-3.5 or custom configuration |
| `@DirtiesContext` | Context cleanup | When absolutely necessary |