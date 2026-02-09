# LangChain4j Vector Stores - API References

Complete API reference for configuring and using vector stores with LangChain4j.

## Vector Store Comparison

| Store      | Setup       | Performance | Scaling        | Features            |
|------------|-------------|-------------|----------------|---------------------|
| In-Memory  | Easy        | Fast        | Single machine | Testing             |
| Pinecone   | SaaS        | Fast        | Automatic      | Namespace, Metadata |
| Weaviate   | Self-hosted | Medium      | Manual         | Hybrid search       |
| Qdrant     | Self-hosted | Fast        | Manual         | Filtering, GRPC     |
| Chroma     | Self-hosted | Medium      | Manual         | Simple API          |
| PostgreSQL | Existing DB | Medium      | Manual         | SQL, pgvector       |
| MongoDB    | SaaS/Self   | Medium      | Automatic      | Document store      |
| Neo4j      | Self-hosted | Medium      | Manual         | Graph + Vector      |
| Milvus     | Self-hosted | Very Fast   | Manual         | Large scale         |

## EmbeddingStore Interface

### Core Methods

```java
public interface EmbeddingStore<Embedded> {

    // Add single embedding
    String add(Embedding embedding);

    String add(String id, Embedding embedding);

    String add(Embedding embedding, Embedded embedded);

    // Add multiple embeddings
    List<String> addAll(List<Embedding> embeddings);

    List<String> addAll(List<Embedding> embeddings, List<Embedded> embeddeds);

    List<String> addAll(List<String> ids, List<Embedding> embeddings, List<Embedded> embeddeds);

    // Search
    EmbeddingSearchResult<Embedded> search(EmbeddingSearchRequest request);

    // Remove
    void remove(String id);

    void removeAll(Collection<String> ids);

    void removeAll(Filter filter);

    void removeAll();
}
```

## EmbeddingSearchRequest

### Building Search Requests

```java
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(embedding)                    // Required
        .maxResults(5)                                // Default: 3
        .minScore(0.7)                                // Threshold: 0-1
        .filter(new IsEqualTo("status", "active"))   // Optional
        .build();
```

### EmbeddingSearchResult

```java
EmbeddingSearchResult<TextSegment> result = store.search(request);

List<EmbeddingMatch<TextSegment>> matches = result.matches();
for(
EmbeddingMatch<TextSegment> match :matches){
double score = match.score();               // 0-1 similarity
TextSegment segment = match.embedded();     // Retrieved content
String id = match.embeddingId();            // Unique ID
}
```

## Vector Store Configurations

### InMemoryEmbeddingStore

```java
EmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();

// Merge multiple stores
InMemoryEmbeddingStore<TextSegment> merged =
        InMemoryEmbeddingStore.merge(store1, store2);
```

### PineconeEmbeddingStore

```java
PineconeEmbeddingStore store = PineconeEmbeddingStore.builder()
        .apiKey(apiKey)                    // Required
        .indexName("index-name")           // Required
        .namespace("namespace")            // Optional: organize data
        .environment("gcp-starter")        // or "aws-us-east-1"
        .build();
```

### WeaviateEmbeddingStore

```java
WeaviateEmbeddingStore store = WeaviateEmbeddingStore.builder()
        .host("localhost")                // Required
        .port(8080)                       // Default: 8080
        .scheme("http")                   // "http" or "https"
        .collectionName("Documents")      // Required
        .apiKey("optional-key")
        .useGrpc(false)                   // Use REST or gRPC
        .build();
```

### QdrantEmbeddingStore

```java
QdrantEmbeddingStore store = QdrantEmbeddingStore.builder()
        .host("localhost")                // Required
        .port(6333)                       // Default: 6333
        .collectionName("documents")      // Required
        .https(false)                     // SSL/TLS
        .apiKey("optional-key")           // For authentication
        .preferGrpc(true)                 // gRPC or REST
        .timeout(Duration.ofSeconds(30))  // Connection timeout
        .build();
```

### ChromaEmbeddingStore

```java
ChromaEmbeddingStore store = ChromaEmbeddingStore.builder()
        .baseUrl("http://localhost:8000")  // Required
        .collectionName("my-collection")   // Required
        .apiKey("optional")                // For authentication
        .logRequests(true)                 // Debug logging
        .logResponses(true)
        .build();
```

### PgVectorEmbeddingStore

```java
PgVectorEmbeddingStore store = PgVectorEmbeddingStore.builder()
        .host("localhost")                 // Required
        .port(5432)                        // Default: 5432
        .database("embeddings")            // Required
        .user("postgres")                  // Required
        .password("password")              // Required
        .table("embeddings")               // Custom table name
        .createTableIfNotExists(true)      // Auto-create table
        .dropTableIfExists(false)          // Safety flag
        .build();
```

### MongoDbEmbeddingStore

```java
MongoDbEmbeddingStore store = MongoDbEmbeddingStore.builder()
        .databaseName("search")            // Required
        .collectionName("documents")       // Required
        .createIndex(true)                 // Auto-create index
        .indexName("vector_index")         // Index name
        .indexMapping(indexMapping)        // Index configuration
        .fromClient(mongoClient)           // Required
        .build();

// Configure index mapping
IndexMapping mapping = IndexMapping.builder()
        .dimension(1536)                   // Vector dimension
        .metadataFieldNames(Set.of("userId", "source"))
        .build();
```

