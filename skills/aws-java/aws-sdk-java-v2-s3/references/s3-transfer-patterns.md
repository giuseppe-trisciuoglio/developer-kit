# S3 Transfer Patterns Reference

## S3 Transfer Manager Advanced Patterns

### Configuration and Optimization

#### Custom Transfer Manager Configuration

```java
import software.amazon.awssdk.transfer.s3.S3TransferManager;
import software.amazon.awssdk.transfer.s3.model.UploadFileRequest;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import java.time.Duration;

public S3TransferManager createOptimizedTransferManager(S3Client s3Client) {
    return S3TransferManager.builder()
        .s3Client(s3Client)
        .storageProvider(ApacheHttpClient.builder()
            .maxConnections(200)
            .connectionTimeout(Duration.ofSeconds(5))
            .socketTimeout(Duration.ofSeconds(60))
            .build())
        .build();
}
```

#### Parallel Upload Configuration

```java
public void configureParallelUploads() {
    S3TransferManager transferManager = S3TransferManager.create();

    FileUpload upload = transferManager.uploadFile(
        UploadFileRequest.builder()
            .putObjectRequest(req -> req
                .bucket("my-bucket")
                .key("large-file.bin"))
            .source(Paths.get("large-file.bin"))
            .build());

    // Track upload progress
    upload.progressFuture().thenAccept(progress -> {
        System.out.println("Upload progress: " + progress.progressPercent());
    });

    // Handle completion
    upload.completionFuture().thenAccept(result -> {
        System.out.println("Upload completed with ETag: " +
            result.response().eTag());
    });
}
```

### Advanced Upload Patterns

#### Multipart Upload with Progress Monitoring

```java
public void multipartUploadWithProgress(S3Client s3Client, String bucketName,
                                     String key, String filePath) {
    int partSize = 5 * 1024 * 1024; // 5 MB parts
    File file = new File(filePath);

    CreateMultipartUploadRequest createRequest = CreateMultipartUploadRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    CreateMultipartUploadResponse createResponse = s3Client.createMultipartUpload(createRequest);
    String uploadId = createResponse.uploadId();

    List<CompletedPart> completedParts = new ArrayList<>();
    long uploadedBytes = 0;
    long totalBytes = file.length();

    try (FileInputStream fis = new FileInputStream(file)) {
        byte[] buffer = new byte[partSize];
        int partNumber = 1;

        while (true) {
            int bytesRead = fis.read(buffer);
            if (bytesRead == -1) break;

            byte[] partData = Arrays.copyOf(buffer, bytesRead);

            UploadPartRequest uploadRequest = UploadPartRequest.builder()
                .bucket(bucketName)
                .key(key)
                .uploadId(uploadId)
                .partNumber(partNumber)
                .build();

            UploadPartResponse uploadResponse = s3Client.uploadPart(
                uploadRequest, RequestBody.fromBytes(partData));

            completedParts.add(CompletedPart.builder()
                .partNumber(partNumber)
                .eTag(uploadResponse.eTag())
                .build());

            uploadedBytes += bytesRead;
            partNumber++;

            // Log progress
            double progress = (double) uploadedBytes / totalBytes * 100;
            System.out.printf("Upload progress: %.2f%%%n", progress);
        }

        CompleteMultipartUploadRequest completeRequest =
            CompleteMultipartUploadRequest.builder()
                .bucket(bucketName)
                .key(key)
                .uploadId(uploadId)
                .multipartUpload(CompletedMultipartUpload.builder()
                    .parts(completedParts)
                    .build())
                .build();

        s3Client.completeMultipartUpload(completeRequest);

    } catch (Exception e) {
        // Abort on failure
        AbortMultipartUploadRequest abortRequest =
            AbortMultipartUploadRequest.builder()
                .bucket(bucketName)
                .key(key)
                .uploadId(uploadId)
                .build();

        s3Client.abortMultipartUpload(abortRequest);
        throw new RuntimeException("Multipart upload failed", e);
    }
}
```

#### Resume Interrupted Uploads

