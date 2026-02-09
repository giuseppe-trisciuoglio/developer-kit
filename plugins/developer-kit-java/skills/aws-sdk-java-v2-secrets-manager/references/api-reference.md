# AWS Secrets Manager API Reference

## Overview
AWS Secrets Manager provides a service to enable you to store, manage, and retrieve secrets with API version 2017-10-17.

## Core Classes

### SecretsManagerClient
- **Purpose**: Synchronous client for AWS Secrets Manager
- **Location**: `software.amazon.awssdk.services.secretsmanager.SecretsManagerClient`
- **Builder**: `SecretsManagerClient.builder()`

### SecretsManagerAsyncClient
- **Purpose**: Asynchronous client for AWS Secrets Manager
- **Location**: `software.amazon.awssdk.services.secretsmanager.SecretsManagerAsyncClient`
- **Builder**: `SecretsManagerAsyncClient.builder()`

## Configuration Classes

### SecretsManagerClientBuilder
- Methods:
  - `region(Region region)` - Set AWS region
  - `credentialsProvider(AwsCredentialsProvider credentialsProvider)` - Set credentials
  - `build()` - Create client instance

### SecretsManagerServiceClientConfiguration
- Service client settings and configuration

## Request Types

### CreateSecretRequest
- **Fields**:
  - `name(String name)` - Secret name (required)
  - `secretString(String secretString)` - Secret value
  - `secretBinary(SdkBytes secretBinary)` - Binary secret value
  - `description(String description)` - Secret description
  - `kmsKeyId(String kmsKeyId)` - KMS key for encryption
  - `tags(List<Tag> tags)` - Tags for organization

### GetSecretValueRequest
- **Fields**:
  - `secretId(String secretId)` - Secret name or ARN
  - `versionId(String versionId)` - Specific version ID
  - `versionStage(String versionStage)` - Version stage (e.g., "AWSCURRENT")

### UpdateSecretRequest
- **Fields**:
  - `secretId(String secretId)` - Secret name or ARN
  - `secretString(String secretString)` - New secret value
  - `secretBinary(SdkBytes secretBinary)` - New binary secret value
  - `kmsKeyId(String kmsKeyId)` - KMS key for encryption

### DeleteSecretRequest
- **Fields**:
  - `secretId(String secretId)` - Secret name or ARN
  - `recoveryWindowInDays(Long recoveryWindowInDays)` - Recovery period
  - `forceDeleteWithoutRecovery(Boolean forceDeleteWithoutRecovery)` - Immediate deletion

### RotateSecretRequest
- **Fields**:
  - `secretId(String secretId)` - Secret name or ARN
  - `rotationLambdaArn(String rotationLambdaArn)` - Lambda ARN for rotation
  - `rotationRules(RotationRulesType rotationRules)` - Rotation configuration
  - `rotationSchedule(RotationScheduleType rotationSchedule)` - Schedule configuration

## Response Types

### CreateSecretResponse
- **Fields**:
  - `arn()` - Secret ARN
  - `name()` - Secret name
  - `versionId()` - Version ID

### GetSecretValueResponse
- **Fields**:
  - `arn()` - Secret ARN
  - `name()` - Secret name
  - `versionId()` - Version ID
  - `secretString()` - Secret value as string
  - `secretBinary()` - Secret value as binary
  - `versionStages()` - Version stages

### UpdateSecretResponse
- **Fields**:
  - `arn()` - Secret ARN
  - `name()` - Secret name
  - `versionId()` - New version ID

### DeleteSecretResponse
- **Fields**:
  - `arn()` - Secret ARN
  - `name()` - Secret name
  - `deletionDate()` - Deletion date/time

### RotateSecretResponse
- **Fields**:
  - `arn()` - Secret ARN
  - `name()` - Secret name
  - `versionId()` - New version ID

## Paginated Operations

### ListSecretsRequest
- **Fields**:
  - `maxResults(Integer maxResults)` - Maximum results per page
  - `nextToken(String nextToken)` - Token for next page
  - `filter(String filter)` - Filter criteria

### ListSecretsResponse
- **Fields**:
  - `secretList()` - List of secrets
  - `nextToken()` - Token for next page

## Error Handling

### SecretsManagerException
- Common error codes:
  - `ResourceNotFoundException` - Secret not found
  - `InvalidParameterException` - Invalid parameters
  - `MalformedPolicyDocumentException` - Invalid policy document
  - `InternalServiceErrorException` - Internal service error
  - `InvalidRequestException` - Invalid request
  - `DecryptionFailure` - Decryption failed
  - `ResourceExistsException` - Resource already exists
  - `ResourceConflictException` - Resource conflict
  - `ValidationException` - Validation failed