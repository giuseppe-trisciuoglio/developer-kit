# AWS Lambda Java SDK Examples

## Client Setup

### Basic Client Configuration
```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.lambda.LambdaClient;

// Create synchronous client
LambdaClient lambdaClient = LambdaClient.builder()
    .region(Region.US_EAST_1)
    .build();

// Create asynchronous client
LambdaAsyncClient asyncLambdaClient = LambdaAsyncClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Client with Configuration
```java
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.http.nio.netty.NettyNioHttpServer;

LambdaClient lambdaClient = LambdaClient.builder()
    .region(Region.US_EAST_1)
    .credentialsProvider(DefaultCredentialsProvider.create())
    .httpClientBuilder(NettyNioHttpServer.builder())
    .build();
```

## Function Invocation Examples

### Synchronous Invocation with String Payload
```java
import software.amazon.awssdk.services.lambda.model.*;
import software.amazon.awssdk.core.SdkBytes;

public String invokeLambdaSync(LambdaClient lambdaClient,
                              String functionName,
                              String payload) {
    InvokeRequest request = InvokeRequest.builder()
        .functionName(functionName)
        .payload(SdkBytes.fromUtf8String(payload))
        .build();

    InvokeResponse response = lambdaClient.invoke(request);

    // Check for function errors
    if (response.functionError() != null) {
        throw new RuntimeException("Lambda function error: " +
            response.payload().asUtf8String());
    }

    return response.payload().asUtf8String();
}
```

### Asynchronous Invocation
```java
import java.util.concurrent.CompletableFuture;

public CompletableFuture<String> invokeLambdaAsync(LambdaClient lambdaClient,
                                                   String functionName,
                                                   String payload) {
    InvokeRequest request = InvokeRequest.builder()
        .functionName(functionName)
        .invocationType(InvocationType.EVENT) // Asynchronous
        .payload(SdkBytes.fromUtf8String(payload))
        .build();

    return lambdaClient.invoke(request)
        .thenApply(response -> response.payload().asUtf8String());
}
```

### Invocation with JSON Object
```java
import com.fasterxml.jackson.databind.ObjectMapper;

public <T> String invokeLambdaWithObject(LambdaClient lambdaClient,
                                        String functionName,
                                        T requestObject) throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    String jsonPayload = mapper.writeValueAsString(requestObject);

    InvokeRequest request = InvokeRequest.builder()
        .functionName(functionName)
        .payload(SdkBytes.fromUtf8String(jsonPayload))
        .build();

    InvokeResponse response = lambdaClient.invoke(request);

    return response.payload().asUtf8String();
}
```

### Parse Typed Response
```java
import com.fasterxml.jackson.databind.ObjectMapper;

public <T> T invokeLambdaAndParse(LambdaClient lambdaClient,
                                String functionName,
                                Object request,
                                Class<T> responseType) throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    String jsonPayload = mapper.writeValueAsString(request);

    InvokeRequest invokeRequest = InvokeRequest.builder()
        .functionName(functionName)
        .payload(SdkBytes.fromUtf8String(jsonPayload))
        .build();

    InvokeResponse response = lambdaClient.invoke(invokeRequest);
    String responseJson = response.payload().asUtf8String();

    return mapper.readValue(responseJson, responseType);
}
```

## Function Management Examples

### List Functions
```java
public List<FunctionConfiguration> listLambdaFunctions(LambdaClient lambdaClient) {
    ListFunctionsResponse response = lambdaClient.listFunctions();
    return response.functions();
}

// List functions with pagination
public List<FunctionConfiguration> listAllFunctions(LambdaClient lambdaClient) {
    ListFunctionsRequest request = ListFunctionsRequest.builder().build();
    ListFunctionsResponse response = lambdaClient.listFunctions(request);

    return response.functions();
}
```

### Get Function Configuration
```java
public FunctionConfiguration getFunctionConfig(LambdaClient lambdaClient,
                                             String functionName) {
    GetFunctionRequest request = GetFunctionRequest.builder()
        .functionName(functionName)
        .build();

    GetFunctionResponse response = lambdaClient.getFunction(request);
    return response.configuration();
}
```

### Get Function Code
```java
public byte[] getFunctionCode(LambdaClient lambdaClient,
                             String functionName) {
    GetFunctionRequest request = GetFunctionRequest.builder()
        .functionName(functionName)
        .build();

    GetFunctionResponse response = lambdaClient.getFunction(request);
    return response.code().zipFile().asByteArray();
}
```

### Update Function Code
```java
import java.nio.file.Files;
import java.nio.file.Paths;

