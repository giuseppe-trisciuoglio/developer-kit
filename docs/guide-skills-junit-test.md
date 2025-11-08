# Complete Guide to JUnit Test Skills

This comprehensive guide documents all JUnit testing skills available in the Developer Kit, organized by testing type with detailed explanations, practical examples, and best practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Controller Layer Testing](#controller-layer-testing)
3. [Service Layer Testing](#service-layer-testing)
4. [Data & Validation Testing](#data--validation-testing)
5. [External Integration Testing](#external-integration-testing)
6. [Infrastructure Testing](#infrastructure-testing)
7. [Advanced Testing Patterns](#advanced-testing-patterns)
8. [Common Workflows](#common-workflows)
9. [Best Practices](#best-practices)

---

## Overview

The JUnit Test skills collection provides comprehensive patterns for testing Spring Boot applications at all layers, from unit tests to integration tests, with emphasis on fast, reliable, and maintainable test suites.

### Skill Categories

- **Controller Layer**: REST API testing with MockMvc
- **Service Layer**: Business logic testing with Mockito
- **Data**: Validation, serialization, mappers
- **External Integration**: WireMock for REST API testing
- **Infrastructure**: Caching, scheduled tasks, security
- **Advanced**: Parameterized tests, boundary conditions

### Technology Stack

- **JUnit**: 5 (Jupiter) for all test cases
- **Mockito**: 4.x/5.x for mocking
- **AssertJ**: Fluent assertions
- **MockMvc**: Spring MVC testing
- **WireMock**: External API mocking
- **Testcontainers**: Integration testing (where applicable)
- **Spring Boot Test**: 3.5.x testing support

### Testing Philosophy

- **Fast**: Unit tests < 50ms, avoid Spring context where possible
- **Isolated**: Test one component at a time
- **Reliable**: No flaky tests, deterministic results
- **Maintainable**: Clear test names, readable assertions
- **Coverage**: Focus on critical paths and edge cases

---

## Controller Layer Testing

### unit-test-controller-layer

**Purpose**: Test REST controllers using MockMvc for HTTP interaction testing without starting a full server.

**When to use:**
- Testing REST endpoint behavior
- Validating request/response payloads
- Testing HTTP status codes and headers
- Validating request validation
- Testing exception handling at controller level

**Key Patterns:**

1. **Basic Controller Test**
```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ProductService productService;

    @Test
    void shouldReturnProductWhenExists() throws Exception {
        // Given
        ProductResponse response = new ProductResponse(1L, "Laptop", new BigDecimal("999.99"));
        when(productService.getById(1L)).thenReturn(response);

        // When & Then
        mockMvc.perform(get("/api/v1/products/1")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.name").value("Laptop"))
            .andExpect(jsonPath("$.price").value(999.99));
    }

    @Test
    void shouldReturn404WhenProductNotFound() throws Exception {
        // Given
        when(productService.getById(999L))
            .thenThrow(new ProductNotFoundException(999L));

        // When & Then
        mockMvc.perform(get("/api/v1/products/999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.message").value("Product not found with id: 999"));
    }
}
```

2. **POST Request Testing**
```java
@Test
void shouldCreateProductWithValidRequest() throws Exception {
    // Given
    CreateProductRequest request = new CreateProductRequest(
        "New Laptop",
        new BigDecimal("1299.99"),
        "Electronics"
    );
    ProductResponse response = new ProductResponse(1L, "New Laptop", new BigDecimal("1299.99"));
    
    when(productService.create(any(CreateProductRequest.class))).thenReturn(response);

    // When & Then
    mockMvc.perform(post("/api/v1/products")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {
                    "name": "New Laptop",
                    "price": 1299.99,
                    "category": "Electronics"
                }
                """))
        .andExpect(status().isCreated())
        .andExpect(header().exists("Location"))
        .andExpect(jsonPath("$.id").value(1))
        .andExpect(jsonPath("$.name").value("New Laptop"));
}

@Test
void shouldRejectInvalidProductRequest() throws Exception {
    // When & Then
    mockMvc.perform(post("/api/v1/products")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {
                    "name": "",
                    "price": -10
                }
                """))
        .andExpect(status().isBadRequest())
        .andExpect(jsonPath("$.errors.name").exists())
        .andExpect(jsonPath("$.errors.price").exists());
}
```

3. **Authentication Testing**
```java
@Test
@WithMockUser(roles = "ADMIN")
void shouldAllowAdminToDeleteProduct() throws Exception {
    // When & Then
    mockMvc.perform(delete("/api/v1/products/1"))
        .andExpect(status().isNoContent());
    
    verify(productService).delete(1L);
}

@Test
@WithMockUser(roles = "USER")
void shouldForbidUserFromDeletingProduct() throws Exception {
    // When & Then
    mockMvc.perform(delete("/api/v1/products/1"))
        .andExpect(status().isForbidden());
}
```

**Best Practices:**
- Use `@WebMvcTest` to load only web layer
- Mock service dependencies with `@MockitoBean`
- Test all HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Validate both success and error scenarios
- Test request validation constraints
- Verify JSON structure with JsonPath
- Test security constraints

**References:**
- `skills/junit-test/unit-test-controller-layer/SKILL.md`

---

### unit-test-exception-handler

**Purpose**: Test global exception handlers and error response formatting.

**When to use:**
- Testing `@RestControllerAdvice` implementations
- Validating error response structure
- Testing custom exception mappings
- Verifying HTTP status codes for exceptions

**Key Patterns:**

1. **Exception Handler Test**
```java
@WebMvcTest(controllers = ProductController.class)
class GlobalExceptionHandlerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ProductService productService;

    @Test
    void shouldHandleValidationException() throws Exception {
        // When & Then
        mockMvc.perform(post("/api/v1/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.timestamp").exists())
            .andExpect(jsonPath("$.status").value(400))
            .andExpect(jsonPath("$.message").value("Validation failed"))
            .andExpect(jsonPath("$.errors").isMap());
    }

    @Test
    void shouldHandleEntityNotFoundException() throws Exception {
        // Given
        when(productService.getById(999L))
            .thenThrow(new EntityNotFoundException("Product", 999L));

        // When & Then
        mockMvc.perform(get("/api/v1/products/999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.status").value(404))
            .andExpect(jsonPath("$.message").value("Product not found with id: 999"));
    }
}
```

**Best Practices:**
- Test each exception type mapped in `@RestControllerAdvice`
- Verify error response structure consistency
- Ensure sensitive data is not exposed in error messages
- Test exception hierarchy (specific vs generic)

**References:**
- `skills/junit-test/unit-test-exception-handler/SKILL.md`

---

## Service Layer Testing

### unit-test-service-layer

**Purpose**: Test business logic in service classes using Mockito for dependency mocking, without Spring context.

**When to use:**
- Testing business rules and workflows
- Validating service orchestration
- Testing transaction boundaries
- Mocking repository and external dependencies

**Key Patterns:**

1. **Service Unit Test (No Spring Context)**
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks
    private UserService userService;

    @Test
    void shouldRegisterNewUser() {
        // Given
        CreateUserRequest request = new CreateUserRequest("john@example.com", "John Doe");
        User user = User.create(request.email(), request.name());
        
        when(userRepository.existsByEmail(request.email())).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(user);

        // When
        UserResponse response = userService.register(request);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.email()).isEqualTo("john@example.com");
        assertThat(response.name()).isEqualTo("John Doe");
        
        verify(userRepository).save(any(User.class));
        verify(emailService).sendWelcomeEmail("john@example.com", "John Doe");
    }

    @Test
    void shouldThrowExceptionWhenEmailAlreadyExists() {
        // Given
        CreateUserRequest request = new CreateUserRequest("existing@example.com", "Jane");
        when(userRepository.existsByEmail(request.email())).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> userService.register(request))
            .isInstanceOf(EmailAlreadyExistsException.class)
            .hasMessage("Email already registered: existing@example.com");
        
        verify(userRepository, never()).save(any());
        verify(emailService, never()).sendWelcomeEmail(any(), any());
    }
}
```

2. **ArgumentCaptor for Complex Verification**
```java
@Test
void shouldSaveUserWithCorrectData() {
    // Given
    ArgumentCaptor<User> userCaptor = ArgumentCaptor.forClass(User.class);
    CreateUserRequest request = new CreateUserRequest("test@example.com", "Test User");
    
    when(userRepository.save(any(User.class))).thenReturn(User.create("test@example.com", "Test User"));

    // When
    userService.register(request);

    // Then
    verify(userRepository).save(userCaptor.capture());
    User savedUser = userCaptor.getValue();
    
    assertThat(savedUser)
        .satisfies(user -> {
            assertThat(user.getEmail()).isEqualTo("test@example.com");
            assertThat(user.getName()).isEqualTo("Test User");
            assertThat(user.getStatus()).isEqualTo(UserStatus.ACTIVE);
        });
}
```

**Best Practices:**
- Avoid `@SpringBootTest` for unit tests (too slow)
- Use `@ExtendWith(MockitoExtension.class)` instead
- Mock all dependencies with `@Mock`
- Use `@InjectMocks` for the class under test
- Test business rules thoroughly
- Verify interactions with `verify()`
- Test exception scenarios
- Keep tests < 50ms execution time

**References:**
- `skills/junit-test/unit-test-service-layer/SKILL.md`

---

### unit-test-application-events

**Purpose**: Test Spring application event publishing and handling.

**When to use:**
- Testing event-driven architecture
- Validating event publishers
- Testing event listeners
- Verifying asynchronous event processing

**Key Patterns:**

1. **Event Publishing Test**
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceEventTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private ApplicationEventPublisher eventPublisher;

    @InjectMocks
    private OrderService orderService;

    @Test
    void shouldPublishOrderCreatedEventWhenOrderIsCreated() {
        // Given
        CreateOrderRequest request = new CreateOrderRequest(/* ... */);
        Order order = Order.create(request);
        
        when(orderRepository.save(any(Order.class))).thenReturn(order);

        // When
        orderService.createOrder(request);

        // Then
        ArgumentCaptor<OrderCreatedEvent> eventCaptor = 
            ArgumentCaptor.forClass(OrderCreatedEvent.class);
        verify(eventPublisher).publishEvent(eventCaptor.capture());
        
        OrderCreatedEvent event = eventCaptor.getValue();
        assertThat(event.orderId()).isEqualTo(order.getId());
        assertThat(event.totalAmount()).isEqualTo(order.getTotalAmount());
    }
}
```

2. **Event Listener Test**
```java
@SpringBootTest
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class OrderEventListenerIntegrationTest {

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    @MockitoBean
    private EmailService emailService;

    @Test
    void shouldSendEmailWhenOrderCreatedEventReceived() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            UUID.randomUUID(),
            "customer@example.com",
            new BigDecimal("299.99")
        );

        // When
        eventPublisher.publishEvent(event);

        // Then
        await().atMost(Duration.ofSeconds(2))
            .untilAsserted(() -> 
                verify(emailService).sendOrderConfirmation(
                    eq("customer@example.com"),
                    any(OrderCreatedEvent.class)
                )
            );
    }
}
```

**Best Practices:**
- Test event publishing separately from event handling
- Use `ArgumentCaptor` to verify event content
- Use Awaitility for async event testing
- Test `@TransactionalEventListener` phases
- Verify idempotency of event handlers

**References:**
- `skills/junit-test/unit-test-application-events/SKILL.md`

---

## Data & Validation Testing

### unit-test-bean-validation

**Purpose**: Test Jakarta Bean Validation constraints on DTOs and domain models.

**When to use:**
- Testing `@Valid` annotations
- Validating constraint annotations
- Testing custom validators
- Group validation testing

**Key Patterns:**

1. **DTO Validation Test**
```java
class CreateProductRequestTest {

    private Validator validator;

    @BeforeEach
    void setUp() {
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    void shouldPassValidationWithValidData() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Valid Product Name",
            new BigDecimal("99.99"),
            "Electronics"
        );

        // When
        Set<ConstraintViolation<CreateProductRequest>> violations = 
            validator.validate(request);

        // Then
        assertThat(violations).isEmpty();
    }

    @Test
    void shouldFailValidationWhenNameIsBlank() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "",
            new BigDecimal("99.99"),
            "Electronics"
        );

        // When
        Set<ConstraintViolation<CreateProductRequest>> violations = 
            validator.validate(request);

        // Then
        assertThat(violations)
            .hasSize(1)
            .extracting(ConstraintViolation::getMessage)
            .contains("Product name is required");
    }

    @Test
    void shouldFailValidationWhenPriceIsNegative() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Product",
            new BigDecimal("-10.00"),
            "Electronics"
        );

        // When
        Set<ConstraintViolation<CreateProductRequest>> violations = 
            validator.validate(request);

        // Then
        assertThat(violations)
            .extracting(ConstraintViolation::getMessage)
            .contains("Price must be greater than 0");
    }
}
```

2. **Custom Validator Test**
```java
@Test
void shouldValidateCustomConstraint() {
    // Given
    @ValidEmail
    class TestObject {
        private String email = "invalid-email";
    }
    
    // When
    Set<ConstraintViolation<TestObject>> violations = 
        validator.validate(new TestObject());

    // Then
    assertThat(violations).hasSize(1);
}
```

**Best Practices:**
- Create `Validator` instance in `@BeforeEach`
- Test each validation constraint separately
- Test edge cases (null, empty, boundary values)
- Verify error messages match expectations
- Test validation groups if used

**References:**
- `skills/junit-test/unit-test-bean-validation/SKILL.md`

---

### unit-test-json-serialization

**Purpose**: Test JSON serialization/deserialization with Jackson.

**When to use:**
- Testing custom JSON serializers/deserializers
- Validating JSON field naming strategies
- Testing date/time formatting
- Testing ignore/include strategies

**Key Patterns:**

1. **Serialization Test**
```java
@JsonTest
class ProductResponseSerializationTest {

    @Autowired
    private JacksonTester<ProductResponse> json;

    @Test
    void shouldSerializeProductResponse() throws Exception {
        // Given
        ProductResponse response = new ProductResponse(
            1L,
            "Laptop",
            new BigDecimal("999.99"),
            LocalDateTime.of(2024, 1, 15, 10, 30)
        );

        // When & Then
        assertThat(json.write(response))
            .extractingJsonPathNumberValue("$.id").isEqualTo(1)
            .extractingJsonPathStringValue("$.name").isEqualTo("Laptop")
            .extractingJsonPathNumberValue("$.price").isEqualTo(999.99)
            .extractingJsonPathStringValue("$.createdAt")
                .isEqualTo("2024-01-15T10:30:00");
    }

    @Test
    void shouldDeserializeProductResponse() throws Exception {
        // Given
        String jsonContent = """
            {
                "id": 1,
                "name": "Laptop",
                "price": 999.99,
                "createdAt": "2024-01-15T10:30:00"
            }
            """;

        // When & Then
        assertThat(json.parse(jsonContent))
            .satisfies(product -> {
                assertThat(product.id()).isEqualTo(1L);
                assertThat(product.name()).isEqualTo("Laptop");
                assertThat(product.price()).isEqualByComparingTo("999.99");
            });
    }
}
```

**Best Practices:**
- Use `@JsonTest` for focused JSON testing
- Test both serialization and deserialization
- Test custom serializers/deserializers
- Verify date/time format handling
- Test null value handling

**References:**
- `skills/junit-test/unit-test-json-serialization/SKILL.md`

---

### unit-test-mapper-converter

**Purpose**: Test object mappers and converters (MapStruct, manual mappers).

**When to use:**
- Testing DTO to entity conversion
- Testing entity to DTO conversion
- Validating field mapping logic
- Testing null handling in mappers

**Key Patterns:**

1. **MapStruct Mapper Test**
```java
class ProductMapperTest {

    private ProductMapper mapper = Mappers.getMapper(ProductMapper.class);

    @Test
    void shouldMapEntityToResponse() {
        // Given
        ProductEntity entity = ProductEntity.builder()
            .id(1L)
            .name("Laptop")
            .price(new BigDecimal("999.99"))
            .category(CategoryEntity.builder().name("Electronics").build())
            .build();

        // When
        ProductResponse response = mapper.toResponse(entity);

        // Then
        assertThat(response)
            .satisfies(r -> {
                assertThat(r.id()).isEqualTo(1L);
                assertThat(r.name()).isEqualTo("Laptop");
                assertThat(r.price()).isEqualByComparingTo("999.99");
                assertThat(r.categoryName()).isEqualTo("Electronics");
            });
    }

    @Test
    void shouldMapRequestToEntity() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "New Product",
            new BigDecimal("149.99"),
            "Books"
        );

        // When
        ProductEntity entity = mapper.toEntity(request);

        // Then
        assertThat(entity)
            .satisfies(e -> {
                assertThat(e.getName()).isEqualTo("New Product");
                assertThat(e.getPrice()).isEqualByComparingTo("149.99");
                assertThat(e.getId()).isNull(); // Not mapped from request
            });
    }

    @Test
    void shouldHandleNullValues() {
        // When
        ProductResponse response = mapper.toResponse(null);

        // Then
        assertThat(response).isNull();
    }
}
```

**Best Practices:**
- Test all mapping methods
- Verify nested object mapping
- Test null handling
- Test collection mapping
- Verify computed/derived fields

**References:**
- `skills/junit-test/unit-test-mapper-converter/SKILL.md`

---

### unit-test-config-properties

**Purpose**: Test `@ConfigurationProperties` classes.

**When to use:**
- Testing configuration binding
- Validating property validation
- Testing nested configuration
- Testing default values

**Key Patterns:**

1. **Configuration Properties Test**
```java
@SpringBootTest(classes = ApplicationProperties.class)
@TestPropertySource(properties = {
    "app.api.base-url=https://api.example.com",
    "app.api.timeout=5000",
    "app.api.retry.max-attempts=3",
    "app.api.retry.backoff=1000"
})
class ApplicationPropertiesTest {

    @Autowired
    private ApplicationProperties properties;

    @Test
    void shouldBindPropertiesCorrectly() {
        assertThat(properties.api().baseUrl()).isEqualTo("https://api.example.com");
        assertThat(properties.api().timeout()).isEqualTo(Duration.ofMillis(5000));
        assertThat(properties.api().retry().maxAttempts()).isEqualTo(3);
        assertThat(properties.api().retry().backoff()).isEqualTo(Duration.ofMillis(1000));
    }

    @Test
    void shouldUseDefaultValues() {
        assertThat(properties.api().connectTimeout())
            .isEqualTo(Duration.ofSeconds(10)); // Default value
    }
}
```

**Best Practices:**
- Test property binding
- Verify default values
- Test validation constraints
- Test nested properties

**References:**
- `skills/junit-test/unit-test-config-properties/SKILL.md`

---

## External Integration Testing

### unit-test-wiremock-rest-api

**Purpose**: Test HTTP clients and external API integrations using WireMock to stub external services.

**When to use:**
- Testing RestTemplate/WebClient usage
- Mocking external REST APIs
- Testing error handling for API calls
- Testing retry logic
- Validating request/response mapping

**Key Patterns:**

1. **WireMock Test Setup**
```java
@SpringBootTest
class ExternalApiClientTest {

    @Autowired
    private ExternalApiClient apiClient;

    private WireMockServer wireMockServer;

    @BeforeEach
    void setUp() {
        wireMockServer = new WireMockServer(8089);
        wireMockServer.start();
        WireMock.configureFor("localhost", 8089);
    }

    @AfterEach
    void tearDown() {
        wireMockServer.stop();
    }

    @Test
    void shouldFetchDataSuccessfully() {
        // Given
        stubFor(get(urlEqualTo("/api/data/123"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("""
                    {
                        "id": "123",
                        "name": "Test Data",
                        "value": 42
                    }
                    """)));

        // When
        DataResponse response = apiClient.getData("123");

        // Then
        assertThat(response)
            .satisfies(data -> {
                assertThat(data.id()).isEqualTo("123");
                assertThat(data.name()).isEqualTo("Test Data");
                assertThat(data.value()).isEqualTo(42);
            });

        verify(getRequestedFor(urlEqualTo("/api/data/123"))
            .withHeader("Accept", equalTo("application/json")));
    }

    @Test
    void shouldHandleApiError() {
        // Given
        stubFor(get(urlEqualTo("/api/data/404"))
            .willReturn(aResponse()
                .withStatus(404)
                .withBody("""
                    {
                        "error": "Not found"
                    }
                    """)));

        // When & Then
        assertThatThrownBy(() -> apiClient.getData("404"))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("Data not found");
    }

    @Test
    void shouldRetryOnTimeout() {
        // Given
        stubFor(get(urlEqualTo("/api/data/slow"))
            .inScenario("Retry")
            .whenScenarioStateIs(STARTED)
            .willReturn(aResponse()
                .withStatus(200)
                .withFixedDelay(5000)) // Timeout
            .willSetStateTo("First Attempt Failed"));

        stubFor(get(urlEqualTo("/api/data/slow"))
            .inScenario("Retry")
            .whenScenario StateIs("First Attempt Failed")
            .willReturn(aResponse()
                .withStatus(200)
                .withBody("""{"id": "slow", "name": "Success"}""")));

        // When
        DataResponse response = apiClient.getData("slow");

        // Then
        assertThat(response.name()).isEqualTo("Success");
        verify(2, getRequestedFor(urlEqualTo("/api/data/slow")));
    }
}
```

2. **Testing Request Body**
```java
@Test
void shouldSendCorrectRequestBody() {
    // Given
    stubFor(post(urlEqualTo("/api/data"))
        .willReturn(aResponse().withStatus(201)));

    CreateDataRequest request = new CreateDataRequest("Test", 100);

    // When
    apiClient.createData(request);

    // Then
    verify(postRequestedFor(urlEqualTo("/api/data"))
        .withRequestBody(equalToJson("""
            {
                "name": "Test",
                "value": 100
            }
            """)));
}
```

**Best Practices:**
- Start WireMock server in `@BeforeEach`
- Stop server in `@AfterEach`
- Use scenarios for stateful testing
- Test retry and timeout logic
- Verify request headers and body
- Test error responses
- Use `@TestPropertySource` to override API URLs

**References:**
- `skills/junit-test/unit-test-wiremock-rest-api/SKILL.md`

---

## Infrastructure Testing

### unit-test-caching

**Purpose**: Test Spring Cache behavior and cache operations.

**When to use:**
- Testing `@Cacheable` behavior
- Validating cache eviction with `@CacheEvict`
- Testing cache updates with `@CachePut`
- Verifying cache key generation

**Key Patterns:**

1. **Cache Behavior Test**
```java
@SpringBootTest
@EnableCaching
class ProductServiceCacheTest {

    @Autowired
    private ProductService productService;

    @Autowired
    private CacheManager cacheManager;

    @MockitoBean
    private ProductRepository productRepository;

    @BeforeEach
    void setUp() {
        cacheManager.getCacheNames()
            .forEach(name -> cacheManager.getCache(name).clear());
    }

    @Test
    void shouldCacheProductOnFirstCall() {
        // Given
        Product product = Product.create("Laptop", Money.of(999.99));
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        // When
        productService.getById(1L); // First call - cache miss
        productService.getById(1L); // Second call - cache hit

        // Then
        verify(productRepository, times(1)).findById(1L);
        
        Cache cache = cacheManager.getCache("products");
        assertThat(cache).isNotNull();
        assertThat(cache.get(1L)).isNotNull();
    }

    @Test
    void shouldEvictCacheOnDelete() {
        // Given
        Product product = Product.create("Laptop", Money.of(999.99));
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        productService.getById(1L); // Populate cache

        // When
        productService.delete(1L);

        // Then
        Cache cache = cacheManager.getCache("products");
        assertThat(cache.get(1L)).isNull();
    }
}
```

**Best Practices:**
- Clear cache before each test
- Verify repository is called only once for cached data
- Test cache eviction
- Test cache key generation
- Use simple cache provider (Caffeine) for tests

**References:**
- `skills/junit-test/unit-test-caching/SKILL.md`

---

### unit-test-scheduled-async

**Purpose**: Test scheduled tasks and asynchronous methods.

**When to use:**
- Testing `@Scheduled` methods
- Testing `@Async` methods
- Validating concurrent execution
- Testing scheduled task logic

**Key Patterns:**

1. **Scheduled Task Test**
```java
@SpringBootTest
class ScheduledTaskTest {

    @MockitoBean
    private ReportService reportService;

    @Test
    void shouldExecuteScheduledTask() {
        // Given
        await().atMost(Duration.ofSeconds(10))
            .untilAsserted(() -> 
                verify(reportService, atLeastOnce()).generateDailyReport()
            );
    }
}
```

2. **Async Method Test**
```java
@SpringBootTest
@EnableAsync
class AsyncServiceTest {

    @Autowired
    private AsyncService asyncService;

    @MockitoBean
    private EmailService emailService;

    @Test
    void shouldExecuteAsynchronously() {
        // When
        CompletableFuture<Void> future = asyncService.sendEmailAsync("test@example.com");

        // Then
        await().atMost(Duration.ofSeconds(5))
            .until(future::isDone);

        verify(emailService).send("test@example.com");
    }
}
```

**Best Practices:**
- Use Awaitility for async assertions
- Set reasonable timeouts
- Test that methods execute asynchronously
- Verify execution thread pool
- Test exception handling in async methods

**References:**
- `skills/junit-test/unit-test-scheduled-async/SKILL.md`

---

### unit-test-security-authorization

**Purpose**: Test Spring Security configuration and authorization rules.

**When to use:**
- Testing role-based access control
- Testing method security (`@PreAuthorize`, `@Secured`)
- Testing authentication requirements
- Testing custom security filters

**Key Patterns:**

1. **Method Security Test**
```java
@SpringBootTest
@Import(SecurityConfig.class)
class SecurityTest {

    @Autowired
    private AdminService adminService;

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAllowAdminAccess() {
        // When & Then
        assertThatCode(() -> adminService.deleteUser(1L))
            .doesNotThrowAnyException();
    }

    @Test
    @WithMockUser(roles = "USER")
    void shouldDenyUserAccess() {
        // When & Then
        assertThatThrownBy(() -> adminService.deleteUser(1L))
            .isInstanceOf(AccessDeniedException.class);
    }

    @Test
    void shouldRequireAuthentication() {
        // When & Then
        assertThatThrownBy(() -> adminService.deleteUser(1L))
            .isInstanceOf(AuthenticationCredentialsNotFoundException.class);
    }
}
```

**Best Practices:**
- Use `@WithMockUser` for role testing
- Test all security constraints
- Test both positive and negative cases
- Verify access denied exceptions
- Test authentication requirements

**References:**
- `skills/junit-test/unit-test-security-authorization/SKILL.md`

---

## Advanced Testing Patterns

### unit-test-parameterized

**Purpose**: Test multiple scenarios with different inputs using parameterized tests.

**When to use:**
- Testing multiple input combinations
- Testing boundary conditions
- Reducing test duplication
- Testing various valid/invalid inputs

**Key Patterns:**

1. **@ParameterizedTest with @ValueSource**
```java
@ParameterizedTest
@ValueSource(strings = {"", " ", "  "})
void shouldRejectBlankNames(String name) {
    // When & Then
    assertThatThrownBy(() -> Product.create(name, Money.of(100)))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("Product name cannot be blank");
}
```

2. **@ParameterizedTest with @CsvSource**
```java
@ParameterizedTest
@CsvSource({
    "100,    10,     10",
    "150,    20,     30",
    "200,    15,     30"
})
void shouldCalculateDiscount(BigDecimal price, int discountPercent, BigDecimal expected) {
    // When
    BigDecimal discount = discountCalculator.calculate(price, discountPercent);

    // Then
    assertThat(discount).isEqualByComparingTo(expected);
}
```

3. **@ParameterizedTest with @MethodSource**
```java
@ParameterizedTest
@MethodSource("provideInvalidEmails")
void shouldRejectInvalidEmail(String email) {
    // When & Then
    assertThatThrownBy(() -> User.create(email, "John"))
        .isInstanceOf(IllegalArgumentException.class);
}

private static Stream<String> provideInvalidEmails() {
    return Stream.of(
        "invalid",
        "@example.com",
        "user@",
        "user @example.com"
    );
}
```

4. **@ParameterizedTest with @EnumSource**
```java
@ParameterizedTest
@EnumSource(value = OrderStatus.class, names = {"PENDING", "PROCESSING"})
void shouldAllowCancellation(OrderStatus status) {
    // Given
    Order order = Order.createWithStatus(status);

    // When & Then
    assertThatCode(() -> order.cancel())
        .doesNotThrowAnyException();
}
```

**Best Practices:**
- Use descriptive test names with `@DisplayName`
- Choose appropriate source annotation
- Use `@CsvSource` for simple data tables
- Use `@MethodSource` for complex objects
- Use `@EnumSource` for enum testing
- Keep parameter count reasonable (< 5)

**References:**
- `skills/junit-test/unit-test-parameterized/SKILL.md`

---

### unit-test-boundary-conditions

**Purpose**: Test edge cases, boundary values, and corner cases.

**When to use:**
- Testing minimum/maximum values
- Testing null handling
- Testing empty collections
- Testing numeric boundaries
- Testing string length limits

**Key Patterns:**

1. **Numeric Boundary Testing**
```java
class PriceValidationTest {

    @Test
    void shouldRejectNegativePrice() {
        assertThatThrownBy(() -> Money.of(-0.01))
            .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void shouldAcceptZeroPrice() {
        assertThatCode(() -> Money.of(0))
            .doesNotThrowAnyException();
    }

    @Test
    void shouldAcceptMaxPrice() {
        assertThatCode(() -> Money.of(new BigDecimal("999999999.99")))
            .doesNotThrowAnyException();
    }
}
```

2. **Collection Boundary Testing**
```java
@Test
void shouldHandleEmptyList() {
    // Given
    List<Product> emptyList = Collections.emptyList();

    // When
    BigDecimal total = orderCalculator.calculateTotal(emptyList);

    // Then
    assertThat(total).isEqualByComparingTo(BigDecimal.ZERO);
}

@Test
void shouldHandleSingleItem() {
    // Given
    List<Product> singleItem = List.of(Product.create("Item", Money.of(50)));

    // When
    BigDecimal total = orderCalculator.calculateTotal(singleItem);

    // Then
    assertThat(total).isEqualByComparingTo("50");
}
```

3. **String Boundary Testing**
```java
@ParameterizedTest
@ValueSource(ints = {0, 1, 100, 255, 256})
void shouldValidateStringLength(int length) {
    String name = "a".repeat(length);
    
    if (length >= 3 && length <= 255) {
        assertThatCode(() -> Product.create(name, Money.of(100)))
            .doesNotThrowAnyException();
    } else {
        assertThatThrownBy(() -> Product.create(name, Money.of(100)))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
```

**Best Practices:**
- Test minimum, maximum, and just beyond boundaries
- Test null, empty, and single-element cases
- Test zero, negative, and positive values
- Test string length limits
- Test concurrent edge cases
- Document why boundary values matter

**References:**
- `skills/junit-test/unit-test-boundary-conditions/SKILL.md`

---

### unit-test-utility-methods

**Purpose**: Test utility classes and static helper methods.

**When to use:**
- Testing pure functions
- Testing string utilities
- Testing date/time utilities
- Testing validation utilities
- Testing formatting utilities

**Key Patterns:**

1. **Utility Method Test**
```java
class StringUtilsTest {

    @Test
    void shouldCapitalizeFirstLetter() {
        assertThat(StringUtils.capitalize("hello")).isEqualTo("Hello");
        assertThat(StringUtils.capitalize("HELLO")).isEqualTo("HELLO");
        assertThat(StringUtils.capitalize("h")).isEqualTo("H");
    }

    @Test
    void shouldHandleNullAndEmpty() {
        assertThat(StringUtils.capitalize(null)).isNull();
        assertThat(StringUtils.capitalize("")).isEmpty();
    }

    @ParameterizedTest
    @CsvSource({
        "'hello world', 'Hello World'",
        "'HELLO WORLD', 'Hello World'",
        "'hello', 'Hello'"
    })
    void shouldConvertToTitleCase(String input, String expected) {
        assertThat(StringUtils.toTitleCase(input)).isEqualTo(expected);
    }
}
```

2. **Date Utility Test**
```java
class DateUtilsTest {

    @Test
    void shouldCalculateDaysBetween() {
        // Given
        LocalDate start = LocalDate.of(2024, 1, 1);
        LocalDate end = LocalDate.of(2024, 1, 10);

        // When
        long days = DateUtils.daysBetween(start, end);

        // Then
        assertThat(days).isEqualTo(9);
    }

    @Test
    void shouldFormatDateCorrectly() {
        // Given
        LocalDateTime dateTime = LocalDateTime.of(2024, 1, 15, 10, 30, 45);

        // When
        String formatted = DateUtils.format(dateTime, "yyyy-MM-dd HH:mm");

        // Then
        assertThat(formatted).isEqualTo("2024-01-15 10:30");
    }
}
```

**Best Practices:**
- Test pure functions without dependencies
- No need for Spring context
- Test all edge cases
- Test null handling
- Use parameterized tests for multiple inputs
- Fast execution (< 10ms per test)

**References:**
- `skills/junit-test/unit-test-utility-methods/SKILL.md`

---

## Common Workflows

### Testing a Complete Feature

```bash
# 1. Test domain model (unit tests)
# - Test business rules
# - Test validation
# - Test state transitions
# - No dependencies, pure Java

# 2. Test repository (integration with Testcontainers)
# - @DataJpaTest with real database
# - Test queries
# - Test relationships

# 3. Test mappers (unit tests)
# - Entity to DTO conversion
# - DTO to Entity conversion
# - Null handling

# 4. Test service layer (unit tests with Mockito)
# - Mock repository and dependencies
# - Test business logic
# - Test exception scenarios
# - Verify interactions

# 5. Test controller (MockMvc tests)
# - @WebMvcTest for web layer
# - Test all endpoints
# - Test validation
# - Test error responses

# 6. Test external integrations (WireMock)
# - Mock external APIs
# - Test retry logic
# - Test error handling

# 7. End-to-end tests (optional, @SpringBootTest + Testcontainers)
# - Full application context
# - Real dependencies
# - Complete workflows
```

---

## Best Practices

### General Testing Principles

1. **Test Pyramid**
   - 70% Unit tests (fast, isolated)
   - 20% Integration tests (service layer, database)
   - 10% E2E tests (full application)

2. **Test Naming**
   - Use descriptive names: `shouldReturnProductWhenExists()`
   - Use `@DisplayName` for complex scenarios
   - Follow pattern: `should[ExpectedBehavior]When[Condition]()`

3. **Assertions**
   - Use AssertJ for fluent assertions
   - Use `assertThat()` over `assertEquals()`
   - Group related assertions with `satisfies()`

4. **Test Organization**
   - One test class per production class
   - Group tests by functionality
   - Use nested test classes for related scenarios

5. **Mocking**
   - Mock external dependencies only
   - Don't mock value objects or DTOs
   - Prefer real objects when simple
   - Use `@Mock` and `@InjectMocks` with Mockito

6. **Performance**
   - Unit tests < 50ms
   - Avoid `@SpringBootTest` for unit tests
   - Use static Testcontainers for reuse
   - Parallelize test execution

7. **Test Data**
   - Use test data builders
   - Avoid shared mutable state
   - Use `@BeforeEach` for setup
   - Clean up in `@AfterEach`

8. **Coverage**
   - Aim for 80%+ coverage
   - Focus on critical paths
   - Don't test trivial getters/setters
   - Test edge cases and error scenarios

### JUnit 5 Best Practices

- Use `@ExtendWith(MockitoExtension.class)` instead of `@RunWith`
- Use `@BeforeEach` instead of `@Before`
- Use `assertThrows()` for exception testing
- Use `@Nested` classes for grouping
- Use `@TestInstance(Lifecycle.PER_CLASS)` when needed
- Leverage `@ParameterizedTest` for multiple scenarios

### AssertJ Best Practices

```java
// ✅ Good - Fluent and readable
assertThat(user)
    .isNotNull()
    .satisfies(u -> {
        assertThat(u.getName()).isEqualTo("John");
        assertThat(u.getEmail()).isEqualTo("john@example.com");
    });

// ❌ Avoid - Multiple separate assertions
assertNotNull(user);
assertEquals("John", user.getName());
assertEquals("john@example.com", user.getEmail());
```

---

## References

- [Contributing Guide](../CONTRIBUTING.md)
- [README](../README.md)

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-08  
