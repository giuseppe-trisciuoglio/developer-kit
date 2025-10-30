---
name: aws-sdk-java-v2-dynamodb
description: Amazon DynamoDB patterns using AWS SDK for Java 2.x. Use when creating, querying, scanning, or performing CRUD operations on DynamoDB tables, working with indexes, batch operations, transactions, or integrating with Spring Boot applications.
category: aws
tags: [aws, dynamodb, java, sdk, nosql, database]
version: 1.1.0
allowed-tools: Read, Write, Bash
---

# AWS SDK for Java 2.x - Amazon DynamoDB

## When to Use

Use this skill when:
- Creating, updating, or deleting DynamoDB tables
- Performing CRUD operations on DynamoDB items
- Querying or scanning tables
- Working with Global Secondary Indexes (GSI) or Local Secondary Indexes (LSI)
- Implementing batch operations for efficiency
- Using DynamoDB transactions
- Integrating DynamoDB with Spring Boot applications
- Working with DynamoDB Enhanced Client for type-safe operations

## Dependencies

Add to `pom.xml`:
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

## Entity Mapping

To define DynamoDB entities, use `@DynamoDbBean` annotation:

```java
@DynamoDbBean
public class Customer {

    @DynamoDbPartitionKey
    private String customerId;

    @DynamoDbAttribute("customer_name")
    private String name;

    private String email;

    @DynamoDbSortKey
    private String orderId;

    // Getters and setters
}
```

For complex entity mapping with GSIs and custom converters, see [Entity Mapping Reference](references/entity-mapping.md).

## CRUD Operations

### Basic Operations
```java
// Create or update item
DynamoDbTable<Customer> table = enhancedClient.table("Customers", TableSchema.fromBean(Customer.class));
table.putItem(customer);

// Get item
Customer result = table.getItem(Key.builder().partitionValue(customerId).build());

// Update item
return table.updateItem(customer);

// Delete item
table.deleteItem(Key.builder().partitionValue(customerId).build());
```

### Composite Key Operations
```java
// Get item with composite key
Order order = table.getItem(Key.builder()
    .partitionValue(customerId)
    .sortValue(orderId)
    .build());
```

## Query Operations

### Basic Query
```java
import software.amazon.awssdk.enhanced.dynamodb.model.QueryConditional;

QueryConditional queryConditional = QueryConditional
    .keyEqualTo(Key.builder()
        .partitionValue(customerId)
        .build());

List<Order> orders = table.query(queryConditional).items().stream()
    .collect(Collectors.toList());
```

### Advanced Query with Filters
```java
import software.amazon.awssdk.enhanced.dynamodb.Expression;

Expression filter = Expression.builder()
    .expression("status = :pending")
    .putExpressionValue(":pending", AttributeValue.builder().s("PENDING").build())
    .build();

List<Order> pendingOrders = table.query(r -> r
    .queryConditional(queryConditional)
    .filterExpression(filter))
    .items().stream()
    .collect(Collectors.toList());
```

For detailed query patterns, see [Advanced Operations Reference](references/advanced-operations.md).

## Scan Operations

```java
// Scan all items
List<Customer> allCustomers = table.scan().items().stream()
    .collect(Collectors.toList());

// Scan with filter
Expression filter = Expression.builder()
    .expression("points >= :minPoints")
    .putExpressionValue(":minPoints", AttributeValue.builder().n("1000").build())
    .build();

List<Customer> vipCustomers = table.scan(r -> r.filterExpression(filter))
    .items().stream()
    .collect(Collectors.toList());
```

## Batch Operations

### Batch Get
```java
import software.amazon.awssdk.enhanced.dynamodb.model.*;

List<Key> keys = customerIds.stream()
    .map(id -> Key.builder().partitionValue(id).build())
    .collect(Collectors.toList());

ReadBatch.Builder<Customer> batchBuilder = ReadBatch.builder(Customer.class)
    .mappedTableResource(table);

keys.forEach(batchBuilder::addGetItem);

BatchGetResultPageIterable result = enhancedClient.batchGetItem(r ->
    r.addReadBatch(batchBuilder.build()));

List<Customer> customers = result.resultsForTable(table).stream()
    .collect(Collectors.toList());
```

### Batch Write
```java
WriteBatch.Builder<Customer> batchBuilder = WriteBatch.builder(Customer.class)
    .mappedTableResource(table);

customers.forEach(batchBuilder::addPutItem);

enhancedClient.batchWriteItem(r -> r.addWriteBatch(batchBuilder.build()));
```

