---
name: langchain4j-ai-services-patterns
description: Comprehensive guide for building declarative AI Services with LangChain4j using interface-based patterns, annotations, memory management, tools integration, and advanced AI application patterns
category: ai-development
tags: [langchain4j, ai-services, annotations, declarative, tools, memory, function-calling, llm, java]
version: 1.0.0
context7_library: /langchain4j/langchain4j
context7_trust_score: 7.8
language: en
license: See LICENSE
---

# LangChain4j AI Services Patterns

This skill provides comprehensive guidance for building declarative AI Services with LangChain4j using interface-based patterns, annotations for system and user messages, memory management, tools integration, and advanced AI application patterns that abstract away low-level LLM interactions.

## When to Use This Skill

Use this skill when:
- Building declarative AI-powered interfaces with minimal boilerplate code
- Creating type-safe AI services with Java interfaces and annotations
- Implementing conversational AI systems with memory management
- Designing AI services that can call external tools and functions
- Building multi-agent systems with specialized AI components
- Creating AI services with different personas and behaviors
- Implementing RAG (Retrieval-Augmented Generation) patterns declaratively
- Building production AI applications with proper error handling and validation
- Creating AI services that return structured data types (enums, POJOs, lists)
- Implementing streaming AI responses with reactive patterns

## Core Concepts

### Declarative AI Services

LangChain4j AI Services allow you to define AI-powered functionality using plain Java interfaces with annotations, eliminating the need for manual prompt construction and response parsing.

**Basic AI Service Definition:**
```java
interface Assistant {
    String chat(String userMessage);
}

// Create instance - LangChain4j generates implementation
Assistant assistant = AiServices.create(Assistant.class, chatModel);

// Use the service
String response = assistant.chat("Hello, how are you?");
System.out.println(response); // Hello, how can I help you?
```

**AI Service with System Message:**
```java
interface CustomerSupportBot {

    @SystemMessage("You are a helpful customer support agent for TechCorp. " +
                  "Be polite, professional, and try to resolve customer issues efficiently.")
    String handleInquiry(String customerMessage);

    @UserMessage("Analyze this customer feedback and extract sentiment: {{it}}")
    @SystemMessage("Return only: POSITIVE, NEGATIVE, or NEUTRAL")
    String analyzeSentiment(String feedback);
}

CustomerSupportBot bot = AiServices.create(CustomerSupportBot.class, chatModel);
String response = bot.handleInquiry("My order hasn't arrived yet");
String sentiment = bot.analyzeSentiment("Great service, very happy!");
```

### Annotation-Based Message Templates

**@SystemMessage Annotation:**
```java
interface Friend {

    @SystemMessage("You are a good friend of mine. Answer using slang.")
    String chat(String userMessage);
}

Friend friend = AiServices.create(Friend.class, model);
String answer = friend.chat("Hello"); // Hey! What's up?
```

**@UserMessage Annotation:**
```java
interface Friend {

    @UserMessage("You are a good friend of mine. Answer using slang. {{it}}")
    String chat(String userMessage);
}

Friend friend = AiServices.create(Friend.class, model);
String answer = friend.chat("Hello"); // Hey! What's shakin'?
```

**Template Variables with @V:**
```java
interface CountryExpert {

    @SystemMessage("Given a name of a country, {{answerInstructions}}")
    @UserMessage("What is the capital of {{country}}?")
    String getCapital(@V("answerInstructions") String instructions, @V("country") String country);
}

CountryExpert expert = AiServices.create(CountryExpert.class, model);
String capital = expert.getCapital("answer with a name of its capital", "Germany");
```

**Advanced Template Patterns:**
```java
interface MultiModalAssistant {

    // Simple message
    String chat(String userMessage);

    // Message with template variable
    String chat(@UserMessage String userMessage, @V("country") String country);

    // Message with content (text, image, audio, video, PDF)
    String chat(@UserMessage String userMessage, @UserMessage Content content);

    // Message with multiple images
    String chat(@UserMessage String userMessage, @UserMessage List<ImageContent> images);

    // Fixed template message
    @UserMessage("What is the capital of Germany?")
    String getGermanCapital();

    // Template with multiple variables
    @UserMessage("What is the {{something}} of {{country}}?")
    String getInfo(@V("something") String something, @V("country") String country);
}
```

