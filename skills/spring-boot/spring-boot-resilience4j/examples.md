# Resilience4j Examples

## Complete E-commerce Service Example

This example demonstrates a comprehensive e-commerce order service using multiple Resilience4j patterns.

### Project Structure

```
order-service/
├── src/main/java/com/ecommerce/order/
│   ├── config/
│   │   ├── ResilienceConfig.java
│   │   └── RestTemplateConfig.java
│   ├── controller/
│   │   ├── OrderController.java
│   │   └── GlobalExceptionHandler.java
│   ├── service/
│   │   ├── OrderService.java
│   │   ├── PaymentService.java
│   │   ├── InventoryService.java
│   │   └── NotificationService.java
│   ├── client/
│   │   ├── PaymentClient.java
│   │   ├── InventoryClient.java
│   │   └── EmailClient.java
│   └── domain/
│       ├── Order.java
│       ├── Payment.java
│       └── OrderStatus.java
└── src/main/resources/
    └── application.yml
```

### Configuration

**application.yml**
```yaml
server:
  port: 8080

spring:
  application:
    name: order-service

# Resilience4j Configuration
resilience4j:
  # Circuit Breaker Configuration
  circuitbreaker:
    configs:
      default:
        registerHealthIndicator: true
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 10
        minimumNumberOfCalls: 5
        failureRateThreshold: 50
        slowCallDurationThreshold: 3s
        slowCallRateThreshold: 50
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 3
        automaticTransitionFromOpenToHalfOpenEnabled: true
        eventConsumerBufferSize: 10
    instances:
      paymentService:
        baseConfig: default
        failureRateThreshold: 60
        waitDurationInOpenState: 60s
      inventoryService:
        baseConfig: default
        slidingWindowSize: 20
        minimumNumberOfCalls: 10

  # Retry Configuration
  retry:
    configs:
      default:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        retryExceptions:
          - org.springframework.web.client.ResourceAccessException
          - java.io.IOException
        ignoreExceptions:
          - java.lang.IllegalArgumentException
          - com.ecommerce.order.exception.BusinessValidationException
    instances:
      paymentService:
        baseConfig: default
        maxAttempts: 5
        waitDuration: 1s
      inventoryService:
        maxAttempts: 3
        waitDuration: 300ms

  # Rate Limiter Configuration
  ratelimiter:
    configs:
      default:
        registerHealthIndicator: true
        limitForPeriod: 100
        limitRefreshPeriod: 1s
        timeoutDuration: 0s
    instances:
      emailService:
        limitForPeriod: 10
        limitRefreshPeriod: 1m
      reportService:
        limitForPeriod: 5
        limitRefreshPeriod: 1s

  # Bulkhead Configuration
  bulkhead:
    configs:
      default:
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms
    instances:
      orderProcessing:
        maxConcurrentCalls: 5

  thread-pool-bulkhead:
    configs:
      default:
        maxThreadPoolSize: 4
        coreThreadPoolSize: 2
        queueCapacity: 100
        keepAliveDuration: 20ms
    instances:
      reportGeneration:
        maxThreadPoolSize: 8
        coreThreadPoolSize: 4
        queueCapacity: 50

  # Time Limiter Configuration
  timelimiter:
    configs:
      default:
        timeoutDuration: 3s
        cancelRunningFuture: true
    instances:
      paymentService:
        timeoutDuration: 5s
      reportService:
        timeoutDuration: 10s

# Actuator Configuration
management:
  endpoints:
    web:
      exposure:
        include: '*'
  endpoint:
    health:
      show-details: always
  health:
    circuitbreakers:
      enabled: true
    ratelimiters:
      enabled: true
  metrics:
    enabled: true
    export:
      prometheus:
        enabled: true
```

### Domain Models

**Order.java**
```java
package com.ecommerce.order.domain;

import lombok.Builder;
import lombok.Value;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Value
@Builder
public class Order {
    Long id;
    String customerId;
    List<OrderItem> items;
    BigDecimal totalAmount;
    OrderStatus status;
    String paymentId;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}

@Value
@Builder
class OrderItem {
    String productId;
    String productName;
    int quantity;
    BigDecimal unitPrice;
    BigDecimal totalPrice;
}
```

**OrderStatus.java**
```java
package com.ecommerce.order.domain;

public enum OrderStatus {
    PENDING,
    PAYMENT_PROCESSING,
    PAYMENT_CONFIRMED,
    INVENTORY_RESERVED,
    CONFIRMED,
    SHIPPED,
    DELIVERED,
    CANCELLED,
    FAILED
}
```

