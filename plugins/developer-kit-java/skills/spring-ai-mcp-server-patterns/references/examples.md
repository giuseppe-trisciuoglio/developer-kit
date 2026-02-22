# Spring AI MCP Server Examples

## 1. Minimal MCP Server (Annotation-Based)

```java
@SpringBootApplication
public class SimpleMcpApplication {
    public static void main(String[] args) {
        SpringApplication.run(SimpleMcpApplication.class, args);
    }
}

@Component
class CalculatorTools {

    @McpTool(description = "Add two numbers")
    public double add(
            @McpToolParam(description = "First number", required = true) double a,
            @McpToolParam(description = "Second number", required = true) double b) {
        return a + b;
    }
}
```

## 2. Prompt Provider Example

```java
@Component
class PromptProvider {

    @McpPrompt(name = "greeting", description = "Generate greeting message")
    public GetPromptResult greeting(
            @McpArg(name = "name", description = "User name", required = true) String name) {

        String message = "Hello, " + name + "!";

        return new GetPromptResult(
            "Greeting",
            List.of(new PromptMessage(Role.ASSISTANT, new TextContent(message)))
        );
    }
}
```

## 3. Maven Setup (WebMVC)

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>${spring-ai.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-model-openai</artifactId>
    </dependency>
</dependencies>
```

## 4. STDIO Configuration

```properties
spring.ai.mcp.server.stdio=true
spring.ai.mcp.server.name=stdio-mcp-server
spring.ai.mcp.server.version=1.0.0
```

## 5. Web Protocol Configuration

```yaml
spring:
  ai:
    mcp:
      server:
        name: weather-server
        version: 1.0.0
        type: SYNC
        protocol: STREAMABLE
        capabilities:
          tool: true
          prompt: true
          resource: false
          completion: false
```

## 6. Secured Tool Example

```java
@Component
@Validated
class AdminTools {

    @McpTool(description = "Delete an order by id")
    @PreAuthorize("hasRole('ADMIN')")
    public DeleteResult deleteOrder(
            @McpToolParam(description = "Order id", required = true)
            @NotBlank String orderId) {
        return new DeleteResult(orderId, true);
    }
}

record DeleteResult(String orderId, boolean deleted) {}
```

## 7. Basic Test Example

```java
@SpringBootTest
class McpServerSmokeTest {

    @Test
    void contextLoads() {
    }
}
```
