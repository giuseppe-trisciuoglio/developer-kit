# Testing Strategies for Camel Routes

Comprehensive testing is essential for reliable Camel integration solutions. This guide covers unit testing, integration testing, and testing best practices.

## Testing Dependencies

### Maven Dependencies

```xml
<!-- Camel Test Support -->
<dependency>
    <groupId>org.apache.camel</groupId>
    <artifactId>camel-test-spring-junit5</artifactId>
    <scope>test</scope>
</dependency>

<!-- Spring Boot Test -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>

<!-- Testcontainers (for integration testing) -->
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>kafka</artifactId>
    <scope>test</scope>
</dependency>
```

## Unit Testing with CamelTestSupport

### Basic Route Test

```java
import org.apache.camel.RoutesBuilder;
import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.test.junit5.CamelTestSupport;
import org.junit.jupiter.api.Test;

class SimpleRouteTest extends CamelTestSupport {

    @Override
    protected RoutesBuilder createRouteBuilder() {
        return new RouteBuilder() {
            @Override
            public void configure() {
                from("direct:start")
                    .transform(body().append(" processed"))
                    .to("mock:result");
            }
        };
    }

    @Test
    void testRoute() throws Exception {
        getMockEndpoint("mock:result").expectedMessageCount(1);
        getMockEndpoint("mock:result").expectedBodiesReceived("Hello processed");

        template.sendBody("direct:start", "Hello");

        assertMockEndpointsSatisfied();
    }
}
```

### Testing with Headers

```java
@Test
void testHeaderPropagation() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedHeaderReceived("CustomHeader", "testValue");
    mock.expectedMessageCount(1);

    template.sendBodyAndHeader("direct:start", "test body", "CustomHeader", "testValue");

    assertMockEndpointsSatisfied();
}
```

### Testing Message Transformations

```java
@Test
void testTransformation() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedBodiesReceived("{\"name\":\"John\",\"age\":30}");

    User user = new User("John", 30);
    template.sendBody("direct:transform", user);

    assertMockEndpointsSatisfied();
}
```

## Spring Boot Integration Testing

### Basic Spring Boot Test

```java
import org.apache.camel.CamelContext;
import org.apache.camel.ProducerTemplate;
import org.apache.camel.test.spring.junit5.CamelSpringBootTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@CamelSpringBootTest
@SpringBootTest
class OrderProcessingRouteTest {

    @Autowired
    private ProducerTemplate producerTemplate;

    @Autowired
    private CamelContext camelContext;

    @Test
    void testOrderProcessing() throws Exception {
        MockEndpoint mockResult = camelContext.getEndpoint("mock:result", MockEndpoint.class);
        mockResult.expectedMessageCount(1);

        Order order = new Order("123", 100.0);
        producerTemplate.sendBody("direct:process-order", order);

        mockResult.assertIsSatisfied();
    }
}
```

### Using Mock Endpoints with @MockEndpoints

```java
@CamelSpringBootTest
@SpringBootTest
@MockEndpoints("jms:*") // Mock all JMS endpoints
class OrderRouteWithMocksTest {

    @EndpointInject("mock:jms:queue:orders")
    private MockEndpoint mockOrders;

    @Produce("direct:start")
    private ProducerTemplate producer;

    @Test
    void testOrderRouting() throws Exception {
        mockOrders.expectedMessageCount(1);
        mockOrders.expectedBodiesReceived(new Order("123", 100.0));

        producer.sendBody(new Order("123", 100.0));

        mockOrders.assertIsSatisfied();
    }
}
```

### Selective Endpoint Mocking

```java
@CamelSpringBootTest
@SpringBootTest
@MockEndpoints("http:*")  // Mock only HTTP endpoints
class HttpIntegrationTest {

    @EndpointInject("mock:http:api.example.com/orders")
    private MockEndpoint mockHttp;

    @Produce("direct:create-order")
    private ProducerTemplate producer;

    @Test
    void testHttpCall() throws Exception {
        mockHttp.expectedMessageCount(1);
        mockHttp.whenAnyExchangeReceived(exchange ->
            exchange.getIn().setBody("{\"status\":\"success\",\"orderId\":\"123\"}")
        );

        String result = producer.requestBody("direct:create-order", new Order(), String.class);

        mockHttp.assertIsSatisfied();
        assertNotNull(result);
    }
}
```

## Advanced Testing Patterns

### Testing Content-Based Routing

```java
@Override
protected RoutesBuilder createRouteBuilder() {
    return new RouteBuilder() {
        @Override
        public void configure() {
            from("direct:route")
                .choice()
                    .when(simple("${body.priority} == 'HIGH'"))
                        .to("mock:high")
                    .when(simple("${body.amount} > 1000"))
                        .to("mock:large")
                    .otherwise()
                        .to("mock:standard")
                .end();
        }
    };
}

@Test
void testHighPriorityRouting() throws Exception {
    getMockEndpoint("mock:high").expectedMessageCount(1);
    getMockEndpoint("mock:large").expectedMessageCount(0);
    getMockEndpoint("mock:standard").expectedMessageCount(0);

    Order order = new Order();
    order.setPriority("HIGH");
    order.setAmount(500.0);

    template.sendBody("direct:route", order);

    assertMockEndpointsSatisfied();
}

@Test
void testLargeOrderRouting() throws Exception {
    getMockEndpoint("mock:high").expectedMessageCount(0);
    getMockEndpoint("mock:large").expectedMessageCount(1);
    getMockEndpoint("mock:standard").expectedMessageCount(0);

    Order order = new Order();
    order.setPriority("NORMAL");
    order.setAmount(1500.0);

    template.sendBody("direct:route", order);

    assertMockEndpointsSatisfied();
}
```

