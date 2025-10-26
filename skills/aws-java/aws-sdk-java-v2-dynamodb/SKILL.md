---
name: aws-sdk-java-v2-dynamodb
description: Amazon DynamoDB patterns using AWS SDK for Java 2.x. Use when working with DynamoDB tables, items (CRUD operations), queries, scans, batch operations, transactions, DynamoDB Enhanced Client, or GSI/LSI indexes.
category: aws
tags: [aws, dynamodb, java, sdk, nosql, database]
version: 1.0.1
allowed-tools: Read, Write, Bash
---

# AWS SDK for Java 2.x - Amazon DynamoDB

## When to Use

Use this skill when:
- Creating, updating, or deleting DynamoDB tables
- Performing CRUD operations on DynamoDB items
- Querying or scanning tables
- Working with Global Secondary Indexes (GSI) or Local Secondary Indexes (LSI)
- Using batch operations for efficiency
- Implementing DynamoDB transactions
- Using DynamoDB Enhanced Client for type-safe operations
- Working with DynamoDB Streams

## Dependencies

```xml
<!-- Low-level DynamoDB client -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>dynamodb</artifactId>
</dependency>

<!-- Enhanced client (recommended) -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>dynamodb-enhanced</artifactId>
</dependency>
```

## Client Setup

### Low-Level Client

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

DynamoDbClient dynamoDb = DynamoDbClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Enhanced Client (Recommended)

```java
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;

DynamoDbEnhancedClient enhancedClient = DynamoDbEnhancedClient.builder()
    .dynamoDbClient(dynamoDb)
    .build();
```

## Enhanced Client - Entity Mapping

### Define Entity

```java
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.*;

@DynamoDbBean
public class Customer {
    
    private String customerId;
    private String name;
    private String email;
    private LocalDateTime createdAt;
    private Integer points;
    
    @DynamoDbPartitionKey
    public String getCustomerId() {
        return customerId;
    }
    
    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }
    
    @DynamoDbAttribute("customer_name")
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    @DynamoDbConvertedBy(LocalDateTimeConverter.class)
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public Integer getPoints() {
        return points;
    }
    
    public void setPoints(Integer points) {
        this.points = points;
    }
}
```

### Entity with Sort Key

```java
@DynamoDbBean
public class Order {
    
    private String customerId;
    private String orderId;
    private String status;
    private BigDecimal total;
    
    @DynamoDbPartitionKey
    @DynamoDbAttribute("customer_id")
    public String getCustomerId() {
        return customerId;
    }
    
    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }
    
    @DynamoDbSortKey
    @DynamoDbAttribute("order_id")
    public String getOrderId() {
        return orderId;
    }
    
    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }
    
    public String getStatus() {
        return status;
    }
    
    public void setStatus(String status) {
        this.status = status;
    }
    
    public BigDecimal getTotal() {
        return total;
    }
    
    public void setTotal(BigDecimal total) {
        this.total = total;
    }
}
```

### Entity with GSI

```java
@DynamoDbBean
public class Product {
    
    private String productId;
    private String category;
    private String name;
    private BigDecimal price;
    
    @DynamoDbPartitionKey
    public String getProductId() {
        return productId;
    }
    
    public void setProductId(String productId) {
        this.productId = productId;
    }
    
    @DynamoDbSecondaryPartitionKey(indexNames = "category-index")
    public String getCategory() {
        return category;
    }
    
    public void setCategory(String category) {
        this.category = category;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    @DynamoDbSecondarySortKey(indexNames = "category-index")
    public BigDecimal getPrice() {
        return price;
    }
    
    public void setPrice(BigDecimal price) {
        this.price = price;
    }
}
```

## Enhanced Client - CRUD Operations

### Create Table

```java
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;

public void createTable(DynamoDbEnhancedClient enhancedClient) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    table.createTable();
}
```

### Put Item

```java
public void putItem(DynamoDbEnhancedClient enhancedClient, Customer customer) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    table.putItem(customer);
}
```

### Get Item

```java
import software.amazon.awssdk.enhanced.dynamodb.Key;

public Customer getItem(DynamoDbEnhancedClient enhancedClient, String customerId) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    Key key = Key.builder()
        .partitionValue(customerId)
        .build();
    
    return table.getItem(key);
}
```

### Get Item with Composite Key

```java
public Order getOrder(DynamoDbEnhancedClient enhancedClient, 
                      String customerId, String orderId) {
    DynamoDbTable<Order> table = enhancedClient.table(
        "Orders", 
        TableSchema.fromBean(Order.class));
    
    Key key = Key.builder()
        .partitionValue(customerId)
        .sortValue(orderId)
        .build();
    
    return table.getItem(key);
}
```

### Update Item

```java
public Customer updateItem(DynamoDbEnhancedClient enhancedClient, Customer customer) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    return table.updateItem(customer);
}
```

### Delete Item

```java
public void deleteItem(DynamoDbEnhancedClient enhancedClient, String customerId) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    Key key = Key.builder()
        .partitionValue(customerId)
        .build();
    
    table.deleteItem(key);
}
```

## Query Operations

### Query by Partition Key

