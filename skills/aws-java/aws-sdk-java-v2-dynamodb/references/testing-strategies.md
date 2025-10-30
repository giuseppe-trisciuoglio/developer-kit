# Testing Strategies for DynamoDB

This document provides comprehensive testing strategies for DynamoDB applications using the AWS SDK for Java 2.x.

## Unit Testing with Mocks

### Mocking DynamoDbClient
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
        Customer customer = new Customer("123", "John Doe", "john@example.com");

        when(enhancedClient.table(anyString(), any(TableSchema.class)))
            .thenReturn(customerTable);

        when(customerTable.putItem(customer))
            .thenReturn(null);

        // Act
        Customer result = customerService.saveCustomer(customer);

        // Assert
        assertNotNull(result);
        assertEquals("123", result.getCustomerId());
        verify(customerTable).putItem(customer);
    }

    @Test
    void getCustomer_NotFound_ShouldReturnEmpty() {
        // Arrange
        when(enhancedClient.table(anyString(), any(TableSchema.class)))
            .thenReturn(customerTable);

        when(customerTable.getItem(any(Key.class)))
            .thenReturn(null);

        // Act
        Optional<Customer> result = customerService.getCustomer("123");

        // Assert
        assertFalse(result.isPresent());
        verify(customerTable).getItem(any(Key.class));
    }
}
```

### Testing Query Operations
```java
@Test
void queryCustomersByStatus_ShouldReturnMatchingCustomers() {
    // Arrange
    List<Customer> mockCustomers = List.of(
        new Customer("1", "Alice", "alice@example.com"),
        new Customer("2", "Bob", "bob@example.com")
    );

    DynamoDbTable<Customer> mockTable = mock(DynamoDbTable.class);
    DynamoDbIndex<Customer> mockIndex = mock(DynamoDbIndex.class);

    QueryEnhancedRequest queryRequest = QueryEnhancedRequest.builder()
        .queryConditional(QueryConditional.keyEqualTo(Key.builder()
            .partitionValue("ACTIVE")
            .build()))
        .build();

    when(enhancedClient.table("Customers", TableSchema.fromBean(Customer.class)))
        .thenReturn(mockTable);
    when(mockTable.index("status-index"))
        .thenReturn(mockIndex);
    when(mockIndex.query(queryRequest))
        .thenReturn(PaginatedQueryIterable.from(mock(Customer.class), mock(QueryResponseEnhanced.class)));

    QueryResponseEnhanced mockResponse = mock(QueryResponseEnhanced.class);
    when(mockResponse.items())
        .thenReturn(mockCustomers.stream());

    when(mockIndex.query(any(QueryEnhancedRequest.class)))
        .thenReturn(PaginatedQueryIterable.from(mock(Customer.class), mockResponse));

    // Act
    List<Customer> result = customerService.findByStatus("ACTIVE");

    // Assert
    assertEquals(2, result.size());
    verify(mockIndex).query(any(QueryEnhancedRequest.class));
}
```

## Integration Testing with Testcontainers

### LocalStack Setup
```java
@Testcontainers
@SpringBootTest
@AutoConfigureMockMvc
class DynamoDbIntegrationTest {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.DYNAMODB);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("aws.region", () -> Region.US_EAST_1.toString());
        registry.add("aws.accessKeyId", () -> localstack.getAccessKey());
        registry.add("aws.secretAccessKey", () -> localstack.getSecretKey());
        registry.add("aws.endpoint",
            () -> localstack.getEndpointOverride(LocalStackContainer.Service.DYNAMODB).toString());
    }

    @Autowired
    private DynamoDbEnhancedClient enhancedClient;

    @BeforeEach
    void setup() {
        createTestTable();
    }

    @Test
    void testCustomerCRUDOperations() {
        // Test create
        Customer customer = new Customer("test-123", "Test User", "test@example.com");
        enhancedClient.table("Customers", TableSchema.fromBean(Customer.class))
            .putItem(customer);

        // Test read
        Customer retrieved = enhancedClient.table("Customers", TableSchema.fromBean(Customer.class))
            .getItem(Key.builder().partitionValue("test-123").build());

        assertNotNull(retrieved);
        assertEquals("Test User", retrieved.getName());

        // Test update
        customer.setPoints(1000);
        enhancedClient.table("Customers", TableSchema.fromBean(Customer.class))
            .putItem(customer);

        // Test delete
        enhancedClient.table("Customers", TableSchema.fromBean(Customer.class))
            .deleteItem(Key.builder().partitionValue("test-123").build());
    }

    private void createTestTable() {
        DynamoDbClient client = DynamoDbClient.builder()
            .region(Region.US_EAST_1)
            .endpointOverride(localstack.getEndpointOverride(LocalStackContainer.Service.DYNAMODB))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(localstack.getAccessKey(), localstack.getSecretKey())))
            .build();

        CreateTableRequest request = CreateTableRequest.builder()
            .tableName("Customers")
            .keySchema(KeySchemaElement.builder()
                .attributeName("customerId")
                .keyType(KeyType.HASH)
                .build())
            .attributeDefinitions(AttributeDefinition.builder()
                .attributeName("customerId")
                .attributeType(ScalarAttributeType.S)
                .build())
            .provisionedThroughput(ProvisionedThroughput.builder()
                .readCapacityUnits(5L)
                .writeCapacityUnits(5L)
                .build())
            .build();

        client.createTable(request);
        waiterForTableActive(client, "Customers");
    }

    private void waiterForTableActive(DynamoDbClient client, String tableName) {
        Waiter waiter = client.waiter();
        CreateTableResponse response = client.createTable(request);

        waiter.waitUntilTableExists(r -> r
            .tableName(tableName)
            .maxWait(Duration.ofSeconds(30)));

        try {
            waiter.waitUntilTableExists(r -> r.tableName(tableName));
        } catch (WaiterTimeoutException e) {
            throw new RuntimeException("Table creation timed out", e);
        }
    }
}
```

### Testcontainers with H2 Migration
```java
@SpringBootTest
@Testcontainers
@AutoConfigureDataJpa
class CustomerRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void postgresProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private CustomerRepository customerRepository;

    @Autowired
    private DynamoDbEnhancedClient dynamoDbClient;

    @Test
    void testRepositoryWithRealDatabase() {
        // Test with real database
        Customer customer = new Customer("123", "Test User", "test@example.com");
        customerRepository.save(customer);

        Customer retrieved = customerRepository.findById("123").orElse(null);
        assertNotNull(retrieved);
        assertEquals("Test User", retrieved.getName());
    }
}
```

## Performance Testing

### Load Testing with Gatling
```java
class CustomerSimulation extends Simulation {
    HttpProtocolBuilder httpProtocolBuilder = http
        .baseUrl("http://localhost:8080")
        .acceptHeader("application/json");

