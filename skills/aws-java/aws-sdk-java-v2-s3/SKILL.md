---
name: aws-sdk-java-v2-s3
description: Amazon S3 patterns and examples using AWS SDK for Java 2.x. Use when working with S3 buckets, uploading/downloading objects, multipart uploads, presigned URLs, S3 Transfer Manager, object operations, or S3-specific configurations.
---

# AWS SDK for Java 2.x - Amazon S3

## When to Use

Use this skill when:
- Creating, listing, or deleting S3 buckets
- Uploading or downloading objects from S3
- Working with multipart uploads for large files
- Generating presigned URLs for temporary access
- Copying or moving objects between buckets
- Setting object metadata and storage classes
- Working with S3 Transfer Manager for optimized transfers
- Implementing S3 event notifications
- Managing bucket policies and ACLs

## Dependencies

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3</artifactId>
</dependency>

<!-- For S3 Transfer Manager -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3-transfer-manager</artifactId>
</dependency>

<!-- For async operations -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>netty-nio-client</artifactId>
</dependency>
```

## Client Setup

### Synchronous Client

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Asynchronous Client

```java
import software.amazon.awssdk.services.s3.S3AsyncClient;

S3AsyncClient s3AsyncClient = S3AsyncClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### With Custom Configuration

```java
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import java.time.Duration;

S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .httpClientBuilder(ApacheHttpClient.builder()
        .maxConnections(100)
        .connectionTimeout(Duration.ofSeconds(5)))
    .overrideConfiguration(b -> b
        .apiCallTimeout(Duration.ofSeconds(60))
        .apiCallAttemptTimeout(Duration.ofSeconds(30)))
    .build();
```

## Bucket Operations

### Create Bucket

```java
import software.amazon.awssdk.services.s3.model.*;

public void createBucket(S3Client s3Client, String bucketName) {
    try {
        CreateBucketRequest request = CreateBucketRequest.builder()
            .bucket(bucketName)
            .build();
        
        s3Client.createBucket(request);
        
        // Wait until bucket exists
        HeadBucketRequest waitRequest = HeadBucketRequest.builder()
            .bucket(bucketName)
            .build();
        
        s3Client.waiter().waitUntilBucketExists(waitRequest);
        
    } catch (S3Exception e) {
        System.err.println("Error: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Create Bucket in Specific Region

```java
public void createBucketInRegion(S3Client s3Client, String bucketName, Region region) {
    CreateBucketConfiguration config = CreateBucketConfiguration.builder()
        .locationConstraint(region.id())
        .build();
    
    CreateBucketRequest request = CreateBucketRequest.builder()
        .bucket(bucketName)
        .createBucketConfiguration(config)
        .build();
    
    s3Client.createBucket(request);
}
```

### List Buckets

```java
public List<String> listBuckets(S3Client s3Client) {
    ListBucketsResponse response = s3Client.listBuckets();
    
    return response.buckets().stream()
        .map(Bucket::name)
        .collect(Collectors.toList());
}
```

### Delete Bucket

```java
public void deleteBucket(S3Client s3Client, String bucketName) {
    // Bucket must be empty before deletion
    DeleteBucketRequest request = DeleteBucketRequest.builder()
        .bucket(bucketName)
        .build();
    
    s3Client.deleteBucket(request);
}
```

### Check if Bucket Exists

```java
public boolean bucketExists(S3Client s3Client, String bucketName) {
    try {
        HeadBucketRequest request = HeadBucketRequest.builder()
            .bucket(bucketName)
            .build();
        
        s3Client.headBucket(request);
        return true;
        
    } catch (NoSuchBucketException e) {
        return false;
    }
}
```

## Object Operations

### Upload Object (Simple)

```java
import software.amazon.awssdk.core.sync.RequestBody;
import java.nio.file.Paths;

