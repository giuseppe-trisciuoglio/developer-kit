---
name: langchain4j-rag-implementation-patterns
description: Retrieval-Augmented Generation (RAG) implementation patterns with LangChain4j. Retrieve documents, embed them, and augment LLM prompts with context. Use when building knowledge-powered AI applications.
category: ai-development
tags: [langchain4j, rag, retrieval-augmented-generation, embedding, vector-search, document-ingestion, content-retrieval, java]
version: 1.0.0
context7_library: /langchain4j/langchain4j
context7_trust_score: 7.8
allowed-tools: Read, Write, Bash
---

# LangChain4j RAG Implementation Patterns

This skill provides comprehensive guidance for implementing Retrieval-Augmented Generation (RAG) systems with LangChain4j, covering document ingestion pipelines, embedding stores, vector search strategies, content retrieval patterns, and advanced RAG architectures for building knowledge-enhanced AI applications.

## When to Use This Skill

Use this skill when:
- Building knowledge-based AI applications that require access to external documents
- Implementing question-answering systems over large document collections
- Creating AI assistants with access to company knowledge bases
- Building semantic search capabilities for document repositories
- Implementing chat systems that can reference specific information sources
- Creating AI applications that need to provide source attribution
- Building domain-specific AI systems with curated knowledge
- Implementing hybrid search combining vector similarity with traditional search
- Creating AI applications that require real-time document updates
- Building multi-modal RAG systems with text, images, and other content types

## Core Concepts

### RAG Architecture Overview

RAG (Retrieval-Augmented Generation) enhances language models by providing them with relevant context retrieved from external knowledge sources, improving accuracy and reducing hallucinations.

**Basic RAG Flow:**
1. **Document Ingestion**: Load and preprocess documents
2. **Text Segmentation**: Split documents into manageable chunks
3. **Embedding Generation**: Convert text segments to vector embeddings
4. **Vector Storage**: Store embeddings in a vector database
5. **Query Processing**: Convert user queries to embeddings
6. **Similarity Search**: Find relevant document segments
7. **Context Injection**: Provide retrieved content to the language model
8. **Response Generation**: Generate answers using retrieved context

### Document Ingestion Pipeline

**Document Loading and Processing:**
```java
@Service
public class DocumentIngestionService {

    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;
    private final DocumentSplitter documentSplitter;

    public DocumentIngestionService(EmbeddingModel embeddingModel,
                                  EmbeddingStore<TextSegment> embeddingStore) {
        this.embeddingModel = embeddingModel;
        this.embeddingStore = embeddingStore;
        this.documentSplitter = DocumentSplitters.recursive(
            500,    // maxSegmentSizeInTokens
            50,     // maxOverlapSizeInTokens
            new OpenAiTokenCountEstimator("gpt-4o-mini")
        );
    }

    public void ingestDocument(String filePath, Map<String, Object> metadata) {
        // Load document
        Document document = FileSystemDocumentLoader.loadDocument(filePath);

        // Add metadata
        document.metadata().putAll(metadata);

        // Split into segments
        List<TextSegment> segments = documentSplitter.split(document);

        // Generate embeddings
        List<Embedding> embeddings = embeddingModel.embedAll(segments).content();

        // Store in vector database
        embeddingStore.addAll(embeddings, segments);
    }

    public void ingestMultipleDocuments(List<String> filePaths, String userId) {
        for (String filePath : filePaths) {
            Map<String, Object> metadata = Map.of(
                "userId", userId,
                "fileName", Paths.get(filePath).getFileName().toString(),
                "ingestedAt", Instant.now().toString()
            );
            ingestDocument(filePath, metadata);
        }
    }
}
```

