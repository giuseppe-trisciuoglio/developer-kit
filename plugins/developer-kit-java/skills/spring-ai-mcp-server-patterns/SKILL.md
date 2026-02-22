---
name: spring-ai-mcp-server-patterns
description: Provides Model Context Protocol (MCP) server implementation patterns with Spring AI. Use when building MCP servers to extend AI capabilities with custom tools, resources, and prompt templates using Spring's official AI framework.
category: ai-integration
tags: [spring-ai, mcp, model-context-protocol, tools, function-calling, prompts, java, spring-boot, enterprise]
version: 2.2.0
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring AI MCP Server Implementation Patterns

Implement Model Context Protocol (MCP) servers with Spring AI to extend AI capabilities with standardized tools, resources, and prompt templates using Spring's native AI abstractions.

## Overview

The Model Context Protocol (MCP) is a standardized protocol for connecting AI applications to external data sources and tools. Spring AI provides native support for MCP servers that expose Spring components as callable capabilities for AI models. This skill covers tools (`@McpTool`), prompts (`@McpPrompt`), transport (STDIO, SSE, Streamable HTTP), security, and testing.

## When to Use

- AI applications requiring external tool integration with Spring AI
- Enterprise MCP servers with Spring ecosystem integration
- Function calling servers with Spring AI's declarative patterns
- Prompt providers for standardized AI interactions
- Production-ready MCP servers with Spring Security and monitoring
- Microservices that expose AI capabilities via MCP protocol

## Instructions

### 1. Project Setup

1. Add Spring AI MCP starter dependencies to your `pom.xml` or `build.gradle`
2. Add the model starter (OpenAI, Anthropic, etc.)
3. Configure server properties under `spring.ai.mcp.server.*`

### 2. Define Tools

1. Create a Spring component class (`@Component` or `@Service`)
2. Annotate methods with `@McpTool(description = "...")`
3. Use `@McpToolParam` to document parameters for model understanding
4. Implement business logic with input validation and explicit errors

### 3. Define Prompts

1. Create prompt provider components
2. Annotate methods with `@McpPrompt`
3. Define arguments with `@McpArg`
4. Return prompt messages using MCP prompt result types

### 4. Configure Transport

1. Choose transport type: `STDIO`, `SSE`, `STREAMABLE`, or `STATELESS`
2. Configure transport properties in `application.yml`
3. Set network/security constraints if exposing HTTP transport

### 5. Add Security

1. Implement Spring Security configuration
2. Apply authorization policies (for example with `@PreAuthorize`)
3. Add validation/sanitization to prevent injection attacks

### 6. Testing

1. Write unit tests for individual tools and prompt providers
2. Add integration tests for Spring context and MCP wiring
3. Use Testcontainers for database-dependent tools

## Examples

### Basic MCP Server with Spring AI

```java
@SpringBootApplication
public class WeatherMcpApplication {
    public static void main(String[] args) {
        SpringApplication.run(WeatherMcpApplication.class, args);
    }
}

@Component
public class WeatherTools {

    @McpTool(description = "Get current weather for a city")
    public WeatherData getWeather(
            @McpToolParam(description = "City name", required = true) String city) {
        return new WeatherData(city, "Sunny", 22.5);
    }
}
```

### Build Configuration

**Maven (WebMVC transport):**
```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-openai</artifactId>
</dependency>
```

**Maven (STDIO transport):**
```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server</artifactId>
</dependency>
```

**Note:** Use the Spring AI BOM and pin a tested version for production.

### MCP Architecture

```
AI Application <-> MCP Client <-> Spring AI <-> MCP Server <-> Spring Services
```

Key Spring AI components:
- **@McpTool**: Declares methods as callable tools
- **@McpToolParam**: Documents tool parameters
- **@McpPrompt**: Declares prompt providers
- **@McpArg**: Documents prompt arguments

## Best Practices

1. **Prefer Declarative MCP Annotations**: Use Spring AI MCP annotations over manual wiring where possible
2. **Keep Tools Focused**: Each tool should do one thing well
3. **Document Parameters**: Use clear descriptions and required flags
4. **Return Structured Data**: Use records or DTOs for return values
5. **Validate Inputs**: Never trust model-generated arguments directly
6. **Apply Authorization**: Enforce role or permission checks for sensitive tools
7. **Add Timeouts and Limits**: Protect expensive operations
8. **Use Caching for Stable Reads**: Cache expensive deterministic lookups
9. **Design for Idempotency**: Especially for retried tool calls
10. **Keep Responses Compact**: Respect model context windows

## Migration from Legacy Tool Annotations

- Replace generic tool annotations with Spring AI MCP annotations:
  - `@Tool` -> `@McpTool`
  - `@ToolParam` -> `@McpToolParam`
- For prompt providers, use `@McpPrompt` with `@McpArg`
- Move configuration to `spring.ai.mcp.server.*` keys

```java
// Before
@Tool(description = "Get weather information")
public String getWeather(@ToolParam("city name") String city) { ... }

// After
@McpTool(description = "Get weather information")
public String getWeather(
        @McpToolParam(description = "City name", required = true) String city) { ... }
```

## Constraints and Warnings

- **Never Expose Sensitive Data** in tool descriptions, parameter names, or error messages
- **Input Validation is Mandatory**: Models may generate malformed or malicious arguments
- **Prevent Injection**: Use parameterized queries and strict path validation
- **Authorization Required**: Sensitive tools must verify caller permissions
- **Timeout Handling**: External calls need bounded latency
- **Version Compatibility**: Spring AI APIs evolve; pin versions and validate before upgrade
- **Non-Idempotent Tools**: Clearly document side effects and guard retries

## References

- [Implementation Patterns](./references/patterns.md) - MCP tool/prompt and callback patterns
- [Configuration Reference](./references/configuration.md) - Starter selection and property patterns
- [Security Patterns](./references/security.md) - Tool authorization and input hardening
- [Testing Patterns](./references/testing.md) - Unit and integration testing patterns
- [Examples](./references/examples.md) - End-to-end MCP server examples
- [API Reference](./references/api-reference.md) - Core annotations and properties
- [Spring AI Documentation](https://docs.spring.io/spring-ai/reference/)
- [Model Context Protocol Specification](https://modelcontextprotocol.org/)
