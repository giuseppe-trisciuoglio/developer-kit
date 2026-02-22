# Spring AI MCP Server - Implementation Patterns

## Tool Creation Pattern

Create tools with Spring AI's declarative approach:

```java
@Component
public class DatabaseTools {

    private final JdbcTemplate jdbcTemplate;

    public DatabaseTools(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @McpTool(description = "Execute a safe read-only SQL query")
    public List<Map<String, Object>> executeQuery(
            @McpToolParam(description = "SQL SELECT query") String query,
            @McpToolParam(description = "Query parameters", required = false)
            Map<String, Object> params) {

        // Validate query is read-only
        if (!query.trim().toUpperCase().startsWith("SELECT")) {
            throw new IllegalArgumentException("Only SELECT queries are allowed");
        }

        return jdbcTemplate.queryForList(query, params);
    }

    @McpTool(description = "Get table schema information")
    public TableSchema getTableSchema(
            @McpToolParam(description = "Table name") String tableName) {

        String sql = "SELECT column_name, data_type " +
                     "FROM information_schema.columns " +
                     "WHERE table_name = ?";

        List<Map<String, Object>> columns = jdbcTemplate.queryForList(sql, tableName);
        return new TableSchema(tableName, columns);
    }
}

record TableSchema(String tableName, List<Map<String, Object>> columns) {}
```

## Advanced Tool Pattern with Validation

```java
@Component
public class ApiTools {

    private final WebClient webClient;

    public ApiTools(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.build();
    }

    @McpTool(description = "Make HTTP GET request to an API")
    public ApiResponse callApi(
            @McpToolParam(description = "API URL") String url,
            @McpToolParam(description = "Headers as JSON string", required = false)
            String headersJson) {

        // Validate URL
        try {
            new URL(url);
        } catch (MalformedURLException e) {
            throw new IllegalArgumentException("Invalid URL format");
        }

        // Parse headers if provided
        HttpHeaders headers = new HttpHeaders();
        if (headersJson != null && !headersJson.isBlank()) {
            try {
                Map<String, String> headersMap = new ObjectMapper()
                    .readValue(headersJson, Map.class);
                headersMap.forEach(headers::add);
            } catch (JsonProcessingException e) {
                throw new IllegalArgumentException("Invalid headers JSON");
            }
        }

        return webClient.get()
                .uri(url)
                .headers(h -> h.addAll(headers))
                .retrieve()
                .bodyToMono(ApiResponse.class)
                .block();
    }
}

record ApiResponse(int status, Map<String, Object> body, HttpHeaders headers) {}
```

## Prompt Template Pattern

Create reusable prompt templates with Spring AI:

```java
@Component
public class CodeReviewPrompts {

    @PromptTemplate(
        name = "java-code-review",
        description = "Review Java code for best practices and issues"
    )
    public Prompt createJavaCodeReviewPrompt(
            @PromptParam("code") String code,
            @PromptParam(value = "focusAreas", required = false)
            List<String> focusAreas) {

        String focus = focusAreas != null ?
            String.join(", ", focusAreas) :
            "general best practices";

        return Prompt.builder()
                .system("You are an expert Java code reviewer with 20 years of experience.")
                .user("""
                    Review the following Java code for {focus}:

                    ```java
                    {code}
                    ```

                    Provide feedback in the following format:
                    1. Critical issues (must fix)
                    2. Warnings (should fix)
                    3. Suggestions (consider improving)
                    4. Positive aspects

                    Be specific and provide code examples where relevant.
                    """.replace("{code}", code).replace("{focus}", focus))
                .build();
    }

    @PromptTemplate(
        name = "generate-unit-tests",
        description = "Generate comprehensive unit tests for Java code"
    )
    public Prompt createTestGenerationPrompt(
            @PromptParam("code") String code,
            @PromptParam("className") String className,
            @PromptParam(value = "testingFramework", required = false)
            String framework) {

        String testFramework = framework != null ? framework : "JUnit 5";

        return Prompt.builder()
                .system("You are an expert in test-driven development.")
                .user("""
                    Generate comprehensive unit tests for the following Java class using {testFramework}:

                    ```java
                    {code}
                    ```

                    Class: {className}

                    Requirements:
                    1. Test all public methods
                    2. Include edge cases and boundary conditions
                    3. Use appropriate assertions
                    4. Follow AAA pattern (Arrange, Act, Assert)
                    5. Include test method naming best practices
                    6. Mock external dependencies
                    """.replace("{code}", code)
                      .replace("{className}", className)
                      .replace("{testFramework}", testFramework))
                .build();
    }
}
```

## Function Callback Pattern

Low-level function calling integration:

