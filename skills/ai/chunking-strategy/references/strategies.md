# Detailed Chunking Strategies

This document provides comprehensive implementation details for all chunking strategies mentioned in the main skill.

## Level 1: Fixed-Size Chunking

### Implementation

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

class FixedSizeChunker:
    def __init__(self, chunk_size=512, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk(self, documents):
        return self.splitter.split_documents(documents)
```

### Parameter Recommendations

| Use Case | Chunk Size | Overlap | Rationale |
|----------|------------|---------|-----------|
| Factoid Queries | 256 | 25 | Small chunks for precise answers |
| General Q&A | 512 | 50 | Balanced approach for most cases |
| Analytical Queries | 1024 | 100 | Larger context for complex analysis |
| Code Documentation | 300 | 30 | Preserve code context while maintaining focus |

### Best Practices

- Start with 512 tokens and 10-20% overlap
- Adjust based on embedding model context window
- Use overlap for queries where context might span boundaries
- Monitor token count vs. character count based on model

## Level 2: Recursive Character Chunking

### Implementation

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RecursiveChunker:
    def __init__(self, chunk_size=512, separators=None):
        self.chunk_size = chunk_size
        self.separators = separators or ["\n\n", "\n", " ", ""]
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=0,
            length_function=len,
            separators=self.separators
        )

    def chunk(self, text):
        return self.splitter.create_documents([text])

# Document-specific configurations
def get_chunker_for_document_type(doc_type):
    configurations = {
        "markdown": ["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        "html": ["</div>", "</p>", "\n\n", "\n", " ", ""],
        "code": ["\n\n", "\n", " ", ""],
        "plain": ["\n\n", "\n", " ", ""]
    }
    return RecursiveChunker(separators=configurations.get(doc_type, ["\n\n", "\n", " ", ""]))
```

### Customization Guidelines

- **Markdown**: Use headings as primary separators
- **HTML**: Use block-level tags as separators
- **Code**: Preserve function and class boundaries
- **Academic papers**: Prioritize paragraph and section breaks

## Level 3: Structure-Aware Chunking

### Markdown Documents

```python
import markdown
from bs4 import BeautifulSoup

class MarkdownChunker:
    def __init__(self, max_chunk_size=512):
        self.max_chunk_size = max_chunk_size

    def chunk(self, markdown_text):
        html = markdown.markdown(markdown_text)
        soup = BeautifulSoup(html, 'html.parser')

        chunks = []
        current_chunk = ""
        current_heading = "Introduction"

        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'pre', 'table']):
            if element.name.startswith('h'):
                if current_chunk.strip():
                    chunks.append({
                        "content": current_chunk.strip(),
                        "heading": current_heading
                    })
                current_heading = element.get_text().strip()
                current_chunk = f"{element}\n"
            elif element.name in ['pre', 'table']:
                # Preserve code blocks and tables intact
                if len(current_chunk) + len(str(element)) > self.max_chunk_size:
                    if current_chunk.strip():
                        chunks.append({
                            "content": current_chunk.strip(),
                            "heading": current_heading
                        })
                    current_chunk = f"{element}\n"
                else:
                    current_chunk += f"{element}\n"
            else:
                current_chunk += str(element)

        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "heading": current_heading
            })

        return chunks
```

### Code Documents

```python
import ast
import re

class CodeChunker:
    def __init__(self, language='python'):
        self.language = language

    def chunk_python(self, code):
        tree = ast.parse(code)
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
                lines = code.split('\n')
                chunk_lines = lines[start_line:end_line]
                chunks.append('\n'.join(chunk_lines))

        return chunks

    def chunk_javascript(self, code):
        # Use regex for languages without AST parsers
        function_pattern = r'(function\s+\w+\s*\([^)]*\)\s*\{[^}]*\})'
        class_pattern = r'(class\s+\w+\s*\{[^}]*\})'

        patterns = [function_pattern, class_pattern]
        chunks = []

        for pattern in patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                chunks.append(match.group(1))

        return chunks

    def chunk(self, code):
        if self.language == 'python':
            return self.chunk_python(code)
        elif self.language == 'javascript':
            return self.chunk_javascript(code)
        else:
            # Fallback to line-based chunking
            return self.chunk_by_lines(code)

    def chunk_by_lines(self, code, max_lines=50):
        lines = code.split('\n')
        chunks = []

        for i in range(0, len(lines), max_lines):
            chunk = '\n'.join(lines[i:i+max_lines])
            chunks.append(chunk)

        return chunks
```

### Tabular Data

```python
import pandas as pd

class TableChunker:
    def __init__(self, max_rows=100, summary_rows=5):
        self.max_rows = max_rows
        self.summary_rows = summary_rows

    def chunk(self, table_data):
        if isinstance(table_data, str):
            df = pd.read_csv(StringIO(table_data))
        else:
            df = table_data

        chunks = []

        if len(df) <= self.max_rows:
            # Small table - keep intact
            chunks.append({
                "type": "full_table",
                "content": df.to_string(),
                "metadata": {
                    "rows": len(df),
                    "columns": len(df.columns)
                }
            })
        else:
            # Large table - create summary + chunks
            summary = df.head(self.summary_rows)
            chunks.append({
                "type": "table_summary",
                "content": f"Table Summary ({len(df)} rows, {len(df.columns)} columns):\n{summary.to_string()}",
                "metadata": {
                    "total_rows": len(df),
                    "summary_rows": self.summary_rows,
                    "columns": list(df.columns)
                }
            })

            # Chunk the remaining data
            for i in range(self.summary_rows, len(df), self.max_rows):
                chunk_df = df.iloc[i:i+self.max_rows]
                chunks.append({
                    "type": "table_chunk",
                    "content": f"Rows {i+1}-{min(i+self.max_rows, len(df))}:\n{chunk_df.to_string()}",
                    "metadata": {
                        "start_row": i + 1,
                        "end_row": min(i + self.max_rows, len(df)),
                        "columns": list(df.columns)
                    }
                })

        return chunks
```

## Level 4: Semantic Chunking

### Implementation

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticChunker:
    def __init__(self, model_name="all-MiniLM-L6-v2", similarity_threshold=0.8, buffer_size=3):
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.buffer_size = buffer_size

    def split_into_sentences(self, text):
        # Simple sentence splitting - can be enhanced with nltk/spacy
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk(self, text):
        sentences = self.split_into_sentences(text)

        if len(sentences) <= self.buffer_size:
            return [text]

        # Create embeddings
        embeddings = self.model.encode(sentences)

        chunks = []
        current_chunk_sentences = []

        for i in range(len(sentences)):
            current_chunk_sentences.append(sentences[i])

            # Check if we should create a boundary
            if i < len(sentences) - 1:
                similarity = cosine_similarity(
                    [embeddings[i]],
                    [embeddings[i + 1]]
                )[0][0]

                if similarity < self.similarity_threshold and len(current_chunk_sentences) >= 2:
                    chunks.append(' '.join(current_chunk_sentences))
                    current_chunk_sentences = []

        # Add remaining sentences
        if current_chunk_sentences:
            chunks.append(' '.join(current_chunk_sentences))

        return chunks
```

### Parameter Tuning

| Parameter | Range | Effect |
|-----------|-------|--------|
| similarity_threshold | 0.5-0.9 | Higher values create more chunks |
| buffer_size | 1-10 | Larger buffers provide more context |
| model_name | Various | Different models for different domains |

### Optimization Tips

- Use domain-specific models for specialized content
- Adjust threshold based on content complexity
- Cache embeddings for repeated processing
- Consider batch processing for large documents

## Level 5: Advanced Contextual Methods

### Late Chunking

```python
import torch
from transformers import AutoTokenizer, AutoModel

class LateChunker:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def chunk(self, text, chunk_size=512):
        # Tokenize entire document
        tokens = self.tokenizer(text, return_tensors="pt", truncation=False)

        # Get token-level embeddings
        with torch.no_grad():
            outputs = self.model(**tokens, output_hidden_states=True)
            token_embeddings = outputs.last_hidden_state[0]

        # Create chunk embeddings from token embeddings
        chunks = []
        for i in range(0, len(token_embeddings), chunk_size):
            chunk_tokens = token_embeddings[i:i+chunk_size]
            chunk_embedding = torch.mean(chunk_tokens, dim=0)
            chunks.append({
                "content": self.tokenizer.decode(tokens["input_ids"][0][i:i+chunk_size]),
                "embedding": chunk_embedding.numpy()
            })

        return chunks
```

### Contextual Retrieval

```python
import openai

class ContextualChunker:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def generate_context(self, chunk, full_document):
        prompt = f"""
        Given the following document and a chunk from it, provide a brief context
        that helps understand the chunk's meaning within the full document.

        Document:
        {full_document[:2000]}...

        Chunk:
        {chunk}

        Context (max 50 words):
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0
        )

        return response.choices[0].message.content.strip()

    def chunk_with_context(self, text, base_chunker):
        # First create base chunks
        base_chunks = base_chunker.chunk(text)

        # Then add context to each chunk
        contextualized_chunks = []
        for chunk in base_chunks:
            context = self.generate_context(chunk.page_content, text)
            contextualized_content = f"Context: {context}\n\nContent: {chunk.page_content}"

            contextualized_chunks.append({
                "content": contextualized_content,
                "original_content": chunk.page_content,
                "context": context
            })

        return contextualized_chunks
```

## Performance Considerations

### Computational Cost Analysis

| Strategy | Time Complexity | Space Complexity | Relative Cost |
|----------|-----------------|------------------|---------------|
| Fixed-Size | O(n) | O(n) | Low |
| Recursive | O(n) | O(n) | Low |
| Structure-Aware | O(n log n) | O(n) | Medium |
| Semantic | O(n²) | O(n²) | High |
| Late Chunking | O(n) | O(n) | Very High |
| Contextual | O(n²) | O(n²) | Very High |

### Optimization Strategies

1. **Parallel Processing**: Process chunks concurrently when possible
2. **Caching**: Store embeddings and intermediate results
3. **Batch Operations**: Group similar operations together
4. **Progressive Loading**: Process large documents in streaming fashion
5. **Model Selection**: Choose appropriate models for task complexity