# Java Clean Architecture Patterns

Specific patterns for implementing Clean Architecture in Java 21+ applications.

## Record Types for Value Objects

Java records provide immutability and automatic equals/hashCode implementation.

```java
// Value object with validation
public record Email(String value) {
    private static final Pattern PATTERN = Pattern.compile("^[A-Za-z0-9+_.-]+@(.+)$");

    public Email {
        if (value == null || !PATTERN.matcher(value).matches()) {
            throw new IllegalArgumentException("Invalid email: " + value);
        }
    }

    public String domain() {
        return value.substring(value.indexOf('@') + 1);
    }
}

// Complex value object with multiple fields
public record Address(
    String street,
    String city,
    String postalCode,
    String country
) {
    public Address {
        Objects.requireNonNull(street, "Street is required");
        Objects.requireNonNull(city, "City is required");
    }

    public String formatted() {
        return String.format("%s, %s %s, %s", street, city, postalCode, country);
    }
}
```

## Sealed Classes for Domain Events

Use sealed classes to control event inheritance.

```java
public sealed interface DomainEvent {
    Instant occurredAt();
    String aggregateId();
}

public record OrderCreatedEvent(
    OrderId orderId,
    Money total,
    Instant occurredAt
) implements DomainEvent {
    public OrderCreatedEvent {
        Objects.requireNonNull(orderId);
        Objects.requireNonNull(total);
        Objects.requireNonNull(occurredAt);
    }

    @Override
    public String aggregateId() {
        return orderId.value().toString();
    }
}

public record OrderConfirmedEvent(
    OrderId orderId,
    Instant confirmedAt
) implements DomainEvent {}
```

## Strongly-Typed IDs

Prevent ID confusion with type-safe wrappers.

```java
public record OrderId(UUID value) {
    public OrderId {
        Objects.requireNonNull(value, "OrderId cannot be null");
    }

    public static OrderId generate() {
        return new OrderId(UUID.randomUUID());
    }

    public static OrderId fromString(String id) {
        return new OrderId(UUID.fromString(id));
    }
}

public record CustomerId(UUID value) {
    public CustomerId {
        Objects.requireNonNull(value);
    }
}
```

## Factory Methods in Entities

Centralize creation logic and enforce invariants.

```java
public class Product {
    private final ProductId id;
    private String name;
    private String description;
    private Money price;
    private Stock stock;

    // Private constructor - use factory methods
    private Product(ProductId id, String name, Money price) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.stock = Stock.zero();
    }

    public static Product create(String name, Money price) {
        validateName(name);
        validatePrice(price);
        return new Product(ProductId.generate(), name, price);
    }

    public static Product reconstitute(ProductId id, String name, Money price, Stock stock) {
        Product product = new Product(id, name, price);
        product.stock = stock;
        return product;
    }

    private static void validateName(String name) {
        if (name == null || name.isBlank() || name.length() > 100) {
            throw new DomainException("Product name must be 1-100 characters");
        }
    }

    public void updatePrice(Money newPrice) {
        if (newPrice.amount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new DomainException("Price must be positive");
        }
        this.price = newPrice;
    }
}
```

## Result Type for Operations

Explicit handling of success/failure without exceptions.

```java
public sealed interface Result<T, E> {
    record Success<T, E>(T value) implements Result<T, E> {}
    record Failure<T, E>(E error) implements Result<T, E> {}

    default boolean isSuccess() {
        return this instanceof Success;
    }

    default Optional<T> getValue() {
        return this instanceof Success<T, E> s ? Optional.of(s.value()) : Optional.empty();
    }
}

// Usage in domain
public Result<Order, OrderError> confirm() {
    if (status != OrderStatus.PENDING) {
        return new Result.Failure<>(OrderError.ALREADY_CONFIRMED);
    }
    if (items.isEmpty()) {
        return new Result.Failure<>(OrderError.EMPTY_ORDER);
    }
    this.status = OrderStatus.CONFIRMED;
    return new Result.Success<>(this);
}
```

