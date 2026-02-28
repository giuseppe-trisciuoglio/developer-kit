# S3 Spring Boot Integration Reference

## Advanced Spring Boot Configuration

### Multi-Environment Configuration

```java
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(S3Properties.class)
public class S3Configuration {

    private final S3Properties properties;

    public S3Configuration(S3Properties properties) {
        this.properties = properties;
    }

    @Bean
    @ConditionalOnProperty(name = "s3.client.async.enabled", havingValue = "true")
    public S3AsyncClient s3AsyncClient() {
        return S3AsyncClient.builder()
            .region(Region.of(properties.getRegion()))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    properties.getAccessKey(),
                    properties.getSecretKey())))
            .endpointOverride(URI.create(properties.getEndpoint()))
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "s3.client.sync.enabled", havingValue = "true", matchIfMissing = true)
    public S3Client s3Client() {
        return S3Client.builder()
            .region(Region.of(properties.getRegion()))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    properties.getAccessKey(),
                    properties.getSecretKey())))
            .endpointOverride(URI.create(properties.getEndpoint()))
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "s3.transfer-manager.enabled", havingValue = "true")
    public S3TransferManager s3TransferManager() {
        return S3TransferManager.builder()
            .s3Client(s3Client())
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "s3.presigner.enabled", havingValue = "true")
    public S3Presigner s3Presigner() {
        return S3Presigner.builder()
            .region(Region.of(properties.getRegion()))
            .build();
    }
}

@ConfigurationProperties(prefix = "s3")
@Data
public class S3Properties {
    private String accessKey;
    private String secretKey;
    private String region = "us-east-1";
    private String endpoint = null;
    private boolean syncEnabled = true;
    private boolean asyncEnabled = false;
    private boolean transferManagerEnabled = false;
    private boolean presignerEnabled = false;
    private int maxConnections = 100;
    private int connectionTimeout = 5000;
    private int socketTimeout = 30000;
    private String defaultBucket;
}
```

### Profile-Specific Configuration

```properties
# application-dev.properties
s3.access-key=${AWS_ACCESS_KEY}
s3.secret-key=${AWS_SECRET_KEY}
s3.region=us-east-1
s3.endpoint=http://localhost:4566
s3.async-enabled=true
s3.transfer-manager-enabled=true

# application-prod.properties
s3.access-key=${AWS_ACCESS_KEY}
s3.secret-key=${AWS_SECRET_KEY}
s3.region=us-east-1
s3.async-enabled=true
s3.presigner-enabled=true
```

## Advanced Service Patterns

### Generic S3 Service Template