### Testing Aggregation

```java
@Test
void testAggregation() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:aggregated");
    mock.expectedMessageCount(1);
    mock.expectedMessagesMatches(exchange -> {
        @SuppressWarnings("unchecked")
        List<String> body = exchange.getIn().getBody(List.class);
        return body.size() == 3;
    });

    template.sendBodyAndHeader("direct:aggregate", "msg1", "correlationId", "123");
    template.sendBodyAndHeader("direct:aggregate", "msg2", "correlationId", "123");
    template.sendBodyAndHeader("direct:aggregate", "msg3", "correlationId", "123");

    assertMockEndpointsSatisfied();
}
```

### Testing Splitter

```java
@Test
void testSplitter() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:split");
    mock.expectedMessageCount(3);
    mock.expectedBodiesReceivedInAnyOrder("item1", "item2", "item3");

    List<String> items = Arrays.asList("item1", "item2", "item3");
    template.sendBody("direct:split", items);

    assertMockEndpointsSatisfied();
}
```

### Testing Error Handling

```java
@Override
protected RoutesBuilder createRouteBuilder() {
    return new RouteBuilder() {
        @Override
        public void configure() {
            onException(IllegalArgumentException.class)
                .handled(true)
                .to("mock:error");

            from("direct:start")
                .process(exchange -> {
                    String body = exchange.getIn().getBody(String.class);
                    if (body.equals("error")) {
                        throw new IllegalArgumentException("Invalid input");
                    }
                })
                .to("mock:success");
        }
    };
}

@Test
void testExceptionHandling() throws Exception {
    getMockEndpoint("mock:error").expectedMessageCount(1);
    getMockEndpoint("mock:success").expectedMessageCount(0);

    template.sendBody("direct:start", "error");

    assertMockEndpointsSatisfied();
}

@Test
void testSuccessPath() throws Exception {
    getMockEndpoint("mock:error").expectedMessageCount(0);
    getMockEndpoint("mock:success").expectedMessageCount(1);

    template.sendBody("direct:start", "valid");

    assertMockEndpointsSatisfied();
}
```

### Testing Retries and Redelivery

```java
@Test
void testRedelivery() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(1);

    // Simulate failure on first 2 attempts, success on 3rd
    AtomicInteger counter = new AtomicInteger(0);
    mock.whenAnyExchangeReceived(exchange -> {
        if (counter.incrementAndGet() < 3) {
            throw new RuntimeException("Simulated failure");
        }
    });

    template.sendBody("direct:retry", "test");

    // Verify redelivery happened
    mock.assertIsSatisfied();
    assertEquals(3, counter.get());
}
```

## Testing with External Systems

### Testing with Testcontainers (Kafka)

```java
@CamelSpringBootTest
@SpringBootTest
@Testcontainers
class KafkaIntegrationTest {

    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0")
    );

    @DynamicPropertySource
    static void kafkaProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
        registry.add("camel.component.kafka.brokers", kafka::getBootstrapServers);
    }

    @Autowired
    private ProducerTemplate producerTemplate;

    @Autowired
    private CamelContext camelContext;

    @Test
    void testKafkaRoute() throws Exception {
        MockEndpoint mock = camelContext.getEndpoint("mock:result", MockEndpoint.class);
        mock.expectedMessageCount(1);
        mock.expectedBodiesReceived("test message");

        producerTemplate.sendBody("direct:to-kafka", "test message");

        // Wait for async processing
        mock.assertIsSatisfied(5000);
    }
}
```

### Testing with Embedded Database

```java
@CamelSpringBootTest
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
class DatabaseRouteTest {

    @Autowired
    private ProducerTemplate producerTemplate;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void testDatabaseInsert() {
        Order order = new Order("123", 100.0);
        producerTemplate.sendBody("direct:save-order", order);

        Integer count = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM orders WHERE id = ?",
            Integer.class,
            "123"
        );

        assertEquals(1, count);
    }
}
```

### Testing HTTP Endpoints with WireMock

```java
@CamelSpringBootTest
@SpringBootTest
@WireMockTest(httpPort = 8089)
class HttpClientTest {

    @Autowired
    private ProducerTemplate producerTemplate;

    @Test
    void testHttpCall() {
        stubFor(get(urlEqualTo("/api/users/123"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("{\"id\":\"123\",\"name\":\"John\"}")));

        String result = producerTemplate.requestBody(
            "direct:get-user",
            "123",
            String.class
        );

        assertNotNull(result);
        assertTrue(result.contains("John"));

        verify(getRequestedFor(urlEqualTo("/api/users/123")));
    }
}
```