### Memory Management Patterns

**Basic Shared Memory:**
```java
interface Assistant {
    String chat(String userMessage);
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
    .build();

// All conversations share the same memory
String response1 = assistant.chat("My name is Alice");
String response2 = assistant.chat("What's my name?"); // "Your name is Alice"
```

**Per-User Memory with @MemoryId:**
```java
interface Assistant {
    String chat(@MemoryId int memoryId, @UserMessage String message);
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(10))
    .build();

// Each user has separate memory
String answerToKlaus = assistant.chat(1, "Hello, my name is Klaus");
String answerToFrancine = assistant.chat(2, "Hello, my name is Francine");

// Klaus's conversation is separate from Francine's
String klausRemembered = assistant.chat(1, "What's my name?"); // "Your name is Klaus"
```

**Advanced Memory Access:**
```java
interface Assistant extends ChatMemoryAccess {
    String chat(@MemoryId int memoryId, @UserMessage String message);
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(10))
    .build();

// Use the service
String response = assistant.chat(1, "Hello, my name is Klaus");

// Access memory directly
List<ChatMessage> messages = assistant.getChatMemory(1).messages();

// Evict memory to prevent leaks
boolean evicted = assistant.evictChatMemory(1);
```

**Dynamic System Messages:**
```java
interface ContextualAssistant {
    String chat(@MemoryId String userId, String message);
}

ContextualAssistant assistant = AiServices.builder(ContextualAssistant.class)
    .chatModel(model)
    .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(10))
    .systemMessageProvider(userId -> {
        // Dynamic system message based on user context
        UserProfile profile = userService.getProfile(userId);
        return String.format("You are assisting %s, who prefers %s communication style",
                profile.getName(), profile.getCommunicationStyle());
    })
    .build();
```

### Tools and Function Calling

**Basic Tool Definition:**
```java
class Calculator {

    @Tool("Adds two given numbers")
    double add(double a, double b) {
        return a + b;
    }

    @Tool("Multiplies two given numbers")
    double multiply(double a, double b) {
        return a * b;
    }

    @Tool("Calculates square root of a number")
    double squareRoot(double x) {
        return Math.sqrt(x);
    }
}

interface MathGenius {
    String ask(String question);
}

MathGenius mathGenius = AiServices.builder(MathGenius.class)
    .chatModel(model)
    .tools(new Calculator())
    .build();

String answer = mathGenius.ask("What is the square root of 475695037565?");
System.out.println(answer); // The square root of 475695037565 is 689706.486532.
```

**Tool with Parameter Descriptions:**
```java
class WeatherService {

    @Tool("Get current weather for a specific city")
    public String getCurrentWeather(@P("The name of the city") String city) {
        // Call external weather API
        return weatherApiClient.getCurrentWeather(city);
    }

    @Tool("Get weather forecast for the next few days")
    public String getWeatherForecast(@P("The name of the city") String city,
                                   @P("Number of days for forecast (1-7)") int days) {
        return weatherApiClient.getForecast(city, days);
    }
}

interface WeatherAssistant {
    String chat(String userMessage);
}

WeatherAssistant assistant = AiServices.builder(WeatherAssistant.class)
    .chatModel(model)
    .tools(new WeatherService())
    .build();

String response = assistant.chat("What's the weather like in New York for the next 3 days?");
```

