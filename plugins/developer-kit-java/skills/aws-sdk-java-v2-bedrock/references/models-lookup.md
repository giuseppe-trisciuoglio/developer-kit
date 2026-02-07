# Model ID Lookup Guide

This document provides quick lookup for the most commonly used model IDs in Amazon Bedrock.

## Text Generation Models

### Claude (Anthropic)
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Claude 4.5 Sonnet | `anthropic.claude-sonnet-4-5-20250929-v1:0` | Latest high-performance model | Complex reasoning, coding, creative tasks |
| Claude 4.5 Haiku | `anthropic.claude-haiku-4-5-20251001-v1:0` | Latest fast model | Real-time applications, chatbots |
| Claude 3.7 Sonnet | `anthropic.claude-3-7-sonnet-20250219-v1:0` | Most advanced reasoning | High-stakes decisions, complex analysis |
| Claude Opus 4.1 | `anthropic.claude-opus-4-1-20250805-v1:0` | Most powerful creative | Advanced creative tasks |
| Claude 3.5 Sonnet v2 | `anthropic.claude-3-5-sonnet-20241022-v2:0` | High-performance model | General use, coding |
| Claude 3.5 Haiku | `anthropic.claude-3-5-haiku-20241022-v1:0` | Fast and affordable | Real-time applications |

### Llama (Meta)
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Llama 3.3 70B | `meta.llama3-3-70b-instruct-v1:0` | Latest generation | Complex reasoning, general use |
| Llama 3.2 90B | `meta.llama3-2-90b-instruct-v1:0` | Large context | Long context tasks |
| Llama 3.2 11B | `meta.llama3-2-11b-instruct-v1:0` | Medium model | Balanced performance |
| Llama 3.2 3B | `meta.llama3-2-3b-instruct-v1:0` | Small model | Fast inference |
| Llama 3.2 1B | `meta.llama3-2-1b-instruct-v1:0` | Ultra-fast | Quick responses |
| Llama 3.1 70B | `meta.llama3-1-70b-instruct-v1:0` | Previous gen | General use |
| Llama 3.1 8B | `meta.llama3-1-8b-instruct-v1:0` | Fast small model | Lightweight applications |

### Mistral AI
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Mistral Large 2407 | `mistral.mistral-large-2407-v1:0` | Latest large model | Complex reasoning |
| Mistral Large 2402 | `mistral.mistral-large-2402-v1:0` | Previous large model | General use |
| Mistral Pixtral 2502 | `mistral.pixtral-large-2502-v1:0` | Multimodal | Text + image understanding |
| Mistral 7B | `mistral.mistral-7b-instruct-v0:2` | Small fast model | Quick responses |

### Amazon
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Titan Text Express | `amazon.titan-text-express-v1` | Fast text generation | Quick responses |
| Titan Text Lite | `amazon.titan-text-lite-v1` | Cost-effective | Budget-sensitive apps |
| Titan Embeddings | `amazon.titan-embed-text-v1` | Text embeddings | Semantic search |

### Cohere
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Command R+ | `cohere.command-r-plus-v1:0` | High performance | Complex tasks |
| Command R | `cohere.command-r-v1:0` | General purpose | Standard use cases |

## Image Generation Models

### Stability AI
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Stable Diffusion 3.5 Large | `stability.sd3-5-large-v1:0` | Latest image gen | High-quality images |
| Stable Diffusion XL | `stability.stable-diffusion-xl-v1` | Previous generation | General image generation |

### Amazon Nova
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Nova Canvas | `amazon.nova-canvas-v1:0` | Image generation | Creative images |
| Nova Reel | `amazon.nova-reel-v1:1` | Video generation | Video content |

## Embedding Models

### Amazon
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Titan Embeddings | `amazon.titan-embed-text-v1` | Text embeddings | Semantic search |
| Titan Embeddings V2 | `amazon.titan-embed-text-v2:0` | Improved embeddings | Better accuracy |

### Cohere
| Model | Model ID | Description | Use Case |
|-------|----------|-------------|----------|
| Embed English | `cohere.embed-english-v3` | English embeddings | English content |
| Embed Multilingual | `cohere.embed-multilingual-v3` | Multi-language | International use |

## Selection Guide

### By Speed
1. **Fastest**: Llama 3.2 1B, Claude 4.5 Haiku, Titan Lite
2. **Fast**: Mistral 7B, Llama 3.2 3B
3. **Medium**: Claude 3.5 Sonnet, Llama 3.2 11B
4. **Slow**: Claude 4.5 Sonnet, Llama 3.3 70B

### By Quality
1. **Highest**: Claude 4.5 Sonnet, Claude 3.7 Sonnet, Claude Opus 4.1
2. **High**: Claude 3.5 Sonnet, Llama 3.3 70B
3. **Medium**: Mistral Large, Llama 3.2 11B
4. **Basic**: Mistral 7B, Llama 3.2 3B

### By Cost
1. **Most Affordable**: Claude 4.5 Haiku, Llama 3.2 1B
2. **Affordable**: Mistral 7B, Titan Lite
3. **Medium**: Claude 3.5 Haiku, Llama 3.2 3B
4. **Expensive**: Claude 4.5 Sonnet, Llama 3.3 70B

## Common Patterns

### Default Model Selection
```java
// For most applications
String DEFAULT_MODEL = "anthropic.claude-sonnet-4-5-20250929-v1:0";

// For real-time applications
String FAST_MODEL = "anthropic.claude-haiku-4-5-20251001-v1:0";

// For budget-sensitive applications
String CHEAP_MODEL = "amazon.titan-text-lite-v1";

// For complex reasoning
String POWERFUL_MODEL = "anthropic.claude-3-7-sonnet-20250219-v1:0";
```

### Model Fallback Chain
```java
private static final String[] MODEL_CHAIN = {
    "anthropic.claude-sonnet-4-5-20250929-v1:0",  // Primary
    "anthropic.claude-haiku-4-5-20251001-v1:0",  // Fast fallback
    "amazon.titan-text-lite-v1"                 // Cheap fallback
};
```