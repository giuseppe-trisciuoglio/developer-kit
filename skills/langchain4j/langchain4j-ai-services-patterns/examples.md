# LangChain4j AI Services - Practical Examples

This document provides practical, production-ready examples for LangChain4j AI Services patterns.

## 1. Basic Chat Interface

**Scenario**: Simple conversational interface without memory.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.model.openai.OpenAiChatModel;

interface SimpleChat {
    String chat(String userMessage);
}

public class BasicChatExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.7)
            .build();

        var chat = AiServices.builder(SimpleChat.class)
            .chatModel(chatModel)
            .build();

        String response = chat.chat("What is Spring Boot?");
        System.out.println(response);
    }
}
```

## 2. Stateful Assistant with Memory

**Scenario**: Multi-turn conversation with 10-message history.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.openai.OpenAiChatModel;

interface ConversationalAssistant {
    String chat(String userMessage);
}

public class StatefulAssistantExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(ConversationalAssistant.class)
            .chatModel(chatModel)
            .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
            .build();

        // Multi-turn conversation
        System.out.println(assistant.chat("My name is Alice"));
        System.out.println(assistant.chat("What is my name?")); // Remembers: "Your name is Alice"
        System.out.println(assistant.chat("What year was Spring Boot released?")); // Answers: "2014"
        System.out.println(assistant.chat("Tell me more about it")); // Context aware
    }
}
```

## 3. Multi-User Memory with @MemoryId

**Scenario**: Separate conversation history per user.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.MemoryId;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.openai.OpenAiChatModel;

interface MultiUserAssistant {
    String chat(@MemoryId int userId, String userMessage);
}

public class MultiUserMemoryExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        var assistant = AiServices.builder(MultiUserAssistant.class)
            .chatModel(chatModel)
            .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(20))
            .build();

        // User 1 conversation
        System.out.println(assistant.chat(1, "I like Java"));
        System.out.println(assistant.chat(1, "What language do I prefer?")); // Java

        // User 2 conversation - separate memory
        System.out.println(assistant.chat(2, "I prefer Python"));
        System.out.println(assistant.chat(2, "What language do I prefer?")); // Python

        // User 1 - still remembers Java
        System.out.println(assistant.chat(1, "What about me?")); // Java
    }
}
```

## 4. System Message & Template Variables

**Scenario**: Configurable system prompt with dynamic template variables.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;
import dev.langchain4j.model.openai.OpenAiChatModel;

interface TemplatedAssistant {
    
    @SystemMessage("You are a {{role}} expert. Be concise and professional.")
    String chat(@V("role") String role, String userMessage);

    @SystemMessage("You are a helpful assistant. Translate to {{language}}")
    @UserMessage("Translate this: {{text}}")
    String translate(@V("text") String text, @V("language") String language);
}

public class TemplatedAssistantExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.3)
            .build();

        var assistant = AiServices.create(TemplatedAssistant.class, chatModel);

        // Dynamic role
        System.out.println(assistant.chat("Java", "Explain dependency injection"));
        System.out.println(assistant.chat("DevOps", "Explain Docker containers"));

        // Translation with template
        System.out.println(assistant.translate("Hello, how are you?", "Spanish"));
        System.out.println(assistant.translate("Good morning", "French"));
    }
}
```

## 5. Structured Output Extraction

**Scenario**: Extract structured data (POJO, enum, list) from LLM responses.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.model.output.structured.Description;
import dev.langchain4j.model.openai.OpenAiChatModel;
import java.util.List;

enum Sentiment {
    POSITIVE, NEGATIVE, NEUTRAL
}

class ContactInfo {
    @Description("Person's full name")
    String fullName;
    
    @Description("Email address")
    String email;
    
    @Description("Phone number with country code")
    String phone;
}

interface DataExtractor {
    
    @UserMessage("Analyze sentiment: {{text}}")
    Sentiment extractSentiment(String text);

    @UserMessage("Extract contact from: {{text}}")
    ContactInfo extractContact(String text);

