# LangChain4J Skills Guide

Quick reference to 8 LangChain4J skills for building AI-powered applications. See individual skill files for complete details.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **langchain4j-spring-boot-integration** | LangChain4J with Spring Boot, bean management |
| **langchain4j-ai-services-patterns** | AI service design, model configuration |
| **langchain4j-rag-implementation-patterns** | RAG systems, vector stores, retrievers |
| **langchain4j-vector-stores-configuration** | Vector store setup, embeddings, similarity search |
| **langchain4j-tool-function-calling-patterns** | Tool definition, function orchestration |
| **langchain4j-mcp-server-patterns** | MCP integration, tool exposure |
| **langchain4j-testing-strategies** | Testing AI systems, mock models |
| **qdrant** | Qdrant vector database integration |
| **spring-ai-mcp-server-patterns** | Spring AI MCP server patterns |

---

## Core Integration

### langchain4j-spring-boot-integration

**File**: `skills/langchain4j-spring-boot-integration/SKILL.md`

Integrate LangChain4J with Spring Boot: beans, configuration, auto-wiring.

**When to use:**
- Setting up LangChain4J in Spring Boot
- Configuring AI service beans
- Model provider integration

---

## AI Services

### langchain4j-ai-services-patterns

**File**: `skills/langchain4j-ai-services-patterns/SKILL.md`

AI service design: service patterns, model configuration, error handling.

**When to use:**
- Designing AI service interfaces
- Model configuration and selection
- Prompt templating and execution

**Pattern:**
```java
@Service
public class ChatService {
    private final ChatLanguageModel model;
    
    public String answer(String question) {
        return model.generate(question);
    }
}
```

---

## Retrieval-Augmented Generation (RAG)

### langchain4j-rag-implementation-patterns

**File**: `skills/langchain4j-rag-implementation-patterns/SKILL.md`

RAG systems: document processing, retriever chains, augmented generation.

**When to use:**
- Building RAG systems
- Knowledge base integration
- Document retrieval and generation

---

### langchain4j-vector-stores-configuration

**File**: `skills/langchain4j-vector-stores-configuration/SKILL.md`

Vector stores: embeddings, similarity search, provider setup.

**When to use:**
- Configuring embeddings
- Vector database setup
- Similarity search implementation

---

### qdrant

**File**: `skills/qdrant/SKILL.md`

Qdrant vector database: Java integration, Spring Boot setup.

**When to use:**
- Using Qdrant for vector storage
- Embedding storage and retrieval
- Hybrid search patterns

---

### spring-ai-mcp-server-patterns

**File**: `skills/spring-ai-mcp-server-patterns/SKILL.md`

Spring AI MCP server: protocol implementation, tool exposure.

**When to use:**
- Creating MCP servers with Spring AI
- Exposing tools to AI agents
- Spring AI MCP protocol integration

---

## Advanced Patterns

### langchain4j-tool-function-calling-patterns

**File**: `skills/langchain4j-tool-function-calling-patterns/SKILL.md`

Tool definition: function calling, agent patterns, orchestration.

**When to use:**
- AI agents with tool access
- Function calling and execution
- Multi-step reasoning

---

### langchain4j-mcp-server-patterns

**File**: `skills/langchain4j-mcp-server-patterns/SKILL.md`

MCP servers: tool exposure, data access, integration.

**When to use:**
- Creating MCP servers
- Exposing tools to AI agents
- Model Context Protocol integration

---

## Testing

### langchain4j-testing-strategies

**File**: `skills/langchain4j-testing-strategies/SKILL.md`

Testing AI systems: mock models, test containers, integration tests.

**When to use:**
- Unit testing AI services
- Integration testing RAG
- Mock model behavior

---

## Common Workflows

### Building a RAG System

```
1. langchain4j-spring-boot-integration    → Spring Boot setup
2. langchain4j-vector-stores-configuration → Embeddings + storage
3. langchain4j-rag-implementation-patterns → RAG retriever + generator
4. langchain4j-testing-strategies         → Test RAG pipelines
```

### Creating AI Service

```
1. langchain4j-spring-boot-integration    → Spring setup
2. langchain4j-ai-services-patterns       → Service interface
3. langchain4j-testing-strategies         → Unit tests
```

### Building AI Agent with Tools

```
1. langchain4j-spring-boot-integration    → Spring setup
2. langchain4j-ai-services-patterns       → Agent service
3. langchain4j-tool-function-calling-patterns → Tool definition
4. langchain4j-mcp-server-patterns        → MCP exposure
5. langchain4j-testing-strategies         → Agent tests
```

### Full RAG + Agent System

```
1. langchain4j-spring-boot-integration    → Setup
2. langchain4j-vector-stores-configuration → Vector DB
3. langchain4j-rag-implementation-patterns → RAG system
4. langchain4j-tool-function-calling-patterns → Tool calling
5. langchain4j-mcp-server-patterns        → MCP servers
6. langchain4j-testing-strategies         → Integration tests
```

---

## Technology Stack

- **LangChain4J**: Latest stable
- **Spring Boot**: 3.5.x+
- **Embeddings**: OpenAI, Hugging Face
- **Vector Stores**: Qdrant, Milvus, Weaviate
- **LLMs**: OpenAI, Anthropic Claude, Ollama
- **Testing**: Mock models, testcontainers

---

## Key Concepts

### AI Services
- Language models and providers
- Prompt templating
- Response parsing
- Error handling

### RAG (Retrieval-Augmented Generation)
- Document indexing
- Similarity search
- Retrieved context augmentation
- Multi-step retrieval

### Function Calling
- Tool definition and description
- Function execution
- Result integration
- Reasoning loops

### MCP (Model Context Protocol)
- Server implementation
- Tool exposure
- Resource management
- Client communication

---

**Note**: For complete patterns and examples, see individual skill files in `skills/`
