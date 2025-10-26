---
name: langchain4j-tool-function-calling-patterns
description: Tool and function calling patterns with LangChain4j. Define tools, handle function calls, and integrate with LLM agents. Use when building agentic applications that interact with tools.
category: ai-development
tags: [langchain4j, tools, function-calling, "@Tool", ToolProvider, ToolExecutor, dynamic-tools, parameter-descriptions, java]
version: 1.0.1
context7_library: /langchain4j/langchain4j
context7_trust_score: 7.8
allowed-tools: Read, Write, Bash
---

# LangChain4j Tool & Function Calling Patterns

This skill provides comprehensive guidance for implementing tool and function calling patterns with LangChain4j, covering declarative tool definitions with annotations, dynamic tool provisioning, parameter handling, error management, and advanced integration patterns for building AI applications that can interact with external systems and APIs.

## When to Use This Skill

Use this skill when:
- Building AI applications that need to interact with external APIs and services
- Creating AI assistants that can perform actions beyond text generation
- Implementing AI systems that need access to real-time data (weather, stocks, etc.)
- Building multi-agent systems where agents can use specialized tools
- Creating AI applications with database read/write capabilities
- Implementing AI systems that need to integrate with existing business systems
- Building AI assistants that can perform calculations, data analysis, or transformations
- Creating context-aware AI applications where tool availability depends on user state
- Implementing AI systems with complex workflows requiring multiple tool interactions
- Building production AI applications that require robust error handling and monitoring

## Core Concepts

### Tool Definition with @Tool Annotation

The `@Tool` annotation is the primary way to define functions that AI models can call. It converts regular Java methods into tools that LLMs can discover and execute.

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

interface MathAssistant {
    String ask(String question);
}

MathAssistant assistant = AiServices.builder(MathAssistant.class)
    .chatModel(chatModel)
    .tools(new CalculatorTools())
    .build();

String answer = assistant.ask("What is the square root of 144 plus 5 times 3?");
// The square root of 144 is 12, and 5 times 3 is 15, so the answer is 27.
```

**Advanced Tool with Parameter Descriptions:**
```java
public class WeatherService {

    private final WeatherApiClient weatherClient;

    public WeatherService(WeatherApiClient weatherClient) {
        this.weatherClient = weatherClient;
    }

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

    @Tool("Get weather forecast for multiple days")
    public String getWeatherForecast(@P("The name of the city or location") String location,
                                   @P("Number of days for forecast (1-7)") int days) {
        if (days < 1 || days > 7) {
            return "Forecast days must be between 1 and 7";
        }

        try {
            List<DailyForecast> forecasts = weatherClient.getForecast(location, days);
            return formatForecast(location, forecasts);
        } catch (Exception e) {
            return "Sorry, I couldn't retrieve forecast information for " + location;
        }
    }

    @Tool("Get weather alerts for a location")
    public String getWeatherAlerts(@P("The name of the city or location") String location) {
        try {
            List<WeatherAlert> alerts = weatherClient.getAlerts(location);
            if (alerts.isEmpty()) {
                return "No weather alerts for " + location;
            }
            return formatAlerts(alerts);
        } catch (Exception e) {
            return "Sorry, I couldn't retrieve weather alerts for " + location;
        }
    }

