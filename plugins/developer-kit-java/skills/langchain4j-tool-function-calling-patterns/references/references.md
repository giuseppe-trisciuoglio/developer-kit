# LangChain4j Tool & Function Calling - API References

Complete API reference for tool and function calling with LangChain4j.

## Tool Definition

### @Tool Annotation

**Purpose**: Mark methods that LLM can call.

```java
@Tool(value = "Description of what this tool does")
ReturnType methodName(ParameterType param) {
    // Implementation
}

// Examples
@Tool("Add two numbers together")
int add(int a, int b) { return a + b; }

@Tool("Query database for user information")
User getUserById(String userId) { ... }

@Tool("Send email to recipient")
void sendEmail(String to, String subject, String body) { ... }
```

### @P Annotation

**Purpose**: Describe tool parameters for LLM understanding.

```java
@Tool("Transfer money between accounts")
void transfer(
    @P("source account ID") String fromAccount,
    @P("destination account ID") String toAccount,
    @P("amount in dollars") double amount
) { ... }
```

## Builder Configuration

### AiServices Builder Extensions for Tools

```java
AiServices.builder(AssistantInterface.class)
    
    // Register tool objects
    .tools(Object... tools)                    // Multiple tool objects
    .tools(new Calculator())                   // Single tool
    .tools(new Calculator(), new DataService()) // Multiple
    
    // Dynamic tool provider
    .toolProvider(ToolProvider toolProvider)
    
    // Error handlers
    .toolExecutionErrorHandler(ToolExecutionErrorHandler)
    .toolArgumentsErrorHandler(ToolArgumentsErrorHandler)
    
    .build();
```

## Error Handlers

### ToolExecutionErrorHandler

**Purpose**: Handle errors during tool execution.

```java
@FunctionalInterface
interface ToolExecutionErrorHandler {
    String handle(ToolExecutionRequest request, Throwable exception);
}

// Usage
.toolExecutionErrorHandler((request, exception) -> {
    logger.error("Tool " + request.name() + " failed", exception);
    return "Error executing " + request.name() + ": " + exception.getMessage();
})
```

### ToolArgumentsErrorHandler

**Purpose**: Handle errors in tool argument parsing/validation.

```java
@FunctionalInterface
interface ToolArgumentsErrorHandler {
    String handle(ToolExecutionRequest request, Throwable exception);
}

// Usage
.toolArgumentsErrorHandler((request, exception) -> {
    logger.warn("Invalid arguments for " + request.name());
    return "Invalid arguments provided";
})
```

## Tool Provider

### ToolProvider Interface

**Purpose**: Dynamically select tools based on context.

```java
@FunctionalInterface
interface ToolProvider {
    List<Object> getTools(ToolProviderContext context);
}

// Context available
interface ToolProviderContext {
    UserMessage userMessage();
    List<ChatMessage> messages();
}
```

### Dynamic Tool Selection

```java
.toolProvider(context -> {
    String message = context.userMessage().singleText();
    
    if (message.contains("calculate")) {
        return Arrays.asList(new Calculator());
    } else if (message.contains("weather")) {
        return Arrays.asList(new WeatherService());
    } else {
        return Collections.emptyList();
    }
})
```

## Tool Execution Models

### ToolExecutionRequest

```java
interface ToolExecutionRequest {
    String name();                // Tool name from @Tool
    String description();         // Tool description
    Map<String, String> arguments(); // Tool arguments
}
```

### ToolExecution (for streaming)

```java
class ToolExecution {
    ToolExecutionRequest request();  // The tool being executed
    String result();                 // Execution result
}
```

## Return Types

### Supported Return Types

**Primitives**:
```java
@Tool("Add numbers")
int add(@P("a") int x, @P("b") int y) { return x + y; }

@Tool("Compare values")
boolean isGreater(@P("a") int x, @P("b") int y) { return x > y; }

@Tool("Get temperature")
double getTemp() { return 22.5; }
```

**String**:
```java
@Tool("Get greeting")
String greet(@P("name") String name) { return "Hello " + name; }
```

**Objects (will be converted to String)**:
```java
@Tool("Get user")
User getUser(@P("id") String id) { return new User(id); }

@Tool("Get user list")
List<User> listUsers() { return userService.getAll(); }
```

**Collections**:
```java
@Tool("Search documents")
List<Document> search(@P("query") String q) { return results; }

@Tool("Get key-value pairs")
Map<String, String> getConfig() { return config; }
```

