# LangChain4j Testing Strategies - API References

Complete API reference for testing LangChain4j applications.

## Testing Dependencies

### Maven
```xml
<!-- JUnit 5 -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.9.3</version>
    <scope>test</scope>
</dependency>

<!-- Mockito -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>5.3.1</version>
    <scope>test</scope>
</dependency>

<!-- Testcontainers -->
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>1.19.0</version>
    <scope>test</scope>
</dependency>

<!-- AssertJ -->
<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>3.24.1</version>
    <scope>test</scope>
</dependency>
```

## JUnit 5 Annotations

### @Test
```java
@Test
void testMethod() {
    // Test implementation
}
```

### @BeforeEach / @AfterEach
```java
class MyTest {
    @BeforeEach
    void setUp() {
        // Setup before each test
    }
    
    @AfterEach
    void tearDown() {
        // Cleanup after each test
    }
}
```

### @BeforeAll / @AfterAll
```java
class MyTest {
    @BeforeAll
    static void setUpAll() {
        // One-time setup
    }
    
    @AfterAll
    static void tearDownAll() {
        // One-time cleanup
    }
}
```

### @ParameterizedTest
```java
@ParameterizedTest
@ValueSource(strings = {"Hello", "Hi", "Hey"})
void testGreetings(String greeting) {
    assertNotNull(greeting);
}

@ParameterizedTest
@CsvSource({
    "1, 2, 3",
    "5, 5, 10",
    "10, 20, 30"
})
void testAddition(int a, int b, int expected) {
    assertEquals(expected, a + b);
}
```

### @DisplayName
```java
@DisplayName("Chat service tests")
class ChatServiceTest {
    
    @Test
    @DisplayName("Should return greeting when given hello")
    void shouldGreet() {
        // Test implementation
    }
}
```

### @Nested
```java
@DisplayName("ChatService")
class ChatServiceTest {
    
    @Nested
    @DisplayName("with memory")
    class WithMemory {
        @Test
        void testRemembersMessages() { }
    }
    
    @Nested
    @DisplayName("without memory")
    class WithoutMemory {
        @Test
        void testForgetsPreviousMessages() { }
    }
}
```

## Mockito API

### Mock Creation
```java
ChatModel mockModel = mock(ChatModel.class);
ChatModel spyModel = spy(new ChatModel());
```

### Stubbing
```java
when(mockModel.chat("Hello")).thenReturn("Hi!");
when(mockModel.chat(anyString())).thenReturn("Generic response");
when(mockModel.chat(contains("question")))
    .thenReturn("I am not sure");

// Throwing exceptions
when(mockModel.chat(null))
    .thenThrow(new IllegalArgumentException("Message cannot be null"));

// Multiple returns
when(mockModel.chat("How are you?"))
    .thenReturn("I'm fine")
    .thenReturn("Still fine")
    .thenReturn("Getting tired");
```

### Argument Matchers
```java
any()                        // Any value
anyString()                  // Any string
anyInt()                     // Any integer
isA(String.class)           // Specific type
contains("substring")       // String contains
matches("pattern")          // Regex pattern
eq("exact")                 // Exact value
isNull()                    // Null value
notNull()                   // Not null
```

### Verification
```java
verify(mockModel).chat("Hello");
verify(mockModel, times(2)).chat("Hello");
verify(mockModel, never()).chat("Hello");
verify(mockModel, atLeastOnce()).chat(anyString());
verify(mockModel, atLeast(2)).chat(anyString());
verify(mockModel, atMost(5)).chat(anyString());

// Argument verification
ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
verify(mockModel).chat(captor.capture());
assertEquals("Hello", captor.getValue());
```

## Testcontainers API

### Generic Container
```java
@Container
static GenericContainer<?> qdrant = 
    new GenericContainer<>("qdrant/qdrant:latest")
        .withExposedPorts(6333)
        .withEnv("QDRANT_API_KEY", "test-key")
        .waitingFor(Wait.forHttp("/health").forPort(6333));
```

