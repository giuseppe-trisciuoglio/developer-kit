---
name: langchain4j-spring-boot-integration
description: Comprehensive guide for integrating LangChain4j with Spring Boot applications including auto-configuration, AI Services, chat models, embedding stores, and production patterns
category: ai-development
tags: [langchain4j, spring-boot, ai, llm, rag, chatbot, integration, configuration, java]
version: 1.0.0
context7_library: /langchain4j/langchain4j
context7_trust_score: 7.8
language: en
license: See LICENSE
---

# LangChain4j Spring Boot Integration

This skill provides comprehensive guidance for integrating LangChain4j with Spring Boot applications, covering auto-configuration, declarative AI Services, chat models, embedding stores, and production-ready patterns for building AI-powered applications.

## When to Use This Skill

Use this skill when:
- Integrating LangChain4j into existing Spring Boot applications
- Building AI-powered microservices with Spring Boot
- Setting up auto-configuration for AI models and services
- Creating declarative AI Services with Spring dependency injection
- Configuring multiple AI providers (OpenAI, Azure, Ollama, etc.)
- Implementing RAG systems with Spring Boot
- Setting up observability and monitoring for AI components
- Building production-ready AI applications with Spring Boot
- Creating chat interfaces and REST APIs for AI services
- Managing AI service lifecycles with Spring context

## Core Concepts

### Auto-Configuration and Starters

LangChain4j provides Spring Boot starters that enable automatic configuration of AI components based on properties.

**Core Dependencies:**

Maven (Core LangChain4j):
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

Maven (OpenAI Integration):
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

Maven (Azure OpenAI Integration):
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-azure-open-ai-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

Maven (Anthropic Integration):
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-anthropic-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

Gradle:
```groovy
implementation 'dev.langchain4j:langchain4j-spring-boot-starter:1.7.0'
implementation 'dev.langchain4j:langchain4j-open-ai-spring-boot-starter:1.7.0'
implementation 'dev.langchain4j:langchain4j-azure-open-ai-spring-boot-starter:1.7.0'
```

### Declarative AI Services

The most powerful feature of LangChain4j Spring Boot integration is declarative AI Services using interfaces.

**Basic AI Service:**
```java
@AiService
interface CustomerSupportAssistant {

    @SystemMessage("You are a helpful customer support agent for TechCorp. " +
                  "Be polite, professional, and try to resolve customer issues efficiently.")
    String handleInquiry(String customerMessage);

    @UserMessage("Analyze this customer feedback and extract sentiment: {{feedback}}")
    @SystemMessage("Return only: POSITIVE, NEGATIVE, or NEUTRAL")
    String analyzeSentiment(String feedback);
}

@RestController
@RequestMapping("/api/support")
@RequiredArgsConstructor
public class CustomerSupportController {

    private final CustomerSupportAssistant assistant;

    @PostMapping("/inquiry")
    public ResponseEntity<String> handleInquiry(@RequestBody String message) {
        String response = assistant.handleInquiry(message);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/sentiment")
    public ResponseEntity<String> analyzeSentiment(@RequestBody String feedback) {
        String sentiment = assistant.analyzeSentiment(feedback);
        return ResponseEntity.ok(sentiment);
    }
}
```

**Streaming AI Service:**
```java
@AiService
interface StreamingAssistant {

    @SystemMessage("You are a helpful assistant that provides detailed explanations.")
    Flux<String> chatStream(String userMessage);
}

@RestController
@RequiredArgsConstructor
public class StreamingChatController {

    private final StreamingAssistant assistant;

    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> streamChat(@RequestBody String message) {
        return assistant.chatStream(message);
    }
}
```

### Configuration Properties

