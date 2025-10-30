# LangChain4j Spring Boot Integration - Configuration Guide

Detailed configuration options and advanced setup patterns for LangChain4j with Spring Boot.

## Property-Based Configuration

### Core Configuration Properties

**application.yml**
```yaml
langchain4j:
  # OpenAI Configuration
  open-ai:
    chat-model:
      api-key: ${OPENAI_API_KEY}
      model-name: gpt-4o-mini
      temperature: 0.7
      max-tokens: 1000
      log-requests: true
      log-responses: true
      timeout: PT60S
      max-retries: 3
      organization: ${OPENAI_ORGANIZATION:}

    embedding-model:
      api-key: ${OPENAI_API_KEY}
      model-name: text-embedding-3-small
      dimensions: 1536
      timeout: PT60S

    streaming-chat-model:
      api-key: ${OPENAI_API_KEY}
      model-name: gpt-4o-mini
      temperature: 0.7
      max-tokens: 2000

  # Azure OpenAI Configuration
  azure-open-ai:
    chat-model:
      endpoint: ${AZURE_OPENAI_ENDPOINT}
      api-key: ${AZURE_OPENAI_KEY}
      deployment-name: gpt-4o
      service-version: 2024-02-15-preview
      temperature: 0.7
      max-tokens: 1000
      log-requests-and-responses: true

    embedding-model:
      endpoint: ${AZURE_OPENAI_ENDPOINT}
      api-key: ${AZURE_OPENAI_KEY}
      deployment-name: text-embedding-3-small
      dimensions: 1536

  # Anthropic Configuration
  anthropic:
    chat-model:
      api-key: ${ANTHROPIC_API_KEY}
      model-name: claude-3-5-sonnet-20241022
      max-tokens: 4000
      temperature: 0.7

    streaming-chat-model:
      api-key: ${ANTHROPIC_API_KEY}
      model-name: claude-3-5-sonnet-20241022

  # Ollama Configuration
  ollama:
    chat-model:
      base-url: http://localhost:11434
      model-name: llama3.1
      temperature: 0.8
      timeout: PT60S

  # Memory Configuration
  memory:
    store-type: in-memory  # in-memory, postgresql, mysql, mongodb
    max-messages: 20
    window-size: 10

  # Vector Store Configuration
  vector-store:
    type: in-memory  # in-memory, pinecone, weaviate, qdrant, postgresql
    pinecone:
      api-key: ${PINECONE_API_KEY}
      index-name: my-index
      namespace: production
    qdrant:
      host: localhost
      port: 6333
      collection-name: documents
    weaviate:
      host: localhost
      port: 8080
      collection-name: Documents
    postgresql:
      table: document_embeddings
      dimension: 1536
```

### Spring Profiles Configuration

**application-dev.yml**
```yaml
langchain4j:
  open-ai:
    chat-model:
      api-key: ${OPENAI_API_KEY_DEV}
      model-name: gpt-4o-mini
      temperature: 0.8  # Higher temperature for experimentation
      log-requests: true
      log-responses: true

  vector-store:
    type: in-memory
```

**application-prod.yml**
```yaml
langchain4j:
  open-ai:
    chat-model:
      api-key: ${OPENAI_API_KEY_PROD}
      model-name: gpt-4o
      temperature: 0.3  # Lower temperature for consistency
      log-requests: false
      log-responses: false

  vector-store:
    type: pinecone
    pinecone:
      api-key: ${PINECONE_API_KEY_PROD}
      index-name: production-knowledge-base
```

## Manual Bean Configuration

### Advanced Chat Model Configuration