**Advanced Document Transformation:**
```java
public class AdvancedDocumentProcessor {

    public EmbeddingStoreIngestor createAdvancedIngestor(
            EmbeddingModel embeddingModel,
            EmbeddingStore<TextSegment> embeddingStore) {

        return EmbeddingStoreIngestor.builder()
            // Add metadata for filtering and attribution
            .documentTransformer(document -> {
                document.metadata().put("processedAt", Instant.now());
                document.metadata().put("documentType", detectDocumentType(document));
                document.metadata().put("language", detectLanguage(document.text()));
                return document;
            })

            // Intelligent text splitting
            .documentSplitter(DocumentSplitters.recursive(
                1000,  // maxSegmentSizeInTokens
                200,   // maxOverlapSizeInTokens
                new OpenAiTokenCountEstimator("gpt-4o-mini")
            ))

            // Enhance segments with context
            .textSegmentTransformer(textSegment -> {
                String fileName = textSegment.metadata().getString("file_name");
                String enhancedText = String.format("Document: %s\nContent: %s",
                    fileName, textSegment.text());
                return TextSegment.from(enhancedText, textSegment.metadata());
            })

            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();
    }

    private String detectDocumentType(Document document) {
        String text = document.text().toLowerCase();
        if (text.contains("policy") || text.contains("procedure")) {
            return "policy";
        } else if (text.contains("api") || text.contains("endpoint")) {
            return "technical";
        } else if (text.contains("faq") || text.contains("question")) {
            return "faq";
        }
        return "general";
    }

    private String detectLanguage(String text) {
        // Simple language detection logic
        // In production, use proper language detection libraries
        return "en"; // Default to English
    }
}
```

### Embedding Models and Vector Stores

**Embedding Model Configuration:**
```java
@Configuration
public class EmbeddingConfiguration {

    @Bean
    @Primary
    public EmbeddingModel primaryEmbeddingModel() {
        return OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .dimensions(1536)
            .build();
    }

    @Bean("localEmbeddingModel")
    public EmbeddingModel localEmbeddingModel() {
        // Local embedding model for privacy-sensitive applications
        return new AllMiniLmL6V2EmbeddingModel();
    }

    @Bean("multilingualEmbeddingModel")
    public EmbeddingModel multilingualEmbeddingModel() {
        return OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-large")
            .dimensions(3072)
            .build();
    }
}
```

**Vector Store Implementations:**

**PostgreSQL with pgvector:**
```java
@Configuration
public class VectorStoreConfiguration {

    @Bean
    @Primary
    public EmbeddingStore<TextSegment> pgVectorEmbeddingStore(
            @Value("${spring.datasource.url}") String jdbcUrl,
            @Value("${spring.datasource.username}") String username,
            @Value("${spring.datasource.password}") String password) {

        return PgVectorEmbeddingStore.builder()
            .host("localhost")
            .port(5432)
            .database("vector_db")
            .user(username)
            .password(password)
            .table("embeddings")
            .dimension(1536)
            .useIndex(true) // Create HNSW index for better performance
            .indexListSize(100)
            .build();
    }

    @Bean("inMemoryEmbeddingStore")
    public EmbeddingStore<TextSegment> inMemoryEmbeddingStore() {
        // For development and testing
        return new InMemoryEmbeddingStore<>();
    }
}
```

**Neo4j Vector Store:**
```java
@Bean("neo4jEmbeddingStore")
public EmbeddingStore<TextSegment> neo4jEmbeddingStore() {
    return Neo4jEmbeddingStore.builder()
        .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
        .dimension(1536)
        .label("Document")
        .embeddingProperty("embedding")
        .textProperty("text")
        .metadataPrefix("metadata_")
        .indexName("document_embeddings")
        .build();
}
```

**Elasticsearch Vector Store:**
```java
@Bean("elasticsearchEmbeddingStore")
public EmbeddingStore<TextSegment> elasticsearchEmbeddingStore() {
    RestHighLevelClient client = new RestHighLevelClient(
        RestClient.builder(new HttpHost("localhost", 9200, "http"))
    );

    return ElasticsearchEmbeddingStore.builder()
        .serverUrl("http://localhost:9200")
        .indexName("documents")
        .dimension(1536)
        .build();
}
```

### Content Retrieval Strategies

**Basic Content Retriever:**
```java
@Configuration
public class ContentRetrieverConfiguration {

    @Bean
    public ContentRetriever basicContentRetriever(
            EmbeddingStore<TextSegment> embeddingStore,
            EmbeddingModel embeddingModel) {

        return EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .minScore(0.7)
            .build();
    }
}
```

