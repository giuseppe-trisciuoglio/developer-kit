# Advanced Chunking Strategies

This document provides detailed implementations of 11 advanced chunking strategies for comprehensive RAG systems.

## Strategy Overview

| Strategy | Complexity | Use Case | Key Benefit |
|----------|------------|----------|-------------|
| Fixed-Length | Low | Simple documents, baseline | Easy implementation |
| Sentence-Based | Medium | General text processing | Natural language boundaries |
| Paragraph-Based | Medium | Structured documents | Context preservation |
| Sliding Window | Medium | Context-critical queries | Overlap for continuity |
| Semantic | High | Complex documents | Thematic coherence |
| Recursive | Medium | Mixed content types | Hierarchical structure |
| Context-Enriched | High | Technical documents | Enhanced context |
| Modality-Specific | High | Multi-modal content | Specialized handling |
| Agentic | Very High | Dynamic requirements | Adaptive chunking |
| Subdocument | Medium | Large documents | Logical grouping |
| Hybrid | Very High | Complex systems | Best-of-all approaches |

## 1. Fixed-Length Chunking

### Overview
Divide documents into chunks of fixed character/token count regardless of content structure.

### Implementation
```python
from langchain.text_splitter import CharacterTextSplitter
import tiktoken

class FixedLengthChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200, encoding_name="cl100k_base"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def chunk_by_characters(self, text):
        """Chunk by character count"""
        splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separator="\n\n"
        )
        return splitter.split_text(text)

    def chunk_by_tokens(self, text):
        """Chunk by token count using tiktoken"""
        tokens = self.encoding.encode(text)
        chunks = []

        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Calculate next start position with overlap
            start = max(0, end - self.chunk_overlap)

            # Prevent infinite loop
            if end >= len(tokens):
                break

        return chunks

    def chunk_optimized(self, text, strategy="balanced"):
        """Optimized chunking based on strategy"""
        strategies = {
            "conservative": {"chunk_size": 500, "overlap": 100},
            "balanced": {"chunk_size": 1000, "overlap": 200},
            "aggressive": {"chunk_size": 2000, "overlap": 400}
        }

        config = strategies.get(strategy, strategies["balanced"])
        self.chunk_size = config["chunk_size"]
        self.chunk_overlap = config["overlap"]

        return self.chunk_by_tokens(text)
```

### Best Practices
- Start with 1000 tokens for general use
- Use 10-20% overlap for context preservation
- Adjust based on embedding model context window
- Consider document type for optimal sizing

## 2. Sentence-Based Chunking

### Overview
Split documents at sentence boundaries while maintaining target chunk sizes.

### Implementation
```python
import nltk
import spacy
from typing import List

class SentenceChunker:
    def __init__(self, max_sentences=10, overlap_sentences=2, library="spacy"):
        self.max_sentences = max_sentences
        self.overlap_sentences = overlap_sentences
        self.library = library

        if library == "spacy":
            self.nlp = spacy.load("en_core_web_sm")
        elif library == "nltk":
            nltk.download('punkt')

    def extract_sentences_spacy(self, text):
        """Extract sentences using spaCy"""
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]

    def extract_sentences_nltk(self, text):
        """Extract sentences using NLTK"""
        sentences = nltk.sent_tokenize(text)
        return [sent.strip() for sent in sentences]

    def chunk_sentences(self, text):
        """Chunk text by sentences"""
        if self.library == "spacy":
            sentences = self.extract_sentences_spacy(text)
        else:
            sentences = self.extract_sentences_nltk(text)

        chunks = []
        for i in range(0, len(sentences), self.max_sentences - self.overlap_sentences):
            end_idx = min(i + self.max_sentences, len(sentences))
            chunk_sentences = sentences[i:end_idx]

            if chunk_sentences:
                chunk = " ".join(chunk_sentences)
                chunks.append(chunk)

        return chunks

    def chunk_with_metadata(self, text):
        """Chunk with sentence count metadata"""
        sentences = self.extract_sentences_spacy(text)
        chunks = []

        for i in range(0, len(sentences), self.max_sentences - self.overlap_sentences):
            end_idx = min(i + self.max_sentences, len(sentences))
            chunk_sentences = sentences[i:end_idx]

            if chunk_sentences:
                chunk = {
                    "text": " ".join(chunk_sentences),
                    "sentence_count": len(chunk_sentences),
                    "start_sentence": i,
                    "end_sentence": end_idx - 1,
                    "overlap": self.overlap_sentences > 0 and i > 0
                }
                chunks.append(chunk)

        return chunks
```

## 3. Paragraph-Based Chunking

### Overview
Split documents at paragraph boundaries while maintaining semantic coherence.