public void uploadObject(S3Client s3Client, String bucketName, String key, String filePath) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();
    
    s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));
}
```

### Upload Object with Metadata

```java
public void uploadWithMetadata(S3Client s3Client, String bucketName, String key, 
                                String filePath, Map<String, String> metadata) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .metadata(metadata)
        .contentType("application/pdf")
        .serverSideEncryption(ServerSideEncryption.AES256)
        .storageClass(StorageClass.STANDARD_IA)
        .build();
    
    PutObjectResponse response = s3Client.putObject(request, 
        RequestBody.fromFile(Paths.get(filePath)));
    
    System.out.println("ETag: " + response.eTag());
}
```

### Upload from Byte Array

```java
public void uploadFromBytes(S3Client s3Client, String bucketName, String key, byte[] data) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();
    
    s3Client.putObject(request, RequestBody.fromBytes(data));
}
```

### Upload from String

```java
public void uploadFromString(S3Client s3Client, String bucketName, String key, String content) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .contentType("text/plain")
        .build();
    
    s3Client.putObject(request, RequestBody.fromString(content));
}
```

### Download Object

```java
import software.amazon.awssdk.core.ResponseInputStream;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;

public byte[] downloadObject(S3Client s3Client, String bucketName, String key) {
    GetObjectRequest request = GetObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();
    
    try (ResponseInputStream<GetObjectResponse> response = s3Client.getObject(request)) {
        return response.readAllBytes();
    } catch (IOException e) {
        throw new RuntimeException("Failed to read S3 object", e);
    }
}
```

### Download Object to File

```java
public void downloadToFile(S3Client s3Client, String bucketName, String key, String destPath) {
    GetObjectRequest request = GetObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();
    
    s3Client.getObject(request, Paths.get(destPath));
}
```

### Download with Range

```java
public byte[] downloadRange(S3Client s3Client, String bucketName, String key, 
                            long start, long end) {
    GetObjectRequest request = GetObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .range("bytes=" + start + "-" + end)
        .build();
    
    try (ResponseInputStream<GetObjectResponse> response = s3Client.getObject(request)) {
        return response.readAllBytes();
    } catch (IOException e) {
        throw new RuntimeException("Failed to read S3 object range", e);
    }
}
```

### Copy Object

```java
public void copyObject(S3Client s3Client, String sourceBucket, String sourceKey,
                       String destBucket, String destKey) {
    CopyObjectRequest request = CopyObjectRequest.builder()
        .sourceBucket(sourceBucket)
        .sourceKey(sourceKey)
        .destinationBucket(destBucket)
        .destinationKey(destKey)
        .build();
    
    s3Client.copyObject(request);
}
```

### Delete Object

```java
public void deleteObject(S3Client s3Client, String bucketName, String key) {
    DeleteObjectRequest request = DeleteObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();
    
    s3Client.deleteObject(request);
}
```

### Delete Multiple Objects

```java
public void deleteObjects(S3Client s3Client, String bucketName, List<String> keys) {
    List<ObjectIdentifier> objectIds = keys.stream()
        .map(key -> ObjectIdentifier.builder().key(key).build())
        .collect(Collectors.toList());
    
    Delete delete = Delete.builder()
        .objects(objectIds)
        .build();
    
    DeleteObjectsRequest request = DeleteObjectsRequest.builder()
        .bucket(bucketName)
        .delete(delete)
        .build();
    
    DeleteObjectsResponse response = s3Client.deleteObjects(request);
    
    response.deleted().forEach(deleted -> 
        System.out.println("Deleted: " + deleted.key()));
}
```

### List Objects

```java
public List<S3Object> listObjects(S3Client s3Client, String bucketName) {
    ListObjectsV2Request request = ListObjectsV2Request.builder()
        .bucket(bucketName)
        .build();
    
    ListObjectsV2Response response = s3Client.listObjectsV2(request);
    
    return response.contents();
}
```

### List Objects with Prefix

```java
public List<S3Object> listObjectsWithPrefix(S3Client s3Client, String bucketName, String prefix) {
    ListObjectsV2Request request = ListObjectsV2Request.builder()
        .bucket(bucketName)
        .prefix(prefix)
        .build();
    
    return s3Client.listObjectsV2(request).contents();
}
```

### List Objects with Pagination

```java
public void listAllObjects(S3Client s3Client, String bucketName) {
    ListObjectsV2Request request = ListObjectsV2Request.builder()
        .bucket(bucketName)
        .maxKeys(100)
        .build();
    
    ListObjectsV2Iterable responses = s3Client.listObjectsV2Paginator(request);
    
    responses.contents().stream()
        .forEach(object -> System.out.println(object.key()));
}
```

## Presigned URLs

### Generate Presigned URL for Download

```java
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.*;
import java.time.Duration;

