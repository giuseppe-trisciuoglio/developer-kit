# Qdrant for Java: Complete Examples

This file provides comprehensive code examples for integrating Qdrant with Java and Spring Boot applications.

## 1. Complete Spring Boot Application with Qdrant

This example demonstrates a full Spring Boot application with Qdrant integration for vector search.

### Project Structure
```
/src/main/java/com/example/qdrantdemo/
├── QdrantDemoApplication.java
├── config/
│   ├── QdrantConfig.java
│   └── Langchain4jConfig.java
├── controller/
│   ├── SearchController.java
│   └── RagController.java
├── service/
│   ├── VectorSearchService.java
│   └── RagService.java
└── Application.properties
```

### Dependencies (pom.xml)
```xml
<dependencies>
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Qdrant Java Client -->
    <dependency>
        <groupId>io.qdrant</groupId>
        <artifactId>client</artifactId>
        <version>1.15.0</version>
    </dependency>

    <!-- LangChain4j -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j</artifactId>
        <version>1.7.0</version>
    </dependency>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-qdrant</artifactId>
        <version>1.7.0</version>
    </dependency>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-all-minilm-l6-v2</artifactId>
        <version>1.7.0</version>
    </dependency>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai</artifactId>
        <version>1.7.0</version>
    </dependency>
</dependencies>
```

### Application Configuration (application.properties)
```properties
# Qdrant Configuration
qdrant.host=localhost
qdrant.port=6334
qdrant.api-key=

# OpenAI Configuration (for RAG)
openai.api-key=YOUR_OPENAI_API_KEY
```

### Qdrant Configuration
```java
package com.example.qdrantdemo.config;

import io.qdrant.client.QdrantClient;
import io.qdrant.client.QdrantGrpcClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class QdrantConfig {

    @Value("${qdrant.host:localhost}")
    private String host;

    @Value("${qdrant.port:6334}")
    private int port;

    @Value("${qdrant.api-key:}")
    private String apiKey;

    @Bean
    public QdrantClient qdrantClient() {
        QdrantGrpcClient grpcClient = QdrantGrpcClient.newBuilder(host, port, false)
            .withApiKey(apiKey)
            .build();

        return new QdrantClient(grpcClient);
    }
}
```

### Vector Search Service
```java
package com.example.qdrantdemo.service;

import io.qdrant.client.QdrantClient;
import io.qdrant.client.grpc.Collections.Distance;
import io.qdrant.client.grpc.Collections.VectorParams;
import io.qdrant.client.grpc.Points.PointStruct;
import io.qdrant.client.grpc.Points.QueryPoints;
import io.qdrant.client.grpc.Points.ScoredPoint;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;

import static io.qdrant.client.PointIdFactory.id;
import static io.qdrant.client.ValueFactory.value;
import static io.qdrant.client.VectorsFactory.vectors;
import static io.qdrant.client.QueryFactory.nearest;

@Service
public class VectorSearchService {

    private final QdrantClient client;

    @Autowired
    private EmbeddingService embeddingService; // Helper service for embeddings

    public static final String COLLECTION_NAME = "document-search";
    public static final int VECTOR_SIZE = 384; // For AllMiniLM-L6-v2

    public VectorSearchService(QdrantClient client) {
        this.client = client;
    }

    @PostConstruct
    public void initializeCollection() throws ExecutionException, InterruptedException {
        // Create collection if it doesn't exist
        client.createCollectionAsync(COLLECTION_NAME,
            VectorParams.newBuilder()
                .setDistance(Distance.Cosine)
                .setSize(VECTOR_SIZE)
                .build()
        ).get();
    }

    public List<ScoredPoint> search(String query, int limit) {
        try {
            List<Float> queryVector = embeddingService.embedQuery(query);

            return client.queryAsync(
                QueryPoints.newBuilder()
                    .setCollectionName(COLLECTION_NAME)
                    .setLimit(limit)
                    .setQuery(nearest(queryVector))
                    .setWithPayload(true)
                    .build()
            ).get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Qdrant search failed", e);
        }
    }

    public void addDocument(String documentId, String title, String content) {
        try {
            List<Float> contentVector = embeddingService.embedText(content);

            PointStruct point = PointStruct.newBuilder()
                .setId(id(documentId))
                .setVectors(vectors(contentVector))
                .putAllPayload(Map.of(
                    "title", value(title),
                    "content", value(content),
                    "created_at", value(System.currentTimeMillis())
                ))
                .build();

            client.upsertAsync(COLLECTION_NAME, List.of(point)).get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Qdrant document insertion failed", e);
        }
    }
}
```

