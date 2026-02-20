# Micronaut Lambda Reference

Complete guide for creating AWS Lambda functions with Micronaut Framework.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Handler Implementation](#handler-implementation)
3. [Cold Start Optimization](#cold-start-optimization)
4. [Dependency Injection](#dependency-injection)
5. [Deployment Configuration](#deployment-configuration)

---

## Project Setup

### Gradle Configuration

```groovy
plugins {
    id("com.github.johnrengelman.shadow") version "8.1.1"
    id("io.micronaut.application") version "4.7.6"
}

version = "1.0.0"
group = "com.example"

repositories {
    mavenCentral()
}

dependencies {
    // Micronaut Lambda
    implementation("io.micronaut.aws:micronaut-function-aws-api-proxy")
    implementation("io.micronaut.aws:micronaut-function-aws-custom-runtime")

    // AWS Lambda Events
    implementation("com.amazonaws:aws-lambda-java-events:3.11.4")
    implementation("com.amazonaws:aws-lambda-java-core:1.2.3")

    // AWS SDK (if needed)
    implementation("software.amazon.awssdk:dynamodb")
    implementation("software.amazon.awssdk:s3")

    // Testing
    testImplementation("io.micronaut.test:micronaut-test-junit5")
    testImplementation("org.junit.jupiter:junit-jupiter")
    testImplementation("org.mockito:mockito-core")
}

application {
    mainClass.set("com.example.Application")
}

java {
    sourceCompatibility = JavaVersion.toVersion("21")
    targetCompatibility = JavaVersion.toVersion("21")
}

micronaut {
    runtime("lambda")
    testRuntime("junit5")
    processing {
        incremental(true)
        annotations("com.example.*")
    }
    aot {
        optimizeClassLoading(true)
        convertYamlToJava(true)
        precomputeOperations(true)
    }
}

tasks.named("shadowJar") {
    archiveClassifier.set("")
    mergeServiceFiles()
}
```

### Maven Configuration

```xml
<project>
    <parent>
        <groupId>io.micronaut</groupId>
        <artifactId>micronaut-parent</artifactId>
        <version>4.7.6</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>my-micronaut-lambda</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <micronaut.version>4.7.6</micronaut.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>io.micronaut.aws</groupId>
            <artifactId>micronaut-function-aws-api-proxy</artifactId>
        </dependency>
        <dependency>
            <groupId>com.amazonaws</groupId>
            <artifactId>aws-lambda-java-events</artifactId>
            <version>3.11.4</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>io.micronaut.maven</groupId>
                <artifactId>micronaut-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### Project Structure

```
src/
├── main/
│   ├── java/
│   │   └── com/example/
│   │       ├── Application.java
│   │       ├── Handler.java
│   │       ├── service/
│   │       │   ├── UserService.java
│   │       │   └── DynamoDbUserService.java
│   │       └── repository/
│   │           └── UserRepository.java
│   └── resources/
│       ├── application.yml
│       └── logback.xml
└── test/
    └── java/
        └── com/example/
            └── HandlerTest.java
```

---

## Handler Implementation

### Basic API Gateway Handler

```java
package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import io.micronaut.function.aws.MicronautRequestHandler;
import jakarta.inject.Inject;

public class Handler extends MicronautRequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    @Inject
    private UserService userService;

    @Override
    public APIGatewayProxyResponseEvent execute(APIGatewayProxyRequestEvent request) {
        String httpMethod = request.getHttpMethod();
        String path = request.getPath();

        return switch (httpMethod) {
            case "GET" -> handleGet(request);
            case "POST" -> handlePost(request);
            case "PUT" -> handlePut(request);
            case "DELETE" -> handleDelete(request);
            default -> methodNotAllowed();
        };
    }

    private APIGatewayProxyResponseEvent handleGet(APIGatewayProxyRequestEvent request) {
        String userId = request.getPathParameters().get("id");
        User user = userService.findById(userId);

        return new APIGatewayProxyResponseEvent()
            .withStatusCode(200)
            .withBody(JsonUtils.toJson(user))
            .withHeaders(Map.of("Content-Type", "application/json"));
    }

    private APIGatewayProxyResponseEvent handlePost(APIGatewayProxyRequestEvent request) {
        User user = JsonUtils.fromJson(request.getBody(), User.class);
        User created = userService.create(user);

        return new APIGatewayProxyResponseEvent()
            .withStatusCode(201)
            .withBody(JsonUtils.toJson(created))
            .withHeaders(Map.of("Content-Type", "application/json"));
    }

    private APIGatewayProxyResponseEvent methodNotAllowed() {
        return new APIGatewayProxyResponseEvent()
            .withStatusCode(405)
            .withBody("{\"error\": \"Method not allowed\"}");
    }
}
```

### Stream Handler (Binary Support)

```java
package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import io.micronaut.function.aws.runtime.MicronautLambdaRuntime;
import io.micronaut.core.annotation.Nullable;

import java.io.InputStream;
import java.io.OutputStream;

public class StreamHandler implements RequestStreamHandler {

    private static final MicronautLambdaRuntime runtime = new MicronautLambdaRuntime();

    @Override
    public void handleRequest(InputStream input, OutputStream output, Context context) {
        runtime.handleRequest(input, output, context);
    }
}
```

### Function Bean Approach

```java
package com.example;

import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import io.micronaut.function.FunctionBean;
import jakarta.inject.Inject;

import java.util.function.Function;

@FunctionBean("user-api")
public class UserApiFunction implements Function<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    @Inject
    private UserService userService;

    @Override
    public APIGatewayProxyResponseEvent apply(APIGatewayProxyRequestEvent request) {
        // Implementation
        return new APIGatewayProxyResponseEvent()
            .withStatusCode(200)
            .withBody("{}");
    }
}
```

---

## Cold Start Optimization

### AOT Compilation Configuration

```yaml
# application.yml
micronaut:
  application:
    name: my-lambda-function

  # Disable features not needed in Lambda
  server:
    enabled: false

  # Optimize bean introspection
  introspection:
    enabled: true
    annotations:
      - com.example.*

# Disable unnecessary logging overhead
logger:
  levels:
    io.micronaut.context: WARN
    io.micronaut.core: WARN
```

### Lazy Initialization Pattern

```java
package com.example;

import io.micronaut.context.annotation.Bean;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Lazy;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

@Factory
public class AwsClientFactory {

    @Bean
    @Lazy
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
            .region(Region.of(System.getenv("AWS_REGION")))
            .build();
    }

    @Bean
    @Lazy
    public S3Client s3Client() {
        return S3Client.builder()
            .region(Region.of(System.getenv("AWS_REGION")))
            .build();
    }
}
```

### Singleton Services

```java
package com.example.service;

import io.micronaut.context.annotation.Singleton;
import jakarta.annotation.PostConstruct;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

@Singleton
public class DynamoDbUserService implements UserService {

    private final DynamoDbClient dynamoDb;
    private String tableName;

    public DynamoDbUserService(DynamoDbClient dynamoDb) {
        this.dynamoDb = dynamoDb;
    }

    @PostConstruct
    public void init() {
        // Initialization that runs once on first use
        this.tableName = System.getenv("USERS_TABLE");
        if (tableName == null) {
            throw new IllegalStateException("USERS_TABLE environment variable required");
        }
    }

    // Service methods...
}
```

---

## Dependency Injection

### Service Interfaces and Implementations

```java
// UserService.java
public interface UserService {
    User findById(String id);
    User create(User user);
    void delete(String id);
}

// DynamoDbUserService.java
@Singleton
public class DynamoDbUserService implements UserService {

    private final DynamoDbClient dynamoDb;
    private final ObjectMapper objectMapper;

    @Inject
    public DynamoDbUserService(DynamoDbClient dynamoDb, ObjectMapper objectMapper) {
        this.dynamoDb = dynamoDb;
        this.objectMapper = objectMapper;
    }

    // Implementation...
}
```

### Configuration Properties

```java
package com.example.config;

import io.micronaut.context.annotation.ConfigurationProperties;

@ConfigurationProperties("app")
public class ApplicationConfig {

    private String usersTable;
    private int defaultPageSize = 20;
    private boolean enableCache = true;

    // Getters and setters
    public String getUsersTable() { return usersTable; }
    public void setUsersTable(String usersTable) { this.usersTable = usersTable; }

    public int getDefaultPageSize() { return defaultPageSize; }
    public void setDefaultPageSize(int defaultPageSize) { this.defaultPageSize = defaultPageSize; }

    public boolean isEnableCache() { return enableCache; }
    public void setEnableCache(boolean enableCache) { this.enableCache = enableCache; }
}
```

```yaml
# application.yml
app:
  users-table: ${USERS_TABLE}
  default-page-size: 20
  enable-cache: true
```

### Conditional Beans

```java
@Singleton
@Requires(property = "app.enable-cache", value = "true")
public class CachingUserService implements UserService {
    // Implementation with caching
}

@Singleton
@Requires(property = "app.enable-cache", value = "false", defaultValue = "false")
public class SimpleUserService implements UserService {
    // Implementation without caching
}
```

---

## Deployment Configuration

### Serverless Framework

```yaml
service: micronaut-lambda-api

provider:
  name: aws
  runtime: java21
  memorySize: 512
  timeout: 10
  region: us-east-1
  environment:
    MICRONAUT_ENVIRONMENTS: lambda
    USERS_TABLE: !Ref UsersTable
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:DeleteItem
            - dynamodb:Scan
            - dynamodb:Query
          Resource: !GetAtt UsersTable.Arn

package:
  artifact: build/libs/my-micronaut-lambda-1.0.0-all.jar

functions:
  api:
    handler: com.example.Handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true

resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: users
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
```

### AWS SAM

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Micronaut Lambda API

Globals:
  Function:
    Timeout: 10
    MemorySize: 512
    Runtime: java21
    Environment:
      Variables:
        MICRONAUT_ENVIRONMENTS: lambda
        USERS_TABLE: !Ref UsersTable

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/my-micronaut-lambda-1.0.0-all.jar
      Handler: com.example.Handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: users
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

### Provisioned Concurrency

```yaml
# serverless.yml with provisioned concurrency
functions:
  api:
    handler: com.example.Handler
    provisionedConcurrency: 5
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

```yaml
# SAM with provisioned concurrency
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 5
      AutoPublishAlias: live
```

---

## Performance Tuning

### JVM Options

```yaml
# serverless.yml
provider:
  name: aws
  runtime: java21
  environment:
    JAVA_TOOL_OPTIONS: >
      -XX:+TieredCompilation
      -XX:TieredStopAtLevel=1
      -XX:+UseSerialGC
      -Xmx384m
```

### Build Optimization

```groovy
// build.gradle - minimize JAR size
shadowJar {
    minimize {
        exclude(dependency('io.micronaut.*'))
        exclude(dependency('com.amazonaws.*'))
    }
}
```

---

## Testing

See [testing-lambda.md](testing-lambda.md) for comprehensive testing patterns including Micronaut-specific test setup.