```java
@Configuration
@Profile("custom-openai")
public class CustomOpenAiConfiguration {

    @Bean
    @Primary
    public ChatModel customOpenAiChatModel(
            @Value("${custom.openai.api.key}") String apiKey,
            @Value("${custom.openai.model}") String model,
            @Value("${custom.openai.temperature}") Double temperature) {

        OpenAiChatModelBuilder builder = OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName(model)
                .temperature(temperature);

        if (Boolean.TRUE.equals(env.getProperty("custom.openai.log-requests", Boolean.class))) {
            builder.logRequests(true);
        }
        if (Boolean.TRUE.equals(env.getProperty("custom.openai.log-responses", Boolean.class))) {
            builder.logResponses(true);
        }

        return builder.build();
    }

    @Bean
    @ConditionalOnProperty(name = "custom.openai.proxy.enabled", havingValue = "true")
    public ChatModel proxiedChatModel(ChatModel delegate) {
        return new ProxiedChatModel(delegate,
                env.getProperty("custom.openai.proxy.url"),
                env.getProperty("custom.openai.proxy.username"),
                env.getProperty("custom.openai.proxy.password"));
    }
}

class ProxiedChatModel implements ChatModel {
    private final ChatModel delegate;
    private final String proxyUrl;
    private final String username;
    private final String password;

    public ProxiedChatModel(ChatModel delegate, String proxyUrl, String username, String password) {
        this.delegate = delegate;
        this.proxyUrl = proxyUrl;
        this.username = username;
        this.password = password;
    }

    @Override
    public Response<AiMessage> generate(ChatRequest request) {
        // Apply proxy configuration
        // Make request through proxy
        return delegate.generate(request);
    }
}
```

### Multiple Provider Configuration

```java
@Configuration
public class MultiProviderConfiguration {

    @Bean("openAiChatModel")
    public ChatModel openAiChatModel(
            @Value("${openai.api.key}") String apiKey,
            @Value("${openai.model.name}") String modelName) {

        return OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName(modelName)
                .temperature(0.7)
                .logRequests(env.acceptsProfiles("dev"))
                .build();
    }

    @Bean("anthropicChatModel")
    public ChatModel anthropicChatModel(
            @Value("${anthropic.api.key}") String apiKey,
            @Value("${anthropic.model.name}") String modelName) {

        return AnthropicChatModel.builder()
                .apiKey(apiKey)
                .modelName(modelName)
                .maxTokens(4000)
                .build();
    }

    @Bean("ollamaChatModel")
    @ConditionalOnProperty(name = "ollama.enabled", havingValue = "true")
    public ChatModel ollamaChatModel(
            @Value("${ollama.base-url}") String baseUrl,
            @Value("${ollama.model.name}") String modelName) {

        return OllamaChatModel.builder()
                .baseUrl(baseUrl)
                .modelName(modelName)
                .temperature(0.8)
                .build();
    }
}
```

### Explicit Wiring Configuration

```java
@AiService(wiringMode = EXPLICIT, chatModel = "productionChatModel")
interface ProductionAssistant {
    @SystemMessage("You are a production-grade AI assistant providing high-quality, reliable responses.")
    String chat(String message);
}

@AiService(wiringMode = EXPLICIT, chatModel = "developmentChatModel")
interface DevelopmentAssistant {
    @SystemMessage("You are a development assistant helping with code and debugging. " +
                  "Be experimental and creative in your responses.")
    String chat(String message);
}

@AiService(wiringMode = EXPLICIT,
           chatModel = "specializedChatModel",
           tools = "businessTools")
interface SpecializedAssistant {
    @SystemMessage("You are a specialized assistant with access to business tools. " +
                  "Use the available tools to provide accurate information.")
    String chat(String message);
}

@Component("businessTools")
public class BusinessLogicTools {

    @Tool("Calculate discount based on customer status")
    public BigDecimal calculateDiscount(
            @P("Purchase amount") BigDecimal amount,
            @P("Customer status") String customerStatus) {

        return switch (customerStatus.toLowerCase()) {
            case "vip" -> amount.multiply(new BigDecimal("0.15"));
            case "premium" -> amount.multiply(new BigDecimal("0.10"));
            case "standard" -> amount.multiply(new BigDecimal("0.05"));
            default -> BigDecimal.ZERO;
        };
    }
}
```

## Embedding Store Configuration

### PostgreSQL with pgvector

