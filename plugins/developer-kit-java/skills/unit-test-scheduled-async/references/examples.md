# Async & Scheduled Testing — Code Examples

## Maven Dependencies

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter</artifactId>
</dependency>
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.awaitility</groupId>
  <artifactId>awaitility</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

## Gradle Dependencies

```kotlin
dependencies {
  implementation("org.springframework.boot:spring-boot-starter")
  testImplementation("org.junit.jupiter:junit-jupiter")
  testImplementation("org.awaitility:awaitility")
  testImplementation("org.assertj:assertj-core")
}
```

## Basic Async Testing with CompletableFuture

```java
@Service
public class EmailService {

  @Async
  public CompletableFuture<Boolean> sendEmailAsync(String to, String subject) {
    return CompletableFuture.supplyAsync(() -> {
      System.out.println("Sending email to " + to);
      return true;
    });
  }

  @Async
  public void notifyUser(String userId) {
    System.out.println("Notifying user: " + userId);
  }
}

// Unit test
class EmailServiceAsyncTest {

  @Test
  void shouldReturnCompletedFutureWhenSendingEmail() throws Exception {
    EmailService service = new EmailService();
    CompletableFuture<Boolean> result = service.sendEmailAsync("test@example.com", "Hello");
    Boolean success = result.get(); // Wait for completion
    assertThat(success).isTrue();
  }

  @Test
  void shouldCompleteWithinTimeout() {
    EmailService service = new EmailService();
    CompletableFuture<Boolean> result = service.sendEmailAsync("test@example.com", "Hello");
    assertThat(result).isCompletedWithValue(true);
  }
}
```

## Async Service with Mocked Dependencies

```java
@Service
public class UserNotificationService {
  private final EmailService emailService;
  private final SmsService smsService;

  public UserNotificationService(EmailService emailService, SmsService smsService) {
    this.emailService = emailService;
    this.smsService = smsService;
  }

  @Async
  public CompletableFuture<String> notifyUserAsync(String userId) {
    return CompletableFuture.supplyAsync(() -> {
      emailService.send(userId);
      smsService.send(userId);
      return "Notification sent";
    });
  }
}

@ExtendWith(MockitoExtension.class)
class UserNotificationServiceAsyncTest {

  @Mock
  private EmailService emailService;
  @Mock
  private SmsService smsService;
  @InjectMocks
  private UserNotificationService notificationService;

  @Test
  void shouldNotifyUserAsynchronously() throws Exception {
    CompletableFuture<String> result = notificationService.notifyUserAsync("user123");
    String message = result.get();
    assertThat(message).isEqualTo("Notification sent");
    verify(emailService).send("user123");
    verify(smsService).send("user123");
  }

  @Test
  void shouldHandleAsyncExceptionGracefully() {
    doThrow(new RuntimeException("Email service failed")).when(emailService).send(any());
    CompletableFuture<String> result = notificationService.notifyUserAsync("user123");
    assertThatThrownBy(result::get)
      .isInstanceOf(ExecutionException.class)
      .hasCauseInstanceOf(RuntimeException.class);
  }
}
```

## Testing `@Scheduled` Methods

```java
@Component
public class DataRefreshTask {
  private final DataRepository dataRepository;

  public DataRefreshTask(DataRepository dataRepository) {
    this.dataRepository = dataRepository;
  }

  @Scheduled(fixedDelay = 60000)
  public void refreshCache() {
    dataRepository.findAll(); // Update cache
  }

  @Scheduled(cron = "0 0 * * * *") // Every hour
  public void cleanupOldData() {
    dataRepository.deleteOldData(LocalDateTime.now().minusDays(30));
  }
}

@ExtendWith(MockitoExtension.class)
class DataRefreshTaskTest {

  @Mock
  private DataRepository dataRepository;
  @InjectMocks
  private DataRefreshTask dataRefreshTask;

  @Test
  void shouldRefreshCacheFromRepository() {
    when(dataRepository.findAll()).thenReturn(List.of(new Data(1L, "item1")));
    dataRefreshTask.refreshCache(); // Call directly — no cron needed
    verify(dataRepository).findAll();
  }

  @Test
  void shouldCleanupOldData() {
    dataRefreshTask.cleanupOldData();
    verify(dataRepository).deleteOldData(any(LocalDateTime.class));
  }
}
```

## Testing Async with Awaitility

```java
@Service
public class BackgroundWorker {
  private final AtomicInteger processedCount = new AtomicInteger(0);

  @Async
  public void processItems(List<String> items) {
    items.forEach(item -> processedCount.incrementAndGet());
  }

  public int getProcessedCount() { return processedCount.get(); }
}

class AwaitilityAsyncTest {

  @Test
  void shouldProcessAllItemsAsynchronously() {
    BackgroundWorker worker = new BackgroundWorker();
    worker.processItems(List.of("item1", "item2", "item3"));
    Awaitility.await()
      .atMost(Duration.ofSeconds(5))
      .pollInterval(Duration.ofMillis(100))
      .untilAsserted(() -> assertThat(worker.getProcessedCount()).isEqualTo(3));
  }

  @Test
  void shouldTimeoutWhenProcessingTakesTooLong() {
    BackgroundWorker worker = new BackgroundWorker();
    worker.processItems(List.of("item1"));
    assertThatThrownBy(() ->
      Awaitility.await().atMost(Duration.ofMillis(100)).until(() -> worker.getProcessedCount() == 10)
    ).isInstanceOf(ConditionTimeoutException.class);
  }
}
```

## Testing Scheduled Task Execution Count

```java
@Component
public class HealthCheckTask {
  private final HealthCheckService healthCheckService;
  private int executionCount = 0;

  public HealthCheckTask(HealthCheckService healthCheckService) {
    this.healthCheckService = healthCheckService;
  }

  @Scheduled(fixedRate = 5000)
  public void checkHealth() {
    executionCount++;
    healthCheckService.check();
  }

  public int getExecutionCount() { return executionCount; }
}

class ScheduledTaskTimingTest {

  @Test
  void shouldExecuteTaskMultipleTimes() {
    HealthCheckService mockService = mock(HealthCheckService.class);
    HealthCheckTask task = new HealthCheckTask(mockService);
    task.checkHealth();
    task.checkHealth();
    task.checkHealth();
    assertThat(task.getExecutionCount()).isEqualTo(3);
    verify(mockService, times(3)).check();
  }
}
```
