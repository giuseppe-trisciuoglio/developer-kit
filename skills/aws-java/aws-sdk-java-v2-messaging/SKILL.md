---
name: aws-sdk-java-v2-messaging
description: AWS messaging patterns using AWS SDK for Java 2.x for SQS and SNS. Use when working with SQS queues (send/receive messages, FIFO queues, DLQ), SNS topics (publish messages, subscriptions), or implementing pub/sub patterns.
---

# AWS SDK for Java 2.x - Messaging (SQS & SNS)

## When to Use

Use this skill when:
- Sending or receiving messages with Amazon SQS
- Working with SQS FIFO queues or standard queues
- Implementing Dead Letter Queues (DLQ)
- Publishing messages to SNS topics
- Managing SNS subscriptions (email, SMS, SQS, Lambda)
- Implementing pub/sub messaging patterns
- Integrating SQS/SNS with Spring Boot

## Dependencies

```xml
<!-- SQS -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>sqs</artifactId>
</dependency>

<!-- SNS -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>sns</artifactId>
</dependency>
```

## Amazon SQS

### Client Setup

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.sqs.SqsClient;

SqsClient sqsClient = SqsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Create Queue

```java
import software.amazon.awssdk.services.sqs.model.*;

public String createQueue(SqsClient sqsClient, String queueName) {
    CreateQueueRequest request = CreateQueueRequest.builder()
        .queueName(queueName)
        .build();
    
    CreateQueueResponse response = sqsClient.createQueue(request);
    
    return response.queueUrl();
}
```

### Create FIFO Queue

```java
public String createFifoQueue(SqsClient sqsClient, String queueName) {
    Map<QueueAttributeName, String> attributes = new HashMap<>();
    attributes.put(QueueAttributeName.FIFO_QUEUE, "true");
    attributes.put(QueueAttributeName.CONTENT_BASED_DEDUPLICATION, "true");
    
    CreateQueueRequest request = CreateQueueRequest.builder()
        .queueName(queueName + ".fifo")
        .attributes(attributes)
        .build();
    
    CreateQueueResponse response = sqsClient.createQueue(request);
    
    return response.queueUrl();
}
```

### Get Queue URL

```java
public String getQueueUrl(SqsClient sqsClient, String queueName) {
    GetQueueUrlRequest request = GetQueueUrlRequest.builder()
        .queueName(queueName)
        .build();
    
    GetQueueUrlResponse response = sqsClient.getQueueUrl(request);
    
    return response.queueUrl();
}
```

### List Queues

```java
public List<String> listQueues(SqsClient sqsClient) {
    ListQueuesResponse response = sqsClient.listQueues();
    
    return response.queueUrls();
}
```

### Send Message

```java
public String sendMessage(SqsClient sqsClient, String queueUrl, String messageBody) {
    SendMessageRequest request = SendMessageRequest.builder()
        .queueUrl(queueUrl)
        .messageBody(messageBody)
        .build();
    
    SendMessageResponse response = sqsClient.sendMessage(request);
    
    return response.messageId();
}
```

### Send Message with Attributes

```java
public String sendMessageWithAttributes(SqsClient sqsClient, 
                                        String queueUrl, 
                                        String messageBody,
                                        Map<String, String> attributes) {
    Map<String, MessageAttributeValue> messageAttributes = attributes.entrySet().stream()
        .collect(Collectors.toMap(
            Map.Entry::getKey,
            e -> MessageAttributeValue.builder()
                .dataType("String")
                .stringValue(e.getValue())
                .build()));
    
    SendMessageRequest request = SendMessageRequest.builder()
        .queueUrl(queueUrl)
        .messageBody(messageBody)
        .messageAttributes(messageAttributes)
        .build();
    
    SendMessageResponse response = sqsClient.sendMessage(request);
    
    return response.messageId();
}
```

### Send Message to FIFO Queue