**Dynamic Content Retriever:**
```java
@Bean
public ContentRetriever dynamicContentRetriever(
        EmbeddingStore<TextSegment> embeddingStore,
        EmbeddingModel embeddingModel) {

    return EmbeddingStoreContentRetriever.builder()
        .embeddingStore(embeddingStore)
        .embeddingModel(embeddingModel)

        // Dynamic maxResults based on query complexity
        .dynamicMaxResults(query -> {
            String queryText = query.text().toLowerCase();
            if (queryText.contains("detailed") || queryText.contains("comprehensive")) {
                return 10;
            } else if (queryText.contains("brief") || queryText.contains("summary")) {
                return 3;
            }
            return 5;
        })

        // Dynamic minScore based on query type
        .dynamicMinScore(query -> {
            if (query.text().length() < 10) {
                return 0.8; // Higher threshold for short queries
            }
            return 0.6;
        })

        // Dynamic filtering based on user context
        .dynamicFilter(query -> {
            String userId = getUserIdFromQuery(query);
            if (userId != null) {
                return metadataKey("userId").isEqualTo(userId);
            }
            return null;
        })
        .build();
}
```

**Advanced Retrieval with Re-ranking:**
```java
@Service
public class AdvancedRetrievalService {

    private final EmbeddingStore<TextSegment> embeddingStore;
    private final EmbeddingModel embeddingModel;
    private final ReRankingService reRankingService;

    public List<Content> retrieveAndRerank(String query, int maxResults) {
        // Initial retrieval with higher number of candidates
        EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
            .queryEmbedding(embeddingModel.embed(query).content())
            .maxResults(maxResults * 3) // Retrieve more candidates
            .minScore(0.5) // Lower initial threshold
            .build();

        List<EmbeddingMatch<TextSegment>> matches = embeddingStore.search(searchRequest).matches();

        // Re-rank using cross-encoder model
        List<TextSegment> candidates = matches.stream()
            .map(EmbeddingMatch::embedded)
            .collect(Collectors.toList());

        List<ScoredSegment> rerankedResults = reRankingService.rerank(query, candidates);

        // Return top results after re-ranking
        return rerankedResults.stream()
            .limit(maxResults)
            .map(scored -> Content.from(scored.segment().text()))
            .collect(Collectors.toList());
    }
}
```

### AI Services with RAG Integration

**Basic RAG-Enabled AI Service:**
```java
interface KnowledgeAssistant {

    @SystemMessage("""
        You are a knowledgeable assistant with access to a comprehensive knowledge base.

        When answering questions:
        1. Use the provided context from the knowledge base
        2. If information is not in the context, clearly state this
        3. Provide accurate, helpful responses
        4. When possible, reference specific sources
        5. If the context is insufficient, ask for clarification
        """)
    String answerQuestion(String question);
}

@Service
public class KnowledgeService {

    private final KnowledgeAssistant assistant;

    public KnowledgeService(ChatModel chatModel,
                           ContentRetriever contentRetriever) {
        this.assistant = AiServices.builder(KnowledgeAssistant.class)
            .chatModel(chatModel)
            .contentRetriever(contentRetriever)
            .build();
    }

    public String answerQuestion(String question) {
        return assistant.answerQuestion(question);
    }
}
```

**Multi-Domain RAG Assistant:**
```java
interface MultiDomainAssistant {

    @SystemMessage("""
        You are an expert assistant with access to multiple knowledge domains:
        - Technical documentation
        - Company policies
        - Product information
        - Customer support guides

        Tailor your response based on the type of question and available context.
        Always indicate which domain the information comes from.
        """)
    String answerQuestion(@MemoryId String userId, String question);

    @UserMessage("Search for information about: {{topic}}")
    @SystemMessage("Find and summarize relevant information from the knowledge base.")
    String searchTopic(@V("topic") String topic);

    @UserMessage("Compare these concepts: {{concept1}} and {{concept2}}")
    @SystemMessage("Compare the concepts using information from the knowledge base.")
    String compareConcepts(@V("concept1") String concept1, @V("concept2") String concept2);
}

@Service
public class MultiDomainKnowledgeService {

    private final MultiDomainAssistant assistant;

    public MultiDomainKnowledgeService(ChatModel chatModel,
                                     EmbeddingStore<TextSegment> embeddingStore,
                                     EmbeddingModel embeddingModel) {

        // Create domain-specific retrievers
        ContentRetriever technicalRetriever = createDomainRetriever(
            embeddingStore, embeddingModel, "technical");
        ContentRetriever policyRetriever = createDomainRetriever(
            embeddingStore, embeddingModel, "policy");

        // Use composite retriever for multi-domain search
        ContentRetriever compositeRetriever = new CompositeContentRetriever(
            technicalRetriever, policyRetriever);

        this.assistant = AiServices.builder(MultiDomainAssistant.class)
            .chatModel(chatModel)
            .contentRetriever(compositeRetriever)
            .chatMemoryProvider(userId -> MessageWindowChatMemory.withMaxMessages(10))
            .build();
    }

    private ContentRetriever createDomainRetriever(
            EmbeddingStore<TextSegment> embeddingStore,
            EmbeddingModel embeddingModel,
            String domain) {

        return EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(3)
            .minScore(0.7)
            .filter(metadataKey("documentType").isEqualTo(domain))
            .build();
    }
}
```

