# AI Plugin — Commands Guide

## Overview

The AI plugin provides one command for prompt optimization. It uses advanced techniques (chain-of-thought, few-shot, constitutional AI) to transform basic instructions into production-ready prompts.

## Available Commands

| Command | Description |
|---------|-------------|
| `/developer-kit-ai:devkit.prompt-optimize` | Optimize prompts at three levels: `basic`, `standard`, `advanced` |

---

## `/developer-kit-ai:devkit.prompt-optimize`

Optimizes prompts using advanced LLM techniques. The command delegates to the `prompt-engineering-expert` agent.

### Syntax

```
/developer-kit-ai:devkit.prompt-optimize [prompt-text] [target-model] [optimization-level]
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `prompt-text` | *(required)* | The prompt text to optimize |
| `target-model` | `claude-sonnet-4-6` | Target LLM model family |
| `optimization-level` | `standard` | Depth of optimization: `basic`, `standard`, or `advanced` |

### Optimization Levels

| Level | Techniques Applied | Output |
|-------|-------------------|--------|
| `basic` | Structure improvement, clarity enhancements, basic chain-of-thought | Quick win optimizations |
| `standard` | CoT, few-shot examples, safety principles, structured output | Comprehensive prompt with report |
| `advanced` | Full optimization suite + testing framework, A/B validation strategy | Production-ready prompt with deployment guide |

### Output

The command produces three deliverables saved to the working directory:

1. **`optimized-prompt.md`** — Complete prompt text ready for immediate use
2. **Optimization Report** — Original assessment, applied techniques, impact metrics
3. **Implementation Guidelines** — Model parameters, safety considerations, monitoring recommendations

### Examples

```bash
# Basic optimization (default model, default level)
/developer-kit-ai:devkit.prompt-optimize "Analyze this code and suggest improvements"

# Standard optimization for Claude Sonnet
/developer-kit-ai:devkit.prompt-optimize "Write a function to process orders" claude-sonnet-4-6 standard

# Advanced optimization for GPT-4 (production-ready)
/developer-kit-ai:devkit.prompt-optimize "Create a code review system" gpt-4 advanced

# Advanced optimization with explicit model
/developer-kit-ai:devkit.prompt-optimize "Build a customer support AI" claude-sonnet-4-6 advanced
```

### Specialized Patterns by Task Type

| Task Type | Applied Techniques |
|-----------|-------------------|
| **Document Analysis** | RAG integration, source citation, cross-reference extraction |
| **Code Comprehension** | Architecture patterns, security detection, refactoring recommendations |
| **Multi-Step Reasoning** | Tree-of-thoughts, self-consistency verification, error recovery |
| **Classification** | Few-shot with edge cases, confidence scoring, calibration prompts |

## Common Workflows

### Prompt Iteration Workflow

```bash
# 1. Start with basic to get quick wins
/developer-kit-ai:devkit.prompt-optimize "Your initial prompt" claude-sonnet-4-6 basic

# 2. Review the output and identify gaps

# 3. Upgrade to advanced with refined requirements
/developer-kit-ai:devkit.prompt-optimize "Refined prompt with more context" claude-sonnet-4-6 advanced

# 4. Test the optimized prompt with real inputs

# 5. Iterate based on test results
```

### Production Prompt Development

```bash
# 1. Define prompt requirements in natural language
# 2. Run advanced optimization
/developer-kit-ai:devkit.prompt-optimize "Production prompt description" claude-sonnet-4-6 advanced

# 3. Review the optimization report
# 4. Test with edge cases and adversarial inputs
# 5. Deploy with monitoring and A/B testing framework
```

## Best Practices

1. **Start with `standard`** — `basic` is useful for quick tweaks, but `standard` gives you the full optimization report
2. **Specify the target model** — Different models benefit from different techniques; always set this explicitly
3. **Provide context** — The more specific your prompt description, the better the optimization
4. **Review all three outputs** — The optimized prompt, the report, and the implementation guidelines are all useful
5. **Test with domain inputs** — Validate the optimized prompt on representative data before production
6. **Iterate** — Use the report's recommendations to refine and re-optimize

## Command Selection Guide

| Task | Command |
|------|---------|
| Quick prompt improvement | `/developer-kit-ai:devkit.prompt-optimize` with `basic` |
| Comprehensive optimization | `/developer-kit-ai:devkit.prompt-optimize` with `standard` |
| Production-ready prompt | `/developer-kit-ai:devkit.prompt-optimize` with `advanced` |
| Model-specific tuning | Set `[target-model]` argument explicitly |
| Adding CoT / few-shot | Use `standard` or `advanced` level |

## See Also

- [AI Agents Guide](./guide-agents.md) — `prompt-engineering-expert` agent
- [Prompt Engineering Skill](../skills/prompt-engineering/) — Skill with reference files for CoT, few-shot, templates, optimization
- [RAG Skill](../skills/rag/) — RAG pipeline implementation for document-grounded prompts
- [Chunking Strategy Skill](../skills/chunking-strategy/) — Document preprocessing for context-window optimization
- [Core Command Guide](../../developer-kit-core/docs/guide-commands.md) — All commands across plugins
- [Java Plugin — LangChain4j Guide](../../developer-kit-java/docs/guide-skills-langchain4j.md) — LangChain4j RAG integration
