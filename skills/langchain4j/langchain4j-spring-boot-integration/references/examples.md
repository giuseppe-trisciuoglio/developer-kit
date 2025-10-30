# LangChain4j Spring Boot Integration - Examples

Comprehensive implementation examples for Spring Boot integration with LangChain4j.

## Basic Setup Example

### Complete Spring Boot Application

```java
@SpringBootApplication
public class Langchain4jApplication {

    public static void main(String[] args) {
        SpringApplication.run(Langchain4jApplication.class, args);
    }
}

@Configuration
public class AiConfiguration {

    @Bean
    @Profile("openai")
    public ChatModel openAiChatModel(@Value("${langchain4j.open-ai.chat-model.api-key}") String apiKey) {
        return OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName("gpt-4o-mini")
                .temperature(0.7)
                .maxTokens(1000)
                .logRequests(true)
                .logResponses(true)
                .build();
    }

    @Bean
    public EmbeddingModel openAiEmbeddingModel(@Value("${langchain4j.open-ai.embedding-model.api-key}") String apiKey) {
        return OpenAiEmbeddingModel.builder()
                .apiKey(apiKey)
                .modelName("text-embedding-3-small")
                .dimensions(1536)
                .build();
    }
}

@AiService
interface CustomerSupportAssistant {

    @SystemMessage("You are a helpful customer support agent for TechCorp. " +
                  "Be polite, professional, and try to resolve customer issues efficiently. " +
                  "If you cannot resolve an issue, escalate to a human agent.")
    String handleInquiry(String customerMessage);

    @UserMessage("Analyze this customer feedback and extract sentiment: {{feedback}}")
    @SystemMessage("Return only: POSITIVE, NEGATIVE, or NEUTRAL")
    String analyzeSentiment(String feedback);

    @UserMessage("Extract key entities from this text: {{text}}")
    @SystemMessage("Return a JSON object with entities as keys and their types as values")
    String extractEntities(String text);
}

@RestController
@RequestMapping("/api/support")
@RequiredArgsConstructor
public class CustomerSupportController {

    private final CustomerSupportAssistant assistant;

    @PostMapping("/inquiry")
    public ResponseEntity<SupportResponse> handleInquiry(@RequestBody @Valid SupportRequest request) {
        String response = assistant.handleInquiry(request.getMessage());
        return ResponseEntity.ok(new SupportResponse(response, Instant.now()));
    }

    @PostMapping("/sentiment")
    public ResponseEntity<SentimentResponse> analyzeSentiment(@RequestBody @Valid SentimentRequest request) {
        String sentiment = assistant.analyzeSentiment(request.getFeedback());
        return ResponseEntity.ok(new SentimentResponse(sentiment, Instant.now()));
    }

    @PostMapping("/entities")
    public ResponseEntity<EntitiesResponse> extractEntities(@RequestBody @Valid EntitiesRequest request) {
        String entities = assistant.extractEntities(request.getText());
        return ResponseEntity.ok(new EntitiesResponse(entities, Instant.now()));
    }
}

// DTO Classes
record SupportRequest(String message) {}
record SupportResponse(String response, Instant timestamp) {}

record SentimentRequest(String feedback) {}
record SentimentResponse(String sentiment, Instant timestamp) {}

record EntitiesRequest(String text) {}
record EntitiesResponse(String entities, Instant timestamp) {}
```

## 2. Custom AI Service Bean Configuration

**Scenario**: Configure AI services as Spring beans.

```java
@Configuration
public class AiConfig {
    
    @Bean
    public ChatModel chatModel() {
        return OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.7)
            .build();
    }
    
    @Bean
    public EmbeddingModel embeddingModel() {
        return OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .build();
    }
    
    @Bean
    public DocumentAssistant documentAssistant(ChatModel chatModel) {
        return AiServices.builder(DocumentAssistant.class)
            .chatModel(chatModel)
            .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
            .build();
    }
}

interface DocumentAssistant {
    String chat(String message);
}
```

## 3. REST API with AI Service

**Scenario**: Expose AI functionality via REST endpoints.

```java
@RestController
@RequestMapping("/api/chat")
public class ChatController {
    
    private final ChatAssistant assistant;
    
    @Autowired
    public ChatController(ChatAssistant assistant) {
        this.assistant = assistant;
    }
    
    @PostMapping
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        try {
            String response = assistant.chat(request.getMessage());
            return ResponseEntity.ok(new ChatResponse(response));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                .body(new ChatResponse("Error: " + e.getMessage()));
        }
    }
    
    @PostMapping("/stream")
    public ResponseEntity<StreamingResponseBody> streamChat(@RequestBody ChatRequest request) {
        return ResponseEntity.ok(outputStream -> {
            var streamAssistant = streamingAssistant;
            var stream = streamAssistant.streamChat(request.getMessage());
            
            stream.onNext(token -> {
                try {
                    outputStream.write(token.getBytes());
                    outputStream.flush();
                } catch (IOException e) {
                    // Handle write error
                }
            }).start();
        });
    }
}

@Data
class ChatRequest {
    private String message;
}

@Data
class ChatResponse {
    private String response;
}
```

## 4. Service with RAG Integration

**Scenario**: Service layer with document search and retrieval.

