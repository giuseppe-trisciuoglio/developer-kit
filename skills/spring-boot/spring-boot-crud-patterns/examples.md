# Spring Boot CRUD Patterns - Examples

Comprehensive examples demonstrating REST CRUD APIs with DDD, feature-based architecture, and constructor injection patterns.

## Example 1: Complete Feature-Based CRUD API

A production-ready example of a product management feature with all layers.

### Domain Layer

```java
// feature/product/domain/model/ProductId.java
@Value
@RequiredArgsConstructor(staticName = "of")
public class ProductId {
    @NonNull String value;

    public static ProductId random() {
        return ProductId.of(UUID.randomUUID().toString());
    }
}

// feature/product/domain/model/Money.java
@Value
@RequiredArgsConstructor(staticName = "of")
public class Money {
    @NonNull BigDecimal amount;
    @NonNull String currency;

    public Money(BigDecimal amount) {
        this.amount = Objects.requireNonNull(amount, "Amount cannot be null");
        this.currency = "EUR";
    }

    public boolean isPositive() {
        return amount.compareTo(BigDecimal.ZERO) > 0;
    }

    public Money multiply(BigDecimal factor) {
        return Money.of(amount.multiply(factor), currency);
    }
}

// feature/product/domain/model/Stock.java
@Value
@RequiredArgsConstructor(staticName = "of")
public class Stock {
    @NonNull Integer quantity;

    public boolean isAvailable(Integer requested) {
        return quantity >= requested;
    }

    public Stock decrease(Integer amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        if (!isAvailable(amount)) throw new IllegalArgumentException("Insufficient stock");
        return Stock.of(quantity - amount);
    }

    public Stock increase(Integer amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        return Stock.of(quantity + amount);
    }
}

// feature/product/domain/model/Product.java
@Getter
@ToString
@EqualsAndHashCode(of = "id")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Product {
    private ProductId id;
    private String name;
    private String description;
    private Money price;
    private Stock stock;
    private ProductStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @Builder
    private Product(ProductId id, String name, String description,
                   Money price, Stock stock, ProductStatus status) {
        this.id = id != null ? id : ProductId.random();
        this.name = Objects.requireNonNull(name, "Name cannot be null");
        this.description = description;
        this.price = Objects.requireNonNull(price, "Price cannot be null");
        this.stock = Objects.requireNonNull(stock, "Stock cannot be null");
        this.status = status != null ? status : ProductStatus.ACTIVE;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        validateInvariants();
    }

    public static Product create(String name, String description, 
                                BigDecimal priceAmount, Integer stockQuantity) {
        return Product.builder()
            .name(name)
            .description(description)
            .price(Money.of(priceAmount))
            .stock(Stock.of(stockQuantity))
            .build();
    }

    public void updateDetails(String name, String description, Money price) {
        this.name = Objects.requireNonNull(name);
        this.description = description;
        this.price = Objects.requireNonNull(price);
        this.updatedAt = LocalDateTime.now();
        validateInvariants();
    }

    public void updateStock(Integer quantity) {
        if (quantity < 0) throw new IllegalArgumentException("Stock cannot be negative");
        this.stock = Stock.of(quantity);
        this.updatedAt = LocalDateTime.now();
    }

    public void markDiscontinued() {
        this.status = ProductStatus.DISCONTINUED;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isActive() {
        return status == ProductStatus.ACTIVE;
    }

    private void validateInvariants() {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Product name cannot be blank");
        }
        if (!price.isPositive()) {
            throw new IllegalArgumentException("Price must be positive");
        }
    }
}
```

### Application Layer

