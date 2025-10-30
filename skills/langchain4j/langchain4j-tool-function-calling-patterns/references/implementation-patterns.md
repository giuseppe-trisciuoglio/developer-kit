# LangChain4j Tool & Function Calling - Implementation Patterns

Comprehensive implementation patterns for tool and function calling with LangChain4j.

## Core Tool Definition Patterns

### Basic Tool Definition with @Tool Annotation

The `@Tool` annotation converts regular Java methods into tools that LLMs can discover and execute.

**Basic Tool Definition:**
```java
public class CalculatorTools {

    @Tool("Adds two given numbers")
    public double add(double a, double b) {
        return a + b;
    }

    @Tool("Multiplies two given numbers")
    public double multiply(double a, double b) {
        return a * b;
    }

    @Tool("Calculates the square root of a given number")
    public double squareRoot(double x) {
        return Math.sqrt(x);
    }

    @Tool("Calculates power of a number")
    public double power(double base, double exponent) {
        return Math.pow(base, exponent);
    }
}
```

**Advanced Tool with Parameter Descriptions:**
```java
public class WeatherService {

    @Tool("Get current weather conditions for a specific location")
    public String getCurrentWeather(@P("The name of the city or location") String location) {
        try {
            WeatherData weather = weatherClient.getCurrentWeather(location);
            return String.format("Weather in %s: %s, %.1f°C, humidity %.0f%%, wind %.1f km/h",
                    location, weather.getCondition(), weather.getTemperature(),
                    weather.getHumidity(), weather.getWindSpeed());
        } catch (Exception e) {
            return "Sorry, I couldn't retrieve weather information for " + location;
        }
    }
}
```

### Parameter Handling and Validation

**Optional Parameters:**
```java
public class DatabaseTools {

    @Tool("Search for users in the database")
    public List<User> searchUsers(
            @P("Search term for user name or email") String searchTerm,
            @P(value = "Maximum number of results to return", required = false) Integer limit,
            @P(value = "Sort order: ASC or DESC", required = false) String sortOrder) {

        int actualLimit = limit != null ? limit : 10;
        String actualSort = sortOrder != null ? sortOrder : "ASC";

        return userRepository.searchUsers(searchTerm, actualLimit, actualSort);
    }
}
```

**Complex Parameter Types:**
```java
public class OrderManagementTools {

    @Description("Customer order information")
    public static class OrderRequest {
        @Description("Customer ID who is placing the order")
        private Long customerId;

        @Description("List of items to order")
        private List<OrderItem> items;

        @Description("Shipping address for the order")
        private Address shippingAddress;

        @Description("Preferred delivery date (optional)")
        @JsonProperty(required = false)
        private LocalDate preferredDeliveryDate;
    }

    @Tool("Create a new customer order")
    public String createOrder(OrderRequest orderRequest) {
        try {
            // Validation and processing logic
            Order order = orderService.createOrder(orderRequest);
            return String.format("Order created successfully! Order ID: %s, Total: $%.2f",
                    order.getId(), order.getTotal());
        } catch (Exception e) {
            return "Failed to create order: " + e.getMessage();
        }
    }
}
```

## Memory Context Integration

### @ToolMemoryId for User Context

Tools can access conversation memory context to provide personalized and contextual responses:

```java
public class PersonalizedTools {

    @Tool("Get personalized recommendations based on user preferences")
    public String getRecommendations(@ToolMemoryId String userId,
                                   @P("Type of recommendation: books, movies, restaurants") String type) {
        UserPreferences prefs = preferenceService.getUserPreferences(userId);
        List<String> history = historyService.getSearchHistory(userId, type);
        return recommendationEngine.getRecommendations(type, prefs, history);
    }
}
```

## Dynamic Tool Provisioning

### ToolProvider for Context-Aware Tools

```java
public class DynamicToolProvider implements ToolProvider {

    @Override
    public ToolProviderResult provideTools(ToolProviderRequest request) {
        String userId = extractUserId(request);
        UserPermissions permissions = permissionService.getUserPermissions(userId);
        String userMessage = request.userMessage().singleText().toLowerCase();

        ToolProviderResult.Builder resultBuilder = ToolProviderResult.builder();

        // Always available tools
        addBasicTools(resultBuilder);

        // Conditional tools based on permissions
        if (permissions.canAccessFinancialData()) {
            addFinancialTools(resultBuilder);
        }

        if (permissions.canModifyUserData()) {
            addUserManagementTools(resultBuilder);
        }

        return resultBuilder.build();
    }
}
```

