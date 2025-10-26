---
name: aws-sdk-java-v2-bedrock
description: Amazon Bedrock patterns using AWS SDK for Java 2.x. Use when working with foundation models (listing, invoking), text generation, image generation, embeddings, streaming responses, or integrating generative AI with Spring Boot applications.
category: aws
tags: [aws, bedrock, java, sdk, generative-ai, foundation-models]
version: 1.0.1
allowed-tools: Read, Write, Bash
---

# AWS SDK for Java 2.x - Amazon Bedrock

## When to Use

Use this skill when:
- Listing and inspecting foundation models
- Invoking foundation models for text generation
- Generating images with AI models
- Creating text embeddings for RAG applications
- Implementing streaming responses
- Working with multiple AI providers (Claude, Llama, Titan, etc.)
- Integrating generative AI into Spring Boot applications
- Building AI-powered chatbots and assistants

## Dependencies

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

## Client Setup

### Bedrock Client (Model Management)

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrock.BedrockClient;

BedrockClient bedrockClient = BedrockClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Bedrock Runtime Client (Model Invocation)

```java
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;

BedrockRuntimeClient bedrockRuntimeClient = BedrockRuntimeClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Async Clients

```java
import software.amazon.awssdk.services.bedrock.BedrockAsyncClient;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeAsyncClient;

BedrockAsyncClient bedrockAsyncClient = BedrockAsyncClient.builder()
    .region(Region.US_EAST_1)
    .build();

BedrockRuntimeAsyncClient bedrockRuntimeAsyncClient = 
    BedrockRuntimeAsyncClient.builder()
        .region(Region.US_EAST_1)
        .build();
```

## Foundation Model Discovery

### List All Foundation Models

```java
import software.amazon.awssdk.services.bedrock.model.*;
import java.util.List;

public List<FoundationModelSummary> listFoundationModels(BedrockClient bedrockClient) {
    try {
        ListFoundationModelsResponse response = bedrockClient.listFoundationModels();
        
        List<FoundationModelSummary> models = response.modelSummaries();
        
        models.forEach(model -> {
            System.out.println("Model ID: " + model.modelId());
            System.out.println("Provider: " + model.providerName());
            System.out.println("Name: " + model.modelName());
            System.out.println();
        });
        
        return models;
        
    } catch (SdkClientException e) {
        System.err.println(e.getMessage());
        throw new RuntimeException(e);
    }
}
```

### Get Foundation Model Details

```java
public FoundationModelDetails getFoundationModel(BedrockClient bedrockClient, 
                                                  String modelIdentifier) {
    try {
        GetFoundationModelResponse response = bedrockClient.getFoundationModel(
            r -> r.modelIdentifier(modelIdentifier));
        
        FoundationModelDetails model = response.modelDetails();
        
        System.out.println("Model ID: " + model.modelId());
        System.out.println("Model ARN: " + model.modelArn());
        System.out.println("Model Name: " + model.modelName());
        System.out.println("Provider: " + model.providerName());
        System.out.println("Input modalities: " + model.inputModalities());
        System.out.println("Output modalities: " + model.outputModalities());
        System.out.println("Streaming supported: " + model.responseStreamingSupported());
        
        return model;
        
    } catch (ValidationException e) {
        throw new IllegalArgumentException(e.getMessage());
    } catch (SdkException e) {
        System.err.println(e.getMessage());
        throw new RuntimeException(e);
    }
}
```

### List Models Async

```java
import java.util.concurrent.CompletableFuture;

public CompletableFuture<List<FoundationModelSummary>> listFoundationModelsAsync(
        BedrockAsyncClient bedrockAsyncClient) {
    
    return bedrockAsyncClient.listFoundationModels()
        .thenApply(response -> {
            response.modelSummaries().forEach(model -> {
                System.out.println("Model ID: " + model.modelId());
                System.out.println("Provider: " + model.providerName());
            });
            return response.modelSummaries();
        })
        .exceptionally(ex -> {
            System.err.println("Error listing models: " + ex.getMessage());
            throw new RuntimeException(ex);
        });
}
```

## Text Generation

### Invoke Claude Model

```java
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.bedrockruntime.model.*;
import org.json.JSONObject;

