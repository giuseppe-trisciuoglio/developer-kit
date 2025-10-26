---
name: langchain4j-vector-stores-configuration
description: Configure LangChain4J vector stores for RAG applications. Use when building semantic search, integrating vector databases (PostgreSQL/pgvector, Pinecone, MongoDB, Milvus, Neo4j), implementing embedding storage/retrieval, setting up hybrid search, or optimizing vector database performance for production AI applications.
allowed-tools: Read, Write, Bash, Edit
category: backend
tags: [langchain4j, vector-stores, embeddings, rag, semantic-search, ai, llm, java, databases]
version: 1.1.0
context7_library: /websites/langchain4j_dev
context7_trust_score: 7.5
---

# LangChain4J Vector Stores Configuration Skill

This skill provides comprehensive guidance for configuring and integrating vector stores with LangChain4J for building RAG (Retrieval-Augmented Generation) applications, semantic search systems, and LLM-powered applications that require efficient vector storage and retrieval.

## When to Use This Skill

Use this skill when:
- Building RAG applications that require embedding storage and retrieval
- Implementing semantic search functionality in Java applications
- Integrating LLMs with vector databases for context-aware responses
- Configuring multi-modal embedding storage for text, images, or other data
- Setting up hybrid search combining vector similarity and full-text search
- Migrating between different vector store providers
- Optimizing vector database performance for production workloads
- Building AI-powered applications with memory and context persistence
- Implementing document chunking and embedding pipelines
- Creating recommendation systems based on vector similarity

## Core Concepts

### EmbeddingStore Interface

LangChain4J provides a unified `EmbeddingStore` interface that abstracts vector storage operations across different database providers.

**Basic Interface Operations:**
```java
public interface EmbeddingStore<Embedded> {

    // Add single embedding
    String add(Embedding embedding);
    String add(Embedding embedding, Embedded embedded);

    // Add multiple embeddings
    List<String> addAll(List<Embedding> embeddings);
    void addAll(List<String> ids, List<Embedding> embeddings, List<Embedded> embedded);

    // Search for similar embeddings
    EmbeddingSearchResult<Embedded> search(EmbeddingSearchRequest request);

    // Remove embeddings
    void remove(String id);
    void removeAll(Collection<String> ids);
    void removeAll(Filter filter);
    void removeAll();
}
```

**Common Usage Pattern:**
```java
@Service
public class DocumentService {

    private final EmbeddingStore<TextSegment> embeddingStore;
    private final EmbeddingModel embeddingModel;

    public DocumentService(EmbeddingStore<TextSegment> embeddingStore,
                          EmbeddingModel embeddingModel) {
        this.embeddingStore = embeddingStore;
        this.embeddingModel = embeddingModel;
    }

    public void storeDocument(String text, Metadata metadata) {
        TextSegment segment = TextSegment.from(text, metadata);
        Embedding embedding = embeddingModel.embed(segment).content();
        embeddingStore.add(embedding, segment);
    }

    public List<TextSegment> findSimilar(String query, int maxResults) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(maxResults)
            .minScore(0.7)
            .build();

        return embeddingStore.search(request).matches()
            .stream()
            .map(EmbeddingMatch::embedded)
            .collect(Collectors.toList());
    }
}
```

### Supported Vector Stores

LangChain4J supports numerous vector database providers, each with specific configuration requirements.

#### In-Memory Store
For development and testing purposes:
```java
@Bean
public EmbeddingStore<TextSegment> inMemoryEmbeddingStore() {
    return new InMemoryEmbeddingStore<>();
}
```

#### PostgreSQL with pgvector
Production-ready relational database with vector extensions:
```java
@Bean
public EmbeddingStore<TextSegment> pgVectorStore() {
    return PgVectorEmbeddingStore.builder()
        .host("localhost")
        .port(5432)
        .database("vectordb")
        .user("username")
        .password("password")
        .table("embeddings")
        .dimension(1536) // OpenAI embedding dimension
        .createTable(true)
        .useIndex(true)
        .indexListSize(100)
        .build();
}
```