```java
public void resumeUpload(S3Client s3Client, String bucketName, String key,
                       String filePath, String existingUploadId) {
    ListMultipartUploadsRequest listRequest = ListMultipartUploadsRequest.builder()
        .bucket(bucketName)
        .prefix(key)
        .build();

    ListMultipartUploadsResponse listResponse = s3Client.listMultipartUploads(listRequest);

    // Check if upload already exists
    boolean uploadExists = listResponse.uploads().stream()
        .anyMatch(upload -> upload.key().equals(key) &&
                           upload.uploadId().equals(existingUploadId));

    if (uploadExists) {
        // Resume existing upload
        continueExistingUpload(s3Client, bucketName, key, existingUploadId, filePath);
    } else {
        // Start new upload
        multipartUploadWithProgress(s3Client, bucketName, key, filePath);
    }
}

private void continueExistingUpload(S3Client s3Client, String bucketName,
                                 String key, String uploadId, String filePath) {
    // List already uploaded parts
    ListPartsRequest listPartsRequest = ListPartsRequest.builder()
        .bucket(bucketName)
        .key(key)
        .uploadId(uploadId)
        .build();

    ListPartsResponse listPartsResponse = s3Client.listParts(listPartsRequest);

    List<CompletedPart> completedParts = listPartsResponse.parts().stream()
        .map(part -> CompletedPart.builder()
            .partNumber(part.partNumber())
            .eTag(part.eTag())
            .build())
        .collect(Collectors.toList());

    // Upload remaining parts
    // ... implementation of remaining parts upload
}
```

### Advanced Download Patterns

#### Partial File Download

```java
public void downloadPartialFile(S3Client s3Client, String bucketName, String key,
                              String destPath, long startByte, long endByte) {
    GetObjectRequest request = GetObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .range("bytes=" + startByte + "-" + endByte)
        .build();

    try (ResponseInputStream<GetObjectResponse> response = s3Client.getObject(request);
         OutputStream outputStream = new FileOutputStream(destPath)) {

        response.transferTo(outputStream);
        System.out.println("Partial download completed: " +
            (endByte - startByte + 1) + " bytes");
    }
}
```

#### Parallel Downloads

```java
import java.util.concurrent.*;
import java.util.stream.*;

public void parallelDownloads(S3Client s3Client, String bucketName,
                           String key, String destPath, int chunkCount) {
    long fileSize = getFileSize(s3Client, bucketName, key);
    long chunkSize = fileSize / chunkCount;

    ExecutorService executor = Executors.newFixedThreadPool(chunkCount);
    List<Future<Void>> futures = new ArrayList<>();

    for (int i = 0; i < chunkCount; i++) {
        long start = i * chunkSize;
        long end = (i == chunkCount - 1) ? fileSize - 1 : start + chunkSize - 1;

        Future<Void> future = executor.submit(() -> {
            downloadPartialFile(s3Client, bucketName, key,
                destPath + ".part" + i, start, end);
            return null;
        });

        futures.add(future);
    }

    // Wait for all downloads to complete
    for (Future<Void> future : futures) {
        try {
            future.get();
        } catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException("Download failed", e);
        }
    }

    // Combine chunks
    combineChunks(destPath, chunkCount);

    executor.shutdown();
}

private void combineChunks(String baseName, int chunkCount) throws IOException {
    try (OutputStream outputStream = new FileOutputStream(baseName)) {
        for (int i = 0; i < chunkCount; i++) {
            String chunkFile = baseName + ".part" + i;
            try (InputStream inputStream = new FileInputStream(chunkFile)) {
                inputStream.transferTo(outputStream);
            }
            new File(chunkFile).delete();
        }
    }
}
```

### Error Handling and Retry

#### Upload with Exponential Backoff

```java
import software.amazon.awssdk.core.retry.conditions.*;
import software.amazon.awssdk.core.retry.*;
import software.amazon.awssdk.core.retry.backoff.*;

public void resilientUpload(S3Client s3Client, String bucketName, String key,
                           String filePath) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    // Configure retry policy
    S3Client retryS3Client = S3Client.builder()
        .overrideConfiguration(b -> b
            .retryPolicy(RetryPolicy.builder()
                .numRetries(5)
                .retryBackoffStrategy(
                    ExponentialRetryBackoff.builder()
                        .baseDelay(Duration.ofSeconds(1))
                        .maxBackoffTime(Duration.ofSeconds(30))
                        .build())
                .retryCondition(
                    RetryCondition.or(
                        RetryCondition.defaultRetryCondition(),
                        RetryCondition.create(response ->
                            response.httpResponse().is5xxServerError()))
                )
                .build()))
        .build();

    retryS3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));
}
```

#### Upload with Checkpoint