**Tool with Memory Context:**
```java
class BookingService {

    @Tool("Get booking details by number")
    public Booking getBookingDetails(@ToolMemoryId String memoryId,
                                   @P("Booking number") String bookingNumber) {
        // Use memoryId to access user context if needed
        return bookingRepository.findByNumber(bookingNumber);
    }

    @Tool("Cancel a booking")
    public String cancelBooking(@ToolMemoryId String memoryId,
                              @P("Booking number") String bookingNumber,
                              @P("Cancellation reason") String reason) {
        // Cancel booking and return confirmation
        bookingRepository.cancel(bookingNumber, reason);
        return "Booking " + bookingNumber + " has been cancelled successfully";
    }
}

interface BookingAssistant {
    String chat(@MemoryId String userId, String userMessage);
}
```

**Accessing Tool Executions:**
```java
interface Assistant {
    Result<String> chat(String userMessage);
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .tools(new Calculator())
    .build();

Result<String> result = assistant.chat("Calculate 15 + 27");

String answer = result.content();
List<ToolExecution> toolExecutions = result.toolExecutions();
TokenUsage tokenUsage = result.tokenUsage();
FinishReason finishReason = result.finishReason();

// Inspect tool executions
for (ToolExecution execution : toolExecutions) {
    System.out.println("Tool: " + execution.request().name());
    System.out.println("Arguments: " + execution.request().arguments());
    System.out.println("Result: " + execution.result());
}
```

### Structured Return Types

**Enum Return Types:**
```java
enum Priority {
    CRITICAL, HIGH, MEDIUM, LOW
}

enum Sentiment {
    POSITIVE, NEGATIVE, NEUTRAL
}

interface Analyzer {

    @UserMessage("Analyze the priority of the following issue: {{it}}")
    Priority analyzePriority(String issueDescription);

    @UserMessage("Analyze sentiment of {{it}}")
    Sentiment analyzeSentiment(String text);

    @UserMessage("Does {{it}} have a positive sentiment?")
    boolean isPositive(String text);
}

Analyzer analyzer = AiServices.create(Analyzer.class, model);

Priority priority = analyzer.analyzePriority("Payment gateway is down");
// Returns: Priority.CRITICAL

Sentiment sentiment = analyzer.analyzeSentiment("Great product!");
// Returns: Sentiment.POSITIVE
```

**POJO Return Types:**
```java
public class Person {
    private String name;
    private int age;
    private String occupation;

    // constructors, getters, setters
}

public class BookSummary {
    private String title;
    private String author;
    private List<String> mainThemes;
    private int rating;

    // constructors, getters, setters
}

interface DataExtractor {

    @UserMessage("Extract person information from: {{it}}")
    Person extractPerson(String text);

    @UserMessage("Summarize this book: {{it}}")
    BookSummary summarizeBook(String bookContent);
}

DataExtractor extractor = AiServices.create(DataExtractor.class, model);

Person person = extractor.extractPerson("John Smith is a 35-year-old software engineer");
BookSummary summary = extractor.summarizeBook("The Great Gatsby by F. Scott Fitzgerald...");
```

**List Return Types:**
```java
interface ContentGenerator {

    @UserMessage("Generate an outline for an article on: {{it}}")
    List<String> generateOutline(String topic);

    @UserMessage("Generate 5 creative names for a {{type}} business")
    List<String> generateBusinessNames(@V("type") String businessType);

    @UserMessage("Extract all email addresses from: {{it}}")
    List<String> extractEmails(String text);
}

ContentGenerator generator = AiServices.create(ContentGenerator.class, model);

List<String> outline = generator.generateOutline("Machine Learning");
List<String> names = generator.generateBusinessNames("coffee shop");
```

**Result Wrapper for Detailed Information:**
```java
interface Assistant {

    @UserMessage("Generate an outline for the article on: {{it}}")
    Result<List<String>> generateOutlineFor(String topic);
}

Assistant assistant = AiServices.create(Assistant.class, model);

Result<List<String>> result = assistant.generateOutlineFor("Java Programming");

List<String> outline = result.content();
TokenUsage tokenUsage = result.tokenUsage();
List<Content> sources = result.sources(); // For RAG applications
List<ToolExecution> toolExecutions = result.toolExecutions();
FinishReason finishReason = result.finishReason();
```

### Multi-Agent Systems

