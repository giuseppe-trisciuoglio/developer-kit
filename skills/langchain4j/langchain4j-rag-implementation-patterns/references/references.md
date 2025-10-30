# LangChain4j RAG Implementation - API References

Complete API reference for implementing RAG systems with LangChain4j.

## Document Loading

### Document Loaders

**FileSystemDocumentLoader**: Load from filesystem.
```java
import dev.langchain4j.data.document.loader.FileSystemDocumentLoader;
import java.nio.file.Path;

List<Document> documents = FileSystemDocumentLoader.load("documents");
List<Document> single = FileSystemDocumentLoader.load("document.pdf");
```

**ClassPathDocumentLoader**: Load from classpath resources.
```java
List<Document> resources = ClassPathDocumentLoader.load("documents");
```

**UrlDocumentLoader**: Load from web URLs.
```java
Document webDoc = UrlDocumentLoader.load("https://example.com/doc.html");
```

## Document Splitting

### DocumentSplitter Interface

```java
interface DocumentSplitter {
    List<TextSegment> split(Document document);
    List<TextSegment> splitAll(Collection<Document> documents);
}
```

### DocumentSplitters Factory

**Recursive Split**: Smart recursive splitting by paragraphs, sentences, words.
```java
DocumentSplitter splitter = DocumentSplitters.recursive(
    500,     // Max segment size (tokens or characters)
    50       // Overlap size
);

// With token counting
DocumentSplitter splitter = DocumentSplitters.recursive(
    500,
    50,
    new OpenAiTokenCountEstimator("gpt-4o-mini")
);
```

**Paragraph Split**: Split by paragraphs.
```java
DocumentSplitter splitter = DocumentSplitters.byParagraph(500, 50);
```

**Sentence Split**: Split by sentences.
```java
DocumentSplitter splitter = DocumentSplitters.bySentence(500, 50);
```

**Line Split**: Split by lines.
```java
DocumentSplitter splitter = DocumentSplitters.byLine(500, 50);
```

## Embedding Models

### EmbeddingModel Interface

```java
public interface EmbeddingModel {
    // Embed single text
    Response<Embedding> embed(String text);
    Response<Embedding> embed(TextSegment textSegment);
    
    // Batch embedding
    Response<List<Embedding>> embedAll(List<TextSegment> textSegments);
    
    // Model dimension
    int dimension();
}
```

### OpenAI Embedding Model

```java
EmbeddingModel model = OpenAiEmbeddingModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName("text-embedding-3-small")  // or text-embedding-3-large
    .dimensions(512)                       // Optional: reduce dimensions
    .timeout(Duration.ofSeconds(30))
    .logRequests(true)
    .logResponses(true)
    .build();
```

### Other Embedding Models

```java
// Google Vertex AI
EmbeddingModel google = VertexAiEmbeddingModel.builder()
    .project("PROJECT_ID")
    .location("us-central1")
    .modelName("textembedding-gecko")
    .build();

// Ollama (local)
EmbeddingModel ollama = OllamaEmbeddingModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("all-minilm")
    .build();

// AllMiniLmL6V2 (offline)
EmbeddingModel offline = new AllMiniLmL6V2EmbeddingModel();
```

## Vector Stores (EmbeddingStore)

### EmbeddingStore Interface

```java
public interface EmbeddingStore<Embedded> {
    // Add embeddings
    String add(Embedding embedding);
    String add(String id, Embedding embedding);
    String add(Embedding embedding, Embedded embedded);
    List<String> addAll(List<Embedding> embeddings);
    List<String> addAll(List<Embedding> embeddings, List<Embedded> embeddeds);
    List<String> addAll(List<String> ids, List<Embedding> embeddings, List<Embedded> embeddeds);
    
    // Search embeddings
    EmbeddingSearchResult<Embedded> search(EmbeddingSearchRequest request);
    
    // Remove embeddings
    void remove(String id);
    void removeAll(Collection<String> ids);
    void removeAll(Filter filter);
    void removeAll();
}
```

### In-Memory Store

```java
EmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();

// Merge stores
InMemoryEmbeddingStore<TextSegment> merged = InMemoryEmbeddingStore.merge(
    store1, store2, store3
);
```

### Pinecone