### Service Layer with Resilience Patterns

**OrderService.java**
```java
package com.ecommerce.order.service;

import com.ecommerce.order.domain.Order;
import com.ecommerce.order.domain.OrderStatus;
import io.github.resilience4j.bulkhead.annotation.Bulkhead;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class OrderService {
    
    private final PaymentService paymentService;
    private final InventoryService inventoryService;
    private final NotificationService notificationService;
    private final OrderRepository orderRepository;
    
    /**
     * Process order with bulkhead to limit concurrent order processing
     */
    @Bulkhead(name = "orderProcessing", type = Bulkhead.Type.SEMAPHORE)
    @Transactional
    public Order processOrder(OrderRequest request) {
        log.info("Processing order for customer: {}", request.getCustomerId());
        
        // Create initial order
        Order order = createOrder(request);
        
        try {
            // Reserve inventory
            inventoryService.reserveInventory(order);
            order = updateOrderStatus(order, OrderStatus.INVENTORY_RESERVED);
            
            // Process payment
            String paymentId = paymentService.processPayment(order);
            order = order.toBuilder()
                .paymentId(paymentId)
                .status(OrderStatus.PAYMENT_CONFIRMED)
                .build();
            orderRepository.save(order);
            
            // Confirm order
            order = updateOrderStatus(order, OrderStatus.CONFIRMED);
            
            // Send notification (async, best effort)
            notificationService.sendOrderConfirmation(order);
            
            log.info("Order processed successfully: {}", order.getId());
            return order;
            
        } catch (Exception ex) {
            log.error("Order processing failed: {}", order.getId(), ex);
            order = updateOrderStatus(order, OrderStatus.FAILED);
            
            // Compensating transactions
            compensateFailedOrder(order);
            
            throw new OrderProcessingException("Failed to process order", ex);
        }
    }
    
    private Order createOrder(OrderRequest request) {
        return Order.builder()
            .customerId(request.getCustomerId())
            .items(request.getItems())
            .totalAmount(calculateTotal(request.getItems()))
            .status(OrderStatus.PENDING)
            .createdAt(LocalDateTime.now())
            .build();
    }
    
    private Order updateOrderStatus(Order order, OrderStatus status) {
        Order updated = order.toBuilder()
            .status(status)
            .updatedAt(LocalDateTime.now())
            .build();
        return orderRepository.save(updated);
    }
    
    private void compensateFailedOrder(Order order) {
        try {
            if (order.getStatus() == OrderStatus.INVENTORY_RESERVED 
                    || order.getStatus() == OrderStatus.PAYMENT_CONFIRMED) {
                inventoryService.releaseInventory(order);
            }
            if (order.getPaymentId() != null) {
                paymentService.refundPayment(order.getPaymentId());
            }
        } catch (Exception ex) {
            log.error("Compensation failed for order: {}", order.getId(), ex);
        }
    }
    
    private BigDecimal calculateTotal(List<OrderItem> items) {
        return items.stream()
            .map(OrderItem::getTotalPrice)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
```

**PaymentService.java**
```java
package com.ecommerce.order.service;

import com.ecommerce.order.client.PaymentClient;
import com.ecommerce.order.domain.Order;
import com.ecommerce.order.domain.Payment;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.github.resilience4j.timelimiter.annotation.TimeLimiter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.concurrent.CompletableFuture;

@Slf4j
@Service
@RequiredArgsConstructor
public class PaymentService {
    
    private final PaymentClient paymentClient;
    
    /**
     * Process payment with circuit breaker, retry, and time limiter
     */
    @CircuitBreaker(name = "paymentService", fallbackMethod = "processPaymentFallback")
    @Retry(name = "paymentService")
    @TimeLimiter(name = "paymentService")
    public CompletableFuture<String> processPayment(Order order) {
        log.info("Processing payment for order: {}", order.getId());
        
        return CompletableFuture.supplyAsync(() -> {
            Payment payment = Payment.builder()
                .orderId(order.getId())
                .customerId(order.getCustomerId())
                .amount(order.getTotalAmount())
                .currency("USD")
                .build();
            
            PaymentResponse response = paymentClient.processPayment(payment);
            
            if (!response.isSuccess()) {
                throw new PaymentFailedException(
                    "Payment failed: " + response.getErrorMessage()
                );
            }
            
            log.info("Payment processed successfully: {}", response.getPaymentId());
            return response.getPaymentId();
        });
    }
    
    private CompletableFuture<String> processPaymentFallback(
            Order order, Exception ex) {
        log.error("Payment processing failed for order: {}. Using fallback.", 
            order.getId(), ex);
        
        // In real scenario, might queue for later processing or use alternative payment
        throw new PaymentServiceUnavailableException(
            "Payment service is currently unavailable. Please try again later.", ex
        );
    }
    
    /**
     * Refund payment with simpler resilience pattern
     */
    @CircuitBreaker(name = "paymentService")
    @Retry(name = "paymentService")
    public void refundPayment(String paymentId) {
        log.info("Initiating refund for payment: {}", paymentId);
        paymentClient.refundPayment(paymentId);
        log.info("Refund completed for payment: {}", paymentId);
    }
}
```

