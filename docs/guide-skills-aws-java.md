# Complete Guide to AWS Java SDK v2 Skills

This comprehensive guide documents all AWS Java SDK v2 skills available in the Developer Kit, organized by service with detailed explanations, practical examples, and best practices for building cloud-native Java applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Core SDK Skills](#core-sdk-skills)
3. [Storage Services](#storage-services)
4. [Database Services](#database-services)
5. [Compute Services](#compute-services)
6. [Messaging Services](#messaging-services)
7. [Security Services](#security-services)
8. [Common Workflows](#common-workflows)
9. [Best Practices](#best-practices)

---

## Overview

The AWS Java SDK v2 skills collection provides comprehensive patterns for integrating AWS services into Spring Boot applications, covering everything from basic SDK setup to advanced service-specific patterns.

### Skill Categories

- **Core SDK**: Configuration, credentials, clients
- **Storage**: S3 for object storage
- **Database**: DynamoDB for NoSQL, RDS for relational databases
- **Compute**: Lambda for serverless functions
- **Messaging**: SQS for queues, SNS for pub/sub
- **Security**: KMS for encryption, Secrets Manager for secrets

### Technology Stack

- **AWS SDK for Java**: 2.x
- **Spring Boot**: 3.5.x or later
- **Java**: 17+
- **Spring Cloud AWS**: 3.x (optional, for Spring integration)
- **Testcontainers**: LocalStack for integration testing

### Key Concepts

- **Async Clients**: Non-blocking, reactive AWS service clients
- **Waiters**: Polling utilities for resource state changes
- **Pagination**: Handle large result sets efficiently
- **Credentials**: IAM roles, profiles, environment variables
- **Regions**: Service endpoint configuration

---

## Core SDK Skills

### aws-sdk-java-v2-core

**Purpose**: Set up AWS SDK for Java v2 in Spring Boot applications with proper configuration, credential management, and client initialization.

**When to use:**
- Starting a new AWS-integrated Spring Boot project
- Configuring AWS credentials
- Setting up AWS service clients
- Managing regions and endpoints
- Implementing retry and timeout policies

**Key Patterns:**

1. **Dependencies**
```xml
<!-- AWS SDK BOM for version management -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>bom</artifactId>
            <version>2.25.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <!-- Core SDK -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>sdk-core</artifactId>
    </dependency>

    <!-- Service-specific dependencies (examples) -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>s3</artifactId>
    </dependency>

    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>dynamodb</artifactId>
    </dependency>

    <!-- Enhanced DynamoDB client -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>dynamodb-enhanced</artifactId>
    </dependency>
</dependencies>
```

2. **Configuration Properties**
```yaml
aws:
  region: us-east-1
  endpoint: ${AWS_ENDPOINT:}  # For LocalStack
  credentials:
    access-key-id: ${AWS_ACCESS_KEY_ID:}
    secret-access-key: ${AWS_SECRET_ACCESS_KEY:}
    profile: ${AWS_PROFILE:default}
  
  # Service-specific configuration
  s3:
    bucket-name: my-application-bucket
  
  dynamodb:
    table-prefix: ${ENVIRONMENT:dev}-
  
  sqs:
    queue-url: ${SQS_QUEUE_URL:}
  
  # Client configuration
  client:
    connection-timeout: PT10S
    read-timeout: PT30S
    max-retries: 3
```

3. **AWS Configuration Class**
```java
@Configuration
@ConfigurationProperties(prefix = "aws")
@Data
public class AwsProperties {
    private String region = "us-east-1";
    private String endpoint;
    private Credentials credentials = new Credentials();
    private Client client = new Client();

    @Data
    public static class Credentials {
        private String accessKeyId;
        private String secretAccessKey;
        private String profile = "default";
    }

    @Data
    public static class Client {
        private Duration connectionTimeout = Duration.ofSeconds(10);
        private Duration readTimeout = Duration.ofSeconds(30);
        private int maxRetries = 3;
    }
}
```

4. **Client Configuration**
```java
@Configuration
@EnableConfigurationProperties(AwsProperties.class)
public class AwsClientConfig {

    @Bean
    public Region region(AwsProperties properties) {
        return Region.of(properties.getRegion());
    }

    @Bean
    public AwsCredentialsProvider credentialsProvider(AwsProperties properties) {
        // Priority order:
        // 1. Static credentials from properties (for LocalStack)
        // 2. AWS profile
        // 3. Default credential provider chain (IAM roles, env vars)
        
        if (properties.getCredentials().getAccessKeyId() != null) {
            return StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    properties.getCredentials().getAccessKeyId(),
                    properties.getCredentials().getSecretAccessKey()
                )
            );
        }

        if (properties.getCredentials().getProfile() != null) {
            return ProfileCredentialsProvider.create(
                properties.getCredentials().getProfile()
            );
        }

        return DefaultCredentialsProvider.create();
    }

    @Bean
    public ClientOverrideConfiguration clientOverrideConfiguration(AwsProperties properties) {
        return ClientOverrideConfiguration.builder()
            .apiCallTimeout(properties.getClient().getReadTimeout())
            .apiCallAttemptTimeout(properties.getClient().getConnectionTimeout())
            .retryPolicy(RetryPolicy.builder()
                .numRetries(properties.getClient().getMaxRetries())
                .build())
            .build();
    }
}
```

5. **Async vs Sync Clients**
```java
// Synchronous client (blocking)
@Bean
public S3Client s3Client(
        Region region,
        AwsCredentialsProvider credentialsProvider,
        ClientOverrideConfiguration clientConfig) {
    
    return S3Client.builder()
        .region(region)
        .credentialsProvider(credentialsProvider)
        .overrideConfiguration(clientConfig)
        .build();
}

// Asynchronous client (non-blocking)
@Bean
public S3AsyncClient s3AsyncClient(
        Region region,
        AwsCredentialsProvider credentialsProvider,
        ClientOverrideConfiguration clientConfig) {
    
    return S3AsyncClient.builder()
        .region(region)
        .credentialsProvider(credentialsProvider)
        .overrideConfiguration(clientConfig)
        .build();
}
```

6. **Local Development with LocalStack**
```java
@Configuration
@Profile("local")
public class LocalStackConfig {

    @Bean
    public S3Client localS3Client() {
        return S3Client.builder()
            .region(Region.US_EAST_1)
            .endpointOverride(URI.create("http://localhost:4566"))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create("test", "test")
            ))
            .forcePathStyle(true)  // Required for LocalStack
            .build();
    }
}
```

**Best Practices:**
- Use BOM for consistent AWS SDK versions
- Prefer IAM roles over static credentials in production
- Use async clients for better performance
- Configure appropriate timeouts and retries
- Use LocalStack for local development
- Use profiles for different environments
- Implement proper error handling
- Close clients on application shutdown

**References:**
- `skills/aws-java/aws-sdk-java-v2-core/SKILL.md`

---

## Storage Services

### aws-sdk-java-v2-s3

**Purpose**: Implement S3 operations for object storage including upload, download, listing, and lifecycle management.

**When to use:**
- Storing files and documents
- Building file upload/download features
- Implementing backup solutions
- Managing static assets
- Generating pre-signed URLs

**Key Patterns:**

1. **S3 Client Configuration**
```java
@Configuration
public class S3Config {

    @Bean
    public S3Client s3Client(
            Region region,
            AwsCredentialsProvider credentialsProvider) {
        
        return S3Client.builder()
            .region(region)
            .credentialsProvider(credentialsProvider)
            .build();
    }

    @Bean
    public S3Presigner s3Presigner(
            Region region,
            AwsCredentialsProvider credentialsProvider) {
        
        return S3Presigner.builder()
            .region(region)
            .credentialsProvider(credentialsProvider)
            .build();
    }
}
```

2. **Upload File**
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class S3Service {
    
    private final S3Client s3Client;
    
    @Value("${aws.s3.bucket-name}")
    private String bucketName;

    public String uploadFile(String key, byte[] fileContent, String contentType) {
        try {
            PutObjectRequest request = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .contentType(contentType)
                .build();

            s3Client.putObject(request, RequestBody.fromBytes(fileContent));
            
            log.info("Uploaded file to S3: bucket={}, key={}", bucketName, key);
            return key;
            
        } catch (S3Exception e) {
            log.error("Failed to upload file to S3", e);
            throw new FileUploadException("Failed to upload file", e);
        }
    }

    public String uploadFile(String key, InputStream inputStream, long contentLength) {
        try {
            PutObjectRequest request = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .build();

            s3Client.putObject(request, 
                RequestBody.fromInputStream(inputStream, contentLength));
            
            return key;
            
        } catch (S3Exception e) {
            throw new FileUploadException("Failed to upload file", e);
        }
    }
}
```

3. **Download File**
```java
public byte[] downloadFile(String key) {
    try {
        GetObjectRequest request = GetObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();

        ResponseBytes<GetObjectResponse> responseBytes = 
            s3Client.getObjectAsBytes(request);
        
        log.info("Downloaded file from S3: bucket={}, key={}", bucketName, key);
        return responseBytes.asByteArray();
        
    } catch (NoSuchKeyException e) {
        throw new FileNotFoundException("File not found: " + key);
    } catch (S3Exception e) {
        throw new FileDownloadException("Failed to download file", e);
    }
}

public InputStream downloadFileAsStream(String key) {
    try {
        GetObjectRequest request = GetObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();

        return s3Client.getObject(request);
        
    } catch (S3Exception e) {
        throw new FileDownloadException("Failed to download file", e);
    }
}
```

4. **List Objects**
```java
public List<S3ObjectSummary> listFiles(String prefix) {
    try {
        ListObjectsV2Request request = ListObjectsV2Request.builder()
            .bucket(bucketName)
            .prefix(prefix)
            .maxKeys(1000)
            .build();

        ListObjectsV2Response response = s3Client.listObjectsV2(request);
        
        return response.contents().stream()
            .map(s3Object -> new S3ObjectSummary(
                s3Object.key(),
                s3Object.size(),
                s3Object.lastModified()
            ))
            .toList();
            
    } catch (S3Exception e) {
        throw new S3OperationException("Failed to list files", e);
    }
}
```

5. **Delete File**
```java
public void deleteFile(String key) {
    try {
        DeleteObjectRequest request = DeleteObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();

        s3Client.deleteObject(request);
        log.info("Deleted file from S3: bucket={}, key={}", bucketName, key);
        
    } catch (S3Exception e) {
        throw new S3OperationException("Failed to delete file", e);
    }
}

public void deleteFiles(List<String> keys) {
    try {
        List<ObjectIdentifier> objectIds = keys.stream()
            .map(key -> ObjectIdentifier.builder().key(key).build())
            .toList();

        Delete delete = Delete.builder()
            .objects(objectIds)
            .build();

        DeleteObjectsRequest request = DeleteObjectsRequest.builder()
            .bucket(bucketName)
            .delete(delete)
            .build();

        s3Client.deleteObjects(request);
        log.info("Deleted {} files from S3", keys.size());
        
    } catch (S3Exception e) {
        throw new S3OperationException("Failed to delete files", e);
    }
}
```

6. **Generate Pre-signed URL**
```java
@RequiredArgsConstructor
@Service
public class S3PresignedUrlService {
    
    private final S3Presigner s3Presigner;
    
    @Value("${aws.s3.bucket-name}")
    private String bucketName;

    public String generateDownloadUrl(String key, Duration expiration) {
        GetObjectRequest getObjectRequest = GetObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();

        GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
            .signatureDuration(expiration)
            .getObjectRequest(getObjectRequest)
            .build();

        PresignedGetObjectRequest presignedRequest = 
            s3Presigner.presignGetObject(presignRequest);

        return presignedRequest.url().toString();
    }

    public String generateUploadUrl(String key, Duration expiration) {
        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
            .bucket(bucketName)
            .key(key)
            .build();

        PutObjectPresignRequest presignRequest = PutObjectPresignRequest.builder()
            .signatureDuration(expiration)
            .putObjectRequest(putObjectRequest)
            .build();

        PresignedPutObjectRequest presignedRequest = 
            s3Presigner.presignPutObject(presignRequest);

        return presignedRequest.url().toString();
    }
}
```

7. **Multipart Upload (Large Files)**
```java
public String uploadLargeFile(String key, File file) {
    CreateMultipartUploadRequest createRequest = CreateMultipartUploadRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    CreateMultipartUploadResponse createResponse = 
        s3Client.createMultipartUpload(createRequest);
    
    String uploadId = createResponse.uploadId();

    try {
        List<CompletedPart> completedParts = new ArrayList<>();
        long partSize = 5 * 1024 * 1024; // 5 MB
        long fileSize = file.length();
        long filePosition = 0;
        
        for (int partNumber = 1; filePosition < fileSize; partNumber++) {
            long currentPartSize = Math.min(partSize, fileSize - filePosition);

            UploadPartRequest uploadPartRequest = UploadPartRequest.builder()
                .bucket(bucketName)
                .key(key)
                .uploadId(uploadId)
                .partNumber(partNumber)
                .contentLength(currentPartSize)
                .build();

            UploadPartResponse uploadPartResponse = s3Client.uploadPart(
                uploadPartRequest,
                RequestBody.fromFile(file, filePosition, currentPartSize)
            );

            completedParts.add(CompletedPart.builder()
                .partNumber(partNumber)
                .eTag(uploadPartResponse.eTag())
                .build());

            filePosition += currentPartSize;
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
        
        log.info("Completed multipart upload: key={}", key);
        return key;

    } catch (Exception e) {
        s3Client.abortMultipartUpload(AbortMultipartUploadRequest.builder()
            .bucket(bucketName)
            .key(key)
            .uploadId(uploadId)
            .build());
        
        throw new FileUploadException("Failed to upload large file", e);
    }
}
```

**Best Practices:**
- Use multipart upload for files > 100 MB
- Generate pre-signed URLs for direct client uploads
- Implement retry logic for transient errors
- Use S3 Transfer Manager for optimized uploads
- Enable versioning for critical buckets
- Implement lifecycle policies for cost optimization
- Use appropriate storage classes (Standard, IA, Glacier)
- Encrypt sensitive data (SSE-S3, SSE-KMS)
- Implement proper access controls (bucket policies, IAM)

**References:**
- `skills/aws-java/aws-sdk-java-v2-s3/SKILL.md`

---

## Database Services

### aws-sdk-java-v2-dynamodb

**Purpose**: Implement DynamoDB operations using the Enhanced Client for type-safe, high-level database access.

**When to use:**
- Building NoSQL data models
- Implementing single-table design patterns
- High-performance key-value storage
- Serverless application data stores
- Event sourcing and CQRS patterns

**Key Patterns:**

1. **Enhanced Client Configuration**
```java
@Configuration
public class DynamoDbConfig {

    @Bean
    public DynamoDbClient dynamoDbClient(
            Region region,
            AwsCredentialsProvider credentialsProvider) {
        
        return DynamoDbClient.builder()
            .region(region)
            .credentialsProvider(credentialsProvider)
            .build();
    }

    @Bean
    public DynamoDbEnhancedClient dynamoDbEnhancedClient(DynamoDbClient dynamoDbClient) {
        return DynamoDbEnhancedClient.builder()
            .dynamoDbClient(dynamoDbClient)
            .build();
    }
}
```

2. **Entity Definition**
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@DynamoDbBean
public class UserEntity {
    
    private String userId;
    private String email;
    private String name;
    private UserStatus status;
    private Instant createdAt;
    private Instant updatedAt;

    @DynamoDbPartitionKey
    @DynamoDbAttribute("PK")
    public String getUserId() {
        return userId;
    }

    @DynamoDbSortKey
    @DynamoDbAttribute("SK")
    public String getEmail() {
        return email;
    }

    @DynamoDbAttribute("Name")
    public String getName() {
        return name;
    }

    @DynamoDbAttribute("Status")
    public UserStatus getStatus() {
        return status;
    }

    @DynamoDbAttribute("CreatedAt")
    public Instant getCreatedAt() {
        return createdAt;
    }

    @DynamoDbAttribute("UpdatedAt")
    @DynamoDbUpdateBehavior(UpdateBehavior.WRITE_IF_NOT_EXISTS)
    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
```

3. **Repository Implementation**
```java
@Repository
@RequiredArgsConstructor
public class UserDynamoDbRepository {
    
    private final DynamoDbEnhancedClient enhancedClient;
    
    @Value("${aws.dynamodb.table-prefix}")
    private String tablePrefix;

    private DynamoDbTable<UserEntity> getUserTable() {
        return enhancedClient.table(
            tablePrefix + "users",
            TableSchema.fromBean(UserEntity.class)
        );
    }

    public UserEntity save(UserEntity user) {
        user.setUpdatedAt(Instant.now());
        getUserTable().putItem(user);
        return user;
    }

    public Optional<UserEntity> findById(String userId, String email) {
        Key key = Key.builder()
            .partitionValue(userId)
            .sortValue(email)
            .build();

        return Optional.ofNullable(getUserTable().getItem(key));
    }

    public void delete(String userId, String email) {
        Key key = Key.builder()
            .partitionValue(userId)
            .sortValue(email)
            .build();

        getUserTable().deleteItem(key);
    }

    public List<UserEntity> findByUserId(String userId) {
        QueryConditional queryConditional = QueryConditional
            .keyEqualTo(Key.builder().partitionValue(userId).build());

        return getUserTable()
            .query(queryConditional)
            .items()
            .stream()
            .toList();
    }
}
```

4. **Query Operations**
```java
public List<UserEntity> findActiveUsers() {
    DynamoDbIndex<UserEntity> statusIndex = getUserTable()
        .index("StatusIndex");

    QueryConditional queryConditional = QueryConditional
        .keyEqualTo(Key.builder()
            .partitionValue(UserStatus.ACTIVE.name())
            .build());

    return statusIndex
        .query(queryConditional)
        .items()
        .stream()
        .toList();
}

public Page<UserEntity> findUsersPaginated(String lastEvaluatedKey, int limit) {
    QueryEnhancedRequest.Builder requestBuilder = QueryEnhancedRequest.builder()
        .limit(limit);

    if (lastEvaluatedKey != null) {
        Map<String, AttributeValue> exclusiveStartKey = Map.of(
            "PK", AttributeValue.builder().s(lastEvaluatedKey).build()
        );
        requestBuilder.exclusiveStartKey(exclusiveStartKey);
    }

    PageIterable<UserEntity> pages = getUserTable()
        .query(requestBuilder.build());

    Page<UserEntity> firstPage = pages.stream().findFirst().orElse(null);
    
    if (firstPage == null) {
        return new Page<>(List.of(), null);
    }

    String nextToken = firstPage.lastEvaluatedKey() != null
        ? firstPage.lastEvaluatedKey().get("PK").s()
        : null;

    return new Page<>(firstPage.items(), nextToken);
}
```

5. **Batch Operations**
```java
public void batchSave(List<UserEntity> users) {
    WriteBatch.Builder<UserEntity> batchBuilder = WriteBatch.builder(UserEntity.class)
        .mappedTableResource(getUserTable());

    users.forEach(user -> {
        user.setUpdatedAt(Instant.now());
        batchBuilder.addPutItem(user);
    });

    enhancedClient.batchWriteItem(BatchWriteItemEnhancedRequest.builder()
        .writeBatches(batchBuilder.build())
        .build());
}

public List<UserEntity> batchGet(List<Key> keys) {
    ReadBatch.Builder<UserEntity> batchBuilder = ReadBatch.builder(UserEntity.class)
        .mappedTableResource(getUserTable());

    keys.forEach(batchBuilder::addGetItem);

    BatchGetResultPageIterable resultPages = enhancedClient.batchGetItem(
        BatchGetItemEnhancedRequest.builder()
            .readBatches(batchBuilder.build())
            .build()
    );

    return resultPages.resultsForTable(getUserTable())
        .stream()
        .flatMap(page -> page.stream())
        .toList();
}
```

6. **Conditional Writes**
```java
public void updateUserStatus(String userId, String email, UserStatus newStatus) {
    Expression conditionalExpression = Expression.builder()
        .expression("attribute_exists(PK) AND #status <> :newStatus")
        .expressionNames(Map.of("#status", "Status"))
        .expressionValues(Map.of(
            ":newStatus", AttributeValue.builder().s(newStatus.name()).build()
        ))
        .build();

    UserEntity user = UserEntity.builder()
        .userId(userId)
        .email(email)
        .status(newStatus)
        .updatedAt(Instant.now())
        .build();

    try {
        getUserTable().updateItem(UpdateItemEnhancedRequest.builder(UserEntity.class)
            .item(user)
            .conditionExpression(conditionalExpression)
            .build());
    } catch (ConditionalCheckFailedException e) {
        throw new ConcurrentModificationException("User status already updated", e);
    }
}
```

**Best Practices:**
- Use Enhanced Client for type-safe operations
- Design partition keys for even distribution
- Use Global Secondary Indexes (GSI) for alternative access patterns
- Implement pagination for large result sets
- Use conditional writes for optimistic locking
- Enable Point-in-Time Recovery (PITR) for production tables
- Use DynamoDB Streams for change data capture
- Monitor consumed capacity and throttling
- Use batch operations for bulk writes (max 25 items)
- Implement exponential backoff for throttling

**References:**
- `skills/aws-java/aws-sdk-java-v2-dynamodb/SKILL.md`

---

### aws-rds-spring-boot-integration

**Purpose**: Integrate AWS RDS (Relational Database Service) with Spring Boot using Spring Data JPA.

**When to use:**
- Building relational database applications
- Using PostgreSQL, MySQL, or other RDS databases
- Migrating from local databases to cloud
- Implementing complex queries and transactions

**Key Patterns:**

1. **Dependencies**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>

<!-- AWS Secrets Manager for credentials -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>secretsmanager</artifactId>
</dependency>
```

2. **Configuration with Secrets Manager**
```java
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource dataSource(
            SecretsManagerClient secretsManagerClient,
            @Value("${aws.rds.secret-name}") String secretName) {
        
        // Retrieve database credentials from Secrets Manager
        GetSecretValueRequest request = GetSecretValueRequest.builder()
            .secretId(secretName)
            .build();

        GetSecretValueResponse response = secretsManagerClient.getSecretValue(request);
        DatabaseCredentials credentials = parseCredentials(response.secretString());

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(credentials.jdbcUrl());
        config.setUsername(credentials.username());
        config.setPassword(credentials.password());
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(2);
        config.setConnectionTimeout(30000);
        
        return new HikariDataSource(config);
    }

    private DatabaseCredentials parseCredentials(String json) {
        // Parse JSON from Secrets Manager
        // ...
    }
}
```

**Best Practices:**
- Store credentials in AWS Secrets Manager
- Use IAM database authentication when possible
- Enable SSL/TLS for database connections
- Configure connection pooling (HikariCP)
- Use RDS Proxy for Lambda functions
- Enable automated backups
- Use Multi-AZ deployments for high availability
- Monitor database performance with CloudWatch

**References:**
- `skills/aws-java/aws-rds-spring-boot-integration/SKILL.md`

---

## Compute Services

### aws-sdk-java-v2-lambda

**Purpose**: Implement AWS Lambda functions in Java and integrate with Lambda from Spring Boot applications.

**When to use:**
- Building serverless applications
- Implementing event-driven workflows
- Processing asynchronous tasks
- Scaling compute automatically
- Reducing infrastructure management

**Key Patterns:**

1. **Lambda Handler**
```java
public class UserRegistrationHandler implements RequestHandler<UserRegistrationEvent, UserRegistrationResponse> {

    private final UserService userService;
    private final EmailService emailService;

    public UserRegistrationHandler() {
        // Initialize dependencies (use DI framework or manual)
        this.userService = new UserService();
        this.emailService = new EmailService();
    }

    @Override
    public UserRegistrationResponse handleRequest(
            UserRegistrationEvent event,
            Context context) {
        
        LambdaLogger logger = context.getLogger();
        logger.log("Processing user registration: " + event.email());

        try {
            // Register user
            User user = userService.register(event.email(), event.name());

            // Send welcome email
            emailService.sendWelcome(user.getEmail());

            logger.log("User registered successfully: " + user.getId());
            
            return new UserRegistrationResponse(
                true,
                user.getId(),
                "User registered successfully"
            );

        } catch (Exception e) {
            logger.log("Failed to register user: " + e.getMessage());
            
            return new UserRegistrationResponse(
                false,
                null,
                "Registration failed: " + e.getMessage()
            );
        }
    }
}
```

2. **Invoking Lambda from Spring Boot**
```java
@Service
@RequiredArgsConstructor
public class LambdaInvoker {
    
    private final LambdaClient lambdaClient;
    private final ObjectMapper objectMapper;

    public <T, R> R invokeLambda(
            String functionName,
            T payload,
            Class<R> responseType) {
        
        try {
            String payloadJson = objectMapper.writeValueAsString(payload);

            InvokeRequest request = InvokeRequest.builder()
                .functionName(functionName)
                .payload(SdkBytes.fromUtf8String(payloadJson))
                .build();

            InvokeResponse response = lambdaClient.invoke(request);

            if (response.statusCode() != 200) {
                throw new LambdaInvocationException(
                    "Lambda invocation failed with status: " + response.statusCode()
                );
            }

            String responseJson = response.payload().asUtf8String();
            return objectMapper.readValue(responseJson, responseType);

        } catch (JsonProcessingException e) {
            throw new LambdaInvocationException("Failed to process Lambda payload", e);
        }
    }

    public <T> void invokeLambdaAsync(String functionName, T payload) {
        try {
            String payloadJson = objectMapper.writeValueAsString(payload);

            InvokeRequest request = InvokeRequest.builder()
                .functionName(functionName)
                .invocationType(InvocationType.EVENT)  // Async invocation
                .payload(SdkBytes.fromUtf8String(payloadJson))
                .build();

            lambdaClient.invoke(request);

        } catch (JsonProcessingException e) {
            throw new LambdaInvocationException("Failed to invoke Lambda async", e);
        }
    }
}
```

**Best Practices:**
- Keep Lambda functions focused and small
- Use environment variables for configuration
- Implement proper error handling and logging
- Use Lambda Layers for shared dependencies
- Configure appropriate timeouts and memory
- Use provisioned concurrency for consistent performance
- Implement idempotency for event-driven functions
- Monitor with CloudWatch Logs and X-Ray

**References:**
- `skills/aws-java/aws-sdk-java-v2-lambda/SKILL.md`

---

## Messaging Services

### aws-sdk-java-v2-messaging

**Purpose**: Implement SQS (Simple Queue Service) and SNS (Simple Notification Service) for asynchronous messaging.

**When to use:**
- Decoupling microservices
- Implementing event-driven architectures
- Building reliable message processing
- Fan-out notifications (SNS)
- Queue-based load leveling (SQS)

**Key Patterns:**

1. **SQS Producer**
```java
@Service
@RequiredArgsConstructor
public class SqsProducer {
    
    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;
    
    @Value("${aws.sqs.queue-url}")
    private String queueUrl;

    public void sendMessage(OrderCreatedEvent event) {
        try {
            String messageBody = objectMapper.writeValueAsString(event);

            SendMessageRequest request = SendMessageRequest.builder()
                .queueUrl(queueUrl)
                .messageBody(messageBody)
                .messageAttributes(Map.of(
                    "EventType", MessageAttributeValue.builder()
                        .dataType("String")
                        .stringValue("OrderCreated")
                        .build()
                ))
                .build();

            SendMessageResponse response = sqsClient.sendMessage(request);
            log.info("Sent message to SQS: messageId={}", response.messageId());

        } catch (JsonProcessingException e) {
            throw new MessagingException("Failed to serialize message", e);
        }
    }

    public void sendMessageBatch(List<OrderCreatedEvent> events) {
        List<SendMessageBatchRequestEntry> entries = new ArrayList<>();

        for (int i = 0; i < events.size(); i++) {
            try {
                String messageBody = objectMapper.writeValueAsString(events.get(i));
                
                entries.add(SendMessageBatchRequestEntry.builder()
                    .id(String.valueOf(i))
                    .messageBody(messageBody)
                    .build());
                    
            } catch (JsonProcessingException e) {
                log.error("Failed to serialize message", e);
            }
        }

        SendMessageBatchRequest request = SendMessageBatchRequest.builder()
            .queueUrl(queueUrl)
            .entries(entries)
            .build();

        sqsClient.sendMessageBatch(request);
    }
}
```

2. **SQS Consumer**
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class SqsConsumer {
    
    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;
    private final OrderService orderService;
    
    @Value("${aws.sqs.queue-url}")
    private String queueUrl;

    @Scheduled(fixedDelay = 5000)
    public void pollMessages() {
        ReceiveMessageRequest request = ReceiveMessageRequest.builder()
            .queueUrl(queueUrl)
            .maxNumberOfMessages(10)
            .waitTimeSeconds(20)  // Long polling
            .messageAttributeNames("All")
            .build();

        ReceiveMessageResponse response = sqsClient.receiveMessage(request);

        for (Message message : response.messages()) {
            try {
                processMessage(message);
                deleteMessage(message.receiptHandle());
                
            } catch (Exception e) {
                log.error("Failed to process message: {}", message.messageId(), e);
                // Consider moving to DLQ or implementing retry logic
            }
        }
    }

    private void processMessage(Message message) throws JsonProcessingException {
        OrderCreatedEvent event = objectMapper.readValue(
            message.body(),
            OrderCreatedEvent.class
        );

        orderService.processOrder(event);
        log.info("Processed order: {}", event.orderId());
    }

    private void deleteMessage(String receiptHandle) {
        DeleteMessageRequest deleteRequest = DeleteMessageRequest.builder()
            .queueUrl(queueUrl)
            .receiptHandle(receiptHandle)
            .build();

        sqsClient.deleteMessage(deleteRequest);
    }
}
```

3. **SNS Publisher**
```java
@Service
@RequiredArgsConstructor
public class SnsPublisher {
    
    private final SnsClient snsClient;
    private final ObjectMapper objectMapper;
    
    @Value("${aws.sns.topic-arn}")
    private String topicArn;

    public void publishEvent(DomainEvent event) {
        try {
            String message = objectMapper.writeValueAsString(event);

            PublishRequest request = PublishRequest.builder()
                .topicArn(topicArn)
                .message(message)
                .subject(event.getClass().getSimpleName())
                .messageAttributes(Map.of(
                    "EventType", MessageAttributeValue.builder()
                        .dataType("String")
                        .stringValue(event.getClass().getSimpleName())
                        .build()
                ))
                .build();

            PublishResponse response = snsClient.publish(request);
            log.info("Published event to SNS: messageId={}", response.messageId());

        } catch (JsonProcessingException e) {
            throw new MessagingException("Failed to publish event", e);
        }
    }
}
```

**Best Practices:**
- Use long polling (20 seconds) for SQS to reduce costs
- Implement Dead Letter Queues (DLQ) for failed messages
- Use message attributes for filtering
- Configure appropriate visibility timeout
- Implement idempotent message processing
- Use FIFO queues for ordering guarantees
- Monitor queue depth and age of oldest message
- Use SNS for fan-out, SQS for reliable processing
- Implement exponential backoff for retries

**References:**
- `skills/aws-java/aws-sdk-java-v2-messaging/SKILL.md`

---

## Security Services

### aws-sdk-java-v2-kms

**Purpose**: Integrate AWS Key Management Service (KMS) for encryption and key management.

**When to use:**
- Encrypting sensitive data
- Managing encryption keys
- Implementing envelope encryption
- Rotating keys automatically
- Auditing key usage

**Key Patterns:**

1. **KMS Client Configuration**
```java
@Configuration
public class KmsConfig {

    @Bean
    public KmsClient kmsClient(
            Region region,
            AwsCredentialsProvider credentialsProvider) {
        
        return KmsClient.builder()
            .region(region)
            .credentialsProvider(credentialsProvider)
            .build();
    }
}
```

2. **Encrypt Data**
```java
@Service
@RequiredArgsConstructor
public class EncryptionService {
    
    private final KmsClient kmsClient;
    
    @Value("${aws.kms.key-id}")
    private String keyId;

    public byte[] encrypt(byte[] plaintext) {
        EncryptRequest request = EncryptRequest.builder()
            .keyId(keyId)
            .plaintext(SdkBytes.fromByteArray(plaintext))
            .build();

        EncryptResponse response = kmsClient.encrypt(request);
        return response.ciphertextBlob().asByteArray();
    }

    public byte[] decrypt(byte[] ciphertext) {
        DecryptRequest request = DecryptRequest.builder()
            .ciphertextBlob(SdkBytes.fromByteArray(ciphertext))
            .build();

        DecryptResponse response = kmsClient.decrypt(request);
        return response.plaintext().asByteArray();
    }

    public String encryptString(String plaintext) {
        byte[] encrypted = encrypt(plaintext.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(encrypted);
    }

    public String decryptString(String encryptedBase64) {
        byte[] encrypted = Base64.getDecoder().decode(encryptedBase64);
        byte[] decrypted = decrypt(encrypted);
        return new String(decrypted, StandardCharsets.UTF_8);
    }
}
```

**Best Practices:**
- Use customer-managed keys (CMK) for sensitive data
- Enable automatic key rotation
- Use encryption context for additional security
- Implement caching for data keys (envelope encryption)
- Audit key usage with CloudTrail
- Use IAM policies to control key access
- Consider multi-region keys for global applications

**References:**
- `skills/aws-java/aws-sdk-java-v2-kms/SKILL.md`

---

### aws-sdk-java-v2-secrets-manager

**Purpose**: Manage application secrets securely using AWS Secrets Manager.

**When to use:**
- Storing database credentials
- Managing API keys
- Rotating secrets automatically
- Centralized secret management
- Auditing secret access

**Key Patterns:**

1. **Secrets Manager Client**
```java
@Service
@RequiredArgsConstructor
public class SecretsManagerService {
    
    private final SecretsManagerClient secretsManagerClient;

    public String getSecret(String secretName) {
        GetSecretValueRequest request = GetSecretValueRequest.builder()
            .secretId(secretName)
            .build();

        GetSecretValueResponse response = secretsManagerClient.getSecretValue(request);
        return response.secretString();
    }

    public <T> T getSecret(String secretName, Class<T> valueType) {
        String secretJson = getSecret(secretName);
        
        try {
            return new ObjectMapper().readValue(secretJson, valueType);
        } catch (JsonProcessingException e) {
            throw new SecretDeserializationException("Failed to parse secret", e);
        }
    }

    public void createSecret(String secretName, String secretValue) {
        CreateSecretRequest request = CreateSecretRequest.builder()
            .name(secretName)
            .secretString(secretValue)
            .build();

        secretsManagerClient.createSecret(request);
    }

    public void updateSecret(String secretName, String newValue) {
        UpdateSecretRequest request = UpdateSecretRequest.builder()
            .secretId(secretName)
            .secretString(newValue)
            .build();

        secretsManagerClient.updateSecret(request);
    }
}
```

2. **Caching Secrets**
```java
@Service
public class CachedSecretsService {
    
    private final SecretsManagerService secretsManagerService;
    private final Cache<String, String> secretCache;

    public CachedSecretsService(SecretsManagerService secretsManagerService) {
        this.secretsManagerService = secretsManagerService;
        this.secretCache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofMinutes(10))
            .maximumSize(100)
            .build();
    }

    public String getSecret(String secretName) {
        return secretCache.get(secretName, secretsManagerService::getSecret);
    }
}
```

**Best Practices:**
- Cache secrets to reduce API calls
- Enable automatic rotation for database credentials
- Use versioning for secret updates
- Tag secrets for organization
- Implement least privilege access with IAM
- Enable CloudTrail logging for auditing
- Use resource policies for fine-grained control

**References:**
- `skills/aws-java/aws-sdk-java-v2-secrets-manager/SKILL.md`

---

## Common Workflows

### Building a Serverless API with AWS Services

```bash
# 1. Set up core AWS SDK (aws-sdk-java-v2-core)
# - Configure credentials and region
# - Set up service clients

# 2. Create DynamoDB table (aws-sdk-java-v2-dynamodb)
# - Define entity with Enhanced Client
# - Implement repository

# 3. Implement S3 file storage (aws-sdk-java-v2-s3)
# - Upload/download files
# - Generate pre-signed URLs

# 4. Add SQS for async processing (aws-sdk-java-v2-messaging)
# - Produce messages
# - Consume with scheduled polling

# 5. Secure with KMS (aws-sdk-java-v2-kms)
# - Encrypt sensitive data
# - Manage encryption keys

# 6. Store secrets (aws-sdk-java-v2-secrets-manager)
# - Retrieve database credentials
# - Cache secrets

# 7. Deploy as Lambda functions (aws-sdk-java-v2-lambda)
# - Create Lambda handlers
# - Configure triggers
```

---

## Best Practices

### General AWS SDK Principles

1. **Client Configuration**
   - Use BOM for version management
   - Prefer async clients for non-blocking operations
   - Configure appropriate timeouts and retries
   - Close clients on application shutdown

2. **Credentials Management**
   - Use IAM roles in production (EC2, Lambda, ECS)
   - Use Secrets Manager for application secrets
   - Never hardcode credentials
   - Use profiles for local development

3. **Error Handling**
   - Implement retry logic with exponential backoff
   - Handle service-specific exceptions
   - Use try-with-resources for clients
   - Log errors with context

4. **Performance**
   - Use async clients for concurrent operations
   - Implement connection pooling
   - Cache frequently accessed data
   - Use batch operations when available

5. **Cost Optimization**
   - Use appropriate storage classes (S3)
   - Configure lifecycle policies
   - Enable DynamoDB auto-scaling
   - Use reserved capacity when predictable
   - Monitor and optimize API calls

6. **Security**
   - Enable encryption at rest and in transit
   - Use least privilege IAM policies
   - Enable CloudTrail for auditing
   - Implement VPC endpoints for private connectivity
   - Use KMS for encryption key management

7. **Monitoring**
   - Enable CloudWatch metrics
   - Set up alarms for critical metrics
   - Use X-Ray for distributed tracing
   - Log with structured logging

8. **Testing**
   - Use LocalStack for local integration tests
   - Mock AWS clients in unit tests
   - Use Testcontainers for reproducible tests
   - Test error scenarios and edge cases

---

## References

- [Contributing Guide](../CONTRIBUTING.md)
- [README](../README.md)

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-08  
