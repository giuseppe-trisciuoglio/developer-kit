---
name: aws-sdk-java-v2-lambda
description: Provides AWS Lambda patterns using AWS SDK for Java 2.x. Use when invoking Lambda functions, creating/updating functions, managing function configurations, working with Lambda layers, or integrating Lambda with Spring Boot applications.
category: aws
tags: [aws, lambda, java, sdk, serverless, functions]
version: 2.2.0
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# AWS SDK for Java 2.x - AWS Lambda

## Overview

AWS Lambda is a compute service that runs code without managing servers. This skill covers implementing AWS Lambda operations using AWS SDK for Java 2.x including invocation, function management, and Spring Boot integration.

## When to Use

- Invoking Lambda functions programmatically (sync/async)
- Creating or updating Lambda functions
- Managing Lambda function configurations and environment variables
- Managing Lambda layers and aliases
- Integrating Lambda with Spring Boot

## Instructions

1. **Add Dependencies** - Include Lambda SDK dependency
2. **Create Client** - Instantiate LambdaClient with proper configuration
3. **Invoke Functions** - Use invoke() with appropriate invocation type
4. **Handle Responses** - Parse response payloads and handle function errors
5. **Manage Functions** - Create, update, or delete Lambda functions
6. **Integrate with Spring** - Configure Lambda beans and services

## Examples

### Synchronous Invocation

```java
InvokeRequest request = InvokeRequest.builder()
    .functionName(functionName)
    .payload(SdkBytes.fromUtf8String(payload))
    .build();

InvokeResponse response = lambdaClient.invoke(request);
String result = response.payload().asUtf8String();
```

### Asynchronous Invocation

```java
InvokeRequest request = InvokeRequest.builder()
    .functionName(functionName)
    .invocationType(InvocationType.EVENT)
    .payload(SdkBytes.fromUtf8String(payload))
    .build();

lambdaClient.invoke(request);
```

### Spring Boot Service

```java
@Service
public class LambdaInvokerService {
    private final LambdaClient lambdaClient;
    private final ObjectMapper objectMapper;

    public <T, R> R invoke(String functionName, T request, Class<R> responseType) {
        String jsonPayload = objectMapper.writeValueAsString(request);
        InvokeResponse response = lambdaClient.invoke(
            InvokeRequest.builder()
                .functionName(functionName)
                .payload(SdkBytes.fromUtf8String(jsonPayload))
                .build());

        if (response.functionError() != null) {
            throw new LambdaInvocationException("Lambda error: " + response.functionError());
        }
        return objectMapper.readValue(response.payload().asUtf8String(), responseType);
    }
}
```

## Constraints and Warnings

- **Payload Size**: 6MB for sync invocation, 256KB for async
- **Timeout**: Maximum function timeout is 15 minutes
- **Memory**: Memory configuration affects CPU and network performance
- **Concurrency**: Account-level concurrency limits can cause throttling
- **Cold Starts**: New invocations may have initialization delays

## Best Practices

1. **Reuse Lambda clients**: Create once and reuse
2. **Set appropriate timeouts**: Match client timeout to Lambda function timeout
3. **Use async invocation**: For fire-and-forget scenarios
4. **Handle errors properly**: Check for function errors and status codes
5. **Implement retry logic**: For transient failures

## References

- [Official Documentation](references/official-documentation.md)
- [Examples](references/examples.md)

## Related Skills

- `aws-sdk-java-v2-core` - Core AWS SDK patterns
- `spring-boot-dependency-injection` - Spring DI best practices
