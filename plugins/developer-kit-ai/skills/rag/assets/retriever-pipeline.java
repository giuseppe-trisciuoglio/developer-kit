package com.example.rag;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.parser.TextDocumentParser;
import dev.langchain4j.data.document.splitter.RecursiveCharacterTextSplitter;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import dev.langchain4j.store.embedding.pinecone.PineconeEmbeddingStore;
import dev.langchain4j.store.embedding.chroma.ChromaEmbeddingStore;
import dev.langchain4j.store.embedding.qdrant.QdrantEmbeddingStore;
import dev.langchain4j.data.document.loader.FileSystemDocumentLoader;
import dev.langchain4j.store.embedding.filter.Filter;
import dev.langchain4j.store.embedding.filter.MetadataFilterBuilder;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Complete RAG Pipeline Implementation
 *
 * This class provides a comprehensive implementation of a RAG (Retrieval-Augmented Generation)
 * system with support for multiple vector stores and advanced retrieval strategies.
 */
public class RAGPipeline {

    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;
    private final DocumentSplitter documentSplitter;
    private final RAGConfig config;

    /**
     * Configuration class for RAG pipeline
     */
    public static class RAGConfig {
        private String vectorStoreType = "chroma";
        private String openAiApiKey;
        private String pineconeApiKey;
        private String pineconeEnvironment;
        private String pineconeIndex = "rag-documents";
        private String chromaCollection = "rag-documents";
        private String chromaPersistPath = "./chroma_db";
        private String qdrantHost = "localhost";
        private int qdrantPort = 6333;
        private String qdrantCollection = "rag-documents";
        private int chunkSize = 1000;
        private int chunkOverlap = 200;
        private int embeddingDimension = 1536;

        // Getters and setters
        public String getVectorStoreType() { return vectorStoreType; }
        public void setVectorStoreType(String vectorStoreType) { this.vectorStoreType = vectorStoreType; }
        public String getOpenAiApiKey() { return openAiApiKey; }
        public void setOpenAiApiKey(String openAiApiKey) { this.openAiApiKey = openAiApiKey; }
        public String getPineconeApiKey() { return pineconeApiKey; }
        public void setPineconeApiKey(String pineconeApiKey) { this.pineconeApiKey = pineconeApiKey; }
        public String getPineconeEnvironment() { return pineconeEnvironment; }
        public void setPineconeEnvironment(String pineconeEnvironment) { this.pineconeEnvironment = pineconeEnvironment; }
        public String getPineconeIndex() { return pineconeIndex; }
        public void setPineconeIndex(String pineconeIndex) { this.pineconeIndex = pineconeIndex; }
        public String getChromaCollection() { return chromaCollection; }
        public void setChromaCollection(String chromaCollection) { this.chromaCollection = chromaCollection; }
        public String getChromaPersistPath() { return chromaPersistPath; }
        public void setChromaPersistPath(String chromaPersistPath) { this.chromaPersistPath = chromaPersistPath; }
        public String getQdrantHost() { return qdrantHost; }
        public void setQdrantHost(String qdrantHost) { this.qdrantHost = qdrantHost; }
        public int getQdrantPort() { return qdrantPort; }
        public void setQdrantPort(int qdrantPort) { this.qdrantPort = qdrantPort; }
        public String getQdrantCollection() { return qdrantCollection; }
        public void setQdrantCollection(String qdrantCollection) { this.qdrantCollection = qdrantCollection; }
        public int getChunkSize() { return chunkSize; }
        public void setChunkSize(int chunkSize) { this.chunkSize = chunkSize; }
        public int getChunkOverlap() { return chunkOverlap; }
        public void setChunkOverlap(int chunkOverlap) { this.chunkOverlap = chunkOverlap; }
        public int getEmbeddingDimension() { return embeddingDimension; }
        public void setEmbeddingDimension(int embeddingDimension) { this.embeddingDimension = embeddingDimension; }
    }

    /**
     * Constructor
     */
    public RAGPipeline(RAGConfig config) {
        this.config = config;
        this.embeddingModel = createEmbeddingModel();
        this.embeddingStore = createEmbeddingStore();
        this.documentSplitter = createDocumentSplitter();
    }

    /**
     * Create embedding model based on configuration
     */
    private EmbeddingModel createEmbeddingModel() {
        return OpenAiEmbeddingModel.builder()
                .apiKey(config.getOpenAiApiKey())
                .modelName("text-embedding-ada-002")
                .build();
    }

    /**
     * Create embedding store based on configuration
     */
    private EmbeddingStore<TextSegment> createEmbeddingStore() {
        switch (config.getVectorStoreType().toLowerCase()) {
            case "pinecone":
                return PineconeEmbeddingStore.builder()
                        .apiKey(config.getPineconeApiKey())
                        .environment(config.getPineconeEnvironment())
                        .index(config.getPineconeIndex())
                        .dimension(config.getEmbeddingDimension())
                        .build();

            case "chroma":
                return ChromaEmbeddingStore.builder()
                        .collectionName(config.getChromaCollection())
                        .persistDirectory(config.getChromaPersistPath())
                        .build();

            case "qdrant":
                return QdrantEmbeddingStore.builder()
                        .host(config.getQdrantHost())
                        .port(config.getQdrantPort())
                        .collectionName(config.getQdrantCollection())
                        .dimension(config.getEmbeddingDimension())
                        .build();

            case "memory":
            default:
                return new InMemoryEmbeddingStore<>();
        }
    }