```java
public String sendFifoMessage(SqsClient sqsClient, 
                              String queueUrl, 
                              String messageBody, 
                              String messageGroupId) {
    SendMessageRequest request = SendMessageRequest.builder()
        .queueUrl(queueUrl)
        .messageBody(messageBody)
        .messageGroupId(messageGroupId)
        .messageDeduplicationId(UUID.randomUUID().toString())
        .build();
    
    SendMessageResponse response = sqsClient.sendMessage(request);
    
    return response.messageId();
}
```

### Send Batch Messages

```java
public void sendBatchMessages(SqsClient sqsClient, 
                              String queueUrl, 
                              List<String> messages) {
    List<SendMessageBatchRequestEntry> entries = IntStream.range(0, messages.size())
        .mapToObj(i -> SendMessageBatchRequestEntry.builder()
            .id(String.valueOf(i))
            .messageBody(messages.get(i))
            .build())
        .collect(Collectors.toList());
    
    SendMessageBatchRequest request = SendMessageBatchRequest.builder()
        .queueUrl(queueUrl)
        .entries(entries)
        .build();
    
    SendMessageBatchResponse response = sqsClient.sendMessageBatch(request);
    
    System.out.println("Successful: " + response.successful().size());
    System.out.println("Failed: " + response.failed().size());
}
```

### Receive Messages

```java
public List<Message> receiveMessages(SqsClient sqsClient, String queueUrl) {
    ReceiveMessageRequest request = ReceiveMessageRequest.builder()
        .queueUrl(queueUrl)
        .maxNumberOfMessages(10)
        .waitTimeSeconds(20) // Long polling
        .messageAttributeNames("All")
        .build();
    
    ReceiveMessageResponse response = sqsClient.receiveMessage(request);
    
    return response.messages();
}
```

### Delete Message

```java
public void deleteMessage(SqsClient sqsClient, String queueUrl, String receiptHandle) {
    DeleteMessageRequest request = DeleteMessageRequest.builder()
        .queueUrl(queueUrl)
        .receiptHandle(receiptHandle)
        .build();
    
    sqsClient.deleteMessage(request);
}
```

### Delete Batch Messages

```java
public void deleteBatchMessages(SqsClient sqsClient, 
                                String queueUrl, 
                                List<Message> messages) {
    List<DeleteMessageBatchRequestEntry> entries = messages.stream()
        .map(msg -> DeleteMessageBatchRequestEntry.builder()
            .id(msg.messageId())
            .receiptHandle(msg.receiptHandle())
            .build())
        .collect(Collectors.toList());
    
    DeleteMessageBatchRequest request = DeleteMessageBatchRequest.builder()
        .queueUrl(queueUrl)
        .entries(entries)
        .build();
    
    sqsClient.deleteMessageBatch(request);
}
```

### Change Message Visibility

```java
public void changeMessageVisibility(SqsClient sqsClient, 
                                    String queueUrl, 
                                    String receiptHandle, 
                                    int visibilityTimeout) {
    ChangeMessageVisibilityRequest request = ChangeMessageVisibilityRequest.builder()
        .queueUrl(queueUrl)
        .receiptHandle(receiptHandle)
        .visibilityTimeout(visibilityTimeout)
        .build();
    
    sqsClient.changeMessageVisibility(request);
}
```

### Purge Queue

```java
public void purgeQueue(SqsClient sqsClient, String queueUrl) {
    PurgeQueueRequest request = PurgeQueueRequest.builder()
        .queueUrl(queueUrl)
        .build();
    
    sqsClient.purgeQueue(request);
}
```

## Amazon SNS

### Client Setup

```java
import software.amazon.awssdk.services.sns.SnsClient;

SnsClient snsClient = SnsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Create Topic

```java
import software.amazon.awssdk.services.sns.model.*;

