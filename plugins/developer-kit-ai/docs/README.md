# Developer Kit AI Plugin — Documentation

## Overview

The AI plugin provides Claude Code with specialized capabilities for building AI-powered applications. It covers the full lifecycle of LLM integration:

- **Prompt Engineering** — designing, optimizing, and scaling prompts
- **RAG Systems** — retrieval-augmented generation pipelines
- **Chunking Strategies** — document preprocessing for vector databases

## Plugin Structure

```
developer-kit-ai/
├── agents/
│   └── prompt-engineering-expert.md     # Expert agent for prompt design
├── commands/
│   └── devkit.prompt-optimize.md        # Prompt optimization command
├── skills/
│   ├── prompt-engineering/              # Prompt design & optimization skill
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── cot-patterns.md
│   │       ├── few-shot-patterns.md
│   │       ├── optimization-frameworks.md
│   │       ├── system-prompt-design.md
│   │       └── template-systems.md
│   ├── rag/                             # RAG implementation skill
│   │   ├── SKILL.md
│   │   ├── assets/
│   │   │   ├── retriever-pipeline.java
│   │   │   └── vector-store-config.yaml
│   │   └── references/
│   │       ├── document-chunking.md
│   │       ├── embedding-models.md
│   │       ├── langchain4j-rag-guide.md
│   │       ├── retrieval-strategies.md
│   │       └── vector-databases.md
│   └── chunking-strategy/               # Document chunking skill
│       ├── SKILL.md
│       └── references/
│           ├── advanced-strategies.md
│           ├── evaluation.md
│           ├── implementation.md
│           ├── research.md
│           ├── semantic-methods.md
│           ├── strategies.md
│           ├── tools.md
│           └── visualization-tools.md
└── docs/
    ├── README.md                        # This file
    ├── guide-agents.md                  # Agent guide
    └── guide-commands.md                 # Command guide
```

## Available Components

| Type | Count | Details |
|------|-------|---------|
| Skills | 3 | prompt-engineering, rag, chunking-strategy |
| Agents | 1 | prompt-engineering-expert |
| Commands | 1 | devkit.prompt-optimize |

## Quick Start

1. **Optimize a prompt** — use [`/developer-kit-ai:devkit.prompt-optimize`](guide-commands.md) with your prompt text
2. **Design a prompt** — invoke the `prompt-engineering-expert` agent for new prompt creation
3. **Build a RAG pipeline** — use the `rag` skill with the LangChain4j reference guide
4. **Choose chunking strategy** — use the `chunking-strategy` skill to select the right approach for your data

## Key Features

### Prompt Engineering

- Few-shot learning with strategic example selection
- Chain-of-thought and tree-of-thought reasoning
- System prompt architecture and role definition
- Prompt template systems with modular composition
- A/B testing and progressive optimization frameworks

### Retrieval-Augmented Generation

- Vector database selection and configuration (Pinecone, Weaviate, Milvus, Chroma, Qdrant, FAISS)
- Embedding model selection (OpenAI, Sentence Transformers, Hugging Face)
- Retrieval strategies: dense, sparse, hybrid, reranking
- LangChain4j integration with complete Java examples

### Chunking Strategies

- 5-level strategy hierarchy: fixed-size (L1) through advanced semantic methods (L5)
- Semantic coherence validation
- Retrieval precision/recall evaluation metrics
- Integration with LangChain, LlamaIndex, and Unstructured

## See Also

- [Core Plugin Documentation](../../developer-kit-core/docs/) — Installation and core workflow guides
- [Java Plugin Documentation](../../developer-kit-java/docs/) — LangChain4j, Spring Boot, and AWS Lambda Java integration
- [Python Plugin Documentation](../../developer-kit-python/docs/) — Python AI/ML development guides
- [TypeScript Plugin Documentation](../../developer-kit-typescript/docs/) — TypeScript and Node.js AI integration