### Implementation
```python
import re
from typing import List, Dict

class ParagraphChunker:
    def __init__(self, max_paragraphs=5, min_length=100, merge_short=True):
        self.max_paragraphs = max_paragraphs
        self.min_length = min_length
        self.merge_short = merge_short

    def extract_paragraphs(self, text):
        """Extract paragraphs from text"""
        # Split on various paragraph separators
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)

        # Clean and filter paragraphs
        cleaned_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > self.min_length // 4:  # Allow short paragraphs
                cleaned_paragraphs.append(para)

        return cleaned_paragraphs

    def chunk_paragraphs(self, text):
        """Chunk text by paragraphs"""
        paragraphs = self.extract_paragraphs(text)
        chunks = []

        current_chunk = []
        current_length = 0

        for i, paragraph in enumerate(paragraphs):
            paragraph_length = len(paragraph)

            # If adding this paragraph exceeds reasonable limits, start new chunk
            if (current_chunk and
                (len(current_chunk) >= self.max_paragraphs or
                 current_length + paragraph_length > 3000)):

                # Save current chunk
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))

                # Start new chunk with overlap
                overlap_count = min(2, len(current_chunk))
                current_chunk = current_chunk[-overlap_count:] if overlap_count > 0 else []
                current_length = sum(len(p) for p in current_chunk)

            current_chunk.append(paragraph)
            current_length += paragraph_length

        # Add final chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def chunk_with_structure(self, text):
        """Chunk while preserving structure information"""
        paragraphs = self.extract_paragraphs(text)
        chunks = []

        current_chunk = []
        current_start = 0

        for i, paragraph in enumerate(paragraphs):
            current_chunk.append(paragraph)

            # Check if we should end the current chunk
            should_end = (
                len(current_chunk) >= self.max_paragraphs or
                (i < len(paragraphs) - 1 and
                 self._is_boundary_paragraph(paragraph, paragraphs[i + 1]))
            )

            if should_end or i == len(paragraphs) - 1:
                chunk_data = {
                    "text": "\n\n".join(current_chunk),
                    "paragraph_count": len(current_chunk),
                    "start_paragraph": current_start,
                    "end_paragraph": i,
                    "structure_type": self._detect_structure_type(current_chunk)
                }
                chunks.append(chunk_data)

                # Prepare for next chunk
                current_start = i + 1
                overlap_count = min(1, len(current_chunk))
                current_chunk = current_chunk[-overlap_count:] if overlap_count > 0 else []

        return chunks

    def _is_boundary_paragraph(self, current, next_para):
        """Check if there's a natural boundary between paragraphs"""
        boundary_indicators = [
            lambda c, n: c.strip().endswith(':'),  # Ends with colon
            lambda c, n: n.strip().startswith(('•', '-', '*')),  # List starts
            lambda c, n: bool(re.match(r'^\d+\.', n.strip())),  # Numbered list
            lambda c, n: len(n.strip()) < 50,  # Very short paragraph
        ]

        return any(indicator(current, next_para) for indicator in boundary_indicators)

    def _detect_structure_type(self, paragraphs):
        """Detect the type of structure in the chunk"""
        text = " ".join(paragraphs)

        if re.search(r'^#+\s', text, re.MULTILINE):
            return "markdown_headings"
        elif re.search(r'^\s*[-*+]\s', text, re.MULTILINE):
            return "bullet_points"
        elif re.search(r'^\s*\d+\.\s', text, re.MULTILINE):
            return "numbered_list"
        elif any(char.isdigit() for char in text) and ('%' in text or '$' in text):
            return "data_heavy"
        else:
            return "prose"
```

## 4. Sliding Window Chunking

### Overview
Create overlapping chunks using a sliding window approach for maximum context preservation.

