# Embedding Models Guide

## Overview
Embedding models convert text into numerical vectors that capture semantic meaning for similarity search in RAG systems.

## Popular Embedding Models

### 1. text-embedding-ada-002 (OpenAI)
- **Dimensions**: 1536
- **Type**: General purpose
- **Use Case**: Most applications requiring high quality embeddings
- **Performance**: Excellent balance of quality and speed

### 2. all-MiniLM-L6-v2 (Sentence Transformers)
- **Dimensions**: 384
- **Type**: Lightweight
- **Use Case**: Applications requiring fast inference
- **Performance**: Good quality, very fast

### 3. e5-large-v2
- **Dimensions**: 1024
- **Type**: High quality
- **Use Case**: Applications needing superior performance
- **Performance**: Excellent quality, multilingual support

### 4. Instructor
- **Dimensions**: Variable (768)
- **Type**: Task-specific
- **Use Case**: Domain-specific applications
- **Performance**: Can be fine-tuned for specific tasks

### 5. bge-large-en-v1.5
- **Dimensions**: 1024
- **Type**: State-of-the-art
- **Use Case**: Applications requiring best possible quality
- **Performance**: SOTA performance on benchmarks

## Selection Criteria

1. **Quality vs Speed**: Balance between embedding quality and inference speed
2. **Dimension Size**: Impact on storage and retrieval performance
3. **Domain**: Specific language or domain requirements
4. **Cost**: API costs vs local deployment
5. **Batch Size**: Throughput requirements
6. **Language**: Multilingual support needs

## Usage Examples

### OpenAI Embeddings
```python
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vector = embeddings.embed_query("Your text here")
```

### Sentence Transformers
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
vector = model.encode("Your text here")
```

### Hugging Face Models
```python
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

## Optimization Tips

1. **Batch Processing**: Process multiple texts together for efficiency
2. **Model Quantization**: Reduce model size for faster inference
3. **Caching**: Cache embeddings for frequently used texts
4. **GPU Acceleration**: Use GPU for faster processing when available
5. **Model Selection**: Choose appropriate model size for your use case

## Evaluation Metrics

1. **Semantic Similarity**: How well embeddings capture meaning
2. **Retrieval Performance**: Quality of retrieved documents
3. **Speed**: Inference time per document
4. **Memory Usage**: RAM requirements for the model
5. **Cost**: API costs or infrastructure requirements