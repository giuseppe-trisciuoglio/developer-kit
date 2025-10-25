# LangChain4j MCP Server Patterns - API References

Complete API reference for Model Context Protocol (MCP) server implementation with LangChain4j.

## MCP Server Basics

### MCPServer Builder

```java
MCPServer server = new MCPServer.Builder()
    .serverInfo(new ServerInfo(name, version))
    .toolProvider(toolProvider)                    // Provide tools
    .toolCallHandler(handler)                      // Handle tool calls
    .resourceListProvider(listProvider)            // List resources
    .resourceReadHandler(readHandler)              // Read resources
    .promptListProvider(promptProvider)            // List prompts
    .promptGetHandler(getHandler)                  // Get prompts
    .samplingProvider(samplingProvider)            // Sampling support
    .exceptionHandler(exceptionHandler)            // Error handling
    .build();

server.start();
server.stop();
```

## Tools API

### Tool Definition

```java
Tool tool = new Tool.Builder()
    .name("unique-tool-name")
    .description("What this tool does")
    .inputSchema(schema)                           // JSON schema
    .build();
```

### Tool Input Schema

```java
Schema schema = Schema.builder()
    .type("object")
    .properties(Map.of(
        "param1", Schema.builder()
            .type("string")
            .description("First parameter")
            .build(),
        "param2", Schema.builder()
            .type("number")
            .description("Second parameter")
            .build()
    ))
    .required(List.of("param1", "param2"))
    .additionalProperties(false)
    .build();

SchemaOrReference schemaRef = SchemaOrReference.schema(schema);
```

### ToolProvider

```java
@FunctionalInterface
interface ToolProvider {
    List<Tool> getTools(ToolContext context);
}

// Usage
.toolProvider(context -> Arrays.asList(
    createTool1(),
    createTool2()
))
```

### ToolCallHandler

```java
@FunctionalInterface
interface ToolCallHandler {
    String handle(String toolName, Map<String, Object> input);
}

// Usage
.toolCallHandler((toolName, input) -> {
    return switch (toolName) {
        case "add" -> handleAdd((int) input.get("a"), (int) input.get("b"));
        case "subtract" -> handleSubtract(...);
        default -> "Unknown tool";
    };
})
```

## Resources API

### Resource Definition

```java
Resource resource = new Resource(
    "uri://identifier",           // Unique URI
    "Display Name",               // Human-readable name
    "text/plain"                  // MIME type
);
```

### ResourceListProvider

```java
@FunctionalInterface
interface ResourceListProvider {
    List<Resource> listResources();
}

// Usage
.resourceListProvider(() -> Arrays.asList(
    new Resource("file://docs/guide.md", "Guide", "text/markdown"),
    new Resource("file://docs/api.md", "API", "text/markdown")
))
```

### ResourceReadHandler

```java
@FunctionalInterface
interface ResourceReadHandler {
    String readResource(String uri);
}

// Usage
.resourceReadHandler(uri -> {
    if (uri.contains("guide")) {
        return loadGuideContent();
    } else if (uri.contains("api")) {
        return loadApiContent();
    }
    throw new ResourceNotFoundException("Not found: " + uri);
})
```

## Prompts API

### Prompt Definition

```java
Prompt prompt = new Prompt.Builder()
    .name("prompt-name")
    .description("What this prompt does")
    .arguments(List.of(
        new PromptArgument.Builder()
            .name("arg1")
            .description("First argument")
            .required(true)
            .build()
    ))
    .build();
```

### PromptArgument

```java
PromptArgument arg = new PromptArgument.Builder()
    .name("argument-name")
    .description("Argument description")
    .required(true)                               // Optional or required
    .build();
```

### PromptListProvider

```java
@FunctionalInterface
interface PromptListProvider {
    List<Prompt> listPrompts();
}

// Usage
.promptListProvider(() -> Arrays.asList(
    createCodeReviewPrompt(),
    createDocumentationPrompt()
))
```

### PromptGetHandler

```java
@FunctionalInterface
interface PromptGetHandler {
    PromptResponse getPrompt(String promptName);
}

// Usage
.promptGetHandler(promptName -> {
    return switch (promptName) {
        case "code-review" -> buildCodeReviewResponse();
        case "documentation" -> buildDocumentationResponse();
        default -> null;
    };
})
```

### PromptResponse

```java
PromptResponse response = new PromptResponse(
    "Prompt text with {{argument}} placeholders",
    List.of()                                     // Additional messages
);
```

## Schema Definition

### Common Schema Types