### Implementation
```python
from typing import List, Iterator
import numpy as np

class SlidingWindowChunker:
    def __init__(self, window_size=1000, step_size=500, unit="tokens"):
        self.window_size = window_size
        self.step_size = step_size
        self.unit = unit

    def sliding_chunk_tokens(self, text, encoding_name="cl100k_base"):
        """Create sliding window chunks by tokens"""
        import tiktoken
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)

        chunks = []
        for start in range(0, len(tokens), self.step_size):
            end = min(start + self.window_size, len(tokens))
            window_tokens = tokens[start:end]
            chunk_text = encoding.decode(window_tokens)

            chunks.append({
                "text": chunk_text,
                "start_token": start,
                "end_token": end - 1,
                "token_count": len(window_tokens),
                "overlap": self.window_size - self.step_size
            })

            if end >= len(tokens):
                break

        return chunks

    def sliding_chunk_characters(self, text):
        """Create sliding window chunks by characters"""
        chunks = []
        for start in range(0, len(text), self.step_size):
            end = min(start + self.window_size, len(text))
            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "start_char": start,
                "end_char": end - 1,
                "char_count": len(chunk_text),
                "overlap": self.window_size - self.step_size
            })

            if end >= len(text):
                break

        return chunks

    def adaptive_sliding_window(self, text, min_overlap=0.1, max_overlap=0.5):
        """Adaptive sliding window based on content density"""
        if self.unit == "tokens":
            base_chunks = self.sliding_chunk_tokens(text)
        else:
            base_chunks = self.sliding_chunk_characters(text)

        # Analyze content density
        adaptive_chunks = []
        for i, chunk in enumerate(base_chunks):
            text_content = chunk["text"]
            density = self._calculate_content_density(text_content)

            # Adjust overlap based on density
            if density > 0.8:  # High density - more overlap
                adjusted_overlap = int(self.window_size * max_overlap)
            elif density < 0.3:  # Low density - less overlap
                adjusted_overlap = int(self.window_size * min_overlap)
            else:
                adjusted_overlap = self.window_size - self.step_size

            chunk["content_density"] = density
            chunk["adjusted_overlap"] = adjusted_overlap
            adaptive_chunks.append(chunk)

        return adaptive_chunks

    def _calculate_content_density(self, text):
        """Calculate content density (information per unit)"""
        # Simple heuristic: unique words / total words
        words = text.split()
        if not words:
            return 0.0

        unique_words = set(word.lower().strip('.,!?;:()[]{}"\'') for word in words)
        density = len(unique_words) / len(words)

        # Adjust for punctuation and special characters
        special_chars = sum(1 for char in text if not char.isalnum() and not char.isspace())
        density += special_chars / len(text) * 0.1

        return min(density, 1.0)

    def semantic_sliding_window(self, text, embedding_model, similarity_threshold=0.7):
        """Sliding window with semantic boundary detection"""
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        # Split into sentences
        sentences = self._split_into_sentences(text)
        if len(sentences) < 2:
            return [{"text": text, "method": "single_sentence"}]

        # Generate sentence embeddings
        sentence_embeddings = embedding_model.encode(sentences)

        chunks = []
        current_window_sentences = []
        current_window_start = 0

        for i, sentence in enumerate(sentences):
            current_window_sentences.append(sentence)

            # Check if we should create a boundary
            should_create_boundary = (
                len(current_window_sentences) >= 10 or  # Max sentences per window
                (i < len(sentences) - 1 and  # Not the last sentence
                 self._should_create_semantic_boundary(
                     sentence_embeddings, i, similarity_threshold
                 ))
            )

            if should_create_boundary:
                chunk_text = " ".join(current_window_sentences)
                chunks.append({
                    "text": chunk_text,
                    "sentence_count": len(current_window_sentences),
                    "start_sentence": current_window_start,
                    "end_sentence": i,
                    "method": "semantic_sliding_window"
                })

                # Start new window with overlap
                overlap_size = min(2, len(current_window_sentences) // 2)
                current_window_sentences = current_window_sentences[-overlap_size:]
                current_window_start = i + 1 - overlap_size

        # Add final chunk
        if current_window_sentences:
            chunk_text = " ".join(current_window_sentences)
            chunks.append({
                "text": chunk_text,
                "sentence_count": len(current_window_sentences),
                "start_sentence": current_window_start,
                "end_sentence": len(sentences) - 1,
                "method": "semantic_sliding_window"
            })

        return chunks

    def _split_into_sentences(self, text):
        """Split text into sentences"""
        import re
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _should_create_semantic_boundary(self, embeddings, current_idx, threshold):
        """Determine if semantic boundary should be created"""
        if current_idx >= len(embeddings) - 1:
            return True

        # Calculate similarity with next sentence
        current_embedding = embeddings[current_idx].reshape(1, -1)
        next_embedding = embeddings[current_idx + 1].reshape(1, -1)

        similarity = cosine_similarity(current_embedding, next_embedding)[0][0]

        return similarity < threshold
```

## 5. Semantic Chunking

### Overview
Use semantic similarity to identify natural boundaries in text.

