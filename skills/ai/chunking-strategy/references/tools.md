# Recommended Libraries and Frameworks

This document provides a comprehensive guide to tools, libraries, and frameworks for implementing chunking strategies.

## Core Chunking Libraries

### LangChain

**Overview**: Comprehensive framework for building applications with large language models, includes robust text splitting utilities.

**Installation**:
```bash
pip install langchain langchain-text-splitters
```

**Key Features**:
- Multiple text splitting strategies
- Integration with various document loaders
- Support for different content types (code, markdown, etc.)
- Customizable separators and parameters

**Example Usage**:

```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter
)

# Basic recursive splitting
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

chunks = splitter.split_text(large_text)

# Markdown-specific splitting
markdown_splitter = MarkdownTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

# Code-specific splitting
code_splitter = PythonCodeTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)
```

**Pros**:
- Well-maintained and actively developed
- Extensive documentation and examples
- Integrates well with other LangChain components
- Supports multiple document types

**Cons**:
- Can be heavy dependency for simple use cases
- Some advanced features require LangChain ecosystem

### LlamaIndex

**Overview**: Data framework for LLM applications with advanced indexing and retrieval capabilities.

**Installation**:
```bash
pip install llama-index
```

**Key Features**:
- Advanced semantic chunking
- Hierarchical indexing
- Context-aware retrieval
- Integration with vector databases

**Example Usage**:

```python
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser
)
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding

# Basic sentence splitting
splitter = SentenceSplitter(
    chunk_size=1024,
    chunk_overlap=20
)

# Semantic chunking with embeddings
embed_model = OpenAIEmbedding()
semantic_splitter = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=embed_model
)

# Load and process documents
documents = SimpleDirectoryReader("./data").load_data()
nodes = semantic_splitter.get_nodes_from_documents(documents)
```

**Pros**:
- Excellent semantic chunking capabilities
- Built for production RAG systems
- Strong vector database integration
- Active community support

**Cons**:
- More complex setup for basic use cases
- Semantic chunking requires embedding model setup

### Unstructured

**Overview**: Open-source library for processing unstructured documents, especially strong with multi-modal content.

**Installation**:
```bash
pip install "unstructured[pdf,png,jpg]"
```

**Key Features**:
- Multi-modal document processing
- Support for PDFs, images, and various formats
- Structure preservation
- Table extraction and processing

**Example Usage**:

```python
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title

# Partition document by type
elements = partition(filename="document.pdf")

# Chunk by title/heading structure
chunks = chunk_by_title(
    elements,
    combine_text_under_n_chars=2000,
    max_characters=10000,
    new_after_n_chars=1500,
    multipage_sections=True
)

# Access chunked content
for chunk in chunks:
    print(f"Category: {chunk.category}")
    print(f"Content: {chunk.text[:200]}...")
```

**Pros**:
- Excellent for PDF and image processing
- Preserves document structure
- Handles tables and figures well
- Strong multi-modal capabilities

**Cons**:
- Can be slower for large documents
- Requires additional dependencies for some formats

## Text Processing Libraries

### NLTK (Natural Language Toolkit)

**Installation**:
```bash
pip install nltk
```

**Key Features**:
- Sentence tokenization
- Language detection
- Text preprocessing
- Linguistic analysis

**Example Usage**:

```python
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required data
nltk.download('punkt')
nltk.download('stopwords')

# Sentence and word tokenization
text = "This is a sample sentence. This is another sentence."
sentences = sent_tokenize(text)
words = word_tokenize(text)

# Stop words removal
stop_words = set(stopwords.words('english'))
filtered_words = [word for word in words if word.lower() not in stop_words]
```

### spaCy

**Installation**:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**Key Features**:
- Industrial-strength NLP
- Named entity recognition
- Dependency parsing
- Sentence boundary detection

**Example Usage**:

```python
import spacy

# Load language model
nlp = spacy.load("en_core_web_sm")

# Process text
doc = nlp("This is a sample sentence. This is another sentence.")

# Extract sentences
sentences = [sent.text for sent in doc.sents]

# Named entities
entities = [(ent.text, ent.label_) for ent in doc.ents]

# Dependency parsing for better chunking
for token in doc:
    print(f"{token.text}: {token.dep_} (head: {token.head.text})")
```

### Sentence Transformers

**Installation**:
```bash
pip install sentence-transformers
```

**Key Features**:
- Pre-trained sentence embeddings
- Semantic similarity calculation
- Multi-lingual support
- Custom model training

**Example Usage**:

```python
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
sentences = ["This is a sentence.", "This is another sentence."]
embeddings = model.encode(sentences)

# Calculate semantic similarity
similarity = util.cos_sim(embeddings[0], embeddings[1])

# Find semantic boundaries for chunking
def find_semantic_boundaries(text, model, threshold=0.8):
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    embeddings = model.encode(sentences)

    boundaries = [0]
    for i in range(1, len(sentences)):
        similarity = util.cos_sim(embeddings[i-1], embeddings[i])
        if similarity < threshold:
            boundaries.append(i)

    return boundaries
```

## Vector Databases and Search