### Advanced RAG Patterns

**Hierarchical RAG:**
```java
@Service
public class HierarchicalRAGService {

    private final EmbeddingStore<TextSegment> chunkStore;
    private final EmbeddingStore<TextSegment> summaryStore;
    private final EmbeddingModel embeddingModel;
    private final ChatModel chatModel;

    public String performHierarchicalRetrieval(String query) {
        // Step 1: Search document summaries
        List<EmbeddingMatch<TextSegment>> summaryMatches = searchSummaries(query);

        // Step 2: For each relevant summary, search detailed chunks
        List<TextSegment> relevantChunks = new ArrayList<>();
        for (EmbeddingMatch<TextSegment> summaryMatch : summaryMatches) {
            String documentId = summaryMatch.embedded().metadata().getString("documentId");
            List<EmbeddingMatch<TextSegment>> chunkMatches = searchChunksInDocument(query, documentId);
            chunkMatches.stream()
                .map(EmbeddingMatch::embedded)
                .forEach(relevantChunks::add);
        }

        // Step 3: Generate response using retrieved chunks
        return generateResponseWithChunks(query, relevantChunks);
    }

    private List<EmbeddingMatch<TextSegment>> searchSummaries(String query) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(5)
            .minScore(0.7)
            .filter(metadataKey("type").isEqualTo("summary"))
            .build();
        return summaryStore.search(request).matches();
    }

    private List<EmbeddingMatch<TextSegment>> searchChunksInDocument(String query, String documentId) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(10)
            .minScore(0.6)
            .filter(metadataKey("documentId").isEqualTo(documentId))
            .build();
        return chunkStore.search(request).matches();
    }
}
```

**Query Expansion and Rewriting:**
```java
@Service
public class QueryProcessingService {

    private final ChatModel chatModel;
    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;

    public List<Content> retrieveWithQueryExpansion(String originalQuery) {
        // Generate alternative query formulations
        List<String> expandedQueries = expandQuery(originalQuery);

        // Search with all query variations
        Set<TextSegment> allResults = new HashSet<>();
        for (String query : expandedQueries) {
            List<EmbeddingMatch<TextSegment>> matches = performSingleSearch(query);
            matches.stream()
                .map(EmbeddingMatch::embedded)
                .forEach(allResults::add);
        }

        // Deduplicate and rank results
        return rankAndDeduplicateResults(originalQuery, allResults);
    }

    private List<String> expandQuery(String originalQuery) {
        String expansionPrompt = String.format("""
            Generate 3 alternative ways to ask this question while preserving the core intent:

            Original question: %s

            Return only the alternative questions, one per line.
            """, originalQuery);

        String response = chatModel.chat(expansionPrompt);
        List<String> expandedQueries = new ArrayList<>();
        expandedQueries.add(originalQuery); // Include original
        expandedQueries.addAll(Arrays.asList(response.split("\n")));

        return expandedQueries;
    }

    private List<EmbeddingMatch<TextSegment>> performSingleSearch(String query) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(5)
            .minScore(0.6)
            .build();
        return embeddingStore.search(request).matches();
    }
}
```