#### Pinecone
Managed vector database service:
```java
@Bean
public EmbeddingStore<TextSegment> pineconeStore() {
    return PineconeEmbeddingStore.builder()
        .apiKey("${pinecone.api.key}")
        .index("my-index")
        .nameSpace("production")
        .metadataTextKey("text")
        .createIndex(PineconeIndexConfig.builder()
            .dimension(1536)
            .metric("cosine")
            .cloud("aws")
            .region("us-east-1")
            .build())
        .build();
}
```

#### MongoDB Atlas Vector Search
Document database with vector search capabilities:
```java
@Bean
public EmbeddingStore<TextSegment> mongoDbStore() {
    MongoClient mongoClient = MongoClients.create("${mongodb.uri}");

    IndexMapping indexMapping = IndexMapping.builder()
        .dimension(1536)
        .metadataFieldNames(Set.of("category", "source"))
        .build();

    return MongoDbEmbeddingStore.builder()
        .fromClient(mongoClient)
        .databaseName("vectordb")
        .collectionName("embeddings")
        .indexName("vector_index")
        .indexMapping(indexMapping)
        .createIndex(true)
        .build();
}
```

#### Neo4j Vector Index
Graph database with vector search:
```java
@Bean
public EmbeddingStore<TextSegment> neo4jStore() {
    return Neo4jEmbeddingStore.builder()
        .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
        .dimension(1536)
        .label("Document")
        .embeddingProperty("embedding")
        .textProperty("text")
        .metadataPrefix("metadata_")
        .autoCreateIndex(true)
        .build();
}
```

#### Milvus/Zilliz
High-performance vector database:
```java
@Bean
public EmbeddingStore<TextSegment> milvusStore() {
    return MilvusEmbeddingStore.builder()
        .host("localhost")
        .port(19530)
        .collectionName("documents")
        .dimension(1536)
        .indexType(IndexType.IVF_FLAT)
        .metricType(MetricType.COSINE)
        .consistencyLevel(ConsistencyLevelEnum.BOUNDED)
        .autoFlushOnInsert(true)
        .build();
}
```

### Configuration Patterns

#### Environment-Based Configuration
Use application properties for environment-specific settings:

```properties
# PostgreSQL pgvector configuration
vector.store.pgvector.host=${PGVECTOR_HOST:localhost}
vector.store.pgvector.port=${PGVECTOR_PORT:5432}
vector.store.pgvector.database=${PGVECTOR_DB:vectordb}
vector.store.pgvector.username=${PGVECTOR_USER:postgres}
vector.store.pgvector.password=${PGVECTOR_PASSWORD}
vector.store.pgvector.table=${PGVECTOR_TABLE:embeddings}
vector.store.pgvector.dimension=${EMBEDDING_DIMENSION:1536}

# Pinecone configuration
vector.store.pinecone.api-key=${PINECONE_API_KEY}
vector.store.pinecone.environment=${PINECONE_ENVIRONMENT:us-east-1-aws}
vector.store.pinecone.index=${PINECONE_INDEX:documents}
vector.store.pinecone.namespace=${PINECONE_NAMESPACE:production}

# MongoDB Atlas configuration
vector.store.mongodb.uri=${MONGODB_ATLAS_URI}
vector.store.mongodb.database=${MONGODB_DATABASE:vectordb}
vector.store.mongodb.collection=${MONGODB_COLLECTION:embeddings}
```

#### Configuration Classes
Create type-safe configuration properties:

```java
@ConfigurationProperties(prefix = "vector.store")
@Configuration
public class VectorStoreConfig {

    private PgVectorConfig pgvector = new PgVectorConfig();
    private PineconeConfig pinecone = new PineconeConfig();
    private MongoDbConfig mongodb = new MongoDbConfig();

    @Data
    public static class PgVectorConfig {
        private String host = "localhost";
        private int port = 5432;
        private String database;
        private String username;
        private String password;
        private String table = "embeddings";
        private int dimension = 1536;
        private boolean createTable = true;
        private boolean useIndex = true;
    }

    @Data
    public static class PineconeConfig {
        private String apiKey;
        private String environment;
        private String index;
        private String namespace;
        private String metadataTextKey = "text";
    }

    @Data
    public static class MongoDbConfig {
        private String uri;
        private String database = "vectordb";
        private String collection = "embeddings";
        private String indexName = "vector_index";
        private Set<String> metadataFields = new HashSet<>();
    }

    // Getters and setters
}
```

