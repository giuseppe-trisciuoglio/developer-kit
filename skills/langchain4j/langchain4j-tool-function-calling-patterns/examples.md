# LangChain4j Tool & Function Calling - Practical Examples

Production-ready examples for tool calling and function execution patterns with LangChain4j.

## 1. Basic Tool Calling

**Scenario**: Simple tools that LLM can invoke automatically.

```java
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.model.openai.OpenAiChatModel;

class Calculator {
    @Tool("Add two numbers together")
    int add(@P("first number") int a, @P("second number") int b) {
        return a + b;
    }

    @Tool("Multiply two numbers")
    int multiply(@P("first number") int a, @P("second number") int b) {
        return a * b;
    }

    @Tool("Divide two numbers")
    double divide(@P("dividend") double a, @P("divisor") double b) {
        if (b == 0) throw new IllegalArgumentException("Cannot divide by zero");
        return a / b;
    }
}

interface CalculatorAssistant {
    String chat(String query);
}

public class BasicToolExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.0)  // Deterministic for tools
            .build();

        var assistant = AiServices.builder(CalculatorAssistant.class)
            .chatModel(chatModel)
            .tools(new Calculator())
            .build();

        System.out.println(assistant.chat("What is 25 + 37?"));
        System.out.println(assistant.chat("Calculate 12 * 8"));
        System.out.println(assistant.chat("Divide 100 by 4"));
    }
}
```

## 2. Multiple Tool Objects

**Scenario**: LLM selecting from multiple tool domains.

```java
class WeatherService {
    @Tool("Get current weather for a city")
    String getWeather(@P("city name") String city) {
        // Simulate API call
        return "Weather in " + city + ": 22°C, Partly cloudy";
    }

    @Tool("Get weather forecast for next 5 days")
    String getForecast(@P("city name") String city) {
        return "5-day forecast for " + city + ": Sunny, Cloudy, Rainy, Sunny, Cloudy";
    }
}

class DateTimeService {
    @Tool("Get current date and time")
    String getCurrentDateTime() {
        return LocalDateTime.now().toString();
    }

    @Tool("Get day of week for a date")
    String getDayOfWeek(@P("date in YYYY-MM-DD format") String date) {
        LocalDate localDate = LocalDate.parse(date);
        return localDate.getDayOfWeek().toString();
    }
}

interface MultiToolAssistant {
    String help(String query);
}

public class MultipleToolsExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(MultiToolAssistant.class)
            .chatModel(chatModel)
            .tools(new WeatherService(), new DateTimeService())
            .build();

        System.out.println(assistant.help("What's the weather in Paris?"));
        System.out.println(assistant.help("What time is it?"));
        System.out.println(assistant.help("What day is 2024-12-25?"));
    }
}
```

## 3. Tool with Complex Return Types

**Scenario**: Tools returning structured objects.

```java
class UserRecord {
    public String id;
    public String name;
    public String email;
    public LocalDate createdDate;

    public UserRecord(String id, String name, String email, LocalDate createdDate) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.createdDate = createdDate;
    }
}

class UserService {
    @Tool("Look up user information by ID")
    UserRecord getUserById(@P("user ID") String userId) {
        // Simulate database lookup
        return new UserRecord(userId, "John Doe", "john@example.com", LocalDate.now());
    }

    @Tool("List all users (returns top 10)")
    List<UserRecord> listUsers() {
        return Arrays.asList(
            new UserRecord("1", "Alice", "alice@example.com", LocalDate.now()),
            new UserRecord("2", "Bob", "bob@example.com", LocalDate.now())
        );
    }

    @Tool("Search users by name pattern")
    List<UserRecord> searchByName(@P("name pattern") String pattern) {
        return Arrays.asList(
            new UserRecord("1", "John Smith", "john.smith@example.com", LocalDate.now())
        );
    }
}

interface UserAssistant {
    String answer(String query);
}

public class ComplexReturnTypeExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(UserAssistant.class)
            .chatModel(chatModel)
            .tools(new UserService())
            .build();

        System.out.println(assistant.answer("Who is user 123?"));
        System.out.println(assistant.answer("List all users"));
        System.out.println(assistant.answer("Find users named John"));
    }
}
```

