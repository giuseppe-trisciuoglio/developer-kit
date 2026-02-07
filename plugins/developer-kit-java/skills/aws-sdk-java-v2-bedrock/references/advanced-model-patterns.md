# Advanced Model Patterns

## Model-Specific Configuration

### Claude Models Configuration

```java
// Claude 3 Sonnet
public String invokeClaude3Sonnet(BedrockRuntimeClient client, String prompt) {
    String modelId = "anthropic.claude-3-sonnet-20240229-v1:0";

    JSONObject payload = new JSONObject()
        .put("anthropic_version", "bedrock-2023-05-31")
        .put("max_tokens", 1000)
        .put("temperature", 0.7)
        .put("top_p", 1.0)
        .put("messages", new JSONObject[]{
            new JSONObject()
                .put("role", "user")
                .put("content", prompt)
        });

    InvokeModelResponse response = client.invokeModel(request -> request
        .modelId(modelId)
        .body(SdkBytes.fromUtf8String(payload.toString())));

    JSONObject responseBody = new JSONObject(response.body().asUtf8String());
    return responseBody.getJSONArray("content")
        .getJSONObject(0)
        .getString("text");
}

// Claude 3 Haiku (faster, cheaper)
public String invokeClaude3Haiku(BedrockRuntimeClient client, String prompt) {
    String modelId = "anthropic.claude-3-haiku-20240307-v1:0";

    JSONObject payload = new JSONObject()
        .put("anthropic_version", "bedrock-2023-05-31")
        .put("max_tokens", 400)
        .put("messages", new JSONObject[]{
            new JSONObject()
                .put("role", "user")
                .put("content", prompt)
        });

    // Similar invocation pattern as above
}
```

### Llama Models Configuration

```java
// Llama 3 70B
public String invokeLlama3_70B(BedrockRuntimeClient client, String prompt) {
    String modelId = "meta.llama3-70b-instruct-v1:0";

    JSONObject payload = new JSONObject()
        .put("prompt", prompt)
        .put("max_gen_len", 512)
        .put("temperature", 0.7)
        .put("top_p", 0.9)
        .put("stop", new String[]{"[INST]", "[/INST]"}); // Custom stop tokens

    InvokeModelResponse response = client.invokeModel(request -> request
        .modelId(modelId)
        .body(SdkBytes.fromUtf8String(payload.toString())));

    JSONObject responseBody = new JSONObject(response.body().asUtf8String());
    return responseBody.getString("generation");
}
```

## Multi-Model Service Layer

```java
@Service
public class MultiModelService {

    private final BedrockRuntimeClient bedrockRuntimeClient;
    private final ObjectMapper objectMapper;

    public MultiModelService(BedrockRuntimeClient bedrockRuntimeClient,
                           ObjectMapper objectMapper) {
        this.bedrockRuntimeClient = bedrockRuntimeClient;
        this.objectMapper = objectMapper;
    }

    public String invokeModel(String modelId, String prompt, Map<String, Object> additionalParams) {
        Map<String, Object> payload = createModelPayload(modelId, prompt, additionalParams);

        try {
            InvokeModelResponse response = bedrockRuntimeClient.invokeModel(
                request -> request
                    .modelId(modelId)
                    .body(SdkBytes.fromUtf8String(objectMapper.writeValueAsString(payload))));

            return extractResponseContent(modelId, response.body().asUtf8String());

        } catch (Exception e) {
            throw new RuntimeException("Model invocation failed: " + e.getMessage(), e);
        }
    }

    private Map<String, Object> createModelPayload(String modelId, String prompt,
                                                   Map<String, Object> additionalParams) {
        Map<String, Object> payload = new HashMap<>();

        if (modelId.startsWith("anthropic.claude")) {
            payload.put("anthropic_version", "bedrock-2023-05-31");
            payload.put("messages", List.of(Map.of("role", "user", "content", prompt)));

            // Add common parameters with defaults
            payload.putIfAbsent("max_tokens", 1000);
            payload.putIfAbsent("temperature", 0.7);

        } else if (modelId.startsWith("meta.llama")) {
            payload.put("prompt", prompt);
            payload.putIfAbsent("max_gen_len", 512);
            payload.putIfAbsent("temperature", 0.7);

        } else if (modelId.startsWith("amazon.titan")) {
            payload.put("inputText", prompt);
            payload.putIfAbsent("textGenerationConfig",
                Map.of("maxTokenCount", 512, "temperature", 0.7));
        }

        // Add additional parameters
        if (additionalParams != null) {
            payload.putAll(additionalParams);
        }

        return payload;
    }
}
```