    private String formatForecast(String location, List<DailyForecast> forecasts) {
        StringBuilder result = new StringBuilder();
        result.append(String.format("Weather forecast for %s:\n", location));
        for (DailyForecast forecast : forecasts) {
            result.append(String.format("%s: %s, High %.1f°C, Low %.1f°C\n",
                    forecast.getDate(), forecast.getCondition(),
                    forecast.getHighTemp(), forecast.getLowTemp()));
        }
        return result.toString();
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

    @Tool("Update user information")
    public String updateUser(
            @P("User ID to update") Long userId,
            @P(value = "New email address", required = false) String email,
            @P(value = "New phone number", required = false) String phone) {

        User user = userRepository.findById(userId);
        if (user == null) {
            return "User not found with ID: " + userId;
        }

        boolean updated = false;
        if (email != null && !email.trim().isEmpty()) {
            user.setEmail(email);
            updated = true;
        }
        if (phone != null && !phone.trim().isEmpty()) {
            user.setPhone(phone);
            updated = true;
        }

        if (updated) {
            userRepository.save(user);
            return "User " + userId + " updated successfully";
        } else {
            return "No updates provided for user " + userId;
        }
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

        // constructors, getters, setters
    }

    @Description("Individual item in an order")
    public static class OrderItem {
        @Description("Product ID or SKU")
        private String productId;

        @Description("Quantity to order")
        private Integer quantity;

        @Description("Special instructions for this item")
        @JsonProperty(required = false)
        private String specialInstructions;

        // constructors, getters, setters
    }

    @Tool("Create a new customer order")
    public String createOrder(OrderRequest orderRequest) {
        try {
            // Validate order request
            ValidationResult validation = validateOrderRequest(orderRequest);
            if (!validation.isValid()) {
                return "Order validation failed: " + validation.getErrors();
            }

            // Process the order
            Order order = orderService.createOrder(orderRequest);

            return String.format("Order created successfully! Order ID: %s, Total: $%.2f, " +
                    "Estimated delivery: %s",
                    order.getId(), order.getTotal(), order.getEstimatedDelivery());
        } catch (Exception e) {
            return "Failed to create order: " + e.getMessage();
        }
    }

    @Tool("Cancel an existing order")
    public String cancelOrder(@P("Order ID to cancel") String orderId,
                            @P("Reason for cancellation") String reason) {
        try {
            CancellationResult result = orderService.cancelOrder(orderId, reason);
            if (result.isSuccessful()) {
                return String.format("Order %s cancelled successfully. Refund amount: $%.2f",
                        orderId, result.getRefundAmount());
            } else {
                return "Cannot cancel order " + orderId + ": " + result.getReason();
            }
        } catch (Exception e) {
            return "Error cancelling order: " + e.getMessage();
        }
    }
}
```

### Memory Context with @ToolMemoryId

Tools can access conversation memory context to provide personalized and contextual responses:

```java
public class PersonalizedTools {

    private final UserPreferenceService preferenceService;
    private final ConversationHistoryService historyService;

    @Tool("Get personalized recommendations based on user preferences")
    public String getRecommendations(@ToolMemoryId String userId,
                                   @P("Type of recommendation: books, movies, restaurants") String type) {
        UserPreferences prefs = preferenceService.getUserPreferences(userId);
        List<String> history = historyService.getSearchHistory(userId, type);

        return recommendationEngine.getRecommendations(type, prefs, history);
    }

    @Tool("Save user preference")
    public String savePreference(@ToolMemoryId String userId,
                                @P("Preference category") String category,
                                @P("Preference value") String value) {
        preferenceService.savePreference(userId, category, value);
        return "Preference saved: " + category + " = " + value;
    }

    @Tool("Get user's conversation summary")
    public String getConversationSummary(@ToolMemoryId String userId) {
        return historyService.getConversationSummary(userId);
    }
}

interface PersonalizedAssistant {
    String chat(@MemoryId String userId, String message);
}

PersonalizedAssistant assistant = AiServices.builder(PersonalizedAssistant.class)
    .chatModel(chatModel)
    .tools(new PersonalizedTools(preferenceService, historyService))
    .chatMemoryProvider(userId -> MessageWindowChatMemory.withMaxMessages(20))
    .build();
```

### Dynamic Tool Provisioning

**ToolProvider for Context-Aware Tools:**
```java
public class DynamicToolProvider implements ToolProvider {

    private final UserPermissionService permissionService;
    private final ToolRegistry toolRegistry;

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

        if (permissions.isAdmin()) {
            addAdminTools(resultBuilder);
        }

        // Context-aware tools based on user message
        if (userMessage.contains("booking") || userMessage.contains("reservation")) {
            addBookingTools(resultBuilder);
        }

        if (userMessage.contains("weather") || userMessage.contains("forecast")) {
            addWeatherTools(resultBuilder);
        }

        if (userMessage.contains("email") || userMessage.contains("send")) {
            addEmailTools(resultBuilder);
        }

