---
name: aws-sdk-java-v2-lambda
description: AWS Lambda patterns using AWS SDK for Java 2.x. Use when invoking Lambda functions, creating/updating functions, managing function configurations, working with Lambda layers, or integrating Lambda with Spring Boot applications.
category: aws
tags: [aws, lambda, java, sdk, serverless, functions]
version: 1.0.1
allowed-tools: Read, Write, Bash
---

# AWS SDK for Java 2.x - AWS Lambda

## When to Use

Use this skill when:
- Invoking Lambda functions programmatically
- Creating or updating Lambda functions
- Managing Lambda function configurations
- Working with Lambda environment variables
- Managing Lambda layers and aliases
- Implementing asynchronous Lambda invocations
- Integrating Lambda with Spring Boot

## Dependencies

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>lambda</artifactId>
</dependency>
```

## Client Setup

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.lambda.LambdaClient;

LambdaClient lambdaClient = LambdaClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

## Invoke Lambda Function

### Synchronous Invocation

```java
import software.amazon.awssdk.services.lambda.model.*;
import software.amazon.awssdk.core.SdkBytes;

public String invokeLambda(LambdaClient lambdaClient, 
                           String functionName, 
                           String payload) {
    InvokeRequest request = InvokeRequest.builder()
        .functionName(functionName)
        .payload(SdkBytes.fromUtf8String(payload))
        .build();
    
    InvokeResponse response = lambdaClient.invoke(request);
    
    return response.payload().asUtf8String();
}
```

### Asynchronous Invocation

```java
public void invokeLambdaAsync(LambdaClient lambdaClient, 
                              String functionName, 
                              String payload) {
    InvokeRequest request = InvokeRequest.builder()
        .functionName(functionName)
        .invocationType(InvocationType.EVENT) // Asynchronous
        .payload(SdkBytes.fromUtf8String(payload))
        .build();
    
    InvokeResponse response = lambdaClient.invoke(request);
    
    System.out.println("Status: " + response.statusCode());
}
```

### Invoke with JSON Payload

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

### Parse Lambda Response

```java
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

## Function Management

### List Functions

```java
public List<FunctionConfiguration> listFunctions(LambdaClient lambdaClient) {
    ListFunctionsResponse response = lambdaClient.listFunctions();
    
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

### Update Function Code

```java
import java.nio.file.Files;
import java.nio.file.Paths;

public void updateFunctionCode(LambdaClient lambdaClient,
                               String functionName,
                               String zipFilePath) throws IOException {
    byte[] zipBytes = Files.readAllBytes(Paths.get(zipFilePath));
    
    UpdateFunctionCodeRequest request = UpdateFunctionCodeRequest.builder()
        .functionName(functionName)
        .zipFile(SdkBytes.fromByteArray(zipBytes))
        .publish(true)
        .build();
    
    UpdateFunctionCodeResponse response = lambdaClient.updateFunctionCode(request);
    
    System.out.println("Updated function version: " + response.version());
}
```

### Update Function Configuration

```java
public void updateFunctionConfiguration(LambdaClient lambdaClient,
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
public void createFunction(LambdaClient lambdaClient,
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
        .build();
    
    CreateFunctionResponse response = lambdaClient.createFunction(request);
    
    System.out.println("Function ARN: " + response.functionArn());
}
```

### Delete Function

```java
public void deleteFunction(LambdaClient lambdaClient, String functionName) {
    DeleteFunctionRequest request = DeleteFunctionRequest.builder()
        .functionName(functionName)
        .build();
    
    lambdaClient.deleteFunction(request);
}
```

## Spring Boot Integration

### Configuration

```java
@Configuration
public class LambdaConfiguration {
    
    @Bean
    public LambdaClient lambdaClient() {
        return LambdaClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### Lambda Invoker Service

```java
@Service
public class LambdaInvokerService {
    
    private final LambdaClient lambdaClient;
    private final ObjectMapper objectMapper;
    
    public LambdaInvokerService(LambdaClient lambdaClient, ObjectMapper objectMapper) {
        this.lambdaClient = lambdaClient;
        this.objectMapper = objectMapper;
    }
    
    public <T, R> R invoke(String functionName, T request, Class<R> responseType) {
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
    
    public void invokeAsync(String functionName, Object request) {
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

### Typed Lambda Client

```java
public interface OrderProcessor {
    OrderResponse processOrder(OrderRequest request);
}

@Service
public class LambdaOrderProcessor implements OrderProcessor {
    
    private final LambdaInvokerService lambdaInvoker;
    
    @Value("${lambda.order-processor.function-name}")
    private String functionName;
    
    public LambdaOrderProcessor(LambdaInvokerService lambdaInvoker) {
        this.lambdaInvoker = lambdaInvoker;
    }
    
    @Override
    public OrderResponse processOrder(OrderRequest request) {
        return lambdaInvoker.invoke(functionName, request, OrderResponse.class);
    }
}
```

## Error Handling

```java
public String invokeLambdaSafe(LambdaClient lambdaClient,
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
            throw new RuntimeException("Lambda error: " + errorMessage);
        }
        
        // Check status code
        if (response.statusCode() != 200) {
            throw new RuntimeException("Lambda invocation failed with status: " + 
                response.statusCode());
        }
        
        return response.payload().asUtf8String();
        
    } catch (LambdaException e) {
        System.err.println("Lambda error: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

## Best Practices

1. **Reuse Lambda client**: Create once and reuse across invocations
2. **Set appropriate timeouts**: Match client timeout to Lambda function timeout
3. **Use async invocation**: For fire-and-forget scenarios
4. **Handle errors properly**: Check for function errors and status codes
5. **Use environment variables**: For function configuration
6. **Implement retry logic**: For transient failures
7. **Monitor invocations**: Use CloudWatch metrics
8. **Version functions**: Use aliases and versions for production
9. **Use VPC**: For accessing resources in private subnets
10. **Optimize payload size**: Keep payloads small for better performance

## Testing

### Unit Test Lambda Invocation

```java
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
        OrderRequest request = new OrderRequest("ORDER-123");
        OrderResponse expectedResponse = new OrderResponse("SUCCESS");
        
        when(objectMapper.writeValueAsString(request))
            .thenReturn("{\"orderId\":\"ORDER-123\"}");
        
        when(lambdaClient.invoke(any(InvokeRequest.class)))
            .thenReturn(InvokeResponse.builder()
                .statusCode(200)
                .payload(SdkBytes.fromUtf8String("{\"status\":\"SUCCESS\"}"))
                .build());
        
        when(objectMapper.readValue("{\"status\":\"SUCCESS\"}", OrderResponse.class))
            .thenReturn(expectedResponse);
        
        OrderResponse result = service.invoke("order-processor", request, OrderResponse.class);
        
        assertThat(result).isEqualTo(expectedResponse);
    }
}
```

## Related Skills

- @aws-sdk-java-v2-core - Core AWS SDK patterns
- @spring-boot-dependency-injection - Spring dependency injection
- @unit-test-service-layer - Service testing patterns

## References

- [Lambda Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/lambda)
- [Lambda API Reference](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/lambda/package-summary.html)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
