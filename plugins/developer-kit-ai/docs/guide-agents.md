# AI Plugin — Agents Guide

## Overview

The AI plugin provides one specialized agent for prompt engineering and AI system design. This agent is invoked automatically by Claude Code when tasks involve prompt creation, optimization, or AI application development.

## Available Agents

### `prompt-engineering-expert`

**File:** `../agents/prompt-engineering-expert.md`
**Model:** `sonnet`
**Allowed Tools:** `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`

An expert agent for advanced prompting techniques, LLM optimization, and AI system design. Specializes in chain-of-thought, constitutional AI, and production-grade prompt strategies.

## When to Use

Invoke or trigger this agent when:

- Designing a new prompt from requirements
- Optimizing an existing prompt for better performance
- Implementing few-shot examples or chain-of-thought reasoning
- Creating system prompts for consistent AI behavior
- Building multi-step reasoning or code analysis prompts
- Scaling prompt systems across an application

## Core Capabilities

| Domain | Capabilities |
|--------|-------------|
| **Advanced Prompting** | Chain-of-thought, constitutional AI, few-shot, meta-prompting, self-consistency, PALM |
| **Document & Information** | Semantic search, cross-reference analysis, summarization, information extraction |
| **Code Comprehension** | Architecture analysis, security detection, documentation, testing patterns |
| **Multi-Agent Systems** | Role definition, collaboration protocols, workflow orchestration |
| **Production Optimization** | Token efficiency, latency tuning, A/B testing, monitoring |
| **Model-Specific Tuning** | Claude, GPT-4, Gemini, open-source models, multimodal models |

## How to Invoke

### Automatic

Claude Code automatically selects this agent when your request matches its capabilities. No explicit invocation needed.

### Manual

Use the agent by name in conversation:

```
Use the prompt-engineering-expert agent to design a system prompt for a code review assistant.
```

### Via Task Tool

```json
{
  "subagent_type": "developer-kit-ai:prompt-engineering-expert",
  "prompt": "Design a prompt for..."
}
```

## Agent Output Format

The agent provides structured responses with:

1. **Analysis** — Current prompt assessment, failure modes, optimization opportunities
2. **Recommendations** — Specific techniques to apply with rationale
3. **Implementation** — Complete prompt text ready for use
4. **Considerations** — Model-specific notes, edge cases, safety guidelines

## Integration with Other Skills

The agent works seamlessly with the plugin's skills:

- **`prompt-engineering`** — Pattern reference files for CoT, few-shot, templates
- **`rag`** — Document-grounded prompting with source citation
- **`chunking-strategy`** — Context-window optimization for large documents

It also references LangChain4j skills from the Java plugin for context-enhanced prompting and RAG integration.

## Agent Selection Guide

| Task | Agent | Notes |
|------|-------|-------|
| Write a new prompt | `prompt-engineering-expert` | Specify target model and task type |
| Optimize an existing prompt | `prompt-engineering-expert` | Include current prompt in context |
| Add few-shot examples | `prompt-engineering-expert` | Specify domain and edge cases |
| Implement chain-of-thought | `prompt-engineering-expert` | Identify complexity level |
| Build a RAG prompt | `prompt-engineering` skill | Use RAG skill for pipeline context |
| Choose chunking strategy | `chunking-strategy` skill | Pipeline context informs prompt design |

## See Also

- [AI Commands Guide](./guide-commands.md) — `/devkit.prompt-optimize` command
- [Prompt Engineering Skill](../skills/prompt-engineering/) — Skill with 5 reference files
- [RAG Skill](../skills/rag/) — RAG pipeline implementation
- [Chunking Strategy Skill](../skills/chunking-strategy/) — Document preprocessing
- [Core Agent Guide](../../developer-kit-core/docs/guide-agents.md) — All agents across plugins
- [Java Plugin — LangChain4j Guide](../../developer-kit-java/docs/guide-skills-langchain4j.md) — LangChain4j integration
