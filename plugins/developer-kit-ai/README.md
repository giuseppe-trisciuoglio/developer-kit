# Developer Kit AI Plugin

AI/ML capabilities for Claude Code — prompt engineering, Retrieval-Augmented Generation (RAG), and document chunking strategies.

## Overview

The `developer-kit-ai` plugin provides specialized skills and agents for building AI-powered applications. It covers the full lifecycle of LLM integration: from prompt design and optimization, to RAG pipeline implementation, to document chunking strategies for vector databases.

## Components

### Skills

| Skill | Description | Reference Files |
|-------|-------------|-----------------|
| `prompt-engineering` | Write, debug, and optimize prompts for LLMs. Covers few-shot learning, chain-of-thought, system prompt design, and template composition. | 5 reference files |
| `rag` | Implement document chunking, embedding, vector storage, and retrieval pipelines for RAG systems. Includes LangChain4j examples. | 5 reference files + 2 assets |
| `chunking-strategy` | Generate chunk size recommendations (256–1024 tokens), overlap percentages (10–20%), and semantic boundary detection methods. | 8 reference files |

### Agents

| Agent | Description |
|-------|-------------|
| `prompt-engineering-expert` | Expert agent for advanced prompting techniques, LLM optimization, and AI system design. Specializes in CoT, constitutional AI, and production prompt strategies. |

### Commands

| Command | Description |
|---------|-------------|
| `/developer-kit-ai:devkit.prompt-optimize` | Optimize prompts using advanced techniques (CoT, few-shot, constitutional AI) with three levels: `basic`, `standard`, `advanced`. |

## Dependencies

- `developer-kit-core` (required by all Developer Kit plugins)

## Usage

This plugin is typically used alongside:

- **`developer-kit-java`** — LangChain4j integration with Java examples
- **`developer-kit-python`** — Python AI/ML development
- **`developer-kit-typescript`** — TypeScript/JavaScript AI integrations

## Documentation

See [`docs/`](docs/) for detailed guides:

- [`docs/README.md`](docs/README.md) — Plugin overview and quick start
- [`docs/guide-agents.md`](docs/guide-agents.md) — Agent capabilities and usage
- [`docs/guide-commands.md`](docs/guide-commands.md) — Command reference with examples
