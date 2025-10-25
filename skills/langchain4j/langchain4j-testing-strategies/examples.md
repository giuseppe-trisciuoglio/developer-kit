# LangChain4j Testing Strategies - Practical Examples

Production-ready testing patterns for LangChain4j applications.

## 1. Unit Testing with Mock ChatModel

**Scenario**: Test business logic without calling real LLMs.

```java
import org.junit.jupiter.api.Test;
import static org.mockito.Mockito.*;

class ChatServiceUnitTest {
    
    @Test
    void testChatWithMockModel() {
        // Arrange
        ChatModel mockModel = mock(ChatModel.class);
        when(mockModel.chat("Hello")).thenReturn("Hi there!");
        
        var chatService = new ChatService(mockModel);
        
        // Act
        String response = chatService.chat("Hello");
        
        // Assert
        assertEquals("Hi there!", response);
        verify(mockModel, times(1)).chat("Hello");
    }
    
    @Test
    void testComplexPrompt() {
        ChatModel mockModel = mock(ChatModel.class);
        
        when(mockModel.chat(
            argThat(msg -> msg.contains("Calculate"))
        )).thenReturn("42");
        
        var service = new ChatService(mockModel);
        String result = service.chat("Calculate 2+2");
        
        assertEquals("42", result);
    }
}
```

## 2. Integration Testing with Testcontainers

**Scenario**: Test with real services in containers.

```java
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

@Testcontainers
class VectorStoreIntegrationTest {
    
    @Container
    static GenericContainer<?> qdrantContainer = 
        new GenericContainer<>("qdrant/qdrant:latest")
            .withExposedPorts(6333);
    
    private EmbeddingStore<TextSegment> embeddingStore;
    
    @BeforeEach
    void setUp() {
        var host = qdrantContainer.getHost();
        var port = qdrantContainer.getFirstMappedPort();
        
        embeddingStore = QdrantEmbeddingStore.builder()
            .host(host)
            .port(port)
            .collectionName("test-collection")
            .build();
    }
    
    @Test
    void testEmbeddingStorage() {
        var embedding = new Embedding(new float[]{0.1f, 0.2f, 0.3f});
        var segment = TextSegment.from("Test content");
        
        String id = embeddingStore.add(embedding, segment);
        assertNotNull(id);
        
        var request = EmbeddingSearchRequest.builder()
            .queryEmbedding(embedding)
            .maxResults(1)
            .build();
            
        var result = embeddingStore.search(request);
        assertEquals(1, result.matches().size());
    }
}
```

## 3. AI Service Testing with Captured Responses

**Scenario**: Test AI service behavior with predefined responses.

```java
class AIServiceTest {
    
    @Test
    void testAIServiceWithCapturedResponses() {
        var chatModel = new CapturedResponseChatModel(
            Map.of(
                "What is Spring Boot?", 
                "Spring Boot is a Java framework for building applications.",
                "What is RAG?",
                "RAG stands for Retrieval-Augmented Generation."
            )
        );
        
        var assistant = AiServices.builder(Assistant.class)
            .chatModel(chatModel)
            .build();
        
        assertEquals(
            "Spring Boot is a Java framework for building applications.",
            assistant.chat("What is Spring Boot?")
        );
    }
}

class CapturedResponseChatModel implements ChatModel {
    private final Map<String, String> responses;
    
    public CapturedResponseChatModel(Map<String, String> responses) {
        this.responses = responses;
    }
    
    @Override
    public String chat(String userMessage) {
        return responses.getOrDefault(
            userMessage,
            "I don't have a response for that."
        );
    }
}
```

## 4. Testing Tools/Function Calling

**Scenario**: Verify that tools are called correctly.

```java
class ToolCallingTest {
    
    @Test
    void testToolExecution() {
        var mockCalculator = spy(new Calculator());
        
        var chatModel = mock(ChatModel.class);
        when(chatModel.chat(anyString())).thenReturn("Result is 5");
        
        var assistant = AiServices.builder(Assistant.class)
            .chatModel(chatModel)
            .tools(mockCalculator)
            .build();
        
        assistant.chat("Add 2 and 3");
        
        // Verify tool was called
        verify(mockCalculator, times(1)).add(2, 3);
    }
    
    @Test
    void testToolErrorHandling() {
        var chatModel = mock(ChatModel.class);
        
        var assistant = AiServices.builder(Assistant.class)
            .chatModel(chatModel)
            .tools(new FaultyTool())
            .toolExecutionErrorHandler((request, exception) -> 
                "Tool error: " + exception.getMessage()
            )
            .build();
        
        // Should handle error gracefully
        String result = assistant.chat("Execute faulty tool");
        assertTrue(result.contains("Tool error"));
    }
}
```

## 5. RAG Testing with In-Memory Store

**Scenario**: Test RAG functionality with in-memory vector store.