```java
@Configuration
@RequiredArgsConstructor
public class PostgresEmbeddingStoreConfiguration {

    @Bean
    public EmbeddingStore<TextSegment> postgresEmbeddingStore(
            DataSource dataSource,
            @Value("${spring.datasource.schema}") String schema) {

        return PgVectorEmbeddingStore.builder()
                .dataSource(dataSource)
                .table("document_embeddings")
                .dimension(1536)
                .initializeSchema(true)
                .schema(schema)
                .indexName("document_embeddings_idx")
                .build();
    }

    @Bean
    public ContentRetriever postgresContentRetriever(
            EmbeddingStore<TextSegment> embeddingStore,
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

### Pinecone Configuration

```java
@Configuration
@Profile("pinecone")
public class PineconeConfiguration {

    @Bean
    public EmbeddingStore<TextSegment> pineconeEmbeddingStore(
            @Value("${pinecone.api.key}") String apiKey,
            @Value("${pinecone.index.name}") String indexName,
            @Value("${pinecone.namespace}") String namespace) {

        PineconeEmbeddingStore store = PineconeEmbeddingStore.builder()
                .apiKey(apiKey)
                .indexName(indexName)
                .namespace(namespace)
                .build();

        // Initialize if needed
        if (!store.indexExists()) {
            store.createIndex(1536);
        }

        return store;
    }
}
```

### Custom Embedding Store

```java
@Component
public class CustomEmbeddingStore implements EmbeddingStore<TextSegment> {

    private final Map<UUID, TextSegment> embeddings = new ConcurrentHashMap<>();
    private final Map<UUID, float[]> vectors = new ConcurrentHashMap<>();

    @Override
    public void add(Embedding embedding, TextSegment textSegment) {
        UUID id = UUID.randomUUID();
        embeddings.put(id, textSegment);
        vectors.put(id, embedding.vector());
    }

    @Override
    public void addAll(List<Embedding> embeddings, List<TextSegment> textSegments) {
        for (int i = 0; i < embeddings.size(); i++) {
            add(embeddings.get(i), textSegments.get(i));
        }
    }

    @Override
    public List<Embedding> findRelevant(Embedding embedding, int maxResults) {
        return vectors.entrySet().stream()
                .sorted(Comparator.comparingDouble(e -> cosineSimilarity(e.getValue(), embedding.vector())))
                .limit(maxResults)
                .map(e -> new EmbeddingImpl(e.getValue(), embeddings.get(e.getKey()).id()))
                .collect(Collectors.toList());
    }

    private double cosineSimilarity(float[] vec1, float[] vec2) {
        // Implementation of cosine similarity
        return 0.0;
    }
}
```

## Memory Configuration

### Chat Memory Store Configuration

```java
@Configuration
public class MemoryConfiguration {

    @Bean
    @Profile("in-memory")
    public ChatMemoryStore inMemoryChatMemoryStore() {
        return new InMemoryChatMemoryStore();
    }

    @Bean
    @Profile("database")
    public ChatMemoryStore databaseChatMemoryStore(ChatMessageRepository messageRepository) {
        return new DatabaseChatMemoryStore(messageRepository);
    }

    @Bean
    public ChatMemoryProvider chatMemoryProvider(ChatMemoryStore memoryStore) {
        return memoryId -> MessageWindowChatMemory.builder()
                .id(memoryId)
                .maxMessages(getMaxMessages())
                .chatMemoryStore(memoryStore)
                .build();
    }

    private int getMaxMessages() {
        return env.getProperty("langchain4j.memory.max-messages", int.class, 20);
    }
}
```

### Database Chat Memory Store

```java
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
        entity.setMessageType(determineMessageType(message));
        return entity;
    }

    private MessageType determineMessageType(ChatMessage message) {
        if (message instanceof UserMessage) return MessageType.USER;
        if (message instanceof AiMessage) return MessageType.AI;
        if (message instanceof SystemMessage) return MessageType.SYSTEM;
        throw new IllegalArgumentException("Unknown message type: " + message.getClass());
    }
}
```

## Observability Configuration

### Monitoring and Metrics

```java
@Configuration
public class ObservabilityConfiguration {