public String createTopic(SnsClient snsClient, String topicName) {
    CreateTopicRequest request = CreateTopicRequest.builder()
        .name(topicName)
        .build();
    
    CreateTopicResponse response = snsClient.createTopic(request);
    
    return response.topicArn();
}
```

### Create FIFO Topic

```java
public String createFifoTopic(SnsClient snsClient, String topicName) {
    Map<String, String> attributes = new HashMap<>();
    attributes.put("FifoTopic", "true");
    attributes.put("ContentBasedDeduplication", "true");
    
    CreateTopicRequest request = CreateTopicRequest.builder()
        .name(topicName + ".fifo")
        .attributes(attributes)
        .build();
    
    CreateTopicResponse response = snsClient.createTopic(request);
    
    return response.topicArn();
}
```

### List Topics

```java
public List<Topic> listTopics(SnsClient snsClient) {
    ListTopicsResponse response = snsClient.listTopics();
    
    return response.topics();
}
```

### Publish Message

```java
public String publishMessage(SnsClient snsClient, String topicArn, String message) {
    PublishRequest request = PublishRequest.builder()
        .topicArn(topicArn)
        .message(message)
        .build();
    
    PublishResponse response = snsClient.publish(request);
    
    return response.messageId();
}
```

### Publish Message with Subject

```java
public String publishMessageWithSubject(SnsClient snsClient, 
                                        String topicArn, 
                                        String subject, 
                                        String message) {
    PublishRequest request = PublishRequest.builder()
        .topicArn(topicArn)
        .subject(subject)
        .message(message)
        .build();
    
    PublishResponse response = snsClient.publish(request);
    
    return response.messageId();
}
```

### Publish Message with Attributes

```java
public String publishMessageWithAttributes(SnsClient snsClient, 
                                           String topicArn, 
                                           String message,
                                           Map<String, String> attributes) {
    Map<String, MessageAttributeValue> messageAttributes = attributes.entrySet().stream()
        .collect(Collectors.toMap(
            Map.Entry::getKey,
            e -> MessageAttributeValue.builder()
                .dataType("String")
                .stringValue(e.getValue())
                .build()));
    
    PublishRequest request = PublishRequest.builder()
        .topicArn(topicArn)
        .message(message)
        .messageAttributes(messageAttributes)
        .build();
    
    PublishResponse response = snsClient.publish(request);
    
    return response.messageId();
}
```

### Publish to FIFO Topic

```java
public String publishFifoMessage(SnsClient snsClient, 
                                 String topicArn, 
                                 String message, 
                                 String messageGroupId) {
    PublishRequest request = PublishRequest.builder()
        .topicArn(topicArn)
        .message(message)
        .messageGroupId(messageGroupId)
        .messageDeduplicationId(UUID.randomUUID().toString())
        .build();
    
    PublishResponse response = snsClient.publish(request);
    
    return response.messageId();
}
```

### Subscribe Email to Topic

```java
public String subscribeEmail(SnsClient snsClient, String topicArn, String email) {
    SubscribeRequest request = SubscribeRequest.builder()
        .protocol("email")
        .endpoint(email)
        .topicArn(topicArn)
        .build();
    
    SubscribeResponse response = snsClient.subscribe(request);
    
    return response.subscriptionArn();
}
```

### Subscribe SQS to Topic

```java
public String subscribeSqs(SnsClient snsClient, String topicArn, String queueArn) {
    SubscribeRequest request = SubscribeRequest.builder()
        .protocol("sqs")
        .endpoint(queueArn)
        .topicArn(topicArn)
        .build();
    
    SubscribeResponse response = snsClient.subscribe(request);
    
    return response.subscriptionArn();
}
```

### Subscribe Lambda to Topic

```java
public String subscribeLambda(SnsClient snsClient, String topicArn, String lambdaArn) {
    SubscribeRequest request = SubscribeRequest.builder()
        .protocol("lambda")
        .endpoint(lambdaArn)
        .topicArn(topicArn)
        .build();
    
    SubscribeResponse response = snsClient.subscribe(request);
    
    return response.subscriptionArn();
}
```

### List Subscriptions

```java
public List<Subscription> listSubscriptions(SnsClient snsClient, String topicArn) {
    ListSubscriptionsByTopicRequest request = ListSubscriptionsByTopicRequest.builder()
        .topicArn(topicArn)
        .build();
    
    ListSubscriptionsByTopicResponse response = snsClient.listSubscriptionsByTopic(request);
    
    return response.subscriptions();
}
```

### Unsubscribe

```java
public void unsubscribe(SnsClient snsClient, String subscriptionArn) {
    UnsubscribeRequest request = UnsubscribeRequest.builder()
        .subscriptionArn(subscriptionArn)
        .build();
    
    snsClient.unsubscribe(request);
}
```

## Spring Boot Integration

### Configuration

```java
@Configuration
public class MessagingConfiguration {
    