**String**:
```java
Schema.builder()
    .type("string")
    .minLength(1)
    .maxLength(100)
    .pattern("^[A-Za-z]+$")
    .enum(List.of("value1", "value2"))
    .build()
```

**Number**:
```java
Schema.builder()
    .type("number")
    .minimum(0)
    .maximum(100)
    .exclusiveMinimum(true)
    .multipleOf(5)
    .build()
```

**Integer**:
```java
Schema.builder()
    .type("integer")
    .minimum(1)
    .maximum(10)
    .build()
```

**Boolean**:
```java
Schema.builder()
    .type("boolean")
    .build()
```

**Array**:
```java
Schema.builder()
    .type("array")
    .items(Schema.builder()
        .type("string")
        .build())
    .minItems(1)
    .maxItems(10)
    .uniqueItems(true)
    .build()
```

**Object**:
```java
Schema.builder()
    .type("object")
    .properties(Map.of(
        "name", Schema.builder().type("string").build(),
        "age", Schema.builder().type("integer").build()
    ))
    .required(List.of("name"))
    .additionalProperties(false)
    .build()
```

## Server Info

### ServerInfo Definition

```java
ServerInfo info = new ServerInfo(
    "server-name",           // Unique identifier
    "1.0.0"                  // Version
);
```

## Context API

### ToolContext

```java
interface ToolContext {
    List<String> toolNames();
    String clientName();
    // Additional context
}
```

## Exception Handling

### ExceptionHandler

```java
@FunctionalInterface
interface ExceptionHandler {
    String handle(Exception exception);
}

// Usage
.exceptionHandler(exception -> {
    logger.error("Error in MCP server", exception);
    return "Error: " + exception.getMessage();
})
```

## MCPClient API

### Client Connection

```java
MCPClient client = new MCPClient.Builder()
    .connect(host, port)
    .timeout(Duration.ofSeconds(30))
    .build();
```

### Tool Operations

```java
// List tools
List<Tool> tools = client.listTools();

// Get tool details
Tool tool = client.getTool("tool-name");

// Call tool
String result = client.callTool("tool-name", Map.of(
    "param1", "value1",
    "param2", 42
));
```

### Resource Operations

```java
// List resources
List<Resource> resources = client.listResources();

// Read resource
String content = client.readResource("resource-uri");
```

### Prompt Operations

```java
// List prompts
List<Prompt> prompts = client.listPrompts();

// Get prompt
PromptResponse response = client.getPrompt("prompt-name", Map.of(
    "arg1", "value1"
));
```

## Input/Output Formats

### Tool Input Format

```java
Map<String, Object> input = new HashMap<>();
input.put("param1", "string value");
input.put("param2", 42);
input.put("param3", Arrays.asList("item1", "item2"));
```

### Tool Output Format

```java
// String output
return "Success: operation completed";

// JSON output
return "{\"status\": \"success\", \"count\": 10}";

// Structured output
Map<String, Object> output = new HashMap<>();
output.put("status", "success");
output.put("data", results);
return objectMapper.writeValueAsString(output);
```

## Best Practices

1. **Descriptive Names**: Clear, actionable tool names
2. **Comprehensive Schemas**: Detailed JSON schemas for validation
3. **Error Messages**: Clear, actionable error messages
4. **Input Validation**: Validate all inputs before processing
5. **Performance**: Cache results when possible
6. **Security**: Sanitize and validate all inputs
7. **Logging**: Log tool calls for debugging
8. **Documentation**: Document all tools and parameters
9. **Versioning**: Version your server and tools
10. **Testing**: Test tools with various inputs

## Common Patterns

### Error Handling Pattern
```java
try {
    return executeOperation(input);
} catch (ValidationException e) {
    return "Validation error: " + e.getMessage();
} catch (Exception e) {
    logger.error("Unexpected error", e);
    return "An error occurred: " + e.getMessage();
}
```

### Schema Building Pattern
```java
private static Schema buildParameterSchema(String paramName, 
                                           String type, 
                                           String description) {
    return Schema.builder()
        .type(type)
        .description(description)
        .build();
}
```

### Tool Creation Pattern
```java
private static Tool createTool(String name, String description,
                               Map<String, Schema> properties) {
    return new Tool.Builder()
        .name(name)
        .description(description)
        .inputSchema(SchemaOrReference.schema(
            Schema.builder()
                .type("object")
                .properties(properties)
                .required(new ArrayList<>(properties.keySet()))
                .build()
        ))
        .build();
}
```

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [LangChain4j Documentation](https://docs.langchain4j.dev)
- [OpenAI API Reference](https://platform.openai.com/docs)
