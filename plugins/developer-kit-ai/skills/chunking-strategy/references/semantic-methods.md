# Semantic and Contextual Chunking Methods

This document provides comprehensive coverage of semantic and contextual chunking approaches for advanced RAG systems.

## Overview of Semantic Methods

Semantic chunking methods use understanding of text meaning and relationships to create more meaningful chunks than simple size-based approaches.

| Method | Approach | Best For | Complexity |
|--------|----------|----------|------------|
| Embedding-Based Similarity | Sentence embeddings to find boundaries | Thematic documents | High |
| Topic Modeling | LDA/NMF to identify topic segments | Mixed-topic documents | Medium |
| Named Entity Recognition | Entity-aware boundaries | Technical/medical docs | Medium |
| Dependency Parsing | Syntactic relationships | Structured content | High |
| Cross-Encoder Scoring | BERT-based boundary detection | High-precision needs | Very High |

## 1. Embedding-Based Semantic Chunking

### Core Concept
Use sentence embeddings to identify semantic boundaries where topic shifts occur.

### Advanced Implementation

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
import re

class AdvancedSemanticChunker:
    def __init__(self, model_name="all-MiniLM-L6-v2",
                 boundary_threshold=0.7,
                 min_chunk_size=3,
                 max_chunk_size=15,
                 clustering_method="kmeans"):
        self.model = SentenceTransformer(model_name)
        self.boundary_threshold = boundary_threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.clustering_method = clustering_method

    def multi_level_semantic_chunking(self, text):
        """Multi-level semantic analysis for optimal chunking"""
        # Extract sentences
        sentences = self._extract_sentences(text)
        if len(sentences) <= self.min_chunk_size:
            return [{"text": text, "method": "too_short", "level": 0}]

        # Generate embeddings
        embeddings = self.model.encode(sentences)

        # Level 1: Similarity-based boundaries
        similarity_boundaries = self._find_similarity_boundaries(embeddings)
        similarity_chunks = self._create_chunks_from_boundaries(
            sentences, similarity_boundaries, "similarity"
        )

        # Level 2: Clustering-based boundaries
        clustering_boundaries = self._find_clustering_boundaries(embeddings)
        clustering_chunks = self._create_chunks_from_boundaries(
            sentences, clustering_boundaries, "clustering"
        )

        # Level 3: Hybrid approach
        hybrid_boundaries = self._find_hybrid_boundaries(
            similarity_boundaries, clustering_boundaries, embeddings
        )
        hybrid_chunks = self._create_chunks_from_boundaries(
            sentences, hybrid_boundaries, "hybrid"
        )

        # Evaluate and select best approach
        approaches = [
            {"chunks": similarity_chunks, "method": "similarity"},
            {"chunks": clustering_chunks, "method": "clustering"},
            {"chunks": hybrid_chunks, "method": "hybrid"}
        ]

        best_approach = self._evaluate_approaches(approaches, sentences, embeddings)

        return best_approach["chunks"]

    def _extract_sentences(self, text):
        """Enhanced sentence extraction"""
        # Multiple sentence splitting approaches
        patterns = [
            r'(?<=[.!?])\s+(?=[A-Z])',  # Standard sentence boundaries
            r'(?<=[.!?]\s)\s*(?=[A-Z])',  # Handle multiple spaces
            r'(?<=[.!?])\s+(?=[a-z])',  # Handle lowercase starts
        ]

        sentences = []
        for pattern in patterns:
            potential_sentences = re.split(pattern, text)
            potential_sentences = [s.strip() for s in potential_sentences if s.strip()]

            if len(potential_sentences) > len(sentences):
                sentences = potential_sentences

        return sentences if sentences else [text]

    def _find_similarity_boundaries(self, embeddings):
        """Find boundaries based on similarity drops"""
        boundaries = []

        for i in range(len(embeddings) - 1):
            # Calculate similarity between consecutive sentences
            similarity = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0][0]

            # Dynamic threshold based on local context
            local_threshold = self._calculate_local_threshold(embeddings, i)

            if similarity < local_threshold:
                boundaries.append(i)

        return self._filter_boundaries(boundaries, len(embeddings))

    def _calculate_local_threshold(self, embeddings, index):
        """Calculate dynamic threshold based on local similarity patterns"""
        window_size = min(5, index, len(embeddings) - index - 1)
        start_idx = max(0, index - window_size)
        end_idx = min(len(embeddings), index + window_size + 1)

        local_embeddings = embeddings[start_idx:end_idx]

        if len(local_embeddings) < 2:
            return self.boundary_threshold

        # Calculate local similarity statistics
        similarities = []
        for i in range(len(local_embeddings) - 1):
            sim = cosine_similarity(
                local_embeddings[i].reshape(1, -1),
                local_embeddings[i + 1].reshape(1, -1)
            )[0][0]
            similarities.append(sim)

        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)

        # Threshold based on local statistics
        return max(0.3, mean_sim - std_sim * 0.5)

    def _find_clustering_boundaries(self, embeddings):
        """Find boundaries using clustering approaches"""
        if self.clustering_method == "kmeans":
            return self._kmeans_boundaries(embeddings)
        elif self.clustering_method == "hierarchical":
            return self._hierarchical_boundaries(embeddings)
        else:
            return self._dbscan_boundaries(embeddings)

    def _kmeans_boundaries(self, embeddings):
        """K-means clustering for boundary detection"""
        n_clusters = min(max(len(embeddings) // 5, 2), 10)  # Adaptive cluster count

        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)

        boundaries = []
        for i in range(len(labels) - 1):
            if labels[i] != labels[i + 1]:
                boundaries.append(i)

        return self._filter_boundaries(boundaries, len(embeddings))

    def _hierarchical_boundaries(self, embeddings):
        """Hierarchical clustering for boundary detection"""
        from sklearn.cluster import AgglomerativeClustering

        n_clusters = min(max(len(embeddings) // 4, 2), 8)
        clustering = AgglomerativeClustering(n_clusters=n_clusters)
        labels = clustering.fit_predict(embeddings)

        boundaries = []
        for i in range(len(labels) - 1):
            if labels[i] != labels[i + 1]:
                boundaries.append(i)

        return self._filter_boundaries(boundaries, len(embeddings))

    def _dbscan_boundaries(self, embeddings):
        """DBSCAN clustering for boundary detection"""
        from sklearn.cluster import DBSCAN

        # Adaptive eps based on data characteristics
        distances = []
        for i in range(min(10, len(embeddings))):
            for j in range(i + 1, min(i + 10, len(embeddings))):
                dist = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[j].reshape(1, -1)
                )[0][0]
                distances.append(dist)

        eps = np.percentile(distances, 25) if distances else 0.5

        clustering = DBSCAN(eps=eps, min_samples=2, metric="cosine")
        labels = clustering.fit_predict(embeddings)

        boundaries = []
        for i in range(len(labels) - 1):
            if labels[i] != labels[i + 1] and labels[i] != -1 and labels[i + 1] != -1:
                boundaries.append(i)

        return self._filter_boundaries(boundaries, len(embeddings))

    def _find_hybrid_boundaries(self, similarity_boundaries, clustering_boundaries, embeddings):
        """Combine similarity and clustering approaches"""
        # Combine boundaries from both methods
        all_boundaries = set(similarity_boundaries) | set(clustering_boundaries)
        combined_boundaries = sorted(list(all_boundaries))

        # Refine using consensus scoring
        refined_boundaries = []
        for boundary in combined_boundaries:
            score = self._calculate_boundary_score(boundary, embeddings)
            if score > 0.5:  # Threshold for hybrid approach
                refined_boundaries.append(boundary)

        return self._filter_boundaries(refined_boundaries, len(embeddings))

    def _calculate_boundary_score(self, boundary_idx, embeddings):
        """Calculate confidence score for a boundary"""
        if boundary_idx >= len(embeddings) - 1:
            return 0.0

        # Similarity drop score
        similarity = cosine_similarity(
            embeddings[boundary_idx].reshape(1, -1),
            embeddings[boundary_idx + 1].reshape(1, -1)
        )[0][0]

        similarity_score = 1.0 - similarity  # Lower similarity = higher boundary score

        # Local variance score
        window_size = min(3, boundary_idx, len(embeddings) - boundary_idx - 1)
        start_idx = max(0, boundary_idx - window_size)
        end_idx = min(len(embeddings), boundary_idx + window_size + 1)

        window_embeddings = embeddings[start_idx:end_idx]
        if len(window_embeddings) > 1:
            similarities = []
            for i in range(len(window_embeddings) - 1):
                sim = cosine_similarity(
                    window_embeddings[i].reshape(1, -1),
                    window_embeddings[i + 1].reshape(1, -1)
                )[0][0]
                similarities.append(sim)

            variance_score = np.var(similarities)
        else:
            variance_score = 0.0

        # Combined score
        return (similarity_score * 0.7 + variance_score * 0.3)

    def _filter_boundaries(self, boundaries, total_sentences):
        """Filter boundaries to meet size constraints"""
        if not boundaries:
            return boundaries

        filtered_boundaries = []
        last_boundary = -1

        for boundary in boundaries:
            chunk_size = boundary - last_boundary

            # Check if chunk meets minimum size
            if chunk_size >= self.min_chunk_size:
                # Check if next chunk won't be too small
                remaining_sentences = total_sentences - boundary - 1
                if (remaining_sentences >= self.min_chunk_size or
                    boundary == total_sentences - 1):
                    filtered_boundaries.append(boundary)
                    last_boundary = boundary
            else:
                # Chunk too small, try to extend it
                next_boundary = boundary + (self.min_chunk_size - chunk_size)
                if next_boundary < total_sentences:
                    filtered_boundaries.append(next_boundary)
                    last_boundary = next_boundary

        return filtered_boundaries

    def _create_chunks_from_boundaries(self, sentences, boundaries, method):
        """Create chunks using identified boundaries"""
        chunks = []
        start_idx = 0

        for boundary in boundaries:
            if boundary > start_idx:
                chunk_sentences = sentences[start_idx:boundary + 1]
                chunk_text = " ".join(chunk_sentences)

                chunks.append({
                    "text": chunk_text,
                    "sentence_count": len(chunk_sentences),
                    "start_sentence": start_idx,
                    "end_sentence": boundary,
                    "method": method
                })

                start_idx = boundary + 1

        # Add remaining sentences
        if start_idx < len(sentences):
            chunk_sentences = sentences[start_idx:]
            chunk_text = " ".join(chunk_sentences)

            chunks.append({
                "text": chunk_text,
                "sentence_count": len(chunk_sentences),
                "start_sentence": start_idx,
                "end_sentence": len(sentences) - 1,
                "method": method
            })

        return chunks

    def _evaluate_approaches(self, approaches, sentences, embeddings):
        """Evaluate different chunking approaches"""
        best_approach = approaches[0]
        best_score = 0.0

        for approach in approaches:
            score = self._calculate_approach_score(
                approach["chunks"], sentences, embeddings
            )
            approach["score"] = score

            if score > best_score:
                best_score = score
                best_approach = approach

        return best_approach

    def _calculate_approach_score(self, chunks, sentences, embeddings):
        """Calculate quality score for a chunking approach"""
        if not chunks:
            return 0.0

        # Coherence score (average intra-chunk similarity)
        coherence_scores = []
        for chunk in chunks:
            start_idx = chunk["start_sentence"]
            end_idx = chunk["end_sentence"]

            if end_idx > start_idx:
                chunk_embeddings = embeddings[start_idx:end_idx + 1]
                similarities = []

                for i in range(len(chunk_embeddings) - 1):
                    sim = cosine_similarity(
                        chunk_embeddings[i].reshape(1, -1),
                        chunk_embeddings[i + 1].reshape(1, -1)
                    )[0][0]
                    similarities.append(sim)

                coherence_scores.append(np.mean(similarities) if similarities else 0.0)

        coherence_score = np.mean(coherence_scores) if coherence_scores else 0.0

        # Boundary score (low inter-chunk similarity)
        boundary_scores = []
        for i in range(len(chunks) - 1):
            current_end = chunks[i]["end_sentence"]
            next_start = chunks[i + 1]["start_sentence"]

            if current_end < len(embeddings) and next_start < len(embeddings):
                similarity = cosine_similarity(
                    embeddings[current_end].reshape(1, -1),
                    embeddings[next_start].reshape(1, -1)
                )[0][0]
                boundary_scores.append(1.0 - similarity)  # Lower similarity = better boundary

        boundary_score = np.mean(boundary_scores) if boundary_scores else 0.0

        # Size appropriateness score
        size_scores = []
        for chunk in chunks:
            sentence_count = chunk["sentence_count"]
            if self.min_chunk_size <= sentence_count <= self.max_chunk_size:
                size_scores.append(1.0)
            else:
                # Penalty for size violations
                deviation = min(
                    abs(sentence_count - self.min_chunk_size),
                    abs(sentence_count - self.max_chunk_size)
                )
                size_scores.append(max(0.0, 1.0 - deviation / 10.0))

        size_score = np.mean(size_scores) if size_scores else 0.0

        # Combined score
        return (
            coherence_score * 0.4 +
            boundary_score * 0.4 +
            size_score * 0.2
        )
```

## 2. Contextual Retrieval

### Core Concept
Enhance each chunk with LLM-generated contextual information to improve retrieval and understanding.

### Implementation

```python
import openai
from typing import List, Dict, Optional
import json
import asyncio

class ContextualRetriever:
    def __init__(self, api_key, model="gpt-3.5-turbo", max_context_length=200):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_context_length = max_context_length

    def contextual_chunking(self, text, base_chunker):
        """Add contextual information to chunks"""
        # First, create base chunks
        base_chunks = base_chunker.chunk(text)

        # Generate context for each chunk
        contextualized_chunks = []
        total_chunks = len(base_chunks)

        for i, chunk in enumerate(base_chunks):
            print(f"Processing chunk {i + 1}/{total_chunks}")

            # Generate contextual information
            context = self._generate_context(chunk, text, i, total_chunks)

            # Create contextualized chunk
            contextualized_chunk = {
                "original_text": chunk,
                "context": context,
                "contextualized_text": f"Context: {context}\n\nContent: {chunk}",
                "chunk_index": i,
                "total_chunks": total_chunks,
                "method": "contextual_retrieval"
            }

            contextualized_chunks.append(contextualized_chunk)

        return contextualized_chunks

    def _generate_context(self, chunk, full_document, chunk_index, total_chunks):
        """Generate contextual information for a chunk"""
        # Create a comprehensive prompt for context generation
        prompt = self._create_context_prompt(
            chunk, full_document, chunk_index, total_chunks
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at providing contextual information for document chunks. Generate concise, relevant context that helps understand the chunk's place in the larger document."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating context: {e}")
            return self._generate_fallback_context(chunk, chunk_index, total_chunks)

    def _create_context_prompt(self, chunk, full_document, chunk_index, total_chunks):
        """Create prompt for context generation"""
        # Get surrounding context
        surrounding_context = self._get_surrounding_context(
            full_document, chunk, chunk_index, total_chunks
        )

        prompt = f"""
I need you to provide brief contextual information for a chunk from a larger document.

Document position: Chunk {chunk_index + 1} of {total_chunks}

Surrounding context:
{surrounding_context}

Current chunk:
{chunk}

Please provide a concise context (maximum {self.max_context_length} characters) that:
1. Explains where this chunk fits in the overall document
2. Mentions key topics or themes immediately before/after
3. Helps understand the chunk's purpose and relevance
4. Is written in a clear, informative style

Context:
"""
        return prompt

    def _get_surrounding_context(self, full_document, chunk, chunk_index, total_chunks):
        """Extract context from surrounding parts of the document"""
        # Find chunk position in document
        chunk_start = full_document.find(chunk)
        if chunk_start == -1:
            return "Context not available"

        # Extract surrounding text
        context_window = 500  # characters
        start_pos = max(0, chunk_start - context_window)
        end_pos = min(len(full_document), chunk_start + len(chunk) + context_window)

        surrounding_text = full_document[start_pos:end_pos]

        # Highlight the chunk position
        relative_start = chunk_start - start_pos
        relative_end = relative_start + len(chunk)

        before_chunk = surrounding_text[:relative_start]
        after_chunk = surrounding_text[relative_end:]

        context_parts = []
        if before_chunk.strip():
            context_parts.append(f"Before: {before_chunk.strip()[-100:]}...")
        if after_chunk.strip():
            context_parts.append(f"After: ...{after_chunk.strip()[:100]}")

        return " | ".join(context_parts)

    def _generate_fallback_context(self, chunk, chunk_index, total_chunks):
        """Generate simple fallback context"""
        return f"This is chunk {chunk_index + 1} of {total_chunks} in the document."

    async def async_contextual_chunking(self, text, base_chunker, max_concurrent=5):
        """Asynchronous contextual chunking for better performance"""
        # Create base chunks first
        base_chunks = base_chunker.chunk(text)
        total_chunks = len(base_chunks)

        # Create semaphore to limit concurrent API calls
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_chunk(chunk, index):
            async with semaphore:
                return await self._async_generate_context(chunk, text, index, total_chunks)

        # Process all chunks concurrently
        tasks = [
            process_chunk(chunk, i) for i, chunk in enumerate(base_chunks)
        ]

        contextualized_chunks = await asyncio.gather(*tasks)

        # Add chunk information
        for i, chunk in enumerate(base_chunks):
            contextualized_chunks[i]["original_text"] = chunk
            contextualized_chunks[i]["chunk_index"] = i
            contextualized_chunks[i]["total_chunks"] = total_chunks
            contextualized_chunks[i]["method"] = "async_contextual_retrieval"

        return contextualized_chunks

    async def _async_generate_context(self, chunk, full_document, chunk_index, total_chunks):
        """Asynchronous context generation"""
        surrounding_context = self._get_surrounding_context(
            full_document, chunk, chunk_index, total_chunks
        )

        prompt = self._create_context_prompt(
            chunk, full_document, chunk_index, total_chunks
        )

        try:
            # Note: This would require an async OpenAI client
            # For now, we'll use the synchronous version
            context = self._generate_context(chunk, full_document, chunk_index, total_chunks)

            return {
                "context": context,
                "contextualized_text": f"Context: {context}\n\nContent: {chunk}"
            }

        except Exception as e:
            print(f"Error in async context generation: {e}")
            fallback_context = self._generate_fallback_context(chunk, chunk_index, total_chunks)
            return {
                "context": fallback_context,
                "contextualized_text": f"Context: {fallback_context}\n\nContent: {chunk}"
            }

    def hierarchical_contextual_chunking(self, text, base_chunker):
        """Hierarchical contextual chunking with multiple context levels"""
        # Create base chunks
        base_chunks = base_chunker.chunk(text)

        # Level 1: Document-level context
        document_summary = self._generate_document_summary(text)

        # Level 2: Section-level context
        section_contexts = self._generate_section_contexts(text, base_chunks)

        # Level 3: Local context for each chunk
        contextualized_chunks = []
        for i, chunk in enumerate(base_chunks):
            local_context = self._generate_context(chunk, text, i, len(base_chunks))

            # Combine all context levels
            combined_context = f"""
Document Overview: {document_summary}

Section Context: {section_contexts.get(i, "Section context not available")}

Local Context: {local_context}
"""

            contextualized_chunk = {
                "original_text": chunk,
                "document_context": document_summary,
                "section_context": section_contexts.get(i, ""),
                "local_context": local_context,
                "combined_context": combined_context.strip(),
                "contextualized_text": f"Context: {combined_context.strip()}\n\nContent: {chunk}",
                "chunk_index": i,
                "method": "hierarchical_contextual"
            }

            contextualized_chunks.append(contextualized_chunk)

        return contextualized_chunks

    def _generate_document_summary(self, text):
        """Generate a summary of the entire document"""
        try:
            prompt = f"""
Please provide a brief summary (maximum 100 words) of this document:

{text[:1000]}...
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing documents concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating document summary: {e}")
            return "Document summary not available"

    def _generate_section_contexts(self, text, chunks):
        """Generate context for different sections of the document"""
        section_contexts = {}

        # Simple section detection based on position
        total_chunks = len(chunks)
        sections = 3  # Divide document into 3 sections

        for i, chunk in enumerate(chunks):
            section_number = min(i // (total_chunks // sections), sections - 1)

            if section_number not in section_contexts:
                section_contexts[section_number] = self._generate_section_context(
                    text, section_number, sections
                )

        return {i: section_contexts.get(i // (total_chunks // sections), "")
                for i in range(total_chunks)}

    def _generate_section_context(self, text, section_number, total_sections):
        """Generate context for a specific section"""
        try:
            section_size = len(text) // total_sections
            start_pos = section_number * section_size
            end_pos = min((section_number + 1) * section_size, len(text))

            section_text = text[start_pos:end_pos]

            prompt = f"""
Provide brief context for section {section_number + 1} of {total_sections} in this document:

Section text:
{section_text[:500]}...

Context (maximum 50 words):
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at providing document section context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating section context: {e}")
            return f"This is section {section_number + 1} of the document"
```

## 3. Late Chunking

### Core Concept
Generate embeddings for the entire document first, then create chunk embeddings from token-level embeddings.

### Implementation

```python
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Tuple
import logging

class LateChunker:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2",
                 device="cpu", chunk_size=512):
        self.device = device
        self.chunk_size = chunk_size

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()

    def late_chunk_embedding(self, text, chunk_sizes=None):
        """Generate late chunk embeddings"""
        if chunk_sizes is None:
            chunk_sizes = [256, 512, 1024]  # Multiple chunk sizes to try

        results = {}

        for chunk_size in chunk_sizes:
            # Tokenize entire document
            encoded = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=False,
                padding=False
            ).to(self.device)

            input_ids = encoded["input_ids"][0]
            attention_mask = encoded["attention_mask"][0]

            # Generate embeddings for all tokens
            with torch.no_grad():
                outputs = self.model(**encoded, output_hidden_states=True)
                # Use last hidden state
                token_embeddings = outputs.last_hidden_state[0]  # Shape: [seq_len, hidden_dim]

            # Create chunks from token embeddings
            chunk_embeddings = self._create_chunk_embeddings(
                token_embeddings, attention_mask, chunk_size, input_ids
            )

            # Create chunk texts
            chunk_texts = self._create_chunk_texts(input_ids, chunk_size)

            results[chunk_size] = {
                "chunk_embeddings": chunk_embeddings,
                "chunk_texts": chunk_texts,
                "chunk_size": chunk_size,
                "method": "late_chunking"
            }

        return results

    def _create_chunk_embeddings(self, token_embeddings, attention_mask, chunk_size, input_ids):
        """Create chunk embeddings from token embeddings"""
        chunk_embeddings = []
        valid_token_indices = torch.where(attention_mask == 1)[0]

        for i in range(0, len(valid_token_indices), chunk_size):
            end_idx = min(i + chunk_size, len(valid_token_indices))
            chunk_token_indices = valid_token_indices[i:end_idx]

            # Get embeddings for tokens in this chunk
            chunk_token_embeddings = token_embeddings[chunk_token_indices]

            # Pool token embeddings to create chunk embedding
            # Using mean pooling
            chunk_embedding = torch.mean(chunk_token_embeddings, dim=0)
            chunk_embeddings.append(chunk_embedding.cpu().numpy())

        return chunk_embeddings

    def _create_chunk_texts(self, input_ids, chunk_size):
        """Create text for each chunk"""
        chunk_texts = []
        total_tokens = input_ids.shape[0]

        for i in range(0, total_tokens, chunk_size):
            end_idx = min(i + chunk_size, total_tokens)
            chunk_ids = input_ids[i:end_idx]
            chunk_text = self.tokenizer.decode(chunk_ids, skip_special_tokens=True)
            chunk_texts.append(chunk_text)

        return chunk_texts

    def adaptive_late_chunking(self, text, complexity_analyzer=None):
        """Adaptive late chunking based on document complexity"""
        # Analyze document complexity
        if complexity_analyzer:
            complexity = complexity_analyzer.analyze_complexity(text)
        else:
            complexity = self._simple_complexity_analysis(text)

        # Adjust chunk size based on complexity
        if complexity < 0.3:  # Simple document
            chunk_sizes = [512, 1024]
        elif complexity < 0.7:  # Medium complexity
            chunk_sizes = [256, 512, 1024]
        else:  # Complex document
            chunk_sizes = [128, 256, 512]

        results = self.late_chunk_embedding(text, chunk_sizes)

        # Evaluate and select best chunk size
        best_chunk_size = self._evaluate_chunk_sizes(results, complexity)

        return {
            "best_results": results[best_chunk_size],
            "all_results": results,
            "selected_chunk_size": best_chunk_size,
            "complexity": complexity,
            "method": "adaptive_late_chunking"
        }

    def _simple_complexity_analysis(self, text):
        """Simple complexity analysis"""
        # Factors: average sentence length, vocabulary diversity, punctuation complexity
        sentences = text.split('.')
        if not sentences:
            return 0.0

        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        vocab_diversity = unique_words / total_words if total_words > 0 else 0

        # Normalize and combine
        length_score = min(avg_sentence_length / 20, 1.0)  # Normalize to 0-1
        diversity_score = vocab_diversity

        complexity = (length_score + diversity_score) / 2
        return complexity

    def _evaluate_chunk_sizes(self, results, complexity):
        """Evaluate different chunk sizes and select the best one"""
        best_chunk_size = list(results.keys())[0]
        best_score = 0.0

        for chunk_size, result in results.items():
            score = self._calculate_chunking_score(result, complexity)
            result["score"] = score

            if score > best_score:
                best_score = score
                best_chunk_size = chunk_size

        return best_chunk_size

    def _calculate_chunking_score(self, result, complexity):
        """Calculate quality score for a chunking result"""
        chunk_texts = result["chunk_texts"]
        chunk_embeddings = result["chunk_embeddings"]

        if not chunk_texts or not chunk_embeddings:
            return 0.0

        # Factors to consider:
        # 1. Number of chunks (moderate number is better)
        # 2. Chunk size consistency
        # 3. Content preservation (estimated)

        num_chunks = len(chunk_texts)
        chunk_lengths = [len(text.split()) for text in chunk_texts]

        # Score based on optimal number of chunks (5-15 is ideal)
        if 5 <= num_chunks <= 15:
            chunk_count_score = 1.0
        elif num_chunks < 5:
            chunk_count_score = num_chunks / 5.0
        else:
            chunk_count_score = max(0.0, 1.0 - (num_chunks - 15) / 20.0)

        # Score based on size consistency
        if chunk_lengths:
            mean_length = np.mean(chunk_lengths)
            std_length = np.std(chunk_lengths)
            consistency_score = max(0.0, 1.0 - (std_length / mean_length))
        else:
            consistency_score = 0.0

        # Adjust score based on document complexity
        complexity_adjustment = 0.5 + complexity * 0.5

        total_score = (
            chunk_count_score * 0.4 +
            consistency_score * 0.3 +
            complexity_adjustment * 0.3
        )

        return total_score

    def contextual_late_chunking(self, text, context_generator=None):
        """Combine late chunking with contextual information"""
        # Generate late chunk embeddings
        late_results = self.late_chunk_embedding(text)

        # Use best chunk size (default to 512)
        best_chunk_size = 512
        if best_chunk_size in late_results:
            result = late_results[best_chunk_size]
        else:
            result = list(late_results.values())[0]

        chunk_texts = result["chunk_texts"]
        chunk_embeddings = result["chunk_embeddings"]

        # Add contextual information if available
        if context_generator:
            contextualized_chunks = []
            for i, chunk_text in enumerate(chunk_texts):
                context = context_generator.generate_context(
                    chunk_text, text, i, len(chunk_texts)
                )

                contextualized_chunk = {
                    "text": chunk_text,
                    "embedding": chunk_embeddings[i],
                    "context": context,
                    "contextualized_text": f"Context: {context}\n\nContent: {chunk_text}",
                    "chunk_index": i,
                    "method": "contextual_late_chunking"
                }
                contextualized_chunks.append(contextualized_chunk)

            return {
                "chunks": contextualized_chunks,
                "chunk_size": best_chunk_size,
                "method": "contextual_late_chunking"
            }

        # Return without context
        chunks = []
        for i, (chunk_text, embedding) in enumerate(zip(chunk_texts, chunk_embeddings)):
            chunks.append({
                "text": chunk_text,
                "embedding": embedding,
                "chunk_index": i,
                "method": "late_chunking"
            })

        return {
            "chunks": chunks,
            "chunk_size": best_chunk_size,
            "method": "late_chunking"
        }

    def semantic_late_chunking(self, text, semantic_model=None):
        """Combine late chunking with semantic boundary detection"""
        # Generate late chunks
        late_results = self.late_chunk_embedding(text)
        best_chunk_size = 512

        if best_chunk_size in late_results:
            result = late_results[best_chunk_size]
        else:
            result = list(late_results.values())[0]

        chunk_texts = result["chunk_texts"]
        chunk_embeddings = result["chunk_embeddings"]

        # Use semantic model to analyze chunk boundaries
        if semantic_model:
            # Analyze semantic coherence between chunks
            semantic_chunks = self._analyze_semantic_boundaries(
                chunk_texts, chunk_embeddings, semantic_model
            )
        else:
            # Simple semantic analysis using the embeddings we already have
            semantic_chunks = self._simple_semantic_analysis(
                chunk_texts, chunk_embeddings
            )

        return {
            "chunks": semantic_chunks,
            "chunk_size": best_chunk_size,
            "method": "semantic_late_chunking"
        }

    def _analyze_semantic_boundaries(self, chunk_texts, chunk_embeddings, semantic_model):
        """Analyze semantic boundaries using external semantic model"""
        # This would use a semantic model to analyze boundaries
        # For now, return chunks with similarity information
        chunks = []

        for i, (text, embedding) in enumerate(zip(chunk_texts, chunk_embeddings)):
            chunk_data = {
                "text": text,
                "embedding": embedding,
                "chunk_index": i,
                "method": "semantic_late_chunking"
            }

            # Calculate similarity with adjacent chunks
            if i > 0:
                prev_embedding = chunk_embeddings[i - 1]
                similarity = np.dot(embedding, prev_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(prev_embedding)
                )
                chunk_data["similarity_with_previous"] = similarity

            if i < len(chunk_texts) - 1:
                next_embedding = chunk_embeddings[i + 1]
                similarity = np.dot(embedding, next_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(next_embedding)
                )
                chunk_data["similarity_with_next"] = similarity

            chunks.append(chunk_data)

        return chunks

    def _simple_semantic_analysis(self, chunk_texts, chunk_embeddings):
        """Simple semantic analysis using available embeddings"""
        chunks = []

        for i, (text, embedding) in enumerate(zip(chunk_texts, chunk_embeddings)):
            chunk_data = {
                "text": text,
                "embedding": embedding,
                "chunk_index": i,
                "method": "simple_semantic_late_chunking"
            }

            # Calculate similarity with adjacent chunks
            if i > 0:
                prev_embedding = chunk_embeddings[i - 1]
                similarity = np.dot(embedding, prev_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(prev_embedding)
                )
                chunk_data["similarity_with_previous"] = similarity

            if i < len(chunk_texts) - 1:
                next_embedding = chunk_embeddings[i + 1]
                similarity = np.dot(embedding, next_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(next_embedding)
                )
                chunk_data["similarity_with_next"] = similarity

            chunks.append(chunk_data)

        return chunks
```

## 4. Usage Examples and Integration

### Complete Semantic Chunking Pipeline

```python
class SemanticChunkingPipeline:
    def __init__(self, config):
        self.config = config
        self.semantic_chunker = AdvancedSemanticChunker(
            model_name=config.get("semantic_model", "all-MiniLM-L6-v2"),
            boundary_threshold=config.get("boundary_threshold", 0.7)
        )
        self.contextual_retriever = ContextualRetriever(
            api_key=config.get("openai_api_key"),
            model=config.get("context_model", "gpt-3.5-turbo")
        )
        self.late_chunker = LateChunker(
            model_name=config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        )

    def process_document(self, text, method="hybrid"):
        """Process document using specified semantic method"""
        if method == "semantic":
            return self.semantic_chunker.multi_level_semantic_chunking(text)

        elif method == "contextual":
            base_chunker = FixedSizeChunker(chunk_size=512, chunk_overlap=50)
            return self.contextual_retriever.contextual_chunking(text, base_chunker)

        elif method == "late":
            return self.late_chunker.adaptive_late_chunking(text)

        elif method == "hybrid":
            # Combine multiple approaches
            semantic_chunks = self.semantic_chunker.multi_level_semantic_chunking(text)

            # Add contextual information to semantic chunks
            contextualized_chunks = []
            for i, chunk in enumerate(semantic_chunks):
                context = self._generate_simple_context(chunk["text"], text, i)

                contextualized_chunk = chunk.copy()
                contextualized_chunk.update({
                    "context": context,
                    "contextualized_text": f"Context: {context}\n\nContent: {chunk['text']}",
                    "method": "hybrid_semantic_contextual"
                })
                contextualized_chunks.append(contextualized_chunk)

            return contextualized_chunks

        else:
            raise ValueError(f"Unknown method: {method}")

    def _generate_simple_context(self, chunk, full_text, chunk_index):
        """Generate simple context without API calls"""
        # Find chunk position
        chunk_start = full_text.find(chunk)
        if chunk_start == -1:
            return f"Chunk {chunk_index + 1}"

        # Extract surrounding text
        context_window = 200
        start_pos = max(0, chunk_start - context_window)
        end_pos = min(len(full_text), chunk_start + len(chunk) + context_window)

        surrounding = full_text[start_pos:end_pos]
        return f"Part of larger document (position {chunk_start}-{chunk_start + len(chunk)})"

    def evaluate_chunking(self, chunks, text):
        """Evaluate chunking quality"""
        if not chunks:
            return {"overall_score": 0.0, "metrics": {}}

        # Generate embeddings for evaluation
        sentences = self._extract_sentences(text)
        sentence_embeddings = self.semantic_chunker.model.encode(sentences)

        # Calculate metrics
        metrics = {
            "coherence": self._calculate_coherence(chunks, sentence_embeddings),
            "coverage": self._calculate_coverage(chunks, text),
            "size_distribution": self._analyze_size_distribution(chunks),
            "boundary_quality": self._assess_boundary_quality(chunks)
        }

        # Calculate overall score
        weights = {"coherence": 0.3, "coverage": 0.3, "size_distribution": 0.2, "boundary_quality": 0.2}
        overall_score = sum(metrics[metric] * weights[metric] for metric in weights)

        return {
            "overall_score": overall_score,
            "metrics": metrics,
            "chunks_count": len(chunks)
        }

    def _extract_sentences(self, text):
        """Extract sentences for evaluation"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_coherence(self, chunks, sentence_embeddings):
        """Calculate semantic coherence of chunks"""
        coherence_scores = []

        for chunk in chunks:
            chunk_text = chunk.get("text", chunk.get("original_text", ""))
            chunk_sentences = self._extract_sentences(chunk_text)

            if len(chunk_sentences) > 1:
                # Find sentence indices
                sentence_indices = []
                for sentence in chunk_sentences:
                    # Simple matching - could be improved
                    for i, sent in enumerate(self._extract_sentences(" ".join([s for s in chunk_sentences]))):
                        if sentence.strip() == sent.strip():
                            sentence_indices.append(i)
                            break

                if len(sentence_indices) > 1:
                    # Calculate average similarity between consecutive sentences
                    similarities = []
                    for i in range(len(sentence_indices) - 1):
                        idx1, idx2 = sentence_indices[i], sentence_indices[i + 1]
                        if idx1 < len(sentence_embeddings) and idx2 < len(sentence_embeddings):
                            sim = cosine_similarity(
                                sentence_embeddings[idx1].reshape(1, -1),
                                sentence_embeddings[idx2].reshape(1, -1)
                            )[0][0]
                            similarities.append(sim)

                    if similarities:
                        coherence_scores.append(np.mean(similarities))

        return np.mean(coherence_scores) if coherence_scores else 0.0

    def _calculate_coverage(self, chunks, original_text):
        """Calculate how well chunks cover the original text"""
        combined_chunk_text = " ".join([
            chunk.get("text", chunk.get("original_text", "")) for chunk in chunks
        ])

        # Simple coverage based on text overlap
        original_words = set(original_text.lower().split())
        chunk_words = set(combined_chunk_text.lower().split())

        if not original_words:
            return 0.0

        coverage = len(original_words & chunk_words) / len(original_words)
        return coverage

    def _analyze_size_distribution(self, chunks):
        """Analyze the distribution of chunk sizes"""
        sizes = [len(chunk.get("text", chunk.get("original_text", "")).split())
                for chunk in chunks]

        if not sizes:
            return 0.0

        mean_size = np.mean(sizes)
        std_size = np.std(sizes)

        # Ideal distribution has low variance
        consistency_score = max(0.0, 1.0 - (std_size / mean_size))
        return consistency_score

    def _assess_boundary_quality(self, chunks):
        """Assess the quality of chunk boundaries"""
        if len(chunks) < 2:
            return 1.0

        boundary_scores = []

        for i in range(len(chunks) - 1):
            current_chunk = chunks[i].get("text", chunks[i].get("original_text", ""))
            next_chunk = chunks[i + 1].get("text", chunks[i + 1].get("original_text", ""))

            # Check if chunks end/begin naturally
            ends_naturally = current_chunk.strip().endswith(('.', '!', '?', ':', ';'))
            begins_naturally = next_chunk.strip()[0].isupper() if next_chunk.strip() else False

            boundary_score = 0.0
            if ends_naturally:
                boundary_score += 0.5
            if begins_naturally:
                boundary_score += 0.5

            boundary_scores.append(boundary_score)

        return np.mean(boundary_scores) if boundary_scores else 0.0


# Usage Example
if __name__ == "__main__":
    config = {
        "semantic_model": "all-MiniLM-L6-v2",
        "context_model": "gpt-3.5-turbo",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "openai_api_key": "your-api-key-here"
    }

    pipeline = SemanticChunkingPipeline(config)

    # Sample document
    sample_text = """
    Natural language processing has evolved significantly over the past decade.
    Modern transformer models have revolutionized how we approach text understanding and generation.
    These models use attention mechanisms to process input text in parallel.
    The attention mechanism allows the model to focus on different parts of the input when producing each part of the output.

    Retrieval-Augmented Generation (RAG) combines the power of large language models with external knowledge retrieval.
    This approach enables models to access up-to-date information beyond their training data.
    RAG systems typically consist of three main components: a retriever, a knowledge base, and a generator.
    The retriever finds relevant documents from the knowledge base based on the user's query.
    The generator then uses these retrieved documents to produce a more informed response.
    """

    # Process with different methods
    semantic_chunks = pipeline.process_document(sample_text, method="semantic")
    contextual_chunks = pipeline.process_document(sample_text, method="contextual")
    late_chunks = pipeline.process_document(sample_text, method="late")
    hybrid_chunks = pipeline.process_document(sample_text, method="hybrid")

    # Evaluate results
    methods = {
        "semantic": semantic_chunks,
        "contextual": contextual_chunks,
        "late": late_chunks,
        "hybrid": hybrid_chunks
    }

    for method_name, chunks in methods.items():
        evaluation = pipeline.evaluate_chunking(chunks, sample_text)
        print(f"\n{method_name.upper()} Method:")
        print(f"  Chunks: {len(chunks)}")
        print(f"  Overall Score: {evaluation['overall_score']:.3f}")
        print(f"  Coherence: {evaluation['metrics']['coherence']:.3f}")
        print(f"  Coverage: {evaluation['metrics']['coverage']:.3f}")
```

These semantic and contextual chunking methods provide advanced approaches for creating meaningful, context-aware chunks that significantly improve RAG system performance compared to traditional size-based chunking methods.