# Integration Examples

## Multi-Domain Tool Service

```java
@Service
public class MultiDomainToolService {

    @Autowired
    private Assistant assistant;

    public String processRequest(String userId, String request, String domain) {
        String contextualRequest = String.format("[Domain: %s] %s", domain, request);

        Result<String> result = assistant.chat(userId, contextualRequest);

        // Log tool usage
        result.toolExecutions().forEach(execution ->
            analyticsService.recordToolUsage(userId, domain, execution.request().name()));

        return result.content();
    }
}
```

## Database Integration

```java
@Component
public class DatabaseTools {

    private final CustomerRepository repository;

    @Tool("Get customer information by ID")
    public Customer getCustomer(@P("Customer ID") Long customerId) {
        return repository.findById(customerId)
            .orElseThrow(() -> new IllegalArgumentException("Customer not found"));
    }

    @Tool("Update customer email address")
    public String updateEmail(
        @P("Customer ID") Long customerId,
        @P("New email address") String newEmail) {
        Customer customer = repository.findById(customerId)
            .orElseThrow(() -> new IllegalArgumentException("Customer not found"));
        customer.setEmail(newEmail);
        repository.save(customer);
        return "Email updated successfully";
    }
}
```

## REST API Integration

```java
@Component
public class ApiTools {

    private final WebClient webClient;

    @Tool("Get current stock price")
    public String getStockPrice(@P("Stock symbol") String symbol) {
        return webClient.get()
            .uri("/api/stocks/{symbol}", symbol)
            .retrieve()
            .bodyToMono(String.class)
            .block();
    }

    @Tool("Create payment intent")
    public String createPayment(@P("Amount") Double amount, @P("Currency") String currency) {
        return webClient.post()
            .uri("/api/payments")
            .bodyValue(Map.of("amount", amount, "currency", currency))
            .retrieve()
            .bodyToMono(String.class)
            .block();
    }
}
```

## Context-Aware Tools

```java
public class UserPreferencesTools {

    @Tool("Get user preferences for a category")
    public String getPreferences(
        @ToolMemoryId String userId,
        @P("Preference category (e.g., theme, language)") String category) {
        return preferencesService.getPreferences(userId, category);
    }

    @Tool("Set user preference")
    public String setPreference(
        @ToolMemoryId String userId,
        @P("Preference category") String category,
        @P("Preference value") String value) {
        preferencesService.setPreference(userId, category, value);
        return "Preference saved";
    }
}
```

## Dynamic Tool Provider

```java
public class DynamicToolProvider implements ToolProvider {

    private final Map<String, ToolWithExecutor> availableTools = new HashMap<>();

    public void registerTool(String name, ToolSpecification spec, ToolExecutor executor) {
        availableTools.put(name, new ToolWithExecutor(spec, executor));
    }

    @Override
    public ToolProviderResult provideTools(ToolProviderRequest request) {
        var builder = ToolProviderResult.builder();
        String message = request.userMessage().singleText().toLowerCase();

        // Dynamically filter tools based on user message
        if (message.contains("weather")) {
            builder.add(weatherToolSpec, weatherExecutor);
        }
        if (message.contains("calculate") || message.contains("math")) {
            builder.add(calculatorToolSpec, calculatorExecutor);
        }

        return builder.build();
    }
}
```

## Complete Service Example

```java
@Service
public class CustomerSupportAssistant {

    private final SupportAssistant assistant;

    public CustomerSupportAssistant(ChatLanguageModel chatModel) {
        this.assistant = AiServices.builder(SupportAssistant.class)
            .chatModel(chatModel)
            .tools(new CustomerTools(), new OrderTools(), new BillingTools())
            .toolExecutionErrorHandler(this::handleErrors)
            .chatMemoryProvider(MessageWindowChatMemory.withMaxMessages(20))
            .build();
    }

    public String handleCustomerQuery(String customerId, String query) {
        Result<String> result = assistant.chat(customerId, query);

        // Log tool usage for analytics
        result.toolExecutions().forEach(execution -> {
            logToolUsage(customerId, execution.request().name());
        });

        return result.content();
    }

    private String handleErrors(ToolExecutionRequest request, Throwable exception) {
        log.error("Tool execution failed: {} - {}",
            request.name(), exception.getMessage());

        if (exception instanceof CustomerNotFoundException) {
            return "I couldn't find that customer. Please verify the customer ID.";
        }

        return "I encountered an issue processing your request. Please try again.";
    }

    interface SupportAssistant {
        String chat(String userId, String message);
    }
}
```