### ChromaDB

**Installation**:
```bash
pip install chromadb
```

**Key Features**:
- In-memory and persistent storage
- Built-in embedding functions
- Similarity search
- Metadata filtering

**Example Usage**:

```python
import chromadb
from chromadb.utils import embedding_functions

# Initialize client
client = chromadb.Client()

# Create collection
collection = client.create_collection(
    name="document_chunks",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

# Add chunks
collection.add(
    documents=[chunk["content"] for chunk in chunks],
    metadatas=[chunk.get("metadata", {}) for chunk in chunks],
    ids=[chunk["id"] for chunk in chunks]
)

# Search
results = collection.query(
    query_texts=["What is chunking?"],
    n_results=5
)
```

### Pinecone

**Installation**:
```bash
pip install pinecone-client
```

**Key Features**:
- Managed vector database service
- High-performance similarity search
- Metadata filtering
- Scalable infrastructure

**Example Usage**:

```python
import pinecone
from sentence_transformers import SentenceTransformer

# Initialize
pinecone.init(api_key="your-api-key", environment="your-environment")
index_name = "document-chunks"

# Create index if it doesn't exist
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=384,  # Match embedding model
        metric="cosine"
    )

index = pinecone.Index(index_name)

# Generate embeddings and upsert
model = SentenceTransformer('all-MiniLM-L6-v2')
for chunk in chunks:
    embedding = model.encode(chunk["content"])
    index.upsert(
        vectors=[{
            "id": chunk["id"],
            "values": embedding.tolist(),
            "metadata": chunk.get("metadata", {})
        }]
    )

# Search
query_embedding = model.encode("search query")
results = index.query(
    vector=query_embedding.tolist(),
    top_k=5,
    include_metadata=True
)
```

### Weaviate

**Installation**:
```bash
pip install weaviate-client
```

**Key Features**:
- GraphQL API
- Hybrid search (dense + sparse)
- Real-time updates
- Schema validation

**Example Usage**:

```python
import weaviate

# Connect to Weaviate
client = weaviate.Client("http://localhost:8080")

# Define schema
client.schema.create_class({
    "class": "DocumentChunk",
    "description": "A chunk of document content",
    "properties": [
        {
            "name": "content",
            "dataType": ["text"]
        },
        {
            "name": "source",
            "dataType": ["string"]
        }
    ]
})

# Add data
for chunk in chunks:
    client.data_object.create(
        data_object={
            "content": chunk["content"],
            "source": chunk.get("source", "unknown")
        },
        class_name="DocumentChunk"
    )

# Search
results = client.query.get(
    "DocumentChunk",
    ["content", "source"]
).with_near_text({
    "concepts": ["search query"]
}).with_limit(5).do()
```

## Evaluation and Testing

### RAGAS

**Installation**:
```bash
pip install ragas
```

**Key Features**:
- RAG evaluation metrics
- Answer quality assessment
- Context relevance measurement
- Faithfulness evaluation

**Example Usage**:

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_relevancy,
    context_recall
)
from datasets import Dataset

# Prepare evaluation data
dataset = Dataset.from_dict({
    "question": ["What is chunking?"],
    "answer": ["Chunking is the process of breaking large documents into smaller segments"],
    "contexts": [["Chunking involves dividing text into manageable pieces for better processing"]],
    "ground_truth": ["Chunking is a document processing technique"]
})

# Evaluate
result = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_relevancy,
        context_recall
    ]
)

print(result)
```

### TruEra (TruLens)

**Installation**:
```bash
pip install trulens trulens-apps
```

**Key Features**:
- LLM application evaluation
- Feedback functions
- Hallucination detection
- Performance monitoring

**Example Usage**:

```python
from trulens.core import TruSession
from trulens.apps.custom import instrument
from trulens.feedback import GroundTruthAgreement

# Initialize session
session = TruSession()

# Define feedback functions
f_groundedness = GroundTruthAgreement(ground_truth)

# Evaluate chunks
@instrument
def chunk_and_query(text, query):
    chunks = chunk_function(text)
    relevant_chunks = search_function(chunks, query)
    answer = generate_function(relevant_chunks, query)
    return answer

# Record evaluation
with session:
    chunk_and_query("large document text", "what is the main topic?")
```

## Document Processing

### PyPDF2

**Installation**:
```bash
pip install PyPDF2
```

**Key Features**:
- PDF text extraction
- Page manipulation
- Metadata extraction
- Form field processing

**Example Usage**:

```python
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Extract text by page for better chunking
def extract_pages(pdf_path):
    pages = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(reader.pages):
            pages.append({
                "page_number": i + 1,
                "content": page.extract_text()
            })
    return pages
```

### python-docx

**Installation**:
```bash
pip install python-docx
```

**Key Features**:
- Microsoft Word document processing
- Paragraph and table extraction
- Style preservation
- Metadata access

**Example Usage**:

```python
from docx import Document