        return resultBuilder.build();
    }

    private void addBasicTools(ToolProviderResult.Builder builder) {
        ToolSpecification timeSpec = ToolSpecification.builder()
            .name("get_current_time")
            .description("Get the current date and time")
            .build();

        ToolExecutor timeExecutor = (request, memoryId) ->
            LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

        builder.add(timeSpec, timeExecutor);
    }

    private void addFinancialTools(ToolProviderResult.Builder builder) {
        ToolSpecification balanceSpec = ToolSpecification.builder()
            .name("get_account_balance")
            .description("Get account balance for a user")
            .parameters(JsonObjectSchema.builder()
                .addStringProperty("accountId", "Account ID to check balance")
                .required("accountId")
                .build())
            .build();

        ToolExecutor balanceExecutor = (request, memoryId) -> {
            Map<String, Object> args = fromJson(request.arguments());
            String accountId = args.get("accountId").toString();
            return financialService.getAccountBalance(accountId);
        };

        builder.add(balanceSpec, balanceExecutor);
    }

    private String extractUserId(ToolProviderRequest request) {
        // Extract user ID from request metadata
        return request.userMessage().metadata().getString("userId");
    }
}

// Usage
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .toolProvider(new DynamicToolProvider(permissionService, toolRegistry))
    .build();
```

**Programmatic Tool Definition:**
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

            if (!readOnly && !hasWritePermission(memoryId)) {
                return "Write access denied for this user";
            }

            return databaseService.executeQuery(query, readOnly);
        };

        tools.put(querySpec, queryExecutor);

        // Schema information tool
        ToolSpecification schemaSpec = ToolSpecification.builder()
            .name("get_table_schema")
            .description("Get schema information for a database table")
            .parameters(JsonObjectSchema.builder()
                .addStringProperty("tableName", "Name of the table")
                .required("tableName")
                .build())
            .build();

        ToolExecutor schemaExecutor = (request, memoryId) -> {
            Map<String, Object> args = fromJson(request.arguments());
            String tableName = args.get("tableName").toString();
            return databaseService.getTableSchema(tableName);
        };

        tools.put(schemaSpec, schemaExecutor);

        return tools;
    }

    private boolean hasWritePermission(Object memoryId) {
        return permissionService.hasPermission(memoryId.toString(), "database.write");
    }
}
```

### AI Services as Tools

AI Services can be used as tools by other AI Services, enabling hierarchical and specialized agent architectures:

```java
// Specialized Expert Services
interface DataAnalysisExpert {
    @UserMessage("You are a data analysis expert. Analyze this data and provide insights: {{data}}")
    @Tool("Expert data analysis and insights")
    String analyzeData(@V("data") String data);
}

interface SecurityExpert {
    @UserMessage("You are a cybersecurity expert. Assess this security concern: {{concern}}")
    @Tool("Expert security assessment and recommendations")
    String assessSecurity(@V("concern") String concern);
}

interface ComplianceExpert {
    @UserMessage("You are a compliance expert. Review this for regulatory compliance: {{content}}")
    @Tool("Expert compliance review and guidance")
    String reviewCompliance(@V("content") String content);
}

// Router Agent that delegates to experts
interface ExpertRouter {
    @UserMessage("""
        Analyze the user request and determine which expert(s) should handle it:
        - Use the data analysis expert for data-related questions
        - Use the security expert for security-related concerns
        - Use the compliance expert for regulatory/compliance questions

        You can use multiple experts if the question spans multiple domains.

        User request: {{it}}
        """)
    String routeToExperts(String request);
}

@Service
public class ExpertConsultationService {

    private final ExpertRouter router;

    public ExpertConsultationService(ChatModel chatModel) {
        // Build expert services
        DataAnalysisExpert dataExpert = AiServices.create(DataAnalysisExpert.class, chatModel);
        SecurityExpert securityExpert = AiServices.create(SecurityExpert.class, chatModel);
        ComplianceExpert complianceExpert = AiServices.create(ComplianceExpert.class, chatModel);

        // Build router with experts as tools
        this.router = AiServices.builder(ExpertRouter.class)
            .chatModel(chatModel)
            .tools(dataExpert, securityExpert, complianceExpert)
            .build();
    }

    public String consultExperts(String request) {
        return router.routeToExperts(request);
    }
}
```