#### Conditional Bean Configuration
Configure different stores based on profiles or properties:

```java
@Configuration
public class EmbeddingStoreConfiguration {

    @Bean
    @ConditionalOnProperty(name = "vector.store.type", havingValue = "pgvector")
    public EmbeddingStore<TextSegment> pgVectorEmbeddingStore(VectorStoreConfig config) {
        return PgVectorEmbeddingStore.builder()
            .host(config.getPgvector().getHost())
            .port(config.getPgvector().getPort())
            .database(config.getPgvector().getDatabase())
            .user(config.getPgvector().getUsername())
            .password(config.getPgvector().getPassword())
            .table(config.getPgvector().getTable())
            .dimension(config.getPgvector().getDimension())
            .createTable(config.getPgvector().isCreateTable())
            .useIndex(config.getPgvector().isUseIndex())
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "vector.store.type", havingValue = "pinecone")
    public EmbeddingStore<TextSegment> pineconeEmbeddingStore(VectorStoreConfig config) {
        return PineconeEmbeddingStore.builder()
            .apiKey(config.getPinecone().getApiKey())
            .index(config.getPinecone().getIndex())
            .nameSpace(config.getPinecone().getNamespace())
            .metadataTextKey(config.getPinecone().getMetadataTextKey())
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "vector.store.type", havingValue = "inmemory")
    public EmbeddingStore<TextSegment> inMemoryEmbeddingStore() {
        return new InMemoryEmbeddingStore<>();
    }
}
```

### Hybrid Search and Advanced Features

#### Neo4j Hybrid Search
Combine vector similarity with full-text search:

```java
@Bean
public EmbeddingStore<TextSegment> neo4jHybridStore() {
    return Neo4jEmbeddingStore.builder()
        .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
        .dimension(1536)
        .label("Document")
        .fullTextIndexName("document_text")
        .autoCreateFullText(true)
        .build();
}

// Usage with hybrid search
public List<EmbeddingMatch<TextSegment>> hybridSearch(String query, int maxResults) {
    Embedding queryEmbedding = embeddingModel.embed(query).content();

    EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .maxResults(maxResults)
        .filter(metadataKey("category").isEqualTo("documents"))
        .build();

    return embeddingStore.search(request).matches();
}
```

#### Metadata Filtering
Configure metadata-based filtering capabilities:

```java
// MongoDB with metadata field mapping
IndexMapping indexMapping = IndexMapping.builder()
    .dimension(1536)
    .metadataFieldNames(Set.of("category", "source", "created_date", "author"))
    .build();

// Search with metadata filters
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
    .queryEmbedding(queryEmbedding)
    .maxResults(10)
    .filter(and(
        metadataKey("category").isEqualTo("technical_docs"),
        metadataKey("created_date").isGreaterThan(LocalDate.now().minusMonths(6))
    ))
    .build();
```

### Document Ingestion Patterns

#### EmbeddingStoreIngestor Configuration
Configure automated document processing and storage:

```java
@Bean
public EmbeddingStoreIngestor embeddingStoreIngestor(
        EmbeddingStore<TextSegment> embeddingStore,
        EmbeddingModel embeddingModel) {

    return EmbeddingStoreIngestor.builder()
        .documentSplitter(DocumentSplitters.recursive(
            300,  // maxSegmentSizeInTokens
            20,   // maxOverlapSizeInTokens
            new OpenAiTokenizer(GPT_3_5_TURBO)
        ))
        .embeddingModel(embeddingModel)
        .embeddingStore(embeddingStore)
        .build();
}

// Usage
@Service
public class DocumentIngestionService {

    private final EmbeddingStoreIngestor ingestor;

    public void ingestDocuments(List<Document> documents) {
        ingestor.ingest(documents);
    }
}
```

## API Reference

### Common Configuration Properties

**Database Connection Properties:**
- `host`: Database host address
- `port`: Database port number
- `database`/`databaseName`: Database name
- `username`/`user`: Database username
- `password`: Database password
- `uri`/`connectionString`: Full connection URI