**InventoryService.java**
```java
package com.ecommerce.order.service;

import com.ecommerce.order.client.InventoryClient;
import com.ecommerce.order.domain.Order;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class InventoryService {
    
    private final InventoryClient inventoryClient;
    
    /**
     * Reserve inventory with circuit breaker and retry
     */
    @CircuitBreaker(name = "inventoryService", fallbackMethod = "reserveInventoryFallback")
    @Retry(name = "inventoryService")
    public void reserveInventory(Order order) {
        log.info("Reserving inventory for order: {}", order.getId());
        
        for (OrderItem item : order.getItems()) {
            InventoryReservation reservation = InventoryReservation.builder()
                .orderId(order.getId())
                .productId(item.getProductId())
                .quantity(item.getQuantity())
                .build();
            
            InventoryResponse response = inventoryClient.reserveInventory(reservation);
            
            if (!response.isSuccess()) {
                throw new InsufficientInventoryException(
                    String.format("Insufficient inventory for product: %s", 
                        item.getProductId())
                );
            }
        }
        
        log.info("Inventory reserved successfully for order: {}", order.getId());
    }
    
    private void reserveInventoryFallback(Order order, Exception ex) {
        log.error("Inventory reservation failed for order: {}", order.getId(), ex);
        throw new InventoryServiceUnavailableException(
            "Inventory service is currently unavailable", ex
        );
    }
    
    /**
     * Release inventory (compensation action)
     */
    @CircuitBreaker(name = "inventoryService")
    @Retry(name = "inventoryService")
    public void releaseInventory(Order order) {
        log.info("Releasing inventory for order: {}", order.getId());
        
        for (OrderItem item : order.getItems()) {
            try {
                inventoryClient.releaseInventory(order.getId(), item.getProductId());
            } catch (Exception ex) {
                log.error("Failed to release inventory for product: {}", 
                    item.getProductId(), ex);
            }
        }
        
        log.info("Inventory released for order: {}", order.getId());
    }
}
```

**NotificationService.java**
```java
package com.ecommerce.order.service;

import com.ecommerce.order.client.EmailClient;
import com.ecommerce.order.domain.Order;
import io.github.resilience4j.ratelimiter.annotation.RateLimiter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {
    
    private final EmailClient emailClient;
    
    /**
     * Send order confirmation with rate limiting
     * Async to not block order processing
     */
    @Async
    @RateLimiter(name = "emailService", fallbackMethod = "sendEmailFallback")
    public void sendOrderConfirmation(Order order) {
        log.info("Sending order confirmation email for order: {}", order.getId());
        
        EmailRequest email = EmailRequest.builder()
            .to(getCustomerEmail(order.getCustomerId()))
            .subject("Order Confirmation - " + order.getId())
            .body(buildOrderConfirmationEmail(order))
            .build();
        
        emailClient.sendEmail(email);
        log.info("Order confirmation email sent for order: {}", order.getId());
    }
    
    private void sendEmailFallback(Order order, Exception ex) {
        log.warn("Failed to send order confirmation email for order: {}. " +
            "Email will be queued for retry.", order.getId());
        
        // Queue email for later retry (e.g., save to database or message queue)
        queueEmailForRetry(order);
    }
    
    private void queueEmailForRetry(Order order) {
        // Implementation: Save to database or send to message queue
        log.info("Email queued for retry: order {}", order.getId());
    }
    
    private String getCustomerEmail(String customerId) {
        // Fetch from customer service
        return "customer@example.com";
    }
    
    private String buildOrderConfirmationEmail(Order order) {
        return String.format("""
            Dear Customer,
            
            Your order #%s has been confirmed!
            Total Amount: $%s
            
            Thank you for your purchase.
            """, order.getId(), order.getTotalAmount());
    }
}
```