### Programmatic Tool Definition

```java
public class ProgrammaticToolsService {

    public Map<ToolSpecification, ToolExecutor> createDatabaseTools(DatabaseConfig config) {
        Map<ToolSpecification, ToolExecutor> tools = new HashMap<>();

        // Query tool
        ToolSpecification querySpec = ToolSpecification.builder()
            .name("execute_database_query")
            .description("Execute a SQL query on the database")
            .parameters(JsonObjectSchema.builder()
                .addStringProperty("query", "SQL query to execute")
                .addBooleanProperty("readOnly", "Whether this is a read-only query")
                .required("query", "readOnly")
                .build())
            .build();

        ToolExecutor queryExecutor = (request, memoryId) -> {
            Map<String, Object> args = fromJson(request.arguments());
            String query = args.get("query").toString();
            boolean readOnly = (Boolean) args.get("readOnly");
            return databaseService.executeQuery(query, readOnly);
        };

        tools.put(querySpec, queryExecutor);
        return tools;
    }
}
```

## AI Services as Tools

AI Services can be used as tools by other AI Services, enabling hierarchical architectures:

```java
// Specialized Expert Services
interface DataAnalysisExpert {
    @UserMessage("You are a data analysis expert. Analyze this data and provide insights: {{data}}")
    @Tool("Expert data analysis and insights")
    String analyzeData(@V("data") String data);
}

// Router Agent that delegates to experts
interface ExpertRouter {
    @UserMessage("""
        Analyze the user request and determine which expert(s) should handle it:
        - Use the data analysis expert for data-related questions
        - Use the security expert for security-related concerns

        User request: {{it}}
        """)
    String routeToExperts(String request);
}

@Service
public class ExpertConsultationService {
    public ExpertConsultationService(ChatModel chatModel) {
        // Build expert services
        DataAnalysisExpert dataExpert = AiServices.create(DataAnalysisExpert.class, chatModel);

        // Build router with experts as tools
        this.router = AiServices.builder(ExpertRouter.class)
            .chatModel(chatModel)
            .tools(dataExpert)
            .build();
    }
}
```

## Advanced Tool Patterns

### Immediate Return Tools

```java
public class DirectResponseTools {

    @Tool(value = "Get current user information", returnBehavior = ReturnBehavior.IMMEDIATE)
    public String getCurrentUserInfo(@ToolMemoryId String userId) {
        User user = userService.findById(userId);
        return String.format("""
            User Information:
            Name: %s
            Email: %s
            Role: %s
            """, user.getName(), user.getEmail(), user.getRole());
    }
}
```

### Concurrent Tool Execution

```java
public class ConcurrentTools {

    @Tool("Get stock price for a company")
    public String getStockPrice(@P("Stock symbol") String symbol) {
        try {
            Thread.sleep(1000);
            return stockApiService.getPrice(symbol);
        } catch (InterruptedException e) {
            return "Error retrieving stock price";
        }
    }

    @Tool("Get company news")
    public String getCompanyNews(@P("Company symbol") String symbol) {
        // Similar implementation
    }
}

// Configure for concurrent execution
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ConcurrentTools())
    .executeToolsConcurrently() // Execute tools in parallel
    .build();
```

## Error Handling and Resilience

### Tool Execution Error Handling

```java
public class ResilientTools {

    private final CircuitBreaker circuitBreaker;
    private final RetryTemplate retryTemplate;

    @Tool("Get external data with resilience patterns")
    public String getExternalData(@P("Data source identifier") String sourceId) {
        return circuitBreaker.executeSupplier(() -> {
            return retryTemplate.execute(context -> {
                try {
                    return externalApiService.fetchData(sourceId);
                } catch (ApiException e) {
                    if (e.isRetryable()) {
                        throw e; // Will be retried
                    }
                    return "Data temporarily unavailable: " + e.getMessage();
                }
            });
        });
    }
}
```