**Vector Configuration:**
- `dimension`: Vector embedding dimension (typically 1536 for OpenAI)
- `metricType`/`similarity`: Distance metric (COSINE, EUCLIDEAN, DOT_PRODUCT)
- `indexType`: Vector index type (IVF_FLAT, HNSW, etc.)

**Table/Collection Configuration:**
- `table`/`tableName`: Table name for SQL databases
- `collection`/`collectionName`: Collection name for document databases
- `indexName`: Vector index name
- `createTable`/`createIndex`: Auto-create table/index if not exists

**Field Mapping:**
- `idField`/`idColumn`: Primary key field name
- `textField`/`textColumn`: Text content field name
- `embeddingField`/`embeddingColumn`: Vector embedding field name
- `metadataField`/`metadataColumn`: Metadata field name

### EmbeddingSearchRequest Parameters

```java
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
    .queryEmbedding(embedding)        // Required: query vector
    .maxResults(10)                   // Maximum results to return
    .minScore(0.7)                    // Minimum similarity score
    .filter(metadataFilter)           // Metadata-based filtering
    .build();
```

### Metadata Filtering API

**Comparison Operators:**
- `metadataKey("field").isEqualTo(value)`
- `metadataKey("field").isNotEqualTo(value)`
- `metadataKey("field").isGreaterThan(value)`
- `metadataKey("field").isGreaterThanOrEqualTo(value)`
- `metadataKey("field").isLessThan(value)`
- `metadataKey("field").isLessThanOrEqualTo(value)`
- `metadataKey("field").isIn(values)`
- `metadataKey("field").isNotIn(values)`

**Logical Operators:**
- `and(filter1, filter2, ...)`
- `or(filter1, filter2, ...)`
- `not(filter)`

## Workflow Patterns

### Multi-Store Configuration Pattern

Configure multiple vector stores for different use cases:

```java
@Configuration
public class MultiVectorStoreConfiguration {

    @Bean
    @Qualifier("documentsStore")
    public EmbeddingStore<TextSegment> documentsEmbeddingStore() {
        return PgVectorEmbeddingStore.builder()
            .table("document_embeddings")
            .dimension(1536)
            .build();
    }

    @Bean
    @Qualifier("chatHistoryStore")
    public EmbeddingStore<TextSegment> chatHistoryEmbeddingStore() {
        return MongoDbEmbeddingStore.builder()
            .collectionName("chat_embeddings")
            .build();
    }

    @Bean
    @Qualifier("cacheStore")
    public EmbeddingStore<TextSegment> cacheEmbeddingStore() {
        return new InMemoryEmbeddingStore<>();
    }
}

@Service
public class MultiStoreService {

    @Autowired
    @Qualifier("documentsStore")
    private EmbeddingStore<TextSegment> documentsStore;

    @Autowired
    @Qualifier("chatHistoryStore")
    private EmbeddingStore<TextSegment> chatHistoryStore;

    @Autowired
    @Qualifier("cacheStore")
    private EmbeddingStore<TextSegment> cacheStore;
}
```

### Health Check and Monitoring Pattern

Implement health checks for vector store connectivity:

```java
@Component
public class VectorStoreHealthIndicator implements HealthIndicator {

    private final EmbeddingStore<TextSegment> embeddingStore;

    @Override
    public Health health() {
        try {
            // Test basic connectivity
            embeddingStore.search(EmbeddingSearchRequest.builder()
                .queryEmbedding(new Embedding(Collections.nCopies(1536, 0.0f)))
                .maxResults(1)
                .build());

            return Health.up()
                .withDetail("store", embeddingStore.getClass().getSimpleName())
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

### Migration Pattern

Migrate data between different vector stores:

```java
@Service
public class VectorStoreMigrationService {