**OpenAI Configuration:**
```properties
# application.properties

# Mandatory OpenAI Chat Model properties
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.chat-model.model-name=gpt-4o-mini

# Optional properties
langchain4j.open-ai.chat-model.temperature=0.7
langchain4j.open-ai.chat-model.max-tokens=1000
langchain4j.open-ai.chat-model.log-requests=true
langchain4j.open-ai.chat-model.log-responses=true
langchain4j.open-ai.chat-model.timeout=PT60S
langchain4j.open-ai.chat-model.max-retries=3

# OpenAI Embedding Model
langchain4j.open-ai.embedding-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.embedding-model.model-name=text-embedding-3-small
langchain4j.open-ai.embedding-model.dimensions=1536

# OpenAI Streaming Chat Model
langchain4j.open-ai.streaming-chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.streaming-chat-model.model-name=gpt-4o-mini

# OpenAI Moderation Model
langchain4j.open-ai.moderation-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.moderation-model.model-name=text-moderation-stable
```

**Azure OpenAI Configuration:**
```properties
# Azure OpenAI Chat Model
langchain4j.azure-open-ai.chat-model.endpoint=${AZURE_OPENAI_ENDPOINT}
langchain4j.azure-open-ai.chat-model.api-key=${AZURE_OPENAI_KEY}
langchain4j.azure-open-ai.chat-model.deployment-name=gpt-4o
langchain4j.azure-open-ai.chat-model.service-version=2024-02-15-preview
langchain4j.azure-open-ai.chat-model.temperature=0.7
langchain4j.azure-open-ai.chat-model.max-tokens=1000
langchain4j.azure-open-ai.chat-model.log-requests-and-responses=true

# Azure OpenAI Embedding Model
langchain4j.azure-open-ai.embedding-model.endpoint=${AZURE_OPENAI_ENDPOINT}
langchain4j.azure-open-ai.embedding-model.api-key=${AZURE_OPENAI_KEY}
langchain4j.azure-open-ai.embedding-model.deployment-name=text-embedding-3-small
langchain4j.azure-open-ai.embedding-model.dimensions=1536

# Azure OpenAI Streaming Chat Model
langchain4j.azure-open-ai.streaming-chat-model.endpoint=${AZURE_OPENAI_ENDPOINT}
langchain4j.azure-open-ai.streaming-chat-model.api-key=${AZURE_OPENAI_KEY}
langchain4j.azure-open-ai.streaming-chat-model.deployment-name=gpt-4o
```

**Ollama Configuration:**
```properties
# Ollama Chat Model (for local models)
langchain4j.ollama.chat-model.base-url=http://localhost:11434
langchain4j.ollama.chat-model.model-name=llama3.1
langchain4j.ollama.chat-model.temperature=0.8
langchain4j.ollama.chat-model.timeout=PT60S
```

**Anthropic Configuration:**
```properties
# Anthropic Chat Model
langchain4j.anthropic.chat-model.api-key=${ANTHROPIC_API_KEY}
langchain4j.anthropic.chat-model.model-name=claude-3-5-sonnet-20241022

# Anthropic Streaming Chat Model
langchain4j.anthropic.streaming-chat-model.api-key=${ANTHROPIC_API_KEY}
langchain4j.anthropic.streaming-chat-model.model-name=claude-3-5-sonnet-20241022
```

### Manual Bean Configuration

For advanced configurations, you can manually define beans:

**Custom OpenAI Configuration:**
```java
@Configuration
@Profile("openai")
public class OpenAiConfiguration {

    @Bean
    @Primary
    public ChatModel openAiChatModel(@Value("${openai.api.key}") String apiKey) {
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
    public EmbeddingModel openAiEmbeddingModel(@Value("${openai.api.key}") String apiKey) {
        return OpenAiEmbeddingModel.builder()
                .apiKey(apiKey)
                .modelName("text-embedding-3-small")
                .dimensions(1536)
                .build();
    }

    @Bean
    public StreamingChatModel openAiStreamingChatModel(@Value("${openai.api.key}") String apiKey) {
        return OpenAiStreamingChatModel.builder()
                .apiKey(apiKey)
                .modelName("gpt-4o-mini")
                .temperature(0.7)
                .build();
    }
}
```