### Getting Connection Details
```java
String host = container.getHost();
int port = container.getFirstMappedPort();
String url = String.format("http://%s:%d", host, port);
```

### Lifecycle Control
```java
@Testcontainers
class Test {
    @Container
    static GenericContainer<?> container = new GenericContainer<>(...);
    
    // Lifecycle managed automatically
}

// Or manual
GenericContainer<?> container = new GenericContainer<>(...);
container.start();
// Use container
container.stop();
```

## Assertions

### JUnit Assertions
```java
assertEquals(expected, actual);
assertNotEquals(unexpected, actual);
assertTrue(condition);
assertFalse(condition);
assertNull(value);
assertNotNull(value);
assertSame(expected, actual);
assertThrows(IOException.class, () -> { /* code */ });
```

### AssertJ Fluent API
```java
assertThat(response).isNotNull();
assertThat(response).containsIgnoringCase("spring");
assertThat(response).doesNotContain("error");
assertThat(messages).hasSize(3);
assertThat(matches).extracting("score")
    .allMatch(score -> score > 0.7);
```

## Test Utilities

### ChatModel Mock Factory
```java
public static ChatModel createMockChatModel(
    Map<String, String> responses) {
    var mock = mock(ChatModel.class);
    responses.forEach((input, output) ->
        when(mock.chat(contains(input))).thenReturn(output)
    );
    return mock;
}
```

### Document Builder
```java
public static Document createDocument(String content) {
    var doc = Document.from(content);
    doc.metadata().put("source", "test");
    return doc;
}
```

### Embedding Factory
```java
public static Embedding createEmbedding(int dimension) {
    float[] vector = new float[dimension];
    Arrays.fill(vector, 0.5f);
    return new Embedding(vector);
}
```

## Test Organization

### Package Structure
```
src/
  main/
    java/
      com/example/
        service/
          ChatService.java
  test/
    java/
      com/example/
        service/
          ChatServiceTest.java
          ChatServiceIntegrationTest.java
```

### Naming Convention
- Unit tests: `*Test.java` (ChatServiceTest)
- Integration tests: `*IntegrationTest.java`
- Performance tests: `*PerformanceTest.java`

## Assertion Best Practices

### Clear Assertions
```java
// Good
assertEquals(5, result, "Addition should return 5");

// Better with AssertJ
assertThat(result)
    .as("Sum of 2+3")
    .isEqualTo(5);
```

### Multiple Assertions
```java
// Use assertAll for better error messages
assertAll(
    () -> assertNotNull(response),
    () -> assertTrue(response.contains("data")),
    () -> assertTrue(response.length() > 0)
);
```

## Performance Testing

### Timeout Assertions
```java
@Test
@Timeout(5)  // 5 seconds
void testResponseTime() {
    String response = chatModel.chat("Quick question?");
    assertNotNull(response);
}
```

### Measuring Execution
```java
long startTime = System.currentTimeMillis();
// Execute code
long duration = System.currentTimeMillis() - startTime;
assertTrue(duration < 1000, "Should complete in < 1s");
```

## Test Isolation

### Use Spy for Partial Mocking
```java
Calculator real = new Calculator();
Calculator spy = spy(real);

// Real implementation called
doReturn(10).when(spy).add(5, 5);
```

### Resetting Mocks
```java
reset(mockModel);
// All stubbing cleared
```

## Best Practices Summary

1. **Keep Tests Focused**: One concept per test
2. **Use Descriptive Names**: Test name should describe expected behavior
3. **Arrange-Act-Assert**: Clear test structure
4. **Mock External Dependencies**: Don't call real APIs
5. **Use Fixtures**: Reduce test duplication
6. **Test Error Cases**: Verify error handling
7. **Use Testcontainers**: Real integration testing
8. **Performance Tests**: Verify speed requirements
9. **Parameterized Tests**: Test multiple scenarios
10. **Clean Up**: Proper resource management
