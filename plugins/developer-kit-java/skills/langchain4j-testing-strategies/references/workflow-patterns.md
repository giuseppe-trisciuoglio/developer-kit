# Workflow Patterns and Best Practices

## Test Pyramid Strategy

### Unit Tests (70%)

```java
// Fast, isolated tests focusing on business logic
@Test
void shouldValidateUserInput() {
    InputGuardrail guardrail = new InputGuardrail();
    UserMessage message = UserMessage.from("Legitimate query");

    GuardrailResult result = guardrail.validate(message);

    assertThat(result).isSuccessful();
}

@Test
void shouldDetectInvalidInput() {
    InputGuardrail guardrail = new InputGuardrail();
    UserMessage message = UserMessage.from(""); // Empty input

    GuardrailResult result = guardrail.validate(message);

    assertThat(result).hasFailures();
}
```

### Integration Tests (20%)

```java
@Testcontainers
class AiServiceIntegrationTest {
    @Container
    static OllamaContainer ollama = new OllamaContainer("ollama/ollama:0.5.4");

    @Test
    void shouldProcessEndToEndRequest() {
        ChatModel model = OllamaChatModel.builder()
                .baseUrl(ollama.getEndpoint())
                .modelName("llama2")
                .timeout(Duration.ofSeconds(10))
                .build();

        var assistant = AiServices.builder(Assistant.class)
                .chatModel(model)
                .build();

        String response = assistant.chat("Test query");

        assertNotNull(response);
        assertFalse(response.trim().isEmpty());
    }
}
```

### End-to-End Tests (10%)

```java
@Test
@DisplayName("Complete AI workflow test")
void shouldCompleteFullWorkflow() {
    // Test complete user journey
    // Includes all components, real models, and external services

    // Arrange
    var userQuery = "What is the weather today?";
    var service = new CompleteAIService();

    // Act
    var result = service.processCompleteQuery(userQuery);

    // Assert
    assertNotNull(result);
    assertTrue(result.isSuccess());
    assertNotNull(result.getAnswer());

    // Verify all components were used
    verify(weatherService, atLeastOnce()).getWeather();
    verify(guardrail, atLeastOnce()).validate(any());
}
```

## Mock vs Real Model Strategy

### When to Use Mock Models

```java
// Fast unit tests (< 50ms)
@Test
void shouldProcessSimpleQueryFast() {
    ChatModel mockModel = mock(ChatModel.class);
    when(mockModel.generate(anyString()))
        .thenReturn(Response.from(AiMessage.from("Mocked response")));

    var service = AiServices.builder(AiService.class)
            .chatModel(mockModel)
            .build();

    String response = service.chat("What is Java?");

    // Fast assertions
    assertEquals("Mocked response", response);
}

// Business logic validation
@Test
void shouldApplyBusinessRules() {
    var guardrail = new BusinessRuleGuardrail();

    String result = guardrail.validateBusinessLogic("Test input");

    assertBusinessRulesApplied(result);
}

// Edge case testing
@Test
void shouldHandleEdgeCases() {
    var service = createTestService();

    // Test edge cases
    String emptyResponse = service.chat("");
    String longResponse = service.chat("a".repeat(10000));

    verifyEdgeCaseHandling(emptyResponse, longResponse);
}
```

### When to Use Real Models

```java
// Integration tests with real model
@Testcontainers
void shouldIntegrateWithRealModel() {
    @Container
    OllamaContainer ollama = new OllamaContainer("ollama/ollama:0.5.4");

    ChatModel model = OllamaChatModel.builder()
            .baseUrl(ollama.getEndpoint())
            .modelName("llama2")
            .build();

    // Test with real model behavior
    String response = model.generate("What is Java?");

    // Verify model-specific behavior
    assertTrue(response.toLowerCase().contains("programming"));
    assertTrue(response.toLowerCase().contains("java"));
}

// Model-specific behavior validation
@Test
void shouldValidateModelSpecificBehavior() {
    var model = OpenAiChatModel.builder()
            .apiKey(testApiKey)
            .modelName("gpt-4")
            .build();

    // Test model-specific patterns
    String response = model.generate("List 3 numbers");

    // Verify specific model behavior
    assertTrue(response.matches(".*\\d+.*")); // Contains numbers
}

// Performance benchmarking
@Test
@Timeout(10)
void shouldBenchmarkPerformance() {
    var model = OpenAiChatModel.builder()
            .apiKey(testApiKey)
            .modelName("gpt-3.5-turbo")
            .build();

    Instant start = Instant.now();
    String response = model.generate("Complex query");
    Duration duration = Duration.between(start, Instant.now());

    // Performance assertions
    assertTrue(duration.toSeconds() < 5);
    assertTrue(response.length() > 100);
}
```