**Multiple Providers Configuration:**
```java
@Configuration
public class MultiProviderConfiguration {

    @Bean("openAiChatModel")
    public ChatModel openAiChatModel(@Value("${openai.api.key}") String apiKey) {
        return OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName("gpt-4o-mini")
                .build();
    }

    @Bean("ollamaChatModel")
    public ChatModel ollamaChatModel() {
        return OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("llama3.1")
                .build();
    }

    @Bean("anthropicChatModel")
    public ChatModel anthropicChatModel(@Value("${anthropic.api.key}") String apiKey) {
        return AnthropicChatModel.builder()
                .apiKey(apiKey)
                .modelName("claude-3-5-sonnet-20241022")
                .build();
    }
}
```

### Explicit Component Wiring

When using multiple AI models, specify which model to use with explicit wiring:

```java
@AiService(wiringMode = EXPLICIT, chatModel = "openAiChatModel")
interface OpenAiAssistant {
    @SystemMessage("You are an OpenAI-powered assistant")
    String chat(String userMessage);
}

@AiService(wiringMode = EXPLICIT, chatModel = "ollamaChatModel")
interface OllamaAssistant {
    @SystemMessage("You are a locally-hosted Ollama assistant")
    String chat(String userMessage);
}

@AiService(wiringMode = EXPLICIT, chatModel = "anthropicChatModel")
interface AnthropicAssistant {
    @SystemMessage("You are a Claude-powered assistant")
    String chat(String userMessage);
}
```

## RAG Implementation Patterns

### Embedding Store Configuration

**PostgreSQL with pgvector:**
```java
@Configuration
public class EmbeddingStoreConfiguration {

    @Bean
    public EmbeddingStore<TextSegment> embeddingStore(
            @Value("${spring.datasource.url}") String url,
            @Value("${spring.datasource.username}") String username,
            @Value("${spring.datasource.password}") String password) {
        return PgVectorEmbeddingStore.builder()
                .host("localhost")
                .port(5432)
                .database("ai_knowledge_base")
                .user(username)
                .password(password)
                .table("documents")
                .dimension(1536)
                .build();
    }

    @Bean
    public ContentRetriever contentRetriever(EmbeddingStore<TextSegment> embeddingStore,
                                           EmbeddingModel embeddingModel) {
        return EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(5)
                .minScore(0.7)
                .build();
    }
}
```

**Neo4j Configuration (application.properties):**
```properties
# Neo4j Embedding Store
langchain4j.community.neo4j.dimension=1536
langchain4j.community.neo4j.auth.uri=bolt://localhost:7687
langchain4j.community.neo4j.auth.user=neo4j
langchain4j.community.neo4j.auth.password=password
langchain4j.community.neo4j.label=Document
langchain4j.community.neo4j.indexName=documentIndex
langchain4j.community.neo4j.embeddingProperty=embedding
langchain4j.community.neo4j.textProperty=text
langchain4j.community.neo4j.idProperty=id
```

**RAG-Enabled AI Service:**
```java
@Configuration
public class RagConfiguration {

    @Bean
    public ContentRetriever contentRetriever(EmbeddingStore<TextSegment> embeddingStore,
                                           EmbeddingModel embeddingModel) {
        return EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(5)
                .minScore(0.6)
                .build();
    }
}

interface KnowledgeAssistant {

    @SystemMessage("Answer the question based on the provided context. " +
                  "If the context doesn't contain relevant information, say so clearly.")
    String answerQuestion(String question);
}

@Service
@RequiredArgsConstructor
public class KnowledgeService {

    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;
    private final ChatModel chatModel;

    @PostConstruct
    public void init() {
        ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(5)
                .minScore(0.7)
                .build();

        KnowledgeAssistant assistant = AiServices.builder(KnowledgeAssistant.class)
                .chatLanguageModel(chatModel)
                .contentRetriever(retriever)
                .build();
    }
}
```

### Document Ingestion Service

