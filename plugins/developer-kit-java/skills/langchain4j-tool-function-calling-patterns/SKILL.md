---
name: langchain4j-tool-function-calling-patterns
description: Provides tool and function calling patterns with LangChain4j. Handles defining tools, function calls, and LLM agent integration. Use when building agentic applications that interact with tools.
category: ai-development
tags: [langchain4j, tools, function-calling, "@Tool", ToolProvider, ToolExecutor, dynamic-tools, parameter-descriptions, java]
version: 2.2.0
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
---

# LangChain4j Tool & Function Calling Patterns

Define tools and enable AI agents to interact with external systems, APIs, and services using LangChain4j's annotation-based and programmatic tool system.

## Overview

LangChain4j's tool system enables AI agents to execute external functions through declarative annotations and programmatic interfaces. Tools are defined using the `@Tool` annotation and automatically registered with AI services, allowing LLMs to perform actions beyond text generation.

## When to Use

- Building AI applications that need to interact with external APIs
- Creating AI assistants that can perform actions beyond text generation
- Building multi-agent systems with specialized tools
- Creating AI applications with database read/write capabilities
- Building context-aware AI applications with dynamic tool availability

## Instructions

### 1. Define Tool Methods

```java
public class WeatherTools {
    @Tool("Get current weather for a city")
    public String getWeather(
        @P("City name") String city,
        @P("Temperature unit", required = false) String unit) {
        return weatherService.getWeather(city, unit);
    }
}
```

### 2. Register Tools with AI Service

```java
MathAssistant assistant = AiServices.builder(MathAssistant.class)
    .chatModel(chatModel)
    .tools(new Calculator(), new WeatherService())
    .build();
```

### 3. Handle Errors

```java
AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ExternalServiceTools())
    .toolExecutionErrorHandler((request, exception) -> {
        return "An error occurred while processing your request";
    })
    .build();
```

### 4. Configure Builder Options

```java
AiServices.builder(AssistantInterface.class)
    .tools(new Calculator(), new WeatherService())
    .toolProvider(new DynamicToolProvider())
    .executeToolsConcurrently()
    .chatMemoryProvider(userId -> MessageWindowChatMemory.withMaxMessages(20))
    .build();
```

## Examples

### Dynamic Tool Provisioning

```java
public class ContextAwareToolProvider implements ToolProvider {
    @Override
    public ToolProviderResult provideTools(ToolProviderRequest request) {
        String message = request.userMessage().singleText().toLowerCase();
        var builder = ToolProviderResult.builder();
        if (message.contains("weather")) {
            builder.add(weatherToolSpec, weatherExecutor);
        }
        if (message.contains("calculate")) {
            builder.add(calcToolSpec, calcExecutor);
        }
        return builder.build();
    }
}
```

### Memory Context Integration

```java
@Tool("Get user preferences")
public String getPreferences(
    @ToolMemoryId String userId,
    @P("Preference category") String category) {
    return preferenceService.getPreferences(userId, category);
}
```

### Immediate Return Tools

```java
@Tool(value = "Get current time", returnBehavior = ReturnBehavior.IMMEDIATE)
public String getCurrentTime() {
    return LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
}
```

### Streaming with Tool Execution

```java
TokenStream stream = assistant.chat("What's the weather and calculate 15*8?");
stream
    .onToolExecuted(execution -> System.out.println("Executed: " + execution.request().name()))
    .onPartialResponse(System.out::print)
    .onComplete(response -> System.out.println("Complete!"))
    .start();
```

## Best Practices

- **Descriptive Names**: Use clear, actionable tool names
- **Parameter Validation**: Validate inputs before processing
- **Error Messages**: Provide meaningful error messages
- **Concurrent Execution**: Use `executeToolsConcurrently()` for independent tools
- **Permission Checks**: Validate user permissions before tool execution
- **Input Sanitization**: Sanitize all tool inputs
- **Rate Limiting**: Implement rate limiting for external APIs

## Constraints and Warnings

- Tools with side effects should have clear descriptions warning about impacts
- AI models may call tools in unexpected orders or with unexpected parameters
- Never pass sensitive data (API keys, passwords) in tool descriptions or responses
- Large tool sets can confuse AI models; consider dynamic tool providers
- Tool execution errors should be handled gracefully; never expose stack traces
- Be cautious with data-modifying tools; AI models may call them multiple times

## References

- [API Reference](./references/references.md)
- [Implementation Patterns](./references/implementation-patterns.md)
- [Examples](./references/examples.md)

## Related Skills

- `langchain4j-ai-services-patterns`
- `langchain4j-rag-implementation-patterns`
- `langchain4j-spring-boot-integration`