## Testing Best Practices

### 1. Use NotifyBuilder for Async Routes

```java
@Test
void testAsyncRoute() {
    NotifyBuilder notify = new NotifyBuilder(context)
        .from("seda:async")
        .whenDone(1)
        .create();

    template.sendBody("seda:async", "test");

    assertTrue(notify.matches(5, TimeUnit.SECONDS));
}
```

### 2. Test Route Timing and Performance

```java
@Test
void testRoutePerformance() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(100);
    mock.setResultWaitTime(5000);

    StopWatch watch = new StopWatch();
    for (int i = 0; i < 100; i++) {
        template.sendBody("direct:process", "message " + i);
    }

    mock.assertIsSatisfied();
    long elapsed = watch.taken();
    assertTrue(elapsed < 5000, "Route took too long: " + elapsed + "ms");
}
```

### 3. Test with Different Property Configurations

```java
@CamelSpringBootTest
@SpringBootTest(properties = {
    "camel.route.max-retries=5",
    "camel.route.retry-delay=1000"
})
class ConfigurationTest {

    @Test
    void testWithCustomConfig() {
        // Test route behavior with specific configuration
    }
}
```

### 4. Use Test Profiles

```java
@CamelSpringBootTest
@SpringBootTest
@ActiveProfiles("test")
class ProfileSpecificTest {
    // Uses application-test.yml configuration
}
```

### 5. Clean Up Resources

```java
@AfterEach
void cleanup() {
    // Reset mock endpoints
    resetMocks();

    // Clear queues
    if (jdbcTemplate != null) {
        jdbcTemplate.execute("DELETE FROM test_table");
    }
}
```

### 6. Organize Tests by Concern

```java
@Nested
@DisplayName("Order Validation Tests")
class OrderValidationTests {
    @Test void testValidOrder() { }
    @Test void testInvalidOrder() { }
}

@Nested
@DisplayName("Order Processing Tests")
class OrderProcessingTests {
    @Test void testProcessing() { }
    @Test void testErrorHandling() { }
}
```

### 7. Use AdviceWith for Route Modification

Modify routes during testing without changing production code.

```java
@Test
void testWithAdvice() throws Exception {
    AdviceWith.adviceWith(context, "myRoute", advice -> {
        advice.replaceFromWith("direct:start");
        advice.weaveAddLast().to("mock:result");
        advice.mockEndpoints("http:*");
    });

    context.start();

    getMockEndpoint("mock:result").expectedMessageCount(1);
    template.sendBody("direct:start", "test");

    assertMockEndpointsSatisfied();
}
```

### 8. Test Route Startup and Shutdown

```java
@Test
void testRouteLifecycle() throws Exception {
    ServiceStatus status = context.getRouteController().getRouteStatus("myRoute");
    assertEquals(ServiceStatus.Started, status);

    context.getRouteController().stopRoute("myRoute");
    status = context.getRouteController().getRouteStatus("myRoute");
    assertEquals(ServiceStatus.Stopped, status);

    context.getRouteController().startRoute("myRoute");
    status = context.getRouteController().getRouteStatus("myRoute");
    assertEquals(ServiceStatus.Started, status);
}
```

## Test Coverage Goals

1. **Route Logic**: Test all routing decisions and transformations
2. **Error Paths**: Verify exception handling and error recovery
3. **Edge Cases**: Test boundary conditions and invalid inputs
4. **Performance**: Ensure routes meet throughput requirements
5. **Integration Points**: Test interactions with external systems
6. **Configuration**: Verify different configuration scenarios

## Common Testing Patterns

### Pattern: Given-When-Then

```java
@Test
void shouldRouteHighPriorityOrders() {
    // Given
    Order highPriorityOrder = new Order("123", 1000.0, "HIGH");
    MockEndpoint highPriorityQueue = getMockEndpoint("mock:high-priority");
    highPriorityQueue.expectedMessageCount(1);

    // When
    template.sendBody("direct:orders", highPriorityOrder);

    // Then
    highPriorityQueue.assertIsSatisfied();
}
```

### Pattern: Test Data Builders

```java
class OrderBuilder {
    private String id = "default-id";
    private double amount = 100.0;
    private String priority = "NORMAL";

    OrderBuilder withId(String id) {
        this.id = id;
        return this;
    }

    OrderBuilder withAmount(double amount) {
        this.amount = amount;
        return this;
    }

    OrderBuilder withHighPriority() {
        this.priority = "HIGH";
        return this;
    }

    Order build() {
        return new Order(id, amount, priority);
    }
}

@Test
void testWithBuilder() {
    Order order = new OrderBuilder()
        .withId("123")
        .withAmount(5000.0)
        .withHighPriority()
        .build();

    template.sendBody("direct:orders", order);
}
```

## References

- [Camel Test Documentation](https://camel.apache.org/manual/testing.html)
- [Spring Boot Testing](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing)
- [Testcontainers](https://www.testcontainers.org/)
- [WireMock](http://wiremock.org/)
