---
name: aws-sdk-java-v2-core
description: Provides core patterns and best practices for AWS SDK for Java 2.x. Use when configuring AWS service clients, setting up authentication, managing credentials, configuring timeouts, HTTP clients, or following AWS SDK best practices.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# AWS SDK for Java 2.x - Core Patterns

## Overview

Configure AWS service clients, authentication, timeouts, HTTP clients, and implement best practices for AWS SDK for Java 2.x applications.

## When to Use

- Setting up AWS SDK for Java 2.x service clients with proper configuration
- Configuring authentication and credential management strategies
- Implementing client lifecycle management and resource cleanup
- Optimizing performance with HTTP client configuration and connection pooling
- Setting up proper timeout configurations for API calls
- Implementing error handling and retry policies
- Integrating AWS SDK with Spring Boot applications

## Instructions

1. **Add Dependencies** - Include SDK core and appropriate HTTP client dependencies
2. **Configure Credentials** - Set up credential provider chain (env vars, profiles, IAM roles)
3. **Create Clients** - Build service clients with proper region and configuration
4. **Configure Timeouts** - Set API call and attempt timeouts appropriately
5. **Set HTTP Client** - Choose Apache (sync) or Netty (async) with connection pooling
6. **Handle Errors** - Implement proper exception handling and retry logic
7. **Close Resources** - Always close clients and streaming responses
8. **Test Locally** - Use LocalStack or Testcontainers for integration testing

## Examples

### Basic Service Client Setup

```java
S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .build();

// Always close clients when done
try (S3Client s3 = S3Client.builder().region(Region.US_EAST_1).build()) {
    // Use client
}
```

### Advanced Client Configuration

```java
S3Client s3Client = S3Client.builder()
    .region(Region.EU_SOUTH_2)
    .credentialsProvider(EnvironmentVariableCredentialsProvider.create())
    .overrideConfiguration(b -> b
        .apiCallTimeout(Duration.ofSeconds(30))
        .apiCallAttemptTimeout(Duration.ofSeconds(10))
        .addMetricPublisher(CloudWatchMetricPublisher.create()))
    .httpClientBuilder(ApacheHttpClient.builder()
        .maxConnections(100)
        .connectionTimeout(Duration.ofSeconds(5)))
    .build();
```

### Credential Providers

```java
// Default chain (auto-detects)
S3Client.builder().region(Region.US_EAST_1).build();

// Explicit providers
CredentialsProvider envCredentials = EnvironmentVariableCredentialsProvider.create();
CredentialsProvider profileCredentials = ProfileCredentialsProvider.create("myprofile");
CredentialsProvider instanceProfileCredentials = InstanceProfileCredentialsProvider.create();
```

### Error Handling

```java
try {
    s3Client.getObject(request);
} catch (S3Exception e) {
    System.err.println("Error Code: " + e.awsErrorDetails().errorCode());
    System.err.println("Status Code: " + e.statusCode());
} catch (SdkServiceException e) {
    System.err.println("AWS Service Error: " + e.getMessage());
} catch (SdkClientException e) {
    System.err.println("Client Error: " + e.getMessage());
}
```

## Best Practices

1. **Reuse Service Clients**: Clients are thread-safe; create once and reuse
2. **Configure API Timeouts**: Always set both `apiCallTimeout` and `apiCallAttemptTimeout`
3. **Close Streaming Responses**: Prevent connection pool exhaustion
4. **Use IAM Roles**: Prefer IAM roles over access keys when possible
5. **Never Hardcode Credentials**: Use credential providers or environment variables
6. **Optimize SSL**: Use OpenSSL with Netty for better async performance
7. **Enable Metrics**: Use CloudWatch metrics to monitor performance

## Constraints and Warnings

- Never hardcode credentials in source code; use credential providers or environment variables
- Service clients are thread-safe and should be reused; do not create new clients for each request
- Always close streaming responses (`ResponseInputStream`) to prevent connection pool exhaustion
- Set appropriate timeouts to prevent hanging requests
- Be aware of AWS service rate limits; implement exponential backoff for retries
- Async clients require proper event loop management

## References

See [references/](references/) for detailed documentation:
- [Developer Guide](references/developer-guide.md)
- [API Reference](references/api-reference.md)
- [Best Practices](references/best-practices.md)

## Related Skills

- `aws-sdk-java-v2-s3` - S3-specific patterns
- `aws-sdk-java-v2-dynamodb` - DynamoDB patterns
- `aws-sdk-java-v2-lambda` - Lambda patterns
