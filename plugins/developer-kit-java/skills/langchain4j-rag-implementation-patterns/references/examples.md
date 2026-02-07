# LangChain4j RAG Implementation - Practical Examples

Production-ready examples for implementing Retrieval-Augmented Generation (RAG) systems with LangChain4j.

## 1. Simple In-Memory RAG

**Scenario**: Quick RAG setup with documents in memory for development/testing.

```java
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;

interface DocumentAssistant {
    String answer(String question);
}

public class SimpleRagExample {
    public static void main(String[] args) {
        // Setup
        var embeddingStore = new InMemoryEmbeddingStore<TextSegment>();
        
        var embeddingModel = OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .build();

        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        // Ingest documents
        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();

        ingestor.ingest(Document.from("Spring Boot is a framework for building Java applications with minimal configuration."));
        ingestor.ingest(Document.from("Spring Data JPA provides data access abstraction using repositories."));
        ingestor.ingest(Document.from("Spring Cloud enables building distributed systems and microservices."));

        // Create retriever and AI service
        var contentRetriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(3)
            .minScore(0.7)
            .build();

        var assistant = AiServices.builder(DocumentAssistant.class)
            .chatModel(chatModel)
            .contentRetriever(contentRetriever)
            .build();

        // Query with RAG
        System.out.println(assistant.answer("What is Spring Boot?"));
        System.out.println(assistant.answer("What does Spring Data JPA do?"));
    }
}
```

## 2. Vector Database RAG (Pinecone)

**Scenario**: Production RAG with persistent vector database.

```java
import dev.langchain4j.store.embedding.pinecone.PineconeEmbeddingStore;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.Metadata;

public class PineconeRagExample {
    public static void main(String[] args) {
        // Production vector store
        var embeddingStore = PineconeEmbeddingStore.builder()
            .apiKey(System.getenv("PINECONE_API_KEY"))
            .index("docs-index")
            .namespace("production")
            .build();

        var embeddingModel = OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .build();

        // Ingest with metadata
        var ingestor = EmbeddingStoreIngestor.builder()
            .documentTransformer(doc -> {
                doc.metadata().put("source", "documentation");
                doc.metadata().put("date", LocalDate.now().toString());
                return doc;
            })
            .documentSplitter(DocumentSplitters.recursive(1000, 200))
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();

        ingestor.ingest(Document.from("Your large document..."));

        // Retrieve with filters
        var retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .dynamicFilter(query -> 
                new IsEqualTo("source", "documentation")
            )
            .build();
    }
}
```

## 3. Document Loading and Splitting

**Scenario**: Load documents from various sources and split intelligently.

```java
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.loader.FileSystemDocumentLoader;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.openai.OpenAiTokenCountEstimator;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class DocumentProcessingExample {
    public static void main(String[] args) {
        // Load from filesystem
        Path docPath = Paths.get("documents");
        List<Document> documents = FileSystemDocumentLoader.load(docPath);

        // Smart recursive splitting with token counting
        DocumentSplitter splitter = DocumentSplitters.recursive(
            500,  // Max tokens per segment
            50,   // Overlap tokens
            new OpenAiTokenCountEstimator("gpt-4o-mini")
        );

        // Process documents
        for (Document doc : documents) {
            List<TextSegment> segments = splitter.split(doc);
            System.out.println("Document split into " + segments.size() + " segments");
            
            segments.forEach(segment -> {
                System.out.println("Text: " + segment.text());
                System.out.println("Metadata: " + segment.metadata());
            });
        }

        // Alternative: Character-based splitting
        DocumentSplitter charSplitter = DocumentSplitters.recursive(
            1000,  // Max characters
            100    // Overlap characters
        );

        // Alternative: Paragraph-based splitting
        DocumentSplitter paraSplitter = DocumentSplitters.byParagraph(500, 50);
    }
}
```

## 4. Metadata Filtering in RAG

**Scenario**: Search with complex metadata filters for multi-tenant RAG.

