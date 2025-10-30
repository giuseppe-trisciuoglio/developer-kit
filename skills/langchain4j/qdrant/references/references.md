# Qdrant for Java: References

This file contains key technical details and code patterns for integrating Qdrant with Java applications.

## Qdrant Java Client API Reference

### Core Setup

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

### Client Initialization

```java
// Basic client
QdrantClient client = new QdrantClient(
    QdrantGrpcClient.newBuilder("localhost").build());

// Advanced client with TLS and API key
ManagedChannel channel = Grpc.newChannelBuilder(
    "localhost:6334",
    TlsChannelCredentials.newBuilder()
        .trustManager(new File("ssl/ca.crt"))
        .build()).build();

QdrantClient client = new QdrantClient(
    QdrantGrpcClient.newBuilder(channel)
        .withApiKey("<apikey>")
        .build());
```

### Collection Management

```java
// Create collection
client.createCollectionAsync("my_collection",
    VectorParams.newBuilder()
        .setDistance(Distance.Cosine)
        .setSize(4)
        .build()).get();

// Create collection with configuration
client.createCollectionAsync("my_collection",
    VectorParams.newBuilder()
        .setDistance(Distance.Cosine)
        .setSize(384)
        .build())
    .get();
```

### Point Operations

```java
// Insert points
List<PointStruct> points = List.of(
    PointStruct.newBuilder()
        .setId(id(1))
        .setVectors(vectors(0.32f, 0.52f, 0.21f, 0.52f))
        .putAllPayload(Map.of("color", value("red")))
        .build()
);

UpdateResult result = client.upsertAsync("my_collection", points).get();
```

### Search Operations

```java
// Simple search
List<ScoredPoint> results = client.searchAsync(
    SearchPoints.newBuilder()
        .setCollectionName("my_collection")
        .addAllVector(List.of(0.6235f, 0.123f, 0.532f, 0.123f))
        .setLimit(5)
        .build()).get();

// Filtered search
List<ScoredPoint> filteredResults = client.searchAsync(
    SearchPoints.newBuilder()
        .setCollectionName("my_collection")
        .addAllVector(List.of(0.6235f, 0.123f, 0.532f, 0.123f))
        .setFilter(Filter.newBuilder()
            .addMust(range("rand_number",
                Range.newBuilder().setGte(3).build()))
            .build())
        .setLimit(5)
        .build()).get();
```

## LangChain4j Integration Patterns

### QdrantEmbeddingStore Setup

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-qdrant</artifactId>
    <version>1.7.0</version>
</dependency>
```

### Configuration

```java
EmbeddingStore<TextSegment> embeddingStore = QdrantEmbeddingStore.builder()
    .collectionName("YOUR_COLLECTION_NAME")
    .host("YOUR_HOST_URL")
    .port(6334)
    .apiKey("YOUR_API_KEY")
    .build();

// Or with HTTPS
EmbeddingStore<TextSegment> embeddingStore = QdrantEmbeddingStore.builder()
    .collectionName("YOUR_COLLECTION_NAME")
    .host("YOUR_HOST_URL")
    .port(443)
    .useHttps(true)
    .apiKey("YOUR_API_KEY")
    .build();
```

## Official Documentation Resources

- **[Qdrant Documentation](https://qdrant.tech/documentation/)**: Main documentation portal
- **[Qdrant Java Client GitHub](https://github.com/qdrant/java-client)**: Source code and issues
- **[Java Client Javadoc](https://qdrant.github.io/java-client/)**: Complete API documentation
- **[API & SDKs](https://qdrant.tech/documentation/interfaces/)**: All supported clients
- **[Quickstart Guide](https://qdrant.tech/documentation/quickstart/)**: Local setup guide
- **[LangChain4j Official Site](https://langchain4j.dev/)**: Framework documentation
- **[LangChain4j Examples](https://github.com/langchain4j/langchain4j-examples)**: Comprehensive examples
