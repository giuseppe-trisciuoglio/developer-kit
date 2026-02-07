# Testing Strategies

## Unit Testing

### Mocking Bedrock Clients

```java
@ExtendWith(MockitoExtension.class)
class BedrockServiceTest {

    @Mock
    private BedrockRuntimeClient bedrockRuntimeClient;

    @InjectMocks
    private BedrockAIService aiService;

    @Test
    void shouldGenerateTextWithClaude() {
        // Arrange
        String modelId = "anthropic.claude-3-sonnet-20240229-v1:0";
        String prompt = "Hello, world!";
        String expectedResponse = "Hello! How can I help you today?";

        InvokeModelResponse mockResponse = InvokeModelResponse.builder()
            .body(SdkBytes.fromUtf8String(
                "{\"content\":[{\"text\":\"" + expectedResponse + "\"}]}"))
            .build();

        when(bedrockRuntimeClient.invokeModel(any(InvokeModelRequest.class)))
            .thenReturn(mockResponse);

        // Act
        String result = aiService.generateText(prompt, modelId);

        // Assert
        assertThat(result).isEqualTo(expectedResponse);
        verify(bedrockRuntimeClient).invokeModel(argThat(request ->
            request.modelId().equals(modelId)));
    }

    @Test
    void shouldHandleThrottling() {
        // Arrange
        when(bedrockRuntimeClient.invokeModel(any(InvokeModelRequest.class)))
            .thenThrow(ThrottlingException.builder()
                .message("Rate limit exceeded")
                .build());

        // Act & Assert
        assertThatThrownBy(() -> aiService.generateText("test"))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Rate limit exceeded");
    }
}
```

### Testing Error Conditions

```java
@Test
void shouldHandleInvalidModelId() {
    String invalidModelId = "invalid.model.id";
    String prompt = "test";

    when(bedrockRuntimeClient.invokeModel(any(InvokeModelRequest.class)))
        .thenThrow(ValidationException.builder()
            .message("Invalid model identifier")
            .build());

    assertThatThrownBy(() -> aiService.generateText(prompt, invalidModelId))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("Invalid model identifier");
}
```

### Testing Multiple Models

```java
@ParameterizedTest
@EnumSource(ModelProvider.class)
void shouldSupportAllModels(ModelProvider modelProvider) {
    String prompt = "Hello";
    String modelId = modelProvider.getModelId();
    String expectedResponse = "Response";

    InvokeModelResponse mockResponse = InvokeModelResponse.builder()
        .body(SdkBytes.fromUtf8String(createMockResponse(modelProvider, expectedResponse)))
        .build();

    when(bedrockRuntimeClient.invokeModel(any(InvokeModelRequest.class)))
        .thenReturn(mockResponse);

    String result = aiService.generateText(prompt, modelId);

    assertThat(result).isEqualTo(expectedResponse);
}

private enum ModelProvider {
    CLAUDE("anthropic.claude-3-sonnet-20240229-v1:0"),
    LLAMA("meta.llama3-70b-instruct-v1:0"),
    TITAN("amazon.titan-text-express-v1");

    private final String modelId;

    ModelProvider(String modelId) {
        this.modelId = modelId;
    }

    public String getModelId() {
        return modelId;
    }
}
```

## Integration Testing

### Testcontainers Integration

```java
@Testcontainers
@SpringBootTest(classes = BedrockConfiguration.class)
@ActiveProfiles("test")
class BedrockIntegrationTest {

    @Container
    static LocalStackContainer localStack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:latest"))
        .withServices(AWSService BEDROCK_RUNTIME)
        .withEnv("DEFAULT_REGION", "us-east-1");

    @Autowired
    private BedrockRuntimeClient bedrockRuntimeClient;

    @Test
    void shouldConnectToLocalStack() {
        assertThat(bedrockRuntimeClient).isNotNull();
    }

    @Test
    void shouldListFoundationModels() {
        ListFoundationModelsResponse response =
            bedrockRuntimeClient.listFoundationModels();

        assertThat(response.modelSummaries()).isNotEmpty();
    }
}
```

### LocalStack Configuration