    ScenarioBuilder scn = scenario("Customer Operations")
        .exec(http("create_customer")
            .post("/api/customers")
            .body(StringBody(
                """{
                    "customerId": "test-123",
                    "name": "Test User",
                    "email": "test@example.com"
                }"""))
            .asJson()
            .check(status().is(201)))
        .exec(http("get_customer")
            .get("/api/customers/test-123")
            .check(status().is(200)));

    {
        setUp(
            scn.injectOpen(
                rampUsersPerSec(10).to(100).during(60),
                constantUsersPerSec(100).during(120)
            )
        ).protocols(httpProtocolBuilder);
    }
}
```

### Microbenchmark Testing
```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@Warmup(iterations = 5, time = 1, timeUnit = TimeUnit.SECONDS)
@Measurement(iterations = 10, time = 1, timeUnit = TimeUnit.SECONDS)
@Fork(1)
@State(Scope.Benchmark)
public class DynamoDbPerformanceBenchmark {

    private DynamoDbEnhancedClient enhancedClient;
    private DynamoDbTable<Customer> customerTable;
    private Customer testCustomer;

    @Setup
    public void setup() {
        enhancedClient = DynamoDbEnhancedClient.builder()
            .dynamoDbClient(DynamoDbClient.builder().build())
            .build();

        customerTable = enhancedClient.table("Customers", TableSchema.fromBean(Customer.class));
        testCustomer = new Customer("benchmark-123", "Benchmark User", "benchmark@example.com");
    }

    @Benchmark
    public void testPutItem() {
        customerTable.putItem(testCustomer);
    }

    @Benchmark
    public void testGetItem() {
        customerTable.getItem(Key.builder().partitionValue("benchmark-123").build());
    }

    @Benchmark
    public void testQuery() {
        customerTable.scan().items().stream().collect(Collectors.toList());
    }
}
```

## Property-Based Testing

### Using jqwik
```java
@Property
@Report(Reporting.GENERATED)
void customerSerializationShouldBeConsistent(
    @ForAll("customers") Customer customer
) {
    // When
    String serialized = serializeCustomer(customer);
    Customer deserialized = deserializeCustomer(serialized);

    // Then
    assertEquals(customer.getCustomerId(), deserialized.getCustomerId());
    assertEquals(customer.getName(), deserialized.getName());
    assertEquals(customer.getEmail(), deserialized.getEmail());
}

@Provide
 Arbitrary<Customer> customers() {
    return Arbitraries.one(
        Arbitraries.of("customer-", "user-", "client-").string()
    ).map(id -> new Customer(
        id + Arbitraries.integers().between(1000, 9999).sample(),
        Arbitraries.strings().ofLength(10).sample(),
        Arbitraries.strings().email().sample()
    ));
}
```

## Test Data Management

### Test Data Factory
```java
@Component
public class TestDataFactory {

    private final DynamoDbEnhancedClient enhancedClient;

    @Autowired
    public TestDataFactory(DynamoDbEnhancedClient enhancedClient) {
        this.enhancedClient = enhancedClient;
    }

    public Customer createTestCustomer(String id) {
        Customer customer = new Customer(
            id != null ? id : UUID.randomUUID().toString(),
            "Test User",
            "test@example.com"
        );
        customer.setPoints(1000);
        customer.setCreatedAt(LocalDateTime.now());

        enhancedClient.table("Customers", TableSchema.fromBean(Customer.class))
            .putItem(customer);

        return customer;
    }

    public void cleanupTestData() {
        // Implementation to clean up test data
    }
}
```

### Test Database Configuration
```java
@TestConfiguration
public class TestDataConfig {

    @Bean
    public TestDataCleaner testDataCleaner() {
        return new TestDataCleaner();
    }
}

@Component
public class TestDataCleaner {

    private final DynamoDbClient dynamoDbClient;

    @EventListener(ApplicationReadyEvent.class)
    public void cleanup() {
        // Clean up test data before each test run
    }
}
```