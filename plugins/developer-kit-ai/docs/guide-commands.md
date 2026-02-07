# AI Plugin Commands Guide

This guide documents all commands available in the Developer Kit AI Plugin, organized by category with brief descriptions, usage, and practical examples.

---

## Table of Contents

1. [Overview](#overview)
2. [Prompt Engineering Commands](#prompt-engineering-commands)
3. [Command Usage Guidelines](#command-usage-guidelines)
4. [See Also](#see-also)

---

## Overview

The AI Plugin provides specialized commands for AI development, prompt engineering, and AI system integration. These commands leverage advanced techniques for optimizing prompts and building effective AI-powered applications.

### Available Commands

- **Prompt Engineering**: 1 command for prompt optimization using advanced techniques

---

## Prompt Engineering Commands

### `/developer-kit-ai:devkit.prompt-optimize`

**Purpose**: Expert prompt optimization using advanced techniques (Chain-of-Thought, Few-Shot, Constitutional AI) for LLM performance enhancement.

**Usage:**
```bash
/developer-kit-ai:devkit.prompt-optimize [prompt-text] [target-model] [optimization-level]
```

**Arguments:**
- `prompt-text` - The prompt to optimize (required)
- `target-model` - Target LLM model (default: `claude-3.5-sonnet`)
- `optimization-level` - Level of optimization depth (default: `standard`)

**Optimization Levels:**
- `basic` - Quick improvements (structure, clarity, basic CoT)
- `standard` - Comprehensive enhancement (CoT, few-shot, safety)
- `advanced` - Production-ready (full optimization with testing framework)

**Common use cases:**
- Optimizing prompts for better AI model performance
- Converting basic instructions to production-ready prompts
- Adding Chain-of-Thought reasoning patterns
- Implementing Few-Shot learning examples
- Ensuring safety and ethical considerations in prompts

**Advanced Techniques Applied:**
- **Chain-of-Thought (CoT)**: Step-by-step reasoning for complex tasks
- **Few-Shot Learning**: Strategic examples with edge cases
- **Constitutional AI**: Self-critique and safety principles
- **Structured Output**: JSON/XML formats for consistency
- **Meta-Prompting**: Dynamic prompt generation

**Model-Specific Optimization:**
- **Claude 3.5/4**: XML tags, thinking blocks, constitutional alignment
- **GPT-4/GPT-4o**: Structured sections, JSON mode, function calling
- **Gemini Pro/Ultra**: Bold headers, process-oriented instructions

**Examples:**
```bash
# Basic optimization with default settings
/developer-kit-ai:devkit.prompt-optimize "Analyze this code and suggest improvements"

# Standard optimization for Claude
/developer-kit-ai:devkit.prompt-optimize "Write a function to process orders" claude-3.5-sonnet standard

# Advanced optimization for GPT-4
/developer-kit-ai:devkit.prompt-optimize "Create a comprehensive code review system" gpt-4 advanced

# Production-ready prompt with testing framework
/developer-kit-ai:devkit.prompt-optimize "Build an AI assistant for customer support" claude-4 advanced
```

**Output:**
The command generates:
1. **Complete Optimized Prompt** - Full text ready for immediate implementation, saved to `optimized-prompt.md`
2. **Optimization Report** - Original prompt assessment, applied techniques, impact metrics
3. **Implementation Guidelines** - Model parameters, safety considerations, monitoring recommendations

**Specialized Optimization Patterns:**

| Task Type | Optimization Focus |
|-----------|-------------------|
| Document Analysis | RAG integration, source citation, cross-reference analysis |
| Code Comprehension | Architecture analysis, security detection, refactoring recommendations |
| Multi-Step Reasoning | Tree-of-thoughts exploration, self-consistency verification, error handling |

---

## Command Usage Guidelines

### How to Invoke Commands

Commands are invoked using the slash syntax in Claude Code with the plugin prefix:

```bash
/developer-kit-ai:{command-name} [arguments]
```

### Best Practices

1. **Start with clear intent**: Provide a well-described prompt to optimize
2. **Choose appropriate optimization level**: Use `basic` for quick fixes, `advanced` for production systems
3. **Specify target model**: Different models benefit from different optimization strategies
4. **Review the output**: Check the optimized prompt and implementation guidelines
5. **Iterate**: Use the optimization as a starting point and refine as needed
6. **Test thoroughly**: Especially for production-ready prompts, validate with real use cases

---

## Common Workflows

### Prompt Optimization Workflow

```bash
# 1. Start with basic optimization
/developer-kit-ai:devkit.prompt-optimize "Your initial prompt" claude-3.5-sonnet basic

# 2. Review output and identify improvements

# 3. Run advanced optimization with refined requirements
/developer-kit-ai:devkit.prompt-optimize "Refined prompt with context" claude-3.5-sonnet advanced

# 4. Test the optimized prompt with target model

# 5. Iterate based on results
```

### Production Prompt Development

```bash
# 1. Draft initial prompt concept
# 2. Run advanced optimization
/developer-kit-ai:devkit.prompt-optimize "Production prompt description" claude-4 advanced

# 3. Review optimization report
# 4. Test with edge cases
# 5. Monitor and iterate based on real-world performance
```

---

## Command Selection Guide

| Task | Command |
|------|---------|
| Optimize prompt for performance | `/developer-kit-ai:devkit.prompt-optimize` |
| Add Chain-of-Thought reasoning | `/developer-kit-ai:devkit.prompt-optimize` (standard/advanced) |
| Create Few-Shot examples | `/developer-kit-ai:devkit.prompt-optimize` (standard/advanced) |
| Production-ready prompt with testing | `/developer-kit-ai:devkit.prompt-optimize` (advanced) |
| Model-specific optimization | `/developer-kit-ai:devkit.prompt-optimize [prompt] [model]` |

---

## See Also

- [AI Agents Guide](./guide-agents.md) - AI plugin agents
- [Prompt Engineering Skill](../skills/prompt-engineering/) - Comprehensive prompt engineering skill
- [RAG Skill](../skills/rag/) - Retrieval-Augmented Generation skill
- [Chunking Strategy Skill](../skills/chunking-strategy/) - Document chunking strategies
- [Core Command Guide](../developer-kit-core/docs/guide-commands.md) - All commands across plugins
- [Java Plugin](../developer-kit-java/docs/) - LangChain4J and Spring AI integration
