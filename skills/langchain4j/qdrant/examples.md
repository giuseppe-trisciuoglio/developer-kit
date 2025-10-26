# Qdrant for Java: Code Examples

This file provides detailed code examples for integrating Qdrant into a Java and Spring Boot application.

## 1. Complete Spring Boot Application Example

This example demonstrates how to set up a `QdrantClient`, create a collection, upsert data, and search via a REST API endpoint.

### a. Project Structure
```
/src/main/java/com/example/qdrantdemo/
├── QdrantDemoApplication.java
├── config/
│   └── QdrantConfig.java
├── controller/
│   └── SearchController.java
└── service/
    └── QdrantSearchService.java
```

### b. `pom.xml` Dependencies
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>io.qdrant</groupId>
        <artifactId>client</artifactId>
        <version>1.15.0</version>
    </dependency>
    <!-- For embedding generation -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-all-minilm-l6-v2</artifactId>
        <version>1.7.0</version>
    </dependency>
</dependencies>
```

### c. `QdrantConfig.java`
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

    @Bean
    public QdrantClient qdrantClient() {
        return new QdrantClient(
            QdrantGrpcClient.newBuilder(host, port, false).build());
    }
}
```

### d. `QdrantSearchService.java`
```java
package com.example.qdrantdemo.service;

import io.qdrant.client.QdrantClient;
import io.qdrant.client.grpc.Collections.Distance;
import io.qdrant.client.grpc.Collections.VectorParams;
import io.qdrant.client.grpc.Points.PointStruct;
import io.qdrant.client.grpc.Points.QueryPoints;
import io.qdrant.client.grpc.Points.ScoredPoint;
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
public class QdrantSearchService {

    private final QdrantClient client;
    public static final String COLLECTION_NAME = "spring-boot-collection";
    public static final int VECTOR_SIZE = 384; // As per all-MiniLM-L6-v2

    public QdrantSearchService(QdrantClient client) {
        this.client = client;
    }

    @PostConstruct
    public void setup() throws ExecutionException, InterruptedException {
        // Create collection if it doesn't exist
        client.createCollectionAsync(COLLECTION_NAME,
            VectorParams.newBuilder().setDistance(Distance.Cosine).setSize(VECTOR_SIZE).build()
        ).get();

        // Upsert some initial data
        List<PointStruct> points = List.of(
            PointStruct.newBuilder()
                .setId(id(1))
                .setVectors(vectors(generateDummyVector())) // Replace with real embeddings
                .putAllPayload(Map.of("document", value("This is a document about Spring Boot.")))
                .build(),
            PointStruct.newBuilder()
                .setId(id(2))
                .setVectors(vectors(generateDummyVector())) // Replace with real embeddings
                .putAllPayload(Map.of("document", value("Qdrant is a vector database.")))
                .build()
        );
        client.upsertAsync(COLLECTION_NAME, points).get();
    }

    public List<ScoredPoint> search(List<Float> queryVector) {
        try {
            return client.queryAsync(
                QueryPoints.newBuilder()
                    .setCollectionName(COLLECTION_NAME)
                    .setLimit(5)
                    .setQuery(nearest(queryVector))
                    .setWithPayload(enable(true))
                    .build()
            ).get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Qdrant search failed", e);
        }
    }
    
    private float[] generateDummyVector() {
        // In a real app, you'd use an embedding model here.
        float[] vector = new float[VECTOR_SIZE];
        for (int i = 0; i < VECTOR_SIZE; i++) {
            vector[i] = (float) Math.random();
        }
        return vector;
    }
}
```

### e. `SearchController.java`
```java
package com.example.qdrantdemo.controller;

import com.example.qdrantdemo.service.QdrantSearchService;
import dev.langchain4j.embedding.Embedding;
import dev.langchain4j.embedding.EmbeddingModel;
import dev.langchain4j.embedding.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import io.qdrant.client.grpc.Points.ScoredPoint;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/search")
public class SearchController {

    private final QdrantSearchService searchService;
    private final EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

    public SearchController(QdrantSearchService searchService) {
        this.searchService = searchService;
    }

    @GetMapping
    public List<ScoredPoint> search(@RequestParam String query) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        return searchService.search(queryEmbedding.vectorAsList());
    }
}
```

## 2. Langchain4j RAG Example

This example shows a complete setup for a Retrieval-Augmented Generation (RAG) service using Langchain4j and Qdrant.

### a. `pom.xml` Dependencies
```xml
<dependencies>
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Langchain4j -->
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

### b. `Langchain4jConfig.java`
(As defined in `SKILL.md`)

### c. `RagController.java`
```java
package com.example.qdrantdemo.controller;

import com.example.qdrantdemo.service.RagService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/rag")
public class RagController {

    private final RagService ragService;

    public RagController(RagService ragService) {
        this.ragService = ragService;
    }

    @PostMapping("/ingest")
    public String ingestDocument(@RequestBody String document) {
        ragService.addDocument(document);
        return "Document ingested successfully.";
    }

    @GetMapping("/query")
    public String query(@RequestParam String query) {
        return ragService.query(query);
    }
}
```

### d. `RagService.java` (with LLM interaction)
```java
package com.example.qdrantdemo.service;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import org.springframework.stereotype.Service;

@Service
public class RagService {

    interface Assistant {
        String chat(String userMessage);
    }

    private final EmbeddingStoreIngestor ingestor;
    private final Assistant assistant;

    public RagService(EmbeddingStore<TextSegment> embeddingStore, EmbeddingStoreIngestor ingestor) {
        this.ingestor = ingestor;

        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .maxResults(3)
                .minScore(0.7)
                .build();

        ChatLanguageModel chatModel = OpenAiChatModel.builder()
                .apiKey("YOUR_OPENAI_API_KEY") // Replace with your key
                .modelName("gpt-3.5-turbo")
                .build();

        this.assistant = AiServices.builder(Assistant.class)
                .chatLanguageModel(chatModel)
                .contentRetriever(contentRetriever)
                .build();
    }

    public void addDocument(String text) {
        TextSegment segment = TextSegment.from(text);
        ingestor.ingest(segment);
    }

    public String query(String userQuery) {
        return assistant.chat(userQuery);
    }
}
```