**Hybrid Search (Vector + Keyword):**
```java
@Service
public class HybridSearchService {

    private final EmbeddingStore<TextSegment> vectorStore;
    private final FullTextSearchEngine fullTextEngine;
    private final EmbeddingModel embeddingModel;

    public List<Content> hybridSearch(String query, int maxResults) {
        // Vector search
        List<ScoredResult> vectorResults = performVectorSearch(query, maxResults * 2);

        // Keyword search
        List<ScoredResult> keywordResults = performKeywordSearch(query, maxResults * 2);

        // Combine and re-rank results
        return combineAndRerankResults(vectorResults, keywordResults, maxResults);
    }

    private List<ScoredResult> performVectorSearch(String query, int maxResults) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(maxResults)
            .minScore(0.5)
            .build();

        return vectorStore.search(request).matches().stream()
            .map(match -> new ScoredResult(
                match.embedded(),
                match.score(),
                "vector"
            ))
            .collect(Collectors.toList());
    }

    private List<ScoredResult> performKeywordSearch(String query, int maxResults) {
        return fullTextEngine.search(query, maxResults).stream()
            .map(result -> new ScoredResult(
                result.getTextSegment(),
                result.getScore(),
                "keyword"
            ))
            .collect(Collectors.toList());
    }

    private List<Content> combineAndRerankResults(
            List<ScoredResult> vectorResults,
            List<ScoredResult> keywordResults,
            int maxResults) {

        // Reciprocal Rank Fusion (RRF) algorithm
        Map<String, Double> combinedScores = new HashMap<>();
        Map<String, TextSegment> segments = new HashMap<>();

        // Process vector results
        for (int i = 0; i < vectorResults.size(); i++) {
            ScoredResult result = vectorResults.get(i);
            String id = result.getSegment().metadata().getString("id");
            double score = 1.0 / (60 + i + 1); // RRF formula
            combinedScores.put(id, combinedScores.getOrDefault(id, 0.0) + score);
            segments.put(id, result.getSegment());
        }

        // Process keyword results
        for (int i = 0; i < keywordResults.size(); i++) {
            ScoredResult result = keywordResults.get(i);
            String id = result.getSegment().metadata().getString("id");
            double score = 1.0 / (60 + i + 1); // RRF formula
            combinedScores.put(id, combinedScores.getOrDefault(id, 0.0) + score);
            segments.put(id, result.getSegment());
        }

        // Sort by combined score and return top results
        return combinedScores.entrySet().stream()
            .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
            .limit(maxResults)
            .map(entry -> Content.from(segments.get(entry.getKey()).text()))
            .collect(Collectors.toList());
    }
}
```

### Web Search Integration

**Web Search Content Retriever:**
```java
@Configuration
public class WebSearchConfiguration {

    @Bean
    public WebSearchEngine googleSearchEngine() {
        return GoogleCustomWebSearchEngine.builder()
            .apiKey(System.getenv("GOOGLE_API_KEY"))
            .csi(System.getenv("GOOGLE_SEARCH_ENGINE_ID"))
            .build();
    }

    @Bean
    public ContentRetriever webSearchContentRetriever(WebSearchEngine webSearchEngine) {
        return WebSearchContentRetriever.builder()
            .webSearchEngine(webSearchEngine)
            .maxResults(5)
            .build();
    }

    @Bean
    public ContentRetriever hybridWebKnowledgeRetriever(
            ContentRetriever localContentRetriever,
            ContentRetriever webSearchContentRetriever) {

        return new HybridContentRetriever(localContentRetriever, webSearchContentRetriever);
    }
}

@Component
public class HybridContentRetriever implements ContentRetriever {

    private final ContentRetriever localRetriever;
    private final ContentRetriever webRetriever;

    public HybridContentRetriever(ContentRetriever localRetriever,
                                 ContentRetriever webRetriever) {
        this.localRetriever = localRetriever;
        this.webRetriever = webRetriever;
    }

    @Override
    public List<Content> retrieve(Query query) {
        // First try local knowledge base
        List<Content> localResults = localRetriever.retrieve(query);

        // If insufficient local results, supplement with web search
        if (localResults.size() < 3) {
            List<Content> webResults = webRetriever.retrieve(query);

            // Combine results, preferring local content
            List<Content> combinedResults = new ArrayList<>(localResults);
            combinedResults.addAll(webResults.stream()
                .limit(5 - localResults.size())
                .collect(Collectors.toList()));

            return combinedResults;
        }

        return localResults;
    }
}
```

## API Reference

### Core Interfaces

