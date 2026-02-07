# AWS Java SDK Skills Guide

Quick reference to 10 AWS SDK for Java v2 skills for cloud development. See individual skill files for complete details.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **aws-sdk-java-v2-core** | SDK setup, client configuration, credentials |
| **aws-rds-spring-boot-integration** | Aurora RDS with Spring JPA, connection pooling |
| **aws-sdk-java-v2-s3** | S3 operations, uploads, downloads, presigned URLs |
| **aws-sdk-java-v2-dynamodb** | DynamoDB tables, queries, scans, transactions |
| **aws-sdk-java-v2-lambda** | Lambda invocation, event handling, payloads |
| **aws-sdk-java-v2-secrets-manager** | Secrets retrieval, rotation, caching |
| **aws-sdk-java-v2-kms** | KMS encryption, key management, envelope encryption |
| **aws-sdk-java-v2-messaging** | SQS/SNS operations, queues, topics, publishing |
| **aws-sdk-java-v2-rds** | RDS management, instances, snapshots, parameters |
| **aws-sdk-java-v2-bedrock** | Bedrock AI, model invocation, streaming, guardrails |

---

## Core Setup

### aws-sdk-java-v2-core

**File**: `skills/aws-sdk-java-v2-core/SKILL.md`

SDK initialization: client configuration, credential management, async operations.

**When to use:**
- Setting up AWS SDK clients
- Configuring credentials and regions
- Async/await patterns

---

## Storage

### aws-sdk-java-v2-s3

**File**: `skills/aws-sdk-java-v2-s3/SKILL.md`

S3 operations: bucket operations, object upload/download, presigned URLs.

**When to use:**
- File upload/download
- Bucket management
- Generating presigned URLs for public access

**Pattern:**
```java
S3Client s3 = S3Client.builder().build();
s3.putObject(
    PutObjectRequest.builder()
        .bucket("my-bucket")
        .key("file.txt")
        .build(),
    RequestBody.fromString("content")
);
```

---

## Databases

### aws-rds-spring-boot-integration

**File**: `skills/aws-rds-spring-boot-integration/SKILL.md`

Aurora RDS: cluster setup, connection pooling, read/write split, failover.

**When to use:**
- Spring Boot with RDS Aurora
- Connection pool configuration
- Multi-AZ failover

---

### aws-sdk-java-v2-dynamodb

**File**: `skills/aws-sdk-java-v2-dynamodb/SKILL.md`

DynamoDB: table operations, queries, scans, transactions.

**When to use:**
- NoSQL database operations
- Query and scan patterns
- Transactional writes

---

### aws-sdk-java-v2-rds

**File**: `skills/aws-sdk-java-v2-rds/SKILL.md`

RDS management: instance creation, snapshots, parameter groups.

**When to use:**
- RDS cluster management
- Automated snapshots
- Parameter group configuration

---

## Compute

### aws-sdk-java-v2-lambda

**File**: `skills/aws-sdk-java-v2-lambda/SKILL.md`

Lambda: function invocation, event handling, custom runtimes.

**When to use:**
- Invoking Lambda functions
- Event-driven architecture
- Async job processing

---

## Security & Secrets

### aws-sdk-java-v2-secrets-manager

**File**: `skills/aws-sdk-java-v2-secrets-manager/SKILL.md`

Secrets Manager: retrieval, rotation, caching.

**When to use:**
- Managing API keys and passwords
- Secret rotation
- Credential caching

---

### aws-sdk-java-v2-kms

**File**: `skills/aws-sdk-java-v2-kms/SKILL.md`

KMS encryption: key management, encryption/decryption, envelope encryption.

**When to use:**
- Data encryption
- Key management
- Envelope encryption patterns

---

## Messaging

### aws-sdk-java-v2-messaging

**File**: `skills/aws-sdk-java-v2-messaging/SKILL.md`

SQS/SNS: queue operations, topic publishing, message processing.

**When to use:**
- Async messaging
- Event-driven systems
- Decoupled services

---

## AI & ML

### aws-sdk-java-v2-bedrock

**File**: `skills/aws-sdk-java-v2-bedrock/SKILL.md`

Bedrock: model invocation, streaming, guardrails.

**When to use:**
- Using Bedrock AI models
- Streaming responses
- Content filtering with guardrails

---

## Common Workflows

### File Management with S3

```
1. aws-sdk-java-v2-core          → Setup client
2. aws-sdk-java-v2-s3            → S3 operations
3. aws-sdk-java-v2-secrets-manager → S3 credentials
```

### Secure Data Storage

```
1. aws-sdk-java-v2-core          → Setup
2. aws-rds-spring-boot-integration → Database
3. aws-sdk-java-v2-kms           → Encryption
4. aws-sdk-java-v2-secrets-manager → Secrets
```

### Async Job Processing

```
1. aws-sdk-java-v2-messaging     → SQS queues
2. aws-sdk-java-v2-lambda        → Lambda workers
3. aws-sdk-java-v2-dynamodb      → Result storage
```

### Pub/Sub System

```
1. aws-sdk-java-v2-messaging     → SNS topics + SQS queues
2. aws-sdk-java-v2-core          → Client setup
3. aws-sdk-java-v2-kms           → Message encryption
```

### Spring Boot with AWS

```
1. aws-rds-spring-boot-integration → Database setup
2. aws-sdk-java-v2-s3             → File storage
3. aws-sdk-java-v2-secrets-manager → Configuration
4. aws-sdk-java-v2-messaging       → Event processing
```

---

## Technology Stack

- **AWS SDK**: Java v2 (non-blocking)
- **Spring Boot**: 3.5.x+ (optional)
- **Database**: RDS Aurora, DynamoDB
- **Storage**: S3
- **Messaging**: SQS, SNS
- **Security**: KMS, Secrets Manager
- **AI**: Bedrock

---

## Common Patterns

### Request/Response
```java
SqsClient sqs = SqsClient.builder().build();
SendMessageResponse result = sqs.sendMessage(
    SendMessageRequest.builder()
        .queueUrl("https://...")
        .messageBody("message")
        .build()
);
```

### Async Operations
```java
S3AsyncClient s3 = S3AsyncClient.builder().build();
CompletableFuture<GetObjectResponse> response = 
    s3.getObject(GetObjectRequest.builder()...build(), ...);
```

### Error Handling
```java
try {
    s3.getObject(...);
} catch (NoSuchKeyException e) {
    // Handle missing object
} catch (S3Exception e) {
    // Handle S3 errors
}
```

---

**Note**: For complete patterns and examples, see individual skill files in `skills/`