### Advanced Tool Patterns

**Immediate Return Tools:**
```java
public class DirectResponseTools {

    @Tool(value = "Get current user information", returnBehavior = ReturnBehavior.IMMEDIATE)
    public String getCurrentUserInfo(@ToolMemoryId String userId) {
        User user = userService.findById(userId);
        if (user == null) {
            return "User not found";
        }

        return String.format("""
            User Information:
            Name: %s
            Email: %s
            Role: %s
            Last Login: %s
            """, user.getName(), user.getEmail(), user.getRole(), user.getLastLogin());
    }

    @Tool(value = "Generate user report", returnBehavior = ReturnBehavior.IMMEDIATE)
    public String generateUserReport(@P("Report type: summary, detailed, activity") String reportType,
                                   @ToolMemoryId String userId) {
        return reportService.generateUserReport(userId, reportType);
    }
}

// Usage with Result wrapper to access tool executions
interface ReportAssistant {
    Result<String> getReport(String request);
}

ReportAssistant assistant = AiServices.builder(ReportAssistant.class)
    .chatModel(chatModel)
    .tools(new DirectResponseTools())
    .build();

Result<String> result = assistant.getReport("Show me my user information");
String response = result.content(); // Direct tool response
List<ToolExecution> executions = result.toolExecutions();
```

**Concurrent Tool Execution:**
```java
public class ConcurrentTools {

    @Tool("Get stock price for a company")
    public String getStockPrice(@P("Stock symbol") String symbol) {
        // Simulates API call that takes time
        try {
            Thread.sleep(1000);
            return stockApiService.getPrice(symbol);
        } catch (InterruptedException e) {
            return "Error retrieving stock price";
        }
    }

    @Tool("Get company news")
    public String getCompanyNews(@P("Company symbol") String symbol) {
        try {
            Thread.sleep(800);
            return newsApiService.getNews(symbol);
        } catch (InterruptedException e) {
            return "Error retrieving news";
        }
    }

    @Tool("Get analyst ratings")
    public String getAnalystRatings(@P("Stock symbol") String symbol) {
        try {
            Thread.sleep(1200);
            return ratingsApiService.getRatings(symbol);
        } catch (InterruptedException e) {
            return "Error retrieving ratings";
        }
    }
}

// Configure for concurrent execution
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ConcurrentTools())
    .executeToolsConcurrently() // Execute tools in parallel
    .build();

// Or with custom executor
Executor customExecutor = Executors.newFixedThreadPool(5);
Assistant assistant2 = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ConcurrentTools())
    .executeToolsConcurrently(customExecutor)
    .build();
```

### Error Handling and Resilience

**Tool Execution Error Handling:**
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
                    } else {
                        return "Data temporarily unavailable: " + e.getMessage();
                    }
                }
            });
        });
    }

    @Tool("Validate and process user input")
    public String processUserInput(@P("User input to process") String input) {
        // Input validation
        ValidationResult validation = inputValidator.validate(input);
        if (!validation.isValid()) {
            return "Invalid input: " + validation.getErrors().stream()
                .collect(Collectors.joining(", "));
        }

        try {
            return businessLogicService.processInput(input);
        } catch (BusinessException e) {
            log.error("Business logic error: {}", e.getMessage(), e);
            return "Processing failed: " + e.getUserFriendlyMessage();
        } catch (Exception e) {
            log.error("Unexpected error: {}", e.getMessage(), e);
            return "An unexpected error occurred. Please try again later.";
        }
    }
}