```java
// feature/product/application/dto/CreateProductRequest.java
public record CreateProductRequest(
    @NotBlank(message = "Name is required") String name,
    @NotNull(message = "Price is required") BigDecimal price,
    String description,
    @NotNull(message = "Stock quantity is required") Integer stockQuantity
) {}

// feature/product/application/dto/UpdateProductRequest.java
public record UpdateProductRequest(
    @NotBlank(message = "Name is required") String name,
    @NotNull(message = "Price is required") BigDecimal price,
    String description
) {}

// feature/product/application/dto/ProductResponse.java
public record ProductResponse(
    String id,
    String name,
    String description,
    BigDecimal price,
    String currency,
    Integer stock,
    String status,
    LocalDateTime createdAt,
    LocalDateTime updatedAt
) {}

// feature/product/application/service/ProductApplicationService.java
@Service
@Slf4j
@RequiredArgsConstructor
@Transactional
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ProductMapper mapper;

    public ProductResponse createProduct(CreateProductRequest request) {
        log.info("Creating product: {}", request.name());
        
        Product product = Product.create(
            request.name(),
            request.description(),
            request.price(),
            request.stockQuantity()
        );

        Product saved = productRepository.save(product);
        log.info("Product created with id: {}", saved.getId().getValue());
        
        return mapper.toResponse(saved);
    }

    @Transactional(readOnly = true)
    public ProductResponse getProductById(String id) {
        return productRepository.findById(ProductId.of(id))
            .map(mapper::toResponse)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found: " + id));
    }

    @Transactional(readOnly = true)
    public List<ProductResponse> getAllProducts() {
        return productRepository.findAll().stream()
            .map(mapper::toResponse)
            .collect(Collectors.toList());
    }

    public ProductResponse updateProduct(String id, UpdateProductRequest request) {
        log.info("Updating product: {}", id);
        
        Product product = productRepository.findById(ProductId.of(id))
            .orElseThrow(() -> new ResourceNotFoundException("Product not found: " + id));

        product.updateDetails(
            request.name(),
            request.description(),
            Money.of(request.price())
        );

        Product updated = productRepository.save(product);
        return mapper.toResponse(updated);
    }

    public void deleteProduct(String id) {
        log.info("Deleting product: {}", id);
        productRepository.delete(ProductId.of(id));
    }
}

// feature/product/application/mapper/ProductMapper.java
@Component
public class ProductMapper {
    public ProductResponse toResponse(Product product) {
        return new ProductResponse(
            product.getId().getValue(),
            product.getName(),
            product.getDescription(),
            product.getPrice().getAmount(),
            product.getPrice().getCurrency(),
            product.getStock().getQuantity(),
            product.getStatus().name(),
            product.getCreatedAt(),
            product.getUpdatedAt()
        );
    }

    public ProductJpaEntity toEntity(Product product) {
        return ProductJpaEntity.builder()
            .id(product.getId().getValue())
            .name(product.getName())
            .description(product.getDescription())
            .price(product.getPrice().getAmount())
            .currency(product.getPrice().getCurrency())
            .stock(product.getStock().getQuantity())
            .status(product.getStatus().name())
            .createdAt(product.getCreatedAt())
            .updatedAt(product.getUpdatedAt())
            .build();
    }

    public Product toDomain(ProductJpaEntity entity) {
        return Product.builder()
            .id(ProductId.of(entity.getId()))
            .name(entity.getName())
            .description(entity.getDescription())
            .price(Money.of(entity.getPrice(), entity.getCurrency()))
            .stock(Stock.of(entity.getStock()))
            .status(ProductStatus.valueOf(entity.getStatus()))
            .build();
    }
}
```

### Presentation Layer

```java
// feature/product/presentation/rest/ProductController.java
@RestController
@RequestMapping("/api/v1/products")
@RequiredArgsConstructor
@Slf4j
public class ProductController {
    private final ProductApplicationService productService;

    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(
            @Valid @RequestBody CreateProductRequest request) {
        ProductResponse response = productService.createProduct(request);
        return ResponseEntity
            .created(URI.create("/api/v1/products/" + response.id()))
            .body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable String id) {
        return ResponseEntity.ok(productService.getProductById(id));
    }

    @GetMapping
    public ResponseEntity<List<ProductResponse>> getAllProducts() {
        return ResponseEntity.ok(productService.getAllProducts());
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> updateProduct(
            @PathVariable String id,
            @Valid @RequestBody UpdateProductRequest request) {
        ProductResponse response = productService.updateProduct(id, request);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable String id) {
        productService.deleteProduct(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

## Example 2: Custom Exception Handling

```java
// Shared exceptions
public class DomainException extends RuntimeException {
    public DomainException(String message) {
        super(message);
    }
}

public class ResourceNotFoundException extends DomainException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}

public class InvalidProductException extends DomainException {
    public InvalidProductException(String message) {
        super(message);
    }
}

// Global exception handler
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex, HttpServletRequest request) {
        log.warn("Resource not found: {}", ex.getMessage());
        
        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            "NOT_FOUND",
            ex.getMessage(),
            request.getRequestURI(),
            LocalDateTime.now()
        );
        
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex, HttpServletRequest request) {
        String errors = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));

        ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "VALIDATION_ERROR",
            errors,
            request.getRequestURI(),
            LocalDateTime.now()
        );
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(
            Exception ex, HttpServletRequest request) {
        log.error("Unexpected error occurred", ex);
        
        ErrorResponse error = new ErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "INTERNAL_SERVER_ERROR",
            "An unexpected error occurred",
            request.getRequestURI(),
            LocalDateTime.now()
        );
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}

@Data
@AllArgsConstructor
class ErrorResponse {
    private int status;
    private String code;
    private String message;
    private String path;
    private LocalDateTime timestamp;
}
```

---

## Example 3: Advanced Pagination and Filtering

```java
// feature/product/presentation/rest/ProductController.java (extended)
@GetMapping
public ResponseEntity<PageResponse<ProductResponse>> getAllProducts(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(defaultValue = "createdAt") String sortBy,
        @RequestParam(defaultValue = "DESC") String sortDirection,
        @RequestParam(required = false) String nameFilter,
        @RequestParam(required = false) BigDecimal minPrice,
        @RequestParam(required = false) BigDecimal maxPrice) {
    
    Sort sort = Sort.by(Sort.Direction.valueOf(sortDirection), sortBy);
    Pageable pageable = PageRequest.of(page, size, sort);
    
    ProductFilter filter = ProductFilter.builder()
        .name(nameFilter)
        .minPrice(minPrice)
        .maxPrice(maxPrice)
        .build();
    
    Page<ProductResponse> responses = productService.searchProducts(filter, pageable);
    
    PageResponse<ProductResponse> pageResponse = new PageResponse<>(
        responses.getContent(),
        responses.getNumber(),
        responses.getSize(),
        responses.getTotalElements(),
        responses.getTotalPages(),
        responses.isLast()
    );
    
    return ResponseEntity
        .ok()
        .header("X-Total-Count", String.valueOf(responses.getTotalElements()))
        .body(pageResponse);
}

