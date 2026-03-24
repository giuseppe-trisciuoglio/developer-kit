# Spring Boot Integration

## Configuration

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class LambdaConfiguration {

    @Bean
    public LambdaClient lambdaClient() {
        return LambdaClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public LambdaAsyncClient lambdaAsyncClient() {
        return LambdaAsyncClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public ObjectMapper lambdaObjectMapper() {
        return new ObjectMapper();
            .registerModules(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }
}
```

## Lambda Invoker Service

```java
import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class LambdaInvokerService {

    private final LambdaClient lambdaClient;
    private final ObjectMapper objectMapper;

    public <T, R> R invoke(String functionName, T request, Class<R> responseType) {
        try {
            String jsonPayload = objectMapper.writeValueAsString(request);

            InvokeRequest invokeRequest = InvokeRequest.builder()
                .functionName(functionName)
                .payload(SdkBytes.fromUtf8String(jsonPayload))
                .build();

            InvokeResponse response = lambdaClient.invoke(invokeRequest);

            if (response.functionError() != null) {
                throw new LambdaInvocationException(
                    "Lambda function error: " + response.functionError());
            }

            if (response.statusCode() != 200) {
                throw new LambdaInvocationException(
                    functionName,
                    String.valueOf(response.statusCode()),
                    "Lambda invocation failed"
                );
            }

            String responseJson = response.payload().asUtf8String();

            return objectMapper.readValue(responseJson, responseType);

        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke Lambda function", e);
        }
    }

    public void invokeAsync(String functionName, Object request) {
        try {
            String jsonPayload = objectMapper.writeValueAsString(request);

            InvokeRequest invokeRequest = InvokeRequest.builder()
                .functionName(functionName)
                .invocationType(InvocationType.EVENT)
                .payload(SdkBytes.fromUtf8String(jsonPayload))
                .build();

            lambdaClient.invoke(invokeRequest);

        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke Lambda function async", e);
        }
    }

    public String invokeRaw(String functionName, String payload) {
        try {
            InvokeRequest invokeRequest = InvokeRequest.builder()
                .functionName(functionName)
                .payload(SdkBytes.fromUtf8String(payload))
                .build();

            InvokeResponse response = lambdaClient.invoke(invokeRequest);

            if (response.functionError() != null) {
                throw new LambdaInvocationException(
                    "Lambda function error: " + response.functionError());
            }

            return response.payload().asUtf8String();

        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke Lambda function", e);
        }
    }
}
```

## Typed Lambda Client

```java
public interface OrderProcessor {
    OrderResponse processOrder(OrderRequest request);
}

@Service
public class LambdaOrderProcessor implements OrderProcessor {

    private final LambdaInvokerService lambdaInvoker;

    @Value("${lambda.order-processor.function-name}")
    private String functionName;

    public LambdaOrderProcessor(LambdaInvokerService lambdaInvoker) {
        this.lambdaInvoker = lambdaInvoker;
    }

    @Override
    public OrderResponse processOrder(OrderRequest request) {
        return lambdaInvoker.invoke(functionName, request, OrderResponse.class);
    }
}
```

## Configuration Properties

```java
@Configuration
@ConfigurationProperties(prefix = "lambda")
@Data
public class LambdaProperties {
    private Map<String, FunctionConfig> functions = new HashMap<>();

    @Data
    public static class FunctionConfig {
        private String functionName;
        private String region;
        private Integer timeout;
        private Integer memorySize;
        private Map<String, String> environment = new HashMap<>();
    }
}
```

## Application Properties

```yaml
lambda:
  functions:
    order-processor:
      function-name: ${ORDER_PROCESSOR_FUNCTION:order-processor-dev}
      region: ${AWS_REGION:us-east-1}
      timeout: 60
      memory-size: 512
      environment:
        LOG_LEVEL: INFO
    user-processor:
      function-name: ${USER_PROCESSOR_FUNCTION:user-processor-dev}
      region: ${AWS_REGION:us-east-1}
      timeout: 30
      memory-size: 256
```

## Dynamic Lambda Service

```java
@Service
public class DynamicLambdaService {

    private final LambdaClient lambdaClient;
    private final LambdaProperties lambdaProperties;

    public <T, R> R invoke(String functionKey, T request, Class<R> responseType) {
        LambdaProperties.FunctionConfig config = lambdaProperties.getFunctions()
            .get(functionKey);

        if (config == null) {
            throw new IllegalArgumentException("Unknown function key: " + functionKey);
        }

        return invokeLambda(config, request, responseType);
    }

    private <T, R> R invokeLambda(LambdaProperties.FunctionConfig config,
                                   T request,
                                   Class<R> responseType) {
        try {
            String jsonPayload = objectMapper.writeValueAsString(request);

            InvokeRequest invokeRequest = InvokeRequest.builder()
                .functionName(config.getFunctionName())
                .payload(SdkBytes.fromUtf8String(jsonPayload))
                .build();

            InvokeResponse response = lambdaClient.invoke(invokeRequest);

            String responseJson = response.payload().asUtf8String();

            return objectMapper.readValue(responseJson, responseType);

        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke Lambda", e);
        }
    }
}
```

## Async Lambda Service

```java
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import java.util.concurrent.CompletableFuture;

@Service
public class AsyncLambdaService {

    private final LambdaAsyncClient asyncClient;

    @Async
    public CompletableFuture<String> invokeAsync(String functionName,
                                                 String payload) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String jsonPayload = objectMapper.writeValueAsString(payload);

                InvokeRequest request = InvokeRequest.builder()
                    .functionName(functionName)
                    .payload(SdkBytes.fromUtf8String(jsonPayload))
                    .build();

                InvokeResponse response = asyncClient.invoke(request).get();

                return response.payload().asUtf8String();

            } catch (Exception e) {
                throw new RuntimeException("Async invocation failed", e);
            }
        });
    }
}
```

## Health Check

```java
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class LambdaHealthIndicator implements HealthIndicator {

    private final LambdaClient lambdaClient;

    @Override
    public Health health() {
        try {
            ListFunctionsResponse response = lambdaClient.listFunctions();
            return Health.up()
                .withDetail("functions", response.functions().size())
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```
