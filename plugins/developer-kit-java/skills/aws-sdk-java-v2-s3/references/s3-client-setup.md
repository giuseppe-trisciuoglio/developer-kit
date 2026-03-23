# S3 Client Setup and Basic Operations

## Dependencies

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3</artifactId>
    <version>2.20.0</version>
</dependency>

<!-- For S3 Transfer Manager -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3-transfer-manager</artifactId>
    <version>2.20.0</version>
</dependency>

<!-- For async operations -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>netty-nio-client</artifactId>
    <version>2.20.0</version>
</dependency>
```

## Client Setup

### Basic Synchronous Client

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Basic Asynchronous Client

```java
import software.amazon.awssdk.services.s3.S3AsyncClient;

S3AsyncClient s3AsyncClient = S3AsyncClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Configured Client with Retry Logic

```java
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.core.retry.RetryPolicy;
import software.amazon.awssdk.core.retry.backoff.ExponentialRetryBackoff;
import java.time.Duration;

S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .httpClientBuilder(ApacheHttpClient.builder()
        .maxConnections(200)
        .connectionTimeout(Duration.ofSeconds(5)))
    .overrideConfiguration(b -> b
        .apiCallTimeout(Duration.ofSeconds(60))
        .apiCallAttemptTimeout(Duration.ofSeconds(30))
        .retryPolicy(RetryPolicy.builder()
            .numRetries(3)
            .retryBackoffStrategy(ExponentialRetryBackoff.builder()
                .baseDelay(Duration.ofSeconds(1))
                .maxBackoffTime(Duration.ofSeconds(30))
                .build())
            .build()))
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

        // Wait until bucket is ready
        HeadBucketRequest waitRequest = HeadBucketRequest.builder()
            .bucket(bucketName)
            .build();

        s3Client.waiter().waitUntilBucketExists(waitRequest);
        System.out.println("Bucket created successfully: " + bucketName);

    } catch (S3Exception e) {
        System.err.println("Error creating bucket: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### List All Buckets

```java
public List<String> listAllBuckets(S3Client s3Client) {
    ListBucketsResponse response = s3Client.listBuckets();

    return response.buckets().stream()
        .map(Bucket::name)
        .collect(Collectors.toList());
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

## Basic Object Operations

### Upload File

```java
import software.amazon.awssdk.core.sync.RequestBody;
import java.nio.file.Paths;

public void uploadFile(S3Client s3Client, String bucketName, String key, String filePath) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));
    System.out.println("File uploaded: " + key);
}
```

### Download File

```java
import java.nio.file.Paths;

public void downloadFile(S3Client s3Client, String bucketName, String key, String destPath) {
    GetObjectRequest request = GetObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    s3Client.getObject(request, Paths.get(destPath));
    System.out.println("File downloaded: " + destPath);
}
```

### Get Object Metadata

```java
public Map<String, String> getObjectMetadata(S3Client s3Client, String bucketName, String key) {
    HeadObjectRequest request = HeadObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    HeadObjectResponse response = s3Client.headObject(request);
    return response.metadata();
}
```

### Delete Multiple Objects

```java
public void deleteMultipleObjects(S3Client s3Client, String bucketName, List<String> keys) {
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

    response.errors().forEach(error ->
        System.err.println("Failed to delete " + error.key() + ": " + error.message()));
}
```