// Data transfer object for pagination
@Data
@AllArgsConstructor
class PageResponse<T> {
    private List<T> content;
    private int pageNumber;
    private int pageSize;
    private long totalElements;
    private int totalPages;
    private boolean isLast;
}

// Filter criteria
@Data
@Builder
class ProductFilter {
    private String name;
    private BigDecimal minPrice;
    private BigDecimal maxPrice;
}

// Repository with custom query
@Repository
public interface ProductJpaRepository extends JpaRepository<ProductJpaEntity, String> {
    Page<ProductJpaEntity> findByNameContainingAndPriceBetween(
        String name, BigDecimal minPrice, BigDecimal maxPrice, Pageable pageable);
}

// Service with filtering
@Transactional(readOnly = true)
public Page<ProductResponse> searchProducts(ProductFilter filter, Pageable pageable) {
    Page<ProductJpaEntity> results = productJpaRepository
        .findByNameContainingAndPriceBetween(
            filter.getName() != null ? filter.getName() : "",
            filter.getMinPrice() != null ? filter.getMinPrice() : BigDecimal.ZERO,
            filter.getMaxPrice() != null ? filter.getMaxPrice() : BigDecimal.valueOf(Long.MAX_VALUE),
            pageable
        );
    
    return results.map(mapper::toDomain).map(mapper::toResponse);
}
```

---

## Example 4: Integration Tests

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class ProductControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private ProductRepository productRepository;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @BeforeEach
    void setUp() {
        productRepository.deleteAll();
    }

    @Test
    void shouldCreateProductAndReturn201() {
        // Arrange
        CreateProductRequest request = new CreateProductRequest(
            "Test Laptop", BigDecimal.valueOf(999.99), "A great laptop", 10
        );

        // Act
        ResponseEntity<ProductResponse> response = restTemplate.postForEntity(
            "/api/v1/products", request, ProductResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().name()).isEqualTo("Test Laptop");
        assertThat(response.getHeaders().getLocation()).isNotNull();
    }

    @Test
    void shouldRetrieveProductById() {
        // Arrange
        Product product = Product.create(
            "Test Product", "Description", BigDecimal.valueOf(100.00), 5
        );
        Product saved = productRepository.save(product);

        // Act
        ResponseEntity<ProductResponse> response = restTemplate.getForEntity(
            "/api/v1/products/" + saved.getId().getValue(),
            ProductResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().name()).isEqualTo("Test Product");
    }

    @Test
    void shouldReturn404ForNonExistentProduct() {
        // Act
        ResponseEntity<String> response = restTemplate.getForEntity(
            "/api/v1/products/non-existent-id",
            String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void shouldUpdateProduct() {
        // Arrange
        Product product = Product.create(
            "Original", "Desc", BigDecimal.valueOf(50.00), 5
        );
        Product saved = productRepository.save(product);
        
        UpdateProductRequest updateRequest = new UpdateProductRequest(
            "Updated", BigDecimal.valueOf(75.00), "Updated Desc"
        );

        // Act
        ResponseEntity<ProductResponse> response = restTemplate.exchange(
            "/api/v1/products/" + saved.getId().getValue(),
            HttpMethod.PUT,
            new HttpEntity<>(updateRequest),
            ProductResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().name()).isEqualTo("Updated");
        assertThat(response.getBody().price()).isEqualTo(BigDecimal.valueOf(75.00));
    }

    @Test
    void shouldDeleteProduct() {
        // Arrange
        Product product = Product.create(
            "To Delete", "Desc", BigDecimal.valueOf(100.00), 5
        );
        Product saved = productRepository.save(product);

        // Act
        ResponseEntity<Void> response = restTemplate.exchange(
            "/api/v1/products/" + saved.getId().getValue(),
            HttpMethod.DELETE,
            null,
            Void.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NO_CONTENT);
        assertThat(productRepository.findById(saved.getId())).isEmpty();
    }
}
```

---

## Example 5: Flyway Database Migration

```sql
-- db/migration/V1__create_products_table.sql
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    stock INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (price > 0),
    CHECK (stock >= 0)
);

-- db/migration/V2__create_product_indexes.sql
CREATE INDEX idx_product_status ON products(status);
CREATE INDEX idx_product_created_at ON products(created_at DESC);
```

These examples provide a complete, production-ready implementation of REST CRUD APIs following DDD principles with feature-based architecture.