### Implementation
```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict

class SemanticChunker:
    def __init__(self, model_name="all-MiniLM-L6-v2",
                 similarity_threshold=0.8,
                 min_chunk_size=2,
                 max_chunk_size=10):
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def semantic_chunk_sentences(self, text):
        """Chunk text based on semantic similarity between sentences"""
        # Split into sentences
        sentences = self._split_into_sentences(text)
        if len(sentences) <= self.min_chunk_size:
            return [{"text": text, "sentence_count": len(sentences), "method": "single_chunk"}]

        # Generate embeddings for all sentences
        sentence_embeddings = self.model.encode(sentences)

        # Find semantic boundaries
        boundaries = self._find_semantic_boundaries(sentence_embeddings)

        # Create chunks based on boundaries
        chunks = []
        start_idx = 0

        for boundary_idx in boundaries:
            if boundary_idx > start_idx:
                chunk_sentences = sentences[start_idx:boundary_idx + 1]
                chunk_text = " ".join(chunk_sentences)

                chunks.append({
                    "text": chunk_text,
                    "sentence_count": len(chunk_sentences),
                    "start_sentence": start_idx,
                    "end_sentence": boundary_idx,
                    "method": "semantic_boundary"
                })

                start_idx = boundary_idx + 1

        # Add remaining sentences
        if start_idx < len(sentences):
            chunk_sentences = sentences[start_idx:]
            chunk_text = " ".join(chunk_sentences)

            chunks.append({
                "text": chunk_text,
                "sentence_count": len(chunk_sentences),
                "start_sentence": start_idx,
                "end_sentence": len(sentences) - 1,
                "method": "semantic_boundary"
            })

        return self._merge_small_chunks(chunks)

    def _find_semantic_boundaries(self, embeddings):
        """Find semantic boundaries based on similarity thresholds"""
        boundaries = []

        for i in range(len(embeddings) - 1):
            # Calculate similarity between consecutive sentences
            similarity = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0][0]

            # If similarity is below threshold, create boundary
            if similarity < self.similarity_threshold:
                boundaries.append(i)

        return boundaries

    def _split_into_sentences(self, text):
        """Split text into sentences"""
        import re
        # Enhanced sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]

    def _merge_small_chunks(self, chunks):
        """Merge chunks that are too small"""
        if not chunks:
            return chunks

        merged_chunks = []
        current_chunk = chunks[0].copy()

        for next_chunk in chunks[1:]:
            if (current_chunk["sentence_count"] < self.min_chunk_size and
                current_chunk["sentence_count"] + next_chunk["sentence_count"] <= self.max_chunk_size):

                # Merge chunks
                current_chunk["text"] += " " + next_chunk["text"]
                current_chunk["sentence_count"] += next_chunk["sentence_count"]
                current_chunk["end_sentence"] = next_chunk["end_sentence"]
            else:
                merged_chunks.append(current_chunk)
                current_chunk = next_chunk.copy()

        merged_chunks.append(current_chunk)
        return merged_chunks

    def adaptive_semantic_chunking(self, text, content_analyzer=None):
        """Semantic chunking with adaptive threshold"""
        sentences = self._split_into_sentences(text)
        if len(sentences) <= 2:
            return [{"text": text, "method": "too_short"}]

        # Generate embeddings
        embeddings = self.model.encode(sentences)

        # Analyze content complexity
        if content_analyzer:
            complexity = content_analyzer.analyze_complexity(text)
            # Adjust threshold based on complexity
            adaptive_threshold = self.similarity_threshold * (1.0 + complexity * 0.2)
        else:
            adaptive_threshold = self.similarity_threshold

        # Find boundaries with adaptive threshold
        boundaries = self._find_adaptive_boundaries(embeddings, adaptive_threshold)

        # Create chunks
        chunks = []
        start_idx = 0

        for boundary_idx in boundaries:
            if boundary_idx > start_idx:
                chunk_sentences = sentences[start_idx:boundary_idx + 1]
                chunk_text = " ".join(chunk_sentences)

                chunks.append({
                    "text": chunk_text,
                    "sentence_count": len(chunk_sentences),
                    "start_sentence": start_idx,
                    "end_sentence": boundary_idx,
                    "method": "adaptive_semantic",
                    "threshold_used": adaptive_threshold
                })

                start_idx = boundary_idx + 1

        # Add remaining sentences
        if start_idx < len(sentences):
            chunk_sentences = sentences[start_idx:]
            chunk_text = " ".join(chunk_sentences)

            chunks.append({
                "text": chunk_text,
                "sentence_count": len(chunk_sentences),
                "start_sentence": start_idx,
                "end_sentence": len(sentences) - 1,
                "method": "adaptive_semantic",
                "threshold_used": adaptive_threshold
            })

        return chunks

    def _find_adaptive_boundaries(self, embeddings, threshold):
        """Find boundaries with adaptive threshold based on local context"""
        boundaries = []

        for i in range(len(embeddings) - 1):
            # Calculate local similarity
            local_similarities = []

            # Look at local window of similarities
            window_size = min(3, i)
            for j in range(max(0, i - window_size), i + 1):
                if j < len(embeddings) - 1:
                    similarity = cosine_similarity(
                        embeddings[j].reshape(1, -1),
                        embeddings[j + 1].reshape(1, -1)
                    )[0][0]
                    local_similarities.append(similarity)

            # Use local average for comparison
            if local_similarities:
                local_avg = np.mean(local_similarities)
                current_similarity = local_similarities[-1]

                # Create boundary if current similarity is significantly lower than local average
                if current_similarity < local_avg * threshold:
                    boundaries.append(i)
            else:
                # Fallback to global threshold
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[i + 1].reshape(1, -1)
                )[0][0]

                if similarity < threshold:
                    boundaries.append(i)

        return boundaries

    def hierarchical_semantic_chunking(self, text, max_levels=3):
        """Multi-level semantic chunking"""
        sentences = self._split_into_sentences(text)

        if len(sentences) <= 4:
            return [{
                "text": text,
                "level": 0,
                "sentence_count": len(sentences),
                "method": "hierarchical_semantic"
            }]

        # Level 0: Original text
        chunks = [{
            "text": text,
            "level": 0,
            "sentence_count": len(sentences),
            "method": "hierarchical_semantic"
        }]

        # Generate embeddings once
        embeddings = self.model.encode(sentences)

        # Create hierarchical chunks
        current_level_sentences = sentences
        current_level_embeddings = embeddings

        for level in range(1, max_levels + 1):
            if len(current_level_sentences) <= 2:
                break

            # Find boundaries at this level
            boundaries = self._find_semantic_boundaries(current_level_embeddings)

            # Create chunks at this level
            level_chunks = []
            start_idx = 0

            for boundary_idx in boundaries:
                if boundary_idx > start_idx:
                    chunk_sentences = current_level_sentences[start_idx:boundary_idx + 1]
                    chunk_text = " ".join(chunk_sentences)

                    level_chunks.append({
                        "text": chunk_text,
                        "level": level,
                        "sentence_count": len(chunk_sentences),
                        "start_sentence": start_idx,
                        "end_sentence": boundary_idx,
                        "method": "hierarchical_semantic"
                    })

                    start_idx = boundary_idx + 1

            # Add remaining sentences
            if start_idx < len(current_level_sentences):
                chunk_sentences = current_level_sentences[start_idx:]
                chunk_text = " ".join(chunk_sentences)

                level_chunks.append({
                    "text": chunk_text,
                    "level": level,
                    "sentence_count": len(chunk_sentences),
                    "start_sentence": start_idx,
                    "end_sentence": len(current_level_sentences) - 1,
                    "method": "hierarchical_semantic"
                })

            chunks.extend(level_chunks)

            # Prepare for next level
            if len(level_chunks) > 1:
                current_level_sentences = [chunk["text"] for chunk in level_chunks]
                current_level_embeddings = self.model.encode(current_level_sentences)
            else:
                break

        return chunks
```