**Specialized Expert Agents:**
```java
interface MedicalExpert {
    @UserMessage("You are a medical expert. " +
                "Analyze the following request and provide medical advice: {{it}}")
    @Tool("A medical expert")
    String medicalRequest(String request);
}

interface LegalExpert {
    @UserMessage("You are a legal expert. " +
                "Analyze the following request from a legal perspective: {{it}}")
    @Tool("A legal expert")
    String legalRequest(String request);
}

interface TechnicalExpert {
    @UserMessage("You are a technical expert. " +
                "Provide technical guidance for: {{it}}")
    @Tool("A technical expert")
    String technicalRequest(String request);
}

// Router Agent that delegates to experts
interface RouterAgent {
    @UserMessage("Analyze the following user request and categorize it as 'legal', 'medical' or 'technical', " +
                "then forward the request to the corresponding expert. " +
                "Return the expert's answer without modification. " +
                "The user request is: '{{it}}'.")
    String askToExpert(String request);
}

// Build the expert agents
MedicalExpert medicalExpert = AiServices.builder(MedicalExpert.class)
        .chatModel(model)
        .build();

LegalExpert legalExpert = AiServices.builder(LegalExpert.class)
        .chatModel(model)
        .build();

TechnicalExpert technicalExpert = AiServices.builder(TechnicalExpert.class)
        .chatModel(model)
        .build();

// Build router with experts as tools
RouterAgent router = AiServices.builder(RouterAgent.class)
        .chatModel(model)
        .tools(medicalExpert, legalExpert, technicalExpert)
        .build();

String response = router.askToExpert("I broke my leg, what should I do?");
```

**Agents with Memory:**
```java
interface MedicalExpertWithMemory {

    @UserMessage("You are a medical expert. " +
                "Analyze the following user request and provide medical advice. " +
                "Consider our previous conversation. " +
                "The user request is {{request}}.")
    @Agent("A medical expert")
    String medical(@MemoryId String memoryId, @V("request") String request);
}

MedicalExpertWithMemory expert = AgenticServices
        .agentBuilder(MedicalExpertWithMemory.class)
        .chatModel(model)
        .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(10))
        .outputName("response")
        .build();

// Conversations maintain context
String response1 = expert.medical("user123", "I have a headache");
String response2 = expert.medical("user123", "The pain is getting worse");
```

### Advanced Builder Patterns

**Complete AI Service Configuration:**
```java
interface AdvancedAssistant {
    Result<String> chat(@MemoryId String userId, String message);
}

AdvancedAssistant assistant = AiServices.builder(AdvancedAssistant.class)
    .chatModel(chatModel)
    .streamingChatModel(streamingChatModel) // For streaming responses
    .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(20))
    .systemMessageProvider(userId -> getSystemMessageForUser(userId))
    .tools(new WeatherService(), new BookingService(), new Calculator())
    .toolProvider(toolProvider) // Dynamic tool provider
    .contentRetriever(embeddingStoreContentRetriever) // RAG support
    .retrievalAugmentor(retrievalAugmentor) // Custom RAG logic
    .chatRequestTransformer(this::transformRequest) // Request transformation
    .build();
```

**Dynamic Tool Provider:**
```java
ToolProvider dynamicToolProvider = (request, memoryId) -> {
    // Return different tools based on context
    if (isBusinessHours()) {
        return List.of(new BookingService(), new CustomerService());
    } else {
        return List.of(new EmergencyService());
    }
};

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .toolProvider(dynamicToolProvider)
    .build();
```

## API Reference

### Core Annotations

**AI Service Definition:**
- `@AiService`: Mark interface as AI service (Spring Boot integration)
- `@SystemMessage`: Define system message template
- `@UserMessage`: Define user message template
- `@V("variableName")`: Map parameter to template variable
- `@MemoryId`: Identify memory/conversation context
- `@Agent`: Agent description for multi-agent systems

**Tool Annotations:**
- `@Tool`: Mark method as available tool with description
- `@P("description")`: Parameter description for tools
- `@ToolMemoryId`: Link tool parameter to memory context