**EmbeddingStore Interface:**
```java
// Add embeddings
String add(Embedding embedding);
String add(String id, Embedding embedding);
String add(Embedding embedding, TextSegment textSegment);
List<String> addAll(List<Embedding> embeddings);
List<String> addAll(List<Embedding> embeddings, List<TextSegment> textSegments);

// Search embeddings
EmbeddingSearchResult<TextSegment> search(EmbeddingSearchRequest request);

// Remove embeddings
void remove(String id);
void removeAll(List<String> ids);
void removeAll(Filter filter);
void removeAll();
```

**EmbeddingModel Interface:**
```java
// Embed single text
Response<Embedding> embed(String text);
Response<Embedding> embed(TextSegment textSegment);

// Embed multiple texts
Response<List<Embedding>> embedAll(List<TextSegment> textSegments);

// Get model dimension
int dimension();
```

**ContentRetriever Interface:**
```java
List<Content> retrieve(Query query);
```

**DocumentSplitter Interface:**
```java
List<TextSegment> split(Document document);
List<TextSegment> splitAll(List<Document> documents);
```

### Configuration Classes

**EmbeddingStoreContentRetriever.Builder:**
```java
EmbeddingStoreContentRetriever.builder()
    .embeddingStore(EmbeddingStore)           // Required
    .embeddingModel(EmbeddingModel)           // Required
    .maxResults(int)                          // Default: 3
    .minScore(double)                         // Default: 0.0
    .filter(Filter)                           // Optional
    .dynamicMaxResults(Function<Query, Integer>)
    .dynamicMinScore(Function<Query, Double>)
    .dynamicFilter(Function<Query, Filter>)
    .build();
```

**EmbeddingStoreIngestor.Builder:**
```java
EmbeddingStoreIngestor.builder()
    .embeddingModel(EmbeddingModel)           // Required
    .embeddingStore(EmbeddingStore)           // Required
    .documentTransformer(DocumentTransformer) // Optional
    .documentSplitter(DocumentSplitter)       // Optional
    .textSegmentTransformer(TextSegmentTransformer) // Optional
    .build();
```

### Common Document Splitters

**Recursive Character Text Splitter:**
```java
DocumentSplitter recursive = DocumentSplitters.recursive(
    500,    // maxSegmentSizeInTokens
    50,     // maxOverlapSizeInTokens
    new OpenAiTokenCountEstimator("gpt-4o-mini")
);
```

**Paragraph Splitter:**
```java
DocumentSplitter paragraph = DocumentSplitters.paragraph(
    1000,   // maxSegmentSizeInTokens
    new OpenAiTokenCountEstimator("gpt-4o-mini")
);
```

**Sentence Splitter:**
```java
DocumentSplitter sentence = DocumentSplitters.sentence(
    300,    // maxSegmentSizeInTokens
    new OpenAiTokenCountEstimator("gpt-4o-mini")
);
```

### Metadata Filtering

**Filter Construction:**
```java
// Equality filters
Filter userFilter = metadataKey("userId").isEqualTo("12345");
Filter typeFilter = metadataKey("documentType").isEqualTo("policy");

// Comparison filters
Filter scoreFilter = metadataKey("score").isGreaterThan(0.8);
Filter dateFilter = metadataKey("createdAt").isLessThan("2024-01-01");

// Collection filters
Filter categoryFilter = metadataKey("category").isIn(List.of("tech", "business"));

// Logical operators
Filter complexFilter = new And(
    userFilter,
    new Or(typeFilter, categoryFilter)
);

Filter notFilter = new Not(metadataKey("status").isEqualTo("draft"));
```

## Workflow Patterns

### Complete RAG Application Architecture

```java
@SpringBootApplication
public class RAGApplication {

    public static void main(String[] args) {
        SpringApplication.run(RAGApplication.class, args);
    }
}

@RestController
@RequestMapping("/api/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {

    private final DocumentIngestionService ingestionService;
    private final KnowledgeQueryService queryService;

    @PostMapping("/ingest")
    public ResponseEntity<String> ingestDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam("userId") String userId) {
        try {
            String documentId = ingestionService.ingestDocument(file, userId);
            return ResponseEntity.ok("Document ingested: " + documentId);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }

    @PostMapping("/query")
    public ResponseEntity<QueryResponse> query(@RequestBody QueryRequest request) {
        try {
            QueryResponse response = queryService.answerQuestion(
                request.getUserId(),
                request.getQuestion()
            );
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(
                QueryResponse.error("Error processing query: " + e.getMessage())
            );
        }
    }

    @GetMapping("/documents/{userId}")
    public ResponseEntity<List<DocumentSummary>> getUserDocuments(@PathVariable String userId) {
        List<DocumentSummary> documents = ingestionService.getUserDocuments(userId);
        return ResponseEntity.ok(documents);
    }
}
```

