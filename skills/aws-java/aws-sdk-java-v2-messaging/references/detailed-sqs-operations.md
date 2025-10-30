# Detailed SQS Operations Reference

## Queue Management

### Create Standard Queue
```java
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

### Queue Operations
```java
public String getQueueUrl(SqsClient sqsClient, String queueName) {
    return sqsClient.getQueueUrl(GetQueueUrlRequest.builder()
        .queueName(queueName)
        .build()).queueUrl();
}

public List<String> listQueues(SqsClient sqsClient) {
    return sqsClient.listQueues().queueUrls();
}

public void purgeQueue(SqsClient sqsClient, String queueUrl) {
    sqsClient.purgeQueue(PurgeQueueRequest.builder()
        .queueUrl(queueUrl)
        .build());
}
```

## Message Operations

### Send Basic Message
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

### Send FIFO Message
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

## Message Processing

### Receive Messages with Long Polling
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