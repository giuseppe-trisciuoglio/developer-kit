---
name: qdrant-java-development
description: A comprehensive guide for Java developers on using Qdrant with Spring Boot and Langchain4j. It covers setup, core operations, and best practices for building modern AI applications.
category: backend
tags: [qdrant, java, spring-boot, langchain4j, vector-search, ai, machine-learning]
version: 1.1.0
---

# Qdrant for Java and Spring Boot Developers

This skill provides a comprehensive guide for Java developers on integrating Qdrant, the vector search engine, into Spring Boot applications, with a special focus on the Langchain4j framework.

## When to Use This Skill

This skill is essential for Java developers who are:
- Building semantic search or recommendation systems in a Spring Boot environment.
- Implementing Retrieval-Augmented Generation (RAG) pipelines with Java.
- Integrating a powerful vector database into their Java-based AI and machine learning applications.
- Looking for best practices on using Qdrant with Langchain4j and Spring Boot.

## 1. Getting Started: Qdrant Setup

Before integrating with a Java application, you need a running Qdrant instance.

### Run Qdrant with Docker
Ensure Docker is installed, then run the following commands:

```bash
# Pull the latest Qdrant image
docker pull qdrant/qdrant

# Run the Qdrant container
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```
Qdrant will be accessible via:
- **REST API**: `http://localhost:6333`
- **gRPC API**: `http://localhost:6334` (used by the Java client)

## 2. Using the Qdrant Java Client

Qdrant provides an official Java client for interacting with the database via gRPC.

### Dependency Setup

Add the Qdrant Java client to your `pom.xml` or `build.gradle`:

**Maven:**
```xml
<dependency>
    <groupId>io.qdrant</groupId>
    <artifactId>client</artifactId>
    <version>1.15.0</version>
</dependency>
```

**Gradle:**
```gradle
implementation 'io.qdrant:client:1.15.0'
```

### Initializing the Client

Create an instance of `QdrantClient`. It's `AutoCloseable`, but you'll typically manage it as a singleton bean in a Spring application.

```java
import io.qdrant.client.QdrantClient;
import io.qdrant.client.QdrantGrpcClient;

// Connect to a local, unsecured Qdrant instance
QdrantClient client = new QdrantClient(
    QdrantGrpcClient.newBuilder("localhost", 6334, false).build());

// To connect to a secured instance with an API key:
// ManagedChannel channel = Grpc.newChannelBuilder(...)
// QdrantClient secureClient = new QdrantClient(
//     QdrantGrpcClient.newBuilder(channel)
//         .withApiKey("YOUR_API_KEY")
//         .build());
```

## 3. Core Operations with the Java Client

Here’s how to perform basic operations. All client methods return a `ListenableFuture`.

### Create a Collection

```java
import io.qdrant.client.grpc.Collections.Distance;
import io.qdrant.client.grpc.Collections.VectorParams;
import java.util.concurrent.ExecutionException;

try {
    client.createCollectionAsync("my-java-collection",
        VectorParams.newBuilder().setDistance(Distance.Cosine).setSize(384).build()
    ).get();
} catch (InterruptedException | ExecutionException e) {
    // Handle exception
}
```

### Upsert Points (Vectors)

Use the provided factory classes to easily construct points.

```java
import io.qdrant.client.grpc.Points.PointStruct;
import java.util.List;
import java.util.Map;
import static io.qdrant.client.PointIdFactory.id;
import static io.qdrant.client.ValueFactory.value;
import static io.qdrant.client.VectorsFactory.vectors;

List<PointStruct> points = List.of(
    PointStruct.newBuilder()
        .setId(id(1))
        .setVectors(vectors(0.05f, 0.61f, 0.76f, 0.74f))
        .putAllPayload(Map.of("city", value("Berlin")))
        .build(),
    PointStruct.newBuilder()
        .setId(id(2))
        .setVectors(vectors(0.19f, 0.81f, 0.75f, 0.11f))
        .putAllPayload(Map.of("city", value("London")))
        .build()
);

client.upsertAsync("my-java-collection", points).get();
```