public String invokeClaude(BedrockRuntimeClient client, String prompt) {
    String modelId = "anthropic.claude-3-sonnet-20240229-v1:0";
    
    // Create request payload
    JSONObject payload = new JSONObject()
        .put("anthropic_version", "bedrock-2023-05-31")
        .put("max_tokens", 1000)
        .put("messages", new JSONObject[]{
            new JSONObject()
                .put("role", "user")
                .put("content", prompt)
        });
    
    try {
        InvokeModelResponse response = client.invokeModel(request -> request
            .modelId(modelId)
            .body(SdkBytes.fromUtf8String(payload.toString())));
        
        // Parse response
        JSONObject responseBody = new JSONObject(response.body().asUtf8String());
        String content = responseBody
            .getJSONArray("content")
            .getJSONObject(0)
            .getString("text");
        
        return content;
        
    } catch (Exception e) {
        System.err.println("Error invoking Claude: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

### Invoke Llama Model

```java
public String invokeLlama(BedrockRuntimeClient client, String prompt) {
    String modelId = "meta.llama3-70b-instruct-v1:0";
    
    JSONObject payload = new JSONObject()
        .put("prompt", prompt)
        .put("max_gen_len", 512)
        .put("temperature", 0.7)
        .put("top_p", 0.9);
    
    try {
        InvokeModelResponse response = client.invokeModel(request -> request
            .modelId(modelId)
            .body(SdkBytes.fromUtf8String(payload.toString())));
        
        JSONObject responseBody = new JSONObject(response.body().asUtf8String());
        return responseBody.getString("generation");
        
    } catch (Exception e) {
        System.err.println("Error invoking Llama: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

### Invoke Amazon Titan

```java
public String invokeTitan(BedrockRuntimeClient client, String prompt) {
    String modelId = "amazon.titan-text-express-v1";
    
    JSONObject payload = new JSONObject()
        .put("inputText", prompt)
        .put("textGenerationConfig", new JSONObject()
            .put("maxTokenCount", 512)
            .put("temperature", 0.7)
            .put("topP", 0.9));
    
    try {
        InvokeModelResponse response = client.invokeModel(request -> request
            .modelId(modelId)
            .body(SdkBytes.fromUtf8String(payload.toString())));
        
        JSONObject responseBody = new JSONObject(response.body().asUtf8String());
        return responseBody
            .getJSONArray("results")
            .getJSONObject(0)
            .getString("outputText");
        
    } catch (Exception e) {
        System.err.println("Error invoking Titan: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

## Streaming Responses

### Stream Claude Response

```java
import software.amazon.awssdk.services.bedrockruntime.model.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public void streamClaudeResponse(BedrockRuntimeClient client, String prompt) {
    String modelId = "anthropic.claude-3-sonnet-20240229-v1:0";
    
    JSONObject payload = new JSONObject()
        .put("anthropic_version", "bedrock-2023-05-31")
        .put("max_tokens", 1000)
        .put("messages", new JSONObject[]{
            new JSONObject()
                .put("role", "user")
                .put("content", prompt)
        });
    
    try {
        InvokeModelWithResponseStreamRequest streamRequest = 
            InvokeModelWithResponseStreamRequest.builder()
                .modelId(modelId)
                .body(SdkBytes.fromUtf8String(payload.toString()))
                .build();
        
        InvokeModelWithResponseStreamResponseHandler handler = 
            InvokeModelWithResponseStreamResponseHandler.builder()
                .onEventStream(stream -> {
                    stream.forEach(event -> {
                        if (event instanceof PayloadPart) {
                            PayloadPart payloadPart = (PayloadPart) event;
                            String chunk = payloadPart.bytes().asUtf8String();
                            
                            JSONObject chunkJson = new JSONObject(chunk);
                            if (chunkJson.getString("type").equals("content_block_delta")) {
                                String text = chunkJson
                                    .getJSONObject("delta")
                                    .getString("text");
                                System.out.print(text);
                            }
                        }
                    });
                })
                .build();
        
        client.invokeModelWithResponseStream(streamRequest, handler);
        System.out.println(); // New line after streaming
        
    } catch (Exception e) {
        System.err.println("Error streaming response: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

## Image Generation

### Generate Image with Stable Diffusion

```java
import java.util.Base64;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.math.BigInteger;
import java.security.SecureRandom;

public String generateImage(BedrockRuntimeClient client, String prompt) {
    String modelId = "stability.stable-diffusion-xl-v1";
    
    // Generate random seed
    BigInteger seed = new BigInteger(31, new SecureRandom());
    
    JSONObject payload = new JSONObject()
        .put("text_prompts", new JSONObject[]{
            new JSONObject().put("text", prompt)
        })
        .put("style_preset", "photographic")
        .put("seed", seed)
        .put("cfg_scale", 10)
        .put("steps", 50);
    
    try {
        InvokeModelResponse response = client.invokeModel(request -> request
            .modelId(modelId)
            .body(SdkBytes.fromUtf8String(payload.toString())));
        
        JSONObject responseBody = new JSONObject(response.body().asUtf8String());
        String base64Image = responseBody
            .getJSONArray("artifacts")
            .getJSONObject(0)
            .getString("base64");
        
        // Save image to file
        byte[] imageBytes = Base64.getDecoder().decode(base64Image);
        Files.write(Paths.get("generated-image.png"), imageBytes);
        
        return base64Image;
        
    } catch (Exception e) {
        System.err.println("Error generating image: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

### Generate Image with Amazon Titan

```java
public String generateImageWithTitan(BedrockRuntimeClient client, String prompt) {
    String modelId = "amazon.titan-image-generator-v1";
    
    JSONObject payload = new JSONObject()
        .put("taskType", "TEXT_IMAGE")
        .put("textToImageParams", new JSONObject()
            .put("text", prompt))
        .put("imageGenerationConfig", new JSONObject()
            .put("numberOfImages", 1)
            .put("quality", "standard")
            .put("cfgScale", 8.0)
            .put("height", 512)
            .put("width", 512)
            .put("seed", new SecureRandom().nextInt(Integer.MAX_VALUE)));
    
    try {
        InvokeModelResponse response = client.invokeModel(request -> request
            .modelId(modelId)
            .body(SdkBytes.fromUtf8String(payload.toString())));
        
        JSONObject responseBody = new JSONObject(response.body().asUtf8String());
        String base64Image = responseBody
            .getJSONArray("images")
            .getString(0);
        
        return base64Image;
        
    } catch (Exception e) {
        System.err.println("Error generating image with Titan: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

## Text Embeddings

### Create Embeddings with Titan

```java
public double[] createEmbeddings(BedrockRuntimeClient client, String text) {
    String modelId = "amazon.titan-embed-text-v1";
    
    JSONObject payload = new JSONObject()
        .put("inputText", text);
    
    try {
        InvokeModelResponse response = client.invokeModel(request -> request
            .modelId(modelId)
            .body(SdkBytes.fromUtf8String(payload.toString())));
        
        JSONObject responseBody = new JSONObject(response.body().asUtf8String());
        
        // Extract embedding vector
        org.json.JSONArray embeddingArray = responseBody.getJSONArray("embedding");
        double[] embeddings = new double[embeddingArray.length()];
        
        for (int i = 0; i < embeddingArray.length(); i++) {
            embeddings[i] = embeddingArray.getDouble(i);
        }
        
        return embeddings;
        
    } catch (Exception e) {
        System.err.println("Error creating embeddings: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

## Spring Boot Integration

### Configuration

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
    
    @Bean
    public BedrockRuntimeAsyncClient bedrockRuntimeAsyncClient() {
        return BedrockRuntimeAsyncClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### AI Service Layer

```java
@Service
public class BedrockAIService {
    
    private final BedrockRuntimeClient bedrockRuntimeClient;
    private final ObjectMapper objectMapper;
    
    @Value("${bedrock.default-model-id:anthropic.claude-3-sonnet-20240229-v1:0}")
    private String defaultModelId;
    
    public BedrockAIService(BedrockRuntimeClient bedrockRuntimeClient,
                            ObjectMapper objectMapper) {
        this.bedrockRuntimeClient = bedrockRuntimeClient;
        this.objectMapper = objectMapper;
    }
    
    public String generateText(String prompt) {
        return generateText(prompt, defaultModelId);
    }
    
    public String generateText(String prompt, String modelId) {
        try {
            Map<String, Object> payload = createPayload(modelId, prompt);
            String payloadJson = objectMapper.writeValueAsString(payload);
            
            InvokeModelResponse response = bedrockRuntimeClient.invokeModel(
                request -> request
                    .modelId(modelId)
                    .body(SdkBytes.fromUtf8String(payloadJson)));
            
            return extractTextFromResponse(modelId, response.body().asUtf8String());
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate text", e);
        }
    }
    
    private Map<String, Object> createPayload(String modelId, String prompt) {
        if (modelId.startsWith("anthropic.claude")) {
            return Map.of(
                "anthropic_version", "bedrock-2023-05-31",
                "max_tokens", 1000,
                "messages", List.of(
                    Map.of("role", "user", "content", prompt)
                )
            );
        } else if (modelId.startsWith("amazon.titan")) {
            return Map.of(
                "inputText", prompt,
                "textGenerationConfig", Map.of(
                    "maxTokenCount", 512,
                    "temperature", 0.7
                )
            );
        }
        throw new IllegalArgumentException("Unsupported model: " + modelId);
    }
    
    private String extractTextFromResponse(String modelId, String responseJson) 
            throws Exception {
        JsonNode responseNode = objectMapper.readTree(responseJson);
        
        if (modelId.startsWith("anthropic.claude")) {
            return responseNode
                .path("content")
                .get(0)
                .path("text")
                .asText();
        } else if (modelId.startsWith("amazon.titan")) {
            return responseNode
                .path("results")
                .get(0)
                .path("outputText")
                .asText();
        }
        throw new IllegalArgumentException("Unsupported model: " + modelId);
    }
}
```

### REST Controller

```java
@RestController
@RequestMapping("/api/ai")
public class AIController {
    
    private final BedrockAIService aiService;
    
    public AIController(BedrockAIService aiService) {
        this.aiService = aiService;
    }
    
    @PostMapping("/generate")
    public ResponseEntity<AIResponse> generateText(@RequestBody AIRequest request) {
        String response = aiService.generateText(request.prompt());
        return ResponseEntity.ok(new AIResponse(response));
    }
    
    public record AIRequest(String prompt) {}
    public record AIResponse(String text) {}
}
```

### Chatbot Service

```java
@Service
public class ChatbotService {
    
    private final BedrockRuntimeClient bedrockRuntimeClient;
    private final Map<String, List<ChatMessage>> conversationHistory = 
        new ConcurrentHashMap<>();
    
    public ChatbotService(BedrockRuntimeClient bedrockRuntimeClient) {
        this.bedrockRuntimeClient = bedrockRuntimeClient;
    }
    
    public String chat(String conversationId, String userMessage) {
        List<ChatMessage> history = conversationHistory
            .computeIfAbsent(conversationId, k -> new ArrayList<>());
        
        // Add user message to history
        history.add(new ChatMessage("user", userMessage));
        
        // Build messages array for Claude
        JSONArray messages = new JSONArray();
        history.forEach(msg -> {
            messages.put(new JSONObject()
                .put("role", msg.role())
                .put("content", msg.content()));
        });
        
        JSONObject payload = new JSONObject()
            .put("anthropic_version", "bedrock-2023-05-31")
            .put("max_tokens", 1000)
            .put("messages", messages);
        
        try {
            InvokeModelResponse response = bedrockRuntimeClient.invokeModel(
                request -> request
                    .modelId("anthropic.claude-3-sonnet-20240229-v1:0")
                    .body(SdkBytes.fromUtf8String(payload.toString())));
            
            JSONObject responseBody = new JSONObject(response.body().asUtf8String());
            String assistantMessage = responseBody
                .getJSONArray("content")
                .getJSONObject(0)
                .getString("text");
            
            // Add assistant response to history
            history.add(new ChatMessage("assistant", assistantMessage));
            
            return assistantMessage;
            
        } catch (Exception e) {
            throw new RuntimeException("Chat failed", e);
        }
    }
    
    public void clearHistory(String conversationId) {
        conversationHistory.remove(conversationId);
    }
    
    private record ChatMessage(String role, String content) {}
}
```

## Best Practices

1. **Model Selection**: Choose the right model for your use case
   - Claude: Best for complex reasoning and analysis
   - Llama: Open source, good for general tasks
   - Titan: AWS native, cost-effective

2. **Cost Optimization**:
   - Cache foundation model lists
   - Reuse client instances
   - Use appropriate max_tokens limits
   - Monitor usage with CloudWatch

3. **Error Handling**:
   - Implement retry logic for throttling
   - Handle model-specific errors
   - Validate responses before processing

4. **Security**:
   - Never log sensitive prompt data
   - Use IAM roles for authentication
   - Implement rate limiting
   - Sanitize user inputs

5. **Performance**:
   - Use async clients for I/O operations
   - Implement streaming for long responses
   - Cache embeddings when possible
   - Use connection pooling

## Common Model IDs

```java
public static final class BedrockModels {
    // Claude Models
    public static final String CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0";
    public static final String CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0";
    public static final String CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0";
    
    // Llama Models
    public static final String LLAMA_3_70B = "meta.llama3-70b-instruct-v1:0";
    public static final String LLAMA_3_8B = "meta.llama3-8b-instruct-v1:0";
    
    // Amazon Titan Models
    public static final String TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1";
    public static final String TITAN_TEXT_LITE = "amazon.titan-text-lite-v1";
    public static final String TITAN_EMBEDDINGS = "amazon.titan-embed-text-v1";
    public static final String TITAN_IMAGE_GENERATOR = "amazon.titan-image-generator-v1";
    
    // Stable Diffusion
    public static final String STABLE_DIFFUSION_XL = "stability.stable-diffusion-xl-v1";
    
    // Cohere
    public static final String COHERE_COMMAND = "cohere.command-text-v14";
    
    // Mistral
    public static final String MISTRAL_7B = "mistral.mistral-7b-instruct-v0:2";
    public static final String MIXTRAL_8X7B = "mistral.mixtral-8x7b-instruct-v0:1";
}
```

## Testing

### Unit Test with Mocked Client

```java
@ExtendWith(MockitoExtension.class)
class BedrockAIServiceTest {
    
    @Mock
    private BedrockRuntimeClient bedrockRuntimeClient;
    
    @InjectMocks
    private BedrockAIService aiService;
    
    @Test
    void shouldGenerateText() {
        String expectedResponse = "Generated text";
        
        InvokeModelResponse mockResponse = InvokeModelResponse.builder()
            .body(SdkBytes.fromUtf8String(
                "{\"content\":[{\"text\":\"" + expectedResponse + "\"}]}"))
            .build();
        
        when(bedrockRuntimeClient.invokeModel(any(InvokeModelRequest.class)))
            .thenReturn(mockResponse);
        
        String result = aiService.generateText("test prompt");
        
        assertThat(result).isEqualTo(expectedResponse);
    }
}
```

## Related Skills

- @aws-sdk-java-v2-core - Core AWS SDK patterns
- @langchain4j-ai-services-patterns - LangChain4j integration
- @spring-boot-dependency-injection - Spring DI patterns

## References

- [Bedrock Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/bedrock-runtime)
- [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [Foundation Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [Bedrock API Reference](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/bedrockruntime/package-summary.html)
