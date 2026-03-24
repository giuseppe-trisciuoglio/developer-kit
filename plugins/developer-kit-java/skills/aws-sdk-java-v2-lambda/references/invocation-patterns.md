# Lambda Invocation Patterns

## Synchronous Invocation

### Basic Invocation

```java
import software.amazon.awssdk.services.lambda.model.InvokeRequest;
import software.amazon.awssdk.services.lambda.model.InvokeResponse;
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

### With JSON Objects

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

### Parse Typed Responses

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

## Asynchronous Invocation

### Fire-and-Forget

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

### Async with Event

```java
public void invokeAsync(LambdaClient client, String functionName, Map<String, Object> event) {
    try {
        String jsonPayload = new ObjectMapper().writeValueAsString(event);

        InvokeRequest request = InvokeRequest.builder()
            .functionName(functionName)
            .invocationType(InvocationType.EVENT)
            .payload(SdkBytes.fromUtf8String(jsonPayload))
            .build();

        client.invoke(request);

    } catch (Exception e) {
        throw new RuntimeException("Async invocation failed", e);
    }
}
```

## Error Handling

### Comprehensive Error Handling

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

### Custom Exception

```java
public class LambdaInvocationException extends RuntimeException {
    private final String functionName;
    private final String statusCode;

    public LambdaInvocationException(String message) {
        super(message);
        this.functionName = null;
        this.statusCode = null;
    }

    public LambdaInvocationException(String message, Throwable cause) {
        super(message, cause);
        this.functionName = null;
        this.statusCode = null;
    }

    public LambdaInvocationException(String functionName, String statusCode, String message) {
        super(message);
        this.functionName = functionName;
        this.statusCode = statusCode;
    }

    public String getFunctionName() {
        return functionName;
    }

    public String getStatusCode() {
        return statusCode;
    }
}
```

## Advanced Patterns

### Retry Logic

```java
public String invokeWithRetry(LambdaClient lambdaClient,
                              String functionName,
                              String payload,
                              int maxRetries) {
    int attempts = 0;

    while (attempts < maxRetries) {
        try {
            return invokeLambda(lambdaClient, functionName, payload);
        } catch (LambdaException e) {
            attempts++;
            if (attempts >= maxRetries) {
                throw e;
            }

            try {
                Thread.sleep(1000L * attempts); // Exponential backoff
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("Interrupted during retry", ie);
            }
        }
    }

    throw new RuntimeException("Max retries exceeded");
}
```

### Batch Invocation

```java
public List<String> invokeBatch(LambdaClient lambdaClient,
                                String functionName,
                                List<String> payloads) {
    List<String> responses = new ArrayList<>();

    for (String payload : payloads) {
        try {
            String response = invokeLambda(lambdaClient, functionName, payload);
            responses.add(response);
        } catch (Exception e) {
            responses.add("ERROR: " + e.getMessage());
        }
    }

    return responses;
}
```

### Parallel Invocation

```java
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

public List<String> invokeParallel(LambdaAsyncClient asyncClient,
                                   String functionName,
                                   List<String> payloads) {
    List<CompletableFuture<String>> futures = payloads.stream()
        .map(payload -> CompletableFuture.supplyAsync(() -> {
            try {
                return invokeLambdaAsync(asyncClient, functionName, payload);
            } catch (Exception e) {
                return "ERROR: " + e.getMessage();
            }
        }))
        .collect(Collectors.toList());

    return futures.stream()
        .map(CompletableFuture::join)
        .collect(Collectors.toList());
}
```
