# Spring Boot Integration Reference

## Configuration

### Basic Bean Configuration
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

### Configuration Properties
```yaml
# application.yml
aws:
  sqs:
    queue-url: https://sqs.us-east-1.amazonaws.com/123456789012/my-queue
  sns:
    topic-arn: arn:aws:sns:us-east-1:123456789012:my-topic
```

## Service Layer Integration

### SQS Message Service
```java
@Service
@RequiredArgsConstructor
public class SqsMessageService {

    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;

    @Value("${aws.sqs.queue-url}")
    private String queueUrl;

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
@RequiredArgsConstructor
public class SnsNotificationService {

    private final SnsClient snsClient;
    private final ObjectMapper objectMapper;

    @Value("${aws.sns.topic-arn}")
    private String topicArn;

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

## Message Listener Pattern

### Scheduled Polling
```java
@Service
@RequiredArgsConstructor
public class SqsMessageListener {

    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;

    @Value("${aws.sqs.queue-url}")
    private String queueUrl;

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

## Pub/Sub Pattern Integration

### Configuration for Pub/Sub
```java
@Configuration
@RequiredArgsConstructor
public class PubSubConfiguration {

    private final SnsClient snsClient;
    private final SqsClient sqsClient;

    @Bean
    @DependsOn("sqsClient")
    public String setupPubSub() {
        // Create SNS topic
        String topicArn = snsClient.createTopic(CreateTopicRequest.builder()
            .name("order-events")
            .build()).topicArn();

        // Create SQS queue
        String queueUrl = sqsClient.createQueue(CreateQueueRequest.builder()
            .queueName("order-processor")
            .build()).queueUrl();

        // Get queue ARN
        String queueArn = sqsClient.getQueueAttributes(GetQueueAttributesRequest.builder()
            .queueUrl(queueUrl)
            .attributeNames(QueueAttributeName.QUEUE_ARN)
            .build()).attributes().get(QueueAttributeName.QUEUE_ARN);

        // Subscribe SQS to SNS
        snsClient.subscribe(SubscribeRequest.builder()
            .protocol("sqs")
            .endpoint(queueArn)
            .topicArn(topicArn)
            .build());

        return topicArn;
    }
}
```

## Error Handling Patterns

### Retry Mechanism
```java
@Service
@RequiredArgsConstructor
public class RetryableSqsService {

    private final SqsClient sqsClient;
    private final RetryTemplate retryTemplate;

    public void sendMessageWithRetry(String queueUrl, String messageBody) {
        retryTemplate.execute(context -> {
            try {
                SendMessageRequest request = SendMessageRequest.builder()
                    .queueUrl(queueUrl)
                    .messageBody(messageBody)
                    .build();

                sqsClient.sendMessage(request);
                return null;
            } catch (Exception e) {
                throw new RetryableException("Failed to send message", e);
            }
        });
    }
}
```

## Testing Integration

### LocalStack Configuration
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