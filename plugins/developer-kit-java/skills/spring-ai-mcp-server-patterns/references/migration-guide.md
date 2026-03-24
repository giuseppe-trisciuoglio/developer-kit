# Migrating from LangChain4j MCP to Spring AI MCP

Guide for migrating existing LangChain4j MCP server implementations to Spring AI.

## Key Differences

| Aspect | LangChain4j | Spring AI |
|--------|-------------|-----------|
| Tool annotation | `@ToolMethod` | `@Tool(description)` |
| Parameter annotation | `@P` | `@ToolParam` |
| Configuration | Custom properties | Spring Boot auto-configuration |
| Security | Manual | Spring Security integration |
| Integration | Standalone | Deep Spring ecosystem integration |
| Function calling | `AiTool` | `FunctionCallback` |

## Migration Steps

1. Replace `@ToolMethod("description")` with `@Tool(description = "description")` on tool methods
2. Replace `@P("description")` on parameters with `@ToolParam("description")`
3. Wrap tool classes with `@Component` (LangChain4j may use different registration)
4. Update configuration from LangChain4j properties to `spring.ai.mcp.*` properties
5. Migrate prompt templates to use `@PromptTemplate` and `@PromptParam`
6. Replace LangChain4j-specific types with Spring AI equivalents
7. Add `@EnableMcpServer` to the main application class
8. Configure Spring Security if you had custom auth in LangChain4j

## Code Migration Example

**Before (LangChain4j):**

```java
public class WeatherTools {

    @ToolMethod("Get weather information for a city")
    public String getWeather(@P("city name") String city) {
        return weatherService.getWeather(city);
    }

    @ToolMethod("Get 5-day forecast")
    public String getForecast(
            @P("city name") String city,
            @P("temperature unit") String unit) {
        return weatherService.getForecast(city, unit);
    }
}
```

**After (Spring AI):**

```java
@Component
public class WeatherTools {

    private final WeatherService weatherService;

    public WeatherTools(WeatherService weatherService) {
        this.weatherService = weatherService;
    }

    @Tool(description = "Get weather information for a city")
    public WeatherResponse getWeather(@ToolParam("City name") String city) {
        return weatherService.getWeather(city);
    }

    @Tool(description = "Get 5-day forecast")
    public ForecastResponse getForecast(
            @ToolParam("City name") String city,
            @ToolParam(value = "Temperature unit: celsius or fahrenheit", required = false) String unit) {
        return weatherService.getForecast(city, unit != null ? unit : "celsius");
    }
}
```

## Configuration Migration

**Before (LangChain4j application.properties):**

```properties
langchain4j.mcp.enabled=true
langchain4j.mcp.transport=stdio
langchain4j.openai.api-key=${OPENAI_API_KEY}
```

**After (Spring AI application.properties):**

```properties
spring.ai.mcp.enabled=true
spring.ai.mcp.transport.type=stdio
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.openai.chat.options.model=gpt-4o-mini
```

## Prompt Template Migration

**Before (LangChain4j):**

```java
public class CodePrompts {

    public AiPrompt createCodeReviewPrompt(String code) {
        return AiPrompt.builder()
                .system("You are a code reviewer.")
                .user("Review: " + code)
                .build();
    }
}
```

**After (Spring AI):**

```java
@Component
public class CodePrompts {

    @PromptTemplate(
        name = "code-review",
        description = "Review Java code for best practices"
    )
    public Prompt createCodeReviewPrompt(@PromptParam("code") String code) {
        return Prompt.builder()
                .system("You are a code reviewer.")
                .user("Review the following code:\n```java\n" + code + "\n```")
                .build();
    }
}
```

## Main Application Class Update

**Before:**

```java
@SpringBootApplication
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

**After:**

```java
@SpringBootApplication
@EnableMcpServer
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

## Benefits After Migration

- Full Spring Boot auto-configuration reduces boilerplate
- Native Spring Security integration simplifies auth
- Spring Cache integration via `@Cacheable` on tool methods
- Spring Actuator health checks out of the box
- Micrometer metrics integration
- Constructor injection for better testability
- Spring profiles for environment-specific configuration
- Deep integration with Spring Data, WebFlux, and other Spring modules
