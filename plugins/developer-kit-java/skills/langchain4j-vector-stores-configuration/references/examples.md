# LangChain4j Vector Stores Configuration - Practical Examples

Production-ready examples for configuring and using various vector stores with LangChain4j.

## 1. In-Memory Vector Store (Development)

**Scenario**: Quick development and testing without external dependencies.

```java
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.data.embedding.Embedding;

public class InMemoryStoreExample {
    public static void main(String[] args) {
        var store = new InMemoryEmbeddingStore<TextSegment>();
        
        // Add embeddings
        Embedding embedding1 = new Embedding(new float[]{0.1f, 0.2f, 0.3f});
        String id1 = store.add("doc-001", embedding1, 
            TextSegment.from("Spring Boot documentation"));
        
        // Search
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(embedding1)
            .maxResults(5)
            .build();
            
        var results = store.search(request);
        results.matches().forEach(match -> 
            System.out.println("Score: " + match.score())
        );
        
        // Remove
        store.remove(id1);
    }
}
```

## 2. Pinecone Vector Store (Production)

**Scenario**: Serverless vector database for scalable RAG.

```java
import dev.langchain4j.store.embedding.pinecone.PineconeEmbeddingStore;

public class PineconeStoreExample {
    public static void main(String[] args) {
        var store = PineconeEmbeddingStore.builder()
            .apiKey(System.getenv("PINECONE_API_KEY"))
            .indexName("my-index")
            .namespace("production")         // Optional: organize by namespace
            .dimension(1536)                 // Match embedding model
            .build();
        
        // Setup embedding model and ingestor
        var embeddingModel = OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .build();
        
        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(store)
            .documentSplitter(DocumentSplitters.recursive(500, 50))
            .build();
        
        // Ingest documents
        ingestor.ingest(Document.from("Your document content..."));
    }
}
```

## 3. Weaviate Vector Store

**Scenario**: Open-source vector database with hybrid search.

```java
import dev.langchain4j.store.embedding.weaviate.WeaviateEmbeddingStore;

public class WeaviateStoreExample {
    public static void main(String[] args) {
        var store = WeaviateEmbeddingStore.builder()
            .host("localhost")
            .port(8080)
            .scheme("http")              // or "https"
            .collectionName("Documents")
            .useGrpc(false)              // Use REST endpoint
            .build();
        
        // Use with embedding model
        var embeddingModel = OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .build();
        
        // Add and search
        var embedding = embeddingModel.embed("test").content();
        var segment = TextSegment.from("Document content");
        store.add(embedding, segment);
    }
}
```

## 4. Qdrant Vector Store

**Scenario**: Fast vector search with filtering capabilities.

```java
import dev.langchain4j.store.embedding.qdrant.QdrantEmbeddingStore;

public class QdrantStoreExample {
    public static void main(String[] args) {
        var store = QdrantEmbeddingStore.builder()
            .host("localhost")
            .port(6333)
            .collectionName("documents")
            .https(false)                // Set to true for HTTPS
            .preferGrpc(true)            // Use gRPC for better performance
            .build();
        
        // Configure with metadata filtering
        var retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(store)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .dynamicFilter(query -> 
                new IsEqualTo("source", "documentation")
            )
            .build();
    }
}
```

## 5. Chroma Vector Store

**Scenario**: Easy-to-use local or remote vector store.

```java
import dev.langchain4j.store.embedding.chroma.ChromaEmbeddingStore;

public class ChromaStoreExample {
    public static void main(String[] args) {
        // Local Chroma server
        var store = ChromaEmbeddingStore.builder()
            .baseUrl("http://localhost:8000")
            .collectionName("my-documents")
            .logRequests(true)
            .logResponses(true)
            .build();
        
        // Remote Chroma
        var remoteStore = ChromaEmbeddingStore.builder()
            .baseUrl("https://chroma.example.com")
            .collectionName("production-docs")
            .build();
    }
}
```

## 6. PostgreSQL with pgvector

**Scenario**: Use existing PostgreSQL database for vectors.

```java
import dev.langchain4j.store.embedding.pgvector.PgVectorEmbeddingStore;

public class PostgresStoreExample {
    public static void main(String[] args) {
        var store = PgVectorEmbeddingStore.builder()
            .host("localhost")
            .port(5432)
            .database("embeddings")
            .user("postgres")
            .password("password")
            .table("embeddings")
            .createTableIfNotExists(true)
            .dropTableIfExists(false)
            .build();
        
        // With SSL
        var sslStore = PgVectorEmbeddingStore.builder()
            .host("db.example.com")
            .port(5432)
            .database("embeddings")
            .user("postgres")
            .password("password")
            .sslMode("require")
            .table("embeddings")
            .build();
    }
}
```

