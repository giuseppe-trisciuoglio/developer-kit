---
name: langchain4j-tool-function-calling-patterns
description: Provides tool and function calling patterns with LangChain4j. Handles defining tools, function calls, and LLM agent integration. Use when building agentic applications that interact with tools.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
---

# LangChain4j Tool & Function Calling Patterns

Define tools and enable AI agents to interact with external systems, APIs, and services using LangChain4j's annotation-based and programmatic tool system.

## Overview

LangChain4j's tool system enables AI agents to execute external functions through declarative annotations and programmatic interfaces. Tools are defined using the `@Tool` annotation and automatically registered with AI services, allowing LLMs to perform actions beyond text generation such as database queries, API calls, and calculations.

## When to Use This Skill

Use this skill when:
- Building AI applications that need to interact with external APIs and services
- Creating AI assistants that can perform actions beyond text generation
- Implementing AI systems that need access to real-time data (weather, stocks, etc.)
- Building multi-agent systems where agents can use specialized tools
- Creating AI applications with database read/write capabilities
- Implementing AI systems that need to integrate with existing business systems
- Building context-aware AI applications where tool availability depends on user state
- Developing production AI applications that require robust error handling and monitoring

## Instructions

Follow these steps to implement tools with LangChain4j:

### 1. Define Tool Methods
Create methods annotated with `@Tool` in a class. Use `@P` for parameter descriptions.

### 2. Configure Parameter Descriptions
Use `@P` annotation for clear parameter descriptions that help the LLM understand how to call the tool.

### 3. Register Tools with AI Service
Connect tools to an AI service using the AiServices builder.

### 4. Handle Tool Execution Errors
Implement error handling for tool failures.

### 5. Monitor Tool Usage
Track tool calls for debugging and analytics.

## Quick Reference

| Annotation/Concept | Purpose |
|-------------------|---------|
| `@Tool` | Marks method as executable tool |
| `@P` | Describes tool parameters |
| `@ToolMemoryId` | Injects user context ID |
| `AiServices.builder()` | Builds AI service with tools |
| `ToolProvider` | Dynamic tool provisioning |
| `ReturnBehavior.IMMEDIATE` | Return without AI response |

## Examples

### Basic Tool Definition

```java
public class WeatherTools {
    @Tool("Get current weather for a city")
    public String getWeather(
        @P("City name") String city,
        @P("Temperature unit (celsius or fahrenheit)", required = false) String unit) {
        return weatherService.getWeather(city, unit);
    }
}
```

### Register Tools with AI Service

```java
MathAssistant assistant = AiServices.builder(MathAssistant.class)
    .chatModel(chatModel)
    .tools(new Calculator(), new WeatherService())
    .build();
```

### Error Handling

```java
AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ExternalServiceTools())
    .toolExecutionErrorHandler((request, exception) -> {
        log.error("Tool execution failed: {}", exception.getMessage());
        return "An error occurred while processing your request";
    })
    .build();
```

See [references/setup-configuration.md](references/setup-configuration.md) for complete setup examples and [references/integration-examples.md](references/integration-examples.md) for more integration patterns.

## Best Practices

### Tool Design Guidelines
1. **Descriptive Names**: Use clear, actionable tool names
2. **Parameter Validation**: Validate inputs before processing
3. **Error Messages**: Provide meaningful error messages
4. **Return Types**: Use appropriate return types that LLMs can understand
5. **Performance**: Avoid blocking operations in tools

### Security Considerations
1. **Permission Checks**: Validate user permissions before tool execution
2. **Input Sanitization**: Sanitize all tool inputs
3. **Audit Logging**: Log tool usage for security monitoring
4. **Rate Limiting**: Implement rate limiting for external APIs

### Performance Optimization
1. **Concurrent Execution**: Use `executeToolsConcurrently()` for independent tools
2. **Caching**: Cache frequently accessed data
3. **Monitoring**: Monitor tool performance and error rates
4. **Resource Management**: Handle external service timeouts gracefully

## Common Issues and Solutions

### Tool Not Found
**Problem**: LLM calls tools that don't exist
**Solution**: Implement hallucination handler:
```java
.hallucinatedToolNameStrategy(request -> {
    return ToolExecutionResultMessage.from(request,
        "Error: Tool '" + request.name() + "' does not exist");
})
```

### Parameter Validation Errors
**Problem**: Tools receive invalid parameters
**Solution**: Add input validation and error handlers:
```java
.toolArgumentsErrorHandler((error, context) -> {
    return ToolErrorHandlerResult.text("Invalid arguments: " + error.getMessage());
})
```

### Performance Issues
**Problem**: Tools are slow or timeout
**Solution**: Use concurrent execution and resilience patterns:
```java
.executeToolsConcurrently(Executors.newFixedThreadPool(5))
.toolExecutionTimeout(Duration.ofSeconds(30))
```

See [references/error-handling.md](references/error-handling.md) for complete error handling patterns.

## Related Skills

- `langchain4j-ai-services-patterns`
- `langchain4j-rag-implementation-patterns`
- `langchain4j-spring-boot-integration`

## References

### Setup and Configuration
- **[references/setup-configuration.md](references/setup-configuration.md)** - Basic tool registration, builder configuration, chat model setup

### Core Patterns
- **[references/core-patterns.md](references/core-patterns.md)** - Basic tool definition, parameter descriptions, complex types, return types

### Advanced Features
- **[references/advanced-features.md](references/advanced-features.md)** - Memory context integration, dynamic tool provisioning, immediate return tools, streaming

### Integration and Error Handling
- **[references/error-handling.md](references/error-handling.md)** - Tool error handling, resilience patterns, timeout handling, monitoring
- **[references/integration-examples.md](references/integration-examples.md)** - Complete integration examples with databases, REST APIs, context-aware tools

## Constraints and Warnings

- Tools with side effects should have clear descriptions warning about potential impacts
- AI models may call tools in unexpected orders or with unexpected parameters
- Tool execution can be expensive; implement rate limiting and timeout handling
- Never pass sensitive data (API keys, passwords) in tool descriptions or responses
- Large tool sets can confuse AI models; consider using dynamic tool providers
- Tool execution errors should be handled gracefully; never expose stack traces to AI models
- Be cautious with tools that modify data; AI models may call them multiple times
- Parameter descriptions should be precise; vague descriptions lead to incorrect tool usage
- Tools with long execution times should implement timeout handling
- Test tools thoroughly before exposing them to AI models to prevent unexpected behavior