```java
import dev.langchain4j.store.embedding.filter.comparison.*;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;

public class MetadataFilteringExample {
    public static void main(String[] args) {
        var retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            
            // Single filter: user isolation
            .filter(new IsEqualTo("userId", "user123"))
            
            // Complex AND filter
            .filter(new And(
                new IsEqualTo("department", "engineering"),
                new IsEqualTo("status", "active")
            ))
            
            // OR filter: multiple categories
            .filter(new Or(
                new IsEqualTo("category", "tutorial"),
                new IsEqualTo("category", "guide")
            ))
            
            // NOT filter: exclude deprecated
            .filter(new Not(
                new IsEqualTo("deprecated", "true")
            ))
            
            // Numeric filters
            .filter(new IsGreaterThan("relevance", 0.8))
            .filter(new IsLessThanOrEqualTo("createdDaysAgo", 30))
            
            // Multiple conditions
            .dynamicFilter(query -> {
                String userId = extractUserFromQuery(query);
                return new And(
                    new IsEqualTo("userId", userId),
                    new IsGreaterThan("score", 0.7)
                );
            })
            
            .build();
    }

    private static String extractUserFromQuery(Object query) {
        // Extract user context
        return "user123";
    }
}
```

## 5. Document Transformation Pipeline

**Scenario**: Transform documents with custom metadata before ingestion.

```java
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.segment.TextSegment;
import java.time.LocalDate;

public class DocumentTransformationExample {
    public static void main(String[] args) {
        var ingestor = EmbeddingStoreIngestor.builder()
            
            // Add metadata to each document
            .documentTransformer(doc -> {
                doc.metadata().put("ingested_date", LocalDate.now().toString());
                doc.metadata().put("source_system", "internal");
                doc.metadata().put("version", "1.0");
                return doc;
            })
            
            // Split documents intelligently
            .documentSplitter(DocumentSplitters.recursive(500, 50))
            
            // Transform each segment (e.g., add filename)
            .textSegmentTransformer(segment -> {
                String fileName = segment.metadata().getString("file_name", "unknown");
                String enrichedText = "File: " + fileName + "\n" + segment.text();
                return TextSegment.from(enrichedText, segment.metadata());
            })
            
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();

        // Ingest with tracking
        IngestionResult result = ingestor.ingest(document);
        System.out.println("Tokens ingested: " + result.tokenUsage().totalTokenCount());
    }
}
```

## 6. Hybrid Search (Vector + Full-Text)

**Scenario**: Combine semantic search with keyword search for better recall.

```java
import dev.langchain4j.store.embedding.neo4j.Neo4jEmbeddingStore;

public class HybridSearchExample {
    public static void main(String[] args) {
        // Configure Neo4j for hybrid search
        var embeddingStore = Neo4jEmbeddingStore.builder()
            .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
            .dimension(1536)
            
            // Enable full-text search
            .fullTextIndexName("documents_fulltext")
            .autoCreateFullText(true)
            
            // Query for full-text context
            .fullTextQuery("Spring OR Boot")
            
            .build();

        var retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .build();

        // Search combines both vector similarity and full-text keywords
    }
}
```

## 7. Advanced RAG with Query Transformation

**Scenario**: Transform user queries before retrieval for better results.

```java
import dev.langchain4j.rag.DefaultRetrievalAugmentor;
import dev.langchain4j.rag.query.transformer.CompressingQueryTransformer;
import dev.langchain4j.rag.content.aggregator.ReRankingContentAggregator;
import dev.langchain4j.model.cohere.CohereScoringModel;

public class AdvancedRagExample {
    public static void main(String[] args) {
        // Scoring model for re-ranking
        var scoringModel = CohereScoringModel.builder()
            .apiKey(System.getenv("COHERE_API_KEY"))
            .build();

        // Advanced retrieval augmentor
        var augmentor = DefaultRetrievalAugmentor.builder()
            
            // Transform query for better context
            .queryTransformer(new CompressingQueryTransformer(chatModel))
            
            // Retrieve relevant content
            .contentRetriever(EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(10)
                .minScore(0.6)
                .build())
            
            // Re-rank results by relevance
            .contentAggregator(ReRankingContentAggregator.builder()
                .scoringModel(scoringModel)
                .minScore(0.8)
                .build())
            
            .build();

        // Use with AI Service
        var assistant = AiServices.builder(QuestionAnswering.class)
            .chatModel(chatModel)
            .retrievalAugmentor(augmentor)
            .build();
    }
}
```

