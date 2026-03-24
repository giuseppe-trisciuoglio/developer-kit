# Unit Testing Patterns

## Basic Unit Test with Mockito

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;
import static org.assertj.core.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks
    private UserService userService;

    @Test
    void shouldFindUserByIdWhenExists() {
        // Arrange
        Long userId = 1L;
        User user = new User();
        user.setId(userId);
        user.setEmail("test@example.com");

        when(userRepository.findById(userId)).thenReturn(Optional.of(user));

        // Act
        Optional<User> result = userService.findById(userId);

        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getEmail()).isEqualTo("test@example.com");
        verify(userRepository, times(1)).findById(userId);
    }

    @Test
    void shouldReturnEmptyWhenUserNotFound() {
        // Arrange
        Long userId = 999L;
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        // Act
        Optional<User> result = userService.findById(userId);

        // Assert
        assertThat(result).isEmpty();
        verify(userRepository, times(1)).findById(userId);
    }

    @Test
    void shouldThrowExceptionWhenCreatingUserWithInvalidEmail() {
        // Arrange
        CreateUserRequest request = new CreateUserRequest();
        request.setEmail("invalid-email");
        request.setName("Test User");

        // Act & Assert
        assertThatThrownBy(() -> userService.createUser(request))
            .isInstanceOf(InvalidEmailException.class)
            .hasMessage("Invalid email format");

        verify(userRepository, never()).save(any());
    }
}
```

## Testing Business Logic

```java
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private ProductService productService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void shouldCalculateTotalPrice() {
        // Arrange
        OrderItem item1 = new OrderItem();
        item1.setPrice(10.0);
        item1.setQuantity(2);

        OrderItem item2 = new OrderItem();
        item2.setPrice(15.0);
        item2.setQuantity(1);

        List<OrderItem> items = List.of(item1, item2);

        // Act
        double total = orderService.calculateTotal(items);

        // Assert
        assertThat(total).isEqualTo(35.0);
    }

    @Test
    void shouldApplyDiscountForLargeOrders() {
        // Arrange
        Order order = new Order();
        order.setTotal(1000.0);

        // Act
        orderService.applyDiscount(order, 10);

        // Assert
        assertThat(order.getTotal()).isEqualTo(900.0);
    }
}
```

## Testing Exception Scenarios

```java
@Test
void shouldThrowExceptionWhenInsufficientStock() {
    // Arrange
    OrderRequest request = new OrderRequest();
    request.setProductId(1L);
    request.setQuantity(100);

    when(productService.getStock(1L)).thenReturn(50);

    // Act & Assert
    assertThatThrownBy(() -> orderService.createOrder(request))
        .isInstanceOf(InsufficientStockException.class)
        .hasMessageContaining("Insufficient stock");
}
```

## Parameterized Tests

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

class ParameterizedUserServiceTest {

    @ParameterizedTest
    @ValueSource(strings = {"user@example.com", "test@test.com", "admin@domain.com"})
    void shouldAcceptValidEmails(String email) {
        assertThat(userService.isValidEmail(email)).isTrue();
    }

    @ParameterizedTest
    @CsvSource({
        "10, 2, 20",
        "5, 3, 15",
        "100, 0, 0"
    })
    void shouldCalculateTotalCorrectly(double price, int quantity, double expectedTotal) {
        assertThat(orderService.calculateTotal(price, quantity))
            .isEqualTo(expectedTotal);
    }

    @ParameterizedTest
    @MethodSource("provideInvalidEmails")
    void shouldRejectInvalidEmails(String email) {
        assertThat(userService.isValidEmail(email)).isFalse();
    }

    private static Stream<String> provideInvalidEmails() {
        return Stream.of(
            "invalid",
            "@example.com",
            "user@",
            "user @example.com"
        );
    }
}
```

## Test Fixtures

```java
class UserTestFixture {
    public static User createTestUser() {
        User user = new User();
        user.setId(1L);
        user.setEmail("test@example.com");
        user.setName("Test User");
        return user;
    }

    public static CreateUserRequest createTestRequest() {
        CreateUserRequest request = new CreateUserRequest();
        request.setEmail("new@example.com");
        request.setName("New User");
        return request;
    }
}

class UserServiceTest {
    @Test
    void shouldCreateUser() {
        CreateUserRequest request = UserTestFixture.createTestRequest();

        User result = userService.createUser(request);

        assertThat(result.getEmail()).isEqualTo(request.getEmail());
    }
}
```