## Builder Pattern for Complex Aggregates

```java
public class Order {
    private final OrderId id;
    private final CustomerId customerId;
    private final List<OrderItem> items;
    private ShippingAddress shippingAddress;
    private PaymentMethod paymentMethod;

    private Order(Builder builder) {
        this.id = builder.id;
        this.customerId = builder.customerId;
        this.items = List.copyOf(builder.items);
        this.shippingAddress = builder.shippingAddress;
        this.paymentMethod = builder.paymentMethod;
    }

    public static Builder builder(CustomerId customerId) {
        return new Builder(customerId);
    }

    public static class Builder {
        private OrderId id = OrderId.generate();
        private final CustomerId customerId;
        private List<OrderItem> items = new ArrayList<>();
        private ShippingAddress shippingAddress;
        private PaymentMethod paymentMethod;

        private Builder(CustomerId customerId) {
            this.customerId = Objects.requireNonNull(customerId);
        }

        public Builder withItem(ProductId product, int quantity, Money price) {
            items.add(new OrderItem(product, quantity, price));
            return this;
        }

        public Builder shippingTo(ShippingAddress address) {
            this.shippingAddress = address;
            return this;
        }

        public Builder paidWith(PaymentMethod method) {
            this.paymentMethod = method;
            return this;
        }

        public Order build() {
            if (items.isEmpty()) {
                throw new DomainException("Order must have at least one item");
            }
            return new Order(this);
        }
    }
}

// Usage
Order order = Order.builder(customerId)
    .withItem(product1, 2, new Money("29.99", EUR))
    .withItem(product2, 1, new Money("49.99", EUR))
    .shippingTo(new ShippingAddress("123 Main St", "City", "12345"))
    .paidWith(PaymentMethod.CREDIT_CARD)
    .build();
```

## Domain Service Pattern

When logic doesn't belong to a single entity.

```java
// Domain service interface
public interface PricingService {
    Money calculateTotal(List<OrderItem> items, CustomerType customerType);
}

// Domain service implementation (still framework-free)
public class StandardPricingService implements PricingService {
    private static final BigDecimal VIP_DISCOUNT = new BigDecimal("0.90");

    @Override
    public Money calculateTotal(List<OrderItem> items, CustomerType customerType) {
        Money subtotal = items.stream()
            .map(OrderItem::getSubtotal)
            .reduce(Money.zero(), Money::add);

        return customerType == CustomerType.VIP
            ? subtotal.multiply(VIP_DISCOUNT)
            : subtotal;
    }
}
```

## Specification Pattern

Encapsulate business rules as composable objects.

```java
public interface Specification<T> {
    boolean isSatisfiedBy(T candidate);

    default Specification<T> and(Specification<T> other) {
        return candidate -> this.isSatisfiedBy(candidate) && other.isSatisfiedBy(candidate);
    }

    default Specification<T> not() {
        return candidate -> !this.isSatisfiedBy(candidate);
    }
}

// Usage
public class OrderSpecifications {
    public static Specification<Order> isPending() {
        return order -> order.getStatus() == OrderStatus.PENDING;
    }

    public static Specification<Order> hasMinimumValue(Money minimum) {
        return order -> order.getTotal().amount().compareTo(minimum.amount()) >= 0;
    }

    public static Specification<Order> isEligibleForAutoApproval() {
        return isPending().and(hasMinimumValue(new Money("1000.00", EUR))).not();
    }
}
```

## Thread-Safe Domain Events

```java
public abstract class AggregateRoot {
    private final List<DomainEvent> domainEvents = new CopyOnWriteArrayList<>();

    protected void registerEvent(DomainEvent event) {
        domainEvents.add(event);
    }

    public List<DomainEvent> getDomainEvents() {
        return List.copyOf(domainEvents);
    }

    public void clearDomainEvents() {
        domainEvents.clear();
    }
}
```