## Transactions

### Transactional Write
```java
enhancedClient.transactWriteItems(r -> r
    .addPutItem(customerTable, customer)
    .addPutItem(orderTable, order));
```

### Transactional Read
```java
TransactGetItemsEnhancedRequest request = TransactGetItemsEnhancedRequest.builder()
    .addGetItem(customerTable, customerKey)
    .addGetItem(orderTable, orderKey)
    .build();

List<Document> results = enhancedClient.transactGetItems(request);
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
        this.customerTable = enhancedClient.table("Customers", TableSchema.fromBean(Customer.class));
    }

    public void save(Customer customer) {
        customerTable.putItem(customer);
    }

    public Optional<Customer> findById(String customerId) {
        Key key = Key.builder().partitionValue(customerId).build();
        return Optional.ofNullable(customerTable.getItem(key));
    }
}
```

For comprehensive Spring Boot integration patterns, see [Spring Boot Integration Reference](references/spring-boot-integration.md).

## Testing

### Unit Testing with Mocks
```java
@ExtendWith(MockitoExtension.class)
class CustomerServiceTest {

    @Mock
    private DynamoDbClient dynamoDbClient;

    @Mock
    private DynamoDbEnhancedClient enhancedClient;

    @Mock
    private DynamoDbTable<Customer> customerTable;

    @InjectMocks
    private CustomerService customerService;

    @Test
    void saveCustomer_ShouldReturnSavedCustomer() {
        // Arrange
        when(enhancedClient.table(anyString(), any(TableSchema.class)))
            .thenReturn(customerTable);

        Customer customer = new Customer("123", "John Doe", "john@example.com");

        // Act
        Customer result = customerService.saveCustomer(customer);

        // Assert
        assertNotNull(result);
        verify(customerTable).putItem(customer);
    }
}
```

### Integration Testing with LocalStack
```java
@Testcontainers
@SpringBootTest
class DynamoDbIntegrationTest {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.DYNAMODB);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("aws.endpoint",
            () -> localstack.getEndpointOverride(LocalStackContainer.Service.DYNAMODB).toString());
    }

    @Autowired
    private DynamoDbEnhancedClient enhancedClient;

    @Test
    void testCustomerCRUDOperations() {
        // Test implementation
    }
}
```

For detailed testing strategies, see [Testing Strategies](references/testing-strategies.md).

## Best Practices

1. **Use Enhanced Client**: Provides type-safe operations with less boilerplate
2. **Design partition keys carefully**: Distribute data evenly across partitions
3. **Use composite keys**: Leverage sort keys for efficient queries
4. **Create GSIs strategically**: Support different access patterns
5. **Use batch operations**: Reduce API calls for multiple items
6. **Implement pagination**: For large result sets use pagination
7. **Use transactions**: For operations that must be atomic
8. **Avoid scans**: Prefer queries with proper indexes
9. **Handle conditional writes**: Prevent race conditions
10. **Use proper error handling**: Handle exceptions like `ProvisionedThroughputExceeded`

## Common Patterns

### Conditional Operations
```java
PutItemEnhancedRequest request = PutItemEnhancedRequest.builder(table)
    .item(customer)
    .conditionExpression("attribute_not_exists(customerId)")
    .build();

table.putItemWithRequestBuilder(request);
```

### Pagination
```java
ScanEnhancedRequest request = ScanEnhancedRequest.builder()
    .limit(100)
    .build();

PaginatedScanIterable<Customer> results = table.scan(request);
results.stream().forEach(page -> {
    // Process each page
});
```

## Performance Considerations

- Monitor read/write capacity units
- Implement exponential backoff for retries
- Use proper pagination for large datasets
- Consider eventual consistency for reads
- Use `ReturnConsumedCapacity` to monitor capacity usage

## Related Skills

- `aws-sdk-java-v2-core `- Core AWS SDK patterns
- `spring-data-jpa` - Alternative data access patterns
- `unit-test-service-layer` - Service testing patterns
- `unit-test-wiremock-rest-api` - Testing external APIs

## References

- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [AWS SDK for Java Documentation](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/)
- [DynamoDB Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/dynamodb)
- [LocalStack for Testing](https://docs.localstack.cloud/user-guide/aws/)

For detailed implementations, see the references folder:
- [Entity Mapping Reference](references/entity-mapping.md)
- [Advanced Operations Reference](references/advanced-operations.md)
- [Spring Boot Integration Reference](references/spring-boot-integration.md)
- [Testing Strategies](references/testing-strategies.md)