**Return Type Wrappers:**
- `Result<T>`: Wrapper providing access to token usage, tool executions, sources
- `Flux<String>`: Streaming responses (requires reactor integration)

### Builder Methods

**AiServices.builder() Methods:**
```java
AiServices.builder(InterfaceClass.class)
    .chatModel(ChatModel)                    // Required: Chat model
    .streamingChatModel(StreamingChatModel)  // Optional: Streaming model
    .chatMemory(ChatMemory)                  // Shared memory
    .chatMemoryProvider(ChatMemoryProvider)  // Per-user memory
    .systemMessageProvider(Function)         // Dynamic system messages
    .tools(Object...)                        // Static tools
    .toolProvider(ToolProvider)              // Dynamic tools
    .contentRetriever(ContentRetriever)      // RAG support
    .retrievalAugmentor(RetrievalAugmentor)  // Custom RAG logic
    .chatRequestTransformer(Function)        // Request transformation
    .build();
```

### Common Interfaces

**ChatMemoryAccess:**
```java
interface Assistant extends ChatMemoryAccess {
    String chat(@MemoryId int memoryId, String message);

    // Inherited methods:
    // ChatMemory getChatMemory(Object memoryId);
    // boolean evictChatMemory(Object memoryId);
}
```

**ToolProvider:**
```java
ToolProvider toolProvider = (toolExecutionRequest, memoryId) -> {
    // Return list of tools based on context
    return getToolsForContext(memoryId);
};
```

## Workflow Patterns

### Complete Customer Support Bot

```java
// Domain Models
public class Ticket {
    private String id;
    private String customerId;
    private String subject;
    private String description;
    private TicketStatus status;
    private LocalDateTime createdAt;

    // constructors, getters, setters
}

public enum TicketStatus {
    OPEN, IN_PROGRESS, RESOLVED, CLOSED
}

// Tools
class SupportTools {

    private final TicketService ticketService;
    private final CustomerService customerService;

    @Tool("Search for customer tickets by email or phone")
    public List<Ticket> findCustomerTickets(@P("Customer email or phone") String identifier) {
        Customer customer = customerService.findByEmailOrPhone(identifier);
        return ticketService.findByCustomerId(customer.getId());
    }

    @Tool("Create a new support ticket")
    public Ticket createTicket(@ToolMemoryId String memoryId,
                             @P("Customer identifier") String customerId,
                             @P("Ticket subject") String subject,
                             @P("Ticket description") String description) {
        return ticketService.createTicket(customerId, subject, description);
    }

    @Tool("Update ticket status")
    public Ticket updateTicketStatus(@P("Ticket ID") String ticketId,
                                   @P("New status") TicketStatus status,
                                   @P("Update comment") String comment) {
        return ticketService.updateStatus(ticketId, status, comment);
    }

    @Tool("Get detailed ticket information")
    public Ticket getTicketDetails(@P("Ticket ID") String ticketId) {
        return ticketService.findById(ticketId);
    }
}

// AI Service Interface
interface CustomerSupportAgent {

    @SystemMessage("""
        You are a helpful customer support agent for TechCorp.

        Guidelines:
        - Always be polite and professional
        - Use the available tools to help customers
        - For new issues, create tickets with clear subjects and descriptions
        - Provide ticket IDs to customers for reference
        - If you cannot resolve an issue, escalate appropriately
        - Remember customer context throughout the conversation
        """)
    String handleInquiry(@MemoryId String customerId, String customerMessage);

    @UserMessage("Analyze this customer message for urgency level: {{it}}")
    @SystemMessage("Return only: LOW, MEDIUM, HIGH, CRITICAL")
    String assessUrgency(String message);
}

// Service Implementation
@Service
public class CustomerSupportService {

    private final CustomerSupportAgent agent;

    public CustomerSupportService(ChatModel chatModel, SupportTools supportTools) {
        this.agent = AiServices.builder(CustomerSupportAgent.class)
            .chatModel(chatModel)
            .chatMemoryProvider(customerId -> MessageWindowChatMemory.withMaxMessages(20))
            .tools(supportTools)
            .build();
    }

    public String handleCustomerInquiry(String customerId, String message) {
        // Assess urgency first
        String urgency = agent.assessUrgency(message);

        // Handle based on urgency
        if ("CRITICAL".equals(urgency)) {
            // Immediately escalate or add priority handling
            notificationService.notifySupport(customerId, message, urgency);
        }

        // Process the inquiry
        return agent.handleInquiry(customerId, message);
    }
}
```

