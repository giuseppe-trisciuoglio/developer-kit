# Spring Boot Integration Reference

This document provides detailed information about integrating DynamoDB with Spring Boot applications.

## Configuration

### Basic Configuration
```java
@Configuration
public class DynamoDbConfiguration {

    @Bean
    @Profile("local")
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    @Profile("prod")
    public DynamoDbClient dynamoDbClientProd(
            @Value("${aws.region}") String region,
            @Value("${aws.accessKeyId}") String accessKeyId,
            @Value("${aws.secretAccessKey}") String secretAccessKey) {

        return DynamoDbClient.builder()
            .region(Region.of(region))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(accessKeyId, secretAccessKey)))
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

### Properties Configuration
`application-local.properties`:
```properties
aws.region=us-east-1
```

`application-prod.properties`:
```properties
aws.region=us-east-1
aws.accessKeyId=${AWS_ACCESS_KEY_ID}
aws.secretAccessKey=${AWS_SECRET_ACCESS_KEY}
```

## Repository Pattern Implementation

### Base Repository Interface
```java
public interface DynamoDbRepository<T> {
    void save(T entity);
    Optional<T> findById(Object partitionKey);
    Optional<T> findById(Object partitionKey, Object sortKey);
    void delete(Object partitionKey);
    void delete(Object partitionKey, Object sortKey);
    List<T> findAll();
    List<T> findAll(int limit);
    boolean existsById(Object partitionKey);
    boolean existsById(Object partitionKey, Object sortKey);
}

public interface CustomerRepository extends DynamoDbRepository<Customer> {
    List<Customer> findByEmail(String email);
    List<Customer> findByPointsGreaterThan(Integer minPoints);
}
```

### Generic Repository Implementation
```java
@Repository
public class GenericDynamoDbRepository<T> implements DynamoDbRepository<T> {

    private final DynamoDbTable<T> table;

    @SuppressWarnings("unchecked")
    public GenericDynamoDbRepository(DynamoDbEnhancedClient enhancedClient,
                                     Class<T> entityClass,
                                     String tableName) {
        this.table = enhancedClient.table(tableName, TableSchema.fromBean(entityClass));
    }

    @Override
    public void save(T entity) {
        table.putItem(entity);
    }

    @Override
    public Optional<T> findById(Object partitionKey) {
        Key key = Key.builder().partitionValue(partitionKey).build();
        return Optional.ofNullable(table.getItem(key));
    }

    @Override
    public Optional<T> findById(Object partitionKey, Object sortKey) {
        Key key = Key.builder()
            .partitionValue(partitionKey)
            .sortValue(sortKey)
            .build();
        return Optional.ofNullable(table.getItem(key));
    }

    @Override
    public void delete(Object partitionKey) {
        Key key = Key.builder().partitionValue(partitionKey).build();
        table.deleteItem(key);
    }

    @Override
    public List<T> findAll() {
        return table.scan().items().stream()
            .collect(Collectors.toList());
    }

    @Override
    public List<T> findAll(int limit) {
        return table.scan(ScanEnhancedRequest.builder().limit(limit).build())
            .items().stream()
            .collect(Collectors.toList());
    }
}
```

### Specific Repository Implementation
```java
@Repository
public class CustomerRepositoryImpl implements CustomerRepository {

    private final DynamoDbTable<Customer> customerTable;

    public CustomerRepositoryImpl(DynamoDbEnhancedClient enhancedClient) {
        this.customerTable = enhancedClient.table(
            "Customers",
            TableSchema.fromBean(Customer.class));
    }

    @Override
    public List<Customer> findByEmail(String email) {
        Expression filter = Expression.builder()
            .expression("email = :email")
            .putExpressionValue(":email", AttributeValue.builder().s(email).build())
            .build();

        return customerTable.scan(r -> r.filterExpression(filter))
            .items().stream()
            .collect(Collectors.toList());
    }

    @Override
    public List<Customer> findByPointsGreaterThan(Integer minPoints) {
        Expression filter = Expression.builder()
            .expression("points >= :minPoints")
            .putExpressionValue(":minPoints", AttributeValue.builder().n(minPoints.toString()).build())
            .build();

        return customerTable.scan(r -> r.filterExpression(filter))
            .items().stream()
            .collect(Collectors.toList());
    }
}
```

## Service Layer Implementation

### Service with Transaction Management
```java
@Service
@Transactional
public class CustomerService {

    private final CustomerRepository customerRepository;
    private final OrderRepository orderRepository;
    private final DynamoDbEnhancedClient enhancedClient;

    public CustomerService(CustomerRepository customerRepository,
                          OrderRepository orderRepository,
                          DynamoDbEnhancedClient enhancedClient) {
        this.customerRepository = customerRepository;
        this.orderRepository = orderRepository;
        this.enhancedClient = enhancedClient;
    }

