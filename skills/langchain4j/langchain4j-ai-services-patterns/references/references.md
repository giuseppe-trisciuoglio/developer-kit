# LangChain4j AI Services - API References

Complete API reference for LangChain4j AI Services patterns.

## Core Interfaces and Classes

### AiServices Builder

**Purpose**: Creates implementations of custom Java interfaces backed by LLM capabilities.

```java
public class AiServices {
    
    static <T> AiServicesBuilder<T> builder(Class<T> aiService)
    // Create builder for an AI service interface
    
    static <T> T create(Class<T> aiService, ChatModel chatModel)
    // Quick creation with just chat model
    
    static <T> T builder(Class<T> aiService)
        .chatModel(ChatModel chatModel)           // Required for sync
        .streamingChatModel(StreamingChatModel)   // Required for streaming
        .chatMemory(ChatMemory)                   // Single shared memory
        .chatMemoryProvider(ChatMemoryProvider)   // Per-user memory
        .tools(Object... tools)                   // Register tool objects
        .toolProvider(ToolProvider)               // Dynamic tool selection
        .contentRetriever(ContentRetriever)       // For RAG
        .retrievalAugmentor(RetrievalAugmentor)   // Advanced RAG
        .moderationModel(ModerationModel)         // Content moderation
        .build()                                  // Build the implementation
}
```

### Core Annotations

**@SystemMessage**: Define system prompt for the AI service.
```java
@SystemMessage("You are a helpful Java developer")
String chat(String userMessage);

// Template variables
@SystemMessage("You are a {{expertise}} expert")
String explain(@V("expertise") String domain, String question);
```

**@UserMessage**: Define user message template.
```java
@UserMessage("Translate to {{language}}: {{text}}")
String translate(@V("language") String lang, @V("text") String text);

// With method parameters matching template
@UserMessage("Summarize: {{it}}")
String summarize(String text); // {{it}} refers to parameter
```

**@MemoryId**: Create separate memory context per identifier.
```java
interface MultiUserChat {
    String chat(@MemoryId String userId, String message);
    String chat(@MemoryId int sessionId, String message);
}
```

**@V**: Map method parameter to template variable.
```java
@UserMessage("Write {{type}} code for {{language}}")
String writeCode(@V("type") String codeType, @V("language") String lang);
```

### ChatMemory Implementations

**MessageWindowChatMemory**: Keeps last N messages.
```java
ChatMemory memory = MessageWindowChatMemory.withMaxMessages(10);
// Or with explicit builder
ChatMemory memory = MessageWindowChatMemory.builder()
    .maxMessages(10)
    .build();
```

**ChatMemoryProvider**: Factory for creating per-user memory.
```java
ChatMemoryProvider provider = memoryId -> 
    MessageWindowChatMemory.withMaxMessages(20);
```

### Tool Integration

**@Tool**: Mark methods that LLM can call.
```java
@Tool("Calculate sum of two numbers")
int add(@P("first number") int a, @P("second number") int b) {
    return a + b;
}
```

**@P**: Parameter description for LLM.
```java
@Tool("Search documents")
List<Document> search(
    @P("search query") String query,
    @P("max results") int limit
) { ... }
```

**ToolProvider**: Dynamic tool selection based on context.
```java
interface DynamicToolAssistant {
    String execute(String command);
}

ToolProvider provider = context -> 
    context.contains("calculate") ? new Calculator() : new DataService();
```

### Structured Output

**@Description**: Annotate output fields for extraction.
```java
class Person {
    @Description("Person's full name")
    String name;
    
    @Description("Age in years")
    int age;
}

interface Extractor {
    @UserMessage("Extract person from: {{it}}")
    Person extract(String text);
}
```

### Error Handling

**ToolExecutionErrorHandler**: Handle tool execution failures.
```java
.toolExecutionErrorHandler((request, exception) -> {
    logger.error("Tool failed: " + request.name(), exception);
    return "Tool execution failed: " + exception.getMessage();
})
```

**ToolArgumentsErrorHandler**: Handle malformed tool arguments.
```java
.toolArgumentsErrorHandler((request, exception) -> {
    logger.warn("Invalid arguments for " + request.name());
    return "Please provide valid arguments";
})
```

## Streaming APIs

### TokenStream

**Purpose**: Handle streaming LLM responses token-by-token.

```java
interface StreamingAssistant {
    TokenStream streamChat(String message);
}

TokenStream stream = assistant.streamChat("Tell me a story");

stream
    .onNext(token -> {
        // Process each token
        System.out.print(token);
    })
    .onCompleteResponse(response -> {
        // Full response available
        System.out.println("\nTokens used: " + response.tokenUsage());
    })
    .onError(error -> {
        System.err.println("Error: " + error);
    })
    .onToolExecuted(toolExecution -> {
        System.out.println("Tool: " + toolExecution.request().name());
    })
    .onRetrieved(contents -> {
        // RAG content retrieved
        contents.forEach(c -> System.out.println(c.textSegment()));
    })
    .start();
```

### StreamingChatResponseHandler

**Purpose**: Callback-based streaming without TokenStream.

```java
streamingModel.chat(request, new StreamingChatResponseHandler() {
    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.print(partialResponse);
    }
    
    @Override
    public void onCompleteResponse(ChatResponse response) {
        System.out.println("\nComplete!");
    }
    
    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

## Content Retrieval

### ContentRetriever Interface

**Purpose**: Fetch relevant content for RAG.

```java
interface ContentRetriever {
    Content retrieve(Query query);
    List<Content> retrieveAll(List<Query> queries);
}
```

### EmbeddingStoreContentRetriever

```java
ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
    .embeddingStore(embeddingStore)
    .embeddingModel(embeddingModel)
    .maxResults(5)                           // Default max results
    .minScore(0.7)                           // Similarity threshold
    .dynamicMaxResults(query -> 10)          // Query-dependent
    .dynamicMinScore(query -> 0.8)           // Query-dependent
    .filter(new IsEqualTo("userId", "123")) // Metadata filter
    .dynamicFilter(query -> {...})           // Dynamic filter
    .build();