### Content Creation Pipeline

```java
// Content Models
public class Article {
    private String title;
    private String content;
    private List<String> tags;
    private String targetAudience;
    private String tone;

    // constructors, getters, setters
}

// Specialized Agents
interface ContentResearcher {
    @UserMessage("Research the topic '{{topic}}' and provide key points, " +
                "current trends, and relevant statistics.")
    String researchTopic(@V("topic") String topic);
}

interface OutlineGenerator {
    @UserMessage("Create a detailed outline for an article about '{{topic}}' " +
                "targeting {{audience}} with {{tone}} tone. " +
                "Include main sections and key points.")
    List<String> generateOutline(@V("topic") String topic,
                                @V("audience") String audience,
                                @V("tone") String tone);
}

interface ContentWriter {
    @UserMessage("Write a high-quality article section for: {{section}}. " +
                "Topic: {{topic}}, Audience: {{audience}}, Tone: {{tone}}. " +
                "Include relevant examples and maintain consistency.")
    String writeSection(@V("section") String section,
                       @V("topic") String topic,
                       @V("audience") String audience,
                       @V("tone") String tone);
}

interface ContentEditor {
    @UserMessage("Edit and improve this content for clarity, grammar, and flow: {{content}}")
    String editContent(@V("content") String content);

    @UserMessage("Suggest 5 SEO-friendly titles for an article about: {{topic}}")
    List<String> suggestTitles(@V("topic") String topic);
}

// Orchestrator
interface ContentOrchestrator {
    @UserMessage("You are a content creation coordinator. " +
                "Use the available tools to create a complete article about '{{topic}}' " +
                "for {{audience}} with {{tone}} tone. " +
                "Follow this process: research → outline → write sections → edit → finalize.")
    String createArticle(@V("topic") String topic,
                        @V("audience") String audience,
                        @V("tone") String tone);
}

// Build the content creation system
@Service
public class ContentCreationService {

    private final ContentOrchestrator orchestrator;

    public ContentCreationService(ChatModel chatModel) {
        // Build individual agents
        ContentResearcher researcher = AiServices.create(ContentResearcher.class, chatModel);
        OutlineGenerator outlineGenerator = AiServices.create(OutlineGenerator.class, chatModel);
        ContentWriter writer = AiServices.create(ContentWriter.class, chatModel);
        ContentEditor editor = AiServices.create(ContentEditor.class, chatModel);

        // Build orchestrator with agents as tools
        this.orchestrator = AiServices.builder(ContentOrchestrator.class)
            .chatModel(chatModel)
            .tools(researcher, outlineGenerator, writer, editor)
            .build();
    }

    public Article createArticle(String topic, String audience, String tone) {
        String content = orchestrator.createArticle(topic, audience, tone);

        // Parse and structure the result
        return parseArticleFromContent(content, topic, audience, tone);
    }
}
```

### RAG-Enabled Knowledge Assistant