## 4. Error Handling in Tools

**Scenario**: Graceful handling of tool errors.

```java
class DatabaseService {
    @Tool("Execute read query on database")
    String queryDatabase(@P("SQL query") String query) {
        // Validate query is SELECT only
        if (!query.trim().toUpperCase().startsWith("SELECT")) {
            throw new IllegalArgumentException("Only SELECT queries allowed");
        }
        return "Query result: 42 rows returned";
    }

    @Tool("Get user count by status")
    int getUserCount(@P("status") String status) {
        if (!Arrays.asList("active", "inactive", "pending").contains(status)) {
            throw new IllegalArgumentException("Invalid status: " + status);
        }
        return 150;
    }
}

interface ResilientAssistant {
    String execute(String command);
}

public class ErrorHandlingExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(ResilientAssistant.class)
            .chatModel(chatModel)
            .tools(new DatabaseService())
            
            // Handle tool execution errors
            .toolExecutionErrorHandler((toolCall, exception) -> {
                System.err.println("Tool error in " + toolCall.name() + ": " + exception.getMessage());
                return "Error: " + exception.getMessage();
            })
            
            // Handle malformed tool arguments
            .toolArgumentsErrorHandler((toolCall, exception) -> {
                System.err.println("Invalid arguments for " + toolCall.name());
                return "Invalid arguments";
            })
            
            .build();

        System.out.println(assistant.execute("Execute SELECT * FROM users"));
        System.out.println(assistant.execute("How many active users?"));
    }
}
```

## 5. Streaming Tool Execution

**Scenario**: Tools called during streaming responses.

```java
import dev.langchain4j.service.TokenStream;

interface StreamingToolAssistant {
    TokenStream execute(String command);
}

public class StreamingToolsExample {
    public static void main(String[] args) {
        var streamingModel = OpenAiStreamingChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(StreamingToolAssistant.class)
            .streamingChatModel(streamingModel)
            .tools(new Calculator())
            .build();

        assistant.execute("Calculate (5 + 3) * 4 and explain")
            .onNext(token -> System.out.print(token))
            .onToolExecuted(execution -> 
                System.out.println("\n[Tool: " + execution.request().name() + "]"))
            .onCompleteResponse(response -> 
                System.out.println("\n--- Complete ---"))
            .onError(error -> System.err.println("Error: " + error))
            .start();

        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

## 6. Dynamic Tool Provider

**Scenario**: Select tools dynamically based on query context.

```java
interface DynamicToolAssistant {
    String help(String query);
}

class MathTools {
    @Tool("Add two numbers")
    int add(@P("a") int a, @P("b") int b) { return a + b; }
}

class TextTools {
    @Tool("Convert text to uppercase")
    String toUpper(@P("text") String text) { return text.toUpperCase(); }

    @Tool("Convert text to lowercase")
    String toLower(@P("text") String text) { return text.toLowerCase(); }
}

public class DynamicToolProviderExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(DynamicToolAssistant.class)
            .chatModel(chatModel)
            
            // Provide tools dynamically
            .toolProvider(context -> {
                if (context.userMessage().contains("math") || context.userMessage().contains("calculate")) {
                    return Collections.singletonList(new MathTools());
                } else if (context.userMessage().contains("text") || context.userMessage().contains("convert")) {
                    return Collections.singletonList(new TextTools());
                }
                return Collections.emptyList();
            })
            
            .build();

        System.out.println(assistant.help("Calculate 25 + 37"));
        System.out.println(assistant.help("Convert HELLO to lowercase"));
    }
}
```

## 7. Tool with Memory Context

**Scenario**: Tools accessing conversation memory.

```java
class ContextAwareDataService {
    private Map<String, String> userPreferences = new HashMap<>();

    @Tool("Save user preference")
    void savePreference(@P("key") String key, @P("value") String value) {
        userPreferences.put(key, value);
        System.out.println("Saved: " + key + " = " + value);
    }

    @Tool("Get user preference")
    String getPreference(@P("key") String key) {
        return userPreferences.getOrDefault(key, "Not found");
    }

    @Tool("List all preferences")
    Map<String, String> listPreferences() {
        return new HashMap<>(userPreferences);
    }
}