## 6. Recursive Chunking

### Overview
Hierarchical splitting using ordered separators to preserve document structure.

### Implementation
```python
from typing import List, Dict, Optional
import re

class RecursiveChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200,
                 separators=None, length_function=len):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function

        # Default separators in order of preference
        self.separators = separators or [
            "\n\n\n",  # Triple newlines (section breaks)
            "\n\n",    # Double newlines (paragraph breaks)
            "\n",      # Single newlines (line breaks)
            " ",       # Spaces (word breaks)
            ""         # Character-level (last resort)
        ]

    def recursive_split(self, text, separators=None):
        """Recursively split text using hierarchical separators"""
        separators = separators or self.separators
        final_chunks = []

        # Try each separator in order
        for separator in separators:
            if separator == "":
                # Last resort: split by characters
                return self._split_by_characters(text)

            # Split by current separator
            splits = text.split(separator)

            # Filter out empty splits
            splits = [split for split in splits if split.strip()]

            if len(splits) > 1:
                # Found a good separator
                for split in splits:
                    if self.length_function(split) <= self.chunk_size:
                        final_chunks.append(split)
                    else:
                        # Recursively split this piece
                        sub_chunks = self.recursive_split(split, separators[separators.index(separator) + 1:])
                        final_chunks.extend(sub_chunks)

                return self._merge_chunks(final_chunks)

        # No separator worked, split by characters
        return self._split_by_characters(text)

    def _split_by_characters(self, text):
        """Split text by characters as last resort"""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)

            # Calculate next start with overlap
            start = max(0, end - self.chunk_overlap)

            if end >= len(text):
                break

        return chunks

    def _merge_chunks(self, chunks):
        """Merge chunks that are too small"""
        if not chunks:
            return chunks

        merged_chunks = []
        current_chunk = chunks[0]

        for next_chunk in chunks[1:]:
            combined_length = self.length_function(current_chunk + next_chunk)

            if combined_length <= self.chunk_size:
                # Merge chunks
                current_chunk += "\n\n" + next_chunk
            else:
                # Add current chunk and start new one
                merged_chunks.append(current_chunk)
                current_chunk = next_chunk

        merged_chunks.append(current_chunk)
        return merged_chunks

    def recursive_split_with_metadata(self, text, separators=None):
        """Recursive split with detailed metadata"""
        separators = separators or self.separators
        chunks = []

        def _recursive_split_with_context(text_chunk, parent_separator=""):
            nonlocal chunks

            for separator in separators:
                if separator == "":
                    sub_chunks = self._split_by_characters(text_chunk)
                    for i, chunk in enumerate(sub_chunks):
                        chunks.append({
                            "text": chunk,
                            "separator": "character",
                            "parent_separator": parent_separator,
                            "level": len(separators) - separators.index(separator),
                            "chunk_index": len(chunks),
                            "size": self.length_function(chunk)
                        })
                    return

                splits = text_chunk.split(separator)
                splits = [split for split in splits if split.strip()]

                if len(splits) > 1:
                    for i, split in enumerate(splits):
                        if self.length_function(split) <= self.chunk_size:
                            chunks.append({
                                "text": split,
                                "separator": separator,
                                "parent_separator": parent_separator,
                                "level": len(separators) - separators.index(separator),
                                "chunk_index": len(chunks),
                                "size": self.length_function(split)
                            })
                        else:
                            # Recursively split this piece
                            _recursive_split_with_context(split, separator)
                    return

            # No separator worked
            sub_chunks = self._split_by_characters(text_chunk)
            for i, chunk in enumerate(sub_chunks):
                chunks.append({
                    "text": chunk,
                    "separator": "character_fallback",
                    "parent_separator": parent_separator,
                    "level": len(separators),
                    "chunk_index": len(chunks),
                    "size": self.length_function(chunk)
                })

        _recursive_split_with_context(text)
        return chunks

    def markdown_aware_recursive_split(self, text):
        """Recursive splitting optimized for Markdown documents"""
        markdown_separators = [
            "\n# ",      # H1 headers
            "\n## ",     # H2 headers
            "\n### ",    # H3 headers
            "\n#### ",   # H4 headers
            "\n##### ",  # H5 headers
            "\n###### ", # H6 headers
            "\n\n",      # Paragraph breaks
            "\n",        # Line breaks
            " ",         # Spaces
            ""           # Characters
        ]

        chunks = []

        def _split_markdown(text_chunk, separator_idx=0):
            if separator_idx >= len(markdown_separators):
                return self._split_by_characters(text_chunk)

            separator = markdown_separators[separator_idx]

            if separator.startswith("\n#"):
                # Markdown headers
                pattern = re.escape(separator)
                splits = re.split(pattern, text_chunk)

                if len(splits) > 1:
                    # Re-add separator to splits (except first)
                    for i in range(1, len(splits)):
                        splits[i] = separator + splits[i]

                    result_chunks = []
                    for split in splits:
                        if self.length_function(split) <= self.chunk_size:
                            result_chunks.append(split)
                        else:
                            # Try next level separator
                            sub_chunks = _split_markdown(split, separator_idx + 1)
                            result_chunks.extend(sub_chunks)

                    return result_chunks
            else:
                # Regular separators
                splits = text_chunk.split(separator)
                splits = [split for split in splits if split.strip()]

                if len(splits) > 1:
                    result_chunks = []
                    for split in splits:
                        if self.length_function(split) <= self.chunk_size:
                            result_chunks.append(split)
                        else:
                            # Try next level separator
                            sub_chunks = _split_markdown(split, separator_idx + 1)
                            result_chunks.extend(sub_chunks)

                    return result_chunks

            # Try next separator
            return _split_markdown(text_chunk, separator_idx + 1)

        raw_chunks = _split_markdown(text)

        # Add metadata
        for i, chunk in enumerate(raw_chunks):
            chunks.append({
                "text": chunk,
                "chunk_index": i,
                "size": self.length_function(chunk),
                "format": "markdown",
                "contains_header": bool(re.search(r'^#+\s', chunk, re.MULTILINE)),
                "contains_code": bool(re.search(r'```', chunk)),
                "contains_list": bool(re.search(r'^\s*[-*+]\s', chunk, re.MULTILINE))
            })

        return chunks
