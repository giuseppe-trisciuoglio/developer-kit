# Spring AI MCP Server API Reference

This reference summarizes the MCP server annotations and key configuration properties used in Spring AI.

## Core MCP Server Annotations

### `@McpTool`

Declares a method as an MCP tool callable by clients.

```java
@Component
public class WeatherTools {

    @McpTool(name = "current-weather", description = "Get current weather for a city")
    public String getWeather(
            @McpToolParam(description = "City name", required = true) String city) {
        return "Current temperature in " + city + ": 22C";
    }
}
```

### `@McpToolParam`

Documents tool parameters used for generated schema and model understanding.

## Prompt Annotations

### `@McpPrompt`

Declares a prompt provider method.

### `@McpArg`

Declares prompt arguments.

```java
@Component
public class PromptProvider {

    @McpPrompt(name = "greeting", description = "Generate a greeting")
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

## Additional Server Annotations

Spring AI MCP annotations also include:

- `@McpResource`
- `@McpComplete`

Use these when your server needs resource and completion capabilities.

## Transport and Starter Mapping

- `spring-ai-starter-mcp-server`: STDIO transport
- `spring-ai-starter-mcp-server-webmvc`: WebMVC transport
- `spring-ai-starter-mcp-server-webflux`: WebFlux transport

## Key Properties (`spring.ai.mcp.server.*`)

| Property | Purpose | Typical Value |
|---|---|---|
| `enabled` | Enable/disable server | `true` |
| `name` | Server name | `weather-mcp-server` |
| `version` | Server version | `1.0.0` |
| `type` | Sync/Async server mode | `SYNC` or `ASYNC` |
| `protocol` | Web protocol mode | `SSE`, `STREAMABLE`, `STATELESS` |
| `stdio` | Enable STDIO transport | `true` / `false` |
| `capabilities.tool` | Tool capability toggle | `true` |
| `capabilities.resource` | Resource capability toggle | `true` |
| `capabilities.prompt` | Prompt capability toggle | `true` |
| `capabilities.completion` | Completion capability toggle | `true` |
| `annotation-scanner.enabled` | Enable annotation scanning | `true` |
| `tool-callback-converter` | Convert ToolCallbacks to MCP tools | `true` |

## Minimal Config Examples

### STDIO

```properties
spring.ai.mcp.server.stdio=true
spring.ai.mcp.server.name=local-stdio-server
spring.ai.mcp.server.version=1.0.0
```

### WebMVC/WebFlux

```yaml
spring:
  ai:
    mcp:
      server:
        name: web-mcp-server
        version: 1.0.0
        protocol: SSE
```

## Notes

1. Keep examples aligned to the Spring AI version pinned in your BOM.
2. Prefer annotation-based server definitions unless you have a clear need for manual low-level wiring.