```java
@Service
@RequiredArgsConstructor
public class DocumentIngestionService {

    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;

    public void ingestDocument(MultipartFile file) {
        try {
            // Load document
            Document document = loadDocument(file);

            // Split into segments
            DocumentSplitter splitter = DocumentSplitters.recursive(500, 50);
            List<TextSegment> segments = splitter.split(document);

            // Generate embeddings and store
            List<Embedding> embeddings = embeddingModel.embedAll(segments).content();
            embeddingStore.addAll(embeddings, segments);

            log.info("Successfully ingested document: {} ({} segments)",
                    file.getOriginalFilename(), segments.size());
        } catch (Exception e) {
            log.error("Error ingesting document: {}", e.getMessage(), e);
            throw new DocumentIngestionException("Failed to ingest document", e);
        }
    }

    private Document loadDocument(MultipartFile file) throws IOException {
        String content = new String(file.getBytes(), StandardCharsets.UTF_8);
        Map<String, Object> metadata = Map.of(
                "filename", file.getOriginalFilename(),
                "size", file.getSize(),
                "contentType", file.getContentType(),
                "uploadedAt", Instant.now()
        );
        return Document.from(content, metadata);
    }
}
```

## Tool Integration Patterns

### Defining Tools as Spring Components

```java
@Component
public class WeatherTools {

    private final WeatherApiClient weatherApiClient;

    public WeatherTools(WeatherApiClient weatherApiClient) {
        this.weatherApiClient = weatherApiClient;
    }

    @Tool("Get current weather for a city")
    public String getCurrentWeather(@P("City name") String city) {
        try {
            WeatherData weather = weatherApiClient.getCurrentWeather(city);
            return String.format("Current weather in %s: %s, %.1f°C",
                    city, weather.getDescription(), weather.getTemperature());
        } catch (Exception e) {
            return "Sorry, I couldn't retrieve weather information for " + city;
        }
    }

    @Tool("Get weather forecast for next 7 days")
    public String getWeatherForecast(@P("City name") String city) {
        try {
            List<WeatherForecast> forecasts = weatherApiClient.getForecast(city, 7);
            return formatForecast(city, forecasts);
        } catch (Exception e) {
            return "Sorry, I couldn't retrieve forecast information for " + city;
        }
    }

    private String formatForecast(String city, List<WeatherForecast> forecasts) {
        StringBuilder result = new StringBuilder();
        result.append("7-day forecast for ").append(city).append(":\n");
        for (WeatherForecast forecast : forecasts) {
            result.append(String.format("%s: %s, %.1f°C\n",
                    forecast.getDate(), forecast.getDescription(), forecast.getTemperature()));
        }
        return result.toString();
    }
}

@AiService
interface WeatherAssistant {

    @SystemMessage("You are a weather assistant. Use the available tools to provide accurate weather information.")
    String chat(String userMessage);
}
```

### Database Access Tools

```java
@Component
@RequiredArgsConstructor
public class CustomerTools {

    private final CustomerRepository customerRepository;
    private final OrderRepository orderRepository;

    @Tool("Find customer by email address")
    public String findCustomerByEmail(@P("Customer email address") String email) {
        return customerRepository.findByEmail(email)
                .map(customer -> String.format("Customer: %s %s (ID: %d, Email: %s)",
                        customer.getFirstName(), customer.getLastName(),
                        customer.getId(), customer.getEmail()))
                .orElse("Customer not found with email: " + email);
    }

    @Tool("Get customer order history")
    public String getCustomerOrders(@P("Customer ID") Long customerId) {
        List<Order> orders = orderRepository.findByCustomerId(customerId);
        if (orders.isEmpty()) {
            return "No orders found for customer ID: " + customerId;
        }

        StringBuilder result = new StringBuilder();
        result.append("Order history for customer ID ").append(customerId).append(":\n");
        for (Order order : orders) {
            result.append(String.format("Order #%d: %s, Total: $%.2f\n",
                    order.getId(), order.getStatus(), order.getTotal()));
        }
        return result.toString();
    }

    @Tool("Cancel customer order")
    public String cancelOrder(@P("Order ID") Long orderId, @P("Cancellation reason") String reason) {
        return orderRepository.findById(orderId)
                .map(order -> {
                    if (order.getStatus() == OrderStatus.CANCELLED) {
                        return "Order #" + orderId + " is already cancelled";
                    }
                    if (order.getStatus() == OrderStatus.SHIPPED) {
                        return "Cannot cancel order #" + orderId + " - already shipped";
                    }

                    order.setStatus(OrderStatus.CANCELLED);
                    order.setCancellationReason(reason);
                    orderRepository.save(order);
                    return "Order #" + orderId + " has been cancelled successfully";
                })
                .orElse("Order not found with ID: " + orderId);
    }
}
```