    @UserMessage("List all technologies in: {{text}}")
    List<String> extractTechnologies(String text);
    
    @UserMessage("Count items in: {{text}}")
    int countItems(String text);
}

public class StructuredOutputExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .responseFormat("json_object")
            .build();

        var extractor = AiServices.create(DataExtractor.class, chatModel);

        // Enum extraction
        Sentiment sentiment = extractor.extractSentiment("This product is amazing!");
        System.out.println("Sentiment: " + sentiment); // POSITIVE

        // POJO extraction
        ContactInfo contact = extractor.extractContact(
            "John Smith, john@example.com, +1-555-1234");
        System.out.println("Name: " + contact.fullName);
        System.out.println("Email: " + contact.email);

        // List extraction
        List<String> techs = extractor.extractTechnologies(
            "We use Java, Spring Boot, PostgreSQL, and Docker");
        System.out.println("Technologies: " + techs); // [Java, Spring Boot, PostgreSQL, Docker]

        // Primitive type
        int count = extractor.countItems("I have 3 apples, 5 oranges, and 2 bananas");
        System.out.println("Total items: " + count); // 10
    }
}
```

## 6. Tool Calling / Function Calling

**Scenario**: LLM calls Java methods to solve problems.

```java
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.openai.OpenAiChatModel;
import java.time.LocalDate;

class Calculator {
    @Tool("Add two numbers")
    int add(@P("first number") int a, @P("second number") int b) {
        return a + b;
    }

    @Tool("Multiply two numbers")
    int multiply(@P("first") int a, @P("second") int b) {
        return a * b;
    }
}

class WeatherService {
    @Tool("Get weather for a city")
    String getWeather(@P("city name") String city) {
        // Simulate API call
        return "Weather in " + city + ": 22°C, Sunny";
    }
}

class DateService {
    @Tool("Get current date")
    String getCurrentDate() {
        return LocalDate.now().toString();
    }
}

interface ToolUsingAssistant {
    String chat(String userMessage);
}

public class ToolCallingExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.0)
            .build();

        var assistant = AiServices.builder(ToolUsingAssistant.class)
            .chatModel(chatModel)
            .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
            .tools(new Calculator(), new WeatherService(), new DateService())
            .build();

        // LLM calls tools automatically
        System.out.println(assistant.chat("What is 25 + 37?")); 
        // Uses Calculator.add() → "25 + 37 equals 62"

        System.out.println(assistant.chat("What's the weather in Paris?"));
        // Uses WeatherService.getWeather() → "Weather in Paris: 22°C, Sunny"

        System.out.println(assistant.chat("Calculate (5 + 3) * 4"));
        // Uses add() and multiply() → "Result is 32"

        System.out.println(assistant.chat("What's today's date?"));
        // Uses getCurrentDate() → Shows current date
    }
}
```

## 7. Streaming Responses

**Scenario**: Real-time token-by-token streaming for UI responsiveness.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.TokenStream;
import dev.langchain4j.model.openai.OpenAiStreamingChatModel;

interface StreamingAssistant {
    TokenStream streamChat(String userMessage);
}

public class StreamingExample {
    public static void main(String[] args) {
        var streamingModel = OpenAiStreamingChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.7)
            .build();

        var assistant = AiServices.builder(StreamingAssistant.class)
            .streamingChatModel(streamingModel)
            .build();

        // Stream response token by token
        assistant.streamChat("Tell me a short story about a robot")
            .onNext(token -> System.out.print(token)) // Print each token
            .onCompleteResponse(response -> {
                System.out.println("\n--- Complete ---");
                System.out.println("Tokens used: " + response.tokenUsage().totalTokenCount());
            })
            .onError(error -> System.err.println("Error: " + error.getMessage()))
            .start();

        // Wait for completion
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

## 8. System Persona with Context

**Scenario**: Different assistants with distinct personalities and knowledge domains.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.model.openai.OpenAiChatModel;

interface JavaExpert {
    @SystemMessage("""
        You are a Java expert with 15+ years experience.
        Focus on best practices, performance, and clean code.
        Provide code examples when relevant.
        """)
    String answer(String question);
}

interface SecurityExpert {
    @SystemMessage("""
        You are a cybersecurity expert specializing in application security.
        Always consider OWASP principles and threat modeling.
        Provide practical security recommendations.
        """)
    String answer(String question);
}

interface DevOpsExpert {
    @SystemMessage("""
        You are a DevOps engineer with expertise in cloud deployment,
        CI/CD pipelines, containerization, and infrastructure as code.
        """)
    String answer(String question);
}

public class PersonaExample {
    public static void main(String[] args) {
        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .temperature(0.5)
            .build();

        var javaExpert = AiServices.create(JavaExpert.class, chatModel);
        var securityExpert = AiServices.create(SecurityExpert.class, chatModel);
        var devopsExpert = AiServices.create(DevOpsExpert.class, chatModel);

        var question = "How should I handle database connections?";

        System.out.println("=== Java Expert ===");
        System.out.println(javaExpert.answer(question));

        System.out.println("\n=== Security Expert ===");
        System.out.println(securityExpert.answer(question));

        System.out.println("\n=== DevOps Expert ===");
        System.out.println(devopsExpert.answer(question));
    }
}
```

