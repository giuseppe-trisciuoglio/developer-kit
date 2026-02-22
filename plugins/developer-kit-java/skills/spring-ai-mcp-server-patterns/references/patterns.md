# Spring AI MCP Server - Implementation Patterns

## Tool Creation Pattern

Use annotation-driven tools with explicit parameter descriptions.

```java
@Component
public class CalculatorTools {

    @McpTool(name = "add", description = "Add two integers")
    public int add(
            @McpToolParam(description = "First integer", required = true) int a,
            @McpToolParam(description = "Second integer", required = true) int b) {
        return a + b;
    }

    @McpTool(description = "Divide two numbers")
    public double divide(
            @McpToolParam(description = "Dividend", required = true) double a,
            @McpToolParam(description = "Divisor", required = true) double b) {
        if (b == 0) {
            throw new IllegalArgumentException("Divisor must be non-zero");
        }
        return a / b;
    }
}
```

## Prompt Provider Pattern

Use `@McpPrompt` for prompt capabilities.

```java
@Component
public class PromptProvider {

    @McpPrompt(name = "greeting", description = "Generate a greeting message")
    public GetPromptResult greeting(
            @McpArg(name = "name", description = "User name", required = true) String name) {

        String message = "Hello, " + name + "! How can I help you today?";

        return new GetPromptResult(
            "Greeting",
            List.of(new PromptMessage(Role.ASSISTANT, new TextContent(message)))
        );
    }
}
```

## HTTP/SSE Transport Pattern

Use the Web starter and protocol configuration.

```yaml
spring:
  ai:
    mcp:
      server:
        name: weather-server
        version: 1.0.0
        type: SYNC
        protocol: SSE
        capabilities:
          tool: true
          prompt: true
```

## STDIO Pattern

Use the dedicated STDIO starter and enable stdio explicitly.

```properties
spring.ai.mcp.server.stdio=true
spring.ai.mcp.server.name=local-stdio-server
spring.ai.mcp.server.version=1.0.0
```

## Tool Callback Bridge Pattern

You can expose existing Spring AI tool callbacks through the MCP server conversion support.

```properties
spring.ai.mcp.server.tool-callback-converter=true
```

## Operational Pattern

1. Keep tool methods deterministic where possible.
2. Validate every input argument.
3. Fail fast with clear exceptions.
4. Return compact, typed responses.
5. Add observability around tool execution latency and failure rate.
