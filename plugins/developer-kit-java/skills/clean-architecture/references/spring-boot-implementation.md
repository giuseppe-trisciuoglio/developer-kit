# Spring Boot Implementation Guide

Detailed patterns for integrating Clean Architecture with Spring Boot 3.5+.

## Configuration Structure

```java
// Application configuration
@Configuration
@ComponentScan(basePackages = "com.example.order")
@EnableJpaRepositories(basePackages = "com.example.order.infrastructure.persistence")
@EntityScan(basePackages = "com.example.order.infrastructure.persistence")
public class OrderConfiguration {

    @Bean
    public OrderService orderService(
            OrderRepository orderRepository,
            PaymentGateway paymentGateway,
            DomainEventPublisher eventPublisher) {
        return new OrderService(orderRepository, paymentGateway, eventPublisher);
    }
}
```

## Dependency Injection Patterns

### Constructor Injection (Preferred)

```java
@Service
@RequiredArgsConstructor
public class OrderService implements CreateOrderUseCase {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final DomainEventPublisher eventPublisher;
}
```

### Multiple Implementations with Qualifier

```java
// Port interface
public interface NotificationService {
    void sendNotification(String to, String subject, String body);
}

// Primary adapter
@Component
@Primary
public class EmailNotificationService implements NotificationService {
    private final JavaMailSender mailSender;
    // Implementation
}

// Secondary adapter
@Component
@Qualifier("sms")
public class SmsNotificationService implements NotificationService {
    private final SmsClient smsClient;
    // Implementation
}

// Usage
@Service
@RequiredArgsConstructor
public class OrderConfirmationService {
    private final NotificationService emailNotification; // @Primary injected
    private final @Qualifier("sms") NotificationService smsNotification;
}
```

### Conditional Beans

```java
@Component
@ConditionalOnProperty(name = "payment.provider", havingValue = "stripe")
public class StripePaymentAdapter implements PaymentGateway {
    // Stripe implementation
}

@Component
@ConditionalOnProperty(name = "payment.provider", havingValue = "paypal")
public class PayPalPaymentAdapter implements PaymentGateway {
    // PayPal implementation
}
```

## JPA Mapping Strategies

### Separate Entity and Domain Model

```java
// Domain model (in domain package)
public class Order {
    private final OrderId id;
    private OrderStatus status;
    private List<OrderItem> items;
    // Pure business logic, no annotations
}

// JPA entity (in infrastructure package)
@Entity
@Table(name = "orders")
public class OrderJpaEntity {
    @Id
    private UUID id;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id")
    private List<OrderItemJpaEntity> items;

    @Column(name = "created_at")
    private Instant createdAt;
}
```

### Mapper with MapStruct

```java
@Mapper(componentModel = "spring")
public interface OrderJpaMapper {
    OrderJpaEntity toEntity(Order order);
    Order toDomain(OrderJpaEntity entity);

    default UUID map(OrderId id) {
        return id != null ? id.value() : null;
    }

    default OrderId map(UUID id) {
        return id != null ? new OrderId(id) : null;
    }

    default String map(Money money) {
        return money != null ? money.amount().toString() : null;
    }

    default Money map(String amount, String currency) {
        return amount != null ? new Money(new BigDecimal(amount), Currency.getInstance(currency)) : null;
    }
}
```

## Transaction Management

### Application Service Boundary

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;
    private final PaymentGateway paymentGateway;

    @Transactional
    public Order createOrder(CreateOrderCommand command) {
        // All operations within same transaction
        Order order = Order.create(command.customerId(), command.items());

        inventoryService.reserve(order.getItems()); // Will rollback if fails

        PaymentResult payment = paymentGateway.charge(order.getTotal());
        if (!payment.successful()) {
            throw new PaymentFailedException();
        }

        return orderRepository.save(order);
    }

    @Transactional(readOnly = true)
    public Optional<Order> findOrder(OrderId id) {
        return orderRepository.findById(id);
    }
}
```

### Read-Only Transactions for Queries

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class OrderQueryService {
    private final OrderJpaRepository orderJpaRepository;
    private final OrderMapper mapper;

    public Page<OrderSummary> findOrders(OrderSearchCriteria criteria, Pageable pageable) {
        return orderJpaRepository.findByCriteria(criteria, pageable)
            .map(mapper::toSummary);
    }
}
```

## Domain Events Publishing

### Spring ApplicationEventPublisher Adapter