## 9. Error Handling & Tool Execution Errors

**Scenario**: Graceful handling of tool failures and LLM errors.

```java
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.agent.tool.ToolExecutionRequest;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.model.openai.OpenAiChatModel;

class DataAccessService {
    @Tool("Query database for user")
    String queryUser(String userId) {
        // Simulate potential error
        if (!userId.matches("\\d+")) {
            throw new IllegalArgumentException("Invalid user ID format");
        }
        return "User " + userId + ": John Doe";
    }

    @Tool("Update user email")
    String updateEmail(String userId, String email) {
        if (!email.contains("@")) {
            throw new IllegalArgumentException("Invalid email format");
        }
        return "Updated email for user " + userId;
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
            .tools(new DataAccessService())
            .toolExecutionErrorHandler((request, exception) -> {
                System.err.println("Tool error: " + exception.getMessage());
                return "Error: " + exception.getMessage();
            })
            .build();

        // Will handle tool errors gracefully
        System.out.println(assistant.execute("Get details for user abc"));
        System.out.println(assistant.execute("Update user 123 with invalid-email"));
    }
}
```

## 10. RAG Integration with AI Services

**Scenario**: AI Service with content retrieval for knowledge-based Q&A.

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

interface KnowledgeBaseAssistant {
    String askAbout(String question);
}

public class RAGIntegrationExample {
    public static void main(String[] args) {
        // Setup embedding store
        var embeddingStore = new InMemoryEmbeddingStore<TextSegment>();

        // Setup models
        var embeddingModel = OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .build();

        var chatModel = OpenAiChatModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("gpt-4o-mini")
            .build();

        // Ingest documents
        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();

        ingestor.ingest(Document.from("Spring Boot is a framework for building Java applications."));
        ingestor.ingest(Document.from("Spring Data JPA simplifies database access."));

        // Create retriever
        var contentRetriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(3)
            .minScore(0.7)
            .build();

        // Create AI Service with RAG
        var assistant = AiServices.builder(KnowledgeBaseAssistant.class)
            .chatModel(chatModel)
            .contentRetriever(contentRetriever)
            .build();

        String answer = assistant.askAbout("What is Spring Boot?");
        System.out.println(answer);
    }
}
```

## Best Practices Summary

1. **Always use @SystemMessage** for consistent behavior across different messages
2. **Enable temperature=0** for deterministic tasks (extraction, calculations)
3. **Use MessageWindowChatMemory** for conversation history management
4. **Implement error handling** for tool failures
5. **Use structured output** when you need typed responses
6. **Stream long responses** for better UX
7. **Use @MemoryId** for multi-user scenarios
8. **Template variables** for dynamic system prompts
9. **Tool descriptions** should be clear and actionable
10. **Always validate** tool parameters before execution