### Multi-Tenant RAG System

```java
@Service
public class MultiTenantRAGService {

    private final Map<String, EmbeddingStore<TextSegment>> tenantStores;
    private final EmbeddingModel embeddingModel;
    private final ChatModel chatModel;

    public String queryTenantKnowledge(String tenantId, String userId, String question) {
        // Get tenant-specific embedding store
        EmbeddingStore<TextSegment> tenantStore = getTenantStore(tenantId);

        // Create content retriever with tenant and user filtering
        ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(tenantStore)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .minScore(0.7)
            .filter(new And(
                metadataKey("tenantId").isEqualTo(tenantId),
                metadataKey("userId").isEqualTo(userId)
            ))
            .build();

        // Create AI service with retriever
        TenantAssistant assistant = AiServices.builder(TenantAssistant.class)
            .chatModel(chatModel)
            .contentRetriever(retriever)
            .build();

        return assistant.answerQuestion(question);
    }

    private EmbeddingStore<TextSegment> getTenantStore(String tenantId) {
        return tenantStores.computeIfAbsent(tenantId, id -> createTenantStore(id));
    }

    private EmbeddingStore<TextSegment> createTenantStore(String tenantId) {
        return PgVectorEmbeddingStore.builder()
            .host("localhost")
            .port(5432)
            .database("tenant_" + tenantId)
            .user("rag_user")
            .password("password")
            .table("embeddings")
            .dimension(1536)
            .build();
    }
}
```

### Streaming RAG Responses

```java
interface StreamingKnowledgeAssistant {

    @SystemMessage("""
        You are a knowledge assistant. Provide detailed, accurate responses
        based on the retrieved context. Stream your response progressively.
        """)
    Flux<String> answerQuestionStream(String question);
}

@RestController
public class StreamingRAGController {

    private final StreamingKnowledgeAssistant assistant;

    @PostMapping(value = "/stream-query", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> streamQuery(@RequestBody String question) {
        return assistant.answerQuestionStream(question)
            .onErrorReturn("An error occurred while processing your question.");
    }
}
```

## Best Practices

### 1. Optimal Text Segmentation

```java
// Good - Context-aware segmentation
DocumentSplitter intelligentSplitter = DocumentSplitters.recursive(
    500,    // Optimal chunk size for most models
    50,     // Sufficient overlap for context preservation
    new OpenAiTokenCountEstimator("gpt-4o-mini")
);

// Consider document structure
DocumentSplitter hierarchicalSplitter = new HierarchicalDocumentSplitter(
    Map.of(
        "heading", 800,      // Larger chunks for headings
        "paragraph", 400,    // Medium chunks for paragraphs
        "list", 200         // Smaller chunks for lists
    )
);
```

### 2. Metadata Strategy

```java
// Good - Rich metadata for filtering and attribution
Map<String, Object> metadata = Map.of(
    "userId", userId,
    "documentType", "policy",
    "department", "HR",
    "lastUpdated", Instant.now(),
    "confidentialityLevel", "internal",
    "version", "1.2",
    "author", "john.doe@company.com",
    "tags", List.of("employment", "benefits", "vacation")
);
```

### 3. Query Processing Pipeline

