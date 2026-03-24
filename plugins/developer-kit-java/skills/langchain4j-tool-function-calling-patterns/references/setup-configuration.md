# Setup and Configuration

## Basic Tool Registration

```java
// Define tools using @Tool annotation
public class CalculatorTools {
    @Tool("Add two numbers")
    public double add(double a, double b) {
        return a + b;
    }
}

// Register with AiServices builder
interface MathAssistant {
    String ask(String question);
}

MathAssistant assistant = AiServices.builder(MathAssistant.class)
    .chatModel(chatModel)
    .tools(new CalculatorTools())
    .build();
```

## Builder Configuration Options

```java
AiServices.builder(AssistantInterface.class)

    // Static tool registration
    .tools(new Calculator(), new WeatherService())

    // Dynamic tool provider
    .toolProvider(new DynamicToolProvider())

    // Concurrent execution
    .executeToolsConcurrently()

    // Error handling
    .toolExecutionErrorHandler((request, exception) -> {
        return "Error: " + exception.getMessage();
    })

    // Memory for context
    .chatMemoryProvider(userId -> MessageWindowChatMemory.withMaxMessages(20))

    .build();
```

## Chat Model Configuration

```java
// For OpenAI
ChatLanguageModel chatModel = OpenAiChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName(GPT_4_O_MINI)
    .build();

// For HuggingFace
ChatLanguageModel chatModel = HuggingFaceChatModel.builder()
    .accessToken(System.getenv("HUGGINGFACE_API_KEY"))
    .modelId("mistralai/Mistral-7B-Instruct-v0.2")
    .build();
```

## Complete Setup Example

```java
@Configuration
public class LangChain4jConfig {

    @Bean
    public ChatLanguageModel chatLanguageModel() {
        return OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName(GPT_4_O_MINI)
            .temperature(0.7)
            .build();
    }

    @Bean
    public MathAssistant mathAssistant(ChatLanguageModel chatModel) {
        return AiServices.builder(MathAssistant.class)
            .chatModel(chatModel)
            .tools(new CalculatorTools())
            .build();
    }
}
```
