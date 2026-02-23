# Product Feature Examples (Spring Boot 3.x)

## Suggested feature structure

- `product/domain/model/Product.java`
- `product/domain/repository/ProductRepository.java`
- `product/infrastructure/persistence/ProductEntity.java`
- `product/infrastructure/persistence/SpringDataProductRepository.java`
- `product/infrastructure/persistence/ProductRepositoryAdapter.java`
- `product/application/ProductService.java`
- `product/presentation/dto/ProductCreateRequest.java`
- `product/presentation/dto/ProductResponse.java`
- `product/presentation/rest/ProductController.java`

## Domain model

```java
package com.example.product.domain.model;

import java.math.BigDecimal;
import java.util.Objects;

public class Product {

    private final Long id;
    private String name;
    private BigDecimal price;
    private int stock;

    private Product(Long id, String name, BigDecimal price, int stock) {
        this.id = id;
        this.name = requireName(name);
        this.price = requirePrice(price);
        this.stock = requireStock(stock);
    }

    public static Product create(String name, BigDecimal price, int stock) {
        return new Product(null, name, price, stock);
    }

    public static Product rehydrate(Long id, String name, BigDecimal price, int stock) {
        return new Product(id, name, price, stock);
    }

    public void update(String newName, BigDecimal newPrice, int newStock) {
        this.name = requireName(newName);
        this.price = requirePrice(newPrice);
        this.stock = requireStock(newStock);
    }

    public Long id() {
        return id;
    }

    public String name() {
        return name;
    }

    public BigDecimal price() {
        return price;
    }

    public int stock() {
        return stock;
    }

    private static String requireName(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("name is required");
        }
        return value;
    }

    private static BigDecimal requirePrice(BigDecimal value) {
        Objects.requireNonNull(value, "price is required");
        if (value.signum() < 0) {
            throw new IllegalArgumentException("price must be >= 0");
        }
        return value;
    }

    private static int requireStock(int value) {
        if (value < 0) {
            throw new IllegalArgumentException("stock must be >= 0");
        }
        return value;
    }
}
```

## Repository port and persistence adapter

```java
package com.example.product.domain.repository;

import com.example.product.domain.model.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.Optional;

public interface ProductRepository {
    Product save(Product product);
    Optional<Product> findById(Long id);
    Page<Product> findAll(Pageable pageable);
    boolean existsByName(String name);
    void deleteById(Long id);
}
```

```java
package com.example.product.infrastructure.persistence;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.math.BigDecimal;

@Entity
@Table(name = "products")
public class ProductEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 120)
    private String name;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal price;

    @Column(nullable = false)
    private Integer stock;

    protected ProductEntity() {
    }

    ProductEntity(Long id, String name, BigDecimal price, Integer stock) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.stock = stock;
    }

    Long getId() {
        return id;
    }

    String getName() {
        return name;
    }

    BigDecimal getPrice() {
        return price;
    }

    Integer getStock() {
        return stock;
    }
}
```

```java
package com.example.product.infrastructure.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

public interface SpringDataProductRepository extends JpaRepository<ProductEntity, Long> {
    boolean existsByNameIgnoreCase(String name);
}
```

```java
package com.example.product.infrastructure.persistence;

import com.example.product.domain.model.Product;
import com.example.product.domain.repository.ProductRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public class ProductRepositoryAdapter implements ProductRepository {

    private final SpringDataProductRepository jpaRepository;

    public ProductRepositoryAdapter(SpringDataProductRepository jpaRepository) {
        this.jpaRepository = jpaRepository;
    }

    @Override
    public Product save(Product product) {
        ProductEntity saved = jpaRepository.save(toEntity(product));
        return toDomain(saved);
    }

    @Override
    public Optional<Product> findById(Long id) {
        return jpaRepository.findById(id).map(this::toDomain);
    }

    @Override
    public Page<Product> findAll(Pageable pageable) {
        return jpaRepository.findAll(pageable).map(this::toDomain);
    }

    @Override
    public boolean existsByName(String name) {
        return jpaRepository.existsByNameIgnoreCase(name);
    }

    @Override
    public void deleteById(Long id) {
        jpaRepository.deleteById(id);
    }

    private ProductEntity toEntity(Product product) {
        return new ProductEntity(product.id(), product.name(), product.price(), product.stock());
    }

    private Product toDomain(ProductEntity entity) {
        return Product.rehydrate(entity.getId(), entity.getName(), entity.getPrice(), entity.getStock());
    }
}
```

## Application service

```java
package com.example.product.application;

import com.example.product.domain.model.Product;
import com.example.product.domain.repository.ProductRepository;
import com.example.product.presentation.dto.ProductCreateRequest;
import com.example.product.presentation.dto.ProductResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProductService {

    private final ProductRepository repository;

    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public ProductResponse create(ProductCreateRequest request) {
        if (repository.existsByName(request.name())) {
            throw new IllegalStateException("product name already exists");
        }
        Product saved = repository.save(Product.create(request.name(), request.price(), request.stock()));
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public ProductResponse getById(Long id) {
        Product product = repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("product not found"));
        return toResponse(product);
    }

    @Transactional(readOnly = true)
    public Page<ProductResponse> list(Pageable pageable) {
        return repository.findAll(pageable).map(this::toResponse);
    }

    @Transactional
    public ProductResponse update(Long id, ProductCreateRequest request) {
        Product product = repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("product not found"));
        product.update(request.name(), request.price(), request.stock());
        return toResponse(repository.save(product));
    }

    @Transactional
    public void delete(Long id) {
        repository.deleteById(id);
    }

    private ProductResponse toResponse(Product product) {
        return new ProductResponse(product.id(), product.name(), product.price(), product.stock());
    }
}
```

## DTOs

```java
package com.example.product.presentation.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

import java.math.BigDecimal;

public record ProductCreateRequest(
        @NotBlank String name,
        @NotNull @DecimalMin("0.00") BigDecimal price,
        @NotNull @PositiveOrZero Integer stock
) {
}
```

```java
package com.example.product.presentation.dto;

import java.math.BigDecimal;

public record ProductResponse(Long id, String name, BigDecimal price, Integer stock) {
}
```
