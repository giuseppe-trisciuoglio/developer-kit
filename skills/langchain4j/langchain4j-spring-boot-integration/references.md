# LangChain4j Spring Boot Integration - API References

Complete API reference for Spring Boot integration with LangChain4j.

## Spring Boot Starter Dependencies

### Maven
```xml
<!-- Core Spring Boot LangChain4j integration -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>0.27.0</version>
</dependency>

<!-- OpenAI integration -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>0.27.0</version>
</dependency>
```

### Gradle
```gradle
implementation 'dev.langchain4j:langchain4j-spring-boot-starter:0.27.0'
implementation 'dev.langchain4j:langchain4j-open-ai-spring-boot-starter:0.27.0'
```

## Auto-Configuration Properties

### OpenAI Configuration
```yaml
langchain4j:
  open-ai:
    api-key: ${OPENAI_API_KEY}
    model-name: gpt-4o-mini
    temperature: 0.7
    top-p: 1.0
    max-tokens: 2000
    timeout: 60s
    log-requests: true
    log-responses: true

  openai-embedding:
    api-key: ${OPENAI_API_KEY}
    model-name: text-embedding-3-small
    timeout: 60s
```

### Vector Store Configuration
```yaml
langchain4j:
  vector-store:
    type: in-memory  # or pinecone, weaviate, qdrant, etc.
    
  # Pinecone
  pinecone:
    api-key: ${PINECONE_API_KEY}
    index-name: my-index
    namespace: production
    
  # Qdrant
  qdrant:
    host: localhost
    port: 6333
    collection-name: documents
    
  # Weaviate
  weaviate:
    host: localhost
    port: 8080
    collection-name: Documents
```

## Spring Configuration Annotations

### @Configuration
```java
@Configuration
public class AiConfig {
    
    @Bean
    public ChatModel chatModel() {
        // Bean definition
    }
    
    @Bean
    @ConditionalOnMissingBean
    public EmbeddingModel embeddingModel() {
        // Fallback bean
    }
}
```

### @ConditionalOnProperty
```java
@Configuration
@ConditionalOnProperty(
    prefix = "app.ai",
    name = "enabled",
    havingValue = "true"
)
public class AiFeatureConfig {
    // Configuration only if enabled
}
```

### @EnableConfigurationProperties
```java
@Configuration
@EnableConfigurationProperties(AiProperties.class)
public class AiConfig {
    
    @Autowired
    private AiProperties aiProperties;
}
```

## Dependency Injection

### Constructor Injection (Recommended)
```java
@Service
public class ChatService {
    private final ChatModel chatModel;
    private final EmbeddingModel embeddingModel;
    
    public ChatService(ChatModel chatModel, EmbeddingModel embeddingModel) {
        this.chatModel = chatModel;
        this.embeddingModel = embeddingModel;
    }
}
```

### Field Injection (Discouraged)
```java
@Service
public class ChatService {
    @Autowired
    private ChatModel chatModel;  // Not recommended
}
```

### Setter Injection
```java
@Service
public class ChatService {
    private ChatModel chatModel;
    
    @Autowired
    public void setChatModel(ChatModel chatModel) {
        this.chatModel = chatModel;
    }
}
```

## REST Annotations

### @RestController with RequestMapping
```java
@RestController
@RequestMapping("/api/chat")
public class ChatController {
    
    @PostMapping
    public ResponseEntity<Response> chat(@RequestBody ChatRequest request) {
        // Implementation
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Response> getChat(@PathVariable String id) {
        // Implementation
    }
}
```

### RequestBody Validation
```java
@PostMapping
public ResponseEntity<Response> chat(@Valid @RequestBody ChatRequest request) {
    // Validates request object
}

public class ChatRequest {
    @NotBlank(message = "Message cannot be blank")
    private String message;
    
    @Min(0)
    @Max(100)
    private int maxTokens = 2000;
}
```

## Exception Handling

### @ControllerAdvice
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleBadRequest(IllegalArgumentException e) {
        return ResponseEntity.badRequest()
            .body(new ErrorResponse(400, e.getMessage()));
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGlobalException(Exception e) {
        return ResponseEntity.internalServerError()
            .body(new ErrorResponse(500, "Internal server error"));
    }
}
```

### ResponseStatusException
```java
if (!authorized) {
    throw new ResponseStatusException(
        HttpStatus.FORBIDDEN,
        "User not authorized"
    );
}
```

## Async and Reactive

### @Async
```java
@Service
@EnableAsync
public class AsyncService {
    
    @Async
    public CompletableFuture<String> processAsync(String input) {
        String result = processSync(input);
        return CompletableFuture.completedFuture(result);
    }
}
```

### @Scheduled
```java
@Component
public class ScheduledTasks {
    
    @Scheduled(fixedRate = 60000)  // Every minute
    public void performTask() {
        // Task implementation
    }
    
    @Scheduled(cron = "0 0 * * * *")  // Daily at midnight
    public void dailyTask() {
        // Daily task
    }
}
```

## Testing

### @SpringBootTest
```java
@SpringBootTest
class ChatServiceTest {
    
    @Autowired
    private ChatService chatService;
    
    @Test
    void testChat() {
        // Test implementation
    }
}
```

### @WebMvcTest
```java
@WebMvcTest(ChatController.class)
class ChatControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private ChatService chatService;
    
    @Test
    void testChatEndpoint() throws Exception {
        mockMvc.perform(post("/api/chat")
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"message\": \"Hello\"}"))
            .andExpect(status().isOk());
    }
}
```

### @DataJpaTest
```java
@DataJpaTest
class DocumentRepositoryTest {
    
    @Autowired
    private DocumentRepository repository;
    
    @Test
    void testFindByUserId() {
        // Test implementation
    }
}
```

## Logging Configuration

### application.yml
```yaml
logging:
  level:
    root: INFO
    dev.langchain4j: DEBUG
    org.springframework: WARN
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/app.log
```

## Health Checks

### Custom Health Indicator
```java
@Component
public class AiHealthIndicator extends AbstractHealthIndicator {
    
    @Override
    protected void doHealthCheck(Health.Builder builder) {
        try {
            // Check AI service availability
            chatModel.chat("ping");
            builder.up();
        } catch (Exception e) {
            builder.down().withDetail("reason", e.getMessage());
        }
    }
}
```

## Actuator Integration

### Maven Dependency
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

### Configuration
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, metrics, info
  endpoint:
    health:
      show-details: always
```

## Security Configuration

### @EnableWebSecurity
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeRequests()
            .antMatchers("/api/public/**").permitAll()
            .antMatchers("/api/private/**").authenticated()
            .and()
            .httpBasic();
        return http.build();
    }
}
```

## Bean Lifecycle

### @PostConstruct and @PreDestroy
```java
@Service
public class AiService {
    
    @PostConstruct
    public void init() {
        // Initialize resources
        embeddingStore = createEmbeddingStore();
    }
    
    @PreDestroy
    public void cleanup() {
        // Clean up resources
        embeddingStore.close();
    }
}
```

## Best Practices

1. **Use Constructor Injection**: Explicitly declare dependencies
2. **Externalize Configuration**: Use application.yml for settings
3. **Handle Exceptions**: Use @ControllerAdvice for consistent error handling
4. **Implement Caching**: Cache AI responses when appropriate
5. **Use Async Processing**: For long-running AI operations
6. **Add Health Checks**: Implement custom health indicators
7. **Log Appropriately**: Debug AI service calls in development
8. **Test Thoroughly**: Use @SpringBootTest and @WebMvcTest
9. **Secure APIs**: Implement authentication and authorization
10. **Monitor Performance**: Track AI service metrics