    @Bean
    public SqsClient sqsClient() {
        return SqsClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
    
    @Bean
    public SnsClient snsClient() {
        return SnsClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### SQS Message Service

```java
@Service
public class SqsMessageService {
    
    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;
    
    @Value("${aws.sqs.queue-url}")
    private String queueUrl;
    
    public SqsMessageService(SqsClient sqsClient, ObjectMapper objectMapper) {
        this.sqsClient = sqsClient;
        this.objectMapper = objectMapper;
    }
    
    public <T> void sendMessage(T message) {
        try {
            String jsonMessage = objectMapper.writeValueAsString(message);
            
            SendMessageRequest request = SendMessageRequest.builder()
                .queueUrl(queueUrl)
                .messageBody(jsonMessage)
                .build();
            
            sqsClient.sendMessage(request);
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to send SQS message", e);
        }
    }
    
    public <T> List<T> receiveMessages(Class<T> messageType) {
        ReceiveMessageRequest request = ReceiveMessageRequest.builder()
            .queueUrl(queueUrl)
            .maxNumberOfMessages(10)
            .waitTimeSeconds(20)
            .build();
        
        ReceiveMessageResponse response = sqsClient.receiveMessage(request);
        
        return response.messages().stream()
            .map(msg -> {
                try {
                    return objectMapper.readValue(msg.body(), messageType);
                } catch (Exception e) {
                    throw new RuntimeException("Failed to parse message", e);
                }
            })
            .collect(Collectors.toList());
    }
    
    public void deleteMessage(String receiptHandle) {
        DeleteMessageRequest request = DeleteMessageRequest.builder()
            .queueUrl(queueUrl)
            .receiptHandle(receiptHandle)
            .build();
        
        sqsClient.deleteMessage(request);
    }
}
```

### SNS Notification Service

```java
@Service
public class SnsNotificationService {
    
    private final SnsClient snsClient;
    private final ObjectMapper objectMapper;
    
    @Value("${aws.sns.topic-arn}")
    private String topicArn;
    
    public SnsNotificationService(SnsClient snsClient, ObjectMapper objectMapper) {
        this.snsClient = snsClient;
        this.objectMapper = objectMapper;
    }
    
    public void publishNotification(String subject, Object message) {
        try {
            String jsonMessage = objectMapper.writeValueAsString(message);
            
            PublishRequest request = PublishRequest.builder()
                .topicArn(topicArn)
                .subject(subject)
                .message(jsonMessage)
                .build();
            
            snsClient.publish(request);
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to publish SNS notification", e);
        }
    }
}
```

### Message Listener (Polling Pattern)

```java
@Service
public class SqsMessageListener {
    
    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;
    
    @Value("${aws.sqs.queue-url}")
    private String queueUrl;
    
    public SqsMessageListener(SqsClient sqsClient, ObjectMapper objectMapper) {
        this.sqsClient = sqsClient;
        this.objectMapper = objectMapper;
    }
    
    @Scheduled(fixedDelay = 5000)
    public void pollMessages() {
        ReceiveMessageRequest request = ReceiveMessageRequest.builder()
            .queueUrl(queueUrl)
            .maxNumberOfMessages(10)
            .waitTimeSeconds(20)
            .build();
        
        ReceiveMessageResponse response = sqsClient.receiveMessage(request);
        
        response.messages().forEach(this::processMessage);
    }
    
    private void processMessage(Message message) {
        try {
            // Process message
            System.out.println("Processing: " + message.body());
            
            // Delete message after successful processing
            deleteMessage(message.receiptHandle());
            
        } catch (Exception e) {
            // Handle error - message will become visible again
            System.err.println("Failed to process message: " + e.getMessage());
        }
    }
    
    private void deleteMessage(String receiptHandle) {
        DeleteMessageRequest request = DeleteMessageRequest.builder()
            .queueUrl(queueUrl)
            .receiptHandle(receiptHandle)
            .build();
        
        sqsClient.deleteMessage(request);
    }
}
```

## Pub/Sub Pattern (SNS + SQS)

### Setup SNS Topic with SQS Subscription

```java
@Configuration
public class PubSubConfiguration {
    
    @Bean
    public String setupPubSub(SnsClient snsClient, SqsClient sqsClient) {
        // Create SNS topic
        String topicArn = createTopic(snsClient, "order-events");
        
        // Create SQS queue
        String queueUrl = createQueue(sqsClient, "order-processor");
        
        // Get queue ARN
        GetQueueAttributesRequest attrRequest = GetQueueAttributesRequest.builder()
            .queueUrl(queueUrl)
            .attributeNames(QueueAttributeName.QUEUE_ARN)
            .build();
        
        String queueArn = sqsClient.getQueueAttributes(attrRequest)
            .attributes()
            .get(QueueAttributeName.QUEUE_ARN);
        
        // Subscribe SQS to SNS
        subscribeSqs(snsClient, topicArn, queueArn);
        
        return topicArn;
    }
}
```

## Best Practices

### SQS Best Practices

1. **Use long polling**: Set `waitTimeSeconds` to reduce empty responses
2. **Delete messages**: Always delete after successful processing
3. **Handle visibility timeout**: Extend if processing takes longer
4. **Use FIFO queues**: When message order matters
5. **Implement DLQ**: For failed message handling
6. **Batch operations**: Use batch APIs for efficiency
7. **Monitor queue depth**: Set CloudWatch alarms
8. **Handle duplicates**: Implement idempotent processing

### SNS Best Practices

1. **Use message attributes**: For filtering subscriptions
2. **Implement retry logic**: Handle transient failures
3. **Monitor failed deliveries**: Set up DLQ for subscriptions
4. **Use FIFO topics**: When order and deduplication matter
5. **Filter subscriptions**: Use filter policies to reduce noise
6. **Encrypt messages**: Use KMS for sensitive data

## Testing

### LocalStack Integration

```java
@TestConfiguration
public class LocalStackMessagingConfig {
    
    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(
            LocalStackContainer.Service.SQS,
            LocalStackContainer.Service.SNS
        );
    
    @Bean
    public SqsClient sqsClient() {
        return SqsClient.builder()
            .region(Region.US_EAST_1)
            .endpointOverride(
                localstack.getEndpointOverride(LocalStackContainer.Service.SQS))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    localstack.getAccessKey(), 
                    localstack.getSecretKey())))
            .build();
    }
    
    @Bean
    public SnsClient snsClient() {
        return SnsClient.builder()
            .region(Region.US_EAST_1)
            .endpointOverride(
                localstack.getEndpointOverride(LocalStackContainer.Service.SNS))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    localstack.getAccessKey(), 
                    localstack.getSecretKey())))
            .build();
    }
}
```

## Related Skills

- @aws-sdk-java-v2-core - Core AWS SDK patterns
- @spring-boot-event-driven-patterns - Event-driven architecture
- @unit-test-service-layer - Service testing patterns

## References

- [SQS Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/sqs)
- [SNS Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/sns)
- [SQS API Reference](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/sqs/package-summary.html)
- [SNS API Reference](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/sns/package-summary.html)
