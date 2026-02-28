# Integration Testing with Testcontainers

## Ollama Integration Test Setup

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.ollama.OllamaChatModel;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.AfterAll;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

@Testcontainers
class OllamaIntegrationTest {

    @Container
    static GenericContainer<?> ollama = new GenericContainer<>(
        DockerImageName.parse("ollama/ollama:0.5.4")
    ).withExposedPorts(11434);

    private static ChatModel chatModel;

    @BeforeAll
    static void setup() {
        chatModel = OllamaChatModel.builder()
                .baseUrl(ollama.getEndpoint())
                .modelName("llama2") // Use a lightweight model for testing
                .temperature(0.0)
                .timeout(java.time.Duration.ofSeconds(30))
                .build();
    }

    @Test
    void shouldGenerateResponseWithOllama() {
        // Act
        String response = chatModel.generate("What is 2 + 2?");

        // Assert
        assertNotNull(response);
        assertFalse(response.trim().isEmpty());
        assertTrue(response.contains("4") || response.toLowerCase().contains("four"));
    }

    @Test
    void shouldHandleComplexQuery() {
        // Act
        String response = chatModel.generate(
            "Explain the difference between ArrayList and LinkedList in Java"
        );

        // Assert
        assertNotNull(response);
        assertTrue(response.length() > 50);
        assertTrue(response.toLowerCase().contains("arraylist"));
        assertTrue(response.toLowerCase().contains("linkedlist"));
    }
}
```

## Embedding Store Integration Test

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.ollama.OllamaEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class EmbeddingStoreIntegrationTest {

    private EmbeddingModel embeddingModel;
    private EmbeddingStore<TextSegment> embeddingStore;

    @BeforeEach
    void setup() {
        // Use in-memory store for faster tests
        embeddingStore = new InMemoryEmbeddingStore();

        // For production tests, you could use Testcontainers with Chroma/Weaviate
        embeddingModel = OllamaEmbeddingModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("nomic-embed-text")
                .build();
    }

    @Test
    void shouldStoreAndRetrieveEmbeddings() {
        // Arrange
        TextSegment segment = TextSegment.from("Java is a programming language");
        Embedding embedding = embeddingModel.embed(segment.text()).content();

        // Act
        String id = embeddingStore.add(embedding, segment);

        // Assert
        assertNotNull(id);

        // Verify retrieval
        var searchRequest = EmbeddingSearchRequest.builder()
                .queryEmbedding(embedding)
                .maxResults(1)
                .build();

        List<EmbeddingMatch<TextSegment>> matches = embeddingStore.search(searchRequest);
        assertEquals(1, matches.size());
        assertEquals(segment.text(), matches.get(0).embedded().text());
    }
}
```

## RAG Integration Test

```java
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.splitter.ParagraphSplitter;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RagSystemTest {

    private ContentRetriever contentRetriever;
    private ChatModel chatModel;

    @BeforeEach
    void setup() {
        // Setup embedding store
        EmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore();

        // Setup embedding model
        EmbeddingModel embeddingModel = OllamaEmbeddingModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("nomic-embed-text")
                .build();

        // Setup content retriever
        contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingModel(embeddingModel)
                .embeddingStore(embeddingStore)
                .maxResults(3)
                .build();

        // Setup chat model
        chatModel = OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("llama2")
                .build();

        // Ingest test documents
        ingestTestDocuments(embeddingStore, embeddingModel);
    }

    private void ingestTestDocuments(EmbeddingStore<TextSegment> store, EmbeddingModel model) {
        DocumentSplitter splitter = new ParagraphSplitter();

        Document doc1 = Document.from("Spring Boot is a Java framework for building microservices");
        Document doc2 = Document.from("Maven is a build automation tool for Java projects");
        Document doc3 = Document.from("JUnit is a testing framework for Java applications");

        List<Document> documents = List.of(doc1, doc2, doc3);
        EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
                .embeddingModel(model)
                .embeddingStore(store)
                .documentSplitter(splitter)
                .build();

        ingestor.ingest(documents);
    }

    @Test
    void shouldRetrieveRelevantContent() {
        // Arrange
        RagAssistant assistant = AiServices.builder(RagAssistant.class)
                .chatLanguageModel(chatModel)
                .contentRetriever(contentRetriever)
                .build();

        // Act
        String response = assistant.chat("What is Spring Boot?");

        // Assert
        assertNotNull(response);
        assertTrue(response.toLowerCase().contains("spring boot"));
        assertTrue(response.toLowerCase().contains("framework"));
    }

    interface RagAssistant {
        String chat(String message);
    }
}
```

## Performance Testing

### Response Time Test

```java
import dev.langchain4j.model.chat.ChatModel;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.time.Duration;
import java.time.Instant;

import static org.junit.jupiter.api.Assertions.*;

class PerformanceTest {

    @Test
    @Timeout(30)
    void shouldRespondWithinTimeLimit() {
        // Arrange
        ChatModel model = OllamaChatModel.builder()
                .baseUrl("http://localhost:11434")
                .modelName("llama2")
                .timeout(Duration.ofSeconds(20))
                .build();

        // Act
        Instant start = Instant.now();
        String response = model.generate("What is 2 + 2?");
        Instant end = Instant.now();

        // Assert
        Duration duration = Duration.between(start, end);
        assertTrue(duration.toSeconds() < 15, "Response took too long: " + duration);
        assertNotNull(response);
    }
}
```

### Token Usage Tracking Test

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.output.TokenUsage;

@Test
void shouldTrackTokenUsage() {
    // Arrange
    ChatModel mockModel = mock(ChatModel.class);
    var mockResponse = Response.from(
        AiMessage.from("Response"),
        new TokenUsage(10, 20, 30)
    );

    when(mockModel.generate(any(String.class)))
        .thenReturn(mockResponse);

    // Act
    var response = mockModel.generate("Test query");

    // Assert
    assertEquals(10, response.tokenUsage().inputTokenCount());
    assertEquals(20, response.tokenUsage().outputTokenCount());
    assertEquals(30, response.tokenUsage().totalTokenCount());
}
```

## Vector Store Integration Tests

### Qdrant Integration Test

```java
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.qdrant.QdrantEmbeddingStore;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

@Testcontainers
class QdrantIntegrationTest {

    @Container
    static GenericContainer<?> qdrant = new GenericContainer<>(
        DockerImageName.parse("qdrant/qdrant:v1.13.2")
    ).withExposedPorts(6333);

    private EmbeddingStore<TextSegment> embeddingStore;

    @BeforeEach
    void setup() {
        var host = qdrant.getHost();
        var port = qdrant.getFirstMappedPort();

        embeddingStore = QdrantEmbeddingStore.builder()
            .host(host)
            .port(port)
            .collectionName("test-collection")
            .build();
    }

    @Test
    void shouldStoreAndRetrieveVectors() {
        // Arrange
        var text = "Spring Boot is a Java framework";
        var embeddingModel = createMockEmbeddingModel(text);
        var segment = TextSegment.from(text);

        // Act
        String id = embeddingStore.add(embeddingModel.embed(text).content(), segment);

        // Assert
        assertNotNull(id);

        var searchRequest = EmbeddingSearchRequest.builder()
            .queryEmbedding(embeddingModel.embed(text).content())
            .maxResults(1)
            .build();

        var result = embeddingStore.search(searchRequest);
        assertEquals(1, result.matches().size());
    }
}
```