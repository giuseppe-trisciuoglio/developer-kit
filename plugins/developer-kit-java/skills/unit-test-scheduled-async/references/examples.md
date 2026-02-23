# Scheduled and Async Testing - Detailed Examples

## Testing Async with Awaitility

### Wait for Async Completion

```java
import org.awaitility.Awaitility;
import org.awaitility.core.ConditionTimeoutException;
import org.junit.jupiter.api.Test;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import static org.assertj.core.api.Assertions.*;

@Service
public class BackgroundWorker {

  private final AtomicInteger processedCount = new AtomicInteger(0);

  @Async
  public void processItems(List<String> items) {
    items.forEach(item -> {
      processedCount.incrementAndGet();
    });
  }

  public int getProcessedCount() {
    return processedCount.get();
  }
}

class AwaitilityAsyncTest {

  @Test
  void shouldProcessAllItemsAsynchronously() {
    BackgroundWorker worker = new BackgroundWorker();
    List<String> items = List.of("item1", "item2", "item3");

    worker.processItems(items);

    Awaitility.await()
      .atMost(Duration.ofSeconds(5))
      .pollInterval(Duration.ofMillis(100))
      .untilAsserted(() -> {
        assertThat(worker.getProcessedCount()).isEqualTo(3);
      });
  }

  @Test
  void shouldTimeoutWhenProcessingTakesTooLong() {
    BackgroundWorker worker = new BackgroundWorker();
    List<String> items = List.of("item1", "item2", "item3");

    worker.processItems(items);

    assertThatThrownBy(() ->
      Awaitility.await()
        .atMost(Duration.ofMillis(100))
        .until(() -> worker.getProcessedCount() == 10)
    ).isInstanceOf(ConditionTimeoutException.class);
  }
}
```

## Testing Async Error Handling

### Handle Exceptions in Async Methods

```java
@Service
public class DataProcessingService {

  @Async
  public CompletableFuture<Boolean> processDataAsync(String data) {
    return CompletableFuture.supplyAsync(() -> {
      if (data == null || data.isEmpty()) {
        throw new IllegalArgumentException("Data cannot be empty");
      }
      return true;
    });
  }

  @Async
  public CompletableFuture<String> safeFetchData(String id) {
    return CompletableFuture.supplyAsync(() -> {
      try {
        return fetchData(id);
      } catch (Exception e) {
        return "Error: " + e.getMessage();
      }
    });
  }
}

import org.junit.jupiter.api.Test;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import static org.assertj.core.api.Assertions.*;

class AsyncErrorHandlingTest {

  @Test
  void shouldPropagateExceptionFromAsyncMethod() {
    DataProcessingService service = new DataProcessingService();

    CompletableFuture<Boolean> result = service.processDataAsync(null);

    assertThatThrownBy(result::get)
      .isInstanceOf(ExecutionException.class)
      .hasCauseInstanceOf(IllegalArgumentException.class)
      .hasMessageContaining("Data cannot be empty");
  }

  @Test
  void shouldHandleExceptionGracefullyWithFallback() throws Exception {
    DataProcessingService service = new DataProcessingService();

    CompletableFuture<String> result = service.safeFetchData("invalid");

    String message = result.get();
    assertThat(message).startsWith("Error:");
  }
}
```

## Testing Scheduled Task Timing

### Test Schedule Configuration

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

  public int getExecutionCount() {
    return executionCount;
  }
}

import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

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