## 8. Multi-User RAG with Isolation

**Scenario**: Per-user vector stores for data isolation.

```java
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import java.util.HashMap;
import java.util.Map;

public class MultiUserRagExample {
    private final Map<String, EmbeddingStore<TextSegment>> userStores = new HashMap<>();
    
    public void ingestForUser(String userId, Document document) {
        var store = userStores.computeIfAbsent(userId, 
            k -> new InMemoryEmbeddingStore<>());

        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(store)
            .build();

        ingestor.ingest(document);
    }

    public String askQuestion(String userId, String question) {
        var store = userStores.get(userId);
        
        var retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(store)
            .embeddingModel(embeddingModel)
            .maxResults(3)
            .build();

        var assistant = AiServices.builder(QuestionAnswering.class)
            .chatModel(chatModel)
            .contentRetriever(retriever)
            .build();

        return assistant.answer(question);
    }
}
```

## 9. Streaming RAG with Content Access

**Scenario**: Stream RAG responses while accessing retrieved content.

```java
import dev.langchain4j.service.TokenStream;

interface StreamingRagAssistant {
    TokenStream streamAnswer(String question);
}

public class StreamingRagExample {
    public static void main(String[] args) {
        var assistant = AiServices.builder(StreamingRagAssistant.class)
            .streamingChatModel(streamingModel)
            .contentRetriever(contentRetriever)
            .build();

        assistant.streamAnswer("What is Spring Boot?")
            .onRetrieved(contents -> {
                System.out.println("=== Retrieved Content ===");
                contents.forEach(content -> 
                    System.out.println("Score: " + content.score() + 
                                     ", Text: " + content.textSegment().text()));
            })
            .onNext(token -> System.out.print(token))
            .onCompleteResponse(response -> 
                System.out.println("\n=== Complete ==="))
            .onError(error -> System.err.println("Error: " + error))
            .start();

        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

## 10. Batch Document Ingestion

**Scenario**: Efficiently ingest large document collections.

```java
import dev.langchain4j.data.document.Document;
import java.util.List;
import java.util.ArrayList;

public class BatchIngestionExample {
    public static void main(String[] args) {
        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .documentSplitter(DocumentSplitters.recursive(500, 50))
            .build();

        // Load batch of documents
        List<Document> documents = new ArrayList<>();
        for (int i = 1; i <= 100; i++) {
            documents.add(Document.from("Content " + i));
        }

        // Ingest all at once
        IngestionResult result = ingestor.ingest(documents);
        
        System.out.println("Documents ingested: " + documents.size());
        System.out.println("Total tokens: " + result.tokenUsage().totalTokenCount());

        // Track progress
        long tokensPerDoc = result.tokenUsage().totalTokenCount() / documents.size();
        System.out.println("Average tokens per document: " + tokensPerDoc);
    }
}
```

## Performance Considerations

1. **Batch Processing**: Ingest documents in batches to optimize embedding API calls
2. **Document Splitting**: Use recursive splitting for better semantic chunks
3. **Metadata**: Add minimal metadata to reduce embedding overhead
4. **Vector DB**: Choose appropriate vector DB based on scale (in-memory for dev, Pinecone/Weaviate for prod)
5. **Similarity Threshold**: Adjust minScore based on use case (0.7-0.85 typical)
6. **Max Results**: Return top 3-5 results unless specific needs require more
7. **Caching**: Cache frequently retrieved content to reduce API calls
8. **Async Ingestion**: Use async ingestion for large datasets
9. **Monitoring**: Track token usage and retrieval quality metrics
10. **Testing**: Use in-memory store for unit tests, external DB for integration tests
