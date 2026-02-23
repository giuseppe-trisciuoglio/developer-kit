# Service Layer Test Examples

## Example 1: Business logic with mocked repository and publisher

```java
package com.example.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.context.ApplicationEventPublisher;

import java.math.BigDecimal;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private ApplicationEventPublisher eventPublisher;

    @InjectMocks
    private OrderService orderService;

    @Test
    void shouldApproveOrderAndPublishEvent() {
        Order order = new Order(10L, OrderStatus.PENDING, new BigDecimal("120.00"));
        when(orderRepository.findById(10L)).thenReturn(Optional.of(order));

        Order approved = orderService.approveOrder(10L);

        assertThat(approved.status()).isEqualTo(OrderStatus.APPROVED);
        verify(orderRepository).save(approved);

        ArgumentCaptor<OrderApprovedEvent> captor = ArgumentCaptor.forClass(OrderApprovedEvent.class);
        verify(eventPublisher).publishEvent(captor.capture());
        assertThat(captor.getValue().orderId()).isEqualTo(10L);
    }

    @Test
    void shouldRejectApprovalWhenOrderNotFound() {
        when(orderRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> orderService.approveOrder(99L))
                .isInstanceOf(OrderNotFoundException.class)
                .hasMessage("Order 99 not found");

        verify(orderRepository, never()).save(org.mockito.ArgumentMatchers.any());
        verify(eventPublisher, never()).publishEvent(org.mockito.ArgumentMatchers.any());
    }

    static class OrderService {
        private final OrderRepository orderRepository;
        private final ApplicationEventPublisher eventPublisher;

        OrderService(OrderRepository orderRepository, ApplicationEventPublisher eventPublisher) {
            this.orderRepository = orderRepository;
            this.eventPublisher = eventPublisher;
        }

        Order approveOrder(Long orderId) {
            Order current = orderRepository.findById(orderId)
                    .orElseThrow(() -> new OrderNotFoundException("Order " + orderId + " not found"));

            if (current.total().compareTo(BigDecimal.ZERO) <= 0) {
                throw new IllegalArgumentException("Order total must be positive");
            }

            Order approved = new Order(current.id(), OrderStatus.APPROVED, current.total());
            orderRepository.save(approved);
            eventPublisher.publishEvent(new OrderApprovedEvent(orderId));
            return approved;
        }
    }

    interface OrderRepository {
        Optional<Order> findById(Long id);
        Order save(Order order);
    }

    record Order(Long id, OrderStatus status, BigDecimal total) {
    }

    enum OrderStatus {
        PENDING,
        APPROVED
    }

    record OrderApprovedEvent(Long orderId) {
    }

    static class OrderNotFoundException extends RuntimeException {
        OrderNotFoundException(String message) {
            super(message);
        }
    }
}
```

## Example 2: Parameterized service rule checks

```java
package com.example.service;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;

class DiscountPolicyTest {

    private final DiscountPolicy discountPolicy = new DiscountPolicy();

    @ParameterizedTest
    @CsvSource({
            "50.00, 0.00",
            "100.00, 5.00",
            "250.00, 25.00"
    })
    void shouldComputeDiscountByThreshold(String amount, String expectedDiscount) {
        BigDecimal discount = discountPolicy.computeDiscount(new BigDecimal(amount));
        assertThat(discount).isEqualByComparingTo(new BigDecimal(expectedDiscount));
    }

    static class DiscountPolicy {
        BigDecimal computeDiscount(BigDecimal amount) {
            if (amount.compareTo(new BigDecimal("200.00")) >= 0) {
                return amount.multiply(new BigDecimal("0.10")).setScale(2);
            }
            if (amount.compareTo(new BigDecimal("100.00")) >= 0) {
                return amount.multiply(new BigDecimal("0.05")).setScale(2);
            }
            return BigDecimal.ZERO.setScale(2);
        }
    }
}
```