## Memory and Context Management

### Chat Memory Configuration

```java
@Configuration
public class MemoryConfiguration {

    @Bean
    public ChatMemoryStore chatMemoryStore() {
        // In-memory store for development
        return new InMemoryChatMemoryStore();
    }

    @Bean
    public ChatMemoryProvider chatMemoryProvider(ChatMemoryStore memoryStore) {
        return memoryId -> MessageWindowChatMemory.builder()
                .id(memoryId)
                .maxMessages(20)
                .chatMemoryStore(memoryStore)
                .build();
    }
}

@Service
@RequiredArgsConstructor
public class ConversationalService {

    private final ChatModel chatModel;
    private final ChatMemoryProvider memoryProvider;

    public String chat(String userId, String message) {
        ChatMemory memory = memoryProvider.get(userId);

        ConversationalRetrievalChain chain = ConversationalRetrievalChain.builder()
                .chatLanguageModel(chatModel)
                .chatMemory(memory)
                .build();

        return chain.execute(message);
    }
}
```

### Persistent Memory with Database

```java
@Entity
@Table(name = "chat_messages")
@RequiredArgsConstructor
@NoArgsConstructor
public class ChatMessageEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "memory_id", nullable = false)
    private String memoryId;

    @Column(name = "message_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private MessageType messageType;

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    // getters and setters
}

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessageEntity, Long> {
    List<ChatMessageEntity> findByMemoryIdOrderByCreatedAtAsc(String memoryId);
    void deleteByMemoryId(String memoryId);
}

@Component
@RequiredArgsConstructor
public class DatabaseChatMemoryStore implements ChatMemoryStore {

    private final ChatMessageRepository repository;

    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        return repository.findByMemoryIdOrderByCreatedAtAsc(memoryId.toString())
                .stream()
                .map(this::toMessage)
                .collect(Collectors.toList());
    }

    @Override
    public void updateMessages(Object memoryId, List<ChatMessage> messages) {
        String id = memoryId.toString();
        repository.deleteByMemoryId(id);

        List<ChatMessageEntity> entities = messages.stream()
                .map(msg -> toEntity(id, msg))
                .collect(Collectors.toList());

        repository.saveAll(entities);
    }

    @Override
    public void deleteMessages(Object memoryId) {
        repository.deleteByMemoryId(memoryId.toString());
    }

    private ChatMessage toMessage(ChatMessageEntity entity) {
        return switch (entity.getMessageType()) {
            case USER -> UserMessage.from(entity.getContent());
            case AI -> AiMessage.from(entity.getContent());
            case SYSTEM -> SystemMessage.from(entity.getContent());
        };
    }

    private ChatMessageEntity toEntity(String memoryId, ChatMessage message) {
        ChatMessageEntity entity = new ChatMessageEntity();
        entity.setMemoryId(memoryId);
        entity.setContent(message.text());
        entity.setCreatedAt(LocalDateTime.now());

        if (message instanceof UserMessage) {
            entity.setMessageType(MessageType.USER);
        } else if (message instanceof AiMessage) {
            entity.setMessageType(MessageType.AI);
        } else if (message instanceof SystemMessage) {
            entity.setMessageType(MessageType.SYSTEM);
        }

        return entity;
    }
}
```

## Observability and Monitoring

### ChatModel Listeners