public void updateLambdaFunction(LambdaClient lambdaClient,
                                String functionName,
                                String zipFilePath) throws IOException {
    byte[] zipBytes = Files.readAllBytes(Paths.get(zipFilePath));

    UpdateFunctionCodeRequest request = UpdateFunctionCodeRequest.builder()
        .functionName(functionName)
        .zipFile(SdkBytes.fromByteArray(zipBytes))
        .publish(true) // Create new version
        .build();

    UpdateFunctionCodeResponse response = lambdaClient.updateFunctionCode(request);
    System.out.println("Updated function version: " + response.version());
}
```

### Update Function Configuration
```java
public void updateFunctionConfig(LambdaClient lambdaClient,
                                String functionName,
                                Map<String, String> environment) {
    Environment env = Environment.builder()
        .variables(environment)
        .build();

    UpdateFunctionConfigurationRequest request = UpdateFunctionConfigurationRequest.builder()
        .functionName(functionName)
        .environment(env)
        .timeout(60)
        .memorySize(512)
        .build();

    lambdaClient.updateFunctionConfiguration(request);
}
```

### Create Function
```java
import java.nio.file.Files;
import java.nio.file.Paths;

public void createLambdaFunction(LambdaClient lambdaClient,
                                String functionName,
                                String roleArn,
                                String handler,
                                String zipFilePath) throws IOException {
    byte[] zipBytes = Files.readAllBytes(Paths.get(zipFilePath));

    FunctionCode code = FunctionCode.builder()
        .zipFile(SdkBytes.fromByteArray(zipBytes))
        .build();

    CreateFunctionRequest request = CreateFunctionRequest.builder()
        .functionName(functionName)
        .runtime(Runtime.JAVA17)
        .role(roleArn)
        .handler(handler)
        .code(code)
        .timeout(60)
        .memorySize(512)
        .environment(Environment.builder()
            .variables(Map.of("ENV", "production"))
            .build())
        .build();

    CreateFunctionResponse response = lambdaClient.createFunction(request);
    System.out.println("Function ARN: " + response.functionArn());
}
```

### Delete Function
```java
public void deleteLambdaFunction(LambdaClient lambdaClient, String functionName) {
    DeleteFunctionRequest request = DeleteFunctionRequest.builder()
        .functionName(functionName)
        .build();

    lambdaClient.deleteFunction(request);
}
```

## Spring Boot Integration Examples

### Configuration Class
```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class LambdaConfiguration {

    @Bean
    public LambdaClient lambdaClient() {
        return LambdaClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public LambdaAsyncClient asyncLambdaClient() {
        return LambdaAsyncClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### Lambda Invoker Service
```java
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class LambdaInvokerService {

    private final LambdaClient lambdaClient;
    private final ObjectMapper objectMapper;

    @Autowired
    public LambdaInvokerService(LambdaClient lambdaClient,
                               ObjectMapper objectMapper) {
        this.lambdaClient = lambdaClient;
        this.objectMapper = objectMapper;
    }

    public <T, R> R invokeFunction(String functionName,
                                   T request,
                                   Class<R> responseType) {
        try {
            String jsonPayload = objectMapper.writeValueAsString(request);

            InvokeRequest invokeRequest = InvokeRequest.builder()
                .functionName(functionName)
                .payload(SdkBytes.fromUtf8String(jsonPayload))
                .build();

            InvokeResponse response = lambdaClient.invoke(invokeRequest);

            if (response.functionError() != null) {
                throw new LambdaInvocationException(
                    "Lambda function error: " + response.functionError());
            }

            String responseJson = response.payload().asUtf8String();
            return objectMapper.readValue(responseJson, responseType);

        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke Lambda function", e);
        }
    }

    public void invokeFunctionAsync(String functionName, Object request) {
        try {
            String jsonPayload = objectMapper.writeValueAsString(request);

            InvokeRequest invokeRequest = InvokeRequest.builder()
                .functionName(functionName)
                .invocationType(InvocationType.EVENT)
                .payload(SdkBytes.fromUtf8String(jsonPayload))
                .build();

            lambdaClient.invoke(invokeRequest);

        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke Lambda function async", e);
        }
    }
}
```

### Typed Lambda Client Interface
```java
public interface OrderProcessor {
    OrderResponse processOrder(OrderRequest request);
    CompletableFuture<OrderResponse> processOrderAsync(OrderRequest request);
}

@Service
public class LambdaOrderProcessor implements OrderProcessor {

    private final LambdaInvokerService lambdaInvoker;
    private final LambdaAsyncClient asyncLambdaClient;

    @Value("${lambda.order-processor.function-name}")
    private String functionName;

    public LambdaOrderProcessor(LambdaInvokerService lambdaInvoker,
                               LambdaAsyncClient asyncLambdaClient) {
        this.lambdaInvoker = lambdaInvoker;
        this.asyncLambdaClient = asyncLambdaClient;
    }

    @Override
    public OrderResponse processOrder(OrderRequest request) {
        return lambdaInvoker.invoke(functionName, request, OrderResponse.class);
    }

    @Override
    public CompletableFuture<OrderResponse> processOrderAsync(OrderRequest request) {
        // Implement async invocation using async client
        try {
            String jsonPayload = new ObjectMapper().writeValueAsString(request);

            InvokeRequest invokeRequest = InvokeRequest.builder()
                .functionName(functionName)
                .payload(SdkBytes.fromUtf8String(jsonPayload))
                .build();

            return asyncLambdaClient.invoke(invokeRequest)
                .thenApply(response -> {
                    try {
                        return new ObjectMapper().readValue(
                            response.payload().asUtf8String(),
                            OrderResponse.class);
                    } catch (Exception e) {
                        throw new RuntimeException("Failed to parse response", e);
                    }
                });

        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke Lambda function", e);
        }
    }
}
```

## Error Handling Examples

### Comprehensive Error Handling
```java
public String invokeLambdaWithFullErrorHandling(LambdaClient lambdaClient,
                                               String functionName,
                                               String payload) {
    try {
        InvokeRequest request = InvokeRequest.builder()
            .functionName(functionName)
            .payload(SdkBytes.fromUtf8String(payload))
            .build();

        InvokeResponse response = lambdaClient.invoke(request);

        // Check for function error
        if (response.functionError() != null) {
            String errorMessage = response.payload().asUtf8String();
            throw new LambdaInvocationException(
                "Lambda function error: " + errorMessage);
        }

        // Check status code
        if (response.statusCode() != 200) {
            throw new LambdaInvocationException(
                "Lambda invocation failed with status: " + response.statusCode());
        }

        return response.payload().asUtf8String();

    } catch (LambdaException e) {
        System.err.println("AWS Lambda error: " + e.awsErrorDetails().errorMessage());
        throw new LambdaInvocationException(
            "AWS Lambda service error: " + e.awsErrorDetails().errorMessage(), e);
    }
}

public class LambdaInvocationException extends RuntimeException {
    public LambdaInvocationException(String message) {
        super(message);
    }

    public LambdaInvocationException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

## Testing Examples

### Unit Test for Lambda Service
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
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
        // Given
        OrderRequest request = new OrderRequest("ORDER-123");
        OrderResponse expectedResponse = new OrderResponse("SUCCESS");
        String jsonPayload = "{\"orderId\":\"ORDER-123\"};
        String jsonResponse = "{\"status\":\"SUCCESS\"};

        when(objectMapper.writeValueAsString(request))
            .thenReturn(jsonPayload);

        when(lambdaClient.invoke(any(InvokeRequest.class)))
            .thenReturn(InvokeResponse.builder()
                .statusCode(200)
                .payload(SdkBytes.fromUtf8String(jsonResponse))
                .build());

        when(objectMapper.readValue(jsonResponse, OrderResponse.class))
            .thenReturn(expectedResponse);

        // When
        OrderResponse result = service.invoke(
            "order-processor", request, OrderResponse.class);

        // Then
        assertThat(result).isEqualTo(expectedResponse);
        verify(lambdaClient).invoke(any(InvokeRequest.class));
    }

    @Test
    void shouldHandleFunctionError() throws Exception {
        // Given
        OrderRequest request = new OrderRequest("ORDER-123");
        String jsonPayload = "{\"orderId\":\"ORDER-123\"};
        String errorResponse = "{\"errorMessage\":\"Invalid input\"};

        when(objectMapper.writeValueAsString(request))
            .thenReturn(jsonPayload);

        when(lambdaClient.invoke(any(InvokeRequest.class)))
            .thenReturn(InvokeResponse.builder()
                .statusCode(200)
                .functionError("Unhandled")
                .payload(SdkBytes.fromUtf8String(errorResponse))
                .build());

        // When & Then
        assertThatThrownBy(() ->
            service.invoke("order-processor", request, OrderResponse.class))
            .isInstanceOf(LambdaInvocationException.class)
            .hasMessageContaining("Lambda function error");
    }
}
```

## Maven Dependencies
```xml
<!-- AWS SDK for Java v2 Lambda -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>lambda</artifactId>
    <version>2.36.3</version> // Use the latest version available
</dependency>

<!-- Jackson for JSON processing -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>

<!-- Spring Boot support -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```