```java
import software.amazon.awssdk.services.s3.model.*;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class S3Service {

    private final S3Client s3Client;
    private final S3AsyncClient s3AsyncClient;
    private final S3TransferManager transferManager;
    private final S3Properties s3Properties;

    // Basic Operations
    public Mono<Void> uploadObjectAsync(String key, byte[] data) {
        return Mono.fromFuture(() -> {
            PutObjectRequest request = PutObjectRequest.builder()
                .bucket(s3Properties.getDefaultBucket())
                .key(key)
                .build();

            return s3AsyncClient.putObject(request,
                RequestBody.fromBytes(data)).future();
        });
    }

    public Mono<byte[]> downloadObjectAsync(String key) {
        return Mono.fromFuture(() -> {
            GetObjectRequest request = GetObjectRequest.builder()
                .bucket(s3Properties.getDefaultBucket())
                .key(key)
                .build();

            return s3AsyncClient.getObject(request)
                .thenApply(response -> {
                    try {
                        return response.readAllBytes();
                    } catch (IOException e) {
                        throw new RuntimeException("Failed to read S3 object", e);
                    }
                });
        });
    }

    // Advanced Operations
    public Mono<UploadResult> uploadWithMetadata(String key,
                                                  Path file,
                                                  Map<String, String> metadata) {
        return Mono.fromFuture(() -> {
            PutObjectRequest request = PutObjectRequest.builder()
                .bucket(s3Properties.getDefaultBucket())
                .key(key)
                .metadata(metadata)
                .contentType(getContentType(file))
                .build();

            return s3AsyncClient.putObject(request, RequestBody.fromFile(file))
                .thenApply(response -> new UploadResult(key, response.eTag()));
        });
    }

    public Flux<S3Object> listObjectsWithPrefix(String prefix) {
        ListObjectsV2Request request = ListObjectsV2Request.builder()
            .bucket(s3Properties.getDefaultBucket())
            .prefix(prefix)
            .build();

        return Flux.create(sink -> {
            s3Client.listObjectsV2Paginator(request)
                .contents()
                .forEach(sink::next);
            sink.complete();
        });
    }

    public Mono<Void> batchDelete(List<String> keys) {
        return Mono.fromFuture(() -> {
            List<ObjectIdentifier> objectIdentifiers = keys.stream()
                .map(key -> ObjectIdentifier.builder().key(key).build())
                .collect(Collectors.toList());

            Delete delete = Delete.builder()
                .objects(objectIdentifiers)
                .build();

            DeleteObjectsRequest request = DeleteObjectsRequest.builder()
                .bucket(s3Properties.getDefaultBucket())
                .delete(delete)
                .build();

            return s3AsyncClient.deleteObjects(request).future();
        });
    }

    // Transfer Manager Operations
    public Mono<UploadResult> uploadWithTransferManager(String key, Path file) {
        return Mono.fromFuture(() -> {
            UploadFileRequest request = UploadFileRequest.builder()
                .putObjectRequest(req -> req
                    .bucket(s3Properties.getDefaultBucket())
                    .key(key))
                .source(file)
                .build();

            return transferManager.uploadFile(request)
                .completionFuture()
                .thenApply(result -> new UploadResult(key, result.response().eTag()));
        });
    }

    public Mono<DownloadResult> downloadWithTransferManager(String key, Path destination) {
        return Mono.fromFuture(() -> {
            DownloadFileRequest request = DownloadFileRequest.builder()
                .getObjectRequest(req -> req
                    .bucket(s3Properties.getDefaultBucket())
                    .key(key))
                .destination(destination)
                .build();

            return transferManager.downloadFile(request)
                .completionFuture()
                .thenApply(result -> new DownloadResult(destination, result.response().contentLength()));
        });
    }

    // Utility Methods
    private String getContentType(Path file) {
        try {
            return Files.probeContentType(file);
        } catch (IOException e) {
            return "application/octet-stream";
        }
    }

    // Records for Results
    public record UploadResult(String key, String eTag) {}
    public record DownloadResult(Path path, long size) {}
}
```

### Event-Driven S3 Operations

```java
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
public class S3EventService {

    private final S3Service s3Service;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public Mono<UploadResult> uploadAndPublishEvent(String key, Path file) {
        return s3Service.uploadWithTransferManager(key, file)
            .doOnSuccess(result -> {
                eventPublisher.publishEvent(new S3UploadEvent(key, result.eTag()));
            })
            .doOnError(error -> {
                eventPublisher.publishEvent(new S3UploadFailedEvent(key, error.getMessage()));
            });
    }

    public Mono<String> generatePresignedUrl(String key) {
        return s3Service.downloadObjectAsync(key)
            .flatMap(data -> {
                return Mono.fromCallable(() -> {
                    S3Presigner presigner = S3Presigner.create();
                    try {
                        GetObjectRequest request = GetObjectRequest.builder()
                            .bucket(s3Service.getDefaultBucket())
                            .key(key)
                            .build();

                        GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
                            .signatureDuration(Duration.ofMinutes(10))
                            .getObjectRequest(request)
                            .build();

                        return presigner.presignGetObject(presignRequest)
                            .url()
                            .toString();
                    } finally {
                        presigner.close();
                    }
                });
            });
    }
}

// Event Classes
public class S3UploadEvent extends ApplicationEvent {
    private final String key;
    private final String eTag;

    public S3UploadEvent(String key, String eTag) {
        super(key);
        this.key = key;
        this.eTag = eTag;
    }

    public String getKey() { return key; }
    public String getETag() { return eTag; }
}

public class S3UploadFailedEvent extends ApplicationEvent {
    private final String key;
    private final String errorMessage;

    public S3UploadFailedEvent(String key, String errorMessage) {
        super(key);
        this.key = key;
        this.errorMessage = errorMessage;
    }

    public String getKey() { return key; }
    public String getErrorMessage() { return errorMessage; }
}
```