```java
import software.amazon.awssdk.enhanced.dynamodb.model.QueryConditional;

public List<Order> queryOrdersByCustomer(DynamoDbEnhancedClient enhancedClient, 
                                          String customerId) {
    DynamoDbTable<Order> table = enhancedClient.table(
        "Orders", 
        TableSchema.fromBean(Order.class));
    
    QueryConditional queryConditional = QueryConditional
        .keyEqualTo(Key.builder()
            .partitionValue(customerId)
            .build());
    
    return table.query(queryConditional).items().stream()
        .collect(Collectors.toList());
}
```

### Query with Sort Key Condition

```java
public List<Order> queryOrdersByDateRange(DynamoDbEnhancedClient enhancedClient,
                                          String customerId, 
                                          String startDate, 
                                          String endDate) {
    DynamoDbTable<Order> table = enhancedClient.table(
        "Orders", 
        TableSchema.fromBean(Order.class));
    
    QueryConditional queryConditional = QueryConditional
        .sortBetween(
            Key.builder().partitionValue(customerId).sortValue(startDate).build(),
            Key.builder().partitionValue(customerId).sortValue(endDate).build());
    
    return table.query(queryConditional).items().stream()
        .collect(Collectors.toList());
}
```

### Query with Filter Expression

```java
import software.amazon.awssdk.enhanced.dynamodb.Expression;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;

public List<Order> queryPendingOrders(DynamoDbEnhancedClient enhancedClient, 
                                       String customerId) {
    DynamoDbTable<Order> table = enhancedClient.table(
        "Orders", 
        TableSchema.fromBean(Order.class));
    
    Expression filterExpression = Expression.builder()
        .expression("#status = :pending")
        .putExpressionName("#status", "status")
        .putExpressionValue(":pending", AttributeValue.builder().s("PENDING").build())
        .build();
    
    QueryConditional queryConditional = QueryConditional
        .keyEqualTo(Key.builder().partitionValue(customerId).build());
    
    return table.query(r -> r
        .queryConditional(queryConditional)
        .filterExpression(filterExpression))
        .items().stream()
        .collect(Collectors.toList());
}
```

### Query GSI

```java
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbIndex;

public List<Product> queryProductsByCategory(DynamoDbEnhancedClient enhancedClient, 
                                               String category) {
    DynamoDbTable<Product> table = enhancedClient.table(
        "Products", 
        TableSchema.fromBean(Product.class));
    
    DynamoDbIndex<Product> index = table.index("category-index");
    
    QueryConditional queryConditional = QueryConditional
        .keyEqualTo(Key.builder().partitionValue(category).build());
    
    return index.query(queryConditional).stream()
        .flatMap(page -> page.items().stream())
        .collect(Collectors.toList());
}
```

## Scan Operations

### Scan All Items

```java
public List<Customer> scanAllCustomers(DynamoDbEnhancedClient enhancedClient) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    return table.scan().items().stream()
        .collect(Collectors.toList());
}
```

### Scan with Filter

```java
public List<Customer> scanVipCustomers(DynamoDbEnhancedClient enhancedClient) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    Expression filterExpression = Expression.builder()
        .expression("points >= :minPoints")
        .putExpressionValue(":minPoints", 
            AttributeValue.builder().n("1000").build())
        .build();
    
    return table.scan(r -> r.filterExpression(filterExpression))
        .items().stream()
        .collect(Collectors.toList());
}
```

## Batch Operations

### Batch Get

```java
import software.amazon.awssdk.enhanced.dynamodb.model.*;

public List<Customer> batchGet(DynamoDbEnhancedClient enhancedClient, List<String> customerIds) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    List<Key> keys = customerIds.stream()
        .map(id -> Key.builder().partitionValue(id).build())
        .collect(Collectors.toList());
    
    ReadBatch.Builder<Customer> batchBuilder = ReadBatch.builder(Customer.class)
        .mappedTableResource(table);
    
    keys.forEach(batchBuilder::addGetItem);
    
    BatchGetResultPageIterable result = enhancedClient.batchGetItem(r -> 
        r.addReadBatch(batchBuilder.build()));
    
    return result.resultsForTable(table).stream()
        .collect(Collectors.toList());
}
```

### Batch Write

```java
public void batchWrite(DynamoDbEnhancedClient enhancedClient, List<Customer> customers) {
    DynamoDbTable<Customer> table = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    WriteBatch.Builder<Customer> batchBuilder = WriteBatch.builder(Customer.class)
        .mappedTableResource(table);
    
    customers.forEach(batchBuilder::addPutItem);
    
    enhancedClient.batchWriteItem(r -> r.addWriteBatch(batchBuilder.build()));
}
```

## Transactions

### Transactional Write

```java
public void transactionalWrite(DynamoDbEnhancedClient enhancedClient,
                                Customer customer, Order order) {
    DynamoDbTable<Customer> customerTable = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    DynamoDbTable<Order> orderTable = enhancedClient.table(
        "Orders", 
        TableSchema.fromBean(Order.class));
    
    enhancedClient.transactWriteItems(r -> r
        .addPutItem(customerTable, customer)
        .addPutItem(orderTable, order));
}
```

