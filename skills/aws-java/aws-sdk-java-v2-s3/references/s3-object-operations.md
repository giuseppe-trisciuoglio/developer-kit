# S3 Object Operations Reference

## Detailed Object Operations

### Advanced Upload Patterns

#### Streaming Upload with Progress Monitoring

```java
public void uploadWithProgress(S3Client s3Client, String bucketName, String key,
                             String filePath) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    try (RequestBody file = RequestBody.fromFile(Paths.get(filePath))) {
        s3Client.putObject(request, file);
    }
}
```

#### Conditional Upload

```java
public void conditionalUpload(S3Client s3Client, String bucketName, String key,
                           String filePath, String expectedETag) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .ifMatch(expectedETag)
        .build();

    s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));
}
```

### Advanced Download Patterns

#### Range Requests for Large Files

```java
public void downloadInChunks(S3Client s3Client, String bucketName, String key,
                           String destPath, int chunkSizeMB) {
    long fileSize = getFileSize(s3Client, bucketName, key);
    int chunkSize = chunkSizeMB * 1024 * 1024;

    try (OutputStream os = new FileOutputStream(destPath)) {
        for (long start = 0; start < fileSize; start += chunkSize) {
            long end = Math.min(start + chunkSize - 1, fileSize - 1);

            GetObjectRequest request = GetObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .range("bytes=" + start + "-" + end)
                .build();

            try (ResponseInputStream<GetObjectResponse> response =
                 s3Client.getObject(request)) {
                response.transferTo(os);
            }
        }
    }
}
```

### Metadata Management

#### Setting and Retrieving Object Metadata

```java
public void setObjectMetadata(S3Client s3Client, String bucketName, String key,
                           Map<String, String> metadata) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .metadata(metadata)
        .build();

    s3Client.putObject(request, RequestBody.empty());
}

public Map<String, String> getObjectMetadata(S3Client s3Client,
                                            String bucketName, String key) {
    HeadObjectRequest request = HeadObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    HeadObjectResponse response = s3Client.headObject(request);
    return response.metadata();
}
```

### Storage Classes and Lifecycle

#### Managing Different Storage Classes

```java
public void uploadWithStorageClass(S3Client s3Client, String bucketName, String key,
                                 String filePath, StorageClass storageClass) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .storageClass(storageClass)
        .build();

    s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));
}

// Storage class options:
// STANDARD - Default storage class
// STANDARD_IA - Infrequent Access
// ONEZONE_IA - Single-zone infrequent access
// INTELLIGENT_TIERING - Automatically optimizes storage
// GLACIER - Archive storage
// DEEP_ARCHIVE - Long-term archive storage
```

### Object Tagging

#### Adding and Managing Tags

```java
public void addTags(S3Client s3Client, String bucketName, String key,
                  Map<String, String> tags) {
    Tagging tagging = Tagging.builder()
        .tagSet(tags.entrySet().stream()
            .map(entry -> Tag.builder()
                .key(entry.getKey())
                .value(entry.getValue())
                .build())
            .collect(Collectors.toList()))
        .build();

    PutObjectTaggingRequest request = PutObjectTaggingRequest.builder()
        .bucket(bucketName)
        .key(key)
        .tagging(tagging)
        .build();

    s3Client.putObjectTagging(request);
}

public Map<String, String> getTags(S3Client s3Client, String bucketName, String key) {
    GetObjectTaggingRequest request = GetObjectTaggingRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    GetObjectTaggingResponse response = s3Client.getObjectTagging(request);

    return response.tagSet().stream()
        .collect(Collectors.toMap(Tag::key, Tag::value));
}
```

### Advanced Copy Operations

#### Server-Side Copy with Metadata

```java
public void copyWithMetadata(S3Client s3Client, String sourceBucket, String sourceKey,
                           String destBucket, String destKey,
                           Map<String, String> metadata) {
    CopyObjectRequest request = CopyObjectRequest.builder()
        .sourceBucket(sourceBucket)
        .sourceKey(sourceKey)
        .destinationBucket(destBucket)
        .destinationKey(destKey)
        .metadata(metadata)
        .metadataDirective(MetadataDirective.REPLACE)
        .build();

    s3Client.copyObject(request);
}
```

## Error Handling Patterns

### Retry Mechanisms

