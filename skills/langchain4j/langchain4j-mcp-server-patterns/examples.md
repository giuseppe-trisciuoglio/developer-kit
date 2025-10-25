# LangChain4j MCP Server Patterns - Practical Examples

Production-ready examples for Model Context Protocol (MCP) server implementation with LangChain4j.

## 1. Basic MCP Server Setup

**Scenario**: Minimal MCP server providing tools and resources.

```java
import io.modelcontextprotocol.server.*;
import io.modelcontextprotocol.spec.SchemaOrReference;

public class BasicMcpServer {
    
    public static void main(String[] args) throws Exception {
        var server = new MCPServer.Builder()
            .serverInfo(new ServerInfo(
                "langchain4j-server",
                "1.0.0"
            ))
            .toolProvider(context -> List.of(
                new Tool.Builder()
                    .name("add")
                    .description("Add two numbers")
                    .inputSchema(createAddSchema())
                    .build()
            ))
            .toolCallHandler((toolName, toolInput) -> {
                if ("add".equals(toolName)) {
                    int a = (int) toolInput.get("a");
                    int b = (int) toolInput.get("b");
                    return String.valueOf(a + b);
                }
                return "Unknown tool";
            })
            .build();
        
        server.start();
    }
    
    private static SchemaOrReference createAddSchema() {
        return SchemaOrReference.schema(
            Schema.builder()
                .type("object")
                .properties(Map.of(
                    "a", Schema.builder().type("number").build(),
                    "b", Schema.builder().type("number").build()
                ))
                .required(List.of("a", "b"))
                .build()
        );
    }
}
```

## 2. MCP Server with Multiple Tools

**Scenario**: Server providing various computational and data tools.

```java
public class MultiToolMcpServer {
    
    public static void main(String[] args) throws Exception {
        var server = new MCPServer.Builder()
            .serverInfo(new ServerInfo(
                "multi-tool-server",
                "1.0.0"
            ))
            .toolProvider(context -> Arrays.asList(
                createCalculatorTool(),
                createStringTool(),
                createDataTool()
            ))
            .toolCallHandler(new MultiToolHandler())
            .build();
        
        server.start();
    }
    
    private static Tool createCalculatorTool() {
        return new Tool.Builder()
            .name("calculate")
            .description("Perform mathematical calculations")
            .inputSchema(buildCalculatorSchema())
            .build();
    }
    
    private static Tool createStringTool() {
        return new Tool.Builder()
            .name("transform_text")
            .description("Transform text (uppercase, lowercase, reverse)")
            .inputSchema(buildStringSchema())
            .build();
    }
    
    private static Tool createDataTool() {
        return new Tool.Builder()
            .name("query_data")
            .description("Query sample data")
            .inputSchema(buildDataSchema())
            .build();
    }
}

class MultiToolHandler implements ToolCallHandler {
    @Override
    public String handle(String toolName, Map<String, Object> input) {
        return switch (toolName) {
            case "calculate" -> handleCalculate(input);
            case "transform_text" -> handleTransform(input);
            case "query_data" -> handleQuery(input);
            default -> "Unknown tool";
        };
    }
    
    private String handleCalculate(Map<String, Object> input) {
        String operation = (String) input.get("operation");
        double a = ((Number) input.get("a")).doubleValue();
        double b = ((Number) input.get("b")).doubleValue();
        
        return switch (operation) {
            case "add" -> String.valueOf(a + b);
            case "subtract" -> String.valueOf(a - b);
            case "multiply" -> String.valueOf(a * b);
            case "divide" -> String.valueOf(a / b);
            default -> "Unknown operation";
        };
    }
    
    private String handleTransform(Map<String, Object> input) {
        String text = (String) input.get("text");
        String type = (String) input.get("type");
        
        return switch (type) {
            case "uppercase" -> text.toUpperCase();
            case "lowercase" -> text.toLowerCase();
            case "reverse" -> new StringBuilder(text).reverse().toString();
            default -> text;
        };
    }
    
    private String handleQuery(Map<String, Object> input) {
        String table = (String) input.get("table");
        return "Data from " + table + ": [sample data]";
    }
}
```

## 3. MCP Server with Resource Providers

**Scenario**: Server providing access to resources (documents, files).

```java
public class ResourceMcpServer {
    
    public static void main(String[] args) throws Exception {
        var server = new MCPServer.Builder()
            .serverInfo(new ServerInfo(
                "resource-server",
                "1.0.0"
            ))
            .resourceListProvider(() -> Arrays.asList(
                new Resource(
                    "file://docs/guide.md",
                    "Spring Boot Guide",
                    "text/markdown"
                ),
                new Resource(
                    "file://docs/api.md",
                    "API Documentation",
                    "text/markdown"
                )
            ))
            .resourceReadHandler(uri -> {
                if (uri.contains("guide")) {
                    return "# Spring Boot Guide\nSpring Boot simplifies building Java applications...";
                } else if (uri.contains("api")) {
                    return "# API Documentation\nBase URL: https://api.example.com...";
                }
                return "Resource not found";
            })
            .build();
        
        server.start();
    }
}
```

## 4. MCP Server with Prompts

**Scenario**: Server providing reusable prompt templates.