```

## 7-11. Additional Advanced Strategies

### 7. Context-Enriched Chunking

```python
class ContextEnrichedChunker:
    def __init__(self, base_chunker, context_generator=None):
        self.base_chunker = base_chunker
        self.context_generator = context_generator

    def enrich_chunks(self, text, query_context=None):
        """Add contextual information to chunks"""
        base_chunks = self.base_chunker.chunk(text)
        enriched_chunks = []

        for i, chunk in enumerate(base_chunks):
            # Generate context for this chunk
            context = self._generate_context(chunk, text, i, query_context)

            enriched_chunk = {
                "original_text": chunk,
                "context": context,
                "enriched_text": f"Context: {context}\n\nContent: {chunk}",
                "chunk_index": i,
                "method": "context_enriched"
            }
            enriched_chunks.append(enriched_chunk)

        return enriched_chunks

    def _generate_context(self, chunk, full_text, chunk_index, query_context):
        """Generate contextual information for a chunk"""
        # Simple context generation
        sentences = full_text.split('.')

        # Find sentences before and after
        chunk_start = full_text.find(chunk)
        chunk_end = chunk_start + len(chunk)

        # Get preceding and following context
        pre_context = full_text[max(0, chunk_start - 200):chunk_start]
        post_context = full_text[chunk_end:chunk_end + 200]

        context_parts = []
        if pre_context.strip():
            context_parts.append(f"Preceding: {pre_context.strip()}")
        if post_context.strip():
            context_parts.append(f"Following: {post_context.strip()}")

        return " | ".join(context_parts)