### Retry and Error Handling

```java
import org.springframework.retry.annotation.*;
import org.springframework.retry.support.RetryTemplate;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
import software.amazon.awssdk.services.s3.model.*;

@Service
@RequiredArgsConstructor
public class ResilientS3Service {

    private final S3Client s3Client;
    private final RetryTemplate retryTemplate;

    @Retryable(value = {S3Exception.class, SdkClientException.class},
               maxAttempts = 3,
               backoff = @Backoff(delay = 1000, multiplier = 2))
    public Mono<PutObjectResponse> uploadWithRetry(String key, Path file) {
        return Mono.fromCallable(() -> {
            PutObjectRequest request = PutObjectRequest.builder()
                .bucket("my-bucket")
                .key(key)
                .build();

            return s3Client.putObject(request, RequestBody.fromFile(file));
        });
    }

    @Recover
    public Mono<PutObjectResponse> uploadRecover(S3Exception e, String key, Path file) {
        // Log the failure and potentially send notification
        System.err.println("Upload failed after retries: " + e.getMessage());
        return Mono.error(new S3UploadException("Upload failed after retries", e));
    }

    @Retryable(value = {S3Exception.class},
               maxAttempts = 5,
               backoff = @Backoff(delay = 2000, multiplier = 2))
    public Mono<Void> copyObjectWithRetry(String sourceKey, String destinationKey) {
        return Mono.fromFuture(() -> {
            CopyObjectRequest request = CopyObjectRequest.builder()
                .sourceBucket("source-bucket")
                .sourceKey(sourceKey)
                .destinationBucket("destination-bucket")
                .destinationKey(destinationKey)
                .build();

            return s3AsyncClient.copyObject(request).future();
        });
    }
}

public class S3UploadException extends RuntimeException {
    public S3UploadException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

## Testing Integration

### Test Configuration with LocalStack

```java
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.test.context.ActiveProfiles;
import org.testcontainers.utility.DockerImageName;

@Testcontainers
@ActiveProfiles("test")
@TestConfiguration
public class S3TestConfig {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.8.1"))
        .withServices(LocalStackContainer.Service.S3)
        .withEnv("DEFAULT_REGION", "us-east-1");

    @Bean
    public S3Client testS3Client() {
        return S3Client.builder()
            .region(Region.US_EAST_1)
            .endpointOverride(localstack.getEndpointOverride(LocalStackContainer.Service.S3))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    localstack.getAccessKey(),
                    localstack.getSecretKey())))
            .build();
    }

    @Bean
    public S3AsyncClient testS3AsyncClient() {
        return S3AsyncClient.builder()
            .region(Region.US_EAST_1)
            .endpointOverride(localstack.getEndpointOverride(LocalStackContainer.Service.S3))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    localstack.getAccessKey(),
                    localstack.getSecretKey())))
            .build();
    }
}
```

### Unit Testing with Mocks

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;
import reactor.core.publisher.Mono;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class S3ServiceTest {

    @Mock
    private S3Client s3Client;

    @InjectMocks
    private S3Service s3Service;

    @Test
    void uploadObjectAsync_ShouldReturnUploadResult() {
        // Arrange
        String key = "test-key";
        byte[] data = "test-content".getBytes();
        String eTag = "12345";

        PutObjectResponse response = PutObjectResponse.builder()
            .eTag(eTag)
            .build();

        when(s3Client.putObject(any(PutObjectRequest.class), any()))
            .thenReturn(response);

        // Act
        Mono<UploadResult> result = s3Service.uploadObjectAsync(key, data);

        // Assert
        result.subscribe(uploadResult -> {
            assertEquals(key, uploadResult.key());
            assertEquals(eTag, uploadResult.eTag());
        });
    }

    @Test
    void listObjectsWithPrefix_ShouldReturnObjectList() {
        // Arrange
        String prefix = "documents/";
        S3Object object1 = S3Object.builder().key("documents/file1.txt").build();
        S3Object object2 = S3Object.builder().key("documents/file2.txt").build();

        ListObjectsV2Response response = ListObjectsV2Response.builder()
            .contents(object1, object2)
            .build();

        when(s3Client.listObjectsV2(any(ListObjectsV2Request.class)))
            .thenReturn(response);

        // Act
        Flux<S3Object> result = s3Service.listObjectsWithPrefix(prefix);

        // Assert
        result.collectList()
            .subscribe(objects -> {
                assertEquals(2, objects.size());
                assertTrue(objects.stream().allMatch(obj -> obj.key().startsWith(prefix)));
            });
    }
}
```