### Search for Similar Points

```java
import io.qdrant.client.grpc.Points.QueryPoints;
import io.qdrant.client.grpc.Points.ScoredPoint;
import static io.qdrant.client.QueryFactory.nearest;
import java.util.List;

List<ScoredPoint> searchResult = client.queryAsync(
    QueryPoints.newBuilder()
        .setCollectionName("my-java-collection")
        .setLimit(3)
        .setQuery(nearest(0.2f, 0.1f, 0.9f, 0.7f))
        .build()
).get();

System.out.println(searchResult);
```

## 4. Spring Boot Integration

Properly integrate the `QdrantClient` into your Spring Boot application by defining it as a bean.

### Configuration Bean

Create a configuration class to manage the `QdrantClient` lifecycle.

```java
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
        // In a real application, you would handle TLS and API keys here
        return new QdrantClient(
            QdrantGrpcClient.newBuilder(host, port, false).build());
    }
}
```

### Service Layer

Inject the `QdrantClient` bean into your services to abstract away the data access logic.

```java
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.concurrent.ExecutionException;

@Service
public class SearchService {

    private final QdrantClient qdrantClient;

    public SearchService(QdrantClient qdrantClient) {
        this.qdrantClient = qdrantClient;
    }

    public List<ScoredPoint> search(String collectionName, List<Float> queryVector) {
        try {
            return qdrantClient.queryAsync(
                QueryPoints.newBuilder()
                    .setCollectionName(collectionName)
                    .setLimit(5)
                    .setQuery(nearest(queryVector))
                    .build()
            ).get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Qdrant search failed", e);
        }
    }
}
```

## 5. Langchain4j Integration

Langchain4j provides a high-level abstraction over Qdrant with its `QdrantEmbeddingStore`.

### Dependency Setup

Add the `langchain4j-qdrant` dependency to your project.

**Maven:**
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-qdrant</artifactId>
    <version>0.34.0</version> <!-- Check for the latest version -->
</dependency>
```

### `QdrantEmbeddingStore` Bean

Configure `QdrantEmbeddingStore` as a Spring bean. It simplifies embedding management by handling both the embedding model and the vector store.

```java
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.embedding.EmbeddingModel;
import dev.langchain4j.embedding.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.qdrant.QdrantEmbeddingStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class Langchain4jConfig {

    @Bean
    public EmbeddingStore<TextSegment> embeddingStore() {
        return QdrantEmbeddingStore.builder()
            .collectionName("langchain4j-collection")
            .host("localhost")
            .port(6334)
            // .apiKey("YOUR_API_KEY") // Uncomment if auth is enabled
            .build();
    }

    @Bean
    public EmbeddingModel embeddingModel() {
        return new AllMiniLmL6V2EmbeddingModel();
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

### Usage in a Service

Inject the `EmbeddingStore` and `EmbeddingModel` to build a simple RAG-style search.

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.RelevanceScore;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class RagService {

    private final EmbeddingStore<TextSegment> embeddingStore;
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStoreIngestor ingestor;

    public RagService(EmbeddingStore<TextSegment> embeddingStore,
                      EmbeddingModel embeddingModel,
                      EmbeddingStoreIngestor ingestor) {
        this.embeddingStore = embeddingStore;
        this.embeddingModel = embeddingModel;
        this.ingestor = ingestor;
    }

    public void addDocument(String text) {
        TextSegment segment = TextSegment.from(text);
        ingestor.ingest(segment);
    }

    public List<TextSegment> findMostRelevant(String query) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        List<EmbeddingMatch<TextSegment>> relevant = embeddingStore.findRelevant(queryEmbedding, 5, 0.7);
        
        return relevant.stream()
            .map(EmbeddingMatch::embedded)
            .toList();
    }
}
```

## Examples and References

- For detailed, runnable code snippets, see the **[Code Examples](examples.md)** file.
- For a curated list of official documentation and other useful resources, see the **[References](references.md)** file.