```

### 8. Modality-Specific Chunking

```python
class ModalitySpecificChunker:
    def __init__(self):
        self.chunkers = {
            "text": RecursiveChunker(),
            "code": CodeChunker(),
            "table": TableChunker(),
            "image": ImageChunker()
        }

    def chunk_mixed_content(self, document):
        """Chunk document with multiple content types"""
        chunks = []

        # Detect content types
        sections = self._detect_content_types(document)

        for section in sections:
            content_type = section["type"]
            content = section["content"]

            if content_type in self.chunkers:
                section_chunks = self.chunkers[content_type].chunk(content)

                for chunk in section_chunks:
                    chunks.append({
                        "content": chunk,
                        "type": content_type,
                        "metadata": section.get("metadata", {}),
                        "method": f"modality_specific_{content_type}"
                    })

        return chunks

    def _detect_content_types(self, document):
        """Detect different content types in document"""
        sections = []

        # Simple detection logic
        if "```" in document:
            # Code blocks detected
            code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', document, re.DOTALL)
            for lang, code in code_blocks:
                sections.append({
                    "type": "code",
                    "content": code,
                    "metadata": {"language": lang}
                })

        if "|" in document and "\n" in document:
            # Potential table detected
            sections.append({
                "type": "table",
                "content": document,  # Simplified
                "metadata": {}
            })

        # Default to text
        sections.append({
            "type": "text",
            "content": document,
            "metadata": {}
        })

        return sections
```

### 9. Agentic Chunking

```python
class AgenticChunker:
    def __init__(self, chunking_agents):
        self.agents = chunking_agents

    def adaptive_chunking(self, text, requirements):
        """Use agents to determine optimal chunking strategy"""
        # Analyze text characteristics
        text_analysis = self._analyze_text(text)

        # Select appropriate agent based on requirements and text
        selected_agent = self._select_agent(text_analysis, requirements)

        # Use selected agent for chunking
        chunks = selected_agent.chunk(text, requirements)

        return {
            "chunks": chunks,
            "selected_agent": selected_agent.name,
            "reasoning": selected_agent.reasoning,
            "text_analysis": text_analysis
        }

    def _analyze_text(self, text):
        """Analyze text characteristics"""
        return {
            "length": len(text),
            "complexity": self._calculate_complexity(text),
            "structure": self._detect_structure(text),
            "content_type": self._detect_content_type(text)
        }

    def _select_agent(self, analysis, requirements):
        """Select best chunking agent"""
        for agent in self.agents:
            if agent.can_handle(analysis, requirements):
                return agent

        # Fallback to first agent
        return self.agents[0]
```

### 10. Subdocument Chunking

```python
class SubdocumentChunker:
    def __init__(self, max_size=5000):
        self.max_size = max_size

    def chunk_by_logical_sections(self, document):
        """Chunk document by logical sections"""
        sections = self._identify_logical_sections(document)
        chunks = []

        for section in sections:
            if len(section["content"]) <= self.max_size:
                chunks.append({
                    "content": section["content"],
                    "title": section["title"],
                    "level": section["level"],
                    "method": "subdocument_section"
                })
            else:
                # Further split large sections
                sub_chunks = self._split_large_section(section)
                chunks.extend(sub_chunks)

        return chunks

    def _identify_logical_sections(self, document):
        """Identify logical sections in document"""
        sections = []

        # Simple heading detection
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        lines = document.split('\n')

        current_section = {"title": "Introduction", "content": "", "level": 0}

        for line in lines:
            match = re.match(heading_pattern, line)
            if match:
                # Save current section
                if current_section["content"].strip():
                    sections.append(current_section)

                # Start new section
                level = len(match.group(1))
                title = match.group(2)
                current_section = {
                    "title": title,
                    "content": "",
                    "level": level
                }
            else:
                current_section["content"] += line + "\n"

        # Add final section
        if current_section["content"].strip():
            sections.append(current_section)

        return sections
