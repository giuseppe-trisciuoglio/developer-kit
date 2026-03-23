# Error Handling and Resilience

## Tool Error Handling

Handle tool execution errors gracefully:

```java
AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ExternalServiceTools())
    .toolExecutionErrorHandler((request, exception) -> {
        if (exception instanceof ApiException) {
            return "Service temporarily unavailable: " + exception.getMessage();
        }
        return "An error occurred while processing your request";
    })
    .build();
```

## Resilience Patterns

Implement circuit breakers and retries:

```java
public class ResilientService {

    private final CircuitBreaker circuitBreaker = CircuitBreaker.ofDefaults("external-api");

    @Tool("Get external data")
    public String getExternalData(@P("Data identifier") String id) {
        return circuitBreaker.executeSupplier(() -> {
            return externalApi.getData(id);
        });
    }
}
```

## Parameter Validation Errors

```java
.toolArgumentsErrorHandler((error, context) -> {
    return ToolErrorHandlerResult.text("Invalid arguments: " + error.getMessage());
})
```

## Hallucinated Tool Names

```java
.hallucinatedToolNameStrategy(request -> {
    return ToolExecutionResultMessage.from(request,
        "Error: Tool '" + request.name() + "' does not exist");
})
```

## Timeout Handling

```java
AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ExternalTools())
    .toolExecutionTimeout(Duration.ofSeconds(30))
    .build();
```

## Retry Configuration

```java
public class RetryingToolService {

    private final Retry retry = Retry.ofDefaults("tool-retry");

    @Tool("Fetch remote data")
    public String fetchData(@P("URL") String url) {
        return retry.executeSupplier(() -> {
            return webClient.get()
                .uri(url)
                .retrieve()
                .bodyToMono(String.class)
                .block();
        });
    }
}
```

## Monitoring and Logging

```java
AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new BusinessTools())
    .toolExecutionListener(new ToolExecutionListener() {
        @Override
        public void onToolExecuted(ToolExecution execution) {
            log.info("Tool {} executed in {}ms",
                execution.request().name(),
                execution.duration().toMillis());

            // Record metrics
            meterRegistry.timer("tool.execution",
                "tool", execution.request().name())
                .record(execution.duration());
        }

        @Override
        public void onToolExecutionError(ToolExecutionRequest request, Throwable error) {
            log.error("Tool {} execution failed: {}",
                request.name(), error.getMessage());

            // Record error metrics
            meterRegistry.counter("tool.errors",
                "tool", request.name(),
                "error", error.getClass().getSimpleName())
                .increment();
        }
    })
    .build();
```