// Configure error handling at service level
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ResilientTools())
    .toolExecutionErrorHandler((error, context) -> {
        log.error("Tool execution error: {}", error.getMessage(), error);
        return ToolErrorHandlerResult.text("Tool temporarily unavailable: " + error.getMessage());
    })
    .toolArgumentsErrorHandler((error, context) -> {
        log.warn("Tool arguments error: {}", error.getMessage());
        return ToolErrorHandlerResult.text("Invalid tool arguments: " + error.getMessage());
    })
    .hallucinatedToolNameStrategy(request -> {
        log.warn("Hallucinated tool: {}", request.name());
        return ToolExecutionResultMessage.from(request,
            "Error: Tool '" + request.name() + "' does not exist");
    })
    .build();
```

**Graceful Degradation:**
```java
public class FallbackTools {

    private final List<DataProvider> dataProviders;

    @Tool("Get weather information with fallback providers")
    public String getWeather(@P("Location name") String location) {
        for (DataProvider provider : dataProviders) {
            try {
                WeatherData weather = provider.getWeather(location);
                if (weather != null) {
                    return formatWeather(weather, provider.getName());
                }
            } catch (Exception e) {
                log.warn("Weather provider {} failed: {}", provider.getName(), e.getMessage());
                // Continue to next provider
            }
        }

        return "Weather information is currently unavailable for " + location;
    }

    @Tool("Search with multiple search engines")
    public String searchInformation(@P("Search query") String query) {
        // Try primary search engine
        try {
            List<SearchResult> results = primarySearchEngine.search(query);
            if (!results.isEmpty()) {
                return formatSearchResults(results, "primary");
            }
        } catch (Exception e) {
            log.warn("Primary search failed: {}", e.getMessage());
        }

        // Fall back to secondary search engine
        try {
            List<SearchResult> results = secondarySearchEngine.search(query);
            return formatSearchResults(results, "secondary");
        } catch (Exception e) {
            log.error("All search engines failed", e);
            return "Search is temporarily unavailable. Please try again later.";
        }
    }
}
```

### Streaming and Tool Execution

**Streaming with Tool Callbacks:**
```java
interface StreamingToolAssistant {
    TokenStream chat(String message);
}

StreamingToolAssistant assistant = AiServices.builder(StreamingToolAssistant.class)
    .streamingChatModel(streamingChatModel)
    .tools(new CalculatorTools(), new WeatherService())
    .build();

// Handle streaming with tool execution monitoring
TokenStream stream = assistant.chat("What's the weather in Paris and calculate 15 + 27?");

stream
    .onToolExecuted(toolExecution -> {
        System.out.println("Tool executed: " + toolExecution.request().name());
        System.out.println("Arguments: " + toolExecution.request().arguments());
        System.out.println("Result: " + toolExecution.result());
    })
    .onPartialResponse(partialResponse -> {
        System.out.print(partialResponse);
    })
    .onCompleteResponse(completeResponse -> {
        System.out.println("\nComplete response received");
    })
    .onError(error -> {
        System.err.println("Error: " + error.getMessage());
    })
    .start();
```

**Accessing Tool Execution Results:**
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
    System.out.println("Success: " + (execution.result() != null));
}

// Access token usage
TokenUsage tokenUsage = result.tokenUsage();
System.out.println("Input tokens: " + tokenUsage.inputTokenCount());
System.out.println("Output tokens: " + tokenUsage.outputTokenCount());
```

## API Reference

### Core Annotations

**Tool Definition:**
- `@Tool`: Mark method as executable tool with description
- `@P`: Parameter description and optional flag
- `@Description`: Class and field descriptions for complex parameters
- `@ToolMemoryId`: Link parameter to conversation memory context

**Tool Behavior:**
- `@Tool(returnBehavior = ReturnBehavior.IMMEDIATE)`: Return tool result directly
- `@P(required = false)`: Make parameter optional
- `@JsonProperty(required = false)`: Make record field optional

### Builder Configuration

**AiServices.builder() Tool Methods:**
```java
AiServices.builder(InterfaceClass.class)
    .tools(Object...)                              // Static tools
    .tools(Map<ToolSpecification, ToolExecutor>)   // Programmatic tools
    .toolProvider(ToolProvider)                    // Dynamic tools
    .executeToolsConcurrently()                    // Concurrent execution
    .executeToolsConcurrently(Executor)            // Custom executor
    .toolExecutionErrorHandler(ToolExecutionErrorHandler)
    .toolArgumentsErrorHandler(ToolArgumentsErrorHandler)
    .hallucinatedToolNameStrategy(Function<ToolExecutionRequest, ToolExecutionResultMessage>)
    .build();
```

