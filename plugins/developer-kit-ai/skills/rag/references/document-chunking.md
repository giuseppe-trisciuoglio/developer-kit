# Document Chunking Strategies

## Overview
Document chunking is the process of breaking large documents into smaller, manageable pieces that can be effectively embedded and retrieved.

## Chunking Strategies

### 1. Recursive Character Text Splitter
**Method**: Split text based on character count, trying separators in order
**Use Case**: General purpose text splitting
**Advantages**: Preserves sentence and paragraph boundaries when possible

```python
from langchain.text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]  # Try these in order
)
chunks = splitter.split_documents(documents)
```

### 2. Token-Based Splitting
**Method**: Split based on token count rather than characters
**Use Case**: When working with token limits of language models
**Advantages**: Better control over context window usage

```python
from langchain.text_splitters import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=512,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)
```

### 3. Semantic Chunking
**Method**: Split based on semantic similarity
**Use Case**: When maintaining semantic coherence is important
**Advantages**: Chunks are more semantically meaningful

```python
from langchain.text_splitters import SemanticChunker

splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile"
)
chunks = splitter.split_documents(documents)
```

### 4. Markdown Header Splitter
**Method**: Split based on markdown headers
**Use Case**: Structured documents with clear hierarchical organization
**Advantages**: Maintains document structure and context

```python
from langchain.text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_documents(documents)
```

### 5. HTML Splitter
**Method**: Split based on HTML tags
**Use Case**: Web pages and HTML documents
**Advantages**: Preserves HTML structure and metadata

```python
from langchain.text_splitters import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
]

splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_documents(documents)
```

## Parameter Tuning

### Chunk Size
- **Small chunks (200-400 tokens)**: More precise retrieval, but may lose context
- **Medium chunks (500-1000 tokens)**: Good balance of precision and context
- **Large chunks (1000-2000 tokens)**: More context, but less precise retrieval

### Chunk Overlap
- **Purpose**: Preserve context at chunk boundaries
- **Typical range**: 10-20% of chunk size
- **Higher overlap**: Better context preservation, but more redundancy
- **Lower overlap**: Less redundancy, but may lose important context

### Separators
- **Hierarchical separators**: Start with larger boundaries (paragraphs), then smaller (sentences)
- **Custom separators**: Add domain-specific separators for better results
- **Language-specific**: Adjust for different languages and writing styles

## Best Practices

1. **Preserve Context**: Ensure chunks contain enough surrounding context
2. **Maintain Coherence**: Keep semantically related content together
3. **Respect Boundaries**: Avoid breaking sentences or important phrases
4. **Consider Query Types**: Adapt chunking strategy to typical user queries
5. **Test and Iterate**: Evaluate different chunking strategies for your specific use case

## Evaluation Metrics

1. **Retrieval Quality**: How well chunks answer user queries
2. **Context Preservation**: Whether important context is maintained
3. **Chunk Distribution**: Evenness of chunk sizes
4. **Boundary Quality**: How natural chunk boundaries are
5. **Retrieval Efficiency**: Impact on retrieval speed and accuracy

## Advanced Techniques

### Adaptive Chunking
Adjust chunk size based on document structure and content density.

### Hierarchical Chunking
Create multiple levels of chunks for different retrieval scenarios.

### Query-Aware Chunking
Optimize chunk boundaries based on typical query patterns.

### Domain-Specific Splitting
Use specialized splitters for specific document types (legal, medical, technical).