    public void migrate(EmbeddingStore<TextSegment> source,
                       EmbeddingStore<TextSegment> target) {

        List<String> allIds = getAllIds(source);

        for (List<String> batch : Lists.partition(allIds, 100)) {
            List<EmbeddingMatch<TextSegment>> matches = searchByIds(source, batch);

            List<Embedding> embeddings = matches.stream()
                .map(EmbeddingMatch::embedding)
                .collect(Collectors.toList());

            List<TextSegment> segments = matches.stream()
                .map(EmbeddingMatch::embedded)
                .collect(Collectors.toList());

            target.addAll(batch, embeddings, segments);
        }
    }
}
```

## Best Practices

### 1. Choose the Right Vector Store

**For Development:**
- Use `InMemoryEmbeddingStore` for local development and testing
- Fast setup, no external dependencies
- Data lost on application restart

**For Production:**
- **PostgreSQL + pgvector**: Excellent for existing PostgreSQL environments
- **Pinecone**: Managed service, good for rapid prototyping
- **MongoDB Atlas**: Good integration with existing MongoDB applications
- **Milvus/Zilliz**: High performance for large-scale deployments

### 2. Configure Appropriate Index Types

Choose index types based on your use case:

```java
// For high recall requirements
.indexType(IndexType.FLAT)  // Exact search, slower but accurate

// For balanced performance
.indexType(IndexType.IVF_FLAT)  // Good balance of speed and accuracy

// For high-speed approximate search
.indexType(IndexType.HNSW)  // Fastest, slightly less accurate
```

### 3. Optimize Vector Dimensions

Match embedding dimensions to your model:

```java
// OpenAI text-embedding-ada-002
.dimension(1536)

// OpenAI text-embedding-3-small
.dimension(1536)

// OpenAI text-embedding-3-large
.dimension(3072)

// Sentence Transformers (varies by model)
.dimension(384)  // all-MiniLM-L6-v2
.dimension(768)  // all-mpnet-base-v2
```

### 4. Implement Connection Pooling

Configure appropriate connection settings:

```java
@Bean
public EmbeddingStore<TextSegment> optimizedPgVectorStore() {
    HikariConfig hikariConfig = new HikariConfig();
    hikariConfig.setJdbcUrl("jdbc:postgresql://localhost:5432/vectordb");
    hikariConfig.setUsername("username");
    hikariConfig.setPassword("password");
    hikariConfig.setMaximumPoolSize(20);
    hikariConfig.setMinimumIdle(5);
    hikariConfig.setConnectionTimeout(30000);
    hikariConfig.setIdleTimeout(600000);
    hikariConfig.setMaxLifetime(1800000);

    DataSource dataSource = new HikariDataSource(hikariConfig);

    return PgVectorEmbeddingStore.builder()
        .dataSource(dataSource)
        .table("embeddings")
        .dimension(1536)
        .useIndex(true)
        .build();
}
```

### 5. Handle Metadata Efficiently

Design metadata schemas for filtering:

```java
// Define metadata structure
public class DocumentMetadata {
    private String category;
    private String source;
    private LocalDateTime createdAt;
    private String author;
    private List<String> tags;
    private Map<String, Object> customFields;
}

// Configure metadata fields
IndexMapping indexMapping = IndexMapping.builder()
    .dimension(1536)
    .metadataFieldNames(Set.of(
        "category", "source", "created_at", "author", "tags"
    ))
    .build();
```

### 6. Implement Batch Operations

Use batch operations for better performance:

```java
@Service
public class BatchEmbeddingService {

    private static final int BATCH_SIZE = 100;

    public void addDocumentsBatch(List<Document> documents) {
        for (List<Document> batch : Lists.partition(documents, BATCH_SIZE)) {
            List<TextSegment> segments = batch.stream()
                .map(doc -> TextSegment.from(doc.text(), doc.metadata()))
                .collect(Collectors.toList());

            List<Embedding> embeddings = embeddingModel.embedAll(segments)
                .content();

            embeddingStore.addAll(embeddings, segments);
        }
    }
}
```

### 7. Monitor Performance

Track key metrics:

```java
@Component
public class VectorStoreMetrics {

    private final MeterRegistry meterRegistry;
    private final Timer searchTimer;
    private final Counter addCounter;

    @EventListener
    public void onEmbeddingSearch(EmbeddingSearchEvent event) {
        Timer.Sample sample = Timer.start(meterRegistry);
        sample.stop(searchTimer);

        Metrics.gauge("vector.store.results.count", event.getResultCount());
        Metrics.gauge("vector.store.search.score.max", event.getMaxScore());
    }
}
```

### 8. Secure Configuration

Protect sensitive configuration:

```java
// Use environment variables
@Value("${vector.store.api.key:#{null}}")
private String apiKey;

