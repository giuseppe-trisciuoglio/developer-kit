# Visualization and Evaluation Tools

This document covers tools and methodologies for visualizing chunking strategies and evaluating their effectiveness.

## Overview of Visualization Tools

| Tool | Purpose | Complexity | Integration |
|------|---------|------------|-------------|
| ChunkViz | Visualize chunk boundaries and overlaps | Low | Standalone |
| Plotly | Interactive visualizations | Medium | Library |
| TensorBoard | ML experiment tracking | High | Framework |
| Streamlit | Web-based dashboards | Medium | Web App |
| D3.js | Custom visualizations | High | Web Library |

## 1. ChunkViz - Chunking Visualization Tool

### Overview
ChunkViz is a specialized tool for visualizing how different chunking strategies behave with various parameters.

### Installation and Setup

```bash
# Clone ChunkViz repository
git clone https://github.com/gkamradt/ChunkViz.git
cd ChunkViz

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from chunkviz import visualize_chunking
import matplotlib.pyplot as plt

# Sample text
sample_text = """
Natural language processing has evolved significantly over the past decade.
Modern transformer models have revolutionized how we approach text understanding.
These models use attention mechanisms to process input text efficiently.
The attention mechanism allows models to focus on relevant input parts.

Retrieval-Augmented Generation (RAG) combines LLMs with external knowledge.
This approach enables models to access current information beyond training data.
RAG systems typically have three main components: retriever, knowledge base, generator.
The retriever finds relevant documents based on user queries.
The generator uses retrieved documents to produce informed responses.
"""

# Visualize different chunking strategies
strategies = [
    {"name": "Fixed Size 100", "chunk_size": 100, "overlap": 0},
    {"name": "Fixed Size 200", "chunk_size": 200, "overlap": 0},
    {"name": "Fixed Size 100 + 20% Overlap", "chunk_size": 100, "overlap": 20},
    {"name": "Semantic", "method": "semantic", "threshold": 0.7}
]

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
axes = axes.flatten()

for i, strategy in enumerate(strategies):
    if i < len(axes):
        visualize_chunking(
            text=sample_text,
            strategy=strategy,
            ax=axes[i],
            title=strategy["name"]
        )

plt.tight_layout()
plt.show()
```

### Advanced ChunkViz Implementation

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Dict, Tuple
import re