```java
// Knowledge Service with RAG
interface KnowledgeAssistant {

    @SystemMessage("""
        You are a knowledgeable assistant with access to a company knowledge base.

        Guidelines:
        - Answer questions based on the provided context from the knowledge base
        - If information is not available in the context, clearly state this
        - Provide accurate, helpful responses with references when possible
        - For complex topics, break down your explanations
        - If asked about recent updates, use the search tools to find current information
        """)
    String answerQuestion(@MemoryId String userId, String question);

    @UserMessage("Summarize the key points about: {{topic}}")
    String summarizeTopic(@V("topic") String topic);

    @UserMessage("Find and list all policies related to: {{category}}")
    List<String> findPolicies(@V("category") String category);
}

// Search Tools
class KnowledgeTools {

    private final DocumentSearchService searchService;
    private final PolicyService policyService;

    @Tool("Search the knowledge base for specific information")
    public List<String> searchKnowledgeBase(@P("Search query") String query,
                                          @P("Maximum results") int maxResults) {
        return searchService.search(query, maxResults);
    }

    @Tool("Find company policies by category")
    public List<String> findPoliciesByCategory(@P("Policy category") String category) {
        return policyService.findByCategory(category);
    }

    @Tool("Get detailed information about a specific topic")
    public String getTopicDetails(@P("Topic name") String topic) {
        return searchService.getDetailedInformation(topic);
    }
}

// Service with RAG Integration
@Service
public class KnowledgeService {

    private final KnowledgeAssistant assistant;

    public KnowledgeService(ChatModel chatModel,
                           EmbeddingModel embeddingModel,
                           EmbeddingStore<TextSegment> embeddingStore,
                           KnowledgeTools knowledgeTools) {

        // Create content retriever for RAG
        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .minScore(0.7)
            .build();

        // Build assistant with RAG and tools
        this.assistant = AiServices.builder(KnowledgeAssistant.class)
            .chatModel(chatModel)
            .chatMemoryProvider(userId -> MessageWindowChatMemory.withMaxMessages(15))
            .contentRetriever(contentRetriever)
            .tools(knowledgeTools)
            .build();
    }

    public String answerQuestion(String userId, String question) {
        return assistant.answerQuestion(userId, question);
    }

    public String summarizeTopic(String topic) {
        return assistant.summarizeTopic(topic);
    }
}
```

## Best Practices

### 1. Design Clear Interface Contracts

```java
// Good - Clear, focused interface
interface OrderProcessor {

    @SystemMessage("You are an order processing assistant. Be concise and accurate.")
    OrderResult processOrder(@MemoryId String customerId, OrderRequest request);

    @UserMessage("Validate this order data: {{orderData}}")
    @SystemMessage("Return validation result with specific error messages if invalid")
    ValidationResult validateOrder(@V("orderData") String orderData);
}

// Bad - Overly generic interface
interface GenericAssistant {
    String doAnything(String input); // Too vague
}
```

### 2. Use Type-Safe Return Types

```java
// Good - Structured return types
interface DataAnalyzer {

    @UserMessage("Analyze sales data: {{data}}")
    SalesAnalysis analyzeSales(@V("data") String salesData);

    @UserMessage("Extract customer info: {{text}}")
    Optional<Customer> extractCustomer(@V("text") String text);

    @UserMessage("Classify sentiment: {{text}}")
    Sentiment classifySentiment(@V("text") String text);
}

// Bad - Always returning strings
interface BadAnalyzer {
    String analyze(String anything); // Hard to work with programmatically
}
```

### 3. Implement Proper Memory Management

```java
// Good - Proper memory boundaries
interface CustomerSupportBot {
    String chat(@MemoryId String customerId, String message);
}

// Build with memory limits
CustomerSupportBot bot = AiServices.builder(CustomerSupportBot.class)
    .chatModel(model)
    .chatMemoryProvider(customerId ->
        MessageWindowChatMemory.builder()
            .id(customerId)
            .maxMessages(25) // Reasonable limit
            .chatMemoryStore(persistentMemoryStore) // Persistent storage
            .build())
    .build();

// Implement memory cleanup
@Scheduled(fixedRate = 3600000) // Every hour
public void cleanupInactiveMemories() {
    memoryCleanupService.removeInactiveMemories(Duration.ofDays(7));
}
```

### 4. Design Effective Tools