// Validate configuration
@PostConstruct
public void validateConfiguration() {
    if (StringUtils.isBlank(apiKey)) {
        throw new IllegalStateException("Vector store API key must be configured");
    }
}

// Use encrypted properties
@Configuration
@EnableConfigurationProperties(VectorStoreConfig.class)
public class SecureVectorStoreConfig {

    @Bean
    @ConditionalOnProperty("vector.store.encryption.enabled")
    public PropertySourcesPlaceholderConfigurer encryptedPropertyPlaceholder() {
        PropertySourcesPlaceholderConfigurer configurer =
            new PropertySourcesPlaceholderConfigurer();
        configurer.setPlaceholderPrefix("${");
        configurer.setPlaceholderSuffix("}");
        return configurer;
    }
}
```

### 9. Plan for Scaling

Design for horizontal scaling:

```java
@Configuration
public class ScalableVectorStoreConfig {

    @Bean
    @ConditionalOnProperty("vector.store.sharding.enabled")
    public EmbeddingStore<TextSegment> shardedEmbeddingStore() {
        return new ShardedEmbeddingStore(
            createShards(),
            new ConsistentHashShardingStrategy()
        );
    }

    private List<EmbeddingStore<TextSegment>> createShards() {
        return IntStream.range(0, 4)
            .mapToObj(i -> PgVectorEmbeddingStore.builder()
                .table("embeddings_shard_" + i)
                .build())
            .collect(Collectors.toList());
    }
}
```

## Examples

### Basic RAG Application Setup
```java
@Configuration
public class SimpleRagConfig {
    
    @Bean
    public EmbeddingStore<TextSegment> embeddingStore() {
        return PgVectorEmbeddingStore.builder()
            .host("localhost")
            .database("rag_db")
            .table("documents")
            .dimension(1536)
            .build();
    }
    
    @Bean
    public ChatLanguageModel chatModel() {
        return OpenAiChatModel.withApiKey(System.getenv("OPENAI_API_KEY"));
    }
    
    @Bean
    public EmbeddingModel embeddingModel() {
        return OpenAiEmbeddingModel.withApiKey(System.getenv("OPENAI_API_KEY"));
    }
}
```

### Semantic Search Service
```java
@Service
public class SemanticSearchService {
    
    private final EmbeddingStore<TextSegment> store;
    private final EmbeddingModel embeddingModel;
    
    public List<String> search(String query, int maxResults) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(maxResults)
            .minScore(0.75)
            .build();
        
        return store.search(request).matches().stream()
            .map(match -> match.embedded().text())
            .toList();
    }
}
```

### Production Setup with Monitoring
```java
@Configuration
public class ProductionVectorStoreConfig {
    
    @Bean
    public EmbeddingStore<TextSegment> vectorStore(
            @Value("${vector.store.host}") String host,
            MeterRegistry meterRegistry) {
        
        EmbeddingStore<TextSegment> store = PgVectorEmbeddingStore.builder()
            .host(host)
            .database("production_vectors")
            .useIndex(true)
            .indexListSize(200)
            .build();
        
        return new MonitoredEmbeddingStore<>(store, meterRegistry);
    }
}
```

## Summary

This skill provides comprehensive LangChain4J vector store configuration covering:

1. **EmbeddingStore Interface**: Unified API for vector operations across different providers
2. **Supported Stores**: Configuration for PostgreSQL, Pinecone, MongoDB, Neo4j, Milvus, and more
3. **Configuration Patterns**: Environment-based, conditional, and multi-store configurations
4. **Advanced Features**: Hybrid search, metadata filtering, and document ingestion
5. **API Reference**: Complete parameter documentation and search request configuration
6. **Workflow Patterns**: Multi-store setups, health checks, and migration strategies
7. **Best Practices**: Store selection, indexing, performance optimization, and security
8. **Production Readiness**: Connection pooling, batch operations, monitoring, and scaling

The patterns and configurations are based on official LangChain4J documentation (Trust Score: 7.5) and represent current best practices for vector store integration in enterprise Java applications.