```java
class RAGTest {
    
    @Test
    void testRAGWithInMemoryStore() {
        var embeddingStore = new InMemoryEmbeddingStore<TextSegment>();
        
        var mockEmbedding = mock(EmbeddingModel.class);
        when(mockEmbedding.embed(anyString()))
            .thenReturn(new Response<>(
                new Embedding(new float[]{0.1f, 0.2f, 0.3f}),
                null
            ));
        
        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(mockEmbedding)
            .embeddingStore(embeddingStore)
            .build();
        
        ingestor.ingest(Document.from("Spring Boot is powerful"));
        
        assertEquals(1, embeddingStore.removeAll().size());
    }
}
```

## 6. Performance Testing

**Scenario**: Measure response times and token usage.

```java
class PerformanceTest {
    
    @Test
    void testResponseTime() {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();
        
        var startTime = System.currentTimeMillis();
        String response = chatModel.chat("What is AI?");
        var duration = System.currentTimeMillis() - startTime;
        
        // Assert response time < 5 seconds
        assertTrue(duration < 5000, "Response took too long: " + duration + "ms");
        assertNotNull(response);
    }
    
    @Test
    void testTokenUsageTracking() {
        var chatModel = mock(ChatModel.class);
        var mockResponse = new ChatResponse(
            List.of(new AiMessage("Response")),
            new TokenUsage(10, 20, 30),
            "completed"
        );
        
        when(chatModel.chat(any(ChatRequest.class)))
            .thenReturn(mockResponse);
        
        var response = chatModel.chat(ChatRequest.builder().build());
        
        assertEquals(10, response.tokenUsage().inputTokenCount());
        assertEquals(20, response.tokenUsage().outputTokenCount());
        assertEquals(30, response.tokenUsage().totalTokenCount());
    }
}
```

## 7. Streaming Response Testing

**Scenario**: Test streaming functionality.

```java
class StreamingTest {
    
    @Test
    void testStreamingResponse() {
        var streamingModel = mock(StreamingChatModel.class);
        
        doAnswer(invocation -> {
            StreamingChatResponseHandler handler = 
                invocation.getArgument(1);
            handler.onPartialResponse("Hello ");
            handler.onPartialResponse("World");
            handler.onCompleteResponse(
                new ChatResponse(
                    List.of(new AiMessage("Hello World")),
                    null,
                    "completed"
                )
            );
            return null;
        }).when(streamingModel)
          .chat(anyString(), any(StreamingChatResponseHandler.class));
        
        List<String> tokens = new ArrayList<>();
        streamingModel.chat("Test", new StreamingChatResponseHandler() {
            @Override
            public void onPartialResponse(String partialResponse) {
                tokens.add(partialResponse);
            }
            
            @Override
            public void onCompleteResponse(ChatResponse response) {}
            
            @Override
            public void onError(Throwable error) {}
        });
        
        assertEquals(2, tokens.size());
        assertEquals("Hello World", String.join("", tokens));
    }
}
```

## 8. Memory Management Testing

**Scenario**: Test conversation memory.

```java
class MemoryTest {
    
    @Test
    void testChatMemory() {
        var memory = MessageWindowChatMemory.withMaxMessages(3);
        
        memory.add(UserMessage.from("Message 1"));
        memory.add(AiMessage.from("Response 1"));
        memory.add(UserMessage.from("Message 2"));
        memory.add(AiMessage.from("Response 2"));
        
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

## 9. Assertion Helpers

**Scenario**: Custom assertions for AI responses.

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
}

// Usage
@Test
void testResponseFormat() {
    String response = assistant.chat("Return JSON");
    AIAssertions.assertValidJSON(response);
    AIAssertions.assertResponseContains(response, "data", "status");
    AIAssertions.assertNonEmpty(response);
}
```

## 10. Test Fixtures

**Scenario**: Reusable test data and setup.

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
    
    public static EmbeddingModel createMockEmbeddingModel() {
        var mock = mock(EmbeddingModel.class);
        when(mock.embed(any(TextSegment.class)))
            .thenReturn(new Response<>(
                new Embedding(new float[]{0.1f, 0.2f, 0.3f}),
                null
            ));
        return mock;
    }
    
    public static Document createTestDocument(String content) {
        var doc = Document.from(content);
        doc.metadata().put("test", "true");
        return doc;
    }
}

@Test
void testWithFixtures() {
    var chatModel = AiTestFixtures.createMockChatModel(
        Map.of("Hello", "Hi!", "Bye", "Goodbye!")
    );
    
    var service = new ChatService(chatModel);
    assertEquals("Hi!", service.chat("Hello"));
}
```

## Best Practices

1. **Mock External Services**: Don't call real APIs in tests
2. **Use Containers**: Testcontainers for infrastructure testing
3. **Test Memory Management**: Verify conversation history handling
4. **Test Error Paths**: Ensure error handlers work correctly
5. **Performance Assertions**: Check response times in integration tests
6. **Use Fixtures**: Reusable test data reduces duplication
7. **Parameterized Tests**: Test multiple scenarios with @ParameterizedTest
8. **Assertion Helpers**: Create domain-specific assertions
9. **Capture Evidence**: Log prompts and responses for debugging
10. **Clean Up**: Use @BeforeEach and @AfterEach for resource management
