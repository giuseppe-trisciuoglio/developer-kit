# Testing Lambda Reference

Complete guide for testing AWS Lambda Java functions including unit tests, integration tests, and performance testing.

## Table of Contents

1. [Unit Testing](#unit-testing)
2. [Integration Testing](#integration-testing)
3. [Performance Testing](#performance-testing)
4. [Test Automation](#test-automation)

---

## Unit Testing

### JUnit 5 Setup

```groovy
// build.gradle
dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
    testImplementation 'org.mockito:mockito-core:5.7.0'
    testImplementation 'org.mockito:mockito-junit-jupiter:5.7.0'
    testImplementation 'org.assertj:assertj-core:3.24.2'
}

test {
    useJUnitPlatform()
    testLogging {
        events "passed", "skipped", "failed"
    }
}
```

### Handler Unit Test

```java
package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.example.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class HandlerTest {

    @Mock
    private UserService userService;

    @Mock
    private Context context;

    @InjectMocks
    private Handler handler;

    private final ObjectMapper mapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        when(context.getLogger()).thenReturn(System.out::println);
    }

    @Test
    void shouldReturnUser_whenGetRequest() throws Exception {
        // Given
        String userId = "123";
        User mockUser = new User(userId, "John Doe", "john@example.com");

        when(userService.findById(userId)).thenReturn(mockUser);

        APIGatewayProxyRequestEvent request = new APIGatewayProxyRequestEvent()
            .withHttpMethod("GET")
            .withPath("/users/" + userId)
            .withPathParameters(Map.of("id", userId));

        // When
        APIGatewayProxyResponseEvent response = handler.handleRequest(request, context);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(200);
        assertThat(response.getBody()).contains("John Doe");
        verify(userService).findById(userId);
    }

    @Test
    void shouldCreateUser_whenPostRequest() throws Exception {
        // Given
        User newUser = new User(null, "Jane Doe", "jane@example.com");
        User createdUser = new User("456", "Jane Doe", "jane@example.com");

        when(userService.create(any(User.class))).thenReturn(createdUser);

        APIGatewayProxyRequestEvent request = new APIGatewayProxyRequestEvent()
            .withHttpMethod("POST")
            .withPath("/users")
            .withBody(mapper.writeValueAsString(newUser));

        // When
        APIGatewayProxyResponseEvent response = handler.handleRequest(request, context);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(201);
        assertThat(response.getBody()).contains("456");
    }

    @Test
    void shouldReturn404_whenUserNotFound() {
        // Given
        String userId = "999";
        when(userService.findById(userId)).thenReturn(null);

        APIGatewayProxyRequestEvent request = new APIGatewayProxyRequestEvent()
            .withHttpMethod("GET")
            .withPath("/users/" + userId)
            .withPathParameters(Map.of("id", userId));

        // When
        APIGatewayProxyResponseEvent response = handler.handleRequest(request, context);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(404);
        assertThat(response.getBody()).contains("User not found");
    }

    @Test
    void shouldReturn405_forUnsupportedMethod() {
        // Given
        APIGatewayProxyRequestEvent request = new APIGatewayProxyRequestEvent()
            .withHttpMethod("PATCH")
            .withPath("/users/123");

        // When
        APIGatewayProxyResponseEvent response = handler.handleRequest(request, context);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(405);
    }
}
```

### Service Layer Testing

```java
package com.example.service;

import com.example.model.User;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class DynamoDbUserServiceTest {

    @Mock
    private DynamoDbClient dynamoDbClient;

    private DynamoDbUserService userService;

    @BeforeEach
    void setUp() {
        userService = new DynamoDbUserService(dynamoDbClient, "test-table");
    }

    @Test
    void shouldReturnUser_whenFound() {
        // Given
        String userId = "123";
        Map<String, AttributeValue> item = Map.of(
            "id", AttributeValue.builder().s(userId).build(),
            "name", AttributeValue.builder().s("John Doe").build(),
            "email", AttributeValue.builder().s("john@example.com").build()
        );

        when(dynamoDbClient.getItem(any(GetItemRequest.class)))
            .thenReturn(GetItemResponse.builder().item(item).build());

        // When
        User user = userService.findById(userId);

        // Then
        assertThat(user).isNotNull();
        assertThat(user.getId()).isEqualTo(userId);
        assertThat(user.getName()).isEqualTo("John Doe");
    }

    @Test
    void shouldReturnNull_whenNotFound() {
        // Given
        when(dynamoDbClient.getItem(any(GetItemRequest.class)))
            .thenReturn(GetItemResponse.builder().build());

        // When
        User user = userService.findById("999");

        // Then
        assertThat(user).isNull();
    }

    @Test
    void shouldThrowException_whenDynamoDbFails() {
        // Given
        when(dynamoDbClient.getItem(any(GetItemRequest.class)))
            .thenThrow(DynamoDbException.builder().message("Connection failed").build());

        // Then
        assertThatThrownBy(() -> userService.findById("123"))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Connection failed");
    }
}
```

### Micronaut Handler Testing

```java
package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

@MicronautTest
class MicronautHandlerTest {

    @Inject
    private Handler handler;

    @Test
    void testHandler() {
        APIGatewayProxyRequestEvent request = new APIGatewayProxyRequestEvent()
            .withHttpMethod("GET")
            .withPath("/test");

        APIGatewayProxyResponseEvent response = handler.execute(request);

        assertNotNull(response);
        assertEquals(200, response.getStatusCode());
    }
}
```

### Parameterized Tests

```java
package com.example;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.assertj.core.api.Assertions.assertThat;

class ValidationTest {

    @ParameterizedTest
    @ValueSource(strings = {"user@example.com", "test@test.org", "admin@company.co.uk"})
    void shouldAcceptValidEmails(String email) {
        assertThat(EmailValidator.isValid(email)).isTrue();
    }

    @ParameterizedTest
    @ValueSource(strings = {"invalid", "@example.com", "user@", ""})
    void shouldRejectInvalidEmails(String email) {
        assertThat(EmailValidator.isValid(email)).isFalse();
    }

    @ParameterizedTest
    @CsvSource({
        "GET, /users, 200",
        "POST, /users, 201",
        "DELETE, /users/123, 204",
        "PATCH, /users/123, 405"
    })
    void shouldReturnExpectedStatus(String method, String path, int expectedStatus) {
        // Test implementation
    }
}
```

---

## Integration Testing

### SAM Local Testing

```bash
# Install SAM CLI
brew install aws-sam-cli

# Build the application
sam build

# Invoke function locally
sam local invoke ApiFunction -e events/api-request.json

# Start local API Gateway
sam local start-api --warm-containers EAGER
```

### SAM Event Files

```json
// events/get-user.json
{
  "httpMethod": "GET",
  "path": "/users/123",
  "pathParameters": {
    "id": "123"
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "requestContext": {
    "requestId": "test-request-id",
    "stage": "local"
  }
}
```

```json
// events/post-user.json
{
  "httpMethod": "POST",
  "path": "/users",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"name\": \"John Doe\", \"email\": \"john@example.com\"}"
}
```

### TestContainers Integration

```java
package com.example;

import com.example.service.DynamoDbUserService;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.net.URI;

import static org.assertj.core.api.Assertions.assertThat;
import static org.testcontainers.containers.localstack.LocalStackContainer.Service.DYNAMODB;

@Testcontainers
class DynamoDbIntegrationTest {

    @Container
    static LocalStackContainer localStack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(DYNAMODB);

    private static DynamoDbClient dynamoDbClient;
    private static DynamoDbUserService userService;

    @BeforeAll
    static void setUp() {
        dynamoDbClient = DynamoDbClient.builder()
            .endpointOverride(localStack.getEndpointOverride(DYNAMODB))
            .region(Region.of(localStack.getRegion()))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create("test", "test")))
            .build();

        // Create table
        createUsersTable();

        userService = new DynamoDbUserService(dynamoDbClient, "users");
    }

    private static void createUsersTable() {
        dynamoDbClient.createTable(builder -> builder
            .tableName("users")
            .attributeDefinitions(def -> def
                .attributeName("id")
                .attributeType(ScalarAttributeType.S))
            .keySchema(key -> key
                .attributeName("id")
                .keyType(KeyType.HASH))
            .billingMode(BillingMode.PAY_PER_REQUEST));
    }

    @AfterAll
    static void tearDown() {
        if (dynamoDbClient != null) {
            dynamoDbClient.close();
        }
    }

    @Test
    void shouldCreateAndRetrieveUser() {
        // Given
        User user = new User("123", "John Doe", "john@example.com");

        // When
        User created = userService.create(user);
        User retrieved = userService.findById("123");

        // Then
        assertThat(created).isNotNull();
        assertThat(retrieved).isNotNull();
        assertThat(retrieved.getName()).isEqualTo("John Doe");
    }
}
```

### Docker Compose for Local Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:3.0
    ports:
      - "4566:4566"
    environment:
      - SERVICES=dynamodb,s3,lambda
      - DEFAULT_REGION=us-east-1
      - DEBUG=1
    volumes:
      - ./init-scripts:/etc/localstack/init/ready.d

  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      - localstack
    environment:
      - AWS_ENDPOINT=http://localstack:4566
      - AWS_REGION=us-east-1
```

```dockerfile
# Dockerfile.test
FROM eclipse-temurin:21-jdk-alpine

WORKDIR /app
COPY . .
RUN ./gradlew testClasses --no-daemon

CMD ["./gradlew", "integrationTest", "--no-daemon"]
```

---

## Performance Testing

### Cold Start Measurement

```java
package com.example.performance;

import org.junit.jupiter.api.Test;
import software.amazon.awssdk.services.lambda.LambdaClient;
import software.amazon.awssdk.services.lambda.model.*;

import java.time.Instant;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;

class ColdStartTest {

    private final LambdaClient lambda = LambdaClient.create();

    @Test
    void measureColdStart() throws InterruptedException {
        String functionName = "my-java-lambda";

        // Force cold start by updating function configuration
        lambda.updateFunctionConfiguration(UpdateFunctionConfigurationRequest.builder()
            .functionName(functionName)
            .description("Cold start test at " + Instant.now())
            .build());

        // Wait for update
        waitForFunctionUpdate(functionName);

        // Invoke and measure
        long startTime = System.currentTimeMillis();

        InvokeResponse response = lambda.invoke(InvokeRequest.builder()
            .functionName(functionName)
            .payload("{\"test\": true}")
            .build());

        long duration = System.currentTimeMillis() - startTime;

        // Parse response for init duration
        String payload = response.payload().asUtf8String();
        System.out.println("Total duration: " + duration + "ms");
        System.out.println("Response: " + payload);

        // Cold start should be under 500ms for Raw Java
        assertThat(duration).isLessThan(1000);
    }

    private void waitForFunctionUpdate(String functionName) throws InterruptedException {
        while (true) {
            GetFunctionResponse response = lambda.getFunction(GetFunctionRequest.builder()
                .functionName(functionName)
                .build());

            if (response.configuration().lastUpdateStatus() == LastUpdateStatus.SUCCESSFUL) {
                break;
            }

            TimeUnit.SECONDS.sleep(1);
        }
    }
}
```

### Load Testing with JMH

```java
package com.example.benchmark;

import com.example.Handler;
import com.example.service.UserService;
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.runner.Runner;
import org.openjdk.jmh.runner.options.Options;
import org.openjdk.jmh.runner.options.OptionsBuilder;

import java.util.concurrent.TimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@State(Scope.Thread)
@Fork(2)
@Warmup(iterations = 3)
@Measurement(iterations = 5)
public class HandlerBenchmark {

    private Handler handler;
    private APIGatewayProxyRequestEvent request;

    @Setup
    public void setup() {
        handler = new Handler();
        request = new APIGatewayProxyRequestEvent()
            .withHttpMethod("GET")
            .withPath("/users/123")
            .withPathParameters(Map.of("id", "123"));
    }

    @Benchmark
    public APIGatewayProxyResponseEvent testHandleRequest() {
        return handler.handleRequest(request, new TestContext());
    }

    public static void main(String[] args) throws Exception {
        Options opt = new OptionsBuilder()
            .include(HandlerBenchmark.class.getSimpleName())
            .build();
        new Runner(opt).run();
    }
}
```

### AWS Lambda Power Tuning

```python
# power-tuning.py - using AWS Lambda Power Tuning tool
import boto3
import json

def run_power_tuning():
    lambda_client = boto3.client('lambda')
    stepfunctions = boto3.client('stepfunctions')

    # Power tuning configuration
    payload = {
        "lambdaARN": "arn:aws:lambda:us-east-1:123456789:function:my-java-lambda",
        "powerValues": [128, 256, 512, 1024, 2048],
        "num": 50,
        "payload": "{}",
        "parallelInvocation": True,
        "strategy": "speed"
    }

    # Start power tuning state machine
    response = stepfunctions.start_execution(
        stateMachineArn="arn:aws:states:us-east-1:123456789:stateMachine:powerTuningStateMachine",
        input=json.dumps(payload)
    )

    print(f"Power tuning started: {response['executionArn']}")
```

### CloudWatch Metrics Collection

```java
package com.example.performance;

import software.amazon.awssdk.services.cloudwatch.CloudWatchClient;
import software.amazon.awssdk.services.cloudwatch.model.*;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

public class MetricsCollector {

    private final CloudWatchClient cloudWatch = CloudWatchClient.create();

    public void analyzePerformance(String functionName, int hours) {
        Instant endTime = Instant.now();
        Instant startTime = endTime.minus(hours, ChronoUnit.HOURS);

        // Get duration metrics
        GetMetricStatisticsRequest durationRequest = GetMetricStatisticsRequest.builder()
            .namespace("AWS/Lambda")
            .metricName("Duration")
            .dimensions(
                Dimension.builder().name("FunctionName").value(functionName).build())
            .startTime(startTime)
            .endTime(endTime)
            .period(300)
            .statistics(Statistic.AVERAGE, Statistic.MAXIMUM, Statistic.P99)
            .build();

        GetMetricStatisticsResponse durationResponse = cloudWatch.getMetricStatistics(durationRequest);

        System.out.println("Duration Statistics:");
        for (Datapoint dp : durationResponse.datapoints()) {
            System.out.printf("  Average: %.2fms, Max: %.2fms, P99: %.2fms%n",
                dp.average(), dp.maximum(), dp.extendedStatistics().get("p99"));
        }

        // Get error metrics
        GetMetricStatisticsRequest errorRequest = GetMetricStatisticsRequest.builder()
            .namespace("AWS/Lambda")
            .metricName("Errors")
            .dimensions(
                Dimension.builder().name("FunctionName").value(functionName).build())
            .startTime(startTime)
            .endTime(endTime)
            .period(3600)
            .statistics(Statistic.SUM)
            .build();

        GetMetricStatisticsResponse errorResponse = cloudWatch.getMetricStatistics(errorRequest);

        long totalErrors = errorResponse.datapoints().stream()
            .mapToLong(dp -> dp.sum().longValue())
            .sum();

        System.out.println("Total Errors: " + totalErrors);
    }
}
```

---

## Test Automation

### Gradle Test Configuration

```groovy
// build.gradle
test {
    useJUnitPlatform()
    testLogging {
        events "passed", "skipped", "failed", "standardOut", "standardError"
        showExceptions true
        showCauses true
        showStackTraces true
    }
    reports {
        html.required = true
        junitXml.required = true
    }
}

// Integration test source set
sourceSets {
    integrationTest {
        java {
            srcDir 'src/integration-test/java'
        }
        resources {
            srcDir 'src/integration-test/resources'
        }
        compileClasspath += sourceSets.main.output + sourceSets.test.output
        runtimeClasspath += sourceSets.main.output + sourceSets.test.output
    }
}

tasks.register('integrationTest', Test) {
    description = 'Runs integration tests'
    group = 'verification'
    testClassesDirs = sourceSets.integrationTest.output.classesDirs
    classpath = sourceSets.integrationTest.runtimeClasspath
    shouldRunAfter test
}

configurations {
    integrationTestImplementation.extendsFrom testImplementation
    integrationTestRuntimeOnly.extendsFrom testRuntimeOnly
}

// Code coverage
plugins {
    id 'jacoco'
}

jacoco {
    toolVersion = "0.8.11"
}

jacocoTestReport {
    dependsOn test
    reports {
        xml.required = true
        html.required = true
    }
}
```

### Test Reporting

```groovy
// Generate aggregate test report
tasks.register('testReport', TestReport) {
    destinationDirectory = layout.buildDirectory.dir('reports/allTests')
    testResults.from(
        test,
        integrationTest
    )
}
```

### CI/CD Test Integration

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle

      - name: Run unit tests
        run: ./gradlew test

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: build/reports/tests/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: build/reports/jacoco/test/jacocoTestReport.xml

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: gradle

      - name: Start LocalStack
        run: |
          docker run -d \
            -p 4566:4566 \
            -e SERVICES=dynamodb,s3 \
            localstack/localstack:3.0

      - name: Wait for LocalStack
        run: |
          sleep 10
          curl -s http://localhost:4566/_localstack/health

      - name: Run integration tests
        run: ./gradlew integrationTest
        env:
          AWS_ENDPOINT: http://localhost:4566
          AWS_REGION: us-east-1

      - name: Upload integration test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: integration-test-results
          path: build/reports/tests/integrationTest/
```

### Blue-Green Deployment Testing

```java
package com.example.deployment;

import org.junit.jupiter.api.Test;
import software.amazon.awssdk.services.lambda.LambdaClient;
import software.amazon.awssdk.services.lambda.model.*;

import static org.assertj.core.api.Assertions.assertThat;

class BlueGreenDeploymentTest {

    private final LambdaClient lambda = LambdaClient.create();

    @Test
    void canaryDeploymentShouldSucceed() {
        String functionName = "my-java-lambda";
        String aliasName = "live";

        // Publish new version
        PublishVersionResponse versionResponse = lambda.publishVersion(
            PublishVersionRequest.builder()
                .functionName(functionName)
                .description("Canary test version")
                .build());

        String newVersion = versionResponse.version();

        // Update alias to point 10% to new version
        lambda.updateAlias(UpdateAliasRequest.builder()
            .functionName(functionName)
            .name(aliasName)
            .functionVersion(newVersion)
            .routingConfig(AliasRoutingConfiguration.builder()
                .additionalVersionWeights(Map.of("1", 0.9))  // 90% old, 10% new
                .build())
            .build());

        // Run smoke tests
        boolean smokeTestPassed = runSmokeTests(functionName, aliasName);
        assertThat(smokeTestPassed).isTrue();

        // Shift traffic to 100% new version
        lambda.updateAlias(UpdateAliasRequest.builder()
            .functionName(functionName)
            .name(aliasName)
            .functionVersion(newVersion)
            .build());
    }

    private boolean runSmokeTests(String functionName, String aliasName) {
        // Invoke function multiple times and check responses
        for (int i = 0; i < 10; i++) {
            InvokeResponse response = lambda.invoke(InvokeRequest.builder()
                .functionName(functionName + ":" + aliasName)
                .payload("{\"test\": true}")
                .build());

            if (response.statusCode() != 200) {
                return false;
            }
        }
        return true;
    }
}
```

---

## Best Practices

### Test Organization

```
src/
├── main/java/com/example/
│   ├── Handler.java
│   └── service/
├── test/java/com/example/
│   ├── HandlerTest.java           # Unit tests
│   ├── service/
│   │   └── UserServiceTest.java
│   └── util/
│       └── JsonUtilTest.java
└── integration-test/java/com/example/
    ├── HandlerIntegrationTest.java
    └── service/
        └── DynamoDbServiceIT.java
```

### Test Data Builders

```java
package com.example.test;

import com.example.model.User;

public class UserBuilder {
    private String id = "123";
    private String name = "John Doe";
    private String email = "john@example.com";

    public static UserBuilder aUser() {
        return new UserBuilder();
    }

    public UserBuilder withId(String id) {
        this.id = id;
        return this;
    }

    public UserBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public UserBuilder withEmail(String email) {
        this.email = email;
        return this;
    }

    public User build() {
        return new User(id, name, email);
    }
}

// Usage in tests
User user = UserBuilder.aUser()
    .withId("456")
    .withName("Jane Doe")
    .build();
```

### Test Context Mock

```java
package com.example.test;

import com.amazonaws.services.lambda.runtime.ClientContext;
import com.amazonaws.services.lambda.runtime.CognitoIdentity;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;

public class TestContext implements Context {

    @Override
    public String getAwsRequestId() {
        return "test-request-id";
    }

    @Override
    public String getLogGroupName() {
        return "/aws/lambda/test-function";
    }

    @Override
    public String getLogStreamName() {
        return "2024/01/01/test-stream";
    }

    @Override
    public String getFunctionName() {
        return "test-function";
    }

    @Override
    public String getFunctionVersion() {
        return "$LATEST";
    }

    @Override
    public String getInvokedFunctionArn() {
        return "arn:aws:lambda:us-east-1:123456789:function:test-function";
    }

    @Override
    public CognitoIdentity getIdentity() {
        return null;
    }

    @Override
    public ClientContext getClientContext() {
        return null;
    }

    @Override
    public int getRemainingTimeInMillis() {
        return 30000;
    }

    @Override
    public int getMemoryLimitInMB() {
        return 512;
    }

    @Override
    public LambdaLogger getLogger() {
        return System.out::println;
    }
}
```