    public void createCustomerWithOrder(Customer customer, Order order) {
        // Use transaction for atomic operation
        enhancedClient.transactWriteItems(r -> r
            .addPutItem(getCustomerTable(), customer)
            .addPutItem(getOrderTable(), order));
    }

    private DynamoDbTable<Customer> getCustomerTable() {
        return enhancedClient.table("Customers", TableSchema.fromBean(Customer.class));
    }

    private DynamoDbTable<Order> getOrderTable() {
        return enhancedClient.table("Orders", TableSchema.fromBean(Order.class));
    }
}
```

### Async Operations
```java
@Service
public class AsyncCustomerService {

    private final DynamoDbEnhancedClient enhancedClient;

    public CompletableFuture<Void> saveCustomerAsync(Customer customer) {
        return CompletableFuture.runAsync(() -> {
            DynamoDbTable<Customer> table = enhancedClient.table(
                "Customers",
                TableSchema.fromBean(Customer.class));
            table.putItem(customer);
        });
    }

    public CompletableFuture<List<Customer>> findCustomersByPointsAsync(Integer minPoints) {
        return CompletableFuture.supplyAsync(() -> {
            Expression filter = Expression.builder()
                .expression("points >= :minPoints")
                .putExpressionValue(":minPoints", AttributeValue.builder().n(minPoints.toString()).build())
                .build();

            DynamoDbTable<Customer> table = enhancedClient.table(
                "Customers",
                TableSchema.fromBean(Customer.class));

            return table.scan(r -> r.filterExpression(filter))
                .items().stream()
                .collect(Collectors.toList());
        });
    }
}
```

## Testing with LocalStack

### Test Configuration
```java
@TestConfiguration
@ContextConfiguration(classes = {LocalStackDynamoDbConfig.class})
public class DynamoDbTestConfig {

    @Bean
    public DynamoDbClient dynamoDbClient() {
        return LocalStackDynamoDbConfig.dynamoDbClient();
    }

    @Bean
    public DynamoDbEnhancedClient dynamoDbEnhancedClient() {
        return DynamoDbEnhancedClient.builder()
            .dynamoDbClient(dynamoDbClient())
            .build();
    }
}

@SpringBootTest(classes = {DynamoDbTestConfig.class})
@Import(DynamoDbTestConfig.class)
public class CustomerRepositoryIntegrationTest {

    @Autowired
    private DynamoDbEnhancedClient enhancedClient;

    @BeforeEach
    void setUp() {
        // Clean up test data
        clearTestData();
    }

    @Test
    void testCustomerOperations() {
        // Test implementation
    }
}
```

### LocalStack Container Setup
```java
public class LocalStackDynamoDbConfig {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.DYNAMODB);

    @Bean
    @DynamicPropertySource
    public static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("aws.region", () -> Region.US_EAST_1.toString());
        registry.add("aws.accessKeyId", () -> localstack.getAccessKey());
        registry.add("aws.secretAccessKey", () -> localstack.getSecretKey());
        registry.add("aws.endpoint",
            () -> localstack.getEndpointOverride(LocalStackContainer.Service.DYNAMODB).toString());
    }

    @Bean
    public DynamoDbClient dynamoDbClient(
            @Value("${aws.region}") String region,
            @Value("${aws.accessKeyId}") String accessKeyId,
            @Value("${aws.secretAccessKey}") String secretAccessKey,
            @Value("${aws.endpoint}") String endpoint) {

        return DynamoDbClient.builder()
            .region(Region.of(region))
            .endpointOverride(URI.create(endpoint))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(accessKeyId, secretAccessKey)))
            .build();
    }
}
```

## Health Check Integration

### Custom Health Indicator
```java
@Component
public class DynamoDbHealthIndicator implements HealthIndicator {

    private final DynamoDbClient dynamoDbClient;

    public DynamoDbHealthIndicator(DynamoDbClient dynamoDbClient) {
        this.dynamoDbClient = dynamoDbClient;
    }

    @Override
    public Health health() {
        try {
            dynamoDbClient.listTables();
            return Health.up()
                .withDetail("region", dynamoDbClient.serviceClientConfiguration().region())
                .build();
        } catch (Exception e) {
            return Health.down()
                .withException(e)
                .build();
        }
    }
}
```

## Metrics Collection

### Micrometer Integration
```java
@Component
public class DynamoDbMetricsCollector {

    private final DynamoDbClient dynamoDbClient;
    private final MeterRegistry meterRegistry;

    @EventListener
    public void handleDynamoDbOperation(DynamoDbOperationEvent event) {
        Timer.Sample sample = Timer.start();
        sample.stop(Timer.builder("dynamodb.operation")
            .tag("operation", event.getOperation())
            .tag("table", event.getTable())
            .register(meterRegistry));
    }
}

public class DynamoDbOperationEvent {
    private String operation;
    private String table;
    private long duration;

    // Getters and setters
}
```