```java
@Configuration
public class ObservabilityConfiguration {

    @Bean
    public ChatModelListener chatModelListener() {
        return new ChatModelListener() {

            private static final Logger log = LoggerFactory.getLogger(ChatModelListener.class);

            @Override
            public void onRequest(ChatModelRequestContext requestContext) {
                log.info("AI Request - Model: {}, Messages: {}, Tokens: {}",
                        requestContext.model().getClass().getSimpleName(),
                        requestContext.request().messages().size(),
                        countTokens(requestContext.request()));
            }

            @Override
            public void onResponse(ChatModelResponseContext responseContext) {
                Response<AiMessage> response = responseContext.response();
                log.info("AI Response - Tokens: {}, Finish Reason: {}, Duration: {}ms",
                        response.tokenUsage().totalTokenCount(),
                        response.finishReason(),
                        responseContext.duration().toMillis());
            }

            @Override
            public void onError(ChatModelErrorContext errorContext) {
                log.error("AI Error - Model: {}, Error: {}, Duration: {}ms",
                        errorContext.model().getClass().getSimpleName(),
                        errorContext.error().getMessage(),
                        errorContext.duration().toMillis());
            }

            private int countTokens(ChatRequest request) {
                return request.messages().stream()
                        .mapToInt(msg -> msg.text().length() / 4) // Rough estimation
                        .sum();
            }
        };
    }
}
```

### Metrics and Health Checks

```java
@Component
@RequiredArgsConstructor
public class AiHealthIndicator implements HealthIndicator {

    private final ChatModel chatModel;

    @Override
    public Health health() {
        try {
            String response = chatModel.chat("ping");
            if (response != null && !response.trim().isEmpty()) {
                return Health.up()
                        .withDetail("model", chatModel.getClass().getSimpleName())
                        .withDetail("response_time", measureResponseTime())
                        .build();
            }
        } catch (Exception e) {
            return Health.down()
                    .withDetail("model", chatModel.getClass().getSimpleName())
                    .withDetail("error", e.getMessage())
                    .build();
        }

        return Health.down()
                .withDetail("model", chatModel.getClass().getSimpleName())
                .withDetail("reason", "Empty response")
                .build();
    }

    private long measureResponseTime() {
        long start = System.currentTimeMillis();
        try {
            chatModel.chat("ping");
        } catch (Exception ignored) {
        }
        return System.currentTimeMillis() - start;
    }
}

@Component
@RequiredArgsConstructor
public class AiMetrics {

    private final MeterRegistry meterRegistry;
    private final Counter requestCounter;
    private final Timer responseTimer;

    public AiMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestCounter = Counter.builder("ai.requests.total")
                .description("Total AI requests")
                .register(meterRegistry);
        this.responseTimer = Timer.builder("ai.response.duration")
                .description("AI response time")
                .register(meterRegistry);
    }

    public void recordRequest() {
        requestCounter.increment();
    }

    public void recordResponse(Duration duration) {
        responseTimer.record(duration);
    }
}
```

## Event Handling

### AI Service Registration Events

```java
@Component
@Slf4j
public class AiServiceRegistrationListener implements ApplicationListener<AiServiceRegisteredEvent> {

    @Override
    public void onApplicationEvent(AiServiceRegisteredEvent event) {
        Class<?> serviceClass = event.aiServiceClass();
        List<ToolSpecification> tools = event.toolSpecifications();

        log.info("Registered AI Service: {}", serviceClass.getSimpleName());
        log.info("Available Tools: {}", tools.size());

        for (int i = 0; i < tools.size(); i++) {
            ToolSpecification tool = tools.get(i);
            log.info("  Tool {}: {} - {}", i + 1, tool.name(), tool.description());
        }
    }
}
```

### Custom Application Events

```java
@Getter
@AllArgsConstructor
public class DocumentIngestedEvent extends ApplicationEvent {
    private final String documentId;
    private final String filename;
    private final int segmentCount;
    private final Instant timestamp;

    public DocumentIngestedEvent(Object source, String documentId, String filename, int segmentCount) {
        super(source);
        this.documentId = documentId;
        this.filename = filename;
        this.segmentCount = segmentCount;
        this.timestamp = Instant.now();
    }
}

@EventListener
@Component
@Slf4j
public class DocumentEventHandler {

    @EventListener
    public void handleDocumentIngested(DocumentIngestedEvent event) {
        log.info("Document ingested: {} ({} segments) at {}",
                event.getFilename(),
                event.getSegmentCount(),
                event.getTimestamp());

        // Additional processing like notifications, indexing, etc.
    }
}
```

