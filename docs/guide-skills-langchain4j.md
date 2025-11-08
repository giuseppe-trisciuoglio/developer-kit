# Complete Guide to LangChain4j Skills

This comprehensive guide documents all LangChain4j skills available in the Developer Kit, organized by functional area with detailed explanations, practical examples, and best practices for building AI-powered applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Integration Skills](#core-integration-skills)
3. [AI Services & Tools](#ai-services--tools)
4. [RAG Implementation](#rag-implementation)
5. [Vector Stores](#vector-stores)
6. [MCP Server Patterns](#mcp-server-patterns)
7. [Testing Strategies](#testing-strategies)
8. [Common Workflows](#common-workflows)
9. [Best Practices](#best-practices)

---

## Overview

The LangChain4j skills collection provides comprehensive patterns for building AI-powered Java/Spring Boot applications using LangChain4j, covering everything from basic integration to advanced RAG (Retrieval Augmented Generation) implementations.

### Skill Categories

- **Core Integration**: Spring Boot configuration and setup
- **AI Services**: Service interfaces, function calling, memory
- **RAG**: Document ingestion, retrieval, generation
- **Vector Stores**: Qdrant, Chroma, Pinecone, Weaviate configuration
- **MCP Server**: Model Context Protocol server patterns
- **Testing**: Strategies for testing AI-powered features

### Technology Stack

- **LangChain4j**: 1.8.0+
- **Spring Boot**: 3.5.x or later
- **Java**: 17+ (records preferred for DTOs)
- **Vector Stores**: Qdrant, Chroma, Pinecone, Weaviate
- **LLM Providers**: OpenAI, Anthropic, Ollama, Azure OpenAI
- **Embedding Models**: OpenAI, Sentence Transformers, Cohere

### Key Concepts

- **AI Services**: Type-safe interfaces for LLM interactions
- **Tools**: Functions that AI can call to perform actions
- **RAG**: Augment LLM responses with retrieved documents
- **Vector Stores**: Store and retrieve embeddings
- **Memory**: Conversation context management
- **Streaming**: Real-time response streaming

---

## Core Integration Skills

### langchain4j-spring-boot-integration

**Purpose**: Integrate LangChain4j with Spring Boot applications using Spring Boot starters and auto-configuration.

**When to use:**
- Starting a new AI-powered Spring Boot application
- Configuring LLM providers (OpenAI, Anthropic, Ollama)
- Setting up embedding models
- Configuring chat memory
- Managing LLM credentials and endpoints

**Key Patterns:**

1. **Dependencies**
```xml
<!-- LangChain4j Spring Boot Starter -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>1.8.0</version>
</dependency>

<!-- OpenAI Integration -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>1.8.0</version>
</dependency>

<!-- Embedding Store (Qdrant example) -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-qdrant</artifactId>
    <version>1.8.0</version>
</dependency>
```

2. **Configuration**
```yaml
langchain4j:
  open-ai:
    chat-model:
      api-key: ${OPENAI_API_KEY}
      model-name: gpt-4
      temperature: 0.7
      max-tokens: 2000
      timeout: PT30S
    embedding-model:
      api-key: ${OPENAI_API_KEY}
      model-name: text-embedding-3-small
      dimensions: 1536
  
  qdrant:
    host: localhost
    port: 6333
    collection-name: documents
    use-tls: false

  # Memory configuration
  chat-memory:
    type: message-window
    max-messages: 10
```

3. **Basic AI Service**
```java
@Service
public interface AssistantService {
    
    @SystemMessage("""
        You are a helpful customer service assistant.
        Be concise and professional in your responses.
        """)
    String chat(@UserMessage String userMessage);
}
```

4. **Configuration Class**
```java
@Configuration
public class LangChain4jConfig {

    @Bean
    public ChatLanguageModel chatLanguageModel(
            @Value("${langchain4j.open-ai.api-key}") String apiKey) {
        return OpenAiChatModel.builder()
            .apiKey(apiKey)
            .modelName("gpt-4")
            .temperature(0.7)
            .maxTokens(2000)
            .timeout(Duration.ofSeconds(30))
            .logRequests(true)
            .logResponses(true)
            .build();
    }

    @Bean
    public EmbeddingModel embeddingModel(
            @Value("${langchain4j.open-ai.api-key}") String apiKey) {
        return OpenAiEmbeddingModel.builder()
            .apiKey(apiKey)
            .modelName("text-embedding-3-small")
            .dimensions(1536)
            .build();
    }

    @Bean
    public ChatMemoryProvider chatMemoryProvider() {
        return memoryId -> MessageWindowChatMemory.withMaxMessages(10);
    }
}
```

**Best Practices:**
- Store API keys in environment variables or secret managers
- Use Spring Boot configuration properties for flexibility
- Configure timeouts appropriately (30s default)
- Enable request/response logging during development
- Use chat memory for conversational contexts
- Choose appropriate model based on use case (speed vs capability)
- Monitor token usage and costs

**References:**
- `skills/langchain4j/langchain4j-spring-boot-integration/SKILL.md`

---

## AI Services & Tools

### langchain4j-ai-services-patterns

**Purpose**: Build type-safe, declarative AI service interfaces with system messages, user messages, and function calling.

**When to use:**
- Creating conversational AI services
- Implementing domain-specific AI assistants
- Building structured AI interactions
- Type-safe LLM interactions

**Key Patterns:**

1. **Simple AI Service**
```java
public interface CustomerSupportAssistant {
    
    @SystemMessage("""
        You are a customer support agent for an e-commerce platform.
        Your role is to help customers with their orders, returns, and questions.
        Be empathetic, professional, and solution-oriented.
        """)
    String chat(@UserMessage String userMessage);
}
```

2. **AI Service with Memory**
```java
public interface ConversationalAssistant {
    
    @SystemMessage("You are a helpful assistant. Remember context from previous messages.")
    String chat(@MemoryId String conversationId, @UserMessage String message);
}

// Usage
@Service
@RequiredArgsConstructor
public class ChatService {
    private final ConversationalAssistant assistant;

    public String chat(String userId, String message) {
        return assistant.chat(userId, message);
    }
}
```

3. **AI Service with Structured Output**
```java
public interface ProductAnalysisService {
    
    @SystemMessage("Extract product information from the given text.")
    ProductInfo extractProductInfo(@UserMessage String productDescription);
}

public record ProductInfo(
    String name,
    String category,
    BigDecimal estimatedPrice,
    List<String> features
) {}
```

4. **AI Service with Validation**
```java
public interface ContentModerator {
    
    @SystemMessage("""
        Analyze the given text for inappropriate content.
        Return a ModerationResult with:
        - appropriate: boolean (true if content is safe)
        - reason: string (explanation if inappropriate)
        - categories: list of violated categories
        """)
    ModerationResult moderate(@UserMessage String content);
}

public record ModerationResult(
    boolean appropriate,
    @Nullable String reason,
    List<String> violatedCategories
) {}
```

5. **Creating AI Service Instances**
```java
@Configuration
public class AiServiceConfig {

    @Bean
    public CustomerSupportAssistant customerSupportAssistant(
            ChatLanguageModel chatModel,
            ChatMemoryProvider memoryProvider,
            List<Tool> tools) {
        
        return AiServices.builder(CustomerSupportAssistant.class)
            .chatLanguageModel(chatModel)
            .chatMemoryProvider(memoryProvider)
            .tools(tools)
            .build();
    }
}
```

**Best Practices:**
- Use descriptive interface names
- Write clear, detailed system messages
- Use `@MemoryId` for conversation continuity
- Define structured outputs with records
- Include domain-specific context in system messages
- Use validation for AI-generated data
- Log AI interactions for debugging

**References:**
- `skills/langchain4j/langchain4j-ai-services-patterns/SKILL.md`

---

### langchain4j-tool-function-calling-patterns

**Purpose**: Enable AI to call Java methods (tools) to perform actions, retrieve data, or interact with external systems.

**When to use:**
- Allowing AI to query databases
- Integrating AI with REST APIs
- Enabling AI to perform calculations
- Creating AI agents with actions
- Building tool-based workflows

**Key Patterns:**

1. **Simple Tool**
```java
@Component
public class WeatherTools {

    @Tool("Get current weather for a city")
    public String getCurrentWeather(
            @P("The city name") String city) {
        
        // Call weather API
        WeatherData weather = weatherApi.getWeather(city);
        
        return String.format(
            "Temperature in %s is %.1f°C, %s",
            city,
            weather.temperature(),
            weather.condition()
        );
    }
}
```

2. **Tool with Validation**
```java
@Component
public class OrderTools {
    
    private final OrderRepository orderRepository;

    @Tool("Get order details by order ID")
    public OrderDetails getOrder(@P("Order ID") String orderId) {
        return orderRepository.findById(orderId)
            .map(this::toOrderDetails)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    @Tool("Cancel an order")
    public CancellationResult cancelOrder(
            @P("Order ID") String orderId,
            @P("Cancellation reason") String reason) {
        
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));

        if (!order.isCancellable()) {
            return new CancellationResult(
                false,
                "Order cannot be cancelled in current state: " + order.getStatus()
            );
        }

        order.cancel(reason);
        orderRepository.save(order);

        return new CancellationResult(true, "Order cancelled successfully");
    }
}
```

3. **Database Query Tool**
```java
@Component
public class ProductSearchTools {
    
    private final ProductRepository productRepository;

    @Tool("Search products by name or description")
    public List<ProductSummary> searchProducts(
            @P("Search query") String query,
            @P("Maximum results to return") @Optional int limit) {
        
        int maxResults = limit > 0 ? Math.min(limit, 20) : 10;
        
        return productRepository.search(query, PageRequest.of(0, maxResults))
            .stream()
            .map(this::toSummary)
            .toList();
    }

    @Tool("Get product details by ID")
    public ProductDetails getProductById(@P("Product ID") Long productId) {
        return productRepository.findById(productId)
            .map(this::toDetails)
            .orElse(null);
    }
}
```

4. **External API Tool**
```java
@Component
@RequiredArgsConstructor
public class ExternalApiTools {
    
    private final RestTemplate restTemplate;

    @Tool("Search for news articles on a given topic")
    public List<NewsArticle> searchNews(
            @P("Search topic or query") String query,
            @P("Number of articles to return (max 10)") @Optional Integer limit) {
        
        int maxArticles = limit != null ? Math.min(limit, 10) : 5;
        
        NewsApiResponse response = restTemplate.getForObject(
            "https://newsapi.org/v2/everything?q={query}&pageSize={limit}",
            NewsApiResponse.class,
            query,
            maxArticles
        );

        return response != null ? response.articles() : List.of();
    }
}
```

5. **Calculation Tool**
```java
@Component
public class CalculationTools {

    @Tool("Calculate compound interest")
    public CompoundInterestResult calculateCompoundInterest(
            @P("Principal amount") double principal,
            @P("Annual interest rate (as percentage, e.g., 5 for 5%)") double rate,
            @P("Number of years") int years,
            @P("Compounding frequency per year (e.g., 12 for monthly)") int frequency) {
        
        double amount = principal * Math.pow(
            1 + (rate / 100.0) / frequency,
            frequency * years
        );
        
        double totalInterest = amount - principal;

        return new CompoundInterestResult(
            principal,
            rate,
            years,
            frequency,
            amount,
            totalInterest
        );
    }
}
```

6. **Registering Tools with AI Service**
```java
@Configuration
public class AiServiceConfig {

    @Bean
    public AssistantService assistantService(
            ChatLanguageModel chatModel,
            WeatherTools weatherTools,
            OrderTools orderTools,
            ProductSearchTools productSearchTools) {
        
        return AiServices.builder(AssistantService.class)
            .chatLanguageModel(chatModel)
            .tools(weatherTools, orderTools, productSearchTools)
            .build();
    }
}
```

**Best Practices:**
- Use `@Tool` annotation with clear descriptions
- Use `@P` to describe each parameter
- Return structured data (records, POJOs)
- Validate inputs in tool methods
- Handle errors gracefully
- Limit results to prevent token overflow
- Use `@Optional` for optional parameters
- Keep tool methods simple and focused
- Log tool executions for debugging
- Consider security implications (authorization, rate limiting)

**References:**
- `skills/langchain4j/langchain4j-tool-function-calling-patterns/SKILL.md`

---

## RAG Implementation

### langchain4j-rag-implementation-patterns

**Purpose**: Implement Retrieval Augmented Generation (RAG) to enhance LLM responses with relevant document context.

**When to use:**
- Building document Q&A systems
- Creating knowledge base chatbots
- Augmenting LLM with domain-specific information
- Reducing hallucinations with factual data
- Building semantic search features

**Key Patterns:**

1. **Document Ingestion**
```java
@Service
@RequiredArgsConstructor
public class DocumentIngestionService {
    
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;

    public void ingestDocument(String documentPath) {
        // Load document
        Document document = FileSystemDocumentLoader.loadDocument(documentPath);

        // Split into chunks
        DocumentSplitter splitter = DocumentSplitters.recursive(
            500,  // max segment size in tokens
            50    // overlap between segments
        );
        List<TextSegment> segments = splitter.split(document);

        // Generate embeddings
        List<Embedding> embeddings = embeddingModel.embedAll(segments).content();

        // Store in vector database
        embeddingStore.addAll(embeddings, segments);
        
        log.info("Ingested document: {} ({} segments)", documentPath, segments.size());
    }

    public void ingestDocuments(List<Path> documentPaths) {
        documentPaths.forEach(path -> ingestDocument(path.toString()));
    }
}
```

2. **RAG Service**
```java
@Service
@RequiredArgsConstructor
public class RagService {
    
    private final ChatLanguageModel chatModel;
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;

    public String answer(String question) {
        // Retrieve relevant documents
        Embedding questionEmbedding = embeddingModel.embed(question).content();
        
        List<EmbeddingMatch<TextSegment>> relevantDocs = embeddingStore.findRelevant(
            questionEmbedding,
            5  // top 5 most relevant
        );

        // Build context from retrieved documents
        String context = relevantDocs.stream()
            .map(match -> match.embedded().text())
            .collect(Collectors.joining("\n\n"));

        // Generate answer with context
        String prompt = String.format("""
            Use the following context to answer the question.
            If the answer is not in the context, say "I don't know."
            
            Context:
            %s
            
            Question: %s
            
            Answer:
            """, context, question);

        return chatModel.generate(prompt);
    }
}
```

3. **RAG with AI Service**
```java
public interface RagAssistant {
    
    @SystemMessage("""
        You are a helpful assistant that answers questions based on provided context.
        Only use information from the context to answer questions.
        If the answer is not in the context, say "I don't have enough information to answer that."
        """)
    String chat(@UserMessage String question);
}

@Configuration
public class RagConfig {

    @Bean
    public RagAssistant ragAssistant(
            ChatLanguageModel chatModel,
            ContentRetriever contentRetriever) {
        
        return AiServices.builder(RagAssistant.class)
            .chatLanguageModel(chatModel)
            .contentRetriever(contentRetriever)
            .build();
    }

    @Bean
    public ContentRetriever contentRetriever(
            EmbeddingModel embeddingModel,
            EmbeddingStore<TextSegment> embeddingStore) {
        
        return EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .minScore(0.7)  // minimum relevance score
            .build();
    }
}
```

4. **Advanced RAG with Re-ranking**
```java
@Bean
public ContentRetriever advancedContentRetriever(
        EmbeddingModel embeddingModel,
        EmbeddingStore<TextSegment> embeddingStore,
        ScoringModel scoringModel) {
    
    return EmbeddingStoreContentRetriever.builder()
        .embeddingStore(embeddingStore)
        .embeddingModel(embeddingModel)
        .maxResults(10)  // Retrieve more candidates
        .minScore(0.6)
        .build()
        .withReRanking(scoringModel, 5);  // Re-rank to top 5
}
```

5. **Metadata Filtering**
```java
public String answerWithFilter(String question, String category) {
    Embedding questionEmbedding = embeddingModel.embed(question).content();
    
    Filter metadataFilter = Filter.metadataKey("category").isEqualTo(category);
    
    List<EmbeddingMatch<TextSegment>> relevantDocs = embeddingStore.findRelevant(
        questionEmbedding,
        5,
        metadataFilter
    );

    // Build context and generate answer
    // ...
}
```

6. **Hybrid Search (Vector + Keyword)**
```java
@Service
public class HybridSearchService {
    
    public List<SearchResult> hybridSearch(String query) {
        // Vector search
        List<EmbeddingMatch<TextSegment>> vectorResults = 
            vectorSearch(query, 10);

        // Keyword search (e.g., Elasticsearch)
        List<Document> keywordResults = keywordSearch(query, 10);

        // Combine and re-rank results
        return combineAndRerank(vectorResults, keywordResults);
    }
}
```

**Best Practices:**
- Chunk documents appropriately (300-1000 tokens)
- Use overlap between chunks (10-20%)
- Store metadata with embeddings (source, date, category)
- Implement metadata filtering for focused retrieval
- Use re-ranking for better results
- Set minimum relevance score threshold (0.6-0.8)
- Retrieve more candidates (10+) then re-rank
- Handle "no relevant context" scenarios
- Monitor retrieval quality and adjust
- Consider hybrid search (vector + keyword)
- Implement caching for frequent queries
- Use async ingestion for large document sets

**References:**
- `skills/langchain4j/langchain4j-rag-implementation-patterns/SKILL.md`

---

## Vector Stores

### langchain4j-vector-stores-configuration

**Purpose**: Configure and integrate vector databases for storing and retrieving embeddings.

**When to use:**
- Setting up RAG systems
- Implementing semantic search
- Storing document embeddings
- Building recommendation systems
- Managing large knowledge bases

**Supported Vector Stores:**
- **Qdrant**: High-performance, open-source
- **Chroma**: Simple, local-first
- **Pinecone**: Managed, cloud-native
- **Weaviate**: GraphQL interface, hybrid search
- **Milvus**: Scalable, enterprise-grade
- **PgVector**: PostgreSQL extension

**Key Patterns:**

1. **Qdrant Configuration**
```yaml
langchain4j:
  qdrant:
    host: localhost
    port: 6333
    collection-name: documents
    use-tls: false
    api-key: ${QDRANT_API_KEY:}
```

```java
@Configuration
public class QdrantConfig {

    @Bean
    public EmbeddingStore<TextSegment> qdrantEmbeddingStore(
            @Value("${langchain4j.qdrant.host}") String host,
            @Value("${langchain4j.qdrant.port}") int port,
            @Value("${langchain4j.qdrant.collection-name}") String collectionName) {
        
        return QdrantEmbeddingStore.builder()
            .host(host)
            .port(port)
            .collectionName(collectionName)
            .useTls(false)
            .build();
    }
}
```

2. **Qdrant with Docker**
```yaml
# docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant:v1.7.4
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334

volumes:
  qdrant_storage:
```

3. **Chroma Configuration**
```java
@Bean
public EmbeddingStore<TextSegment> chromaEmbeddingStore() {
    return ChromaEmbeddingStore.builder()
        .baseUrl("http://localhost:8000")
        .collectionName("documents")
        .build();
}
```

4. **Pinecone Configuration (Cloud)**
```yaml
langchain4j:
  pinecone:
    api-key: ${PINECONE_API_KEY}
    environment: us-east-1-aws
    index-name: documents
    namespace: default
```

```java
@Bean
public EmbeddingStore<TextSegment> pineconeEmbeddingStore(
        @Value("${langchain4j.pinecone.api-key}") String apiKey,
        @Value("${langchain4j.pinecone.index-name}") String indexName) {
    
    return PineconeEmbeddingStore.builder()
        .apiKey(apiKey)
        .index(indexName)
        .namespace("default")
        .createIndex(true)
        .build();
}
```

5. **PgVector Configuration (PostgreSQL)**
```java
@Bean
public EmbeddingStore<TextSegment> pgVectorEmbeddingStore(DataSource dataSource) {
    return PgVectorEmbeddingStore.builder()
        .dataSource(dataSource)
        .table("embeddings")
        .dimension(1536)  // OpenAI embedding dimension
        .createTable(true)
        .dropTableFirst(false)
        .build();
}
```

6. **Custom Embedding Store Operations**
```java
@Service
@RequiredArgsConstructor
public class VectorStoreService {
    
    private final EmbeddingStore<TextSegment> embeddingStore;
    private final EmbeddingModel embeddingModel;

    public String addDocument(String text, Map<String, String> metadata) {
        TextSegment segment = TextSegment.from(text, Metadata.from(metadata));
        Embedding embedding = embeddingModel.embed(text).content();
        
        String id = embeddingStore.add(embedding, segment);
        log.info("Added document with ID: {}", id);
        
        return id;
    }

    public void removeDocument(String id) {
        embeddingStore.remove(id);
        log.info("Removed document with ID: {}", id);
    }

    public List<EmbeddingMatch<TextSegment>> search(String query, int maxResults) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        
        return embeddingStore.findRelevant(queryEmbedding, maxResults);
    }

    public List<EmbeddingMatch<TextSegment>> searchWithFilter(
            String query,
            int maxResults,
            Filter filter) {
        
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        
        return embeddingStore.findRelevant(
            queryEmbedding,
            maxResults,
            filter
        );
    }
}
```

**Choosing a Vector Store:**

- **Development/Prototyping**: Chroma (simple, local)
- **Production (Self-hosted)**: Qdrant, Milvus (scalable, performant)
- **Production (Cloud)**: Pinecone, Weaviate Cloud (managed)
- **Existing PostgreSQL**: PgVector (leverage existing infrastructure)
- **Hybrid Search**: Weaviate (built-in keyword + vector)

**Best Practices:**
- Choose vector store based on scale and requirements
- Use Docker for local development
- Configure appropriate distance metrics (cosine, dot product)
- Set up indexing for faster searches
- Use metadata filtering for scoped searches
- Implement backup and restore strategies
- Monitor storage and query performance
- Use connection pooling for production
- Consider data privacy and security
- Plan for scaling (sharding, replication)

**References:**
- `skills/langchain4j/langchain4j-vector-stores-configuration/SKILL.md`

---

## MCP Server Patterns

### langchain4j-mcp-server-patterns

**Purpose**: Implement Model Context Protocol (MCP) servers to extend AI capabilities with custom tools and data sources.

**When to use:**
- Exposing custom tools to AI
- Integrating proprietary data sources
- Building reusable AI extensions
- Creating tool marketplaces
- Standardizing AI-tool interfaces

**Key Patterns:**

1. **MCP Server Implementation**
```java
@Component
public class CustomMcpServer implements McpServer {

    @Override
    public List<Tool> listTools() {
        return List.of(
            Tool.builder()
                .name("calculate_tax")
                .description("Calculate tax for a given amount")
                .parameters(JsonSchemaProperty.object(
                    JsonSchemaProperty.property("amount", JsonSchemaProperty.number()),
                    JsonSchemaProperty.property("taxRate", JsonSchemaProperty.number())
                ))
                .build(),
            
            Tool.builder()
                .name("get_customer_orders")
                .description("Retrieve orders for a customer")
                .parameters(JsonSchemaProperty.object(
                    JsonSchemaProperty.property("customerId", JsonSchemaProperty.string())
                ))
                .build()
        );
    }

    @Override
    public ToolExecutionResult executeTool(ToolExecutionRequest request) {
        return switch (request.name()) {
            case "calculate_tax" -> calculateTax(request);
            case "get_customer_orders" -> getCustomerOrders(request);
            default -> ToolExecutionResult.error("Unknown tool: " + request.name());
        };
    }

    private ToolExecutionResult calculateTax(ToolExecutionRequest request) {
        double amount = request.argument("amount", Double.class);
        double taxRate = request.argument("taxRate", Double.class);
        double tax = amount * (taxRate / 100.0);
        
        return ToolExecutionResult.success(Map.of(
            "amount", amount,
            "taxRate", taxRate,
            "tax", tax,
            "total", amount + tax
        ));
    }

    private ToolExecutionResult getCustomerOrders(ToolExecutionRequest request) {
        String customerId = request.argument("customerId", String.class);
        
        // Fetch orders from database
        List<Order> orders = orderRepository.findByCustomerId(customerId);
        
        return ToolExecutionResult.success(orders);
    }
}
```

2. **MCP Server Configuration**
```java
@Configuration
public class McpServerConfig {

    @Bean
    public McpServerStarter mcpServerStarter(List<McpServer> mcpServers) {
        return McpServerStarter.builder()
            .servers(mcpServers)
            .port(8080)
            .build();
    }
}
```

**Best Practices:**
- Define clear tool names and descriptions
- Use JSON Schema for parameter validation
- Handle errors gracefully
- Implement authentication/authorization
- Log tool executions
- Version your MCP servers
- Document tool usage

**References:**
- `skills/langchain4j/langchain4j-mcp-server-patterns/SKILL.md`

---

## Testing Strategies

### langchain4j-testing-strategies

**Purpose**: Test AI-powered features reliably without excessive LLM API calls.

**When to use:**
- Testing AI services in CI/CD
- Validating tool calling logic
- Testing RAG retrieval
- Verifying conversation flows
- Unit testing AI integrations

**Key Patterns:**

1. **Mock ChatLanguageModel**
```java
@ExtendWith(MockitoExtension.class)
class AssistantServiceTest {

    @Mock
    private ChatLanguageModel chatModel;

    @InjectMocks
    private AssistantService assistantService;

    @Test
    void shouldGenerateResponse() {
        // Given
        String userMessage = "What is the weather?";
        String expectedResponse = "The weather is sunny with 25°C.";
        
        when(chatModel.generate(anyString())).thenReturn(expectedResponse);

        // When
        String response = assistantService.chat(userMessage);

        // Then
        assertThat(response).isEqualTo(expectedResponse);
        verify(chatModel).generate(contains(userMessage));
    }
}
```

2. **Test Tools in Isolation**
```java
@ExtendWith(MockitoExtension.class)
class WeatherToolsTest {

    @Mock
    private WeatherApiClient weatherApiClient;

    @InjectMocks
    private WeatherTools weatherTools;

    @Test
    void shouldReturnCurrentWeather() {
        // Given
        when(weatherApiClient.getWeather("London"))
            .thenReturn(new WeatherData(25.0, "Sunny"));

        // When
        String result = weatherTools.getCurrentWeather("London");

        // Then
        assertThat(result).contains("London", "25.0°C", "Sunny");
    }
}
```

3. **Integration Test with Local Model (Ollama)**
```yaml
# application-test.yml
langchain4j:
  ollama:
    base-url: http://localhost:11434
    model-name: llama2
    temperature: 0.1  # Lower for deterministic tests
```

```java
@SpringBootTest
@ActiveProfiles("test")
class AssistantServiceIntegrationTest {

    @Autowired
    private AssistantService assistantService;

    @Test
    void shouldAnswerSimpleQuestion() {
        // When
        String response = assistantService.chat("What is 2+2?");

        // Then
        assertThat(response.toLowerCase()).contains("4", "four");
    }
}
```

4. **Test RAG Retrieval**
```java
@Test
void shouldRetrieveRelevantDocuments() {
    // Given
    String question = "What is LangChain4j?";

    // When
    List<EmbeddingMatch<TextSegment>> results = 
        contentRetriever.retrieve(question);

    // Then
    assertThat(results)
        .isNotEmpty()
        .allSatisfy(match -> {
            assertThat(match.score()).isGreaterThan(0.7);
            assertThat(match.embedded().text()).containsIgnoringCase("langchain4j");
        });
}
```

5. **Snapshot Testing for Prompts**
```java
@Test
void shouldGenerateCorrectPrompt() {
    // When
    String prompt = promptTemplate.apply(Map.of(
        "question", "What is AI?",
        "context", "AI stands for Artificial Intelligence..."
    ));

    // Then
    assertThat(prompt).isEqualTo("""
        Use the following context to answer the question.
        
        Context: AI stands for Artificial Intelligence...
        
        Question: What is AI?
        
        Answer:
        """);
}
```

6. **Test with Wiremock for External LLM APIs**
```java
@SpringBootTest
class OpenAiIntegrationTest {

    @RegisterExtension
    static WireMockExtension wireMock = WireMockExtension.newInstance()
        .options(wireMockConfig().port(8089))
        .build();

    @Test
    void shouldCallOpenAiApi() {
        // Given
        wireMock.stubFor(post("/v1/chat/completions")
            .willReturn(aResponse()
                .withHeader("Content-Type", "application/json")
                .withBody("""
                    {
                        "choices": [{
                            "message": {
                                "content": "This is a test response"
                            }
                        }]
                    }
                    """)));

        // When
        String response = assistantService.chat("Test question");

        // Then
        assertThat(response).isEqualTo("This is a test response");
    }
}
```

**Best Practices:**
- Mock LLM calls in unit tests
- Use local models (Ollama) for integration tests
- Test tools independently
- Use deterministic settings (low temperature) for tests
- Test error handling and edge cases
- Implement retry logic for flaky LLM tests
- Use snapshot testing for prompt validation
- Monitor token usage in tests
- Skip expensive tests in CI with `@Tag("expensive")`
- Cache LLM responses for tests

**References:**
- `skills/langchain4j/langchain4j-testing-strategies/SKILL.md`

---

## Common Workflows

### Building a RAG-Powered Chatbot

```bash
# 1. Set up dependencies (langchain4j-spring-boot-integration)
# - Add LangChain4j starter
# - Add OpenAI integration
# - Add Qdrant vector store

# 2. Configure LLM and embedding model
# - Configure OpenAI API key
# - Set up Qdrant connection
# - Configure chat memory

# 3. Implement document ingestion (langchain4j-rag-implementation-patterns)
# - Load documents
# - Split into chunks
# - Generate embeddings
# - Store in vector database

# 4. Build RAG service
# - Create ContentRetriever
# - Configure AI Service with retriever
# - Implement answer method

# 5. Add tools (langchain4j-tool-function-calling-patterns)
# - Create tool classes
# - Annotate with @Tool
# - Register with AI Service

# 6. Test implementation (langchain4j-testing-strategies)
# - Mock LLM for unit tests
# - Test tools independently
# - Integration tests with local model
```

---

## Best Practices

### General Principles

1. **Model Selection**
   - Use GPT-4 for complex reasoning
   - Use GPT-3.5-turbo for simple tasks
   - Use local models (Ollama) for development
   - Consider cost vs capability tradeoffs

2. **Prompt Engineering**
   - Write clear, specific system messages
   - Provide examples in prompts
   - Use structured outputs
   - Iterate and test prompts

3. **Error Handling**
   - Handle rate limits gracefully
   - Implement retry logic with exponential backoff
   - Validate AI outputs
   - Provide fallback responses

4. **Performance**
   - Use streaming for long responses
   - Cache frequent queries
   - Implement request batching
   - Monitor token usage

5. **Security**
   - Never expose API keys
   - Validate user inputs
   - Sanitize AI outputs
   - Implement rate limiting
   - Use environment-specific keys

6. **Cost Management**
   - Monitor token usage
   - Use cheaper models when possible
   - Implement caching
   - Set token limits
   - Use local models for development/testing

7. **RAG Best Practices**
   - Chunk documents appropriately (300-1000 tokens)
   - Use metadata filtering
   - Implement re-ranking
   - Monitor retrieval quality
   - Handle "no context" scenarios

8. **Testing**
   - Mock LLM calls in unit tests
   - Use local models for integration tests
   - Test tools independently
   - Implement snapshot testing for prompts
   - Monitor flaky tests

---

## References

- [Contributing Guide](../CONTRIBUTING.md)
- [README](../README.md)

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-08  