```java
@Service
public class QueryProcessingPipeline {

    public String processQuery(String rawQuery, String userId) {
        // 1. Clean and normalize query
        String cleanQuery = cleanQuery(rawQuery);

        // 2. Detect query intent
        QueryIntent intent = detectIntent(cleanQuery);

        // 3. Apply query expansion if needed
        String expandedQuery = shouldExpandQuery(intent)
            ? expandQuery(cleanQuery)
            : cleanQuery;

        // 4. Perform retrieval with appropriate strategy
        List<Content> results = retrieveContent(expandedQuery, userId, intent);

        // 5. Generate response
        return generateResponse(expandedQuery, results, intent);
    }

    private String cleanQuery(String query) {
        return query.trim()
            .replaceAll("\\s+", " ")
            .toLowerCase();
    }

    private QueryIntent detectIntent(String query) {
        if (query.contains("compare") || query.contains("difference")) {
            return QueryIntent.COMPARISON;
        } else if (query.contains("how to") || query.contains("steps")) {
            return QueryIntent.PROCEDURAL;
        } else if (query.contains("what is") || query.contains("define")) {
            return QueryIntent.DEFINITIONAL;
        }
        return QueryIntent.GENERAL;
    }
}
```

### 4. Performance Optimization

```java
// Good - Implement caching for embeddings
@Service
@RequiredArgsConstructor
public class CachedEmbeddingService {

    private final EmbeddingModel embeddingModel;
    private final Cache<String, Embedding> embeddingCache;

    @Cacheable("embeddings")
    public Embedding embed(String text) {
        return embeddingCache.computeIfAbsent(text,
            t -> embeddingModel.embed(t).content());
    }

    @Async
    public CompletableFuture<List<Embedding>> embedAllAsync(List<String> texts) {
        List<Embedding> embeddings = texts.parallelStream()
            .map(this::embed)
            .collect(Collectors.toList());
        return CompletableFuture.completedFuture(embeddings);
    }
}
```

### 5. Error Handling and Resilience

```java
@Service
public class ResilientRAGService {

    private final List<ContentRetriever> retrievers;
    private final CircuitBreaker circuitBreaker;

    public List<Content> retrieveWithFallback(String query) {
        return circuitBreaker.executeSupplier(() -> {
            for (ContentRetriever retriever : retrievers) {
                try {
                    List<Content> results = retriever.retrieve(Query.from(query));
                    if (!results.isEmpty()) {
                        return results;
                    }
                } catch (Exception e) {
                    log.warn("Retriever failed, trying next: {}", e.getMessage());
                }
            }
            return Collections.emptyList();
        });
    }
}
```

### 6. Monitoring and Observability

```java
@Component
public class RAGMetrics {

    private final MeterRegistry meterRegistry;
    private final Counter retrievalCounter;
    private final Timer retrievalTimer;
    private final Gauge embeddingStoreSize;

    public RAGMetrics(MeterRegistry meterRegistry, EmbeddingStore<?> embeddingStore) {
        this.meterRegistry = meterRegistry;
        this.retrievalCounter = Counter.builder("rag.retrievals.total")
            .description("Total number of retrievals")
            .register(meterRegistry);
        this.retrievalTimer = Timer.builder("rag.retrieval.duration")
            .description("Retrieval operation duration")
            .register(meterRegistry);
        this.embeddingStoreSize = Gauge.builder("rag.embeddings.count")
            .description("Number of embeddings in store")
            .register(meterRegistry, embeddingStore, this::countEmbeddings);
    }

    public void recordRetrieval(Duration duration, int resultCount) {
        retrievalCounter.increment(Tags.of("result_count", String.valueOf(resultCount)));
        retrievalTimer.record(duration);
    }

    private double countEmbeddings(EmbeddingStore<?> store) {
        // Implementation depends on the specific store
        return 0.0;
    }
}
```

## Summary

This LangChain4j RAG implementation skill covers:

1. **Document Ingestion**: File loading, preprocessing, metadata enrichment, and batch processing
2. **Text Segmentation**: Recursive splitting, paragraph-based splitting, token-aware strategies
3. **Embedding Generation**: Model selection, batch processing, caching strategies
4. **Vector Storage**: PostgreSQL pgvector, Neo4j, Elasticsearch, in-memory options
5. **Content Retrieval**: Basic retrieval, dynamic parameters, filtering, re-ranking
6. **AI Integration**: RAG-enabled AI services, multi-domain assistants, streaming responses
7. **Advanced Patterns**: Hierarchical RAG, query expansion, hybrid search, web integration
8. **Production Concerns**: Multi-tenancy, error handling, monitoring, performance optimization
9. **Best Practices**: Optimal chunking, metadata strategies, query processing, resilience
10. **Observability**: Metrics collection, performance monitoring, debugging strategies