public String generatePresignedGetUrl(String bucketName, String key) {
    try (S3Presigner presigner = S3Presigner.builder()
            .region(Region.US_EAST_1)
            .build()) {
        
        GetObjectRequest getObjectRequest = GetObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();
        
        GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
            .signatureDuration(Duration.ofMinutes(10))
            .getObjectRequest(getObjectRequest)
            .build();
        
        PresignedGetObjectRequest presignedRequest = presigner.presignGetObject(presignRequest);
        
        return presignedRequest.url().toString();
    }
}
```

### Generate Presigned URL for Upload

```java
public String generatePresignedPutUrl(String bucketName, String key) {
    try (S3Presigner presigner = S3Presigner.create()) {
        
        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();
        
        PutObjectPresignRequest presignRequest = PutObjectPresignRequest.builder()
            .signatureDuration(Duration.ofMinutes(10))
            .putObjectRequest(putObjectRequest)
            .build();
        
        PresignedPutObjectRequest presignedRequest = presigner.presignPutObject(presignRequest);
        
        return presignedRequest.url().toString();
    }
}
```

## Multipart Upload

### Simple Multipart Upload

```java
import software.amazon.awssdk.services.s3.model.*;
import java.io.*;
import java.util.*;

public void multipartUpload(S3Client s3Client, String bucketName, String key, String filePath) {
    int partSize = 5 * 1024 * 1024; // 5 MB
    
    // Initiate multipart upload
    CreateMultipartUploadRequest createRequest = CreateMultipartUploadRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();
    
    CreateMultipartUploadResponse createResponse = s3Client.createMultipartUpload(createRequest);
    String uploadId = createResponse.uploadId();
    
    List<CompletedPart> completedParts = new ArrayList<>();
    
    try {
        File file = new File(filePath);
        long fileLength = file.length();
        int partNumber = 1;
        
        try (FileInputStream fis = new FileInputStream(file)) {
            long position = 0;
            
            while (position < fileLength) {
                int bytesToRead = (int) Math.min(partSize, fileLength - position);
                byte[] buffer = new byte[bytesToRead];
                fis.read(buffer);
                
                UploadPartRequest uploadRequest = UploadPartRequest.builder()
                    .bucket(bucketName)
                    .key(key)
                    .uploadId(uploadId)
                    .partNumber(partNumber)
                    .build();
                
                UploadPartResponse uploadResponse = s3Client.uploadPart(
                    uploadRequest, 
                    RequestBody.fromBytes(buffer));
                
                completedParts.add(CompletedPart.builder()
                    .partNumber(partNumber)
                    .eTag(uploadResponse.eTag())
                    .build());
                
                position += bytesToRead;
                partNumber++;
            }
        }
        
        // Complete multipart upload
        CompletedMultipartUpload completedUpload = CompletedMultipartUpload.builder()
            .parts(completedParts)
            .build();
        
        CompleteMultipartUploadRequest completeRequest = CompleteMultipartUploadRequest.builder()
            .bucket(bucketName)
            .key(key)
            .uploadId(uploadId)
            .multipartUpload(completedUpload)
            .build();
        
        s3Client.completeMultipartUpload(completeRequest);
        
    } catch (Exception e) {
        // Abort multipart upload on error
        AbortMultipartUploadRequest abortRequest = AbortMultipartUploadRequest.builder()
            .bucket(bucketName)
            .key(key)
            .uploadId(uploadId)
            .build();
        
        s3Client.abortMultipartUpload(abortRequest);
        throw new RuntimeException("Multipart upload failed", e);
    }
}
```

## S3 Transfer Manager

### Upload with Transfer Manager

```java
import software.amazon.awssdk.transfer.s3.*;
import software.amazon.awssdk.transfer.s3.model.*;

