# Testing Event-Driven Applications

## Unit Testing Domain Events

### Test Domain Event Publishing

```java
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class ProductTest {

    @Test
    void shouldPublishProductCreatedEventOnCreation() {
        // When
        Product product = Product.create(
            "Test Product",
            BigDecimal.TEN,
            100
        );

        // Then
        assertThat(product.getDomainEvents()).hasSize(1);
        assertThat(product.getDomainEvents().get(0))
            .isInstanceOf(ProductCreatedEvent.class);

        ProductCreatedEvent event = (ProductCreatedEvent) product.getDomainEvents().get(0);
        assertThat(event.getName()).isEqualTo("Test Product");
        assertThat(event.getPrice()).isEqualByComparingTo(BigDecimal.TEN);
        assertThat(event.getStock()).isEqualTo(100);
    }

    @Test
    void shouldPublishStockDecreasedEvent() {
        // Given
        Product product = Product.create("Product", BigDecimal.TEN, 100);
        product.clearDomainEvents();

        // When
        product.decreaseStock(10);

        // Then
        assertThat(product.getDomainEvents()).hasSize(1);
        assertThat(product.getDomainEvents().get(0))
            .isInstanceOf(ProductStockDecreasedEvent.class);
    }

    @Test
    void shouldClearDomainEvents() {
        // Given
        Product product = Product.create("Product", BigDecimal.TEN, 100);

        // When
        product.clearDomainEvents();

        // Then
        assertThat(product.getDomainEvents()).isEmpty();
    }
}
```

### Test Event Handlers

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ProductEventHandlerTest {

    @Mock
    private NotificationService notificationService;

    @Mock
    private AuditService auditService;

    @InjectMocks
    private ProductEventHandler handler;

    @Test
    void shouldHandleProductCreatedEvent() {
        // Given
        ProductId productId = ProductId.of("123");
        ProductCreatedEvent event = new ProductCreatedEvent(
            productId,
            "Test Product",
            BigDecimal.TEN,
            100
        );

        // When
        handler.onProductCreated(event);

        // Then
        verify(notificationService).sendProductCreatedNotification("Test Product");
        verify(auditService).logProductCreation(
            eq("123"),
            eq("Test Product"),
            eq(BigDecimal.TEN),
            any(UUID.class)
        );
    }

    @Test
    void shouldHandleProductStockDecreasedEvent() {
        // Given
        ProductId productId = ProductId.of("123");
        ProductStockDecreasedEvent event = new ProductStockDecreasedEvent(
            productId,
            10,
            90
        );

        // When
        handler.onProductStockDecreased(event);

        // Then
        verify(notificationService).sendStockUpdateNotification("123", 10);
    }
}
```

## Integration Testing with Testcontainers

### Kafka Integration Test

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.kafka.test.context.EmbeddedKafka;
import org.springframework.test.context.TestPropertySource;
import java.util.concurrent.TimeUnit;
import static org.awaitility.Awaitility.await;

@SpringBootTest
@EmbeddedKafka(partitions = 1, brokerProperties = {
    "listeners=PLAINTEXT://localhost:9092",
    "port=9092"
})
class KafkaEventIntegrationTest {

    @Autowired
    private ProductApplicationService productService;

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @Autowired
    private ProductEventConsumer consumer;

    @Test
    void shouldPublishEventToKafka() throws Exception {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Test Product",
            BigDecimal.valueOf(99.99),
            50
        );

        // When
        ProductResponse response = productService.createProduct(request);

        // Then
        await()
            .atMost(5, TimeUnit.SECONDS)
            .untilAsserted(() -> {
                verify(consumer).handleProductCreated(any(ProductCreatedEventDto.class));
            });
    }
}
```

### Full Integration Test with Testcontainers

```java
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

@SpringBootTest
@Testcontainers
class EventDrivenIntegrationTest {

    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0")
    );

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Autowired
    private ProductApplicationService productService;

    @Test
    void shouldProcessEndToEnd() {
        // Create product
        CreateProductRequest request = new CreateProductRequest(
            "Test Product",
            BigDecimal.valueOf(99.99),
            50
        );

        ProductResponse response = productService.createProduct(request);

        assertThat(response.getId()).isNotNull();
        assertThat(response.getName()).isEqualTo("Test Product");
    }
}
```

## Testing Event Handlers with `@TransactionalEventListener`

### Test Transactional Event Listener

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;
import org.junit.jupiter.api.Test;
import static org.mockito.ArgumentCaptor.forClass;
import static org.mockito.Mockito.verify;

@SpringBootTest
class TransactionalEventListenerTest {

    @Autowired
    private ProductApplicationService productService;

    @Autowired
    private ProductEventHandler eventHandler;

    @Test
    @Transactional
    void shouldPublishEventAfterTransactionCommit() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Test Product",
            BigDecimal.TEN,
            100
        );

        // When
        productService.createProduct(request);

        // Then - Transaction will commit and event will be published
        // Use TransactionalEventListener test support
    }
}
```

### Test Event Publishing with ApplicationEventPublisher

```java
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.ApplicationEventPublisher;
import org.junit.jupiter.api.Test;
import static org.mockito.Mockito.*;