### Search Controller
```java
package com.example.qdrantdemo.controller;

import com.example.qdrantdemo.service.VectorSearchService;
import io.qdrant.client.grpc.Points.ScoredPoint;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/search")
public class SearchController {

    private final VectorSearchService searchService;

    public SearchController(VectorSearchService searchService) {
        this.searchService = searchService;
    }

    @GetMapping
    public List<ScoredPoint> search(@RequestParam String query,
                                   @RequestParam(defaultValue = "5") int limit) {
        return searchService.search(query, limit);
    }

    @PostMapping("/document")
    public String addDocument(@RequestBody AddDocumentRequest request) {
        searchService.addDocument(request.getDocumentId(), request.getTitle(), request.getContent());
        return "Document added successfully";
    }

    public static class AddDocumentRequest {
        private String documentId;
        private String title;
        private String content;

        // Getters and setters
        public String getDocumentId() { return documentId; }
        public void setDocumentId(String documentId) { this.documentId = documentId; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getContent() { return content; }
        public void setContent(String content) { this.content = content; }
    }
}
```

## 2. Advanced RAG with LangChain4j

This example demonstrates a complete RAG system with Qdrant and LLM integration.

### LangChain4j Configuration
```java
package com.example.qdrantdemo.config;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.embedding.EmbeddingModel;
import dev.langchain4j.embedding.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.qdrant.QdrantEmbeddingStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class Langchain4jConfig {

    @Value("${qdrant.host:localhost}")
    private String host;

    @Value("${qdrant.port:6334}")
    private int port;

    @Value("${qdrant.api-key:}")
    private String apiKey;

    @Value("${openai.api-key}")
    private String openaiApiKey;

    @Bean
    public EmbeddingStore<TextSegment> embeddingStore() {
        return QdrantEmbeddingStore.builder()
            .collectionName("rag-collection")
            .host(host)
            .port(port)
            .apiKey(apiKey)
            .build();
    }

    @Bean
    public EmbeddingModel embeddingModel() {
        return new AllMiniLmL6V2EmbeddingModel();
    }

    @Bean
    public ChatLanguageModel chatLanguageModel() {
        return OpenAiChatModel.builder()
            .apiKey(openaiApiKey)
            .modelName("gpt-3.5-turbo")
            .build();
    }

    @Bean
    public EmbeddingStoreIngestor embeddingStoreIngestor(
            EmbeddingStore<TextSegment> embeddingStore,
            EmbeddingModel embeddingModel) {
        return EmbeddingStoreIngestor.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .build();
    }
}
```

### RAG Service with Assistant
```java
package com.example.qdrantdemo.service;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RagService {

    // Define the AI assistant interface
    interface Assistant {
        String chat(String userMessage);
    }

    private final EmbeddingStoreIngestor ingestor;
    private final Assistant assistant;

    public RagService(EmbeddingStore<TextSegment> embeddingStore,
                     EmbeddingStoreIngestor ingestor,
                     ChatLanguageModel chatModel) {

        this.ingestor = ingestor;

        // Create content retriever for RAG
        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .maxResults(3)
            .minScore(0.7)
            .build();

        // Build the AI assistant with RAG capabilities
        this.assistant = AiServices.builder(Assistant.class)
            .chatLanguageModel(chatModel)
            .contentRetriever(contentRetriever)
            .build();
    }

    public void ingestDocument(String text) {
        TextSegment segment = TextSegment.from(text);
        ingestor.ingest(segment);
    }

    public String query(String userQuery) {
        return assistant.chat(userQuery);
    }

    public List<TextSegment> findRelevantDocuments(String query, int maxResults) {
        EmbeddingStore<TextSegment> embeddingStore = ingestor.getEmbeddingStore();
        return embeddingStore.findRelevant(
            ingestor.getEmbeddingModel().embed(query).content(),
            maxResults,
            0.7
        ).stream()
            .map(match -> match.embedded())
            .toList();
    }
}
```