public void uploadWithTransferManager(String bucketName, String key, String filePath) {
    try (S3TransferManager transferManager = S3TransferManager.create()) {
        
        UploadFileRequest uploadRequest = UploadFileRequest.builder()
            .putObjectRequest(req -> req
                .bucket(bucketName)
                .key(key))
            .source(Paths.get(filePath))
            .build();
        
        FileUpload upload = transferManager.uploadFile(uploadRequest);
        
        CompletedFileUpload result = upload.completionFuture().join();
        
        System.out.println("Upload complete. ETag: " + result.response().eTag());
    }
}
```

### Download with Transfer Manager

```java
public void downloadWithTransferManager(String bucketName, String key, String destPath) {
    try (S3TransferManager transferManager = S3TransferManager.create()) {
        
        DownloadFileRequest downloadRequest = DownloadFileRequest.builder()
            .getObjectRequest(req -> req
                .bucket(bucketName)
                .key(key))
            .destination(Paths.get(destPath))
            .build();
        
        FileDownload download = transferManager.downloadFile(downloadRequest);
        
        CompletedFileDownload result = download.completionFuture().join();
        
        System.out.println("Download complete");
    }
}
```

### Copy with Transfer Manager

```java
public void copyWithTransferManager(String sourceBucket, String sourceKey,
                                    String destBucket, String destKey) {
    try (S3TransferManager transferManager = S3TransferManager.create()) {
        
        CopyObjectRequest copyRequest = CopyObjectRequest.builder()
            .sourceBucket(sourceBucket)
            .sourceKey(sourceKey)
            .destinationBucket(destBucket)
            .destinationKey(destKey)
            .build();
        
        Copy copy = transferManager.copy(req -> req.copyObjectRequest(copyRequest));
        
        CompletedCopy result = copy.completionFuture().join();
        
        System.out.println("Copy complete");
    }
}
```

## Spring Boot Integration

### Configuration

```java
@Configuration
public class S3Configuration {
    
    @Value("${aws.s3.bucket-name}")
    private String bucketName;
    
    @Bean
    public S3Client s3Client() {
        return S3Client.builder()
            .region(Region.US_EAST_1)
            .build();
    }
    
    @Bean
    public S3AsyncClient s3AsyncClient() {
        return S3AsyncClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
    
    @Bean
    public S3TransferManager s3TransferManager() {
        return S3TransferManager.create();
    }
    
    @Bean
    public S3Presigner s3Presigner() {
        return S3Presigner.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### Service Layer

```java
@Service
public class S3Service {
    
    private final S3Client s3Client;
    private final S3TransferManager transferManager;
    private final S3Presigner presigner;
    private final String bucketName;
    
    public S3Service(S3Client s3Client, 
                     S3TransferManager transferManager,
                     S3Presigner presigner,
                     @Value("${aws.s3.bucket-name}") String bucketName) {
        this.s3Client = s3Client;
        this.transferManager = transferManager;
        this.presigner = presigner;
        this.bucketName = bucketName;
    }
    
    public void upload(String key, Path file) {
        PutObjectRequest request = PutObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();
        
        s3Client.putObject(request, RequestBody.fromFile(file));
    }
    
    public byte[] download(String key) {
        GetObjectRequest request = GetObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();
        
        try (ResponseInputStream<GetObjectResponse> response = s3Client.getObject(request)) {
            return response.readAllBytes();
        } catch (IOException e) {
            throw new RuntimeException("Failed to download from S3", e);
        }
    }
    
    public String generatePresignedUrl(String key, Duration duration) {
        GetObjectRequest getRequest = GetObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();
        
        GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
            .signatureDuration(duration)
            .getObjectRequest(getRequest)
            .build();
        
        return presigner.presignGetObject(presignRequest).url().toString();
    }
}
```

## Best Practices

1. **Use Transfer Manager for large files**: Automatically handles multipart uploads and downloads
2. **Close streams promptly**: Always use try-with-resources for ResponseInputStream
3. **Set appropriate timeouts**: Large uploads may need longer timeouts
4. **Use async client for I/O-bound operations**: Better throughput with non-blocking I/O
5. **Enable server-side encryption**: Use SSE-S3 or SSE-KMS for sensitive data
6. **Set lifecycle policies**: Automatically transition or expire objects
7. **Use presigned URLs for temporary access**: Avoid exposing credentials
8. **Implement retry logic**: S3 operations can fail transiently
9. **Monitor costs**: Track data transfer and storage usage

## Testing with LocalStack

```java
@TestConfiguration
public class LocalStackS3Config {
    
    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.S3);
    
    @Bean
    public S3Client s3Client() {
        return S3Client.builder()
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

## Related Skills

- @aws-sdk-java-v2-core - Core AWS SDK patterns and configuration
- @spring-boot-dependency-injection - Spring dependency injection patterns
- @unit-test-service-layer - Testing service layer patterns

## References

- [S3 Examples Repository](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/s3)
- [S3 API Reference](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/s3/package-summary.html)
- [S3 Transfer Manager](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/transfer/s3/S3TransferManager.html)
