# AWS SDK for Java 2.x Best Practices

## Client Configuration

### Timeout Configuration
Always configure both API call and attempt timeouts to prevent hanging requests.

```java
ClientOverrideConfiguration config = ClientOverrideConfiguration.builder()
    .apiCallTimeout(Duration.ofSeconds(30))        // Total for all retries
    .apiCallAttemptTimeout(Duration.ofSeconds(10))  // Per-attempt timeout
    .build();
```

**Best Practices:**
- Set `apiCallTimeout` higher than `apiCallAttemptTimeout`
- Use appropriate timeouts based on your service's characteristics
- Consider network latency and service response times
- Monitor timeout metrics to adjust as needed

### HTTP Client Selection
Choose the appropriate HTTP client for your use case.

#### For Synchronous Applications (Apache HttpClient)
```java
ApacheHttpClient httpClient = ApacheHttpClient.builder()
    .maxConnections(100)
    .connectionTimeout(Duration.ofSeconds(5))
    .socketTimeout(Duration.ofSeconds(30))
    .build();
```

**Best Use Cases:**
- Traditional synchronous applications
- Medium-throughput operations
- When blocking behavior is acceptable

#### For Asynchronous Applications (Netty NIO Client)
```java
NettyNioAsyncHttpClient httpClient = NettyNioAsyncHttpClient.builder()
    .maxConcurrency(100)
    .connectionTimeout(Duration.ofSeconds(5))
    .readTimeout(Duration.ofSeconds(30))
    .writeTimeout(Duration.ofSeconds(30))
    .sslProvider(SslProvider.OPENSSL)
    .build();
```

**Best Use Cases:**
- High-throughput applications
- I/O-bound operations
- When non-blocking behavior is required
- For improved SSL performance

#### For Lightweight Applications (URL Connection Client)
```java
UrlConnectionHttpClient httpClient = UrlConnectionHttpClient.builder()
    .socketTimeout(Duration.ofSeconds(30))
    .build();
```

**Best Use Cases:**
- Simple applications with low requirements
- When minimizing dependencies
- For basic operations

## Authentication and Security

### Credential Management

#### Default Provider Chain
```java
// Use default chain (recommended)
S3Client s3Client = S3Client.builder().build();
```

**Default Chain Order:**
1. Java system properties (`aws.accessKeyId`, `aws.secretAccessKey`)
2. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
3. Web identity token from `AWS_WEB_IDENTITY_TOKEN_FILE`
4. Shared credentials file (`~/.aws/credentials`)
5. Config file (`~/.aws/config`)
6. Amazon ECS container credentials
7. Amazon EC2 instance profile credentials

#### Explicit Credential Provider
```java
// Use specific credential provider
CredentialsProvider credentials = ProfileCredentialsProvider.create("my-profile");

S3Client s3Client = S3Client.builder()
    .credentialsProvider(credentials)
    .build();
```

#### IAM Roles (Preferred for Production)
```java
// Use IAM role credentials
CredentialsProvider instanceProfile = InstanceProfileCredentialsProvider.create();

S3Client s3Client = S3Client.builder()
    .credentialsProvider(instanceProfile)
    .build();
```

### Security Best Practices

1. **Never hardcode credentials** - Use credential providers or environment variables
2. **Use IAM roles** - Prefer over access keys when possible
3. **Implement credential rotation** - For long-lived access keys
4. **Apply least privilege** - Grant minimum required permissions
5. **Enable SSL** - Always use HTTPS (default behavior)
6. **Monitor access** - Enable AWS CloudTrail for auditing
7. **Use SSO for human users** - Instead of long-term credentials

## Resource Management

### Client Lifecycle
```java
// Option 1: Try-with-resources (recommended)
try (S3Client s3 = S3Client.builder().build()) {
    // Use client
} // Auto-closed

// Option 2: Explicit close
S3Client s3 = S3Client.builder().build();
try {
    // Use client
} finally {
    s3.close();
}
```

### Stream Handling
Close streams immediately to prevent connection pool exhaustion.

```java
try (ResponseInputStream<GetObjectResponse> response =
        s3Client.getObject(GetObjectRequest.builder()
            .bucket(bucketName)
            .key(objectKey)
            .build())) {

    // Read and process data immediately
    byte[] data = response.readAllBytes();

} // Stream auto-closed, connection returned to pool
```

## Performance Optimization

### Connection Pooling
```java
// Configure connection pooling
ApacheHttpClient httpClient = ApacheHttpClient.builder()
    .maxConnections(100)          // Adjust based on your needs
    .connectionTimeout(Duration.ofSeconds(5))
    .socketTimeout(Duration.ofSeconds(30))
    .connectionTimeToLive(Duration.ofMinutes(5))
    .build();
```