```java
@Configuration
public class FunctionConfig {

    @Bean
    public FunctionCallback weatherFunction() {
        return FunctionCallback.builder()
                .function("getCurrentWeather", new WeatherService())
                .description("Get the current weather for a location")
                .inputType(WeatherRequest.class)
                .build();
    }

    @Bean
    public FunctionCallback calculatorFunction() {
        return FunctionCallbackWrapper.builder(new Calculator())
                .withName("calculate")
                .withDescription("Perform mathematical calculations")
                .build();
    }
}

class WeatherService implements Function<WeatherRequest, WeatherResponse> {
    @Override
    public WeatherResponse apply(WeatherRequest request) {
        return new WeatherResponse(request.location(), 72, "Sunny");
    }
}

record WeatherRequest(String location) {}
record WeatherResponse(String location, double temperature, String condition) {}
```

## Dynamic Tool Registration

Register tools at runtime:

```java
@Service
public class DynamicToolRegistry {

    private final McpServer mcpServer;
    private final Map<String, ToolRegistration> registeredTools = new ConcurrentHashMap<>();

    public DynamicToolRegistry(McpServer mcpServer) {
        this.mcpServer = mcpServer;
    }

    public void registerTool(ToolRegistration registration) {
        registeredTools.put(registration.getId(), registration);

        Tool tool = Tool.builder()
                .name(registration.getName())
                .description(registration.getDescription())
                .inputSchema(registration.getInputSchema())
                .function(args -> executeDynamicTool(registration.getId(), args))
                .build();

        mcpServer.addTool(tool);
    }

    public void unregisterTool(String toolId) {
        ToolRegistration registration = registeredTools.remove(toolId);
        if (registration != null) {
            mcpServer.removeTool(registration.getName());
        }
    }

    private Object executeDynamicTool(String toolId, Map<String, Object> args) {
        ToolRegistration registration = registeredTools.get(toolId);
        if (registration == null) {
            throw new IllegalStateException("Tool not found: " + toolId);
        }

        return switch (registration.getType()) {
            case GROOVY_SCRIPT -> executeGroovyScript(registration, args);
            case SPRING_BEAN -> executeSpringBeanMethod(registration, args);
            case HTTP_ENDPOINT -> callHttpEndpoint(registration, args);
        };
    }
}

@Data
@Builder
class ToolRegistration {
    private String id;
    private String name;
    private String description;
    private Map<String, Object> inputSchema;
    private ToolType type;
    private String target;
    private Map<String, String> metadata;
}

enum ToolType {
    GROOVY_SCRIPT, SPRING_BEAN, HTTP_ENDPOINT
}
```

## Multi-Model Support

```java
@Configuration
public class MultiModelConfig {

    @Bean
    @Primary
    public ChatModel primaryChatModel(@Value("${spring.ai.primary.model}") String modelName) {
        return switch (modelName) {
            case "gpt-4" -> new OpenAiChatModel(OpenAiApi.builder()
                    .apiKey(System.getenv("OPENAI_API_KEY"))
                    .build());
            case "claude" -> new AnthropicChatModel(AnthropicApi.builder()
                    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
                    .build());
            default -> throw new IllegalArgumentException("Unsupported model: " + modelName);
        };
    }

    @Bean
    public ModelSelector modelSelector(Map<String, ChatModel> models) {
        return new SpringAiModelSelector(models);
    }
}

@Component
public class SpringAiModelSelector implements ModelSelector {

    private final Map<String, ChatModel> models;

    public SpringAiModelSelector(Map<String, ChatModel> models) {
        this.models = models;
    }

    @Override
    public ChatModel selectModel(Prompt prompt, Map<String, Object> context) {
        String modelName = determineBestModel(prompt, context);
        return models.get(modelName);
    }

    private String determineBestModel(Prompt prompt, Map<String, Object> context) {
        return "gpt-4";
    }
}
```

## Caching and Performance

```java
@Configuration
@EnableCaching
public class McpCacheConfig {

    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager(
            "tool-results", "prompt-templates", "function-callbacks"
        );
    }
}

@Component
public class CachedToolExecutor {

    private final McpServer mcpServer;

    public CachedToolExecutor(McpServer mcpServer) {
        this.mcpServer = mcpServer;
    }

    @Cacheable(
        value = "tool-results",
        key = "#toolName + '_' + #args.hashCode()",
        unless = "#result.isCacheable() == false"
    )
    public ToolResult executeTool(String toolName, Map<String, Object> args) {
        return mcpServer.executeTool(toolName, args);
    }

    @CacheEvict(value = "tool-results", allEntries = true)
    public void clearToolCache() {}

    @Cacheable(value = "prompt-templates", key = "#templateName")
    public PromptTemplate getPromptTemplate(String templateName) {
        return mcpServer.getPromptTemplate(templateName);
    }
}
```
