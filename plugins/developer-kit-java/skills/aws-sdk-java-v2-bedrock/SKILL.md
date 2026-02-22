---
name: aws-sdk-java-v2-bedrock
description: Provides Amazon Bedrock patterns using AWS SDK for Java 2.x. Use when working with foundation models (listing, invoking), text generation, image generation, embeddings, streaming responses, or integrating generative AI with Spring Boot applications.
category: aws
tags: [aws, bedrock, java, sdk, generative-ai, foundation-models]
version: 2.2.0
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# AWS SDK for Java 2.x - Amazon Bedrock

## When to Use

Use this skill when:
- Listing and inspecting foundation models on Amazon Bedrock
- Invoking foundation models for text generation (Claude, Llama, Titan)
- Generating images with AI models (Stable Diffusion)
- Creating text embeddings for RAG applications
- Implementing streaming responses for real-time generation
- Working with multiple AI providers through unified API
- Integrating generative AI into Spring Boot applications
- Building AI-powered chatbots and assistants

## Overview

Amazon Bedrock provides access to foundation models from leading AI providers through a unified API. This skill covers patterns for working with various models including Claude, Llama, Titan, and Stability Diffusion using AWS SDK for Java 2.x.

## Instructions

Follow these steps to work with Amazon Bedrock:

1. **Set Up AWS Credentials** - Configure credentials with appropriate Bedrock permissions
2. **Enable Bedrock Access** - Request access to specific foundation models in the AWS Console
3. **Add Dependencies** - Include bedrock and bedrockruntime dependencies
4. **Create Clients** - Instantiate BedrockClient for management and BedrockRuntimeClient for invocation
5. **List Models** - Query available foundation models and their capabilities
6. **Invoke Models** - Build proper payloads for each model provider's format
7. **Handle Streaming** - Implement streaming response handlers for real-time generation
8. **Integrate with Spring** - Configure beans and services for enterprise applications

## Quick Start

### Dependencies

```xml
<!-- Bedrock (model management) -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>bedrock</artifactId>
</dependency>

<!-- Bedrock Runtime (model invocation) -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>bedrockruntime</artifactId>
</dependency>

<!-- For JSON processing -->
<dependency>
    <groupId>org.json</groupId>
    <artifactId>json</artifactId>
    <version>20231013</version>
</dependency>
```

### Basic Client Setup

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrock.BedrockClient;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;

// Model management client
BedrockClient bedrockClient = BedrockClient.builder()
    .region(Region.US_EAST_1)
    .build();

// Model invocation client
BedrockRuntimeClient bedrockRuntimeClient = BedrockRuntimeClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

## Core Patterns

### Model Discovery

```java
import software.amazon.awssdk.services.bedrock.model.*;
import java.util.List;

public List<FoundationModelSummary> listFoundationModels(BedrockClient bedrockClient) {
    return bedrockClient.listFoundationModels().modelSummaries();
}
```

### Model Invocation

```java
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.bedrockruntime.model.*;
import org.json.JSONObject;

public String invokeModel(BedrockRuntimeClient client, String modelId, String prompt) {
    JSONObject payload = createPayload(modelId, prompt);

    InvokeModelResponse response = client.invokeModel(request -> request
        .modelId(modelId)
        .body(SdkBytes.fromUtf8String(payload.toString())));

    return extractTextFromResponse(modelId, response.body().asUtf8String());
}

private JSONObject createPayload(String modelId, String prompt) {
    if (modelId.startsWith("anthropic.claude")) {
        return new JSONObject()
            .put("anthropic_version", "bedrock-2023-05-31")
            .put("max_tokens", 1000)
            .put("messages", new JSONObject[]{
                new JSONObject().put("role", "user").put("content", prompt)
            });
    } else if (modelId.startsWith("amazon.titan")) {
        return new JSONObject()
            .put("inputText", prompt)
            .put("textGenerationConfig", new JSONObject()
                .put("maxTokenCount", 512)
                .put("temperature", 0.7));
    } else if (modelId.startsWith("meta.llama")) {
        return new JSONObject()
            .put("prompt", "[INST] " + prompt + " [/INST]")
            .put("max_gen_len", 512)
            .put("temperature", 0.7);
    }
    throw new IllegalArgumentException("Unsupported model: " + modelId);
}
```

### Streaming Responses

```java
public void streamResponse(BedrockRuntimeClient client, String modelId, String prompt) {
    JSONObject payload = createPayload(modelId, prompt);

    InvokeModelWithResponseStreamRequest streamRequest =
        InvokeModelWithResponseStreamRequest.builder()
            .modelId(modelId)
            .body(SdkBytes.fromUtf8String(payload.toString()))
            .build();

    client.invokeModelWithResponseStream(streamRequest,
        InvokeModelWithResponseStreamResponseHandler.builder()
            .onEventStream(stream -> {
                stream.forEach(event -> {
                    if (event instanceof PayloadPart) {
                        PayloadPart payloadPart = (PayloadPart) event;
                        String chunk = payloadPart.bytes().asUtf8String();
                        processChunk(modelId, chunk);
                    }
                });
            })
            .build());
}
```

### Text Embeddings

```java
public double[] createEmbeddings(BedrockRuntimeClient client, String text) {
    String modelId = "amazon.titan-embed-text-v1";

    JSONObject payload = new JSONObject().put("inputText", text);

    InvokeModelResponse response = client.invokeModel(request -> request
        .modelId(modelId)
        .body(SdkBytes.fromUtf8String(payload.toString())));

    JSONObject responseBody = new JSONObject(response.body().asUtf8String());
    JSONArray embeddingArray = responseBody.getJSONArray("embedding");

    double[] embeddings = new double[embeddingArray.length()];
    for (int i = 0; i < embeddingArray.length(); i++) {
        embeddings[i] = embeddingArray.getDouble(i);
    }

    return embeddings;
}
```

