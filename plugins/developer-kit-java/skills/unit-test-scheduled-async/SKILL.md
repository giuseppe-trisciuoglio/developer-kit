---
name: unit-test-scheduled-async
description: Provides patterns for unit testing Spring `@Scheduled` and `@Async` methods using JUnit 5, CompletableFuture, Awaitility, and Mockito. Covers mocking task execution and timing, verifying execution counts, testing cron expressions, validating retry behavior, and simulating thread pool behavior. Use when testing background tasks, cron jobs, periodic execution, scheduled tasks, or thread pool behavior.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing `@Scheduled` and `@Async` Methods

## Overview

Patterns for unit testing Spring `@Scheduled` and `@Async` methods with JUnit 5. Test `CompletableFuture` results, use Awaitility for race conditions, mock scheduled task execution, and validate error handling — without waiting for real scheduling intervals.

## When to Use

- Testing `@Scheduled` method logic
- Testing `@Async` method behavior
- Verifying `CompletableFuture` results
- Testing async error handling
- Testing cron expression logic without waiting for actual scheduling
- Validating thread pool behavior and execution counts
- Testing background task logic in isolation

## Instructions

1. **Call `@Async` methods directly** — bypass Spring's async proxy; the annotation is irrelevant in unit tests
2. **Mock dependencies** with `@Mock` and `@InjectMocks` (Mockito)
3. **Wait for completion** — use `CompletableFuture.get(timeout, unit)` or `await().atMost(...).untilAsserted(...)`
4. **Call `@Scheduled` methods directly** — do not wait for cron/fixedRate; the annotation is ignored in unit tests
5. **Test exception paths** — verify `ExecutionException` wrapping on `CompletableFuture.get()`

**Validation checkpoints:**
- After `CompletableFuture.get()`, assert the returned value before verifying mock interactions
- If `ExecutionException` is thrown, check `.getCause()` to identify the root exception
- If Awaitility times out, increase `atMost()` duration or reduce `pollInterval()` until the condition is reachable
- After multiple task invocations, assert execution counts before `verify()` calls

## Examples

Key patterns — complete examples in `references/examples.md`:

```java
// @Async: call directly, wait with CompletableFuture.get(timeout, unit)
@Service
class EmailService {
  @Async
  public CompletableFuture<Boolean> sendEmailAsync(String to) {
    return CompletableFuture.supplyAsync(() -> true);
  }
}
@Test
void shouldReturnCompletedFuture() throws Exception {
  EmailService service = new EmailService();
  Boolean result = service.sendEmailAsync("test@example.com").get(5, TimeUnit.SECONDS);
  assertThat(result).isTrue();
}

// @Scheduled: call directly, mock the repository
@Component
class DataRefreshTask {
  @InjectMocks private DataRepository dataRepository;
  @Scheduled(fixedDelay = 60000) public void refreshCache() { /* ... */ }
}
@Test
void shouldRefreshCache() {
  when(dataRepository.findAll()).thenReturn(List.of(new Data(1L, "item1")));
  dataRefreshTask.refreshCache();
  verify(dataRepository).findAll();
}

// Awaitility: use for race conditions with shared mutable state
@Test
void shouldProcessAllItems() {
  BackgroundWorker worker = new BackgroundWorker();
  worker.processItems(List.of("item1", "item2", "item3"));
  Awaitility.await()
    .atMost(Duration.ofSeconds(5))
    .pollInterval(Duration.ofMillis(100))
    .untilAsserted(() -> assertThat(worker.getProcessedCount()).isEqualTo(3));
}

// Mocked dependencies with exception handling
@Test
void shouldHandleAsyncExceptionGracefully() {
  doThrow(new RuntimeException("Email failed")).when(emailService).send(any());
  CompletableFuture<String> result = service.notifyUserAsync("user123");
  assertThatThrownBy(result::get)
    .isInstanceOf(ExecutionException.class)
    .hasCauseInstanceOf(RuntimeException.class);
}
```

Full Maven/Gradle dependencies, additional test classes, and execution count patterns: see `references/examples.md`.

## Best Practices

- Always set a **timeout** on `CompletableFuture.get()` to prevent hanging tests
- **Mock all dependencies** — never call real external services in unit tests
- Use **Awaitility** only for race conditions; prefer direct calls for simple async methods
- Test `@Scheduled` **logic** directly — the annotation is ignored in unit tests
- Assert values before verifying mock interactions; verify **after** async completion

## Common Pitfalls

- Relying on Spring's async executor instead of calling methods directly
- Missing timeout on `CompletableFuture.get()`
- Forgetting to test exception propagation in async methods
- Not mocking dependencies that async methods invoke internally
- Waiting for actual cron/fixedRate timing instead of testing logic in isolation

## Constraints and Warnings

- **`@Async` self-invocation**: calling `@Async` from another method in the same class executes synchronously — the Spring proxy is bypassed
- **Thread pool ordering**: `ThreadPoolTaskScheduler` does not guarantee execution order
- **CompletableFuture chaining**: exceptions in intermediate stages can be silently lost — test each stage
- **Awaitility timeout**: always set a reasonable `atMost()`; infinite waits hang the test suite
- **No actual scheduling**: `@Scheduled` is ignored in unit tests — call methods directly

## References

- [Spring `@Async` Documentation](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/scheduling/annotation/Async.html)
- [Spring `@Scheduled` Documentation](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/scheduling/annotation/Scheduled.html)
- [Awaitility Testing Library](https://github.com/awaitility/awaitility)
- [CompletableFuture API](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html)
- Code examples: `references/examples.md`