```java
@Configuration
public class LocalStackConfig {

    @Value("${localstack.enabled:true}")
    private boolean localStackEnabled;

    @Bean
    @ConditionalOnProperty(name = "localstack.enabled", havingValue = "true")
    public AwsCredentialsProvider localStackCredentialsProvider() {
        return StaticCredentialsProvider.create(
            new AwsBasicCredentialsAccessKey("test", "test"));
    }

    @Bean
    @ConditionalOnProperty(name = "localstack.enabled", havingValue = "true")
    public BedrockRuntimeClient localStackBedrockRuntimeClient(
            AwsCredentialsProvider credentialsProvider) {

        return BedrockRuntimeClient.builder()
            .credentialsProvider(credentialsProvider)
            .endpointOverride(localStack.getEndpoint())
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### Performance Testing

```java
@Test
void shouldPerformWithinTimeLimit() {
    String prompt = "Performance test prompt";
    int iterationCount = 100;

    long startTime = System.currentTimeMillis();

    for (int i = 0; i < iterationCount; i++) {
        InvokeModelResponse response = bedrockRuntimeClient.invokeModel(
            request -> request
                .modelId("anthropic.claude-3-sonnet-20240229-v1:0")
                .body(SdkBytes.fromUtf8String(createPayload(prompt))));
    }

    long duration = System.currentTimeMillis() - startTime;
    double avgTimePerRequest = (double) duration / iterationCount;

    assertThat(avgTimePerRequest).isLessThan(5000); // Less than 5 seconds per request
    System.out.println("Average response time: " + avgTimePerRequest + "ms");
}
```

## Testing Streaming Responses

### Streaming Handler Testing

```java
@Test
void shouldStreamResponse() throws InterruptedException {
    String prompt = "Stream this response";

    MockStreamHandler mockHandler = new MockStreamHandler();

    InvokeModelWithResponseStreamRequest streamRequest =
        InvokeModelWithResponseStreamRequest.builder()
            .modelId("anthropic.claude-3-sonnet-20240229-v1:0")
            .body(SdkBytes.fromUtf8String(createPayload(prompt)))
            .build();

    bedrockRuntimeClient.invokeModelWithResponseStream(streamRequest, mockHandler);

    // Wait for streaming to complete
    mockHandler.awaitCompletion(10, TimeUnit.SECONDS);

    assertThat(mockHandler.getStreamedContent()).isNotEmpty();
    assertThat(mockHandler.getStreamedContent()).contains(" streamed");
}

private static class MockStreamHandler extends
    InvokeModelWithResponseStreamResponseHandler.Visitor {

    private final StringBuilder contentBuilder = new StringBuilder();
    private final CountDownLatch latch = new CountDownLatch(1);

    @Override
    public void visit(EventStream eventStream) {
        eventStream.forEach(event -> {
            if (event instanceof PayloadPart) {
                PayloadPart payloadPart = (PayloadPart) event;
                String chunk = payloadPart.bytes().asUtf8String();
                contentBuilder.append(chunk);
            }
        });
        latch.countDown();
    }

    public String getStreamedContent() {
        return contentBuilder.toString();
    }

    public void awaitCompletion(long timeout, TimeUnit unit)
        throws InterruptedException {
        latch.await(timeout, unit);
    }
}
```

## Testing Configuration

### Testing Different Regions

```java
@ParameterizedTest
@EnumSource(value = Region.class,
    names = {"US_EAST_1", "US_WEST_2", "EU_WEST_1"})
void shouldWorkInAllRegions(Region region) {
    BedrockRuntimeClient client = BedrockRuntimeClient.builder()
        .region(region)
        .build();

    assertThat(client).isNotNull();
}

### Testing Authentication

```java
@Test
void shouldUseIamRoleForAuthentication() {
    BedrockRuntimeClient client = BedrockRuntimeClient.builder()
        .region(Region.US_EAST_1)
        .build();

    // Test that client can make basic calls
    ListFoundationModelsResponse response = client.listFoundationModels();

    assertThat(response).isNotNull();
}
```

## Test Data Management

### Test Response Fixtures

```java
public class BedrockTestFixtures {

    public static String createClaudeResponse() {
        return "{\"content\":[{\"text\":\"Hello! How can I help you today?\"}]}";
    }

    public static String createLlamaResponse() {
        return "{\"generation\":\"Hello! How can I assist you?\"}";
    }

    public static String createTitanResponse() {
        return "{\"results\":[{\"outputText\":\"Hello! How can I help?\"}]}";
    }

    public static String createPayload(String prompt) {
        return new JSONObject()
            .put("anthropic_version", "bedrock-2023-05-31")
            .put("max_tokens", 1000)
            .put("messages", new JSONObject[]{
                new JSONObject()
                    .put("role", "user")
                    .put("content", prompt)
            })
            .toString();
    }
}
```

### Integration Test Suite

```java
@Suite
@SelectClasses({
    BedrockAIServiceTest.class,
    BedrockConfigurationTest.class,
    BedrockStreamingTest.class,
    BedrockErrorHandlingTest.class
})
public class BedrockTestSuite {
    // Integration test suite for all Bedrock functionality
}
```

## Testing Guidelines

### Unit Testing Best Practices

1. **Mock External Dependencies:** Always mock AWS SDK clients in unit tests
2. **Test Error Scenarios:** Include tests for throttling, validation errors, and network issues
3. **Parameterized Tests:** Test multiple models and configurations efficiently
4. **Performance Assertions:** Include basic performance benchmarks
5. **Test Data Fixtures:** Reuse test response data across tests

### Integration Testing Best Practices

1. **Use LocalStack:** Test against LocalStack for local development
2. **Test Multiple Regions:** Verify functionality across different AWS regions
3. **Test Edge Cases:** Include timeout, retry, and concurrent request scenarios
4. **Monitor Performance:** Track response times and error rates
5. **Clean Up Resources:** Ensure proper cleanup after integration tests

### Testing Configuration

```properties
# application-test.properties
localstack.enabled=true
aws.region=us-east-1
bedrock.timeout=5000
bedrock.retry.max-attempts=3
```