### Spring Boot Integration

```java
@Configuration
public class BedrockConfiguration {

    @Bean
    public BedrockClient bedrockClient() {
        return BedrockClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public BedrockRuntimeClient bedrockRuntimeClient() {
        return BedrockRuntimeClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}

@Service
public class BedrockAIService {

    private final BedrockRuntimeClient bedrockRuntimeClient;

    @Value("${bedrock.default-model-id:anthropic.claude-3-5-sonnet-20241022-v2:0}")
    private String defaultModelId;

    public BedrockAIService(BedrockRuntimeClient bedrockRuntimeClient) {
        this.bedrockRuntimeClient = bedrockRuntimeClient;
    }

    public String generateText(String prompt) {
        return generateText(prompt, defaultModelId);
    }

    public String generateText(String prompt, String modelId) {
        Map<String, Object> payload = createPayload(modelId, prompt);
        String payloadJson = new ObjectMapper().writeValueAsString(payload);

        InvokeModelResponse response = bedrockRuntimeClient.invokeModel(
            request -> request
                .modelId(modelId)
                .body(SdkBytes.fromUtf8String(payloadJson)));

        return extractTextFromResponse(modelId, response.body().asUtf8String());
    }
}
```

## Examples

```java
BedrockRuntimeClient client = BedrockRuntimeClient.builder()
    .region(Region.US_EAST_1)
    .build();

String prompt = "Explain quantum computing in simple terms";
String response = invokeModel(client, "anthropic.claude-3-5-sonnet-20241022-v2:0", prompt);
System.out.println(response);
```

## Best Practices

### Model Selection
- **Claude 3.5 Sonnet**: Best for complex reasoning, analysis, and creative tasks
- **Claude 3.5 Haiku**: Fast and affordable for real-time applications
- **Claude 3 Opus**: Most advanced reasoning capabilities
- **Llama 3.1**: Latest generation open-source alternative, good for general tasks
- **Titan**: AWS native, cost-effective for simple text generation

### Performance Optimization
- Reuse client instances (don't create new clients for each request)
- Use async clients for I/O operations
- Implement streaming for long responses
- Cache foundation model lists

### Security
- Never log sensitive prompt data
- Use IAM roles for authentication (never access keys)
- Implement rate limiting for public applications
- Sanitize user inputs to prevent prompt injection

### Error Handling
- Implement retry logic for throttling (exponential backoff)
- Handle model-specific validation errors
- Validate responses before processing
- Use proper exception handling for different error types

### Cost Optimization
- Use appropriate max_tokens limits
- Choose cost-effective models for simple tasks
- Cache embeddings when possible
- Monitor usage and set budget alerts

## Common Model IDs

For complete model ID reference with Java constants, see [Model ID Lookup](references/models-lookup.md).

Key models: `anthropic.claude-3-5-sonnet-20241022-v2:0` (Claude), `meta.llama3-3-70b-instruct-v1:0` (Llama), `amazon.titan-text-express-v1` (Titan), `amazon.nova-pro-v1:0` (Nova).

## Advanced Topics

See the [Advanced Topics](references/advanced-topics.md) for:
- Multi-model service patterns
- Advanced error handling with retries
- Batch processing strategies
- Performance optimization techniques
- Custom response parsing

## Model Reference

See the [Model Reference](references/model-reference.md) for:
- Detailed model specifications
- Payload/response formats for each provider
- Performance characteristics
- Model selection guidelines
- Configuration templates

## Testing Strategies

See the [Testing Strategies](references/testing-strategies.md) for:
- Unit testing with mocked clients
- Integration testing with LocalStack
- Performance testing
- Streaming response testing
- Test data management

## Related Skills

- `aws-sdk-java-v2-core` - Core AWS SDK patterns
- `langchain4j-ai-services-patterns` - LangChain4j integration
- `spring-boot-dependency-injection` - Spring DI patterns
- `spring-boot-test-patterns` - Spring testing patterns

## Constraints and Warnings

- **Cost Management**: Bedrock API calls incur charges per token; implement usage monitoring and set budget alerts to avoid unexpected costs.
- **Model Access**: Foundation models must be explicitly enabled in the AWS Console before use; verify model availability in your region.
- **Rate Limits**: Bedrock has per-model and account-level throttling limits; implement exponential backoff for production workloads.
- **Region Availability**: Not all models are available in all regions; check model availability before deployment.
- **Payload Size**: Maximum payload size varies by model; for large documents, consider chunking strategies.
- **Streaming Complexity**: Streaming responses require careful handling of partial content and error recovery.
- **Security**: Never embed credentials in code; use IAM roles for EC2/Lambda, environment variables for local development.
- **Prompt Injection**: Sanitize user inputs to prevent prompt injection attacks that could manipulate model behavior.
- **Data Privacy**: Prompts and responses may be logged by AWS; review data handling policies for sensitive applications.

## References

- [AWS Bedrock User Guide](references/aws-bedrock-user-guide.md)
- [AWS SDK for Java 2.x Documentation](references/aws-sdk-java-bedrock-api.md)
- [Bedrock API Reference](references/aws-bedrock-api-reference.md)
- [AWS SDK Examples](references/aws-sdk-examples.md)
- [Official AWS Examples](references/bedrock_code_examples.md)
- [Supported Models](references/bedrock_models_supported.md)
- [Runtime Examples](references/bedrock_runtime_code_examples.md)