# Spring AI MCP Server - Configuration Reference

## Starter Selection

Choose one MCP server starter based on transport:

- `spring-ai-starter-mcp-server`: STDIO transport
- `spring-ai-starter-mcp-server-webmvc`: Servlet stack (SSE/Streamable HTTP)
- `spring-ai-starter-mcp-server-webflux`: Reactive stack (SSE/Streamable HTTP)

Add one model starter in the same app (for example OpenAI or Anthropic).

## Maven Example

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

## Core Property Prefix

All MCP server properties use:

```text
spring.ai.mcp.server.*
```

## Common Properties

```yaml
spring:
  ai:
    mcp:
      server:
        enabled: true
        name: weather-mcp-server
        version: 1.0.0
        type: SYNC
        capabilities:
          tool: true
          resource: true
          prompt: true
          completion: true
```

## STDIO Configuration

```properties
spring.ai.mcp.server.stdio=true
spring.ai.mcp.server.name=stdio-mcp-server
spring.ai.mcp.server.version=1.0.0
```

## WebMVC / WebFlux Configuration

Use `protocol` with web starters:

- `SSE`
- `STREAMABLE`
- `STATELESS`

```yaml
spring:
  ai:
    mcp:
      server:
        name: web-mcp-server
        version: 1.0.0
        protocol: STREAMABLE
        sse-message-endpoint: /mcp/messages
        keep-alive-interval: 30s
```

## Annotation Scanner

```properties
spring.ai.mcp.server.annotation-scanner.enabled=true
```

## Tool Callback Conversion

Enable/disable conversion from Spring AI ToolCallbacks to MCP tool specs:

```properties
spring.ai.mcp.server.tool-callback-converter=true
```

## Production Notes

1. Pin `spring-ai.version` and upgrade intentionally.
2. Restrict external transport exposure with network and auth controls.
3. Set request timeouts and keep response payloads bounded.
4. Keep capability flags minimal for principle of least privilege.