## 7. MongoDB Atlas Vector Search

**Scenario**: Store vectors in MongoDB with metadata.

```java
import dev.langchain4j.store.embedding.mongodb.MongoDbEmbeddingStore;
import dev.langchain4j.store.embedding.mongodb.IndexMapping;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;

public class MongoDbStoreExample {
    public static void main(String[] args) {
        MongoClient mongoClient = MongoClients.create(
            System.getenv("MONGODB_URI")
        );
        
        var indexMapping = IndexMapping.builder()
            .dimension(1536)
            .metadataFieldNames(Set.of("source", "userId"))
            .build();
        
        var store = MongoDbEmbeddingStore.builder()
            .databaseName("search")
            .collectionName("documents")
            .createIndex(true)
            .indexName("vector_index")
            .indexMapping(indexMapping)
            .fromClient(mongoClient)
            .build();
        
        // With metadata
        var segment = TextSegment.from(
            "Content",
            Metadata.from(Map.of("source", "docs", "userId", "123"))
        );
        store.add(embedding, segment);
    }
}
```

## 8. Neo4j Graph + Vector Store

**Scenario**: Combine graph relationships with semantic search.

```java
import dev.langchain4j.store.embedding.neo4j.Neo4jEmbeddingStore;
import org.neo4j.driver.Driver;
import org.neo4j.driver.GraphDatabase;

public class Neo4jStoreExample {
    public static void main(String[] args) {
        var store = Neo4jEmbeddingStore.builder()
            .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
            .dimension(1536)
            .label("Document")
            .embeddingProperty("embedding")
            .textProperty("text")
            .metadataPrefix("metadata_")
            .build();
        
        // Hybrid search with full-text index
        var hybridStore = Neo4jEmbeddingStore.builder()
            .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
            .dimension(1536)
            .fullTextIndexName("documents_ft")
            .autoCreateFullText(true)
            .fullTextQuery("Spring")
            .build();
    }
}
```

## 9. Milvus Vector Store

**Scenario**: Open-source vector database for large-scale ML.

```java
import dev.langchain4j.store.embedding.milvus.MilvusEmbeddingStore;
import dev.langchain4j.store.embedding.milvus.IndexType;
import dev.langchain4j.store.embedding.milvus.MetricType;

public class MilvusStoreExample {
    public static void main(String[] args) {
        var store = MilvusEmbeddingStore.builder()
            .host("localhost")
            .port(19530)
            .collectionName("documents")
            .dimension(1536)
            .indexType(IndexType.HNSW)           // or IVF_FLAT, IVF_SQ8
            .metricType(MetricType.COSINE)       // or L2, IP
            .username("root")
            .password("Milvus")
            .autoCreateCollection(true)
            .consistencyLevel("Session")
            .build();
    }
}
```

## 10. Hybrid Store Configuration with Metadata

**Scenario**: Advanced setup with metadata filtering.

```java
import dev.langchain4j.store.embedding.filter.comparison.*;

public class HybridStoreExample {
    public static void main(String[] args) {
        // Create store
        var store = QdrantEmbeddingStore.builder()
            .host("localhost")
            .port(6333)
            .collectionName("multi_tenant_docs")
            .build();
        
        // Ingest with rich metadata
        var ingestor = EmbeddingStoreIngestor.builder()
            .documentTransformer(doc -> {
                doc.metadata().put("userId", "user123");
                doc.metadata().put("source", "api");
                doc.metadata().put("created", LocalDate.now().toString());
                doc.metadata().put("version", 1);
                return doc;
            })
            .documentSplitter(DocumentSplitters.recursive(500, 50))
            .embeddingModel(embeddingModel)
            .embeddingStore(store)
            .build();
        
        // Setup retriever with complex filters
        var retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(store)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .dynamicFilter(query -> {
                // Multi-tenant isolation
                String userId = "user123";
                return new And(
                    new IsEqualTo("userId", userId),
                    new IsEqualTo("version", 1),
                    new IsGreaterThan("score", 0.7)
                );
            })
            .build();
    }
}
```

## Performance Tuning

1. **Batch Size**: Ingest documents in batches of 100-1000
2. **Dimensionality**: Use text-embedding-3-small (1536) unless specific needs
3. **Similarity Threshold**: Adjust minScore based on precision/recall needs
4. **Indexing**: Enable appropriate indexes based on filter patterns
5. **Connection Pooling**: Configure connection pools for production
6. **Timeout**: Set appropriate timeout values for network calls
7. **Caching**: Cache frequently accessed embeddings
8. **Partitioning**: Use namespaces/databases for data isolation
9. **Monitoring**: Track query latency and error rates
10. **Replication**: Enable replication for high availability