## Production Patterns

### Error Handling and Resilience

```java
@ControllerAdvice
public class AiExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(AiExceptionHandler.class);

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ErrorResponse> handleAiException(RuntimeException ex) {
        log.error("AI service error: {}", ex.getMessage(), ex);

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .error("AI Service Error")
                .message("The AI service is temporarily unavailable. Please try again later.")
                .build();

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleValidationError(IllegalArgumentException ex) {
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error("Validation Error")
                .message(ex.getMessage())
                .build();

        return ResponseEntity.badRequest().body(error);
    }
}

@Service
@RequiredArgsConstructor
public class ResilientAiService {

    private final ChatModel primaryModel;
    private final ChatModel fallbackModel;

    @Retryable(value = {RuntimeException.class}, maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public String chat(String message) {
        try {
            return primaryModel.chat(message);
        } catch (Exception e) {
            log.warn("Primary model failed, trying fallback: {}", e.getMessage());
            return fallbackModel.chat(message);
        }
    }

    @Recover
    public String recover(RuntimeException ex, String message) {
        log.error("All AI models failed for message: {}", message, ex);
        return "I'm sorry, I'm experiencing technical difficulties. Please try again later.";
    }
}
```

### Configuration Validation

```java
@Configuration
@ConfigurationProperties(prefix = "app.ai")
@Validated
public class AiConfigurationProperties {

    @NotBlank(message = "OpenAI API key is required")
    private String openaiApiKey;

    @NotBlank(message = "Model name is required")
    private String modelName = "gpt-4o-mini";

    @DecimalMin(value = "0.0", message = "Temperature must be >= 0.0")
    @DecimalMax(value = "2.0", message = "Temperature must be <= 2.0")
    private Double temperature = 0.7;

    @Min(value = 1, message = "Max tokens must be >= 1")
    @Max(value = 8192, message = "Max tokens must be <= 8192")
    private Integer maxTokens = 1000;

    private Boolean logRequests = false;
    private Boolean logResponses = false;

    // getters and setters
}

@Component
@RequiredArgsConstructor
@Slf4j
public class AiConfigurationValidator implements InitializingBean {

    private final AiConfigurationProperties properties;

    @Override
    public void afterPropertiesSet() {
        validateConfiguration();
    }

    private void validateConfiguration() {
        if (properties.getOpenaiApiKey() == null || properties.getOpenaiApiKey().startsWith("sk-")) {
            log.warn("OpenAI API key appears to be missing or invalid");
        }

        if (properties.getMaxTokens() > 4096 && "gpt-3.5-turbo".equals(properties.getModelName())) {
            log.warn("Max tokens {} exceeds recommended limit for model {}",
                    properties.getMaxTokens(), properties.getModelName());
        }

        log.info("AI Configuration validated successfully");
    }
}
```

## API Reference

### Common LangChain4j Spring Boot Properties

**Core Configuration:**
- `langchain4j.open-ai.chat-model.api-key`: OpenAI API key
- `langchain4j.open-ai.chat-model.model-name`: Model name (e.g., gpt-4o-mini)
- `langchain4j.open-ai.chat-model.temperature`: Sampling temperature (0.0-2.0)
- `langchain4j.open-ai.chat-model.max-tokens`: Maximum tokens to generate
- `langchain4j.open-ai.chat-model.log-requests`: Enable request logging
- `langchain4j.open-ai.chat-model.log-responses`: Enable response logging

**Embedding Configuration:**
- `langchain4j.open-ai.embedding-model.model-name`: Embedding model name
- `langchain4j.open-ai.embedding-model.dimensions`: Embedding dimensions