```java
import software.amazon.awssdk.core.retry.RetryPolicy;
import software.amazon.awssdk.core.retry.backoff.FixedRetryBackoff;
import software.amazon.awssdk.core.retry.conditions.RetryCondition;

public S3Client createS3ClientWithRetry() {
    return S3Client.builder()
        .overrideConfiguration(b -> b
            .retryPolicy(RetryPolicy.builder()
                .numRetries(3)
                .retryBackoffStrategy(FixedRetryBackoff.create(
                    Duration.ofSeconds(1), 3))
                .retryCondition(RetryCondition.defaultRetryCondition())
                .build()))
        .build();
}
```

### Throttling Handling

```java
public void handleThrottling(S3Client s3Client, String bucketName, String key) {
    try {
        PutObjectRequest request = PutObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();

        s3Client.putObject(request, RequestBody.fromString("test"));

    } catch (S3Exception e) {
        if (e.statusCode() == 429) {
            // Too Many Requests - implement backoff
            try {
                Thread.sleep(1000);
                // Retry logic here
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
            }
        }
        throw e;
    }
}
```

## Performance Optimization

### Batch Operations

#### Batch Delete Objects

```java
public void batchDeleteObjects(S3Client s3Client, String bucketName,
                              List<String> keys) {
    int batchSize = 1000; // S3 limit for batch operations
    int totalBatches = (int) Math.ceil((double) keys.size() / batchSize);

    for (int i = 0; i < totalBatches; i++) {
        List<String> batchKeys = keys.subList(
            i * batchSize,
            Math.min((i + 1) * batchSize, keys.size()));

        List<ObjectIdentifier> objectIdentifiers = batchKeys.stream()
            .map(key -> ObjectIdentifier.builder().key(key).build())
            .collect(Collectors.toList());

        Delete delete = Delete.builder()
            .objects(objectIdentifiers)
            .build();

        DeleteObjectsRequest request = DeleteObjectsRequest.builder()
            .bucket(bucketName)
            .delete(delete)
            .build();

        s3Client.deleteObjects(request);
    }
}
```

### Parallel Uploads

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public void parallelUploads(S3Client s3Client, String bucketName,
                           List<String> keys, ExecutorService executor) {
    List<CompletableFuture<Void>> futures = new ArrayList<>();

    for (String key : keys) {
        CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
            PutObjectRequest request = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .build();

            s3Client.putObject(request, RequestBody.fromString("data"));
        }, executor);

        futures.add(future);
    }

    CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
}
```

## Security Considerations

### Access Control

#### Setting Object ACLs

```java
public void setObjectAcl(S3Client s3Client, String bucketName, String key,
                        CannedAccessControlList acl) {
    PutObjectAclRequest request = PutObjectAclRequest.builder()
        .bucket(bucketName)
        .key(key)
        .acl(acl)
        .build();

    s3Client.putObjectAcl(request);
}

// ACL options:
// private, public-read, public-read-write, authenticated-read,
// aws-exec-read, bucket-owner-read, bucket-owner-full-control
```

#### Encryption

```java
public void encryptedUpload(S3Client s3Client, String bucketName, String key,
                          String filePath, String kmsKeyId) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .serverSideEncryption(ServerSideEncryption.AWS_KMS)
        .ssekmsKeyId(kmsKeyId)
        .build();

    s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));
}
```

## Monitoring and Logging

#### Upload Completion Events

```java
public void uploadWithMonitoring(S3Client s3Client, String bucketName, String key,
                             String filePath) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    Response<PutObjectResponse> response = s3Client.putObject(request,
        RequestBody.fromFile(Paths.get(filePath)));

    System.out.println("Upload completed with ETag: " +
                       response.response().eTag());
}
```

## Integration Patterns

### Event Notifications

```java
public void setupEventNotifications(S3Client s3Client, String bucketName) {
    NotificationConfiguration configuration = NotificationConfiguration.builder()
        .topicConfigurations(TopicConfiguration.builder()
            .topicArn("arn:aws:sns:us-east-1:123456789012:my-topic")
            .events(Event.OBJECT_CREATED_PUT, Event.OBJECT_CREATED_POST)
            .build())
        .build();

    PutBucketNotificationConfigurationRequest request =
        PutBucketNotificationConfigurationRequest.builder()
            .bucket(bucketName)
            .notificationConfiguration(configuration)
            .build();

    s3Client.putBucketNotificationConfiguration(request);
}
```