class AdvancedChunkViz:
    def __init__(self, figsize=(12, 8)):
        self.figsize = figsize
        self.colors = plt.cm.Set3(np.linspace(0, 1, 12))

    def visualize_multiple_strategies(self, text, strategies, save_path=None):
        """Visualize multiple chunking strategies side by side"""
        n_strategies = len(strategies)
        n_cols = min(3, n_strategies)
        n_rows = (n_strategies + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4, n_rows * 3))
        if n_strategies == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes.reshape(1, -1)

        for i, strategy in enumerate(strategies):
            row, col = i // n_cols, i % n_cols
            ax = axes[row, col] if n_rows > 1 else axes[col]

            self._visualize_single_strategy(text, strategy, ax)

        # Hide unused subplots
        for i in range(n_strategies, n_rows * n_cols):
            row, col = i // n_cols, i % n_cols
            ax = axes[row, col] if n_rows > 1 else axes[col]
            ax.set_visible(False)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def _visualize_single_strategy(self, text, strategy, ax):
        """Visualize a single chunking strategy"""
        chunks = self._apply_strategy(text, strategy)

        # Set up the plot
        ax.set_xlim(0, len(text))
        ax.set_ylim(0, len(chunks))
        ax.set_xlabel('Character Position')
        ax.set_ylabel('Chunk Index')
        ax.set_title(self._get_strategy_title(strategy))

        # Color code chunks
        for i, chunk in enumerate(chunks):
            start_pos = chunk['start']
            end_pos = chunk['end']
            color = self.colors[i % len(self.colors)]

            # Draw chunk rectangle
            rect = patches.Rectangle(
                (start_pos, i), end_pos - start_pos, 0.8,
                linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
            )
            ax.add_patch(rect)

            # Add chunk text (truncated)
            chunk_text = chunk['text'][:20] + "..." if len(chunk['text']) > 20 else chunk['text']
            ax.text(
                start_pos + (end_pos - start_pos) / 2, i + 0.4,
                chunk_text, ha='center', va='center', fontsize=8
            )

            # Add chunk size info
            ax.text(
                start_pos, i - 0.1,
                f"{len(chunk['text'])} chars", ha='left', va='top', fontsize=6
            )

        # Add overlap indicators
        for i in range(1, len(chunks)):
            prev_end = chunks[i-1]['end']
            curr_start = chunks[i]['start']
            if curr_start < prev_end:  # Overlap exists
                overlap_len = prev_end - curr_start
                ax.axvspan(
                    curr_start, prev_end, alpha=0.3, color='red',
                    ymin=(i-0.5)/len(chunks), ymax=(i+0.5)/len(chunks)
                )
                ax.text(
                    (curr_start + prev_end) / 2, i + 0.9,
                    f"Overlap: {overlap_len}", ha='center', va='bottom',
                    fontsize=6, color='red', weight='bold'
                )

    def _apply_strategy(self, text, strategy):
        """Apply chunking strategy to text"""
        if strategy.get('method') == 'semantic':
            return self._semantic_chunking(text, strategy)
        else:
            return self._fixed_size_chunking(text, strategy)

    def _fixed_size_chunking(self, text, strategy):
        """Fixed-size chunking"""
        chunk_size = strategy.get('chunk_size', 100)
        overlap = strategy.get('overlap', 0)
        overlap_chars = int(chunk_size * overlap / 100) if isinstance(overlap, int) else overlap

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append({
                'text': text[start:end],
                'start': start,
                'end': end
            })

            # Calculate next start with overlap
            start = max(0, end - overlap_chars)

            if end >= len(text):
                break

        return chunks

    def _semantic_chunking(self, text, strategy):
        """Simple semantic chunking simulation"""
        # For visualization purposes, split by sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        threshold = strategy.get('threshold', 0.7)
        chunks = []
        current_chunk = []
        current_start = 0

        for i, sentence in enumerate(sentences):
            current_chunk.append(sentence)

            # Simple heuristic: create new chunk after certain number of sentences
            if len(current_chunk) >= 3:
                chunk_text = '. '.join(current_chunk) + '.'
                end_pos = current_start + len(chunk_text)
                chunks.append({
                    'text': chunk_text,
                    'start': current_start,
                    'end': end_pos
                })

                # Start new chunk
                current_start = end_pos
                current_chunk = []

        # Add remaining sentences
        if current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            chunks.append({
                'text': chunk_text,
                'start': current_start,
                'end': current_start + len(chunk_text)
            })

        return chunks

    def _get_strategy_title(self, strategy):
        """Get descriptive title for strategy"""
        if strategy.get('method') == 'semantic':
            return f"Semantic (threshold={strategy.get('threshold', 0.7)})"
        else:
            chunk_size = strategy.get('chunk_size', 100)
            overlap = strategy.get('overlap', 0)
            return f"Fixed Size ({chunk_size} chars, {overlap}% overlap)"

    def create_interactive_visualization(self, text, strategies):
        """Create interactive visualization using Plotly"""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        n_strategies = len(strategies)
        fig = make_subplots(
            rows=n_strategies, cols=1,
            subplot_titles=[self._get_strategy_title(s) for s in strategies],
            vertical_spacing=0.1
        )

        for i, strategy in enumerate(strategies):
            chunks = self._apply_strategy(text, strategy)

            for j, chunk in enumerate(chunks):
                fig.add_trace(
                    go.Scatter(
                        x=[chunk['start'], chunk['end']],
                        y=[j, j],
                        mode='lines+markers',
                        line=dict(width=20),
                        hovertemplate='<b>Chunk %{text}</b><br>' +
                                    'Start: %{x}<br>' +
                                    'End: %{customdata}<br>' +
                                    'Length: %{marker.size}<extra></extra>',
                        text=[f"Chunk {j+1}"],
                        customdata=[chunk['end']],
                        marker=dict(size=len(chunk['text'])),
                        name=f"Chunk {j+1}"
                    ),
                    row=i+1, col=1
                )

        fig.update_layout(
            height=300 * n_strategies,
            title_text="Interactive Chunking Visualization",
            showlegend=False
        )

        return fig

    def compare_chunk_size_distributions(self, text, chunk_sizes):
        """Compare chunk size distributions"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Collect chunk sizes for each strategy
        all_chunk_sizes = []
        labels = []

        for size in chunk_sizes:
            strategy = {"chunk_size": size, "overlap": 0}
            chunks = self._apply_strategy(text, strategy)
            chunk_sizes_list = [len(chunk['text']) for chunk in chunks]
            all_chunk_sizes.append(chunk_sizes_list)
            labels.append(f"Size {size}")

        # Box plot
        ax1.boxplot(all_chunk_sizes, labels=labels)
        ax1.set_title('Chunk Size Distribution')
        ax1.set_ylabel('Chunk Size (characters)')
        ax1.grid(True, alpha=0.3)

        # Histogram
        for i, (sizes, label) in enumerate(zip(all_chunk_sizes, labels)):
            ax2.hist(sizes, alpha=0.7, label=label, bins=20)

        ax2.set_title('Chunk Size Histograms')
        ax2.set_xlabel('Chunk Size (characters)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def visualize_overlap_effects(self, text, base_chunk_size, overlap_percentages):
        """Visualize effects of different overlap percentages"""
        fig, axes = plt.subplots(len(overlap_percentages), 1,
                                figsize=(12, 3 * len(overlap_percentages)))

        if len(overlap_percentages) == 1:
            axes = [axes]

        for i, overlap in enumerate(overlap_percentages):
            strategy = {"chunk_size": base_chunk_size, "overlap": overlap}
            chunks = self._apply_strategy(text, strategy)

            self._visualize_single_strategy(text, strategy, axes[i])

            # Add overlap statistics
            total_overlap = sum(
                max(0, chunks[j-1]['end'] - chunks[j]['start'])
                for j in range(1, len(chunks))
            )
            total_text = len(text)
            overlap_percentage = (total_overlap / total_text) * 100 if total_text > 0 else 0

            axes[i].text(
                0.02, 0.98, f"Total Overlap: {overlap_percentage:.1f}%",
                transform=axes[i].transAxes, ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            )

        plt.tight_layout()
        return fig
```

## 2. Plotly Interactive Visualizations

### Advanced Interactive Dashboard

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict

class InteractiveChunkingDashboard:
    def __init__(self):
        self.figures = {}

    def create_strategy_comparison_dashboard(self, text, strategies):
        """Create comprehensive dashboard for strategy comparison"""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Chunk Boundaries', 'Chunk Size Distribution',
                'Overlap Analysis', 'Coverage Analysis',
                'Performance Metrics', 'Interactive Chunk Explorer'
            ],
            specs=[
                [{"type": "scatter"}, {"type": "histogram"}],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "table"}]
            ]
        )

        # Process all strategies
        strategy_data = {}
        for strategy in strategies:
            chunks = self._apply_chunking_strategy(text, strategy)
            strategy_data[strategy['name']] = {
                'chunks': chunks,
                'strategy': strategy
            }

        # 1. Chunk Boundaries Visualization
        self._add_chunk_boundaries(fig, strategy_data, row=1, col=1)

        # 2. Chunk Size Distribution
        self._add_size_distribution(fig, strategy_data, row=1, col=2)

        # 3. Overlap Analysis
        self._add_overlap_analysis(fig, strategy_data, row=2, col=1)

        # 4. Coverage Analysis
        self._add_coverage_analysis(fig, strategy_data, text, row=2, col=2)

        # 5. Performance Metrics
        self._add_performance_metrics(fig, strategy_data, row=3, col=1)

        # 6. Interactive Chunk Explorer
        self._add_chunk_explorer(fig, strategy_data, row=3, col=2)

        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Comprehensive Chunking Strategy Analysis",
            showlegend=True
        )

        return fig

    def _apply_chunking_strategy(self, text, strategy):
        """Apply chunking strategy and return chunks"""
        # This would use actual chunking implementations
        # For now, simulate fixed-size chunking
        chunk_size = strategy.get('chunk_size', 100)
        overlap = strategy.get('overlap', 0)

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append({
                'id': chunk_id,
                'text': text[start:end],
                'start': start,
                'end': end,
                'size': end - start
            })
            chunk_id += 1

            # Calculate next start with overlap
            start = max(0, end - int(chunk_size * overlap / 100))

            if end >= len(text):
                break

        return chunks

    def _add_chunk_boundaries(self, fig, strategy_data, row, col):
        """Add chunk boundaries visualization"""
        colors = px.colors.qualitative.Set3

        for i, (strategy_name, data) in enumerate(strategy_data.items()):
            chunks = data['chunks']

            for j, chunk in enumerate(chunks):
                fig.add_trace(
                    go.Scatter(
                        x=[chunk['start'], chunk['end']],
                        y=[i, i],
                        mode='lines+markers',
                        line=dict(width=15, color=colors[i % len(colors)]),
                        hovertemplate=f'<b>{strategy_name}</b><br>' +
                                    f'Chunk {j+1}<br>' +
                                    f'Start: {chunk["start"]}<br>' +
                                    f'End: {chunk["end"]}<br>' +
                                    f'Size: {chunk["size"]}<extra></extra>',
                        name=f'{strategy_name} - Chunk {j+1}' if j < 3 else None,
                        showlegend=j < 3
                    ),
                    row=row, col=col
                )

        fig.update_xaxes(title_text="Character Position", row=row, col=col)
        fig.update_yaxes(title_text="Strategy", row=row, col=col)

    def _add_size_distribution(self, fig, strategy_data, row, col):
        """Add chunk size distribution histogram"""
        for i, (strategy_name, data) in enumerate(strategy_data.items()):
            chunks = data['chunks']
            sizes = [chunk['size'] for chunk in chunks]

            fig.add_trace(
                go.Histogram(
                    x=sizes,
                    name=strategy_name,
                    opacity=0.7,
                    nbinsx=20
                ),
                row=row, col=col
            )

        fig.update_xaxes(title_text="Chunk Size (characters)", row=row, col=col)
        fig.update_yaxes(title_text="Frequency", row=row, col=col)

    def _add_overlap_analysis(self, fig, strategy_data, row, col):
        """Add overlap analysis bar chart"""
        strategy_names = []
        overlap_totals = []
        overlap_percentages = []

        for strategy_name, data in strategy_data.items():
            chunks = data['chunks']
            strategy = data['strategy']
            overlap = strategy.get('overlap', 0)

            if overlap > 0:
                total_overlap = sum(
                    max(0, chunks[j-1]['end'] - chunks[j]['start'])
                    for j in range(1, len(chunks))
                )
                overlap_pct = (total_overlap / len(chunks[0]['text'])) * 100 if chunks else 0
            else:
                total_overlap = 0
                overlap_pct = 0

            strategy_names.append(strategy_name)
            overlap_totals.append(total_overlap)
            overlap_percentages.append(overlap_pct)

        fig.add_trace(
            go.Bar(
                x=strategy_names,
                y=overlap_percentages,
                name="Overlap %",
                marker_color='lightblue'
            ),
            row=row, col=col
        )

        fig.update_xaxes(title_text="Strategy", row=row, col=col)
        fig.update_yaxes(title_text="Overlap Percentage", row=row, col=col)

    def _add_coverage_analysis(self, fig, strategy_data, text, row, col):
        """Add coverage analysis scatter plot"""
        strategy_names = []
        chunk_counts = []
        avg_sizes = []
        coverage_scores = []

        for strategy_name, data in strategy_data.items():
            chunks = data['chunks']

            # Calculate coverage (simplified)
            total_covered = sum(chunk['size'] for chunk in chunks)
            coverage = (total_covered / len(text)) * 100 if text else 0

            strategy_names.append(strategy_name)
            chunk_counts.append(len(chunks))
            avg_sizes.append(np.mean([chunk['size'] for chunk in chunks]) if chunks else 0)
            coverage_scores.append(coverage)

        fig.add_trace(
            go.Scatter(
                x=chunk_counts,
                y=avg_sizes,
                mode='markers+text',
                text=strategy_names,
                textposition="top center",
                marker=dict(
                    size=coverage_scores,
                    color=coverage_scores,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Coverage %", x=1.02)
                ),
                name="Strategies"
            ),
            row=row, col=col
        )

        fig.update_xaxes(title_text="Number of Chunks", row=row, col=col)
        fig.update_yaxes(title_text="Average Chunk Size", row=row, col=col)

    def _add_performance_metrics(self, fig, strategy_data, row, col):
        """Add performance metrics comparison"""
        metrics = ['Coherence', 'Speed', 'Memory', 'Accuracy']
        strategies = list(strategy_data.keys())

        # Simulated metrics (in real implementation, these would be calculated)
        metric_values = {
            'Coherence': [0.8, 0.7, 0.9, 0.6],
            'Speed': [0.9, 0.95, 0.7, 0.85],
            'Memory': [0.7, 0.8, 0.6, 0.9],
            'Accuracy': [0.75, 0.8, 0.85, 0.7]
        }

        for i, metric in enumerate(metrics):
            fig.add_trace(
                go.Bar(
                    x=strategies,
                    y=metric_values[metric][:len(strategies)],
                    name=metric,
                    opacity=0.8
                ),
                row=row, col=col
            )

        fig.update_xaxes(title_text="Strategy", row=row, col=col)
        fig.update_yaxes(title_text="Score (0-1)", row=row, col=col)

    def _add_chunk_explorer(self, fig, strategy_data, row, col):
        """Add interactive chunk explorer table"""
        # Select first strategy for table display
        first_strategy = list(strategy_data.keys())[0]
        chunks = strategy_data[first_strategy]['chunks']

        # Create table data
        table_data = [
            [
                f"Chunk {i+1}",
                f"{chunk['size']}",
                f"{chunk['start']}-{chunk['end']}",
                chunk['text'][:50] + "..." if len(chunk['text']) > 50 else chunk['text']
            ]
            for i, chunk in enumerate(chunks[:10])  # Limit to 10 chunks
        ]

        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Chunk ID', 'Size', 'Position', 'Preview'],
                    fill_color='lightblue',
                    align='left'
                ),
                cells=dict(
                    values=list(zip(*table_data)),
                    fill_color='white',
                    align='left'
                ),
                name="Chunk Details"
            ),
            row=row, col=col
        )

    def create_real_time_analysis(self, text_input_callback):
        """Create real-time analysis dashboard"""
        fig = go.Figure()

        # This would be connected to real-time data
        fig.add_trace(
            go.Scatter(
                x=[1, 2, 3, 4],
                y=[10, 11, 12, 13],
                mode='lines+markers',
                name='Real-time Performance'
            )
        )

        fig.update_layout(
            title="Real-time Chunking Analysis",
            xaxis_title="Time",
            yaxis_title="Performance Metric",
            updatemenus=[{
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None]
                    },
                    {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {'frame': {'duration': 0, 'redraw': False}}]
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'x': 0.011,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }]
        )

        return fig
```

## 3. Streamlit Web Dashboard

### Complete Web Application

```python
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict
import time

class StreamlitChunkingDashboard:
    def __init__(self):
        self.chunking_strategies = {
            "Fixed Size - Small": {"chunk_size": 100, "overlap": 0},
            "Fixed Size - Medium": {"chunk_size": 250, "overlap": 0},
            "Fixed Size - Large": {"chunk_size": 500, "overlap": 0},
            "With Overlap - 10%": {"chunk_size": 250, "overlap": 10},
            "With Overlap - 25%": {"chunk_size": 250, "overlap": 25},
            "Semantic": {"method": "semantic", "threshold": 0.7}
        }

    def run(self):
        """Run the Streamlit dashboard"""
        st.set_page_config(
            page_title="Chunking Strategy Analyzer",
            page_icon="📊",
            layout="wide"
        )

        st.title("🔪 Chunking Strategy Analyzer")
        st.markdown("""
        Analyze and visualize different chunking strategies for RAG systems.
        Compare performance metrics and find the optimal approach for your use case.
        """)

        # Sidebar for configuration
        self._render_sidebar()

        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "🔍 Comparison", "📈 Metrics", "⚙️ Settings"])

        with tab1:
            self._render_analysis_tab()

        with tab2:
            self._render_comparison_tab()

        with tab3:
            self._render_metrics_tab()

        with tab4:
            self._render_settings_tab()

    def _render_sidebar(self):
        """Render sidebar configuration"""
        st.sidebar.header("Configuration")

        # Text input
        input_method = st.sidebar.radio(
            "Input Method",
            ["Sample Text", "Upload File", "Enter Text"]
        )

        if input_method == "Sample Text":
            self._load_sample_text()
        elif input_method == "Upload File":
            self._handle_file_upload()
        else:
            self._handle_text_input()

        # Strategy selection
        st.sidebar.subheader("Select Strategies")
        selected_strategies = []
        for strategy_name in self.chunking_strategies.keys():
            if st.sidebar.checkbox(strategy_name, value=True):
                selected_strategies.append(strategy_name)

        st.session_state.selected_strategies = selected_strategies

        # Analysis parameters
        st.sidebar.subheader("Analysis Parameters")
        st.session_state.min_chunk_size = st.sidebar.slider(
            "Min Chunk Size", 50, 500, 100
        )
        st.session_state.max_chunk_size = st.sidebar.slider(
            "Max Chunk Size", 100, 2000, 500
        )

    def _load_sample_text(self):
        """Load sample text for demonstration"""
        sample_texts = {
            "Technical Document": """
            Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.
            Deep learning, a subset of machine learning, uses neural networks with multiple layers to progressively extract higher-level features from raw input.
            Natural Language Processing (NLP) combines computational linguistics with statistical and machine learning models to enable computers to process human language.
            Transformer models have revolutionized NLP by using attention mechanisms to weigh the importance of different words in the input text.
            Retrieval-Augmented Generation (RAG) enhances language models by retrieving relevant information from external knowledge bases.
            """,
            "Legal Document": """
            This agreement is entered into on this date between the parties herein mentioned.
            The terms and conditions outlined herein shall govern the relationship between the parties.
            Any breach of contract shall result in immediate termination and possible legal action.
            The jurisdiction for any disputes shall be the courts of the specified region.
            All amendments must be made in writing and signed by both parties.
            """,
            "Scientific Paper": """
            Our research demonstrates significant improvements in chunking strategies for RAG systems.
            We evaluated multiple approaches across different document types and query patterns.
            Experimental results show that semantic chunking outperforms fixed-size methods by 23% on average.
            Contextual retrieval provides additional benefits but requires increased computational resources.
            Future work will explore hybrid approaches that combine multiple strategies.
            """
        }

        selected_sample = st.sidebar.selectbox(
            "Select Sample Text",
            list(sample_texts.keys())
        )

        st.session_state.input_text = sample_texts[selected_sample]

    def _handle_file_upload(self):
        """Handle file upload"""
        uploaded_file = st.sidebar.file_uploader(
            "Choose a file",
            type=['txt', 'md', 'csv']
        )

        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                st.session_state.input_text = content
                st.sidebar.success(f"Loaded {uploaded_file.name}")
            except Exception as e:
                st.sidebar.error(f"Error reading file: {e}")

    def _handle_text_input(self):
        """Handle manual text input"""
        text = st.sidebar.text_area(
            "Enter your text:",
            height=200
        )

        if text:
            st.session_state.input_text = text

    def _render_analysis_tab(self):
        """Render analysis tab"""
        if 'input_text' not in st.session_state or not st.session_state.input_text:
            st.warning("Please input text using the sidebar configuration.")
            return

        st.header("📊 Chunk Analysis")

        # Display text statistics
        self._display_text_statistics()

        # Apply selected strategies
        if 'selected_strategies' in st.session_state and st.session_state.selected_strategies:
            strategy_results = self._apply_strategies()

            # Create visualizations
            col1, col2 = st.columns(2)

            with col1:
                self._create_chunk_boundary_chart(strategy_results)

            with col2:
                self._create_size_distribution_chart(strategy_results)

            # Detailed analysis
            st.subheader("Detailed Strategy Analysis")
            self._create_detailed_analysis_table(strategy_results)

    def _render_comparison_tab(self):
        """Render comparison tab"""
        if 'selected_strategies' not in st.session_state or not st.session_state.selected_strategies:
            st.warning("Please select strategies in the sidebar.")
            return

        st.header("🔍 Strategy Comparison")

        strategy_results = self._apply_strategies()

        # Comparison metrics
        col1, col2 = st.columns(2)

        with col1:
            self._create_performance_radar_chart(strategy_results)

        with col2:
            self._create_efficiency_comparison(strategy_results)

        # Detailed comparison table
        st.subheader("Detailed Comparison")
        self._create_comparison_table(strategy_results)

    def _render_metrics_tab(self):
        """Render metrics tab"""
        st.header("📈 Performance Metrics")

        if 'input_text' not in st.session_state:
            st.warning("Please input text first.")
            return

        # Metric selection
        selected_metrics = st.multiselect(
            "Select Metrics to Display",
            ["Coverage", "Overlap", "Coherence", "Speed", "Memory Usage"],
            default=["Coverage", "Overlap", "Coherence"]
        )

        if selected_metrics:
            strategy_results = self._apply_strategies()
            self._create_metrics_dashboard(strategy_results, selected_metrics)

    def _render_settings_tab(self):
        """Render settings tab"""
        st.header("⚙️ Advanced Settings")

        # Chunking parameters
        st.subheader("Chunking Parameters")
        col1, col2 = st.columns(2)

        with col1:
            st.number_input("Default Chunk Size", value=250, min_value=50, max_value=2000)
            st.number_input("Default Overlap %", value=10, min_value=0, max_value=50)

        with col2:
            st.selectbox("Default Strategy", ["Fixed Size", "Semantic", "Hybrid"])
            st.slider("Similarity Threshold", 0.0, 1.0, 0.7)

        # Visualization settings
        st.subheader("Visualization Settings")
        st.checkbox("Show Overlap Regions", value=True)
        st.checkbox("Show Chunk Statistics", value=True)
        st.checkbox("Color Code by Strategy", value=True)

        # Export settings
        st.subheader("Export Options")
        export_format = st.selectbox("Export Format", ["PNG", "SVG", "PDF", "CSV"])

        if st.button("Export Analysis"):
            st.success(f"Analysis exported as {export_format}")

    def _display_text_statistics(self):
        """Display input text statistics"""
        text = st.session_state.input_text
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = text.count('.') + text.count('!') + text.count('?')

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Characters", f"{char_count:,}")
        with col2:
            st.metric("Words", f"{word_count:,}")
        with col3:
            st.metric("Sentences", f"{sentence_count:,}")
        with col4:
            st.metric("Avg Word Length", f"{char_count/word_count:.1f}")

    def _apply_strategies(self):
        """Apply selected chunking strategies"""
        text = st.session_state.input_text
        results = {}

        for strategy_name in st.session_state.selected_strategies:
            strategy = self.chunking_strategies[strategy_name]
            chunks = self._chunk_text(text, strategy)
            results[strategy_name] = {
                'chunks': chunks,
                'strategy': strategy,
                'metrics': self._calculate_metrics(chunks, text)
            }

        return results

    def _chunk_text(self, text, strategy):
        """Apply chunking strategy to text"""
        # Simplified chunking implementation
        if strategy.get('method') == 'semantic':
            # Simulate semantic chunking
            sentences = text.split('. ')
            chunks = []
            current_chunk = []

            for sentence in sentences:
                current_chunk.append(sentence)
                if len(' '.join(current_chunk)) > strategy.get('chunk_size', 250):
                    chunks.append({
                        'text': '. '.join(current_chunk),
                        'size': len('. '.join(current_chunk))
                    })
                    current_chunk = []

            if current_chunk:
                chunks.append({
                    'text': '. '.join(current_chunk),
                    'size': len('. '.join(current_chunk))
                })

        else:
            # Fixed-size chunking
            chunk_size = strategy.get('chunk_size', 250)
            overlap = strategy.get('overlap', 0)
            overlap_chars = int(chunk_size * overlap / 100)

            chunks = []
            start = 0

            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunks.append({
                    'text': text[start:end],
                    'size': end - start
                })

                start = max(0, end - overlap_chars)
                if end >= len(text):
                    break

        return chunks

    def _calculate_metrics(self, chunks, original_text):
        """Calculate metrics for chunks"""
        if not chunks:
            return {}

        total_chars = sum(chunk['size'] for chunk in chunks)
        coverage = (total_chars / len(original_text)) * 100 if original_text else 0

        chunk_sizes = [chunk['size'] for chunk in chunks]
        avg_size = np.mean(chunk_sizes) if chunk_sizes else 0
        size_variance = np.var(chunk_sizes) if chunk_sizes else 0

        # Simulated metrics
        coherence_score = np.random.uniform(0.6, 0.9)
        speed_score = 1.0 - (len(chunks) / 100)  # More chunks = slower
        memory_score = 1.0 - (total_chars / 10000)  # More text = more memory

        return {
            'num_chunks': len(chunks),
            'avg_chunk_size': avg_size,
            'coverage': coverage,
            'size_variance': size_variance,
            'coherence': coherence_score,
            'speed': speed_score,
            'memory': memory_score
        }

    def _create_chunk_boundary_chart(self, strategy_results):
        """Create chunk boundary visualization"""
        fig = go.Figure()

        colors = px.colors.qualitative.Set3

        for i, (strategy_name, data) in enumerate(strategy_results.items()):
            chunks = data['chunks']

            for j, chunk in enumerate(chunks):
                # Create chunk visualization
                fig.add_trace(
                    go.Scatter(
                        x=[j, j + 1],
                        y=[i, i],
                        mode='lines',
                        line=dict(width=chunk['size']/10, color=colors[i % len(colors)]),
                        hovertemplate=f'<b>{strategy_name}</b><br>' +
                                    f'Chunk {j+1}<br>' +
                                    f'Size: {chunk["size"]}<extra></extra>',
                        name=f'{strategy_name}' if j == 0 else None,
                        showlegend=j == 0
                    )
                )

        fig.update_layout(
            title="Chunk Boundaries Visualization",
            xaxis_title="Chunk Index",
            yaxis_title="Strategy",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_size_distribution_chart(self, strategy_results):
        """Create size distribution chart"""
        fig = go.Figure()

        for strategy_name, data in strategy_results.items():
            chunk_sizes = [chunk['size'] for chunk in data['chunks']]

            fig.add_trace(
                go.Histogram(
                    x=chunk_sizes,
                    name=strategy_name,
                    opacity=0.7,
                    nbinsx=20
                )
            )

        fig.update_layout(
            title="Chunk Size Distribution",
            xaxis_title="Chunk Size (characters)",
            yaxis_title="Frequency",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_performance_radar_chart(self, strategy_results):
        """Create performance radar chart"""
        metrics = ['Coherence', 'Speed', 'Memory', 'Coverage', 'Consistency']

        fig = go.Figure()

        for strategy_name, data in strategy_results.items():
            metrics_data = data['metrics']
            values = [
                metrics_data.get('coherence', 0.5),
                metrics_data.get('speed', 0.5),
                metrics_data.get('memory', 0.5),
                metrics_data.get('coverage', 0.5) / 100,
                1.0 - (metrics_data.get('size_variance', 0) / 10000)  # Inverse variance
            ]

            fig.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=metrics,
                    fill='toself',
                    name=strategy_name
                )
            )

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Performance Comparison",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_efficiency_comparison(self, strategy_results):
        """Create efficiency comparison chart"""
        strategies = list(strategy_results.keys())
        processing_times = [np.random.uniform(0.5, 2.0) for _ in strategies]  # Simulated
        memory_usage = [np.random.uniform(10, 50) for _ in strategies]  # Simulated

        fig = go.Figure()

        # Add processing time
        fig.add_trace(
            go.Scatter(
                x=strategies,
                y=processing_times,
                mode='markers+lines',
                name='Processing Time (s)',
                marker=dict(size=10),
                line=dict(width=2)
            )
        )

        # Add memory usage
        fig.add_trace(
            go.Scatter(
                x=strategies,
                y=memory_usage,
                mode='markers+lines',
                name='Memory Usage (MB)',
                marker=dict(size=10),
                line=dict(width=2),
                yaxis='y2'
            )
        )

        fig.update_layout(
            title="Efficiency Comparison",
            xaxis_title="Strategy",
            yaxis=dict(title="Processing Time (s)"),
            yaxis2=dict(title="Memory Usage (MB)", overlaying="y", side="right"),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_detailed_analysis_table(self, strategy_results):
        """Create detailed analysis table"""
        table_data = []

        for strategy_name, data in strategy_results.items():
            metrics = data['metrics']
            table_data.append({
                'Strategy': strategy_name,
                'Chunks': metrics['num_chunks'],
                'Avg Size': f"{metrics['avg_chunk_size']:.0f}",
                'Coverage (%)': f"{metrics['coverage']:.1f}",
                'Coherence': f"{metrics['coherence']:.2f}",
                'Speed': f"{metrics['speed']:.2f}",
                'Memory': f"{metrics['memory']:.2f}"
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)

    def _create_comparison_table(self, strategy_results):
        """Create detailed comparison table"""
        comparison_data = []

        metrics = ['num_chunks', 'avg_chunk_size', 'coverage', 'coherence', 'speed', 'memory']
        metric_names = ['Chunks', 'Avg Size', 'Coverage %', 'Coherence', 'Speed', 'Memory']

        for i, metric in enumerate(metrics):
            row = {'Metric': metric_names[i]}
            for strategy_name, data in strategy_results.items():
                value = data['metrics'].get(metric, 0)
                if metric == 'coverage':
                    row[strategy_name] = f"{value:.1f}%"
                else:
                    row[strategy_name] = f"{value:.3f}"
            comparison_data.append(row)

        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)

    def _create_metrics_dashboard(self, strategy_results, selected_metrics):
        """Create metrics dashboard"""
        for metric in selected_metrics:
            st.subheader(f"{metric} Analysis")

            if metric == "Coverage":
                self._create_coverage_chart(strategy_results)
            elif metric == "Overlap":
                self._create_overlap_chart(strategy_results)
            elif metric == "Coherence":
                self._create_coherence_chart(strategy_results)
            elif metric == "Speed":
                self._create_speed_chart(strategy_results)
            elif metric == "Memory Usage":
                self._create_memory_chart(strategy_results)

    def _create_coverage_chart(self, strategy_results):
        """Create coverage analysis chart"""
        strategies = list(strategy_results.keys())
        coverage_values = [data['metrics']['coverage'] for data in strategy_results.values()]

        fig = go.Figure(data=[
            go.Bar(x=strategies, y=coverage_values, marker_color='lightblue')
        ])

        fig.update_layout(
            title="Text Coverage by Strategy",
            xaxis_title="Strategy",
            yaxis_title="Coverage (%)",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_overlap_chart(self, strategy_results):
        """Create overlap analysis chart"""
        # Simulated overlap data
        strategies = list(strategy_results.keys())
        overlap_data = []

        for strategy_name, data in strategy_results.items():
            strategy = data['strategy']
            overlap = strategy.get('overlap', 0)
            overlap_data.append(overlap)

        fig = go.Figure(data=[
            go.Bar(x=strategies, y=overlap_data, marker_color='lightcoral')
        ])

        fig.update_layout(
            title="Overlap Percentage by Strategy",
            xaxis_title="Strategy",
            yaxis_title="Overlap (%)",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_coherence_chart(self, strategy_results):
        """Create coherence analysis chart"""
        strategies = list(strategy_results.keys())
        coherence_values = [data['metrics']['coherence'] for data in strategy_results.values()]

        fig = go.Figure(data=[
            go.Bar(x=strategies, y=coherence_values, marker_color='lightgreen')
        ])

        fig.update_layout(
            title="Coherence Score by Strategy",
            xaxis_title="Strategy",
            yaxis_title="Coherence Score",
            yaxis=dict(range=[0, 1]),
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_speed_chart(self, strategy_results):
        """Create speed analysis chart"""
        strategies = list(strategy_results.keys())
        speed_values = [data['metrics']['speed'] for data in strategy_results.values()]

        fig = go.Figure(data=[
            go.Bar(x=strategies, y=speed_values, marker_color='gold')
        ])

        fig.update_layout(
            title="Processing Speed by Strategy",
            xaxis_title="Strategy",
            yaxis_title="Speed Score",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_memory_chart(self, strategy_results):
        """Create memory usage analysis chart"""
        strategies = list(strategy_results.keys())
        memory_values = [data['metrics']['memory'] for data in strategy_results.values()]

        fig = go.Figure(data=[
            go.Bar(x=strategies, y=memory_values, marker_color='plum')
        ])

        fig.update_layout(
            title="Memory Usage by Strategy",
            xaxis_title="Strategy",
            yaxis_title="Memory Score",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)


# Run the dashboard
if __name__ == "__main__":
    dashboard = StreamlitChunkingDashboard()
    dashboard.run()
```

## 4. Command Line Usage Examples

### Basic Visualization

```python
# Example 1: Basic ChunkViz usage
from chunkviz.advanced import AdvancedChunkViz

text = "Your long document text here..."
viz = AdvancedChunkViz()

# Compare multiple strategies
strategies = [
    {"name": "Small Chunks", "chunk_size": 100, "overlap": 0},
    {"name": "Medium Chunks", "chunk_size": 250, "overlap": 0},
    {"name": "Large Chunks", "chunk_size": 500, "overlap": 0},
    {"name": "With Overlap", "chunk_size": 250, "overlap": 20}
]

viz.visualize_multiple_strategies(text, strategies, save_path="chunking_comparison.png")

# Analyze overlap effects
viz.visualize_overlap_effects(text, 250, [0, 10, 20, 30], save_path="overlap_analysis.png")
```

### Interactive Dashboard

```python
# Example 2: Interactive dashboard
from chunkviz.dashboard import InteractiveChunkingDashboard

dashboard = InteractiveChunkingDashboard()

# Create comprehensive analysis
strategies = [
    {"name": "Fixed-100", "chunk_size": 100, "overlap": 0},
    {"name": "Fixed-250", "chunk_size": 250, "overlap": 0},
    {"name": "Semantic", "method": "semantic"}
]

fig = dashboard.create_strategy_comparison_dashboard(text, strategies)
fig.show()

# Create size distribution comparison
fig = dashboard.compare_chunk_size_distributions(text, [100, 200, 300, 400, 500])
fig.show()
```

### Streamlit Web Application

```python
# Example 3: Run Streamlit dashboard
# Save as app.py and run: streamlit run app.py

from chunkviz.streamlit_app import StreamlitChunkingDashboard

dashboard = StreamlitChunkingDashboard()
dashboard.run()
```

These visualization and evaluation tools provide comprehensive capabilities for analyzing, comparing, and optimizing chunking strategies across different use cases and requirements.