**Azure OpenAI Configuration:**
- `langchain4j.azure-open-ai.chat-model.endpoint`: Azure endpoint URL
- `langchain4j.azure-open-ai.chat-model.deployment-name`: Deployment name

**Anthropic Configuration:**
- `langchain4j.anthropic.chat-model.api-key`: Anthropic API key
- `langchain4j.anthropic.chat-model.model-name`: Claude model name

### Key Annotations

**LangChain4j Annotations:**
- `@AiService`: Mark interface as AI service
- `@SystemMessage`: Define system message template
- `@UserMessage`: Define user message template
- `@Tool`: Mark method as available tool
- `@P`: Parameter description for tools

**Spring Annotations:**
- `@Component`: Mark tool classes as Spring components
- `@Service`: Mark service classes
- `@Configuration`: Configuration classes
- `@Bean`: Bean definition methods
- `@Value`: Inject property values
- `@Profile`: Profile-specific beans

## Workflow Patterns

### Complete RAG Application

```java
@SpringBootApplication
@EnableJpaAuditing
public class RagApplication {

    public static void main(String[] args) {
        SpringApplication.run(RagApplication.class, args);
    }
}

@RestController
@RequestMapping("/api/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {

    private final DocumentIngestionService ingestionService;
    private final KnowledgeQueryService queryService;

    @PostMapping("/documents")
    public ResponseEntity<String> uploadDocument(@RequestParam("file") MultipartFile file) {
        try {
            String documentId = ingestionService.ingestDocument(file);
            return ResponseEntity.ok("Document uploaded successfully: " + documentId);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error uploading document: " + e.getMessage());
        }
    }

    @PostMapping("/query")
    public ResponseEntity<String> query(@RequestBody String question) {
        try {
            String answer = queryService.answer(question);
            return ResponseEntity.ok(answer);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error processing query: " + e.getMessage());
        }
    }
}
```

## Best Practices

### 1. Use Property-Based Configuration

Prefer external configuration over hardcoded values:

```properties
# Good - External configuration
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.chat-model.model-name=${AI_MODEL:gpt-4o-mini}
```

### 2. Implement Proper Error Handling

```java
@Service
@RequiredArgsConstructor
public class SafeAiService {

    private final ChatModel chatModel;

    public Optional<String> safeChat(String message) {
        try {
            String response = chatModel.chat(message);
            return Optional.ofNullable(response);
        } catch (Exception e) {
            log.error("AI service error: {}", e.getMessage(), e);
            return Optional.empty();
        }
    }
}
```

### 3. Use Profiles for Different Environments

```java
@Configuration
@Profile("development")
public class DevAiConfiguration {
    // Development-specific configuration
}

@Configuration
@Profile("production")
public class ProdAiConfiguration {
    // Production-specific configuration
}
```

### 4. Implement Proper Logging

```properties
# Enable LangChain4j debug logging
logging.level.dev.langchain4j=DEBUG
logging.level.dev.langchain4j.model.openai=INFO

# Application-specific logging
langchain4j.open-ai.chat-model.log-requests=true
langchain4j.open-ai.chat-model.log-responses=false
```

### 5. Secure API Keys

```properties
# Use environment variables
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}

# Or Spring Cloud Config
# Never commit API keys to version control
```

## Summary

This LangChain4j Spring Boot integration skill covers:

1. **Auto-Configuration**: Spring Boot starters and property-based configuration
2. **Declarative AI Services**: Interface-based AI service definitions with annotations
3. **Multiple Providers**: OpenAI, Azure OpenAI, Anthropic, Ollama integration
4. **RAG Implementation**: Embedding stores, content retrievers, document ingestion
5. **Tool Integration**: Spring component-based tools and function calling
6. **Memory Management**: Chat memory with database persistence
7. **Observability**: Listeners, metrics, health checks, and monitoring
8. **Production Patterns**: Error handling, resilience, configuration validation
9. **Event Handling**: Application events and custom event processing
10. **Best Practices**: Security, logging, profiles, and deployment patterns