@SpringBootTest
class ApplicationEventPublisherTest {

    @Autowired
    private ProductApplicationService productService;

    @MockBean
    private ApplicationEventPublisher eventPublisher;

    @Test
    void shouldPublishEvents() {
        // Given
        CreateProductRequest request = new CreateProductRequest(
            "Test Product",
            BigDecimal.TEN,
            100
        );

        // When
        productService.createProduct(request);

        // Then
        verify(eventPublisher).publishEvent(any(ProductCreatedEvent.class));
    }
}
```

## Testing Kafka Consumers

### Test Kafka Listener

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.kafka.test.context.EmbeddedKafka;
import org.springframework.kafka.test.utils.KafkaTestUtils;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@EmbeddedKafka
class KafkaConsumerTest {

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @Autowired
    private ProductEventConsumer consumer;

    @Test
    void shouldConsumeProductCreatedEvent() throws Exception {
        // Given
        ProductCreatedEventDto event = new ProductCreatedEventDto(
            UUID.randomUUID().toString(),
            "123",
            "Test Product",
            BigDecimal.TEN,
            100,
            LocalDateTime.now(),
            UUID.randomUUID().toString()
        );

        // When
        kafkaTemplate.send("product-events", "123", event).get();

        // Then
        // Wait for async processing
        TimeUnit.SECONDS.sleep(2);

        verify(consumer).handleProductCreated(event);
    }
}
```

## Testing Spring Cloud Stream

### Test Stream Functions

```java
import org.springframework.cloud.stream.binder.test.InputDestination;
import org.springframework.cloud.stream.binder.test.OutputDestination;
import org.springframework.cloud.stream.binder.test.TestChannelBinderConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.Import;
import org.junit.jupiter.api.Test;
import org.springframework.messaging.Message;
import org.springframework.messaging.support.GenericMessage;

@SpringBootTest
@Import(TestChannelBinderConfiguration.class)
class StreamFunctionTest {

    @Autowired
    private InputDestination input;

    @Autowired
    private OutputDestination output;

    @Test
    void shouldProcessProductCreatedEvent() {
        // Given
        ProductCreatedEventDto event = new ProductCreatedEventDto(
            UUID.randomUUID().toString(),
            "123",
            "Test Product",
            BigDecimal.TEN,
            100,
            LocalDateTime.now(),
            UUID.randomUUID().toString()
        );

        Message<ProductCreatedEventDto> message = new GenericMessage<>(event);

        // When
        input.send(message, "productCreated-in-0");

        // Then
        Message<byte[]> result = output.receive(1000, "productCreated-out-0");
        assertThat(result).isNotNull();
    }
}
```

## Testing Event Sourcing Scenarios

### Test Event Reconstruction

```java
class EventSourcingTest {

    @Test
    void shouldReconstructAggregateFromEvents() {
        // Given
        List<DomainEvent> events = List.of(
            new ProductCreatedEvent(ProductId.of("123"), "Product", BigDecimal.TEN, 100),
            new ProductStockDecreasedEvent(ProductId.of("123"), 10, 90),
            new ProductStockDecreasedEvent(ProductId.of("123"), 5, 85)
        );

        // When
        Product product = Product.replay(events);

        // Then
        assertThat(product.getStock()).isEqualTo(85);
    }

    @Test
    void shouldRebuildStateFromEventStream() {
        // Given
        EventStream eventStream = eventStore.getEvents(ProductId.of("123"));

        // When
        Product product = Product.rebuild(eventStream);

        // Then
        assertThat(product).isNotNull();
        assertThat(product.getStock()).isEqualTo(85);
    }
}
```

## Testing Error Scenarios

### Test Event Handler Failure

```java
@Test
void shouldHandleEventProcessingFailure() {
    // Given
    ProductCreatedEvent event = new ProductCreatedEvent(
        ProductId.of("123"),
        "Test Product",
        BigDecimal.TEN,
        100
    );

    doThrow(new RuntimeException("Processing failed"))
        .when(orderService).onProductCreated(any());

    // When
    assertThatThrownBy(() -> consumer.handleProductCreated(event))
        .isInstanceOf(RuntimeException.class)
        .hasMessage("Processing failed");

    // Then
    verify(orderService, times(3)).onProductCreated(any()); // Retry attempts
}
```

### Test Dead Letter Queue

```java
@Test
void shouldSendFailedEventsToDLQ() {
    // Given
    ProductCreatedEventDto event = createEvent();

    doThrow(new RuntimeException("Max retries exceeded"))
        .when(orderService).onProductCreated(any());

    // When
    kafkaTemplate.send("product-events", event);

    // Then
    await().atMost(10, TimeUnit.SECONDS)
        .untilAsserted(() -> {
            Message<?> dltMessage = kafkaTemplate.receive("product-events-dlt");
            assertThat(dltMessage).isNotNull();
        });
}
```
