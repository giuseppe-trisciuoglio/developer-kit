# AWS SQS & SNS Official Documentation Reference

This file contains reference information extracted from official AWS resources for the AWS SDK for Java 2.x messaging patterns.

## Source Documents
- [AWS Java SDK v2 Examples - SQS](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/sqs)
- [AWS Java SDK v2 Examples - SNS](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/sns)
- [AWS SQS Developer Guide](https://docs.aws.amazon.com/sqs/latest/dg/)
- [AWS SNS Developer Guide](https://docs.aws.amazon.com/sns/latest/dg/)

## Amazon SQS Reference

### Core Operations
- **CreateQueue** - Create new SQS queue
- **DeleteMessage** - Delete individual message from queue
- **ListQueues** - List available queues
- **ReceiveMessage** - Receive messages from queue
- **SendMessage** - Send message to queue
- **SendMessageBatch** - Send multiple messages to queue

### Advanced Features
- **Large Message Handling** - Use S3 for messages larger than 256KB
- **Batch Operations** - Process multiple messages efficiently
- **Long Polling** - Reduce empty responses with `waitTimeSeconds`
- **Visibility Timeout** - Control message visibility during processing
- **Dead Letter Queues (DLQ)** - Handle failed messages
- **FIFO Queues** - Ensure message ordering and deduplication

### Java SDK v2 Key Classes
```java
// Core clients and models
software.amazon.awssdk.services.sqs.SqsClient
software.amazon.awssdk.services.sqs.model.*
software.amazon.awssdk.services.sqs.model.QueueAttributeName
```

## Amazon SNS Reference

### Core Operations
- **CreateTopic** - Create new SNS topic
- **Publish** - Send message to topic
- **Subscribe** - Subscribe endpoint to topic
- **ListSubscriptions** - List topic subscriptions
- **Unsubscribe** - Remove subscription

### Advanced Features
- **Platform Endpoints** - Mobile push notifications
- **SMS Publishing** - Send SMS messages
- **FIFO Topics** - Ordered message delivery with deduplication
- **Filter Policies** - Filter messages based on attributes
- **Message Attributes** - Enrich messages with metadata
- **DLQ for Subscriptions** - Handle failed deliveries

### Java SDK v2 Key Classes
```java
// Core clients and models
software.amazon.awssdk.services.sns.SnsClient
software.amazon.awssdk.services.sns.model.*
software.amazon.awssdk.services.sns.model.MessageAttributeValue
```

## Best Practices from AWS

### SQS Best Practices
1. **Use Long Polling**: Set `waitTimeSeconds` (10-40 seconds) to reduce empty responses
2. **Batch Operations**: Use `SendMessageBatch` for efficiency
3. **Visibility Timeout**: Set appropriately based on processing time
4. **Handle Duplicates**: Implement idempotent processing for retries
5. **Monitor Queue Depth**: Use CloudWatch for monitoring
6. **Implement DLQ**: Route failed messages for analysis

### SNS Best Practices
1. **Use Filter Policies**: Reduce noise by filtering messages
2. **Message Attributes**: Add metadata for routing decisions
3. **Retry Logic**: Handle transient failures gracefully
4. **Monitor Failed Deliveries**: Set up CloudWatch alarms
5. **Security**: Use IAM policies for access control
6. **FIFO Topics**: Use when order and deduplication are critical

## Error Handling Patterns

### Common SQS Errors
- **QueueDoesNotExistException**: Verify queue URL
- **MessageNotInflightException**: Check message visibility
- **OverLimitException**: Implement backoff/retry logic
- **InvalidAttributeValueException**: Validate queue attributes

### Common SNS Errors
- **NotFoundException**: Verify topic ARN
- **InvalidParameterException**: Validate subscription parameters
- **InternalFailureException**: Implement retry logic
- **AuthorizationErrorException**: Check IAM permissions

## Integration Patterns

### Spring Boot Integration
- Use `@Service` classes for business logic
- Inject `SqsClient` and `SnsClient` via constructor injection
- Configure clients with `@Configuration` beans
- Use `@Value` for externalizing configuration

### Testing Strategies
- Use LocalStack for local development
- Mock AWS services with Mockito for unit tests
- Integrate with Testcontainers for integration tests
- Test idempotent operations thoroughly

## Configuration Options

### SQS Configuration
```java
SqsClient sqsClient = SqsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### SNS Configuration
```java
SnsClient snsClient = SnsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Advanced Configuration
- Override endpoint for local development
- Configure custom credentials provider
- Set custom HTTP client
- Configure retry policies

## Monitoring and Observability

### SQS Metrics
- ApproximateNumberOfMessagesVisible
- ApproximateNumberOfMessagesNotVisible
- ApproximateNumberOfMessagesDelayed
- SentMessages
- ReceiveCalls

### SNS Metrics
- NumberOfNotifications
- PublishSuccess
- PublishFailed
- SubscriptionConfirmation
- SubscriptionConfirmationFailed

## Security Considerations

### IAM Permissions
- Grant least privilege access
- Use IAM roles for EC2/ECS
- Implement resource-based policies
- Use condition keys for fine-grained control

### Data Protection
- Encrypt sensitive data in messages
- Use KMS for message encryption
- Implement message signing
- Secure endpoints with HTTPS