### Transactional Read

```java
public Map<String, Object> transactionalRead(DynamoDbEnhancedClient enhancedClient,
                                              String customerId, String orderId) {
    DynamoDbTable<Customer> customerTable = enhancedClient.table(
        "Customers", 
        TableSchema.fromBean(Customer.class));
    
    DynamoDbTable<Order> orderTable = enhancedClient.table(
        "Orders", 
        TableSchema.fromBean(Order.class));
    
    Key customerKey = Key.builder().partitionValue(customerId).build();
    Key orderKey = Key.builder()
        .partitionValue(customerId)
        .sortValue(orderId)
        .build();
    
    TransactGetItemsEnhancedRequest request = TransactGetItemsEnhancedRequest.builder()
        .addGetItem(customerTable, customerKey)
        .addGetItem(orderTable, orderKey)
        .build();
    
    List<Document> results = enhancedClient.transactGetItems(request);
    
    return Map.of(
        "customer", results.get(0).getItem(customerTable),
        "order", results.get(1).getItem(orderTable)
    );
}
```

## Low-Level Client Operations

### Put Item (Low-Level)

```java
import software.amazon.awssdk.services.dynamodb.model.*;
import java.util.HashMap;

public void putItemLowLevel(DynamoDbClient dynamoDb, String customerId, String name) {
    HashMap<String, AttributeValue> itemValues = new HashMap<>();
    itemValues.put("customer_id", AttributeValue.builder().s(customerId).build());
    itemValues.put("name", AttributeValue.builder().s(name).build());
    
    PutItemRequest request = PutItemRequest.builder()
        .tableName("Customers")
        .item(itemValues)
        .build();
    
    dynamoDb.putItem(request);
}
```

### Query (Low-Level)

```java
public List<Map<String, AttributeValue>> queryLowLevel(DynamoDbClient dynamoDb, 
                                                        String customerId) {
    QueryRequest request = QueryRequest.builder()
        .tableName("Orders")
        .keyConditionExpression("customer_id = :customerId")
        .expressionAttributeValues(Map.of(
            ":customerId", AttributeValue.builder().s(customerId).build()))
        .build();
    
    QueryResponse response = dynamoDb.query(request);
    
    return response.items();
}
```

## Spring Boot Integration

### Configuration

```java
@Configuration
public class DynamoDbConfiguration {
    
    @Bean
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
            .region(Region.US_EAST_1)
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

### Repository Pattern

```java
@Repository
public class CustomerRepository {
    
    private final DynamoDbTable<Customer> customerTable;
    
    public CustomerRepository(DynamoDbEnhancedClient enhancedClient) {
        this.customerTable = enhancedClient.table(
            "Customers", 
            TableSchema.fromBean(Customer.class));
    }
    
    public void save(Customer customer) {
        customerTable.putItem(customer);
    }
    
    public Optional<Customer> findById(String customerId) {
        Key key = Key.builder().partitionValue(customerId).build();
        return Optional.ofNullable(customerTable.getItem(key));
    }
    
    public void delete(String customerId) {
        Key key = Key.builder().partitionValue(customerId).build();
        customerTable.deleteItem(key);
    }
    
    public List<Customer> findAll() {
        return customerTable.scan().items().stream()
            .collect(Collectors.toList());
    }
}
```

### Service Layer

```java
@Service
public class CustomerService {
    
    private final CustomerRepository customerRepository;
    
    public CustomerService(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }
    
    public void createCustomer(Customer customer) {
        customer.setCreatedAt(LocalDateTime.now());
        customerRepository.save(customer);
    }
    
    public Customer getCustomer(String customerId) {
        return customerRepository.findById(customerId)
            .orElseThrow(() -> new EntityNotFoundException("Customer not found"));
    }
    
    public void updateCustomerPoints(String customerId, Integer points) {
        Customer customer = getCustomer(customerId);
        customer.setPoints(customer.getPoints() + points);
        customerRepository.save(customer);
    }
}
```

## Best Practices

1. **Use Enhanced Client**: Type-safe operations with less boilerplate
2. **Design partition keys carefully**: Distribute data evenly across partitions
3. **Use composite keys**: Leverage sort keys for efficient queries
4. **Create GSIs strategically**: Support different access patterns
5. **Use batch operations**: Reduce API calls for multiple items
6. **Implement pagination**: For large result sets use pagination
7. **Use transactions**: For operations that must be atomic
8. **Avoid scans**: Prefer queries with proper indexes
9. **Monitor capacity**: Track read/write capacity units
10. **Use conditional writes**: Prevent race conditions

## Testing with LocalStack

```java
@TestConfiguration
public class LocalStackDynamoDbConfig {
    
    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.DYNAMODB);
    
    @Bean
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
            .region(Region.US_EAST_1)
            .endpointOverride(
                localstack.getEndpointOverride(LocalStackContainer.Service.DYNAMODB))
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
- @spring-data-jpa - Alternative data access patterns
- @unit-test-service-layer - Service testing patterns

## References

- [DynamoDB Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/dynamodb)
- [DynamoDB Enhanced Client Guide](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/ddb-en-client-gs.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