### RAG Controller
```java
package com.example.qdrantdemo.controller;

import com.example.qdrantdemo.service.RagService;
import dev.langchain4j.data.segment.TextSegment;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rag")
public class RagController {

    private final RagService ragService;

    public RagController(RagService ragService) {
        this.ragService = ragService;
    }

    @PostMapping("/ingest")
    public String ingestDocument(@RequestBody String document) {
        ragService.ingestDocument(document);
        return "Document ingested successfully.";
    }

    @PostMapping("/query")
    public String query(@RequestBody QueryRequest request) {
        return ragService.query(request.getQuery());
    }

    @GetMapping("/documents")
    public List<TextSegment> findDocuments(@RequestParam String query,
                                          @RequestParam(defaultValue = "3") int maxResults) {
        return ragService.findRelevantDocuments(query, maxResults);
    }

    public static class QueryRequest {
        private String query;

        public String getQuery() { return query; }
        public void setQuery(String query) { this.query = query; }
    }
}
```

## 3. Multi-tenant Vector Search Application

This example demonstrates advanced patterns for multi-tenant applications.

### Multi-Tenant Vector Service
```java
package com.example.qdrantdemo.service;

import io.qdrant.client.QdrantClient;
import io.qdrant.client.grpc.Points.PointStruct;
import io.qdrant.client.grpc.Points.QueryPoints;
import io.qdrant.client.grpc.Points.ScoredPoint;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.ExecutionException;

@Service
public class MultiTenantVectorService {

    private final QdrantClient client;

    public MultiTenantVectorService(QdrantClient client) {
        this.client = client;
    }

    // Collection-based multi-tenancy
    public List<ScoredPoint> searchByTenant(String tenantId, List<Float> queryVector, int limit) {
        try {
            String collectionName = "tenant_" + tenantId + "_documents";

            return client.queryAsync(
                QueryPoints.newBuilder()
                    .setCollectionName(collectionName)
                    .setLimit(limit)
                    .addAllVector(queryVector)
                    .setWithPayload(true)
                    .build()
            ).get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Multi-tenant search failed", e);
        }
    }

    public void upsertForTenant(String tenantId, List<PointStruct> points) {
        try {
            String collectionName = "tenant_" + tenantId + "_documents";
            client.upsertAsync(collectionName, points).get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Multi-tenant upsert failed", e);
        }
    }

    // Hybrid search with tenant-specific filters
    public List<ScoredPoint> hybridSearch(String tenantId, List<Float> queryVector,
                                        String category, int limit) {
        try {
            String collectionName = "tenant_" + tenantId + "_documents";

            QueryPoints.Builder queryBuilder = QueryPoints.newBuilder()
                .setCollectionName(collectionName)
                .setLimit(limit)
                .addAllVector(queryVector);

            // Add category filter if provided
            if (category != null && !category.isEmpty()) {
                queryBuilder.setFilter(Filter.newBuilder()
                    .addMust(exactMatch("category", category))
                    .build());
            }

            return client.queryAsync(queryBuilder.build()).get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Hybrid search failed", e);
        }
    }
}
```

## Deployment and Configuration

### Docker Compose Setup
```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:v1.7.0
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334

volumes:
  qdrant_storage:
```

### Production Configuration
```properties
# application-prod.properties
qdrant.host=qdrant-service
qdrant.port=6334
qdrant.api-key=${QDRANT_API_KEY}

# Enable HTTPS for production
server.ssl.enabled=true
server.ssl.key-store=classpath:keystore.p12
server.ssl.key-store-password=${SSL_KEYSTORE_PASSWORD}

# OpenAI Configuration
openai.api-key=${OPENAI_API_KEY}

# Logging
logging.level.com.example.qdrantdemo=INFO
logging.level.io.qdrant=INFO
```

## Testing Strategy

### Unit Tests for Vector Service
```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
public class VectorSearchServiceTest {

    @Autowired
    private VectorSearchService vectorSearchService;

    @Test
    public void testCollectionInitialization() {
        // Test that collection is created properly
        // This could involve checking collection metadata
    }

    @Test
    public void testDocumentUpsert() {
        // Test document insertion and retrieval
    }

    @Test
    public void testSearchFunctionality() {
        // Test vector search functionality
    }
}
```

This comprehensive example provides a complete foundation for building Qdrant-powered applications with Spring Boot and LangChain4j.