**Void**:
```java
@Tool("Send notification")
void notify(@P("message") String msg) { 
    notificationService.send(msg);
}
```

## Parameter Types

### Supported Parameter Types

**Primitives**:
```java
int, long, float, double, boolean, byte, short, char
```

**Strings and wrapper types**:
```java
String, Integer, Long, Float, Double, Boolean
```

**Collections**:
```java
List<String>, Set<Integer>, Collection<T>
```

**Custom objects** (must have toString() that's meaningful):
```java
@Tool("Process data")
void process(CustomData data) { ... }
```

**Dates and times**:
```java
@Tool("Get events for date")
List<Event> getEvents(LocalDate date) { ... }

@Tool("Schedule for time")
void schedule(LocalDateTime when) { ... }
```

## Annotation Combinations

### Complete Tool Definition

```java
class DataService {
    
    // Basic tool
    @Tool("Get user information")
    User getUser(@P("user ID") String userId) { ... }
    
    // Tool with multiple params
    @Tool("Search users by criteria")
    List<User> search(
        @P("first name") String firstName,
        @P("last name") String lastName,
        @P("department") String dept
    ) { ... }
    
    // Tool returning collection
    @Tool("List all active users")
    List<User> getActiveUsers() { ... }
    
    // Tool with void return
    @Tool("Archive old records")
    void archiveOldRecords(@P("older than days") int days) { ... }
    
    // Tool with complex return
    @Tool("Get detailed report")
    Map<String, Object> generateReport(@P("month") int month) { ... }
}
```

## Best Practices for API Usage

### Tool Design

1. **Descriptive Names**: Use clear, actionable names
```java
// Good
@Tool("Get current weather for a city")
String getWeather(String city) { ... }

// Avoid
@Tool("Get info")
String getInfo(String x) { ... }
```

2. **Parameter Descriptions**: Be specific about formats
```java
// Good
@Tool("Calculate date difference")
long daysBetween(
    @P("start date in YYYY-MM-DD format") String start,
    @P("end date in YYYY-MM-DD format") String end
) { ... }

// Avoid
@Tool("Calculate difference")
long calculate(@P("date1") String d1, @P("date2") String d2) { ... }
```

3. **Appropriate Return Types**: Return what LLM can use
```java
// Good - LLM can interpret
@Tool("Get user role")
String getUserRole(String userId) { return "admin"; }

// Avoid - hard to parse
@Tool("Get user info")
User getUser(String id) { ... } // Will convert to toString()
```

4. **Error Messages**: Provide actionable errors
```java
.toolExecutionErrorHandler((request, exception) -> {
    if (exception instanceof IllegalArgumentException) {
        return "Invalid argument: " + exception.getMessage();
    }
    return "Error executing " + request.name();
})
```

### Common Patterns

**Validation Pattern**:
```java
@Tool("Create user")
String createUser(@P("email") String email) {
    if (!email.contains("@")) {
        throw new IllegalArgumentException("Invalid email format");
    }
    return "User created: " + email;
}
```

**Batch Pattern**:
```java
@Tool("Bulk delete users")
String deleteUsers(@P("user IDs comma-separated") String userIds) {
    List<String> ids = Arrays.asList(userIds.split(","));
    return "Deleted " + ids.size() + " users";
}
```

**Async Pattern** (synchronous wrapper):
```java
@Tool("Submit async task")
String submitTask(@P("task name") String name) {
    // Internally async, but returns immediately
    taskExecutor.submitAsync(name);
    return "Task " + name + " submitted";
}
```

## Integration with AiServices

### Complete Setup

```java
interface Assistant {
    String execute(String command);
}

public class Setup {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.0)  // Deterministic
            .build();

        var assistant = AiServices.builder(Assistant.class)
            .chatModel(chatModel)
            
            // Register tools
            .tools(
                new Calculator(),
                new WeatherService(),
                new UserDataService()
            )
            
            // Error handling
            .toolExecutionErrorHandler((request, exception) -> {
                System.err.println("Tool error: " + exception.getMessage());
                return "Tool failed";
            })
            
            // Optional: memory for context
            .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
            
            .build();

        // Use the assistant
        String result = assistant.execute("What is the weather in Paris?");
        System.out.println(result);
    }
}
```

## Resource Links

- [LangChain4j Tools Documentation](https://docs.langchain4j.dev/features/tools)
- [Agent Tutorial](https://docs.langchain4j.dev/tutorials/agents)
- [GitHub Examples](https://github.com/langchain4j/langchain4j-examples)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
