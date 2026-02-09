# Advanced Operations Reference

This document covers advanced DynamoDB operations and patterns.

## Query Operations

### Key Conditions

#### Key.equalTo()
```java
QueryConditional equalTo = QueryConditional
    .keyEqualTo(Key.builder()
        .partitionValue("customer123")
        .build());
```

#### Key.between()
```java
QueryConditional between = QueryConditional
    .sortBetween(
        Key.builder().partitionValue("customer123").sortValue("2023-01-01").build(),
        Key.builder().partitionValue("customer123").sortValue("2023-12-31").build());
```

#### Key.beginsWith()
```java
QueryConditional beginsWith = QueryConditional
    .sortKeyBeginsWith(Key.builder()
        .partitionValue("customer123")
        .sortValue("2023-")
        .build());
```

### Filter Expressions

```java
Expression filter = Expression.builder()
    .expression("points >= :minPoints AND status = :status")
    .putExpressionName("#p", "points")
    .putExpressionName("#s", "status")
    .putExpressionValue(":minPoints", AttributeValue.builder().n("1000").build())
    .putExpressionValue(":status", AttributeValue.builder().s("ACTIVE").build())
    .build();
```

### Projection Expressions

```java
Expression projection = Expression.builder()
    .expression("customerId, name, email")
    .putExpressionName("#c", "customerId")
    .putExpressionName("#n", "name")
    .putExpressionName("#e", "email")
    .build();
```

## Scan Operations

### Pagination
```java
ScanEnhancedRequest request = ScanEnhancedRequest.builder()
    .limit(100)
    .build();

PaginatedScanIterable<Customer> results = table.scan(request);
results.stream().forEach(page -> {
    // Process each page of results
});
```

### Conditional Scan
```java
Expression filter = Expression.builder()
    .expression("active = :active")
    .putExpressionValue(":active", AttributeValue.builder().bool(true).build())
    .build();

return table.scan(r -> r
    .filterExpression(filter)
    .limit(50))
    .items().stream()
    .collect(Collectors.toList());
```

## Batch Operations

### Batch Get with Unprocessed Keys
```java
List<Key> keys = customerIds.stream()
    .map(id -> Key.builder().partitionValue(id).build())
    .collect(Collectors.toList());

ReadBatch.Builder<Customer> batchBuilder = ReadBatch.builder(Customer.class)
    .mappedTableResource(table);

keys.forEach(batchBuilder::addGetItem);

BatchGetResultPageIterable result = enhancedClient.batchGetItem(r ->
    r.addReadBatch(batchBuilder.build()));

// Handle unprocessed keys
result.stream()
    .flatMap(page -> page.unprocessedKeys().entrySet().stream())
    .forEach(entry -> {
        // Retry logic for unprocessed keys
    });
```

### Batch Write with Different Operations
```java
WriteBatch.Builder<Customer> batchBuilder = WriteBatch.builder(Customer.class)
    .mappedTableResource(table);

batchBuilder.addPutItem(customer1);
batchBuilder.addDeleteItem(customer2);
batchBuilder.addPutItem(customer3);

enhancedClient.batchWriteItem(r -> r.addWriteBatch(batchBuilder.build()));
```

## Transactions

### Conditional Writes
```java
PutItemEnhancedRequest putRequest = PutItemEnhancedRequest.builder(table)
    .item(customer)
    .conditionExpression("attribute_not_exists(customerId)")
    .build();

table.putItemWithRequestBuilder(putRequest);
```

### Multiple Table Operations
```java
TransactWriteItemsEnhancedRequest request = TransactWriteItemsEnhancedRequest.builder()
    .addPutItem(customerTable, customer)
    .addPutItem(orderTable, order)
    .addUpdateItem(productTable, product)
    .addDeleteItem(cartTable, cartKey)
    .build();

enhancedClient.transactWriteItems(request);
```

## Conditional Operations

### Condition Expressions
```java
// Check if attribute exists
.setAttribute("conditionExpression", "attribute_not_exists(customerId)")

// Check attribute values
.setAttribute("conditionExpression", "points > :currentPoints")
.setAttribute("expressionAttributeValues", Map.of(
    ":currentPoints", AttributeValue.builder().n("500").build()))

// Multiple conditions
.setAttribute("conditionExpression", "points > :min AND active = :active")
.setAttribute("expressionAttributeValues", Map.of(
    ":min", AttributeValue.builder().n("100").build(),
    ":active", AttributeValue.builder().bool(true).build()))
```

## Error Handling

### Provisioned Throughput Exceeded
```java
try {
    table.putItem(customer);
} catch (TransactionCanceledException e) {
    // Handle transaction cancellation
} catch (ConditionalCheckFailedException e) {
    // Handle conditional check failure
} catch (ResourceNotFoundException e) {
    // Handle table not found
} catch (DynamoDbException e) {
    // Handle other DynamoDB exceptions
}
```

### Exponential Backoff for Retry
```java
int maxRetries = 3;
long baseDelay = 1000; // 1 second

for (int attempt = 0; attempt < maxRetries; attempt++) {
    try {
        operation();
        break;
    } catch (ProvisionedThroughputExceededException e) {
        long delay = baseDelay * (1 << attempt);
        Thread.sleep(delay);
    }
}
```