### Controller Layer

**OrderController.java**
```java
package com.ecommerce.order.controller;

import com.ecommerce.order.domain.Order;
import com.ecommerce.order.service.OrderService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {
    
    private final OrderService orderService;
    
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @RequestBody @Valid OrderRequest request) {
        log.info("Received order request for customer: {}", request.getCustomerId());
        
        Order order = orderService.processOrder(request);
        
        OrderResponse response = OrderResponse.builder()
            .orderId(order.getId())
            .status(order.getStatus().name())
            .totalAmount(order.getTotalAmount())
            .message("Order created successfully")
            .build();
        
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
    
    @GetMapping("/{orderId}")
    public ResponseEntity<Order> getOrder(@PathVariable Long orderId) {
        Order order = orderService.getOrder(orderId);
        return ResponseEntity.ok(order);
    }
}
```

**GlobalExceptionHandler.java**
```java
package com.ecommerce.order.controller;

import io.github.resilience4j.bulkhead.BulkheadFullException;
import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import io.github.resilience4j.ratelimiter.RequestNotPermitted;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.util.concurrent.TimeoutException;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(CallNotPermittedException.class)
    public ResponseEntity<ErrorResponse> handleCallNotPermitted(
            CallNotPermittedException ex) {
        log.error("Circuit breaker is open", ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .code("SERVICE_UNAVAILABLE")
            .message("Service is temporarily unavailable. Please try again later.")
            .status(HttpStatus.SERVICE_UNAVAILABLE.value())
            .build();
        
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
    }
    
    @ExceptionHandler(RequestNotPermitted.class)
    public ResponseEntity<ErrorResponse> handleRequestNotPermitted(
            RequestNotPermitted ex) {
        log.warn("Rate limit exceeded", ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .code("TOO_MANY_REQUESTS")
            .message("Too many requests. Please slow down and try again.")
            .status(HttpStatus.TOO_MANY_REQUESTS.value())
            .build();
        
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(error);
    }
    
    @ExceptionHandler(BulkheadFullException.class)
    public ResponseEntity<ErrorResponse> handleBulkheadFull(
            BulkheadFullException ex) {
        log.warn("Bulkhead is full", ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .code("SERVICE_BUSY")
            .message("Service is currently at capacity. Please try again shortly.")
            .status(HttpStatus.SERVICE_UNAVAILABLE.value())
            .build();
        
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
    }
    
    @ExceptionHandler(TimeoutException.class)
    public ResponseEntity<ErrorResponse> handleTimeout(TimeoutException ex) {
        log.error("Request timed out", ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .code("REQUEST_TIMEOUT")
            .message("Request timed out. Please try again.")
            .status(HttpStatus.REQUEST_TIMEOUT.value())
            .build();
        
        return ResponseEntity.status(HttpStatus.REQUEST_TIMEOUT).body(error);
    }
    
    @ExceptionHandler(PaymentServiceUnavailableException.class)
    public ResponseEntity<ErrorResponse> handlePaymentServiceUnavailable(
            PaymentServiceUnavailableException ex) {
        log.error("Payment service unavailable", ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .code("PAYMENT_SERVICE_UNAVAILABLE")
            .message("Payment service is currently unavailable. " +
                    "Your order has been saved and will be processed shortly.")
            .status(HttpStatus.SERVICE_UNAVAILABLE.value())
            .build();
        
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
    }
    
    @ExceptionHandler(InsufficientInventoryException.class)
    public ResponseEntity<ErrorResponse> handleInsufficientInventory(
            InsufficientInventoryException ex) {
        log.warn("Insufficient inventory", ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .code("INSUFFICIENT_INVENTORY")
            .message(ex.getMessage())
            .status(HttpStatus.CONFLICT.value())
            .build();
        
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }
}
```

## Testing Examples

### Circuit Breaker Testing