    @Bean
    public ChatModelListener chatModelListener(MeterRegistry meterRegistry) {
        return new MonitoringChatModelListener(meterRegistry);
    }

    @Bean
    public HealthIndicator aiHealthIndicator(ChatModel chatModel) {
        return new AiHealthIndicator(chatModel);
    }
}

class MonitoringChatModelListener implements ChatModelListener {

    private final MeterRegistry meterRegistry;
    private final Counter requestCounter;
    private final Timer responseTimer;

    public MonitoringChatModelListener(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestCounter = Counter.builder("ai.requests.total")
                .description("Total AI requests")
                .register(meterRegistry);
        this.responseTimer = Timer.builder("ai.response.duration")
                .description("AI response time")
                .register(meterRegistry);
    }

    @Override
    public void onRequest(ChatModelRequestContext requestContext) {
        requestCounter.increment();
        logRequest(requestContext);
    }

    @Override
    public void onResponse(ChatModelResponseContext responseContext) {
        responseTimer.record(responseContext.duration());
        logResponse(responseContext);
    }

    private void logRequest(ChatModelRequestContext requestContext) {
        meterRegistry.gauge("ai.request.tokens",
                requestContext.request().messages().size());
    }

    private void logResponse(ChatModelResponseContext responseContext) {
        Response<AiMessage> response = responseContext.response();
        meterRegistry.gauge("ai.response.tokens",
                response.tokenUsage().totalTokenCount());
    }
}
```

### Custom Health Check

```java
@Component
@RequiredArgsConstructor
public class AiHealthIndicator implements HealthIndicator {

    private final ChatModel chatModel;
    private final EmbeddingModel embeddingModel;

    @Override
    public Health health() {
        try {
            // Test chat model
            Health.Builder builder = Health.up();
            String chatResponse = chatModel.chat("ping");
            builder.withDetail("chat_model", "healthy");

            if (chatResponse == null || chatResponse.trim().isEmpty()) {
                return Health.down().withDetail("reason", "Empty response");
            }

            // Test embedding model
            List<String> testTexts = List.of("test", "ping", "hello");
            List<Embedding> embeddings = embeddingModel.embedAll(testTexts).content();

            if (embeddings.isEmpty()) {
                return Health.down().withDetail("reason", "No embeddings generated");
            }

            builder.withDetail("embedding_model", "healthy")
                   .withDetail("embedding_dimension", embeddings.get(0).vector().length);

            return builder.build();

        } catch (Exception e) {
            return Health.down()
                    .withDetail("error", e.getMessage())
                    .withDetail("exception_class", e.getClass().getSimpleName());
        }
    }
}
```

## Security Configuration

### API Key Security

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .authorizeRequests()
                .requestMatchers("/api/ai/**").hasRole("AI_USER")
                .requestMatchers("/actuator/ai/**").hasRole("AI_ADMIN")
                .anyRequest().permitAll()
            .and()
            .httpBasic();
        return http.build();
    }

    @Bean
    public ApiKeyAuthenticationFilter apiKeyAuthenticationFilter() {
        return new ApiKeyAuthenticationFilter("/api/ai/**");
    }
}

class ApiKeyAuthenticationFilter extends OncePerRequestFilter {

    private final String pathPrefix;

    public ApiKeyAuthenticationFilter(String pathPrefix) {
        this.pathPrefix = pathPrefix;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                   HttpServletResponse response,
                                   FilterChain filterChain) throws ServletException, IOException {

        if (request.getRequestURI().startsWith(pathPrefix)) {
            String apiKey = request.getHeader("X-API-Key");
            if (apiKey == null || !isValidApiKey(apiKey)) {
                response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid API key");
                return;
            }
        }

        filterChain.doFilter(request, response);
    }

    private boolean isValidApiKey(String apiKey) {
        // Validate API key against database or security service
        return true;
    }
}
```