```java
EmbeddingStore<TextSegment> store = PineconeEmbeddingStore.builder()
    .apiKey(System.getenv("PINECONE_API_KEY"))
    .index("my-index")
    .namespace("production")
    .environment("gcp-starter")  // or "aws-us-east-1"
    .build();
```

### Weaviate

```java
EmbeddingStore<TextSegment> store = WeaviateEmbeddingStore.builder()
    .host("localhost")
    .port(8080)
    .scheme("http")
    .collectionName("Documents")
    .build();
```

### Qdrant

```java
EmbeddingStore<TextSegment> store = QdrantEmbeddingStore.builder()
    .host("localhost")
    .port(6333)
    .collectionName("documents")
    .build();
```

### Chroma

```java
EmbeddingStore<TextSegment> store = ChromaEmbeddingStore.builder()
    .baseUrl("http://localhost:8000")
    .collectionName("my-collection")
    .build();
```

### Neo4j

```java
EmbeddingStore<TextSegment> store = Neo4jEmbeddingStore.builder()
    .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
    .dimension(1536)
    .label("Document")
    .build();
```

### MongoDB Atlas

```java
EmbeddingStore<TextSegment> store = MongoDbEmbeddingStore.builder()
    .databaseName("search")
    .collectionName("documents")
    .indexName("vector_index")
    .createIndex(true)
    .fromClient(mongoClient)
    .build();
```

### PostgreSQL (pgvector)

```java
EmbeddingStore<TextSegment> store = PgVectorEmbeddingStore.builder()
    .host("localhost")
    .port(5432)
    .database("embeddings")
    .user("postgres")
    .password("password")
    .table("embeddings")
    .createTableIfNotExists(true)
    .build();
```

### Milvus

```java
EmbeddingStore<TextSegment> store = MilvusEmbeddingStore.builder()
    .host("localhost")
    .port(19530)
    .collectionName("documents")
    .dimension(1536)
    .build();
```

## Document Ingestion

### EmbeddingStoreIngestor

```java
public class EmbeddingStoreIngestor {
    public static Builder builder();
    
    public IngestionResult ingest(Document document);
    public IngestionResult ingest(Document... documents);
    public IngestionResult ingest(Collection<Document> documents);
}
```

### Building an Ingestor

```java
EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
    
    // Document transformation
    .documentTransformer(doc -> {
        doc.metadata().put("source", "manual");
        return doc;
    })
    
    // Document splitting strategy
    .documentSplitter(DocumentSplitters.recursive(500, 50))
    
    // Text segment transformation
    .textSegmentTransformer(segment -> {
        String enhanced = "Category: Spring\n" + segment.text();
        return TextSegment.from(enhanced, segment.metadata());
    })
    
    // Embedding model (required)
    .embeddingModel(embeddingModel)
    
    // Embedding store (required)
    .embeddingStore(embeddingStore)
    
    .build();
```

### IngestionResult

```java
IngestionResult result = ingestor.ingest(documents);

// Access results
TokenUsage usage = result.tokenUsage();
long totalTokens = usage.totalTokenCount();
long inputTokens = usage.inputTokenCount();
```

## Content Retrieval

### EmbeddingSearchRequest

```java
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
    .queryEmbedding(embedding)           // Required
    .maxResults(5)                       // Default: 3
    .minScore(0.7)                       // Threshold 0-1
    .filter(new IsEqualTo("category", "tutorial"))
    .build();
```

### EmbeddingSearchResult

```java
EmbeddingSearchResult<TextSegment> result = store.search(request);
List<EmbeddingMatch<TextSegment>> matches = result.matches();

for (EmbeddingMatch<TextSegment> match : matches) {
    double score = match.score();           // Relevance 0-1
    TextSegment segment = match.embedded(); // Retrieved content
    String id = match.embeddingId();        // Store ID
}
```

### ContentRetriever Interface

```java
public interface ContentRetriever {
    Content retrieve(Query query);
    List<Content> retrieveAll(List<Query> queries);
}
```

### EmbeddingStoreContentRetriever