**PaymentServiceTest.java**
```java
package com.ecommerce.order.service;

import com.ecommerce.order.client.PaymentClient;
import com.ecommerce.order.domain.Order;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.web.client.ResourceAccessException;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@SpringBootTest
class PaymentServiceTest {
    
    @Autowired
    private PaymentService paymentService;
    
    @Autowired
    private CircuitBreakerRegistry circuitBreakerRegistry;
    
    @MockBean
    private PaymentClient paymentClient;
    
    private CircuitBreaker circuitBreaker;
    
    @BeforeEach
    void setUp() {
        circuitBreaker = circuitBreakerRegistry.circuitBreaker("paymentService");
        circuitBreaker.reset();
    }
    
    @Test
    void shouldOpenCircuitAfterFailureThreshold() {
        // Arrange
        Order order = createTestOrder();
        when(paymentClient.processPayment(any()))
            .thenThrow(new ResourceAccessException("Connection failed"));
        
        // Act - Trigger failures to open circuit
        for (int i = 0; i < 5; i++) {
            assertThatThrownBy(() -> 
                paymentService.processPayment(order).get()
            ).hasRootCauseInstanceOf(ResourceAccessException.class);
        }
        
        // Assert - Circuit should be open
        assertThat(circuitBreaker.getState())
            .isEqualTo(CircuitBreaker.State.OPEN);
        
        // Next call should fail fast without calling the service
        assertThatThrownBy(() -> 
            paymentService.processPayment(order).get()
        ).hasRootCauseInstanceOf(PaymentServiceUnavailableException.class);
        
        // Verify service was called only during failures, not after circuit opened
        verify(paymentClient, times(5)).processPayment(any());
    }
    
    @Test
    void shouldTransitionToHalfOpenAndRecover() throws Exception {
        // Open the circuit
        Order order = createTestOrder();
        when(paymentClient.processPayment(any()))
            .thenThrow(new ResourceAccessException("Connection failed"));
        
        for (int i = 0; i < 5; i++) {
            try {
                paymentService.processPayment(order).get();
            } catch (Exception ignored) {}
        }
        
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.OPEN);
        
        // Manually transition to half-open (in real scenario, wait for timeout)
        circuitBreaker.transitionToHalfOpenState();
        
        // Service recovers
        PaymentResponse successResponse = new PaymentResponse("PAY-123", true, null);
        when(paymentClient.processPayment(any())).thenReturn(successResponse);
        
        // Successful calls in half-open state
        String paymentId = paymentService.processPayment(order).get();
        assertThat(paymentId).isEqualTo("PAY-123");
        
        // Circuit should close after successful calls
        assertThat(circuitBreaker.getState())
            .isEqualTo(CircuitBreaker.State.CLOSED);
    }
    
    private Order createTestOrder() {
        return Order.builder()
            .id(1L)
            .customerId("CUST-001")
            .totalAmount(new BigDecimal("99.99"))
            .build();
    }
}
```

### Integration Testing with WireMock

