# Model Reference

## Supported Foundation Models

### Amazon Models

#### Amazon Titan Text

**Model ID:** `amazon.titan-text-express-v1`
- **Description:** High-quality text generation model
- **Context Window:** Up to 8K tokens
- **Languages:** English, Spanish, French, German, Italian, Portuguese

**Payload Format:**
```json
{
    "inputText": "Your prompt here",
    "textGenerationConfig": {
        "maxTokenCount": 512,
        "temperature": 0.7,
        "topP": 0.9
    }
}
```

**Response Format:**
```json
{
    "results": [{
        "outputText": "Generated text"
    }]
}
```

#### Amazon Titan Text Lite

**Model ID:** `amazon.titan-text-lite-v1`
- **Description:** Cost-effective text generation model
- **Context Window:** Up to 4K tokens
- **Use Case:** Simple text generation tasks

#### Amazon Titan Embeddings

**Model ID:** `amazon.titan-embed-text-v1`
- **Description:** High-quality text embeddings
- **Context Window:** 8K tokens
- **Output:** 1024-dimensional vector

**Payload Format:**
```json
{
    "inputText": "Your text here"
}
```

**Response Format:**
```json
{
    "embedding": [0.1, -0.2, 0.3, ...]
}
```

#### Amazon Titan Image Generator

**Model ID:** `amazon.titan-image-generator-v1`
- **Description:** High-quality image generation
- **Image Size:** 512x512, 1024x1024
- **Use Case:** Text-to-image generation

**Payload Format:**
```json
{
    "taskType": "TEXT_IMAGE",
    "textToImageParams": {
        "text": "Your description"
    },
    "imageGenerationConfig": {
        "numberOfImages": 1,
        "quality": "standard",
        "cfgScale": 8.0,
        "height": 512,
        "width": 512,
        "seed": 12345
    }
}
```

### Anthropic Models

#### Claude 3.5 Sonnet

