# Build Integration

## Maven Plugin

### OpenAPI Generation Plugin

```xml
<plugin>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-maven-plugin</artifactId>
    <version>1.4</version>
    <executions>
        <execution>
            <phase>integration-test</phase>
            <goals>
                <goal>generate</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <apiDocsUrl>http://localhost:8080/v3/api-docs</apiDocsUrl>
        <outputFileName>openapi.json</outputFileName>
        <outputDir>${project.build.directory}</outputDir>
    </configuration>
</plugin>
```

### Custom Configuration

```xml
<plugin>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-maven-plugin</artifactId>
    <version>1.4</version>
    <executions>
        <execution>
            <phase>verify</phase>
            <goals>
                <goal>generate</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <apiDocsUrl>http://localhost:8080/v3/api-docs</apiDocsUrl>
        <outputFileName>openapi.yaml</outputFileName>
        <outputDir>${project.build.directory}/docs</outputDir>
        <skip>false</skip>
        <headers>
            <Authorization>Bearer test-token</Authorization>
        </headers>
    </configuration>
</plugin>
```

### Multiple API Groups

```xml
<plugin>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-maven-plugin</artifactId>
    <version>1.4</version>
    <executions>
        <execution>
            <id>generate-public-api</id>
            <phase>verify</phase>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <apiDocsUrl>http://localhost:8080/v3/api-docs/public</apiDocsUrl>
                <outputFileName>public-api.json</outputFileName>
                <outputDir>${project.build.directory}/docs</outputDir>
            </configuration>
        </execution>
        <execution>
            <id>generate-admin-api</id>
            <phase>verify</phase>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <apiDocsUrl>http://localhost:8080/v3/api-docs/admin</apiDocsUrl>
                <outputFileName>admin-api.json</outputFileName>
                <outputDir>${project.build.directory}/docs</outputDir>
            </configuration>
        </execution>
    </executions>
</plugin>
```

## Gradle Plugin

### Basic Gradle Configuration

```gradle
plugins {
    id 'org.springdoc.openapi-gradle-plugin' version '1.9.0'
}

openApi {
    apiDocsUrl = "http://localhost:8080/v3/api-docs"
    outputDir = file("$buildDir/docs")
    outputFileName = "openapi.json"
}
```

### Custom Gradle Configuration

```gradle
openapi {
    apiDocsUrl.set("http://localhost:8080/v3/api-docs")
    outputDir.set(file("$buildDir/docs"))
    outputFileName.set("openapi.yaml")
    groupedApiMappings.set([
        "public": "http://localhost:8080/v3/api-docs/public",
        "admin": "http://localhost:8080/v3/api-docs/admin"
    ])
}
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Generate API Docs

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run application
        run: |
          mvn spring-boot:run &
          sleep 30  # Wait for app to start

      - name: Generate OpenAPI docs
        run: mvn verify

      - name: Upload API docs
        uses: actions/upload-artifact@v3
        with:
          name: openapi-spec
          path: target/openapi.json
```

### GitLab CI Pipeline

```yaml
stages:
  - build
  - docs

build:
  stage: build
  script:
    - mvn clean install
  artifacts:
    paths:
      - target/*.jar

generate-docs:
  stage: docs
  services:
    - name: app:latest
      alias: api
  script:
    - apk add --no-cache curl
    - curl http://api:8080/v3/api-docs -o openapi.json
  artifacts:
    paths:
      - openapi.json
  only:
    - main
```

## Automated Testing

### OpenAPI Specification Validation

```java
import org.springdoc.core.utils.SpringDocUtils;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class OpenApiDocumentationTest {

    @Autowired
    private OpenApiContract openApiContract;

    @Test
    void validateOpenApiSpec() {
        OpenAPI openAPI = openApiContract.getOpenApi();

        assertNotNull(openAPI);
        assertNotNull(openAPI.getInfo());
        assertEquals("1.0.0", openAPI.getInfo().getVersion());
        assertFalse(openAPI.getPaths().isEmpty());
    }

    @Test
    void allPathsHaveDocumentation() {
        OpenAPI openAPI = openApiContract.getOpenApi();

        openAPI.getPaths().forEach((path, pathItem) -> {
            pathItem.readOperationsMap().forEach((method, operation) -> {
                assertNotNull(operation.getSummary(), "Missing summary for " + method + " " + path);
                assertFalse(operation.getResponses().isEmpty(), "No responses for " + method + " " + path);
            });
        });
    }
}
```

### Schema Validation Tests

```java
@Test
void validateBookSchema() {
    OpenAPI openAPI = openApiContract.getOpenApi();
    Schema bookSchema = openAPI.getComponents().getSchemas().get("Book");

    assertNotNull(bookSchema);
    assertTrue(bookSchema.getProperties().containsKey("id"));
    assertTrue(bookSchema.getProperties().containsKey("title"));
    assertTrue(bookSchema.getProperties().containsKey("author"));
}
```

## Static Documentation Generation

### Generate Swagger UI Static Files

```bash
# Using Maven
mvn verify

# Using Gradle
gradle openApi

# The generated files will be in:
# - target/openapi.json (Maven)
# - buildDir/docs/openapi.json (Gradle)
```

### Custom Output Directory

```xml
<plugin>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-maven-plugin</artifactId>
    <configuration>
        <outputDir>${project.basedir}/src/main/resources/static/docs</outputDir>
        <outputFileName>swagger.json</outputFileName>
    </configuration>
</plugin>
```

## Redoc Integration

### Add Redoc Dependency

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
</dependency>
```

### Access Redoc UI

After adding the dependency:
- **Redoc UI**: `http://localhost:8080/api-docs` (Redoc styling)
- **Swagger UI**: `http://localhost:8080/swagger-ui/index.html` (original)

### Custom Redoc Configuration

```java
@Bean
public OpenAPI openAPI() {
    return new OpenAPI()
        .info(new Info()
            .title("API Documentation")
            .version("1.0.0")
        );
}

@Configuration
public class RedocConfig {

    @Bean
    public IndexPageCustomizer indexPageCustomizer() {
        return indexHtml -> indexHtml.replace(
            "<title>",
            "<link rel='stylesheet' href='/webjars/redoc/redoc.css'><script src='/webjars/redoc/redoc.standalone.js'></script><title>"
        );
    }
}
```

## Version Management

### API Versioning Strategy

```yaml
# application.yml
springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html

# Multiple API versions
springdoc:
  group-configs:
    - group: 'v1'
      paths-to-match: /api/v1/**
    - group: 'v2'
      paths-to-match: /api/v2/**
```

### Generate Versioned Specs

```bash
# Generate v1 spec
curl http://localhost:8080/v3/api-docs/v1 > openapi-v1.json

# Generate v2 spec
curl http://localhost:8080/v3/api-docs/v2 > openapi-v2.json
```