### Integration Testing

```java
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import software.amazon.awssdk.services.s3.model.*;
import java.nio.file.*;
import java.util.Map;

@SpringBootTest
@ActiveProfiles("test")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class S3IntegrationTest {

    @Autowired
    private S3Service s3Service;

    private static final String TEST_BUCKET = "test-bucket";
    private static final String TEST_FILE = "test-document.txt";

    @BeforeAll
    static void setup() throws Exception {
        // Create test file
        Files.write(Paths.get(TEST_FILE), "Test content".getBytes());
    }

    @Test
    @Order(1)
    void uploadFile_ShouldSucceed() {
        // Act & Assert
        s3Service.uploadWithMetadata(TEST_FILE, Paths.get(TEST_FILE),
            Map.of("author", "test", "type", "document"))
            .as(StepVerifier::create)
            .expectNextMatches(result ->
                result.key().equals(TEST_FILE) && result.eTag() != null)
            .verifyComplete();
    }

    @Test
    @Order(2)
    void downloadFile_ShouldReturnContent() {
        // Act & Assert
        s3Service.downloadObjectAsync(TEST_FILE)
            .as(StepVerifier::create)
            .expectNext("Test content".getBytes())
            .verifyComplete();
    }

    @Test
    @Order(3)
    void listObjects_ShouldReturnFiles() {
        // Act & Assert
        s3Service.listObjectsWithPrefix("")
            .as(StepVerifier::create)
            .expectNextCount(1)
            .verifyComplete();
    }

    @AfterAll
    static void cleanup() {
        try {
            Files.deleteIfExists(Paths.get(TEST_FILE));
        } catch (IOException e) {
            // Ignore
        }
    }
}
```

## Advanced Configuration Patterns

### Environment-Specific Configuration

```java
import org.springframework.boot.autoconfigure.condition.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.*;

@Configuration
public class EnvironmentAwareS3Config {

    @Bean
    @ConditionalOnMissingBean
    public AwsCredentialsProvider awsCredentialsProvider(S3Properties properties) {
        if (properties.getAccessKey() != null && properties.getSecretKey() != null) {
            return StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    properties.getAccessKey(),
                    properties.getSecretKey()));
        }
        return DefaultCredentialsProvider.create();
    }

    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnProperty(name = "s3.region")
    public Region region(S3Properties properties) {
        return Region.of(properties.getRegion());
    }

    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnProperty(name = "s3.endpoint")
    public String endpoint(S3Properties properties) {
        return properties.getEndpoint();
    }
}
```

### Multi-Bucket Support

```java
import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class MultiBucketS3Service {

    private final Map<String, S3Client> bucketClients = new HashMap<>();
    private final S3Client defaultS3Client;

    @Autowired
    public MultiBucketS3Service(S3Client defaultS3Client) {
        this.defaultS3Client = defaultS3Client;
    }

    public S3Client getClientForBucket(String bucketName) {
        return bucketClients.computeIfAbsent(bucketName, name ->
            S3Client.builder()
                .region(defaultS3Client.config().region())
                .credentialsProvider(defaultS3Client.config().credentialsProvider())
                .build());
    }

    public Mono<UploadResult> uploadToBucket(String bucketName, String key, Path file) {
        S3Client client = getClientForBucket(bucketName);
        // Upload implementation using the specific client
        return Mono.empty(); // Implementation
    }
}
```