### Core Interfaces

**ToolProvider:**
```java
public interface ToolProvider {
    ToolProviderResult provideTools(ToolProviderRequest request);
}

// Usage
ToolProvider provider = (request) -> {
    if (request.userMessage().singleText().contains("database")) {
        return ToolProviderResult.builder()
            .add(databaseToolSpec, databaseExecutor)
            .build();
    }
    return null;
};
```

**ToolExecutor:**
```java
public interface ToolExecutor {
    String execute(ToolExecutionRequest request, Object memoryId);
}

// Usage
ToolExecutor executor = (request, memoryId) -> {
    Map<String, Object> args = fromJson(request.arguments());
    // Execute tool logic
    return result;
};
```

**ToolSpecification Builder:**
```java
ToolSpecification spec = ToolSpecification.builder()
    .name("tool_name")
    .description("Tool description")
    .parameters(JsonObjectSchema.builder()
        .addStringProperty("param1", "Parameter description")
        .addIntegerProperty("param2", "Number parameter")
        .required("param1")
        .build())
    .build();
```

### Error Handling Interfaces

**ToolExecutionErrorHandler:**
```java
ToolExecutionErrorHandler handler = (error, context) -> {
    log.error("Tool execution failed: {}", error.getMessage());
    return ToolErrorHandlerResult.text("Tool temporarily unavailable");
};
```

**ToolArgumentsErrorHandler:**
```java
ToolArgumentsErrorHandler handler = (error, context) -> {
    return ToolErrorHandlerResult.text("Invalid arguments: " + error.getMessage());
};
```

## Workflow Patterns

### Complete Tool-Enabled Application

```java
@SpringBootApplication
public class ToolEnabledApplication {

    public static void main(String[] args) {
        SpringApplication.run(ToolEnabledApplication.class, args);
    }
}

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

    @GetMapping("/tools")
    public ResponseEntity<List<ToolInfo>> getAvailableTools(@RequestParam String userId) {
        List<ToolInfo> tools = assistant.getAvailableTools(userId);
        return ResponseEntity.ok(tools);
    }

    private List<String> extractToolNames(List<ToolExecution> executions) {
        return executions.stream()
            .map(execution -> execution.request().name())
            .collect(Collectors.toList());
    }
}

interface ToolEnabledAssistant {
    Result<String> chat(@MemoryId String userId, String message);
    List<ToolInfo> getAvailableTools(String userId);
}
```

### Multi-Domain Tool Integration

```java
@Service
public class MultiDomainToolService {

    private final ToolEnabledAssistant assistant;

    public MultiDomainToolService(ChatModel chatModel,
                                 List<DomainTools> domainTools,
                                 DynamicToolProvider toolProvider) {

        this.assistant = AiServices.builder(ToolEnabledAssistant.class)
            .chatModel(chatModel)
            .tools(domainTools.toArray())
            .toolProvider(toolProvider)
            .chatMemoryProvider(userId -> MessageWindowChatMemory.withMaxMessages(20))
            .executeToolsConcurrently()
            .toolExecutionErrorHandler(this::handleToolError)
            .build();
    }

    public String processRequest(String userId, String request, String domain) {
        // Add domain context to request
        String contextualRequest = String.format("[Domain: %s] %s", domain, request);

        Result<String> result = assistant.chat(userId, contextualRequest);

        // Log tool usage for analytics
        logToolUsage(userId, domain, result.toolExecutions());

        return result.content();
    }

    private ToolErrorHandlerResult handleToolError(Exception error, ToolExecutionContext context) {
        // Categorize error and provide appropriate response
        if (error instanceof TimeoutException) {
            return ToolErrorHandlerResult.text("Service is temporarily slow, please try again");
        } else if (error instanceof SecurityException) {
            return ToolErrorHandlerResult.text("Access denied for this operation");
        } else {
            return ToolErrorHandlerResult.text("Operation failed, please try again later");
        }
    }

    private void logToolUsage(String userId, String domain, List<ToolExecution> executions) {
        for (ToolExecution execution : executions) {
            analyticsService.recordToolUsage(
                userId, domain, execution.request().name(),
                execution.duration(), execution.result() != null
            );
        }
    }
}
```

