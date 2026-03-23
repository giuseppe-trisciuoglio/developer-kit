# Aggregate Root with Event Publishing

## Aggregate Root Design

### Base Aggregate Root

```java
import jakarta.persistence.*;
import lombok.*;
import java.util.ArrayList;
import java.util.List;

@MappedSuperclass
@Getter
public abstract class AggregateRoot<ID> {
    @Transient
    protected List<DomainEvent> domainEvents = new ArrayList<>();

    public List<DomainEvent> getDomainEvents() {
        return new ArrayList<>(domainEvents);
    }

    public void clearDomainEvents() {
        domainEvents.clear();
    }

    protected void addDomainEvent(DomainEvent event) {
        domainEvents.add(event);
    }
}
```

### Product Aggregate

```java
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "products")
@Getter
@Setter(AccessLevel.PROTECTED)
@EqualsAndHashCode(of = "id")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Product extends AggregateRoot<ProductId> {

    @Id
    @Embedded
    private ProductId id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private Integer stock;

    // Factory method
    public static Product create(String name, BigDecimal price, Integer stock) {
        Product product = new Product();
        product.id = ProductId.generate();
        product.name = name;
        product.price = price;
        product.stock = stock;
        product.addDomainEvent(new ProductCreatedEvent(product.id, name, price, stock));
        return product;
    }

    // Domain behavior
    public void decreaseStock(Integer quantity) {
        if (this.stock < quantity) {
            throw new InsufficientStockException(
                String.format("Insufficient stock: requested=%d, available=%d",
                    quantity, this.stock)
            );
        }

        this.stock -= quantity;
        addDomainEvent(new ProductStockDecreasedEvent(this.id, quantity, this.stock));
    }

    public void increaseStock(Integer quantity) {
        this.stock += quantity;
        addDomainEvent(new ProductStockIncreasedEvent(this.id, quantity, this.stock));
    }

    public void updatePrice(BigDecimal newPrice) {
        if (newPrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidPriceException("Price must be positive");
        }

        BigDecimal oldPrice = this.price;
        this.price = newPrice;
        addDomainEvent(new ProductPriceUpdatedEvent(this.id, oldPrice, newPrice));
    }

    public void discontinue() {
        addDomainEvent(new ProductDiscontinuedEvent(this.id, this.name, this.stock));
    }

    @Embeddable
    @EqualsAndHashCode
    @NoArgsConstructor(access = AccessLevel.PROTECTED)
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    public static class ProductId {
        private String value;

        public static ProductId of(String value) {
            return new ProductId(value);
        }

        public static ProductId generate() {
            return new ProductId(UUID.randomUUID().toString());
        }

        @Override
        public String toString() {
            return value;
        }
    }
}
```

## Order Aggregate

```java
@Entity
@Table(name = "orders")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Order extends AggregateRoot<OrderId> {

    @Id
    @Embedded
    private OrderId id;

    @Embedded
    private CustomerId customerId;

    @ElementCollection
    @CollectionTable(name = "order_items", joinColumns = @JoinColumn(name = "order_id"))
    private List<OrderItem> items = new ArrayList<>();

    @Enumerated(Enum.STRING)
    private OrderStatus status;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount;

    public static Order create(CustomerId customerId, List<OrderItem> items) {
        Order order = new Order();
        order.id = OrderId.generate();
        order.customerId = customerId;
        order.items = List.copyOf(items);
        order.status = OrderStatus.PENDING;
        order.totalAmount = calculateTotal(items);
        order.addDomainEvent(new OrderCreatedEvent(
            order.id,
            order.customerId,
            order.items,
            order.totalAmount
        ));
        return order;
    }

    public void pay(PaymentMethod paymentMethod) {
        if (this.status != OrderStatus.PENDING) {
            throw new InvalidOrderStatusException(
                "Cannot pay order in status: " + this.status
            );
        }

        this.status = OrderStatus.PAID;
        addDomainEvent(new OrderPaidEvent(
            this.id,
            this.customerId,
            this.totalAmount,
            paymentMethod
        ));
    }

    public void ship(ShippingAddress shippingAddress) {
        if (this.status != OrderStatus.PAID) {
            throw new InvalidOrderStatusException(
                "Cannot ship order in status: " + this.status
            );
        }

        this.status = OrderStatus.SHIPPED;
        addDomainEvent(new OrderShippedEvent(
            this.id,
            this.customerId,
            shippingAddress
        ));
    }

    public void cancel(String reason) {
        if (this.status == OrderStatus.SHIPPED || this.status == OrderStatus.DELIVERED) {
            throw new InvalidOrderStatusException(
                "Cannot cancel order in status: " + this.status
            );
        }

        this.status = OrderStatus.CANCELLED;
        addDomainEvent(new OrderCancelledEvent(
            this.id,
            this.customerId,
            reason
        ));
    }

    private static BigDecimal calculateTotal(List<OrderItem> items) {
        return items.stream()
            .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    @Embeddable
    @EqualsAndHashCode
    @NoArgsConstructor(access = AccessLevel.PROTECTED)
    @AllArgsConstructor(access = AccessLevel.PRIVATE)
    public static class OrderId {
        private String value;

        public static OrderId of(String value) {
            return new OrderId(value);
        }

        public static OrderId generate() {
            return new OrderId(UUID.randomUUID().toString());
        }
    }

    @Embeddable
    @AllArgsConstructor
    @NoArgsConstructor
    public static class OrderItem {
        private ProductId productId;
        private String productName;
        private Integer quantity;
        private BigDecimal unitPrice;
    }

    public enum OrderStatus {
        PENDING, PAID, SHIPPED, DELIVERED, CANCELLED
    }
}
```

## Repository Pattern

```java
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ProductRepository extends JpaRepository<Product, Product.ProductId> {
    Optional<Product> findByProductName(String name);
}
```

## Application Service Pattern

```java
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public ProductResponse createProduct(CreateProductRequest request) {
        Product product = Product.create(
            request.getName(),
            request.getPrice(),
            request.getStock()
        );

        productRepository.save(product);

        // Publish domain events
        product.getDomainEvents().forEach(eventPublisher::publishEvent);
        product.clearDomainEvents();

        return mapToResponse(product);
    }

    @Transactional
    public void decreaseStock(DecreaseStockRequest request) {
        Product product = productRepository.findById(request.getProductId())
            .orElseThrow(() -> new ProductNotFoundException(request.getProductId()));

        product.decreaseStock(request.getQuantity());

        productRepository.save(product);

        // Publish domain events
        product.getDomainEvents().forEach(eventPublisher::publishEvent);
        product.clearDomainEvents();
    }

    private ProductResponse mapToResponse(Product product) {
        return new ProductResponse(
            product.getId().getValue(),
            product.getName(),
            product.getPrice(),
            product.getStock()
        );
    }
}
```