    /**
     * Create document splitter
     */
    private DocumentSplitter createDocumentSplitter() {
        return new RecursiveCharacterTextSplitter(
                config.getChunkSize(),
                config.getChunkOverlap()
        );
    }

    /**
     * Load documents from directory
     */
    public List<Document> loadDocuments(String directoryPath) {
        try {
            Path directory = Paths.get(directoryPath);
            List<Document> documents = FileSystemDocumentLoader.loadDocuments(directory);

            // Add metadata to documents
            for (Document document : documents) {
                Map<String, Object> metadata = new HashMap<>(document.metadata().toMap());
                metadata.put("loaded_at", System.currentTimeMillis());
                metadata.put("source_directory", directoryPath);

                // Update document metadata
                document = Document.from(document.text(), metadata);
            }

            return documents;
        } catch (Exception e) {
            throw new RuntimeException("Failed to load documents from " + directoryPath, e);
        }
    }

    /**
     * Process and ingest documents
     */
    public void ingestDocuments(List<Document> documents) {
        // Split documents into segments
        List<TextSegment> segments = documentSplitter.split(documents);

        // Add additional metadata to segments
        for (int i = 0; i < segments.size(); i++) {
            TextSegment segment = segments.get(i);
            Map<String, Object> metadata = new HashMap<>(segment.metadata().toMap());
            metadata.put("segment_index", i);
            metadata.put("total_segments", segments.size());
            metadata.put("processed_at", System.currentTimeMillis());

            segments.set(i, TextSegment.from(segment.text(), metadata));
        }

        // Ingest into embedding store
        EmbeddingStoreIngestor.ingest(segments, embeddingStore);

        System.out.println("Ingested " + documents.size() + " documents into " +
                          segments.size() + " segments");
    }

    /**
     * Search documents with optional filtering
     */
    public List<TextSegment> search(String query, int maxResults, Filter filter) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();

        return embeddingStore.findRelevant(queryEmbedding, maxResults, filter);
    }

    /**
     * Search documents with metadata filtering
     */
    public List<TextSegment> searchWithMetadataFilter(String query, int maxResults,
                                                    Map<String, Object> metadataFilters) {
        Filter filter = null;

        if (metadataFilters != null && !metadataFilters.isEmpty()) {
            MetadataFilterBuilder filterBuilder = new MetadataFilterBuilder();

            for (Map.Entry<String, Object> entry : metadataFilters.entrySet()) {
                String key = entry.getKey();
                Object value = entry.getValue();

                if (value instanceof String) {
                    filterBuilder = filterBuilder.metadata(key).isEqualTo((String) value);
                } else if (value instanceof Number) {
                    filterBuilder = filterBuilder.metadata(key).isEqualTo(((Number) value).doubleValue());
                }
                // Add more type handling as needed
            }

            filter = filterBuilder.build();
        }

        return search(query, maxResults, filter);
    }

    /**
     * Get statistics about the stored documents
     */
    public RAGStatistics getStatistics() {
        // This is a simplified implementation
        // In practice, you might want to track more detailed statistics
        return new RAGStatistics(
                embeddingStore.getClass().getSimpleName(),
                config.getVectorStoreType()
        );
    }

    /**
     * Statistics holder class
     */
    public static class RAGStatistics {
        private final String storeType;
        private final String implementation;

        public RAGStatistics(String storeType, String implementation) {
            this.storeType = storeType;
            this.implementation = implementation;
        }

        public String getStoreType() { return storeType; }
        public String getImplementation() { return implementation; }

        @Override
        public String toString() {
            return "RAGStatistics{" +
                    "storeType='" + storeType + '\'' +
                    ", implementation='" + implementation + '\'' +
                    '}';
        }
    }

    /**
     * Example usage
     */
    public static void main(String[] args) {
        // Configure the pipeline
        RAGConfig config = new RAGConfig();
        config.setVectorStoreType("chroma"); // or "pinecone", "qdrant", "memory"
        config.setOpenAiApiKey("your-openai-api-key");
        config.setChunkSize(1000);
        config.setChunkOverlap(200);

        // Create pipeline
        RAGPipeline pipeline = new RAGPipeline(config);

        // Load documents
        List<Document> documents = pipeline.loadDocuments("./documents");

        // Ingest documents
        pipeline.ingestDocuments(documents);

        // Search for relevant content
        List<TextSegment> results = pipeline.search("What is machine learning?", 5, null);

        // Print results
        for (int i = 0; i < results.size(); i++) {
            TextSegment segment = results.get(i);
            System.out.println("Result " + (i + 1) + ":");
            System.out.println("Content: " + segment.text().substring(0, Math.min(200, segment.text().length())) + "...");
            System.out.println("Metadata: " + segment.metadata());
            System.out.println();
        }

        // Print statistics
        System.out.println("Pipeline Statistics: " + pipeline.getStatistics());
    }
}