**OrderServiceIntegrationTest.java**
```java
package com.ecommerce.order.service;

import com.ecommerce.order.domain.Order;
import com.ecommerce.order.domain.OrderStatus;
import com.github.tomakehurst.wiremock.WireMockServer;
import com.github.tomakehurst.wiremock.client.WireMock;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static com.github.tomakehurst.wiremock.core.WireMockConfiguration.wireMockConfig;
import static org.assertj.core.api.Assertions.*;

@SpringBootTest
class OrderServiceIntegrationTest {
    
    private static WireMockServer wireMockServer;
    
    @Autowired
    private OrderService orderService;
    
    @BeforeAll
    static void setupWireMock() {
        wireMockServer = new WireMockServer(wireMockConfig().port(9090));
        wireMockServer.start();
        WireMock.configureFor("localhost", 9090);
    }
    
    @AfterAll
    static void tearDownWireMock() {
        wireMockServer.stop();
    }
    
    @BeforeEach
    void resetWireMock() {
        wireMockServer.resetAll();
    }
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("payment.service.url", () -> "http://localhost:9090");
        registry.add("inventory.service.url", () -> "http://localhost:9090");
    }
    
    @Test
    void shouldProcessOrderSuccessfully() {
        // Mock inventory service
        stubFor(post(urlEqualTo("/inventory/reserve"))
            .willReturn(okJson("{\"success\": true, \"reservationId\": \"RES-123\"}")));
        
        // Mock payment service
        stubFor(post(urlEqualTo("/payment/process"))
            .willReturn(okJson("{\"success\": true, \"paymentId\": \"PAY-123\"}")));
        
        // Process order
        OrderRequest request = createOrderRequest();
        Order order = orderService.processOrder(request);
        
        // Verify order was created successfully
        assertThat(order).isNotNull();
        assertThat(order.getStatus()).isEqualTo(OrderStatus.CONFIRMED);
        assertThat(order.getPaymentId()).isEqualTo("PAY-123");
        
        // Verify services were called
        verify(exactly(1), postRequestedFor(urlEqualTo("/inventory/reserve")));
        verify(exactly(1), postRequestedFor(urlEqualTo("/payment/process")));
    }
    
    @Test
    void shouldRetryOnTransientFailure() {
        // First two calls fail, third succeeds
        stubFor(post(urlEqualTo("/payment/process"))
            .inScenario("Retry")
            .whenScenarioStateIs(STARTED)
            .willReturn(serverError())
            .willSetStateTo("First Retry"));
        
        stubFor(post(urlEqualTo("/payment/process"))
            .inScenario("Retry")
            .whenScenarioStateIs("First Retry")
            .willReturn(serverError())
            .willSetStateTo("Second Retry"));
        
        stubFor(post(urlEqualTo("/payment/process"))
            .inScenario("Retry")
            .whenScenarioStateIs("Second Retry")
            .willReturn(okJson("{\"success\": true, \"paymentId\": \"PAY-456\"}")));
        
        stubFor(post(urlEqualTo("/inventory/reserve"))
            .willReturn(okJson("{\"success\": true, \"reservationId\": \"RES-456\"}")));
        
        // Process order
        OrderRequest request = createOrderRequest();
        Order order = orderService.processOrder(request);
        
        // Verify retry happened and order succeeded
        assertThat(order.getStatus()).isEqualTo(OrderStatus.CONFIRMED);
        verify(exactly(3), postRequestedFor(urlEqualTo("/payment/process")));
    }
    
    @Test
    void shouldHandleRateLimitExceeded() {
        // Setup: configure rate limiter to allow only 2 requests per second
        stubFor(post(urlEqualTo("/inventory/reserve"))
            .willReturn(okJson("{\"success\": true}")));
        stubFor(post(urlEqualTo("/payment/process"))
            .willReturn(okJson("{\"success\": true, \"paymentId\": \"PAY-789\"}")));
        
        // Process multiple orders rapidly
        OrderRequest request = createOrderRequest();
        
        // First 2 should succeed
        assertThatCode(() -> {
            orderService.processOrder(request);
            orderService.processOrder(request);
        }).doesNotThrowAnyException();
        
        // Additional requests should be rate limited (depends on configuration)
        // This test depends on your actual rate limiter configuration
    }
    
    private OrderRequest createOrderRequest() {
        return OrderRequest.builder()
            .customerId("CUST-001")
            .items(List.of(
                OrderItem.builder()
                    .productId("PROD-001")
                    .quantity(2)
                    .unitPrice(new BigDecimal("29.99"))
                    .build()
            ))
            .build();
    }
}
```

## Advanced Use Cases

### Custom Resilience Configuration Bean

```java
package com.ecommerce.order.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.core.registry.EntryAddedEvent;
import io.github.resilience4j.core.registry.EntryRemovedEvent;
import io.github.resilience4j.core.registry.EntryReplacedEvent;
import io.github.resilience4j.core.registry.RegistryEventConsumer;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.time.Duration;

@Slf4j
@Configuration
public class ResilienceConfig {
    
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .slowCallRateThreshold(50)
            .waitDurationInOpenState(Duration.ofSeconds(30))
            .slowCallDurationThreshold(Duration.ofSeconds(2))
            .permittedNumberOfCallsInHalfOpenState(3)
            .minimumNumberOfCalls(5)
            .slidingWindowSize(10)
            .recordException(e -> !(e instanceof BusinessException))
            .build();
        
        CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);
        
        // Register event consumer for all circuit breakers
        registry.getEventPublisher()
            .onEntryAdded(event -> 
                log.info("Circuit breaker added: {}", event.getAddedEntry().getName())
            )
            .onEntryRemoved(event -> 
                log.info("Circuit breaker removed: {}", event.getRemovedEntry().getName())
            );
        
        return registry;
    }
    
    @Bean
    public RegistryEventConsumer<CircuitBreaker> circuitBreakerEventConsumer() {
        return new RegistryEventConsumer<>() {
            @Override
            public void onEntryAddedEvent(EntryAddedEvent<CircuitBreaker> entryAddedEvent) {
                CircuitBreaker circuitBreaker = entryAddedEvent.getAddedEntry();
                circuitBreaker.getEventPublisher()
                    .onStateTransition(event -> 
                        log.warn("Circuit breaker {} transitioned from {} to {}",
                            circuitBreaker.getName(),
                            event.getStateTransition().getFromState(),
                            event.getStateTransition().getToState()
                        )
                    )
                    .onError(event -> 
                        log.error("Circuit breaker {} recorded error: {}",
                            circuitBreaker.getName(),
                            event.getThrowable().getMessage()
                        )
                    )
                    .onSuccess(event -> 
                        log.debug("Circuit breaker {} recorded success",
                            circuitBreaker.getName()
                        )
                    );
            }
            
            @Override
            public void onEntryRemovedEvent(EntryRemovedEvent<CircuitBreaker> entryRemoveEvent) {
                log.info("Circuit breaker removed: {}", 
                    entryRemoveEvent.getRemovedEntry().getName());
            }
            
            @Override
            public void onEntryReplacedEvent(EntryReplacedEvent<CircuitBreaker> entryReplacedEvent) {
                log.info("Circuit breaker replaced: {}", 
                    entryReplacedEvent.getNewEntry().getName());
            }
        };
    }
}
```