### Tool Testing and Validation

```java
@Component
public class ToolTestingFramework {

    private final ToolRegistry toolRegistry;
    private final ChatModel testChatModel;

    public ToolValidationResult validateTool(Object toolInstance, String methodName) {
        try {
            // Create test AI service with single tool
            TestAssistant testAssistant = AiServices.builder(TestAssistant.class)
                .chatModel(testChatModel)
                .tools(toolInstance)
                .build();

            // Test basic tool functionality
            String response = testAssistant.testTool(methodName);

            // Validate response
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

    interface TestAssistant {
        String testTool(String toolName);
    }

    @TestConfiguration
    static class ToolTestConfig {

        @Bean
        @Primary
        public ChatModel testChatModel() {
            // Use a reliable model for testing
            return OpenAiChatModel.builder()
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .modelName("gpt-4o-mini")
                .temperature(0.0) // Deterministic for testing
                .build();
        }
    }
}
```

## Best Practices

### 1. Design Clear Tool Interfaces

```java
// Good - Clear, specific tool with detailed parameters
@Tool("Calculate monthly loan payment with principal, interest rate, and term")
public String calculateLoanPayment(
        @P("Loan principal amount in dollars") double principal,
        @P("Annual interest rate as percentage (e.g., 5.5 for 5.5%)") double annualRate,
        @P("Loan term in years") int termYears) {

    if (principal <= 0 || annualRate < 0 || termYears <= 0) {
        return "Invalid parameters: all values must be positive";
    }

    double monthlyRate = annualRate / 100 / 12;
    int numPayments = termYears * 12;

    double monthlyPayment = principal * (monthlyRate * Math.pow(1 + monthlyRate, numPayments))
                           / (Math.pow(1 + monthlyRate, numPayments) - 1);

    return String.format("Monthly payment: $%.2f for a $%.2f loan at %.2f%% for %d years",
                        monthlyPayment, principal, annualRate, termYears);
}

// Bad - Vague tool without proper validation
@Tool("Do math")
public String calculate(String operation) {
    // Unclear what operations are supported
    return "result";
}
```

### 2. Implement Robust Error Handling

```java
// Good - Comprehensive error handling
@Tool("Send email notification to user")
public String sendEmail(@P("Recipient email address") String to,
                       @P("Email subject") String subject,
                       @P("Email body content") String body) {
    try {
        // Validate email address
        if (!EmailValidator.isValid(to)) {
            return "Invalid email address: " + to;
        }

        // Check rate limits
        if (!rateLimiter.tryAcquire()) {
            return "Email rate limit exceeded. Please try again later.";
        }

        // Send email
        EmailResult result = emailService.sendEmail(to, subject, body);

        if (result.isSuccessful()) {
            return "Email sent successfully to " + to;
        } else {
            return "Failed to send email: " + result.getErrorMessage();
        }

    } catch (SecurityException e) {
        log.warn("Email sending security violation: {}", e.getMessage());
        return "Email sending is not permitted for this user";
    } catch (Exception e) {
        log.error("Unexpected error sending email", e);
        return "Email service is temporarily unavailable";
    }
}
```

### 3. Use Appropriate Return Types

```java
// Good - Structured return for complex data
@Description("Customer account information")
public static class AccountInfo {
    @Description("Account ID")
    private String accountId;

    @Description("Current balance in dollars")
    private BigDecimal balance;

    @Description("Account status: ACTIVE, SUSPENDED, CLOSED")
    private String status;

    @Description("Last transaction date")
    private LocalDate lastTransactionDate;
}

@Tool("Get comprehensive account information")
public AccountInfo getAccountInfo(@P("Customer account ID") String accountId) {
    Account account = accountService.findByAccountId(accountId);
    if (account == null) {
        throw new IllegalArgumentException("Account not found: " + accountId);
    }

    return AccountInfo.builder()
        .accountId(account.getId())
        .balance(account.getBalance())
        .status(account.getStatus().name())
        .lastTransactionDate(account.getLastTransactionDate())
        .build();
}
```