```java
@Service
public class KnowledgeBaseService {
    
    private final DocumentAssistant assistant;
    private final EmbeddingStore<TextSegment> embeddingStore;
    private final EmbeddingModel embeddingModel;
    
    @Autowired
    public KnowledgeBaseService(
            DocumentAssistant assistant,
            EmbeddingStore<TextSegment> embeddingStore,
            EmbeddingModel embeddingModel) {
        this.assistant = assistant;
        this.embeddingStore = embeddingStore;
        this.embeddingModel = embeddingModel;
    }
    
    public void ingestDocument(String content, Map<String, Object> metadata) {
        var document = Document.from(content);
        document.metadata().putAll(metadata);
        
        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .documentSplitter(DocumentSplitters.recursive(500, 50))
            .build();
        
        ingestor.ingest(document);
    }
    
    public String answerQuestion(String question) {
        return assistant.answerAbout(question);
    }
}

interface DocumentAssistant {
    String answerAbout(String question);
}
```

## 5. Scheduled Task for Document Updates

**Scenario**: Periodically update knowledge base.

```java
@Service
public class DocumentUpdateService {
    
    private final EmbeddingStore<TextSegment> embeddingStore;
    private final EmbeddingModel embeddingModel;
    
    @Autowired
    public DocumentUpdateService(
            EmbeddingStore<TextSegment> embeddingStore,
            EmbeddingModel embeddingModel) {
        this.embeddingStore = embeddingStore;
        this.embeddingModel = embeddingModel;
    }
    
    @Scheduled(fixedRate = 86400000)  // Daily
    public void updateDocuments() {
        var documents = fetchLatestDocuments();
        
        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();
        
        documents.forEach(ingestor::ingest);
        logger.info("Documents updated successfully");
    }
    
    private List<Document> fetchLatestDocuments() {
        // Fetch from database or external API
        return Collections.emptyList();
    }
}
```

## 6. Controller with Tool Integration

**Scenario**: AI service with business logic tools.

```java
@Service
public class BusinessLogicService {
    
    @Tool("Get user by ID")
    public User getUser(@P("user ID") String userId) {
        // Implementation
        return new User(userId);
    }
    
    @Tool("Calculate discount")
    public double calculateDiscount(@P("purchase amount") double amount) {
        if (amount > 1000) return 0.15;
        if (amount > 500) return 0.10;
        return 0.05;
    }
}

@Service
public class ToolAssistant {
    
    private final ChatModel chatModel;
    private final BusinessLogicService businessLogic;
    
    @Autowired
    public ToolAssistant(ChatModel chatModel, BusinessLogicService businessLogic) {
        this.chatModel = chatModel;
        this.businessLogic = businessLogic;
    }
    
    public String processRequest(String request) {
        return AiServices.builder(Assistant.class)
            .chatModel(chatModel)
            .tools(businessLogic)
            .build()
            .chat(request);
    }
}

interface Assistant {
    String chat(String message);
}
```

## 7. Error Handling with Spring Exception Handler

**Scenario**: Centralized error handling for AI services.

```java
@ControllerAdvice
public class AiExceptionHandler {
    
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleBadRequest(IllegalArgumentException e) {
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("Invalid input: " + e.getMessage()));
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleError(Exception e) {
        logger.error("Error in AI service", e);
        return ResponseEntity.internalServerError()
            .body(new ErrorResponse("An error occurred: " + e.getMessage()));
    }
}

@Data
class ErrorResponse {
    private String message;
}
```

## 8. Configuration Properties

**Scenario**: Externalize AI configuration.

```java
@Configuration
@ConfigurationProperties(prefix = "app.ai")
@Data
public class AiProperties {
    private String openaiApiKey;
    private String openaiModel = "gpt-4o-mini";
    private double temperature = 0.7;
    private int maxTokens = 2000;
    private String embeddingModel = "text-embedding-3-small";
    private int memorySize = 10;
    private String vectorStoreType = "in-memory";
}

// application.yml
app:
  ai:
    openai-api-key: ${OPENAI_API_KEY}
    openai-model: gpt-4o-mini
    temperature: 0.7
    max-tokens: 2000
    embedding-model: text-embedding-3-small
    memory-size: 10
    vector-store-type: pinecone
```

## 9. Integration Testing

**Scenario**: Test AI services with Spring Boot Test.

```java
@SpringBootTest
class ChatServiceTest {
    
    @MockBean
    private ChatModel chatModel;
    
    @Autowired
    private ChatService chatService;
    
    @Test
    void testChat() {
        when(chatModel.chat("Hello"))
            .thenReturn("Hi there!");
        
        String response = chatService.chat("Hello");
        assertEquals("Hi there!", response);
    }
}
```

## 10. Async Processing with CompletableFuture

**Scenario**: Non-blocking AI service calls.

```java
@Service
@EnableAsync
public class AsyncChatService {
    
    private final ChatModel chatModel;
    
    @Autowired
    public AsyncChatService(ChatModel chatModel) {
        this.chatModel = chatModel;
    }
    
    @Async
    public CompletableFuture<String> chatAsync(String message) {
        try {
            String response = chatModel.chat(message);
            return CompletableFuture.completedFuture(response);
        } catch (Exception e) {
            return CompletableFuture.failedFuture(e);
        }
    }
}

// Usage in controller
@RestController
public class AsyncController {
    
    @Autowired
    private AsyncChatService asyncChatService;
    
    @PostMapping("/chat/async")
    public CompletableFuture<ResponseEntity<String>> chatAsync(@RequestBody ChatRequest request) {
        return asyncChatService.chatAsync(request.getMessage())
            .thenApply(ResponseEntity::ok)
            .exceptionally(e -> ResponseEntity.internalServerError().build());
    }
}
```

## Configuration Examples

### Maven Dependency
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>0.27.0</version>
</dependency>
```

### Gradle
```gradle
implementation 'dev.langchain4j:langchain4j-spring-boot-starter:0.27.0'
```