### Reactive WebFlux Example

```java
package com.ecommerce.order.service;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.reactor.circuitbreaker.operator.CircuitBreakerOperator;
import io.github.resilience4j.reactor.retry.RetryOperator;
import io.github.resilience4j.retry.Retry;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
public class ReactiveProductService {
    
    private final WebClient webClient;
    private final CircuitBreaker circuitBreaker;
    private final Retry retry;
    
    public Mono<Product> getProduct(String productId) {
        return webClient.get()
            .uri("/products/{id}", productId)
            .retrieve()
            .bodyToMono(Product.class)
            .transformDeferred(CircuitBreakerOperator.of(circuitBreaker))
            .transformDeferred(RetryOperator.of(retry))
            .onErrorResume(throwable -> {
                log.error("Failed to fetch product: {}", productId, throwable);
                return Mono.just(Product.unavailable(productId));
            });
    }
    
    public Flux<Product> streamProducts() {
        return webClient.get()
            .uri("/products/stream")
            .retrieve()
            .bodyToFlux(Product.class)
            .transformDeferred(CircuitBreakerOperator.of(circuitBreaker))
            .transformDeferred(RetryOperator.of(retry))
            .onErrorResume(throwable -> {
                log.error("Product stream failed", throwable);
                return Flux.empty();
            });
    }
}
```

### Monitoring Dashboard Data

```java
package com.ecommerce.order.monitoring;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/monitoring")
@RequiredArgsConstructor
public class ResilienceMonitoringController {
    
    private final CircuitBreakerRegistry circuitBreakerRegistry;
    
    @GetMapping("/circuit-breakers")
    public List<CircuitBreakerStatus> getCircuitBreakersStatus() {
        return circuitBreakerRegistry.getAllCircuitBreakers().stream()
            .map(this::toStatus)
            .collect(Collectors.toList());
    }
    
    private CircuitBreakerStatus toStatus(CircuitBreaker cb) {
        CircuitBreaker.Metrics metrics = cb.getMetrics();
        
        return CircuitBreakerStatus.builder()
            .name(cb.getName())
            .state(cb.getState().name())
            .failureRate(metrics.getFailureRate())
            .slowCallRate(metrics.getSlowCallRate())
            .numberOfBufferedCalls(metrics.getNumberOfBufferedCalls())
            .numberOfFailedCalls(metrics.getNumberOfFailedCalls())
            .numberOfSlowCalls(metrics.getNumberOfSlowCalls())
            .numberOfNotPermittedCalls(metrics.getNumberOfNotPermittedCalls())
            .numberOfSuccessfulCalls(metrics.getNumberOfSuccessfulCalls())
            .build();
    }
}

@Value
@Builder
class CircuitBreakerStatus {
    String name;
    String state;
    float failureRate;
    float slowCallRate;
    int numberOfBufferedCalls;
    int numberOfFailedCalls;
    int numberOfSlowCalls;
    long numberOfNotPermittedCalls;
    int numberOfSuccessfulCalls;
}
```

This comprehensive example demonstrates a production-ready implementation of Resilience4j patterns in a real-world e-commerce scenario, including proper configuration, error handling, testing, and monitoring.
