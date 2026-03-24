# Lambda Client Setup

## Maven Dependency

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>lambda</artifactId>
</dependency>
```

## Basic Client Configuration

### Synchronous Client

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.lambda.LambdaClient;

LambdaClient lambdaClient = LambdaClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Asynchronous Client

```java
import software.amazon.awssdk.services.lambda.LambdaAsyncClient;

LambdaAsyncClient asyncLambdaClient = LambdaAsyncClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Custom Configuration

```java
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import java.time.Duration;

LambdaClient lambdaClient = LambdaClient.builder()
    .region(Region.US_EAST_1)
    .httpClientBuilder(ApacheHttpClient.builder()
        .connectionTimeout(Duration.ofSeconds(5))
        .socketTimeout(Duration.ofSeconds(300)))
    .build();
```

### With Credentials Provider

```java
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;

AwsBasicCredentials credentials = AwsBasicCredentials.create(
    "access-key-id",
    "secret-access-key"
);

LambdaClient lambdaClient = LambdaClient.builder()
    .region(Region.US_EAST_1)
    .credentialsProvider(StaticCredentialsProvider.create(credentials))
    .build();
```

## Spring Boot Configuration

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
    public LambdaAsyncClient lambdaAsyncClient() {
        return LambdaAsyncClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

## Environment-Specific Configuration

```java
@Bean
public LambdaClient lambdaClient(
    @Value("${aws.region}") String region,
    @Value("${aws.endpoint}") Optional<String> endpoint
) {
    LambdaClient.Builder builder = LambdaClient.builder()
        .region(Region.of(region));

    endpoint.ifPresent(e -> builder.endpointOverride(URI.create(e)));

    return builder.build();
}
```
