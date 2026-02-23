---
name: langchain4j-mcp-server-patterns
description: Provides Model Context Protocol (MCP) server implementation patterns with LangChain4j. Use when building MCP servers to extend AI capabilities with custom tools, resources, and prompt templates.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
---

# LangChain4j MCP Server Implementation Patterns

Implement Model Context Protocol (MCP) servers with LangChain4j to extend AI capabilities with standardized tools, resources, and prompt templates.

## Overview

MCP is a standardized protocol for connecting AI applications to external data sources and tools. LangChain4j provides MCP server implementation patterns that enable AI systems to dynamically discover and execute tools, access resources, and use prompt templates through a standardized interface.

## When to Use

- AI applications requiring external tool integration
- Enterprise MCP servers with multi-domain support
- Dynamic tool providers with context-aware filtering
- Resource-based data access systems for AI models
- Spring Boot applications with MCP integration
- Production-ready MCP servers with security and monitoring

## Instructions

### 1. Create Tool Provider

```java
class WeatherToolProvider implements ToolProvider {
    @Override
    public List<ToolSpecification> listTools() {
        return List.of(ToolSpecification.builder()
            .name("get_weather")
            .description("Get weather for a city")
            .inputSchema(Map.of(
                "type", "object",
                "properties", Map.of("city", Map.of("type", "string")),
                "required", List.of("city")))
            .build());
    }

    @Override
    public String executeTool(String name, String arguments) {
        return "Weather data result";
    }
}
```

### 2. Configure MCP Server

```java
MCPServer server = MCPServer.builder()
    .server(new StdioServer.Builder())
    .addToolProvider(new WeatherToolProvider())
    .build();
server.start();
```

### 3. Add Resource Provider

```java
class CompanyResourceProvider implements ResourceListProvider, ResourceReadHandler {
    @Override
    public List<McpResource> listResources() {
        return List.of(McpResource.builder()
            .uri("policies").name("Company Policies").mimeType("text/plain").build());
    }
    @Override
    public String readResource(String uri) { return loadResourceContent(uri); }
}
```

### 4. Implement Security

```java
McpToolProvider secureProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .filter((client, tool) -> {
        if (tool.name().startsWith("admin_") && !isAdmin()) return false;
        return true;
    })
    .build();
```

## Examples

### MCP Architecture

```
AI Application <-> MCP Client <-> Transport <-> MCP Server <-> External Service
```

Key Components: MCPServer, ToolProvider, ResourceListProvider, PromptListProvider, Transport (stdio, HTTP)

### Client Integration

```java
McpClient client = new DefaultMcpClient.Builder()
    .key("my-client")
    .transport(transport)
    .cacheToolList(true)
    .build();

McpToolProvider provider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .failIfOneServerFails(false)
    .build();

AIAssistant assistant = AiServices.builder(AIAssistant.class)
    .chatModel(chatModel)
    .toolProvider(provider)
    .build();
```

### Transport Configuration

```java
// Stdio (local process)
McpTransport transport = new StdioMcpTransport.Builder()
    .command(List.of("npm", "exec", "@modelcontextprotocol/server-everything"))
    .build();

// HTTP (remote server)
McpTransport transport = new HttpMcpTransport.Builder()
    .sseUrl("http://localhost:3001/sse")
    .build();
```

## Best Practices

1. **Resource Management**: Always close MCP clients with try-with-resources
2. **Error Handling**: Implement graceful degradation when servers fail
3. **Security**: Use tool filtering and resource access controls
4. **Performance**: Enable caching and optimize tool execution
5. **Monitoring**: Implement health checks and observability
6. **Configuration**: Use structured configuration for maintainability

## Constraints and Warnings

- MCP servers should implement proper resource cleanup when stopped
- Tool execution errors should not expose stack traces to clients
- Resource URIs should be validated to prevent directory traversal
- Stdio transport requires proper process lifecycle management
- HTTP transport should implement authentication and rate limiting
- Multi-server configurations require careful failure handling
- Tools with external side effects may be called unexpectedly by AI models

## References

- [API Reference](./references/api-reference.md)
- [Examples](./references/examples.md)
- [LangChain4j Documentation](https://langchain4j.com/docs/)
- [Model Context Protocol Specification](https://modelcontextprotocol.org/)