## Test Data Management

### Test Fixtures

```java
class TestDataFixtures {
    public static final String SAMPLE_QUERY = "What is Java?";
    public static final String SAMPLE_RESPONSE = "Java is a programming language...";

    public static final Document DOCUMENT_1 = Document.from(
        "Spring Boot is a Java framework for building microservices"
    );

    public static final Document DOCUMENT_2 = Document.from(
        "Maven is a build automation tool for Java projects"
    );

    public static UserMessage createTestMessage(String content) {
        return UserMessage.from(content);
    }

    public static AiMessage createAiMessage(String content) {
        return AiMessage.from(content);
    }

    public static List<Document> createSampleDocuments() {
        return List.of(DOCUMENT_1, DOCUMENT_2);
    }

    public static Embedding createTestEmbedding() {
        float[] vector = new float[1536];
        Arrays.fill(vector, 0.1f);
        return new Embedding(vector);
    }
}

// Usage
class MyTest {
    @Test
    void useTestDataFixtures() {
        var message = TestDataFixtures.createTestMessage("Hello");
        var documents = TestDataFixtures.createSampleDocuments();

        // Test with fixtures
        var service = new AIService();
        var response = service.process(message, documents);

        // Verify
        assertNotNull(response);
    }
}
```

### Configuration Management

```java
@TestPropertySource(properties = {
    "langchain4j.openai.api-key=test-key",
    "langchain4j.ollama.base-url=http://localhost:11434",
    "app.test.mode=true"
})
class ConfigurationTest {
    @Autowired
    private TestConfig config;

    @Test
    void shouldUseTestConfiguration() {
        // Uses application-test.properties
        // Ensures test isolation
        assertEquals("test-key", config.getOpenaiApiKey());
        assertEquals("http://localhost:11434", config.getOllamaBaseUrl());
    }
}

// Configuration class
@Configuration
@ConfigurationProperties(prefix = "langchain4j")
class TestConfig {
    private String openaiApiKey;
    private String ollamaBaseUrl;

    // Getters and setters
    public String getOpenaiApiKey() { return openaiApiKey; }
    public void setOpenaiApiKey(String key) { this.openaiApiKey = key; }
    public String getOllamaBaseUrl() { return ollamaBaseUrl; }
    public void setOllamaBaseUrl(String url) { this.ollamaBaseUrl = url; }
}
```

### Test Data Cleanup

```java
class DataCleanupTest {
    @BeforeEach
    void setupTestData() {
        // Setup test data
        prepareTestDatabase();
    }

    @AfterEach
    void cleanupTestData() {
        // Clean up test data
        cleanupDatabase();
    }

    @Test
    void shouldMaintainDataIsolation() {
        // Act
        createTestData();

        // Assert
        assertTestDataExists();
    }

    private void prepareTestDatabase() {
        // Setup test database schema and initial data
    }

    private void cleanupDatabase() {
        // Clean up test data
    }

    private void createTestData() {
        // Create test data for specific test
    }

    private void assertTestDataExists() {
        // Verify test data
    }
}
```

## Test Organization Patterns

### Package Structure

```
src/test/java/com/example/ai/
├── service/
│   ├── unit/
│   │   ├── ChatServiceUnitTest.java
│   │   ├── GuardrailServiceUnitTest.java
│   │   └── ToolServiceUnitTest.java
│   ├── integration/
│   │   ├── OllamaIntegrationTest.java
│   │   ├── VectorStoreIntegrationTest.java
│   │   └── RagSystemIntegrationTest.java
│   └── e2e/
│       ├── CompleteWorkflowTest.java
│       ├── PerformanceTest.java
│       └── LoadTest.java
├── fixture/
│   ├── AiTestFixtures.java
│   ├── TestDataFactory.java
│   └── MockConfig.java
└── utils/
    ├── TestAssertions.java
    ├── PerformanceMetrics.java
    └── TestDataBuilder.java
```

### Test Naming Conventions