```java
public class PromptMcpServer {
    
    public static void main(String[] args) throws Exception {
        var server = new MCPServer.Builder()
            .serverInfo(new ServerInfo(
                "prompt-server",
                "1.0.0"
            ))
            .promptListProvider(() -> Arrays.asList(
                createCodeReviewPrompt(),
                createDocumentationPrompt(),
                createTestGenerationPrompt()
            ))
            .promptGetHandler(promptName -> {
                return switch (promptName) {
                    case "code-review" -> buildCodeReviewPrompt();
                    case "documentation" -> buildDocumentationPrompt();
                    case "test-generation" -> buildTestPrompt();
                    default -> null;
                };
            })
            .build();
        
        server.start();
    }
    
    private static Prompt createCodeReviewPrompt() {
        return new Prompt.Builder()
            .name("code-review")
            .description("Template for code review analysis")
            .arguments(List.of(
                new PromptArgument.Builder()
                    .name("code")
                    .description("Code to review")
                    .required(true)
                    .build()
            ))
            .build();
    }
    
    private static PromptResponse buildCodeReviewPrompt() {
        return new PromptResponse(
            "Review the following code for quality, security, and performance:\n\n" +
            "{{code}}\n\n" +
            "Provide feedback on:\n" +
            "1. Code quality and readability\n" +
            "2. Security vulnerabilities\n" +
            "3. Performance optimization opportunities\n" +
            "4. Best practices and patterns",
            new ArrayList<>()
        );
    }
    
    // Similar for documentation and test generation...
}
```

## 5. MCP Server with Error Handling

**Scenario**: Robust error handling and validation.

```java
public class RobustMcpServer {
    
    public static void main(String[] args) throws Exception {
        var server = new MCPServer.Builder()
            .serverInfo(new ServerInfo(
                "robust-server",
                "1.0.0"
            ))
            .toolProvider(context -> List.of(
                createValidatedTool()
            ))
            .toolCallHandler(new RobustToolHandler())
            .exceptionHandler((exception) -> {
                logger.error("Tool execution error", exception);
                return "Error: " + exception.getMessage();
            })
            .build();
        
        server.start();
    }
    
    private static Tool createValidatedTool() {
        return new Tool.Builder()
            .name("validated-operation")
            .description("Operation with input validation")
            .inputSchema(buildValidatedSchema())
            .build();
    }
}

class RobustToolHandler implements ToolCallHandler {
    
    @Override
    public String handle(String toolName, Map<String, Object> input) {
        try {
            validateInput(input);
            return executeOperation(input);
        } catch (ValidationException e) {
            return "Validation error: " + e.getMessage();
        } catch (Exception e) {
            return "Execution error: " + e.getMessage();
        }
    }
    
    private void validateInput(Map<String, Object> input) 
        throws ValidationException {
        if (input == null || input.isEmpty()) {
            throw new ValidationException("Input cannot be empty");
        }
        
        if (!input.containsKey("required_field")) {
            throw new ValidationException("Missing required field");
        }
        
        Object value = input.get("required_field");
        if (value instanceof Number num && num.doubleValue() < 0) {
            throw new ValidationException("Value must be non-negative");
        }
    }
    
    private String executeOperation(Map<String, Object> input) {
        // Safe execution after validation
        return "Operation completed successfully";
    }
}

class ValidationException extends Exception {
    public ValidationException(String message) {
        super(message);
    }
}
```

## 6. MCP Server with Context Integration

**Scenario**: Server integrated with Spring or application context.

```java
@Configuration
public class McpServerConfiguration {
    
    @Bean
    public MCPServer mcpServer(ChatModel chatModel, 
                               EmbeddingModel embeddingModel) {
        return new MCPServer.Builder()
            .serverInfo(new ServerInfo(
                "spring-integrated-server",
                "1.0.0"
            ))
            .toolProvider(context -> buildToolsFromContext(
                chatModel, embeddingModel
            ))
            .toolCallHandler((toolName, input) -> 
                executeToolWithContext(toolName, input, 
                    chatModel, embeddingModel)
            )
            .build();
    }
    
    private List<Tool> buildToolsFromContext(
            ChatModel chatModel,
            EmbeddingModel embeddingModel) {
        return List.of(
            createAiServiceTool(chatModel),
            createEmbeddingTool(embeddingModel)
        );
    }
    
    private String executeToolWithContext(String toolName,
            Map<String, Object> input,
            ChatModel chatModel,
            EmbeddingModel embeddingModel) {
        return switch (toolName) {
            case "ai-query" -> handleAiQuery((String) input.get("query"), chatModel);
            case "embedding" -> handleEmbedding((String) input.get("text"), embeddingModel);
            default -> "Unknown tool";
        };
    }
}
```

## 7. MCP Server Client Connection

**Scenario**: Connect clients to the MCP server.

```java
public class McpServerClient {
    
    public static void main(String[] args) throws Exception {
        // Start server
        var server = createMcpServer();
        server.start();
        
        // Connect client
        var client = new MCPClient.Builder()
            .connect("localhost", 3000)
            .build();
        
        // List available tools
        var tools = client.listTools();
        tools.forEach(tool -> 
            System.out.println("Tool: " + tool.name())
        );
        
        // Call a tool
        var result = client.callTool("add", Map.of(
            "a", 5,
            "b", 3
        ));
        System.out.println("Result: " + result);
    }
}
```

## Best Practices

1. **Clear Tool Descriptions**: Help clients understand capabilities
2. **Input Validation**: Validate all inputs before execution
3. **Error Handling**: Graceful error messages and logging
4. **Schema Definition**: Clear, accurate JSON schemas
5. **Resource Management**: Proper cleanup of resources
6. **Performance**: Cache frequently accessed data
7. **Security**: Validate and sanitize inputs
8. **Testing**: Test tools with various inputs
9. **Documentation**: Document tools and resources
10. **Monitoring**: Track tool usage and performance
