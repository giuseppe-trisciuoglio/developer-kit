# Advanced Testing Patterns

## Testing Streaming Responses

### Streaming Response Test

```java
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler;
import org.junit.jupiter.api.Test;
import reactor.core.publisher.Flux;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

class StreamingResponseTest {

    @Test
    void shouldHandleStreamingResponse() throws Exception {
        // Arrange
        StreamingChatModel streamingModel = OllamaStreamingChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("llama2")
                .build();

        List<String> chunks = new ArrayList<>();
        CompletableFuture<ChatResponse> responseFuture = new CompletableFuture<>();

        StreamingChatResponseHandler handler = new StreamingChatResponseHandler() {
            @Override
            public void onPartialResponse(String partialResponse) {
                chunks.add(partialResponse);
            }

            @Override
            public void onComplete(ChatResponse completeResponse) {
                responseFuture.complete(completeResponse);
            }

            @Override
            public void onError(Throwable error) {
                responseFuture.completeExceptionally(error);
            }
        };

        // Act
        streamingModel.generate("Count to 5", handler);
        ChatResponse response = responseFuture.get(30, java.util.concurrent.TimeUnit.SECONDS);

        // Assert
        assertNotNull(response);
        assertFalse(chunks.isEmpty());
        assertTrue(response.content().text().length() > 0);
    }
}
```

### Mock Streaming Test

```java
@Test
void shouldMockStreamingResponse() {
    // Arrange
    StreamingChatModel mockModel = mock(StreamingChatModel.class);

    List<String> chunks = new ArrayList<>();
    doAnswer(invocation -> {
        StreamingChatResponseHandler handler = invocation.getArgument(1);
        handler.onPartialResponse("Hello ");
        handler.onPartialResponse("World");
        handler.onComplete(Response.from(AiMessage.from("Hello World")));
        return null;
    }).when(mockModel)
        .generate(anyString(), any(StreamingChatResponseHandler.class));

    // Act
    mockModel.generate("Test", new StreamingChatResponseHandler() {
        @Override
        public void onPartialResponse(String partialResponse) {
            chunks.add(partialResponse);
        }

        @Override
        public void onComplete(ChatResponse response) {}

        @Override
        public void onError(Throwable error) {}
    });

    // Assert
    assertEquals(2, chunks.size());
    assertEquals("Hello World", String.join("", chunks));
}
```

## Memory Management Testing

### Chat Memory Testing

```java
import dev.langchain4j.memory.chat.MessageWindowChatMemory;

class MemoryTest {

    @Test
    void testChatMemory() {
        // Arrange
        var memory = MessageWindowChatMemory.withMaxMessages(3);

        memory.add(UserMessage.from("Message 1"));
        memory.add(AiMessage.from("Response 1"));
        memory.add(UserMessage.from("Message 2"));
        memory.add(AiMessage.from("Response 2"));

        // Assert
        List<ChatMessage> messages = memory.messages();
        assertEquals(4, messages.size());

        // Add more to test window
        memory.add(UserMessage.from("Message 3"));
        assertEquals(4, memory.messages().size());  // Window size limit
    }

    @Test
    void testMultiUserMemory() {
        var memoryProvider =
            memoryId -> MessageWindowChatMemory.withMaxMessages(10);

        var memory1 = memoryProvider.provide("user1");
        var memory2 = memoryProvider.provide("user2");

        memory1.add(UserMessage.from("User 1 message"));
        memory2.add(UserMessage.from("User 2 message"));

        assertEquals(1, memory1.messages().size());
        assertEquals(1, memory2.messages().size());
    }
}
```

### Memory Persistence Test

```java
@Test
void testMemorySerialization() throws Exception {
    var memory = MessageWindowChatMemory.withMaxMessages(5);
    memory.add(UserMessage.from("Test message"));

    // Serialize
    var bytes = serializeMemory(memory);

    // Deserialize
    var deserializedMemory = deserializeMemory(bytes);

    // Verify
    assertEquals(memory.messages().size(), deserializedMemory.messages().size());
}

private byte[] serializeMemory(MessageWindowChatMemory memory) {
    // Implement serialization logic
    return new byte[0];
}

private MessageWindowChatMemory deserializeMemory(byte[] bytes) {
    // Implement deserialization logic
    return MessageWindowChatMemory.withMaxMessages(5);
}
```

## Error Handling Tests

### Service Unavailable Test

```java
@Test
void shouldHandleServiceUnavailable() {
    // Arrange
    ChatModel mockModel = mock(ChatModel.class);
    when(mockModel.generate(any()))
        .thenThrow(new RuntimeException("Service unavailable"));

    var service = AiServices.builder(AiService.class)
            .chatModel(mockModel)
            .toolExecutionErrorHandler((request, exception) ->
                "Service unavailable: " + exception.getMessage()
            )
            .build();

    // Act
    String response = service.chat("test");

    // Assert
    assertTrue(response.contains("Service unavailable"));
}
```

### Rate Limiting Test

