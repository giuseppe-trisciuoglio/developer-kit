---
name: qdrant
description: Provides Qdrant vector database integration patterns with LangChain4j. Handles embedding storage, similarity search, and vector management for Java applications. Use when implementing vector-based retrieval for RAG systems, semantic search, or recommendation engines.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Qdrant Vector Database Integration

## Overview

Qdrant is an AI-native vector database for semantic search and similarity retrieval. This skill provides patterns for integrating Qdrant with Java applications, focusing on Spring Boot and LangChain4j framework support for RAG systems, recommendation engines, and semantic search.

## When to Use

- Semantic search or recommendation systems in Spring Boot
- Retrieval-Augmented Generation (RAG) pipelines with LangChain4j
- High-performance similarity search with filtered queries
- Embedding storage and retrieval for context-aware applications

## Instructions

### 1. Deploy Qdrant Instance

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
```

### 2. Add Dependencies

```xml
<dependency>
    <groupId>io.qdrant</groupId>
    <artifactId>client</artifactId>
    <version>1.15.0</version>
</dependency>
```

### 3. Initialize Client and Create Collection

```java
QdrantClient client = new QdrantClient(
    QdrantGrpcClient.newBuilder("localhost").build());

client.createCollectionAsync("search-collection",
    VectorParams.newBuilder().setDistance(Distance.Cosine).setSize(384).build()).get();
```

### 4. Vector Operations

```java
// Upsert
List<PointStruct> points = List.of(
    PointStruct.newBuilder()
        .setId(id(1))
        .setVectors(vectors(0.05f, 0.61f, 0.76f, 0.74f))
        .putAllPayload(Map.of("title", value("Spring Boot Documentation")))
        .build());
client.upsertAsync("search-collection", points).get();

// Search
List<ScoredPoint> results = client.queryAsync(
    QueryPoints.newBuilder()
        .setCollectionName("search-collection")
        .setLimit(5)
        .setQuery(nearest(0.2f, 0.1f, 0.9f, 0.7f))
        .build()).get();
```

### 5. LangChain4j Integration

```java
EmbeddingStore<TextSegment> embeddingStore = QdrantEmbeddingStore.builder()
    .collectionName("rag-collection")
    .host("localhost")
    .port(6334)
    .build();
```

## Examples

### Spring Boot Configuration

```java
@Configuration
public class QdrantConfig {
    @Value("${qdrant.host:localhost}") private String host;
    @Value("${qdrant.port:6334}") private int port;

    @Bean
    public QdrantClient qdrantClient() {
        return new QdrantClient(
            QdrantGrpcClient.newBuilder(host, port, false).build());
    }
}
```

### Hybrid Search with Filters

```java
Filter filter = Filter.newBuilder()
    .addMust(range("created_at", Range.newBuilder().setGte(dateRange.getTime()).build()))
    .addMust(exactMatch("category", category))
    .build();

List<ScoredPoint> results = client.searchAsync(
    SearchPoints.newBuilder()
        .setCollectionName(collectionName)
        .addAllVector(queryVector)
        .setFilter(filter)
        .build()).get();
```

## Best Practices

- Use Cosine distance for text embeddings, Euclidean for numerical data
- Optimize vector dimensions based on embedding model specs
- Use constructor injection for Spring Boot integration
- Handle async operations with proper exception handling
- Never hardcode API keys; use environment variables
- Batch operations for bulk upserts
- Use gRPC API (port 6334) for production; REST (port 6333) for debugging

## Constraints and Warnings

- Vector dimensions must match the embedding model; mismatched dimensions cause errors
- Large collections require proper indexing for acceptable search performance
- Collection recreation deletes all data; implement backup strategies
- Implement proper connection pooling to avoid exhaustion under load
- Filtering without indexing on large datasets degrades performance

## References

- [Qdrant API Reference](references/references.md)
- [Complete Spring Boot Examples](references/examples.md)
- [Official Qdrant Documentation](https://qdrant.tech/documentation/)
