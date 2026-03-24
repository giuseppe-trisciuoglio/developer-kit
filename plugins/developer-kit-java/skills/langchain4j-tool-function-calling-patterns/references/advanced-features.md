# Advanced Features

## Memory Context Integration

Access user context using `@ToolMemoryId`:

```java
public class PersonalizedTools {

    @Tool("Get user preferences")
    public String getPreferences(
        @ToolMemoryId String userId,
        @P("Preference category") String category) {

        return preferenceService.getPreferences(userId, category);
    }
}
```

## Dynamic Tool Provisioning

Create tools that change based on context:

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

## Immediate Return Tools

Return results immediately without full AI response:

```java
public class QuickTools {

    @Tool(value = "Get current time", returnBehavior = ReturnBehavior.IMMEDIATE)
    public String getCurrentTime() {
        return LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
    }
}
```

## Streaming with Tool Execution

```java
interface StreamingAssistant {
    TokenStream chat(String message);
}

StreamingAssistant assistant = AiServices.builder(StreamingAssistant.class)
    .streamingChatModel(streamingChatModel)
    .tools(new Tools())
    .build();

TokenStream stream = assistant.chat("What's the weather and calculate 15*8?");

stream
    .onToolExecuted(execution ->
        System.out.println("Executed: " + execution.request().name()))
    .onPartialResponse(System.out::print)
    .onComplete(response -> System.out.println("Complete!"))
    .start();
```

## Tool Specification Builder

```java
ToolSpecification toolSpec = ToolSpecification.builder()
    .name("advanced_search")
    .description("Search across multiple data sources")
    .addParameter("query", type("string"), description("Search query"))
    .addParameter("sources", type("array"), description("Data sources to search"))
    .addParameter("filters", type("object"), description("Search filters"), required(false)
    .build();
```