### Configuration Validation

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class AiConfigurationValidator implements InitializingBean {

    private final AiProperties properties;

    @Override
    public void afterPropertiesSet() {
        validateConfiguration();
    }

    private void validateConfiguration() {
        if (properties.getOpenai() != null) {
            validateOpenAiConfiguration();
        }

        if (properties.getAzureOpenAi() != null) {
            validateAzureConfiguration();
        }

        if (properties.getAnthropic() != null) {
            validateAnthropicConfiguration();
        }

        log.info("AI configuration validation completed successfully");
    }

    private void validateOpenAiConfiguration() {
        OpenAiProperties openAi = properties.getOpenai();

        if (openAi.getChatModel() != null &&
            (openAi.getChatModel().getApiKey() == null ||
             openAi.getChatModel().getApiKey().isEmpty())) {
            log.warn("OpenAI chat model API key is not configured");
        }

        if (openAi.getChatModel() != null &&
            openAi.getChatModel().getMaxTokens() != null &&
            openAi.getChatModel().getMaxTokens() > 8192) {
            log.warn("OpenAI max tokens {} exceeds recommended limit of 8192",
                    openAi.getChatModel().getMaxTokens());
        }
    }

    private void validateAzureConfiguration() {
        AzureOpenAiProperties azure = properties.getAzureOpenAi();

        if (azure.getChatModel() != null &&
            (azure.getChatModel().getEndpoint() == null ||
             azure.getChatModel().getApiKey() == null)) {
            log.error("Azure OpenAI endpoint or API key is not configured");
        }
    }

    private void validateAnthropicConfiguration() {
        AnthropicProperties anthropic = properties.getAnthropic();

        if (anthropic.getChatModel() != null &&
            (anthropic.getChatModel().getApiKey() == null ||
             anthropic.getChatModel().getApiKey().isEmpty())) {
            log.warn("Anthropic chat model API key is not configured");
        }
    }
}

@Configuration
@ConfigurationProperties(prefix = "langchain4j")
@Validated
@Data
public class AiProperties {
    private OpenAiProperties openai;
    private AzureOpenAiProperties azureOpenAi;
    private AnthropicProperties anthropic;
    private MemoryProperties memory;
    private VectorStoreProperties vectorStore;

    // Validation annotations for properties
}

@Data
@Validated
public class OpenAiProperties {
    private ChatModelProperties chatModel;
    private EmbeddingModelProperties embeddingModel;
    private StreamingChatModelProperties streamingChatModel;

    @Valid
    @NotNull
    public ChatModelProperties getChatModel() {
        return chatModel;
    }
}
```

## Environment-Specific Configurations

### Development Configuration

```yaml
# application-dev.yml
langchain4j:
  open-ai:
    chat-model:
      api-key: ${OPENAI_API_KEY_DEV}
      model-name: gpt-4o-mini
      temperature: 0.8
      log-requests: true
      log-responses: true

  memory:
    store-type: in-memory
    max-messages: 10

  vector-store:
    type: in-memory

logging:
  level:
    dev.langchain4j: DEBUG
    org.springframework.ai: DEBUG
```

### Production Configuration

```yaml
# application-prod.yml
langchain4j:
  open-ai:
    chat-model:
      api-key: ${OPENAI_API_KEY_PROD}
      model-name: gpt-4o
      temperature: 0.3
      log-requests: false
      log-responses: false
      max-tokens: 4000

  memory:
    store-type: postgresql
    max-messages: 5

  vector-store:
    type: pinecone
    pinecone:
      index-name: production-knowledge-base
      namespace: prod

logging:
  level:
    dev.langchain4j: WARN
    org.springframework.ai: WARN

management:
  endpoints:
    web:
      exposure:
        include: health, metrics, info
  endpoint:
    health:
      show-details: when-authorized
```

This configuration guide provides comprehensive options for setting up LangChain4j with Spring Boot, covering various providers, storage backends, monitoring, and security considerations.