# AI Plugin Agents Guide

This guide provides comprehensive documentation for all AI specialized agents available in the Developer Kit AI Plugin.

---

## Overview

The AI Plugin provides specialized agents for AI development, prompt engineering, and AI system integration. These agents have deep expertise in AI/ML concepts, prompt optimization, and AI application patterns.

### Available Agents

- **Prompt Engineering**: 1 agent for prompt optimization and pattern design

---

## AI Agents

### `prompt-engineering-expert`

**File**: `agents/prompt-engineering-expert.md`

**Purpose**: Prompt optimization and pattern design specialist for building effective AI prompts and AI-powered applications.

**When to use:**
- Designing effective prompts for AI models
- Optimizing prompt performance
- Implementing prompt patterns
- Building AI-powered features
- Troubleshooting AI prompt issues

**Key Capabilities:**
- Prompt optimization strategies
- Few-shot learning patterns
- Chain-of-thought reasoning
- Prompt template systems
- System prompt design
- AI application patterns

---

## Agent Usage Guidelines

### When to Use AI Plugin Agents

AI Plugin agents are most effective for:
- **Prompt Engineering**: Designing and optimizing AI prompts
- **AI Development**: Building AI-powered applications
- **Prompt Patterns**: Implementing proven prompt patterns
- **AI Integration**: Integrating AI capabilities into applications

### How to Invoke Agents

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the prompt-engineering-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

### Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Design prompts | `prompt-engineering-expert` |
| Optimize prompts | `prompt-engineering-expert` |
| Implement prompt patterns | `prompt-engineering-expert` |
| Build AI features | `prompt-engineering-expert` |

---

## See Also

- [AI Commands Guide](./guide-commands.md) - AI plugin commands
- [Prompt Engineering Skill](../skills/prompt-engineering/) - Comprehensive prompt engineering skill
- [RAG Skill](../skills/rag/) - Retrieval-Augmented Generation skill
- [Chunking Strategy Skill](../skills/chunking-strategy/) - Document chunking strategies
- [Core Agent Guide](../developer-kit-core/docs/guide-agents.md) - All agents across plugins
- [Java Plugin](../developer-kit-java/docs/) - LangChain4J and Spring AI integration
