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

The Model Context Protocol (MCP) is a standardized protocol for connecting AI applications to external data sources and tools. Spring AI provides native support for building MCP servers that expose Spring components as callable tools, resources, and prompt templates for AI models. This skill covers tools (`@McpTool`), resources, prompts (`@PromptTemplate`), transport (stdio, HTTP, SSE), security, and testing.

## When to Use

- AI applications requiring external tool integration with Spring AI
- Enterprise MCP servers with Spring ecosystem integration
- Function calling servers with Spring AI's declarative patterns
- Prompt template servers for standardized AI interactions
- Production-ready MCP servers with Spring Security and monitoring
- Microservices that expose AI capabilities via MCP protocol

## Instructions

### 1. Project Setup

1. Add Spring AI MCP dependencies to your `pom.xml` or `build.gradle`
2. Configure the AI model (OpenAI, Anthropic, etc.) in `application.properties`
3. Enable MCP server with `@EnableMcpServer` annotation

### 2. Define Tools

1. Create a Spring component class (`@Component`)
2. Annotate methods with `@McpTool(description = "...")`
3. Use `@McpToolParam` to document parameters for AI understanding
4. Implement business logic with proper error handling

### 3. Create Prompt Templates

1. Create prompt template components with `@PromptTemplate`
2. Define parameters with `@PromptParam`
3. Return `Prompt` objects with system and user messages

### 4. Configure Transport

1. Choose transport type: `stdio`, `http`, or `sse`
2. Configure transport properties in `application.yml`
3. Set up CORS if using HTTP/SSE

### 5. Add Security

1. Implement Spring Security configuration
2. Create tool filters for role-based access control
3. Add input validation to prevent injection attacks

### 6. Testing

1. Write unit tests for individual tools
2. Create integration tests for MCP endpoints
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

**Maven:**
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

**Note:** Use the Spring AI BOM to manage versions:
```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>1.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### MCP Architecture

```
AI Application <-> MCP Client <-> Spring AI <-> MCP Server <-> Spring Services
```

Key Spring AI Components:
- **@McpTool**: Declares methods as callable functions for AI models
- **@McpToolParam**: Documents parameter purposes for AI understanding
- **@PromptTemplate**: Defines reusable prompt patterns
- **FunctionCallback**: Low-level function calling integration

## Best Practices

1. **Use Declarative Annotations**: Prefer `@McpTool` and `@PromptTemplate` over manual registration
2. **Keep Tools Focused**: Each tool should do one thing well
3. **Document Parameters**: Use `@McpToolParam` with clear descriptions
4. **Return Structured Data**: Use records or DTOs for return values
5. **Implement Input Validation**: Never trust AI-generated parameters without validation
6. **Use Authorization**: Implement role-based access control with Spring Security
7. **Rate Limiting**: Implement rate limiting for expensive operations
8. **Use Caching**: Cache results of expensive operations with `@Cacheable`
9. **Design for Idempotency**: Tools should be idempotent when possible
10. **Handle Large Responses**: Consider pagination or summary options

## Migration from LangChain4j

- Replace `@ToolMethod` with Spring AI `@McpTool`
- Migrate tool providers to Spring components with `@Component`
- Update configuration to Spring AI properties
- Replace LangChain4j-specific types with Spring AI equivalents

```java
// Before: LangChain4j
@ToolMethod("Get weather information")
public String getWeather(@P("city name") String city) { ... }

// After: Spring AI
@Component
public class WeatherTools {
    @McpTool(description = "Get weather information")
    public String getWeather(
            @McpToolParam(description = "City name", required = true) String city) { ... }
}
```

## Constraints and Warnings

- **Never Expose Sensitive Data** in tool descriptions, parameter names, or error messages
- **Input Validation is Mandatory**: AI models may generate malicious parameters
- **SQL Injection Prevention**: Use parameterized queries exclusively
- **Path Traversal Prevention**: Validate and normalize all file paths
- **Authorization Required**: Every tool should verify user permissions
- **Timeout Handling**: All tools must implement proper timeout handling
- **Context Window Limits**: Tool responses should be concise
- **Version Compatibility**: Spring AI API may change between versions; pin versions in production
- **Idempotency**: Non-idempotent operations should clearly document this behavior

## References

- [Implementation Patterns](./references/patterns.md) - Tool, prompt template, function callback, dynamic registration, multi-model, caching patterns
- [Configuration Reference](./references/configuration.md) - Auto-configuration, properties, custom server config
- [Security Patterns](./references/security.md) - Tool security, input validation, error handling
- [Testing Patterns](./references/testing.md) - Unit tests, integration tests, Testcontainers, security tests
- [Examples](./references/examples.md) - Complete server implementations
- [API Reference](./references/api-reference.md) - Core annotations and interfaces
- [Spring AI Documentation](https://docs.spring.io/spring-ai/reference/)
- [Model Context Protocol Specification](https://modelcontextprotocol.org/)