```java
@Test
void shouldHandleRateLimiting() {
    // Arrange
    ChatModel mockModel = mock(ChatModel.class);

    // Simulate rate limiting
    when(mockModel.generate(any()))
        .thenThrow(new RuntimeException("Rate limit exceeded"));

    var service = new AiService(mockModel);

    // Act & Assert
    assertThrows(RuntimeException.class, () -> service.chat("test"));
}
```

## Load Testing

### Concurrent Request Test

```java
@Test
void shouldHandleConcurrentRequests() throws InterruptedException {
    // Arrange
    ChatModel mockModel = mock(ChatModel.class);
    when(mockModel.generate(any()))
        .thenReturn(Response.from(AiMessage.from("Response")));

    var service = AiServices.builder(AiService.class)
            .chatModel(mockModel)
            .build();

    int threadCount = 10;
    ExecutorService executor = Executors.newFixedThreadPool(threadCount);
    List<Future<String>> futures = new ArrayList<>();

    // Act
    for (int i = 0; i < threadCount; i++) {
        futures.add(executor.submit(() -> service.chat("test")));
    }

    // Assert
    for (Future<String> future : futures) {
        assertNotNull(future.get());
        assertEquals("Response", future.get());
    }

    executor.shutdown();
}
```

### Long-running Test

```java
@Test
void shouldHandleLongRunningRequests() {
    // Arrange
    ChatModel model = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o")
            .timeout(Duration.ofMinutes(2))
            .build();

    // Act
    Instant start = Instant.now();
    String response = model.chat("Explain quantum computing in detail");
    Duration duration = Duration.between(start, Instant.now());

    // Assert
    assertTrue(duration.toMinutes() < 1, "Should complete in less than 1 minute");
    assertNotNull(response);
    assertTrue(response.length() > 100);
}
```

## Custom Assertion Helpers

```java
class AIAssertions {

    static void assertResponseContains(String response, String... keywords) {
        for (String keyword : keywords) {
            assertTrue(
                response.toLowerCase().contains(keyword.toLowerCase()),
                "Response does not contain: " + keyword
            );
        }
    }

    static void assertValidJSON(String response) {
        try {
            new JsonParser().parse(response);
        } catch (Exception e) {
            fail("Response is not valid JSON: " + e.getMessage());
        }
    }

    static void assertNonEmpty(String response) {
        assertNotNull(response);
        assertFalse(response.trim().isEmpty());
    }

    static void assertCoherentResponse(String response, String query) {
        assertNotNull(response);
        assertFalse(response.trim().isEmpty());
        assertFalse(response.contains("error"));
        // Additional coherence checks based on domain
    }
}

// Usage
@Test
void testResponseQuality() {
    String response = assistant.chat("Explain microservices");

    AIAssertions.assertNonEmpty(response);
    AIAssertions.assertResponseContains(response, "microservices", "architecture");
    AIAssertions.assertCoherentResponse(response, "Explain microservices");
}
```

## Test Fixtures and Utilities

### Test Data Fixtures

```java
class AiTestFixtures {

    public static ChatModel createMockChatModel(
        Map<String, String> responses) {
        var mock = mock(ChatModel.class);
        responses.forEach((input, output) ->
            when(mock.chat(contains(input))).thenReturn(output)
        );
        return mock;
    }

    public static EmbeddingModel createMockEmbeddingModel(String text) {
        var mock = mock(EmbeddingModel.class);
        var embedding = new Response<>(
            new Embedding(new float[]{0.1f, 0.2f, 0.3f}), null
        );
        when(mock.embed(text)).thenReturn(embedding);
        return mock;
    }

    public static Document createTestDocument(String content) {
        var doc = Document.from(content);
        doc.metadata().put("source", "test");
        doc.metadata().put("created", Instant.now().toString());
        return doc;
    }

    public static UserMessage createTestMessage(String content) {
        return UserMessage.from(content);
    }

    public static AiService createTestService(ChatModel model) {
        return AiServices.builder(AiService.class)
                .chatModel(model)
                .build();
    }
}

// Usage in tests
@Test
void testWithFixtures() {
    var chatModel = AiTestFixtures.createMockChatModel(
        Map.of("Hello", "Hi!", "Bye", "Goodbye!")
    );

    var service = AiTestFixtures.createTestService(chatModel);
    assertEquals("Hi!", service.chat("Hello"));
}
```

### Test Context Management

```java
class TestContext {
    private static final ThreadLocal<ChatModel> currentModel =
        new ThreadLocal<>();
    private static final ThreadLocal<EmbeddingStore> currentStore =
        new ThreadLocal<>();

    public static void setModel(ChatModel model) {
        currentModel.set(model);
    }

    public static ChatModel getModel() {
        return currentModel.get();
    }

    public static void setStore(EmbeddingStore store) {
        currentStore.set(store);
    }

    public static EmbeddingStore getStore() {
        return currentStore.get();
    }

    public static void clear() {
        currentModel.remove();
        currentStore.remove();
    }
}

@BeforeAll
static void setupTestContext() {
    var model = createTestModel();
    TestContext.setModel(model);

    var store = createTestStore();
    TestContext.setStore(store);
}

@AfterAll
static void cleanupTestContext() {
    TestContext.clear();
}
```