**Model ID:** `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Description:** High-performance model for complex reasoning, analysis, and creative tasks
- **Context Window:** 200K tokens
- **Languages:** Multiple languages supported
- **Use Case:** Code generation, complex analysis, creative writing, research
- **Features:** Tool use, function calling, JSON mode

**Payload Format:**
```json
{
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [{
        "role": "user",
        "content": "Your message"
    }]
}
```

**Response Format:**
```json
{
    "content": [{
        "text": "Response content"
    }],
    "usage": {
        "input_tokens": 10,
        "output_tokens": 20
    }
}
```

#### Claude 3.5 Haiku

**Model ID:** `anthropic.claude-3-5-haiku-20241022-v2:0`
- **Description:** Fast and affordable model for real-time applications
- **Context Window:** 200K tokens
- **Use Case:** Real-time applications, chatbots, quick responses
- **Features:** Tool use, function calling, JSON mode

#### Claude 3 Opus

**Model ID:** `anthropic.claude-3-opus-20240229-v1:0`
- **Description:** Most capable model
- **Context Window:** 200K tokens
- **Use Case:** Complex reasoning, analysis

#### Claude 3 Sonnet (Legacy)

**Model ID:** `anthropic.claude-3-sonnet-20240229-v1:0`
- **Description:** Previous generation model
- **Context Window:** 200K tokens
- **Use Case:** General purpose applications

### Meta Models

#### Llama 3.1 70B

**Model ID:** `meta.llama3-1-70b-instruct-v1:0`
- **Description:** Latest generation large open-source model
- **Context Window:** 128K tokens
- **Use Case:** General purpose instruction following, complex reasoning
- **Features:** Improved instruction following, larger context window

#### Llama 3.1 8B

**Model ID:** `meta.llama3-1-8b-instruct-v1:0`
- **Description:** Latest generation small fast model
- **Context Window:** 8K tokens
- **Use Case:** Fast inference, lightweight applications

#### Llama 3 70B

**Model ID:** `meta.llama3-70b-instruct-v1:0`
- **Description:** Previous generation large open-source model
- **Context Window:** 8K tokens
- **Use Case:** General purpose instruction following

**Payload Format:**
```json
{
    "prompt": "[INST] Your prompt here [/INST]",
    "max_gen_len": 512,
    "temperature": 0.7,
    "top_p": 0.9
}
```

**Response Format:**
```json
{
    "generation": "Generated text"
}
```

#### Llama 3 8B

**Model ID:** `meta.llama3-8b-instruct-v1:0`
- **Description:** Smaller, faster version
- **Context Window:** 8K tokens
- **Use Case:** Fast inference, lightweight applications

### Stability AI Models

#### Stable Diffusion XL

**Model ID:** `stability.stable-diffusion-xl-v1`
- **Description:** High-quality image generation
- **Image Size:** Up to 1024x1024
- **Use Case:** Text-to-image generation, art creation

**Payload Format:**
```json
{
    "text_prompts": [{
        "text": "Your description"
    }],
    "style_preset": "photographic",
    "seed": 12345,
    "cfg_scale": 10,
    "steps": 50
}
```

**Response Format:**
```json
{
    "artifacts": [{
        "base64": "base64-encoded-image-data",
        "finishReason": "SUCCESS"
    }]
}
```

### Other Models

#### Cohere Command

**Model ID:** `cohere.command-text-v14`
- **Description:** Text generation model
- **Context Window:** 128K tokens
- **Use Case:** Content generation, summarization

#### Mistral Models

**Model ID:** `mistral.mistral-7b-instruct-v0:2`
- **Description:** High-performing open-source model
- **Context Window:** 32K tokens
- **Use Case:** Instruction following, code generation

**Model ID:** `mistral.mixtral-8x7b-instruct-v0:1`
- **Description:** Mixture of experts model
- **Context Window:** 32K tokens
- **Use Case:** Complex reasoning tasks

## Model Selection Guide

### Use Case Recommendations

| Use Case | Recommended Models | Notes |
|----------|-------------------|-------|
| **General Chat/Chatbots** | Claude 3.5 Haiku, Llama 3 8B | Fast response times |
| **Content Creation** | Claude 3.5 Sonnet, Cohere | Creative, coherent outputs |
| **Code Generation** | Claude 3.5 Sonnet, Llama 3.1 70B | Excellent understanding |
| **Analysis & Reasoning** | Claude 3 Opus, Claude 3.5 Sonnet | Complex reasoning |
| **Real-time Applications** | Claude 3.5 Haiku, Titan Lite | Fast inference |
| **Cost-sensitive Apps** | Titan Lite, Claude 3.5 Haiku | Lower cost per token |
| **High Quality** | Claude 3 Opus, Claude 3.5 Sonnet | Premium quality |

### Performance Characteristics

| Model | Speed | Cost | Quality | Context Window |
|-------|-------|------|---------|----------------|
| Claude 3 Opus | Slow | High | Excellent | 200K |
| Claude 3.5 Sonnet | Medium | Medium | Excellent | 200K |
| Claude 3.5 Haiku | Fast | Low | Good | 200K |
| Claude 3 Sonnet (Legacy) | Medium | Medium | Good | 200K |
| Llama 3.1 70B | Medium | Medium | Good | 128K |
| Llama 3.1 8B | Fast | Low | Fair | 8K |
| Llama 3 70B | Medium | Medium | Good | 8K |
| Llama 3 8B | Fast | Low | Fair | 8K |
| Titan Express | Fast | Medium | Good | 8K |
| Titan Lite | Fast | Low | Fair | 4K |

## Model Comparison Matrix

| Feature | Claude 3 | Llama 3 | Titan | Stability |
|---------|----------|---------|-------|-----------|
| **Streaming** | ✅ | ✅ | ✅ | ❌ |
| **Tool Use** | ✅ | ❌ | ❌ | ❌ |
| **Image Generation** | ❌ | ❌ | ✅ | ✅ |
| **Embeddings** | ❌ | ❌ | ✅ | ❌ |
| **Multiple Languages** | ✅ | ✅ | ✅ | ✅ |
| **Context Window** | 200K | 8K | 8K | N/A |
| **Open Source** | ❌ | ✅ | ❌ | ✅ |

## Model Configuration Templates

### Text Generation Template
```java
private static JSONObject createTextGenerationPayload(String modelId, String prompt) {
    JSONObject payload = new JSONObject();

    if (modelId.startsWith("anthropic.claude")) {
        payload.put("anthropic_version", "bedrock-2023-05-31");
        payload.put("max_tokens", 1000);
        payload.put("messages", new JSONObject[]{new JSONObject()
            .put("role", "user")
            .put("content", prompt)
        });
    } else if (modelId.startsWith("meta.llama")) {
        payload.put("prompt", "[INST] " + prompt + " [/INST]");
        payload.put("max_gen_len", 512);
    } else if (modelId.startsWith("amazon.titan")) {
        payload.put("inputText", prompt);
        payload.put("textGenerationConfig", new JSONObject()
            .put("maxTokenCount", 512)
            .put("temperature", 0.7)
        );
    }

    return payload;
}
```

### Image Generation Template
```java
private static JSONObject createImageGenerationPayload(String modelId, String prompt) {
    JSONObject payload = new JSONObject();

    if (modelId.equals("amazon.titan-image-generator-v1")) {
        payload.put("taskType", "TEXT_IMAGE");
        payload.put("textToImageParams", new JSONObject().put("text", prompt));
        payload.put("imageGenerationConfig", new JSONObject()
            .put("numberOfImages", 1)
            .put("quality", "standard")
            .put("height", 512)
            .put("width", 512)
        );
    } else if (modelId.equals("stability.stable-diffusion-xl-v1")) {
        payload.put("text_prompts", new JSONObject[]{new JSONObject().put("text", prompt)});
        payload.put("style_preset", "photographic");
        payload.put("steps", 50);
        payload.put("cfg_scale", 10);
    }

    return payload;
}
```