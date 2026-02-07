# Detailed SNS Operations Reference

## Topic Management

### Create Standard Topic
```java
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

### Topic Operations
```java
public List<Topic> listTopics(SnsClient snsClient) {
    return snsClient.listTopics().topics();
}

public String getTopicArn(SnsClient snsClient, String topicName) {
    return snsClient.createTopic(CreateTopicRequest.builder()
        .name(topicName)
        .build()).topicArn();
}
```

## Message Publishing

### Publish Basic Message
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

### Publish with Subject
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

### Publish with Attributes
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

### Publish FIFO Message
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

## Subscription Management

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

### Subscription Operations
```java
public List<Subscription> listSubscriptions(SnsClient snsClient, String topicArn) {
    return snsClient.listSubscriptionsByTopic(ListSubscriptionsByTopicRequest.builder()
        .topicArn(topicArn)
        .build()).subscriptions();
}

public void unsubscribe(SnsClient snsClient, String subscriptionArn) {
    snsClient.unsubscribe(UnsubscribeRequest.builder()
        .subscriptionArn(subscriptionArn)
        .build());
}
```