### Neo4jEmbeddingStore

```java
Neo4jEmbeddingStore store = Neo4jEmbeddingStore.builder()
        .withBasicAuth(uri, user, password)  // Required
        .dimension(1536)                     // Vector dimension
        .label("Document")                   // Node label
        .embeddingProperty("embedding")      // Property name
        .textProperty("text")                // Text content property
        .metadataPrefix("metadata_")         // Metadata prefix
        .build();
```

### MilvusEmbeddingStore

```java
MilvusEmbeddingStore store = MilvusEmbeddingStore.builder()
        .host("localhost")                 // Required
        .port(19530)                       // Default: 19530
        .collectionName("documents")       // Required
        .dimension(1536)                   // Vector dimension
        .indexType(IndexType.HNSW)         // HNSW, IVF_FLAT, IVF_SQ8
        .metricType(MetricType.COSINE)     // COSINE, L2, IP
        .username("root")                  // Optional
        .password("Milvus")                // Optional
        .build();
```

## Metadata and Filtering

### Filter Operations

```java
// Equality
new IsEqualTo("status","active")
new

IsNotEqualTo("archived","true")

// Comparison
new

IsGreaterThan("score",0.8)
new

IsLessThanOrEqualTo("days",30)
new

IsGreaterThanOrEqualTo("priority",5)
new

IsLessThan("errorRate",0.01)

// Membership
new

IsIn("category",Arrays.asList("tech", "guide"))
        new

IsNotIn("status",Arrays.asList("deleted"))

// String operations
        new

ContainsString("content","Spring")

// Logical
new

And(filter1, filter2)
new

Or(filter1, filter2)
new

Not(filter1)
```

### Dynamic Filtering

```java
.dynamicFilter(query ->{
String userId = extractUserIdFromQuery(query);
    return new

IsEqualTo("userId",userId);
})
```

## Integration with EmbeddingStoreIngestor

### Basic Ingestor

```java
EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
        .embeddingModel(embeddingModel)    // Required
        .embeddingStore(store)             // Required
        .build();

IngestionResult result = ingestor.ingest(document);
```

### Advanced Ingestor

```java
EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
        .documentTransformer(doc -> {
            doc.metadata().put("ingested_date", LocalDate.now());
            return doc;
        })
        .documentSplitter(DocumentSplitters.recursive(500, 50))
        .textSegmentTransformer(segment -> {
            String enhanced = "File: " + segment.metadata().getString("filename") +
                              "\n" + segment.text();
            return TextSegment.from(enhanced, segment.metadata());
        })
        .embeddingModel(embeddingModel)
        .embeddingStore(store)
        .build();

ingestor.

ingest(documents);
```

## ContentRetriever Integration

### Basic Retriever

```java
ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
        .embeddingStore(embeddingStore)
        .embeddingModel(embeddingModel)
        .maxResults(3)
        .minScore(0.7)
        .build();
```

### Advanced Retriever

```java
ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
        .embeddingStore(embeddingStore)
        .embeddingModel(embeddingModel)
        .dynamicMaxResults(query -> 10)
        .dynamicMinScore(query -> 0.75)
        .dynamicFilter(query ->
                new IsEqualTo("userId", getCurrentUserId())
        )
        .build();
```

## Multi-Tenant Support

### Namespace-based Isolation (Pinecone)

```java
// User 1
var store1 = PineconeEmbeddingStore.builder()
                .apiKey(key)
                .indexName("docs")
                .namespace("user-1")
                .build();

// User 2
var store2 = PineconeEmbeddingStore.builder()
        .apiKey(key)
        .indexName("docs")
        .namespace("user-2")
        .build();
```

### Metadata-based Isolation

```java
.dynamicFilter(query ->
        new

IsEqualTo("userId",getContextUserId())
        )
```

## Performance Optimization

### Connection Configuration

```java
// With timeout and pooling
store =QdrantEmbeddingStore.

builder()
    .

host("localhost")
    .

port(6333)
    .

timeout(Duration.ofSeconds(30))
        .

maxConnections(10)
    .

build();
```

### Batch Operations

```java
// Batch add
List<Embedding> embeddings = embeddingModel.embedAll(segments).content();
List<String> ids = store.addAll(embeddings, segments);
```

### Caching Strategy

```java
// Cache results locally
Map<String, List<Content>> cache = new HashMap<>();
```

## Monitoring and Debugging

### Enable Logging

```java
ChromaEmbeddingStore store = ChromaEmbeddingStore.builder()
        .baseUrl("http://localhost:8000")
        .collectionName("docs")
        .logRequests(true)
        .logResponses(true)
        .build();
```

## Best Practices

1. **Choose Right Store**: In-memory for dev, Pinecone/Qdrant for production
2. **Configure Dimension**: Match embedding model dimension (usually 1536)
3. **Set Thresholds**: Adjust minScore based on precision needs (0.7-0.85 typical)
4. **Use Metadata**: Add rich metadata for filtering and traceability
5. **Index Strategically**: Create indexes on frequently filtered fields
6. **Monitor Performance**: Track query latency and relevance metrics
7. **Plan Scaling**: Consider multi-tenancy and sharding strategies
8. **Backup Data**: Implement backup and recovery procedures
9. **Version Management**: Track embedding model versions
10. **Test Thoroughly**: Validate retrieval quality with sample queries