def extract_from_docx(docx_path):
    doc = Document(docx_path)
    content = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            content.append({
                "type": "paragraph",
                "text": paragraph.text,
                "style": paragraph.style.name
            })

    for table in doc.tables:
        table_text = []
        for row in table.rows:
            row_text = [cell.text for cell in row.cells]
            table_text.append(" | ".join(row_text))

        content.append({
            "type": "table",
            "text": "\n".join(table_text)
        })

    return content
```

## Specialized Libraries

### tiktoken (OpenAI)

**Installation**:
```bash
pip install tiktoken
```

**Key Features**:
- Accurate token counting for OpenAI models
- Fast encoding/decoding
- Multiple model support
- Language model specific tokenization

**Example Usage**:

```python
import tiktoken

# Get encoding for specific model
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Encode text
tokens = encoding.encode("This is a sample text")
print(f"Token count: {len(tokens)}")

# Decode tokens
text = encoding.decode(tokens)

# Count tokens without full encoding
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Use in chunking
def chunk_by_tokens(text, max_tokens=1000):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks
```

### PDFMiner

**Installation**:
```bash
pip install pdfminer.six
```

**Key Features**:
- Detailed PDF analysis
- Layout preservation
- Font and style information
- High-precision text extraction

**Example Usage**:

```python
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

def extract_structured_text(pdf_path):
    structured_content = []

    for page_layout in extract_pages(pdf_path):
        page_content = []

        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text()
                font_info = {
                    "font_size": element.height,
                    "is_bold": "Bold" in element.fontname,
                    "x0": element.x0,
                    "y0": element.y0
                }
                page_content.append({
                    "text": text.strip(),
                    "font_info": font_info
                })

        structured_content.append({
            "page_number": page_layout.pageid,
            "content": page_content
        })

    return structured_content
```

## Performance and Optimization

### Dask

**Installation**:
```bash
pip install dask[complete]
```

**Key Features**:
- Parallel processing
- Out-of-core computation
- Distributed computing
- Integration with pandas

**Example Usage**:

```python
import dask.bag as db
from dask.distributed import Client

# Setup distributed client
client = Client(n_workers=4)

# Parallel chunking of multiple documents
def chunk_document(document):
    # Your chunking logic here
    return chunk_function(document)

# Process documents in parallel
documents = ["doc1", "doc2", "doc3", ...]  # List of document contents
document_bag = db.from_sequence(documents)

# Apply chunking function in parallel
chunked_documents = document_bag.map(chunk_document)

# Compute results
results = chunked_documents.compute()
```

### Ray

**Installation**:
```bash
pip install ray
```

**Key Features**:
- Distributed computing
- Actor model
- Autoscaling
- ML pipeline integration

**Example Usage**:

```python
import ray

# Initialize Ray
ray.init()

@ray.remote
class ChunkingWorker:
    def __init__(self, strategy):
        self.strategy = strategy

    def chunk_documents(self, documents):
        results = []
        for doc in documents:
            chunks = self.strategy.chunk(doc)
            results.append(chunks)
        return results

# Create workers
workers = [ChunkingWorker.remote(strategy) for _ in range(4)]

# Distribute work
documents_batch = [documents[i::4] for i in range(4)]
futures = [worker.chunk_documents.remote(batch)
           for worker, batch in zip(workers, documents_batch)]

# Get results
results = ray.get(futures)
```

## Development and Testing

### pytest

**Installation**:
```bash
pip install pytest pytest-asyncio
```

**Example Tests**:

```python
import pytest
from your_chunking_module import FixedSizeChunker, SemanticChunker

class TestFixedSizeChunker:
    def test_chunk_size_respect(self):
        chunker = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
        text = "word " * 50  # 50 words

        chunks = chunker.chunk(text)

        for chunk in chunks:
            assert len(chunk.split()) <= 100  # Account for word boundaries

    def test_overlap_consistency(self):
        chunker = FixedSizeChunker(chunk_size=50, chunk_overlap=10)
        text = "word " * 30

        chunks = chunker.chunk(text)

        # Check overlap between consecutive chunks
        for i in range(1, len(chunks)):
            chunk1_words = set(chunks[i-1].split()[-10:])
            chunk2_words = set(chunks[i].split()[:10])
            overlap = len(chunk1_words & chunk2_words)
            assert overlap >= 5  # Allow some tolerance

@pytest.mark.asyncio
async def test_semantic_chunker():
    chunker = SemanticChunker()
    text = "First topic sentence. Another sentence about first topic. " \
           "Now switching to second topic. More about second topic."

    chunks = await chunker.chunk_async(text)

    # Should detect topic change and create boundary
    assert len(chunks) >= 2
    assert "first topic" in chunks[0].lower()
    assert "second topic" in chunks[1].lower()
```

### Memory Profiler

**Installation**:
```bash
pip install memory-profiler
```

**Example Usage**:

```python
from memory_profiler import profile

@profile
def chunk_large_document():
    chunker = FixedSizeChunker(chunk_size=1000)
    large_text = "word " * 100000  # Large document

    chunks = chunker.chunk(large_text)
    return chunks

# Run with: python -m memory_profiler your_script.py
```

This comprehensive toolset provides everything needed to implement, test, and optimize chunking strategies for various use cases, from simple text processing to production-grade RAG systems.