```java
ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
    .embeddingStore(embeddingStore)
    .embeddingModel(embeddingModel)
    
    // Static configuration
    .maxResults(5)
    .minScore(0.7)
    
    // Dynamic configuration per query
    .dynamicMaxResults(query -> 10)
    .dynamicMinScore(query -> 0.8)
    .dynamicFilter(query -> 
        new IsEqualTo("userId", extractUserId(query))
    )
    
    .build();
```

## Advanced RAG

### RetrievalAugmentor

```java
public interface RetrievalAugmentor {
    AugmentationResult augment(UserMessage message);
    AugmentationResult augmentAll(List<UserMessage> messages);
}
```

### DefaultRetrievalAugmentor

```java
RetrievalAugmentor augmentor = DefaultRetrievalAugmentor.builder()
    
    // Query transformation
    .queryTransformer(new CompressingQueryTransformer(chatModel))
    
    // Content retrieval
    .contentRetriever(contentRetriever)
    
    // Content aggregation and re-ranking
    .contentAggregator(ReRankingContentAggregator.builder()
        .scoringModel(scoringModel)
        .minScore(0.8)
        .build())
    
    // Parallelization
    .executor(customExecutor)
    
    .build();
```

### Use with AI Services

```java
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .retrievalAugmentor(augmentor)
    .build();
```

## Metadata and Filtering

### Metadata Object

```java
// Create from map
Metadata meta = Metadata.from(Map.of(
    "userId", "user123",
    "category", "tutorial",
    "score", 0.95
));

// Add entries
meta.put("status", "active");
meta.put("version", 2);

// Retrieve entries
String userId = meta.getString("userId");
int version = meta.getInt("version");
double score = meta.getDouble("score");

// Check existence
boolean has = meta.containsKey("userId");

// Remove entry
meta.remove("userId");

// Merge
Metadata other = Metadata.from(Map.of("source", "db"));
meta.merge(other);
```

### Filter Operations

```java
import dev.langchain4j.store.embedding.filter.comparison.*;
import dev.langchain4j.store.embedding.filter.logical.*;

// Equality
Filter filter = new IsEqualTo("status", "active");
Filter filter = new IsNotEqualTo("deprecated", "true");

// Comparison
Filter filter = new IsGreaterThan("score", 0.8);
Filter filter = new IsLessThanOrEqualTo("daysOld", 30);
Filter filter = new IsGreaterThanOrEqualTo("priority", 5);
Filter filter = new IsLessThan("errorRate", 0.01);

// Membership
Filter filter = new IsIn("category", Arrays.asList("tech", "guide"));
Filter filter = new IsNotIn("status", Arrays.asList("archived"));

// String operations
Filter filter = new ContainsString("content", "Spring");

// Logical operations
Filter filter = new And(
    new IsEqualTo("userId", "123"),
    new IsGreaterThan("score", 0.7)
);

Filter filter = new Or(
    new IsEqualTo("type", "doc"),
    new IsEqualTo("type", "guide")
);

Filter filter = new Not(new IsEqualTo("archived", "true"));
```

## TextSegment

### Creating TextSegments

```java
// Text only
TextSegment segment = TextSegment.from("This is the content");

// With metadata
Metadata metadata = Metadata.from(Map.of("source", "docs"));
TextSegment segment = TextSegment.from("Content", metadata);

// Accessing
String text = segment.text();
Metadata meta = segment.metadata();
```

## Best Practices

1. **Chunk Size**: Use 300-500 tokens per chunk for optimal balance
2. **Overlap**: Use 10-50 token overlap for semantic continuity
3. **Metadata**: Include source and timestamp for traceability
4. **Batch Processing**: Ingest documents in batches when possible
5. **Similarity Threshold**: Adjust minScore (0.7-0.85) based on precision/recall needs
6. **Vector DB Selection**: In-memory for dev/test, Pinecone/Qdrant for production
7. **Filtering**: Pre-filter by metadata to reduce search space
8. **Re-ranking**: Use scoring models for better relevance in production
9. **Monitoring**: Track retrieval quality metrics
10. **Testing**: Use small in-memory stores for unit tests

## Performance Tips

- Use recursive splitting for semantic coherence
- Enable batch processing for large datasets
- Use dynamic max results based on query complexity
- Cache embedding model for frequently accessed content
- Implement async ingestion for large document collections
- Monitor token usage for cost optimization
- Use appropriate vector DB indexes for scale
