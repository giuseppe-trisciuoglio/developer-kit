# Testing Lambda Services

## Unit Testing with Mocks

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import software.amazon.awssdk.services.lambda.LambdaClient;
import software.amazon.awssdk.services.lambda.model.InvokeResponse;
import software.amazon.awssdk.core.SdkBytes;

import static org.mockito.Mockito.*;
import static org.assertj.core.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class LambdaInvokerServiceTest {

    @Mock
    private LambdaClient lambdaClient;

    @Mock
    private ObjectMapper objectMapper;

    @InjectMocks
    private LambdaInvokerService service;

    @Test
    void shouldInvokeLambdaSuccessfully() throws Exception {
        // Arrange
        String functionName = "test-function";
        OrderRequest request = new OrderRequest("123", List.of());

        String jsonPayload = "{\"orderId\":\"123\",\"items\":[]}";
        String jsonResponse = "{\"status\":\"SUCCESS\"}";

        when(objectMapper.writeValueAsString(request)).thenReturn(jsonPayload);
        when(objectMapper.readValue(jsonResponse, OrderResponse.class))
            .thenReturn(new OrderResponse("SUCCESS"));

        InvokeResponse invokeResponse = InvokeResponse.builder()
            .statusCode(200)
            .payload(SdkBytes.fromUtf8String(jsonResponse))
            .build();

        when(lambdaClient.invoke(any(InvokeRequest.class))).thenReturn(invokeResponse);

        // Act
        OrderResponse response = service.invoke(functionName, request, OrderResponse.class);

        // Assert
        assertThat(response.getStatus()).isEqualTo("SUCCESS");

        InvokeRequest expectedRequest = InvokeRequest.builder()
            .functionName(functionName)
            .payload(SdkBytes.fromUtf8String(jsonPayload))
            .build();

        verify(lambdaClient).invoke(expectedRequest);
    }

    @Test
    void shouldHandleLambdaFunctionError() throws Exception {
        // Arrange
        String functionName = "test-function";
        OrderRequest request = new OrderRequest("123", List.of());
        String jsonPayload = "{\"orderId\":\"123\",\"items\":[]}";
        String errorResponse = "{\"error\":\"Invalid input\"}";

        when(objectMapper.writeValueAsString(request)).thenReturn(jsonPayload);

        InvokeResponse invokeResponse = InvokeResponse.builder()
            .statusCode(200)
            .functionError("Unhandled")
            .payload(SdkBytes.fromUtf8String(errorResponse))
            .build();

        when(lambdaClient.invoke(any(InvokeRequest.class))).thenReturn(invokeResponse);

        // Act & Assert
        assertThatThrownBy(() -> service.invoke(functionName, request, OrderResponse.class))
            .isInstanceOf(LambdaInvocationException.class)
            .hasMessageContaining("Lambda function error");
    }

    @Test
    void shouldHandleServiceException() {
        // Arrange
        String functionName = "test-function";
        OrderRequest request = new OrderRequest("123", List.of());

        when(lambdaClient.invoke(any(InvokeRequest.class)))
            .thenThrow(new LambdaException("Service unavailable"));

        // Act & Assert
        assertThatThrownBy(() -> service.invoke(functionName, request, OrderResponse.class))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Failed to invoke Lambda function");
    }
}
```

## Integration Testing

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
class LambdaInvokerServiceIntegrationTest {

    @Autowired
    private LambdaInvokerService lambdaInvoker;

    @Test
    void shouldInvokeRealLambdaFunction() {
        // Arrange
        String functionName = "test-function";
        TestRequest request = new TestRequest("test-data");

        // Act
        TestResponse response = lambdaInvoker.invoke(functionName, request, TestResponse.class);

        // Assert
        assertThat(response).isNotNull();
        assertThat(response.getStatus()).isEqualTo("SUCCESS");
    }
}
```

## Testing with LocalStack

```java
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.lambda.LambdaClient;

@SpringBootTest
@Testcontainers
class LambdaLocalStackTest {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:latest"))
        .withServices(LocalStackContainer.Service.LAMBDA);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("aws.endpoint", localstack::getEndpoint);
        registry.add("aws.region", () -> "us-east-1");
    }

    @Bean
    public LambdaClient lambdaClient() {
        return LambdaClient.builder()
            .endpointOverride(URI.create(localstack.getEndpoint()))
            .region(Region.US_EAST_1)
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create("test", "test")))
            .build();
    }
}
```

## Testing Async Invocations

```java
@ExtendWith(MockitoExtension.class)
class AsyncLambdaServiceTest {

    @Mock
    private LambdaAsyncClient asyncClient;

    @InjectMocks
    private AsyncLambdaService asyncService;

    @Test
    void shouldInvokeLambdaAsync() throws Exception {
        // Arrange
        String functionName = "test-function";
        String payload = "{\"test\":\"data\"}";

        CompletableFuture<InvokeResponse> future = CompletableFuture.completedFuture(
            InvokeResponse.builder()
                .statusCode(202)
                .payload(SdkBytes.fromUtf8String("{\"status\":\"accepted\"}"))
                .build()
        );

        when(asyncClient.invoke(any(InvokeRequest.class))).thenReturn(future);

        // Act
        CompletableFuture<String> result = asyncService.invokeAsync(functionName, payload);

        // Assert
        assertThat(result.get()).contains("accepted");
    }
}
```

## Testing Error Scenarios

```java
@Test
void shouldHandleTimeout() {
    // Arrange
    when(lambdaClient.invoke(any(InvokeRequest.class)))
        .thenAnswer(invocation -> {
            Thread.sleep(5000); // Simulate timeout
            return InvokeResponse.builder().build();
        });

    // Act & Assert
    assertThatThrownBy(() -> service.invoke("function", request, Response.class))
        .isInstanceOf(RuntimeException.class);
}

@Test
void shouldRetryOnTransientFailure() {
    // Arrange
    when(lambdaClient.invoke(any(InvokeRequest.class)))
        .thenThrow(new LambdaException("Service unavailable"))
        .thenReturn(InvokeResponse.builder()
            .statusCode(200)
            .payload(SdkBytes.fromUtf8String("{\"status\":\"ok\"}"))
            .build());

    // Act
    Response response = service.invokeWithRetry("function", request, Response.class, 3);

    // Assert
    assertThat(response.getStatus()).isEqualTo("ok");
    verify(lambdaClient, times(2)).invoke(any(InvokeRequest.class));
}
```

## Test Fixtures

```java
class LambdaTestFixture {
    public static InvokeResponse successResponse(String payload) {
        return InvokeResponse.builder()
            .statusCode(200)
            .payload(SdkBytes.fromUtf8String(payload))
            .build();
    }

    public static InvokeResponse errorResponse(String error) {
        return InvokeResponse.builder()
            .statusCode(200)
            .functionError("Handled")
            .payload(SdkBytes.fromUtf8String("{\"error\":\"" + error + "\"}"))
            .build();
    }

    public static InvokeRequest invokeRequest(String functionName, String payload) {
        return InvokeRequest.builder()
            .functionName(functionName)
            .payload(SdkBytes.fromUtf8String(payload))
            .build();
    }
}
```
