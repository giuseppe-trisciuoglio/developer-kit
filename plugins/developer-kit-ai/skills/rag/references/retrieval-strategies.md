# Advanced Retrieval Strategies

## Overview
Different retrieval approaches for finding relevant documents in RAG systems, each with specific strengths and use cases.

## Retrieval Approaches

### 1. Dense Retrieval
**Method**: Semantic similarity via embeddings
**Use Case**: Understanding meaning and context
**Example**: Finding documents about "machine learning" when query is "AI algorithms"

```python
from langchain.vectorstores import Chroma

vectorstore = Chroma.from_documents(chunks, embeddings)
results = vectorstore.similarity_search("query", k=5)
```

### 2. Sparse Retrieval
**Method**: Keyword matching (BM25, TF-IDF)
**Use Case**: Exact term matching and keyword-specific queries
**Example**: Finding documents containing specific technical terms

```python
from langchain.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 5
results = bm25_retriever.get_relevant_documents("query")
```

### 3. Hybrid Search
**Method**: Combine dense + sparse retrieval
**Use Case**: Balance between semantic understanding and keyword matching

```python
from langchain.retrievers import BM25Retriever, EnsembleRetriever

# Sparse retriever (BM25)
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 5

# Dense retriever (embeddings)
embedding_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Combine with weights
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, embedding_retriever],
    weights=[0.3, 0.7]
)
```

### 4. Multi-Query Retrieval
**Method**: Generate multiple query variations
**Use Case**: Complex queries that can be interpreted in multiple ways

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

# Generate multiple query perspectives
retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=OpenAI()
)

# Single query → multiple variations → combined results
results = retriever.get_relevant_documents("What is the main topic?")
```

### 5. HyDE (Hypothetical Document Embeddings)
**Method**: Generate hypothetical documents for better retrieval
**Use Case**: When queries are very different from document style

```python
# Generate hypothetical document based on query
hypothetical_doc = llm.generate(f"Write a document about: {query}")
# Use hypothetical doc for retrieval
results = vectorstore.similarity_search(hypothetical_doc, k=5)
```

## Advanced Retrieval Patterns

### Contextual Compression
Compress retrieved documents to only include relevant parts

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)
```

### Parent Document Retriever
Store small chunks for retrieval, return larger chunks for context

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

store = InMemoryStore()
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)
```

## Retrieval Optimization Techniques

### 1. Metadata Filtering
Filter results based on document metadata

```python
results = vectorstore.similarity_search(
    "query",
    filter={"category": "technical", "date": {"$gte": "2023-01-01"}},
    k=5
)
```

### 2. Maximal Marginal Relevance (MMR)
Balance relevance with diversity

```python
results = vectorstore.max_marginal_relevance_search(
    "query",
    k=5,
    fetch_k=20,
    lambda_mult=0.5  # 0=max diversity, 1=max relevance
)
```

### 3. Reranking
Improve top results with cross-encoder

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
candidates = vectorstore.similarity_search("query", k=20)
pairs = [[query, doc.page_content] for doc in candidates]
scores = reranker.predict(pairs)
reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:5]
```

## Selection Guidelines

1. **Query Type**: Choose strategy based on typical query patterns
2. **Document Type**: Consider document structure and content
3. **Performance Requirements**: Balance quality vs speed
4. **Domain Knowledge**: Leverage domain-specific patterns
5. **User Expectations**: Match retrieval behavior to user expectations