interface ContextAssistant {
    String chat(String message);
}

public class ToolMemoryExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var dataService = new ContextAwareDataService();

        var assistant = AiServices.builder(ContextAssistant.class)
            .chatModel(chatModel)
            .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
            .tools(dataService)
            .build();

        System.out.println(assistant.chat("Remember that I like Java"));
        System.out.println(assistant.chat("What do I like?"));
        System.out.println(assistant.chat("Also remember I use Spring Boot"));
        System.out.println(assistant.chat("What are all my preferences?"));
    }
}
```

## 8. Stateful Tool Execution

**Scenario**: Tools that maintain state across calls.

```java
class StatefulCounter {
    private int count = 0;

    @Tool("Increment counter by 1")
    int increment() {
        return ++count;
    }

    @Tool("Decrement counter by 1")
    int decrement() {
        return --count;
    }

    @Tool("Get current counter value")
    int getCount() {
        return count;
    }

    @Tool("Reset counter to zero")
    void reset() {
        count = 0;
    }
}

interface CounterAssistant {
    String interact(String command);
}

public class StatefulToolExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var counter = new StatefulCounter();

        var assistant = AiServices.builder(CounterAssistant.class)
            .chatModel(chatModel)
            .tools(counter)
            .build();

        System.out.println(assistant.interact("Increment the counter"));
        System.out.println(assistant.interact("Increment again"));
        System.out.println(assistant.interact("What's the current count?"));
        System.out.println(assistant.interact("Reset the counter"));
        System.out.println(assistant.interact("Decrement"));
    }
}
```

## 9. Tool Validation and Authorization

**Scenario**: Validate and authorize tool execution.

```java
class SecureDataService {
    @Tool("Get sensitive data")
    String getSensitiveData(@P("data_id") String dataId) {
        // This should normally check authorization
        if (!dataId.matches("^[A-Z][0-9]{3}$")) {
            throw new IllegalArgumentException("Invalid data ID format");
        }
        return "Sensitive data for " + dataId;
    }

    @Tool("Delete data (requires authorization)")
    void deleteData(@P("data_id") String dataId) {
        if (!dataId.matches("^[A-Z][0-9]{3}$")) {
            throw new IllegalArgumentException("Invalid data ID");
        }
        System.out.println("Data " + dataId + " deleted");
    }
}

interface SecureAssistant {
    String execute(String command);
}

public class AuthorizationExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(SecureAssistant.class)
            .chatModel(chatModel)
            .tools(new SecureDataService())
            
            .toolExecutionErrorHandler((request, exception) -> {
                System.err.println("Authorization/validation failed: " + exception.getMessage());
                return "Operation denied: " + exception.getMessage();
            })
            
            .build();

        System.out.println(assistant.execute("Get data A001"));
        System.out.println(assistant.execute("Get data invalid"));
    }
}
```

## 10. Advanced: Tool Result Processing

**Scenario**: Process and transform tool results before returning to LLM.

```java
class DataService {
    @Tool("Fetch user data from API")
    String fetchUserData(@P("user_id") String userId) {
        return "User{id=" + userId + ", name=John, role=Admin}";
    }
}

interface ProcessingAssistant {
    String answer(String query);
}

public class ToolResultProcessingExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(ProcessingAssistant.class)
            .chatModel(chatModel)
            .tools(new DataService())
            
            // Can add interceptors for tool results if needed
            // This would be in a future LangChain4j version
            
            .build();

        System.out.println(assistant.answer("What is the role of user 123?"));
    }
}
```

## Best Practices

1. **Clear Descriptions**: Write detailed @Tool descriptions for LLM context
2. **Strong Typing**: Use specific types (int, String) instead of generic Object
3. **Parameter Descriptions**: Use @P with clear descriptions of expected formats
4. **Error Handling**: Always implement error handlers for graceful failures
5. **Temperature**: Set temperature=0 for deterministic tool selection
6. **Validation**: Validate all parameters before execution
7. **Logging**: Log tool calls and results for debugging
8. **State Management**: Keep tools stateless or manage state explicitly
9. **Timeout**: Set timeouts on long-running tools
10. **Authorization**: Validate authorization before executing sensitive operations