```java
// Unit tests
@Test
void shouldProcessSimpleQuery() { }

@Test
void shouldValidateInputFormat() { }

@Test
void shouldHandleEmptyInput() { }

// Integration tests
@Testcontainers
@DisplayName("Ollama Integration")
class OllamaIntegrationTest {
    @Test
    void shouldGenerateResponse() { }

    @Test
    void shouldHandleLargeQueries() { }
}

// Edge case tests
@Test
@DisplayName("Edge Cases")
class EdgeCaseTest {
    @Test
    void shouldHandleVeryLongInput() { }

    @Test
    void shouldHandleSpecialCharacters() { }

    @Test
    void shouldHandleNullInput() { }
}

// Performance tests
@Test
@DisplayName("Performance")
class PerformanceTest {
    @Test
    @Timeout(5)
    void shouldRespondWithinTimeLimit() { }

    @Test
    void shouldMeasureTokenUsage() { }
}
```

### Test Grouping

```java
@Tag("unit")
@Tag("service")
class UnitTestGroup { }

@Tag("integration")
@Tag("ollama")
class IntegrationTestGroup { }

@Tag("performance")
@Tag("e2e")
class PerformanceTestGroup { }

// Running specific test groups
mvn test -Dgroups="unit,service"          // Run unit service tests
mvn test -Dgroups="integration"           // Run all integration tests
mvn test -Dgroups="performance"           // Run performance tests
```

## Assertion Best Practices

### Clear Assertions

```java
// Good
assertEquals(5, result, "Addition should return 5");

// Better with AssertJ
assertThat(result)
    .as("Sum of 2+3")
    .isEqualTo(5);

// Even better - domain-specific
assertThat(result)
    .as("Calculation result")
    .isCorrectAnswer(5);  // Custom assertion
```

### Multiple Assertions

```java
// Use assertAll for better error messages
assertAll(
    () -> assertNotNull(response),
    () -> assertTrue(response.contains("data")),
    () -> assertTrue(response.length() > 0)
);

// With AssertJ
assertThat(response)
    .isNotNull()
    .contains("data")
    .hasSizeGreaterThan(0);
```

### Assertion Helpers

```java
class AiTestAssertions {
    static void assertValidResponse(String response) {
        assertThat(response)
            .isNotNull()
            .isNotEmpty()
            .doesNotContain("error");
    }

    static void assertResponseContainsKeywords(String response, String... keywords) {
        assertThat(response).containsAll(List.of(keywords));
    }

    static void assertResponseFormat(String response, ResponseFormat expectedFormat) {
        assertThat(response).matches(expectedFormat.getPattern());
    }

    static void assertResponseQuality(String response, String query) {
        assertThat(response)
            .isNotNull()
            .hasLengthGreaterThan(10)
            .doesNotContain("error")
            .containsAnyOf(query.split(" "));
    }
}

// Usage
@Test
void testResponseQuality() {
    String response = assistant.chat("What is AI?");
    AiTestAssertions.assertResponseQuality(response, "What is AI?");
}
```

## Test Isolation Techniques

### Mock Spy for Partial Mocking

```java
@Test
void testSpyPartialMocking() {
    Calculator real = new Calculator();
    Calculator spy = spy(real);

    // Mock specific method
    doReturn(10).when(spy).add(5, 5);

    // Real implementation for other methods
    int sum = spy.add(3, 4); // Returns 7 (real implementation)
    int special = spy.add(5, 5); // Returns 10 (mocked)
}
```

### Test Double Setup

```java
class TestDoubleSetup {
    private ChatModel mockModel;
    private EmbeddingStore mockStore;
    private AiService service;

    @BeforeEach
    void setupTestDoubles() {
        // Setup mocks
        mockModel = mock(ChatModel.class);
        mockStore = mock(EmbeddingStore.class);

        // Setup behavior
        when(mockModel.generate(anyString()))
            .thenReturn(Response.from(AiMessage.from("Test response")));

        // Create service
        service = AiServices.builder(AiService.class)
                .chatModel(mockModel)
                .build();
    }

    @AfterEach
    void verifyInteractions() {
        // Verify key interactions
        verify(mockModel, atLeastOnce()).generate(anyString());
        verifyNoMoreInteractions(mockModel);
    }
}
```

### Resetting Mocks

```java
class MockResetTest {
    private ChatModel mockModel;

    @BeforeEach
    void setup() {
        mockModel = mock(ChatModel.class);
        // Setup initial behavior
        when(mockModel.generate("hello")).thenReturn("Hi");
    }

    @AfterEach
    void cleanup() {
        reset(mockModel); // Clear all stubbing
    }

    @Test
    void firstTest() {
        // Use mock
    }

    @Test
    void secondTest() {
        // Fresh mock state due to reset
        when(mockModel.generate("hello")).thenReturn("Hello");
    }
}
```