## Advanced Error Handling

```java
@Component
public class BedrockErrorHandler {

    @Retryable(value = {SdkClientException.class}, maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public String invokeWithRetry(BedrockRuntimeClient client, String modelId,
                                String payloadJson) {
        try {
            InvokeModelResponse response = client.invokeModel(request -> request
                .modelId(modelId)
                .body(SdkBytes.fromUtf8String(payloadJson)));
            return response.body().asUtf8String();

        } catch (ThrottlingException e) {
            // Exponential backoff for throttling
            throw new RuntimeException("Rate limit exceeded, please try again later", e);
        } catch (ValidationException e) {
            throw new IllegalArgumentException("Invalid request: " + e.getMessage(), e);
        } catch (SdkException e) {
            throw new RuntimeException("AWS SDK error: " + e.getMessage(), e);
        }
    }
}
```

## Batch Processing

```java
@Service
public class BedrockBatchService {

    public List<String> processBatch(BedrockRuntimeClient client, String modelId,
                                    List<String> prompts) {
        return prompts.parallelStream()
            .map(prompt -> invokeModelWithTimeout(client, modelId, prompt, 30))
            .collect(Collectors.toList());
    }

    private String invokeModelWithTimeout(BedrockRuntimeClient client, String modelId,
                                         String prompt, int timeoutSeconds) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<String> future = executor.submit(() -> {
            JSONObject payload = new JSONObject()
                .put("prompt", prompt)
                .put("max_tokens", 500);

            InvokeModelResponse response = client.invokeModel(request -> request
                .modelId(modelId)
                .body(SdkBytes.fromUtf8String(payload.toString())));

            return response.body().asUtf8String();
        });

        try {
            return future.get(timeoutSeconds, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            future.cancel(true);
            throw new RuntimeException("Model invocation timed out");
        } catch (Exception e) {
            throw new RuntimeException("Batch processing error", e);
        } finally {
            executor.shutdown();
        }
    }
}
```

## Model Performance Optimization

```java
@Configuration
public class BedrockOptimizationConfig {

    @Bean
    public BedrockRuntimeClient optimizedBedrockRuntimeClient() {
        return BedrockRuntimeClient.builder()
            .region(Region.US_EAST_1)
            .overrideConfiguration(ClientOverrideConfiguration.builder()
                .apiCallTimeout(Duration.ofSeconds(30))
                .apiCallAttemptTimeout(Duration.ofSeconds(20))
                .build())
            .httpClient(ApacheHttpClient.builder()
                .connectionTimeout(Duration.ofSeconds(10))
                .socketTimeout(Duration.ofSeconds(30))
                .build())
            .build();
    }
}
```

## Custom Response Parsing

```java
public class BedrockResponseParser {

    public static TextResponse parseTextResponse(String modelId, String responseBody) {
        try {
            switch (getModelProvider(modelId)) {
                case ANTHROPIC:
                    return parseAnthropicResponse(responseBody);
                case META:
                    return parseMetaResponse(responseBody);
                case AMAZON:
                    return parseAmazonResponse(responseBody);
                default:
                    throw new IllegalArgumentException("Unsupported model: " + modelId);
            }
        } catch (Exception e) {
            throw new ResponseParsingException("Failed to parse response for model: " + modelId, e);
        }
    }

    private static TextResponse parseAnthropicResponse(String responseBody) throws JSONException {
        JSONObject json = new JSONObject(responseBody);
        JSONArray content = json.getJSONArray("content");
        String text = content.getJSONObject(0).getString("text");
        int usage = json.getJSONObject("usage").getInt("input_tokens");

        return new TextResponse(text, usage, "anthropic");
    }

    private static TextResponse parseMetaResponse(String responseBody) throws JSONException {
        JSONObject json = new JSONObject(responseBody);
        String text = json.getString("generation");
        // Note: Meta doesn't provide token usage in basic response

        return new TextResponse(text, 0, "meta");
    }

    private enum ModelProvider {
        ANTHROPIC, META, AMAZON
    }

    public record TextResponse(String content, int tokensUsed, String provider) {}
}
```