```java
// Good - Well-documented tools with clear parameters
class OrderTools {

    @Tool("Search for orders by customer email or order ID")
    public List<Order> searchOrders(@P("Customer email or order ID") String identifier) {
        return orderService.search(identifier);
    }

    @Tool("Cancel an order and process refund if applicable")
    public CancellationResult cancelOrder(@P("Order ID") String orderId,
                                        @P("Cancellation reason") String reason,
                                        @P("Process refund (true/false)") boolean processRefund) {
        return orderService.cancel(orderId, reason, processRefund);
    }

    @Tool("Get detailed shipping information for an order")
    public ShippingDetails getShippingDetails(@P("Order ID") String orderId) {
        return shippingService.getDetails(orderId);
    }
}

// Bad - Vague tools without proper descriptions
class BadTools {
    @Tool("Does stuff")
    String doSomething(String input) { // Unclear what this does
        return "something";
    }
}
```

### 5. Handle Errors Gracefully

```java
interface ResilientAssistant {
    Result<String> chat(@MemoryId String userId, String message);
}

@Service
public class ResilientAssistantService {

    private final ResilientAssistant assistant;

    public String safeChat(String userId, String message) {
        try {
            Result<String> result = assistant.chat(userId, message);
            return result.content();
        } catch (Exception e) {
            log.error("AI service error for user {}: {}", userId, e.getMessage(), e);
            return "I'm sorry, I'm experiencing technical difficulties. Please try again later.";
        }
    }
}
```

### 6. Use Streaming for Long Responses

```java
interface StreamingAssistant {

    @SystemMessage("You are a helpful assistant. Provide detailed explanations.")
    Flux<String> chatStream(String userMessage);
}

// Controller for streaming responses
@RestController
public class StreamingController {

    private final StreamingAssistant assistant;

    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> streamChat(@RequestBody String message) {
        return assistant.chatStream(message)
                .onErrorReturn("Error occurred while processing your request");
    }
}
```

### 7. Implement Validation and Input Sanitization

```java
interface ValidatedAssistant {

    @UserMessage("Process this customer request: {{request}}")
    @SystemMessage("Validate input and respond appropriately. Reject inappropriate content.")
    String processRequest(@V("request") @Valid String request);
}

@Service
public class ValidationService {

    public String sanitizeInput(String input) {
        // Remove potentially harmful content
        return inputSanitizer.sanitize(input);
    }

    public boolean isValidInput(String input) {
        return input != null &&
               input.length() <= 1000 &&
               !containsInappropriateContent(input);
    }
}
```

### 8. Monitor AI Service Performance

```java
@Component
public class AiServiceMonitor {

    private final MeterRegistry meterRegistry;
    private final Counter requestCounter;
    private final Timer responseTimer;

    public AiServiceMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestCounter = Counter.builder("ai.service.requests")
            .description("Total AI service requests")
            .register(meterRegistry);
        this.responseTimer = Timer.builder("ai.service.response.time")
            .description("AI service response time")
            .register(meterRegistry);
    }

    public <T> T monitorExecution(String serviceName, Supplier<T> operation) {
        requestCounter.increment(Tags.of("service", serviceName));

        return Timer.Sample.start(meterRegistry)
            .stop(responseTimer.tag("service", serviceName), operation);
    }
}
```

## Summary

This LangChain4j AI Services skill covers:

1. **Declarative Interfaces**: Interface-based AI service definitions with zero boilerplate
2. **Annotation System**: @SystemMessage, @UserMessage, @V, @MemoryId, @Tool annotations
3. **Memory Management**: Shared memory, per-user memory, memory access and cleanup
4. **Tools Integration**: Function calling, parameter descriptions, memory context
5. **Structured Returns**: Enums, POJOs, lists, Result wrapper with metadata
6. **Multi-Agent Systems**: Specialized agents, routing, expert coordination
7. **Advanced Patterns**: Streaming, RAG integration, dynamic configuration
8. **Production Patterns**: Error handling, validation, monitoring, resilience
9. **Spring Boot Integration**: Auto-configuration, dependency injection, REST APIs
10. **Best Practices**: Type safety, memory management, performance optimization
