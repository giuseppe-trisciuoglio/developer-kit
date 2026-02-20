# Raw Java Lambda Reference

Complete guide for creating minimal AWS Lambda functions in pure Java without frameworks.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Minimal Handler](#minimal-handler)
3. [Singleton Pattern](#singleton-pattern)
4. [JAR Packaging](#jar-packaging)
5. [Performance Tuning](#performance-tuning)

---

## Project Structure

### Gradle Configuration

```groovy
plugins {
    id 'java'
    id 'com.github.johnrengelman.shadow' version '8.1.1'
}

group = 'com.example'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

repositories {
    mavenCentral()
}

dependencies {
    // AWS Lambda Core
    implementation 'com.amazonaws:aws-lambda-java-core:1.2.3'
    implementation 'com.amazonaws:aws-lambda-java-events:3.11.4'
    implementation 'com.amazonaws:aws-lambda-java-log4j2:1.5.1'

    // JSON Processing (choose one)
    implementation 'com.fasterxml.jackson.core:jackson-databind:2.16.0'
    // Or use org.json for minimal size
    // implementation 'org.json:json:20231013'

    // AWS SDK (optional - include only what you need)
    implementation 'software.amazon.awssdk:dynamodb:2.21.0'

    // Testing
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
    testImplementation 'org.mockito:mockito-core:5.7.0'
}

test {
    useJUnitPlatform()
}

shadowJar {
    archiveClassifier = ''
    mergeServiceFiles()
}
```

### Maven Configuration

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>raw-java-lambda</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>com.amazonaws</groupId>
            <artifactId>aws-lambda-java-core</artifactId>
            <version>1.2.3</version>
        </dependency>
        <dependency>
            <groupId>com.amazonaws</groupId>
            <artifactId>aws-lambda-java-events</artifactId>
            <version>3.11.4</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.16.0</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.5.1</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <createDependencyReducedPom>false</createDependencyReducedPom>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

### Directory Structure

```
raw-java-lambda/
├── build.gradle (or pom.xml)
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/
│   │   │       ├── Handler.java
│   │   │       ├── service/
│   │   │       │   ├── UserService.java
│   │   │       │   └── UserServiceImpl.java
│   │   │       ├── model/
│   │   │       │   └── User.java
│   │   │       └── util/
│   │   │           └── JsonUtil.java
│   │   └── resources/
│   │       └── log4j2.xml
│   └── test/
│       └── java/
│           └── com/example/
│               └── HandlerTest.java
└── serverless.yml (or template.yaml)
```

---

## Minimal Handler

### Basic Request Handler

```java
package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.example.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Map;

public class Handler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Static initialization for reuse across invocations
    private static final ObjectMapper mapper = new ObjectMapper();
    private static final UserService userService = new UserServiceImpl();

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        try {
            context.getLogger().log("Processing request: " + request.getHttpMethod() + " " + request.getPath());

            String method = request.getHttpMethod();
            String path = request.getPath();

            return switch (method) {
                case "GET" -> handleGet(request, context);
                case "POST" -> handlePost(request, context);
                case "PUT" -> handlePut(request, context);
                case "DELETE" -> handleDelete(request, context);
                default -> createResponse(405, "{\"error\": \"Method not allowed\"}");
            };

        } catch (Exception e) {
            context.getLogger().log("Error: " + e.getMessage());
            return createResponse(500, "{\"error\": \"Internal server error\"}");
        }
    }

    private APIGatewayProxyResponseEvent handleGet(APIGatewayProxyRequestEvent request, Context context) {
        String userId = request.getPathParameters().get("id");
        User user = userService.findById(userId);

        if (user == null) {
            return createResponse(404, "{\"error\": \"User not found\"}");
        }

        try {
            String body = mapper.writeValueAsString(user);
            return createResponse(200, body);
        } catch (Exception e) {
            return createResponse(500, "{\"error\": \"Serialization error\"}");
        }
    }

    private APIGatewayProxyResponseEvent handlePost(APIGatewayProxyRequestEvent request, Context context) {
        try {
            User user = mapper.readValue(request.getBody(), User.class);
            User created = userService.create(user);
            String body = mapper.writeValueAsString(created);
            return createResponse(201, body);
        } catch (Exception e) {
            return createResponse(400, "{\"error\": \"Invalid request body\"}");
        }
    }

    private APIGatewayProxyResponseEvent handlePut(APIGatewayProxyRequestEvent request, Context context) {
        // Implementation
        return createResponse(200, "{\"message\": \"Updated\"}");
    }

    private APIGatewayProxyResponseEvent handleDelete(APIGatewayProxyRequestEvent request, Context context) {
        String userId = request.getPathParameters().get("id");
        userService.delete(userId);
        return createResponse(204, "");
    }

    private APIGatewayProxyResponseEvent createResponse(int statusCode, String body) {
        return new APIGatewayProxyResponseEvent()
            .withStatusCode(statusCode)
            .withBody(body)
            .withHeaders(Map.of(
                "Content-Type", "application/json",
                "Access-Control-Allow-Origin", "*"
            ));
    }
}
```

### Stream Handler (Binary Data)

```java
package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.nio.charset.StandardCharsets;

public class StreamHandler implements RequestStreamHandler {

    private static final ObjectMapper mapper = new ObjectMapper();

    @Override
    public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
        try {
            // Parse input
            JsonNode root = mapper.readTree(inputStream);
            String action = root.path("action").asText();

            // Process based on action
            String result = switch (action) {
                case "process" -> processData(root);
                case "transform" -> transformData(root);
                default -> "{\"error\": \"Unknown action\"}";
            };

            // Write output
            outputStream.write(result.getBytes(StandardCharsets.UTF_8));

        } catch (Exception e) {
            String error = "{\"error\": \"" + e.getMessage() + "\"}";
            outputStream.write(error.getBytes(StandardCharsets.UTF_8));
        }
    }

    private String processData(JsonNode input) {
        // Processing logic
        return "{\"status\": \"processed\"}";
    }

    private String transformData(JsonNode input) {
        // Transformation logic
        return "{\"status\": \"transformed\"}";
    }
}
```

### S3 Event Handler

```java
package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.lambda.runtime.events.models.s3.S3EventNotification;

public class S3Handler implements RequestHandler<S3Event, String> {

    @Override
    public String handleRequest(S3Event event, Context context) {
        for (S3EventNotification.S3EventNotificationRecord record : event.getRecords()) {
            String bucket = record.getS3().getBucket().getName();
            String key = record.getS3().getObject().getKey();

            context.getLogger().log("Processing s3://" + bucket + "/" + key);

            // Process the S3 object
            processS3Object(bucket, key, context);
        }
        return "Processed " + event.getRecords().size() + " records";
    }

    private void processS3Object(String bucket, String key, Context context) {
        // Implementation
    }
}
```

---

## Singleton Pattern

### Application Context Cache

```java
package com.example;

import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.s3.S3Client;

/**
 * Application context singleton for caching initialized services.
 * Initialized once on first Lambda container creation, reused for warm invocations.
 */
public final class ApplicationContext {

    // Singleton instance
    private static volatile ApplicationContext instance;
    private static final Object lock = new Object();

    // Cached clients
    private final DynamoDbClient dynamoDbClient;
    private final S3Client s3Client;
    private final String usersTableName;

    private ApplicationContext() {
        // Initialize AWS clients
        this.dynamoDbClient = DynamoDbClient.create();
        this.s3Client = S3Client.create();

        // Load configuration from environment
        this.usersTableName = System.getenv("USERS_TABLE");
        if (usersTableName == null) {
            throw new IllegalStateException("USERS_TABLE environment variable required");
        }

        // Pre-warm connections if needed
        validateConnections();
    }

    public static ApplicationContext getInstance() {
        if (instance == null) {
            synchronized (lock) {
                if (instance == null) {
                    instance = new ApplicationContext();
                }
            }
        }
        return instance;
    }

    private void validateConnections() {
        // Optional: Verify connections work
        dynamoDbClient.listTables();
    }

    public DynamoDbClient getDynamoDbClient() {
        return dynamoDbClient;
    }

    public S3Client getS3Client() {
        return s3Client;
    }

    public String getUsersTableName() {
        return usersTableName;
    }
}
```

### Lazy Initialization Service

```java
package com.example.service;

import com.example.ApplicationContext;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;

public class DynamoDbUserService implements UserService {

    // Lazy-loaded via singleton
    private final DynamoDbClient dynamoDb;
    private final String tableName;

    public DynamoDbUserService() {
        ApplicationContext ctx = ApplicationContext.getInstance();
        this.dynamoDb = ctx.getDynamoDbClient();
        this.tableName = ctx.getUsersTableName();
    }

    @Override
    public User findById(String id) {
        GetItemRequest request = GetItemRequest.builder()
            .tableName(tableName)
            .key(Map.of("id", AttributeValue.builder().s(id).build()))
            .build();

        GetItemResponse response = dynamoDb.getItem(request);

        if (!response.hasItem()) {
            return null;
        }

        return mapToUser(response.item());
    }

    @Override
    public User create(User user) {
        PutItemRequest request = PutItemRequest.builder()
            .tableName(tableName)
            .item(mapFromUser(user))
            .conditionExpression("attribute_not_exists(id)")
            .build();

        dynamoDb.putItem(request);
        return user;
    }

    @Override
    public void delete(String id) {
        DeleteItemRequest request = DeleteItemRequest.builder()
            .tableName(tableName)
            .key(Map.of("id", AttributeValue.builder().s(id).build()))
            .build();

        dynamoDb.deleteItem(request);
    }

    private User mapToUser(Map<String, AttributeValue> item) {
        User user = new User();
        user.setId(item.get("id").s());
        user.setName(item.get("name").s());
        user.setEmail(item.get("email").s());
        return user;
    }

    private Map<String, AttributeValue> mapFromUser(User user) {
        Map<String, AttributeValue> item = new HashMap<>();
        item.put("id", AttributeValue.builder().s(user.getId()).build());
        item.put("name", AttributeValue.builder().s(user.getName()).build());
        item.put("email", AttributeValue.builder().s(user.getEmail()).build());
        return item;
    }
}
```

### Handler with Context

```java
package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.example.service.DynamoDbUserService;
import com.example.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;

public class Handler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Static initialization - runs once per container
    private static final ObjectMapper mapper = new ObjectMapper();
    private static final UserService userService = new DynamoDbUserService();

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        // Log initialization timing
        long startTime = System.currentTimeMillis();

        try {
            // Process request using cached services
            String userId = request.getPathParameters().get("id");
            User user = userService.findById(userId);

            long duration = System.currentTimeMillis() - startTime;
            context.getLogger().log("Request processed in " + duration + "ms");

            return new APIGatewayProxyResponseEvent()
                .withStatusCode(200)
                .withBody(mapper.writeValueAsString(user));

        } catch (Exception e) {
            context.getLogger().log("Error: " + e.getMessage());
            return new APIGatewayProxyResponseEvent()
                .withStatusCode(500)
                .withBody("{\"error\": \"Internal error\"}");
        }
    }
}
```

---

## JAR Packaging

### Minimal JAR Configuration

```groovy
// build.gradle
shadowJar {
    archiveClassifier = ''
    mergeServiceFiles()

    // Exclude unnecessary files to reduce size
    exclude 'META-INF/*.SF'
    exclude 'META-INF/*.DSA'
    exclude 'META-INF/*.RSA'
    exclude 'META-INF/LICENSE*'
    exclude 'META-INF/NOTICE*'
    exclude 'META-INF/DEPENDENCIES'

    // Minimize to remove unused dependencies
    minimize {
        // Keep these packages even if not directly referenced
        exclude(dependency('com.amazonaws:.*'))
        exclude(dependency('software.amazon.awssdk:.*'))
        exclude(dependency('org.apache.logging.log4j:.*'))
    }
}
```

### Custom Packaging Script

```groovy
// build.gradle - custom tasks
tasks.register('packageForLambda', Zip) {
    from(shadowJar.outputs)
    archiveFileName = "function.zip"
    destinationDirectory = layout.buildDirectory.dir('distributions')
}

tasks.register('deployLocal', Copy) {
    dependsOn shadowJar
    from shadowJar.outputs
    into layout.buildDirectory.dir('sam-local')
}
```

### Maven Shade Configuration

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-shade-plugin</artifactId>
    <version>3.5.1</version>
    <configuration>
        <createDependencyReducedPom>false</createDependencyReducedPom>
        <filters>
            <filter>
                <artifact>*:*</artifact>
                <excludes>
                    <exclude>META-INF/*.SF</exclude>
                    <exclude>META-INF/*.DSA</exclude>
                    <exclude>META-INF/*.RSA</exclude>
                    <exclude>META-INF/LICENSE*</exclude>
                    <exclude>META-INF/NOTICE*</exclude>
                </excludes>
            </filter>
        </filters>
    </configuration>
    <executions>
        <execution>
            <phase>package</phase>
            <goals>
                <goal>shade</goal>
            </goals>
            <configuration>
                <transformers>
                    <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
                </transformers>
            </configuration>
        </execution>
    </executions>
</plugin>
```

---

## Performance Tuning

### JVM Options for Lambda

```yaml
# serverless.yml
provider:
  name: aws
  runtime: java21
  environment:
    # Optimize for short-lived Lambda
    JAVA_TOOL_OPTIONS: >-
      -XX:+TieredCompilation
      -XX:TieredStopAtLevel=1
      -XX:+UseSerialGC
      -Xmx256m
      -XX:MaxMetaspaceSize=128m
```

### Custom Runtime (Advanced)

For maximum cold start reduction, consider GraalVM native image:

```dockerfile
# Dockerfile for custom runtime
FROM ghcr.io/graalvm/graalvm-ce:ol9-java21-21.0.2 AS builder
WORKDIR /app
COPY . .
RUN ./gradlew nativeCompile

FROM public.ecr.aws/lambda/provided:al2023
COPY --from=builder /app/build/native/nativeCompile/my-app ${LAMBDA_RUNTIME_DIR}/bootstrap
CMD ["com.example.Handler"]
```

### Memory Configuration Guide

| JAR Size | Min Memory | Recommended | Notes |
|----------|-----------|-------------|-------|
| < 10MB | 256MB | 512MB | Simple handlers |
| 10-50MB | 512MB | 1024MB | With AWS SDK |
| > 50MB | 1024MB | 1769MB | Large dependencies |

### Cold Start Benchmarks

Typical cold start times for Raw Java (512MB):

- **Minimal handler** (no AWS SDK): ~150-250ms
- **With DynamoDB client**: ~200-350ms
- **With multiple clients**: ~300-500ms

Warm start times: typically < 10ms

---

## Logging Configuration

```xml
<!-- src/main/resources/log4j2.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<Configuration>
    <Appenders>
        <Lambda name="Lambda">
            <PatternLayout>
                <pattern>%d{yyyy-MM-dd HH:mm:ss} %X{AWSRequestId} %-5p %c{1} - %m%n</pattern>
            </PatternLayout>
        </Lambda>
    </Appenders>
    <Loggers>
        <Root level="info">
            <AppenderRef ref="Lambda"/>
        </Root>
        <Logger name="software.amazon.awssdk" level="warn"/>
    </Loggers>
</Configuration>
```

---

## Best Practices Summary

1. **Always use static fields** for service initialization
2. **Keep JAR size minimal** - exclude unused dependencies
3. **Use Java 21** for best performance
4. **Set appropriate memory** - start with 512MB
5. **Handle exceptions** gracefully with proper HTTP status codes
6. **Log request IDs** for troubleshooting
7. **Validate environment variables** at startup
8. **Reuse AWS clients** - don't create per-request