```

### RetrievalAugmentor

**Purpose**: Advanced RAG pipeline with query transformation and re-ranking.

```java
RetrievalAugmentor augmentor = DefaultRetrievalAugmentor.builder()
    .queryTransformer(new CompressingQueryTransformer(chatModel))
    .contentRetriever(contentRetriever)
    .contentAggregator(ReRankingContentAggregator.builder()
        .scoringModel(scoringModel)
        .minScore(0.8)
        .build())
    .build();

// Use with AI Service
var assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .retrievalAugmentor(augmentor)
    .build();
```

## Request/Response Models

### ChatRequest

**Purpose**: Build complex chat requests with multiple messages.

```java
ChatRequest request = ChatRequest.builder()
    .messages(
        SystemMessage.from("You are helpful"),
        UserMessage.from("What is AI?"),
        AiMessage.from("AI is...")
    )
    .temperature(0.7)
    .maxTokens(500)
    .topP(0.95)
    .build();

ChatResponse response = chatModel.chat(request);
```

### ChatResponse

**Purpose**: Access chat model responses and metadata.

```java
String content = response.aiMessage().text();
TokenUsage usage = response.tokenUsage();

System.out.println("Tokens: " + usage.totalTokenCount());
System.out.println("Prompt tokens: " + usage.inputTokenCount());
System.out.println("Completion tokens: " + usage.outputTokenCount());
System.out.println("Finish reason: " + response.finishReason());
```

## Query and Content

### Query

**Purpose**: Represent a user query in retrieval context.

```java
// Query object contains:
String text                      // The query text
Metadata metadata()              // Query metadata (e.g., userId)
Object metadata(String key)      // Get metadata value
Object metadata(String key, Object defaultValue)
```

### Content

**Purpose**: Retrieved content with metadata.

```java
String textSegment()            // Retrieved text
double score()                  // Relevance score
Metadata metadata()             // Content metadata (e.g., source)
Map<String, Object> source()    // Original source data
```

## Message Types

### SystemMessage
```java
SystemMessage message = SystemMessage.from("You are a code reviewer");
```

### UserMessage
```java
UserMessage message = UserMessage.from("Review this code");
// With images
UserMessage message = UserMessage.from(
    TextContent.from("Analyze this"),
    ImageContent.from("http://...", "image/png")
);
```

### AiMessage
```java
AiMessage message = AiMessage.from("Here's my analysis");
// With tool calls
AiMessage message = AiMessage.from(
    "Let me calculate",
    ToolExecutionResultMessage.from(toolName, result)
);
```

## Configuration Patterns

### Chat Model Configuration

```java
ChatModel model = OpenAiChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName("gpt-4o-mini")           // Model selection
    .temperature(0.7)                   // Creativity (0-2)
    .topP(0.95)                         // Diversity (0-1)
    .topK(40)                           // Top K tokens
    .maxTokens(2000)                    // Max generation
    .frequencyPenalty(0.0)              // Reduce repetition
    .presencePenalty(0.0)               // Reduce topic switching
    .seed(42)                           // Reproducibility
    .logRequests(true)                  // Debug logging
    .logResponses(true)                 // Debug logging
    .build();
```

### Embedding Model Configuration

```java
EmbeddingModel embedder = OpenAiEmbeddingModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName("text-embedding-3-small")
    .dimensions(512)                    // Custom dimensions
    .build();
```

## Best Practices for API Usage

1. **Type Safety**: Always define typed interfaces for type safety at compile time
2. **Separation of Concerns**: Use different interfaces for different domains
3. **Error Handling**: Always implement error handlers for tools
4. **Memory Management**: Choose appropriate memory implementation for use case
5. **Token Optimization**: Use temperature=0 for deterministic tasks
6. **Testing**: Mock ChatModel for unit tests
7. **Logging**: Enable request/response logging in development
8. **Rate Limiting**: Implement backoff strategies for API calls
9. **Caching**: Cache responses for frequently asked questions
10. **Monitoring**: Track token usage for cost management

## Common Patterns

### Factory Pattern for Multiple Assistants
```java
public class AssistantFactory {
    static JavaExpert createJavaExpert() {
        return AiServices.create(JavaExpert.class, chatModel);
    }
    
    static PythonExpert createPythonExpert() {
        return AiServices.create(PythonExpert.class, chatModel);
    }
}
```

### Decorator Pattern for Enhanced Functionality
```java
public class LoggingAssistant implements Assistant {
    private final Assistant delegate;
    
    public String chat(String message) {
        logger.info("User: " + message);
        String response = delegate.chat(message);
        logger.info("Assistant: " + response);
        return response;
    }
}
```

### Builder Pattern for Complex Configurations
```java
var assistant = AiServices.builder(ComplexAssistant.class)
    .chatModel(getChatModel())
    .chatMemory(getMemory())
    .tools(getTool1(), getTool2())
    .contentRetriever(getRetriever())
    .build();
```

## Resources

- [LangChain4j Documentation](https://docs.langchain4j.dev)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [LangChain4j GitHub](https://github.com/langchain4j/langchain4j)
- [LangChain4j Examples](https://github.com/langchain4j/langchain4j-examples)