```java
import java.nio.file.*;

public void uploadWithCheckpoint(S3Client s3Client, String bucketName,
                               String key, String filePath) {
    String checkpointFile = filePath + ".checkpoint";
    Path checkpointPath = Paths.get(checkpointFile);

    long startPos = 0;
    if (Files.exists(checkpointPath)) {
        // Read checkpoint
        try {
            startPos = Long.parseLong(Files.readString(checkpointPath));
        } catch (IOException e) {
            throw new RuntimeException("Failed to read checkpoint", e);
        }
    }

    if (startPos > 0) {
        // Resume upload
        continueUploadFromCheckpoint(s3Client, bucketName, key, filePath, startPos);
    } else {
        // Start new upload
        startNewUpload(s3Client, bucketName, key, filePath);
    }

    // Update checkpoint
    long endPos = new File(filePath).length();
    try {
        Files.writeString(checkpointPath, String.valueOf(endPos));
    } catch (IOException e) {
        throw new RuntimeException("Failed to write checkpoint", e);
    }
}

private void continueUploadFromCheckpoint(S3Client s3Client, String bucketName,
                                        String key, String filePath, long startPos) {
    // Implement resume logic
}

private void startNewUpload(S3Client s3Client, String bucketName,
                          String key, String filePath) {
    // Implement initial upload logic
}
```

### Performance Tuning

#### Buffer Configuration

```java
public S3Client configureLargeBuffer() {
    return S3Client.builder()
        .overrideConfiguration(b -> b
            .apiCallAttemptTimeout(Duration.ofMinutes(5))
            .apiCallTimeout(Duration.ofMinutes(10)))
        .build();
}

public S3TransferManager configureHighThroughput() {
    return S3TransferManager.builder()
        .multipartUploadThreshold(8 * 1024 * 1024) // 8 MB
        .multipartUploadPartSize(10 * 1024 * 1024) // 10 MB
        .build();
}
```

#### Network Optimization

```java
public S3Client createOptimizedS3Client() {
    return S3Client.builder()
        .httpClientBuilder(ApacheHttpClient.builder()
            .maxConnections(200)
            .connectionPoolStrategy(ConnectionPoolStrategy.defaultStrategy())
            .socketTimeout(Duration.ofSeconds(30))
            .connectionTimeout(Duration.ofSeconds(5))
            .connectionAcquisitionTimeout(Duration.ofSeconds(30))
            .build())
        .region(Region.US_EAST_1)
        .build();
}
```

### Monitoring and Metrics

#### Upload Progress Tracking

```java
public void uploadWithProgressTracking(S3Client s3Client, String bucketName,
                                    String key, String filePath) {
    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    // Create progress listener
    software.amazon.awssdk.core.ProgressListener progressListener =
        progressEvent -> {
            System.out.println("Transferred: " +
                progressEvent.transferredBytes() + " bytes");
            System.out.println("Progress: " +
                progressEvent.progressPercent() + "%");
        };

    Response<PutObjectResponse> response = s3Client.putObject(
        request,
        RequestBody.fromFile(Paths.get(filePath)),
        software.amazon.awssdk.core.sync.RequestBody.fromFile(Paths.get(filePath))
            .contentLength(new File(filePath).length()),
        progressListener);

    System.out.println("Upload complete. ETag: " +
        response.response().eTag());
}
```

#### Throughput Measurement

```java
public void measureUploadThroughput(S3Client s3Client, String bucketName,
                                  String key, String filePath) {
    long startTime = System.currentTimeMillis();
    long fileSize = new File(filePath).length();

    PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));

    long endTime = System.currentTimeMillis();
    long duration = endTime - startTime;
    double throughput = (fileSize * 1000.0) / duration / (1024 * 1024); // MB/s

    System.out.printf("Upload throughput: %.2f MB/s%n", throughput);
}
```

## Testing and Validation

#### Upload Validation

```java
public void validateUpload(S3Client s3Client, String bucketName, String key,
                         String localFilePath) {
    // Download file from S3
    byte[] s3Content = downloadObject(s3Client, bucketName, key);

    // Read local file
    byte[] localContent = Files.readAllBytes(Paths.get(localFilePath));

    // Validate content matches
    if (!Arrays.equals(s3Content, localContent)) {
        throw new RuntimeException("Upload validation failed: content mismatch");
    }

    // Verify file size
    long s3Size = s3Content.length;
    long localSize = localContent.length;
    if (s3Size != localSize) {
        throw new RuntimeException("Upload validation failed: size mismatch");
    }

    System.out.println("Upload validation successful");
}
```