**Best Practices:**
- Set appropriate `maxConnections` based on expected load
- Consider connection time to live (TTL)
- Monitor connection pool metrics
- Use appropriate timeouts

### SSL Optimization
Use OpenSSL with Netty for better SSL performance.

```xml
<!-- Maven dependency -->
<dependency>
    <groupId>io.netty</groupId>
    <artifactId>netty-tcnative-boringssl-static</artifactId>
    <version>2.0.61.Final</version>
    <scope>runtime</scope>
</dependency>
```

```java
// Use OpenSSL for async clients
NettyNioAsyncHttpClient httpClient = NettyNioAsyncHttpClient.builder()
    .sslProvider(SslProvider.OPENSSL)
    .build();
```

### Async for I/O-Bound Operations
```java
// Use async clients for I/O-bound operations
S3AsyncClient s3AsyncClient = S3AsyncClient.builder()
    .httpClient(httpClient)
    .build();

// Use CompletableFuture for non-blocking operations
CompletableFuture<PutObjectResponse> future = s3AsyncClient.putObject(request);
future.thenAccept(response -> {
    // Handle success
}).exceptionally(error -> {
    // Handle error
    return null;
});
```

## Monitoring and Observability

### Enable SDK Metrics
```java
CloudWatchMetricPublisher publisher = CloudWatchMetricPublisher.create();

S3Client s3Client = S3Client.builder()
    .overrideConfiguration(b -> b
        .addMetricPublisher(publisher))
    .build();
```

### CloudWatch Integration
Configure CloudWatch metrics publisher to collect SDK metrics.

```java
CloudWatchMetricPublisher cloudWatchPublisher = CloudWatchMetricPublisher.builder()
    .namespace("MyApplication")
    .credentialProvider(credentials)
    .build();
```

### Custom Metrics
Implement custom metrics for application-specific monitoring.

```java
public class CustomMetricPublisher implements MetricPublisher {
    @Override
    public void publish(MetricCollection metrics) {
        // Implement custom metrics logic
        metrics.forEach(metric -> {
            System.out.println("Metric: " + metric.name() + " = " + metric.value());
        });
    }
}
```

## Error Handling

### Comprehensive Error Handling
```java
try {
    awsOperation();
} catch (SdkServiceException e) {
    // Service-specific error
    System.err.println("AWS Service Error: " + e.awsErrorDetails().errorMessage());
    System.err.println("Error Code: " + e.awsErrorDetails().errorCode());
    System.err.println("Status Code: " + e.statusCode());
    System.err.println("Request ID: " + e.requestId());

} catch (SdkClientException e) {
    // Client-side error (network, timeout, etc.)
    System.err.println("Client Error: " + e.getMessage());

} catch (Exception e) {
    // Other errors
    System.err.println("Unexpected Error: " + e.getMessage());
}
```

### Retry Configuration
```java
RetryPolicy retryPolicy = RetryPolicy.builder()
    .numRetries(3)
    .retryCondition(RetryCondition.defaultRetryCondition())
    .backoffStrategy(BackoffStrategy.defaultStrategy())
    .build();
```

## Testing Strategies

### Local Testing with LocalStack
```java
@TestConfiguration
public class LocalStackConfig {
    @Bean
    public S3Client s3Client() {
        return S3Client.builder()
            .endpointOverride(URI.create("http://localhost:4566"))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create("test", "test")))
            .build();
    }
}
```

### Testcontainers Integration
```java
@Testcontainers
@SpringBootTest
public class AwsIntegrationTest {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.S3);

    @DynamicPropertySource
    static void configProperties(DynamicPropertyRegistry registry) {
        registry.add("aws.endpoint", () -> localstack.getEndpointOverride(LocalStackContainer.Service.S3));
    }
}
```

## Configuration Templates

### High-Throughput Configuration
```java
ApacheHttpClient highThroughputClient = ApacheHttpClient.builder()
    .maxConnections(200)
    .connectionTimeout(Duration.ofSeconds(3))
    .socketTimeout(Duration.ofSeconds(30))
    .connectionTimeToLive(Duration.ofMinutes(10))
    .build();

S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .httpClient(highThroughputClient)
    .overrideConfiguration(b -> b
        .apiCallTimeout(Duration.ofSeconds(45))
        .apiCallAttemptTimeout(Duration.ofSeconds(15)))
    .build();
```

### Low-Latency Configuration
```java
ApacheHttpClient lowLatencyClient = ApacheHttpClient.builder()
    .maxConnections(50)
    .connectionTimeout(Duration.ofSeconds(2))
    .socketTimeout(Duration.ofSeconds(10))
    .build();

S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .httpClient(lowLatencyClient)
    .overrideConfiguration(b -> b
        .apiCallTimeout(Duration.ofSeconds(15))
        .apiCallAttemptTimeout(Duration.ofSeconds(3)))
    .build();
```