```

### 11. Hybrid Chunking

```python
class HybridChunker:
    def __init__(self, strategies, weights=None):
        self.strategies = strategies
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)

    def hybrid_chunk(self, text, evaluation_criteria=None):
        """Combine multiple chunking strategies"""
        all_chunks = []

        # Apply all strategies
        for i, strategy in enumerate(self.strategies):
            strategy_chunks = strategy.chunk(text)

            for chunk in strategy_chunks:
                all_chunks.append({
                    "content": chunk,
                    "strategy": strategy.name,
                    "strategy_weight": self.weights[i],
                    "method": "hybrid"
                })

        # Evaluate and select best chunks
        if evaluation_criteria:
            evaluated_chunks = self._evaluate_chunks(all_chunks, evaluation_criteria)
        else:
            evaluated_chunks = all_chunks

        # Merge overlapping chunks from different strategies
        merged_chunks = self._merge_overlapping_chunks(evaluated_chunks)

        return merged_chunks

    def _evaluate_chunks(self, chunks, criteria):
        """Evaluate chunks based on criteria"""
        for chunk in chunks:
            score = 0.0
            for criterion, weight in criteria.items():
                criterion_score = self._evaluate_criterion(chunk, criterion)
                score += criterion_score * weight

            chunk["evaluation_score"] = score

        # Sort by evaluation score
        chunks.sort(key=lambda x: x["evaluation_score"], reverse=True)
        return chunks

    def _merge_overlapping_chunks(self, chunks):
        """Merge chunks that overlap significantly"""
        # Simple implementation - could be more sophisticated
        merged = []
        used_indices = set()

        for i, chunk1 in enumerate(chunks):
            if i in used_indices:
                continue

            best_chunk = chunk1.copy()

            for j, chunk2 in enumerate(chunks[i+1:], i+1):
                if j in used_indices:
                    continue

                # Check overlap
                overlap = self._calculate_overlap(chunk1["content"], chunk2["content"])

                if overlap > 0.7:  # High overlap
                    # Merge chunks
                    best_chunk["content"] = max(
                        chunk1["content"],
                        chunk2["content"],
                        key=len
                    )
                    best_chunk["merged_strategies"] = [
                        chunk1["strategy"],
                        chunk2["strategy"]
                    ]
                    used_indices.add(j)

            merged.append(best_chunk)
            used_indices.add(i)

        return merged

    def _calculate_overlap(self, text1, text2):
        """Calculate text overlap ratio"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0
```

## Usage Examples

### Basic Usage
```python
# Initialize different chunkers
fixed_chunker = FixedLengthChunker(chunk_size=1000, chunk_overlap=200)
semantic_chunker = SemanticChunker(similarity_threshold=0.8)
hybrid_chunker = HybridChunker([fixed_chunker, semantic_chunker])

# Apply chunking
text = "Your long document text here..."

fixed_chunks = fixed_chunker.chunk_optimized(text, strategy="balanced")
semantic_chunks = semantic_chunker.semantic_chunk_sentences(text)
hybrid_chunks = hybrid_chunker.hybrid_chunk(text)

print(f"Fixed chunks: {len(fixed_chunks)}")
print(f"Semantic chunks: {len(semantic_chunks)}")
print(f"Hybrid chunks: {len(hybrid_chunks)}")
```

### Advanced Usage with Evaluation
```python
# Create evaluation criteria
evaluation_criteria = {
    "coherence": 0.4,
    "size_appropriateness": 0.3,
    "content_completeness": 0.3
}

# Apply hybrid chunking with evaluation
results = hybrid_chunker.hybrid_chunk(text, evaluation_criteria)

# Analyze results
for chunk in results[:5]:
    print(f"Strategy: {chunk['strategy']}")
    print(f"Score: {chunk.get('evaluation_score', 'N/A')}")
    print(f"Content preview: {chunk['content'][:100]}...")
    print("-" * 50)
```

These 11 advanced chunking strategies provide comprehensive coverage of different approaches for various document types and use cases, from simple fixed-size chunking to sophisticated hybrid methods that combine multiple strategies.