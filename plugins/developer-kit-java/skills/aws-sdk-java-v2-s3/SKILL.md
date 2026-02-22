---
name: aws-sdk-java-v2-s3
description: Provides Amazon S3 patterns and examples using AWS SDK for Java 2.x. Use when working with S3 buckets, uploading/downloading objects, multipart uploads, presigned URLs, S3 Transfer Manager, object operations, or S3-specific configurations.
category: aws
tags: [aws, s3, java, sdk, storage, objects, transfer-manager, presigned-urls]
version: 2.2.0
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# AWS SDK for Java 2.x - Amazon S3

## Overview

Amazon S3 (Simple Storage Service) is object storage built to store and retrieve any amount of data. This skill covers patterns for working with S3 using AWS SDK for Java 2.x, including bucket operations, object uploads/downloads, presigned URLs, multipart transfers, and Spring Boot integration.

## When to Use

- Creating, listing, or deleting S3 buckets
- Uploading or downloading objects with metadata and encryption
- Working with multipart uploads for large files (>100MB)
- Generating presigned URLs for temporary access
- Implementing S3 Transfer Manager for optimized transfers
- Integrating S3 with Spring Boot applications
- Testing S3 integrations with LocalStack

## Instructions

1. **Add Dependencies** - Include S3 and optional Transfer Manager dependencies
2. **Create Client** - Instantiate S3Client with region and credentials
3. **Create Bucket** - Use createBucket() with unique name
4. **Upload Objects** - Use putObject() for small files or Transfer Manager for large files
5. **Download Objects** - Use getObject() with ResponseInputStream
6. **Generate Presigned URLs** - Use S3Presigner for temporary access
7. **Configure Permissions** - Set bucket policies and access controls
8. **Set Lifecycle Rules** - Configure object expiration and transitions

## Examples

### Upload and Download

```java
// Upload file
PutObjectRequest request = PutObjectRequest.builder()
    .bucket(bucketName).key(key).build();
s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));

// Download file
s3Client.getObject(
    GetObjectRequest.builder().bucket(bucketName).key(key).build(),
    Paths.get(destPath));
```

### Presigned URL

```java
try (S3Presigner presigner = S3Presigner.builder().region(Region.US_EAST_1).build()) {
    GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
        .signatureDuration(Duration.ofMinutes(10))
        .getObjectRequest(GetObjectRequest.builder().bucket(bucket).key(key).build())
        .build();
    return presigner.presignGetObject(presignRequest).url().toString();
}
```

### Transfer Manager

```java
try (S3TransferManager transferManager = S3TransferManager.create()) {
    FileUpload upload = transferManager.uploadFile(UploadFileRequest.builder()
        .putObjectRequest(req -> req.bucket(bucket).key(key))
        .source(Paths.get(filePath))
        .build());
    CompletedFileUpload result = upload.completionFuture().join();
}
```

## Best Practices

- **Use S3 Transfer Manager** for files >100MB (handles multipart automatically)
- **Reuse S3 Client** across operations (thread-safe)
- **Enable server-side encryption** (AES-256 or KMS) for sensitive data
- **Use presigned URLs** instead of exposing credentials
- **Use appropriate storage classes** based on access patterns
- **Implement retry logic** with exponential backoff
- **Close streaming responses** to prevent connection pool exhaustion

## Constraints and Warnings

- Single PUT limited to 5GB; use multipart uploads for larger files
- Bucket names must be globally unique across all AWS accounts
- Maximum 1000 objects per DeleteObjects batch operation
- User-defined metadata limited to 2KB
- Presigned URLs maximum expiration is 7 days
- Multipart upload parts must be at least 5MB (except last part)

## References

- [S3 Object Operations Reference](./references/s3-object-operations.md)
- [S3 Transfer Manager Patterns](./references/s3-transfer-patterns.md)
- [Spring Boot Integration Guide](./references/s3-spring-boot-integration.md)

## Related Skills

- `aws-sdk-java-v2-core` - Core AWS SDK patterns
- `spring-boot-dependency-injection` - Spring DI patterns