### 4. Implement Tool Security

```java
@Component
public class SecureToolsService {

    @Tool("Access sensitive customer data")
    public String getCustomerData(@ToolMemoryId String userId,
                                 @P("Customer ID to look up") String customerId) {

        // Check permissions
        if (!securityService.hasPermission(userId, "customer.read")) {
            return "Access denied: insufficient permissions";
        }

        // Check data access rules
        if (!dataAccessService.canAccessCustomer(userId, customerId)) {
            return "Access denied: cannot access this customer's data";
        }

        // Audit the access
        auditService.logDataAccess(userId, "customer_data", customerId);

        Customer customer = customerService.findById(customerId);
        return formatCustomerInfo(customer);
    }

    @Tool("Update customer information")
    public String updateCustomerInfo(@ToolMemoryId String userId,
                                   @P("Customer ID") String customerId,
                                   @P("Updated information") CustomerUpdateRequest update) {

        // Verify write permissions
        if (!securityService.hasPermission(userId, "customer.write")) {
            return "Access denied: no write permissions";
        }

        // Validate update request
        ValidationResult validation = customerValidator.validate(update);
        if (!validation.isValid()) {
            return "Invalid update: " + validation.getErrors();
        }

        // Apply update with audit trail
        CustomerUpdateResult result = customerService.updateCustomer(customerId, update, userId);

        return result.isSuccessful()
            ? "Customer updated successfully"
            : "Update failed: " + result.getErrorMessage();
    }
}
```

### 5. Monitor Tool Performance

```java
@Component
public class ToolPerformanceMonitor {

    private final MeterRegistry meterRegistry;

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

        // Record usage patterns
        meterRegistry.counter("tool.execution.count",
                "tool", event.getToolName(),
                "user_type", event.getUserType())
            .increment();
    }

    @Scheduled(fixedRate = 60000) // Every minute
    public void reportSlowTools() {
        // Report tools with high latency
        toolMetricsService.getSlowTools()
            .forEach(tool -> log.warn("Slow tool detected: {} avg: {}ms",
                                    tool.getName(), tool.getAverageLatency()));
    }
}
```

### 6. Optimize Tool Discoverability

```java
// Good - Well-organized tool categories
public class WeatherToolSuite {

    @Tool("Get current weather conditions including temperature, humidity, and wind")
    public String getCurrentWeather(@P("City name or coordinates") String location) {
        // Implementation
    }

    @Tool("Get detailed weather forecast for 1-10 days with daily summaries")
    public String getWeatherForecast(@P("City name or coordinates") String location,
                                   @P("Number of days (1-10)") int days) {
        // Implementation
    }

    @Tool("Get severe weather alerts and warnings for a location")
    public String getWeatherAlerts(@P("City name or coordinates") String location) {
        // Implementation
    }

    @Tool("Get historical weather data for analysis and comparison")
    public String getHistoricalWeather(@P("City name or coordinates") String location,
                                     @P("Date in YYYY-MM-DD format") String date) {
        // Implementation
    }
}
```

## Summary

This LangChain4j Tool & Function Calling skill covers:

1. **Tool Definition**: @Tool annotations, parameter descriptions, complex types
2. **Dynamic Tools**: ToolProvider, programmatic definitions, context-aware provisioning
3. **Parameter Handling**: Optional parameters, validation, complex objects
4. **Memory Integration**: @ToolMemoryId, user context, personalization
5. **AI Services as Tools**: Hierarchical agents, expert routing, specialization
6. **Advanced Patterns**: Immediate return, concurrent execution, streaming
7. **Error Handling**: Resilience patterns, graceful degradation, error recovery
8. **Integration Patterns**: Spring Boot, REST APIs, database integration
9. **Security**: Permission checks, audit trails, data access controls
10. **Best Practices**: Performance monitoring, testing, optimization