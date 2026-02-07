# AWS SDK for Java 2.x API Reference

## Core Client Classes

### AwsClient
Base interface for all AWS service clients.

```java
public interface AwsClient extends AutoCloseable {
    // Base client interface
}
```

### SdkClient
Enhanced client interface with SDK-specific features.

```java
public interface SdkClient extends AwsClient {
    // Enhanced client methods
}
```

## Client Builders

### ClientBuilder
Base builder interface for all AWS service clients.

**Key Methods:**
- `region(Region region)` - Set AWS region
- `credentialsProvider(CredentialsProvider credentialsProvider)` - Configure authentication
- `overrideConfiguration(ClientOverrideConfiguration overrideConfiguration)` - Override default settings
- `httpClient(HttpClient httpClient)` - Specify HTTP client implementation
- `build()` - Create client instance

## Configuration Classes

### ClientOverrideConfiguration
Controls client-level configuration including timeouts and metrics.

**Key Properties:**
- `apiCallTimeout(Duration)` - Total timeout for all retry attempts
- `apiCallAttemptTimeout(Duration)` - Timeout per individual attempt
- `retryPolicy(RetryPolicy)` - Retry behavior configuration
- `metricPublishers(MetricPublisher...)` - Enable metrics collection

### Builder Example

```java
ClientOverrideConfiguration config = ClientOverrideConfiguration.builder()
    .apiCallTimeout(Duration.ofSeconds(30))
    .apiCallAttemptTimeout(Duration.ofSeconds(10))
    .addMetricPublisher(CloudWatchMetricPublisher.create())
    .build();
```

## HTTP Client Implementations

### ApacheHttpClient
Synchronous HTTP client with advanced features.

**Builder Configuration:**
- `maxConnections(Integer)` - Maximum concurrent connections
- `connectionTimeout(Duration)` - Connection establishment timeout
- `socketTimeout(Duration)` - Socket read/write timeout
- `connectionTimeToLive(Duration)` - Connection lifetime
- `proxyConfiguration(ProxyConfiguration)` - Proxy settings

### NettyNioAsyncHttpClient
Asynchronous HTTP client for high-performance applications.

**Builder Configuration:**
- `maxConcurrency(Integer)` - Maximum concurrent operations
- `connectionTimeout(Duration)` - Connection timeout
- `readTimeout(Duration)` - Read operation timeout
- `writeTimeout(Duration)` - Write operation timeout
- `sslProvider(SslProvider)` - SSL/TLS implementation

### UrlConnectionHttpClient
Lightweight HTTP client using Java's URLConnection.

**Builder Configuration:**
- `socketTimeout(Duration)` - Socket timeout
- `connectTimeout(Duration)` - Connection timeout

## Authentication and Credentials

### Credential Providers

#### EnvironmentVariableCredentialsProvider
Reads credentials from environment variables.

```java
CredentialsProvider provider = EnvironmentVariableCredentialsProvider.create();
```

#### SystemPropertyCredentialsProvider
Reads credentials from Java system properties.

```java
CredentialsProvider provider = SystemPropertyCredentialsProvider.create();
```

#### ProfileCredentialsProvider
Reads credentials from AWS configuration files.

```java
CredentialsProvider provider = ProfileCredentialsProvider.create("profile-name");
```

#### StaticCredentialsProvider
Provides static credentials (not recommended for production).

```java
AwsBasicCredentials credentials = AwsBasicCredentials.create("key", "secret");
CredentialsProvider provider = StaticCredentialsProvider.create(credentials);
```

#### DefaultCredentialsProvider
Implements the default credential provider chain.

```java
CredentialsProvider provider = DefaultCredentialsProvider.create();
```

### SSO Authentication

#### AwsSsoCredentialsProvider
Enables SSO-based authentication.

```java
AwsSsoCredentialsProvider ssoProvider = AwsSsoCredentialsProvider.builder()
    .ssoProfile("my-sso-profile")
    .build();
```

## Error Handling Classes

### SdkClientException
Client-side exceptions (network, timeout, configuration issues).

```java
try {
    awsOperation();
} catch (SdkClientException e) {
    // Handle client-side errors
}
```

### SdkServiceException
Service-side exceptions (AWS service errors).

```java
try {
    awsOperation();
} catch (SdkServiceException e) {
    // Handle service-side errors
    System.err.println("Error Code: " + e.awsErrorDetails().errorCode());
    System.err.println("Request ID: " + e.requestId());
}
```

### S3Exception
S3-specific exceptions.

```java
try {
    s3Operation();
} catch (S3Exception e) {
    // Handle S3-specific errors
    System.err.println("S3 Error: " + e.awsErrorDetails().errorMessage());
}
```

## Metrics and Monitoring

### CloudWatchMetricPublisher
Publishes metrics to AWS CloudWatch.

```java
CloudWatchMetricPublisher publisher = CloudWatchMetricPublisher.create();
```

### MetricPublisher
Base interface for custom metrics publishers.

```java
public interface MetricPublisher {
    void publish(MetricCollection metricCollection);
}
```

## Utility Classes

### Duration and Time
Configure timeouts using Java Duration.

```java
Duration apiTimeout = Duration.ofSeconds(30);
Duration attemptTimeout = Duration.ofSeconds(10);
```

### Region
AWS regions for service endpoints.

```java
Region region = Region.US_EAST_1;
Region regionEU = Region.EU_WEST_1;
```

### URI
Endpoint configuration and proxy settings.

```java
URI proxyUri = URI.create("http://proxy:8080");
URI endpointOverride = URI.create("http://localhost:4566");
```

## Configuration Best Practices

### Resource Management
Always close clients when no longer needed.

```java
try (S3Client s3 = S3Client.builder().build()) {
    // Use client
} // Auto-closed
```

### Connection Pooling
Reuse clients to avoid connection pool overhead.

```java
@Service
public class AwsService {
    private final S3Client s3Client;

    public AwsService() {
        this.s3Client = S3Client.builder().build();
    }

    // Reuse s3Client throughout application
}
```

### Error Handling
Implement comprehensive error handling for robust applications.

```java
try {
    // AWS operation
} catch (SdkServiceException e) {
    // Handle service errors
} catch (SdkClientException e) {
    // Handle client errors
} catch (Exception e) {
    // Handle other errors
}
```