### Graceful Degradation

```java
public class FallbackTools {

    @Tool("Get weather information with fallback providers")
    public String getWeather(@P("Location name") String location) {
        // Try primary provider first
        for (DataProvider provider : dataProviders) {
            try {
                WeatherData weather = provider.getWeather(location);
                if (weather != null) {
                    return formatWeather(weather, provider.getName());
                }
            } catch (Exception e) {
                // Continue to next provider
            }
        }
        return "Weather information is currently unavailable for " + location;
    }
}
```

## Streaming and Tool Execution

### Streaming with Tool Callbacks

```java
interface StreamingToolAssistant {
    TokenStream chat(String message);
}

StreamingToolAssistant assistant = AiServices.builder(StreamingToolAssistant.class)
    .streamingChatModel(streamingChatModel)
    .tools(new CalculatorTools(), new WeatherService())
    .build();

TokenStream stream = assistant.chat("What's the weather in Paris and calculate 15 + 27?");

stream
    .onToolExecuted(toolExecution -> {
        System.out.println("Tool executed: " + toolExecution.request().name());
        System.out.println("Result: " + toolExecution.result());
    })
    .onPartialResponse(partialResponse -> {
        System.out.print(partialResponse);
    })
    .start();
```

### Accessing Tool Execution Results

```java
interface AnalyticsAssistant {
    Result<String> analyze(String request);
}

AnalyticsAssistant assistant = AiServices.builder(AnalyticsAssistant.class)
    .chatModel(chatModel)
    .tools(new DataAnalysisTools(), new DatabaseTools())
    .build();

Result<String> result = assistant.analyze("Analyze sales data for Q4 2023");

// Access the response
String response = result.content();

// Access tool execution details
List<ToolExecution> toolExecutions = result.toolExecutions();
for (ToolExecution execution : toolExecutions) {
    System.out.println("Tool: " + execution.request().name());
    System.out.println("Duration: " + execution.duration().toMillis() + "ms");
}
```

## Complete Tool-Enabled Application

### Spring Boot Integration

```java
@RestController
@RequestMapping("/api/assistant")
@RequiredArgsConstructor
public class ToolAssistantController {

    private final ToolEnabledAssistant assistant;

    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        try {
            Result<String> result = assistant.chat(request.getUserId(), request.getMessage());

            ChatResponse response = ChatResponse.builder()
                .response(result.content())
                .toolsUsed(extractToolNames(result.toolExecutions()))
                .tokenUsage(result.tokenUsage())
                .build();

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(
                ChatResponse.error("Error processing request: " + e.getMessage())
            );
        }
    }
}

interface ToolEnabledAssistant {
    Result<String> chat(@MemoryId String userId, String message);
    List<ToolInfo> getAvailableTools(String userId);
}
```

## Performance Optimization

### Tool Performance Monitoring

```java
@Component
public class ToolPerformanceMonitor {

    @EventListener
    public void handleToolExecution(ToolExecutionEvent event) {
        // Record execution metrics
        Timer.Sample sample = Timer.start(meterRegistry);
        sample.stop(Timer.builder("tool.execution.duration")
                .tag("tool", event.getToolName())
                .tag("success", String.valueOf(event.isSuccessful()))
                .register(meterRegistry));

        // Record error rates
        if (!event.isSuccessful()) {
            meterRegistry.counter("tool.execution.errors",
                    "tool", event.getToolName(),
                    "error_type", event.getErrorType())
                .increment();
        }
    }
}
```

## Testing Framework

```java
@Component
public class ToolTestingFramework {

    public ToolValidationResult validateTool(Object toolInstance, String methodName) {
        try {
            TestAssistant testAssistant = AiServices.builder(TestAssistant.class)
                .chatModel(testChatModel)
                .tools(toolInstance)
                .build();

            String response = testAssistant.testTool(methodName);
            return ToolValidationResult.builder()
                .toolName(methodName)
                .isValid(response != null && !response.contains("Error"))
                .response(response)
                .build();

        } catch (Exception e) {
            return ToolValidationResult.builder()
                .toolName(methodName)
                .isValid(false)
                .error(e.getMessage())
                .build();
        }
    }
}
```