```java
@Component
@RequiredArgsConstructor
public class SpringDomainEventPublisher implements DomainEventPublisher {
    private final ApplicationEventPublisher publisher;

    @Override
    public void publish(DomainEvent event) {
        publisher.publishEvent(event);
    }
}

// Or with @TransactionalEventListener for after-commit
@Component
@RequiredArgsConstructor
public class OrderEventListener {
    private final EmailService emailService;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCreated(OrderCreatedEvent event) {
        emailService.sendOrderConfirmation(event.orderId());
    }

    @EventListener
    public void handleOrderCancelled(OrderCancelledEvent event) {
        // Handle synchronously
    }
}
```

## Validation

### Bean Validation in Application Layer

```java
public record CreateOrderRequest(
    @NotNull(message = "Customer ID is required")
    UUID customerId,

    @NotEmpty(message = "Order must have at least one item")
    @Valid
    List<@NotNull OrderItemRequest> items,

    @Valid
    ShippingAddressRequest shippingAddress
) {}

public record OrderItemRequest(
    @NotNull
    UUID productId,

    @Min(value = 1, message = "Quantity must be at least 1")
    @Max(value = 100, message = "Maximum quantity is 100")
    int quantity
) {}
```

### Custom Validator

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = ValidOrderIdValidator.class)
public @interface ValidOrderId {
    String message() default "Invalid order ID";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

@Component
public class ValidOrderIdValidator implements ConstraintValidator<ValidOrderId, String> {
    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null) return true;
        try {
            UUID.fromString(value);
            return true;
        } catch (IllegalArgumentException e) {
            return false;
        }
    }
}
```

## Exception Handling

### Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(DomainException.class)
    public ResponseEntity<ErrorResponse> handleDomainException(DomainException ex) {
        ErrorResponse error = new ErrorResponse(
            ex.getCode(),
            ex.getMessage(),
            Instant.now()
        );
        return ResponseEntity.badRequest().body(error);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ValidationErrorResponse> handleValidationErrors(
            MethodArgumentNotValidException ex) {
        List<FieldError> errors = ex.getBindingResult().getFieldErrors().stream()
            .map(error -> new FieldError(
                error.getField(),
                error.getDefaultMessage()
            ))
            .toList();

        return ResponseEntity.badRequest()
            .body(new ValidationErrorResponse(errors));
    }

    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("NOT_FOUND", ex.getMessage(), Instant.now()));
    }
}
```

## Testing Configuration

### Slice Tests for Adapters

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class OrderRepositoryAdapterTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private OrderJpaRepository jpaRepository;

    @Autowired
    private OrderJpaMapper mapper;

    private OrderRepositoryAdapter adapter;

    @BeforeEach
    void setUp() {
        adapter = new OrderRepositoryAdapter(jpaRepository, mapper);
    }

    @Test
    void shouldSaveAndRetrieveOrder() {
        Order order = Order.create(new CustomerId(UUID.randomUUID()), sampleItems());

        Order saved = adapter.save(order);
        Optional<Order> found = adapter.findById(saved.getId());

        assertThat(found).isPresent();
        assertThat(found.get().getId()).isEqualTo(saved.getId());
    }
}
```

### WebMvcTest for Controllers

```java
@WebMvcTest(OrderController.class)
@Import({OrderMapperImpl.class, GlobalExceptionHandler.class})
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private CreateOrderUseCase createOrderUseCase;

    @MockitoBean
    private GetOrderUseCase getOrderUseCase;

    @Test
    void shouldCreateOrder() throws Exception {
        when(createOrderUseCase.createOrder(any()))
            .thenReturn(new OrderResponse(UUID.randomUUID(), OrderStatus.PENDING));

        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                        "customerId": "550e8400-e29b-41d4-a716-446655440000",
                        "items": [{"productId": "550e8400-e29b-41d4-a716-446655440001", "quantity": 2}]
                    }
                    """))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.status").value("PENDING"));
    }
}
```

## OpenAPI Documentation

```java
@Tag(name = "Orders", description = "Order management endpoints")
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    @Operation(summary = "Create new order")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Order created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid request"),
        @ApiResponse(responseCode = "422", description = "Business rule violation")
    })
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @Valid @RequestBody @Parameter(description = "Order creation request") CreateOrderRequest request) {
        // Implementation
    }
}
```

## Profiles for Environment-Specific Adapters

```java
@Component
@Profile("!test")
public class SmtpEmailService implements EmailService {
    // Real SMTP implementation
}

@Component
@Profile("test")
public class InMemoryEmailService implements EmailService {
    private final List<EmailMessage> sentEmails = new ArrayList<>();

    @Override
    public void send(String to, String subject, String body) {
        sentEmails.add(new EmailMessage(to, subject, body));
    }

    public List<EmailMessage> getSentEmails() {
        return List.copyOf(sentEmails);
    }
}
```
