# Spring Boot CRUD Examples

Progressive examples illustrating how to assemble CRUD features with Spring Boot 3.5+, Spring Data JPA, and feature-oriented architecture.

## Example 1: Basic RESTful CRUD (Starter)

```java
// domain/Product.java
@Entity
public class Product {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private String id;
    private String name;
    private BigDecimal price;

    protected Product() { }

    public Product(String name, BigDecimal price) {
        this.name = Objects.requireNonNull(name);
        this.price = Objects.requireNonNull(price);
    }
}

// infrastructure/ProductRepository.java
public interface ProductRepository extends JpaRepository<Product, String> { }

// presentation/ProductController.java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    @PostMapping
    ResponseEntity<Product> create(@RequestBody Product product) {
        Product saved = repository.save(product);
        URI location = URI.create("/api/products/" + saved.getId());
        return ResponseEntity.created(location).body(saved);
    }

    @GetMapping("/{id}")
    ResponseEntity<Product> findById(@PathVariable String id) {
        return repository.findById(id)
            .map(ResponseEntity::ok)
            .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @GetMapping
    List<Product> listAll() {
        return repository.findAll(Sort.by("name").ascending());
    }

    @DeleteMapping("/{id}")
    ResponseEntity<Void> delete(@PathVariable String id) {
        repository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

**Highlights**
- Demonstrates minimal repository and controller plumbing.
- Leverages HTTP semantics (201 Created, 404 Not Found, 204 No Content).
- Suitable for prototypes, spikes, or scaffolding CLI tooling.

## Example 2: Feature Package with Domain Services (Intermediate)

```java
// feature/product/domain/model/Product.java
@Getter
@EqualsAndHashCode(of = "id")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Product {
    private ProductId id;
    private String name;
    private Money price;
    private Stock stock;
    private ProductStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @Builder
    private Product(ProductId id, String name, Money price, Stock stock, ProductStatus status) {
        this.id = id != null ? id : ProductId.random();
        this.name = Objects.requireNonNull(name);
        this.price = Objects.requireNonNull(price);
        this.stock = Objects.requireNonNull(stock);
        this.status = Objects.requireNonNullElse(status, ProductStatus.ACTIVE);
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        validateInvariants();
    }

    public void updateDetails(String name, Money price) {
        this.name = Objects.requireNonNull(name);
        this.price = Objects.requireNonNull(price);
        this.updatedAt = LocalDateTime.now();
        validateInvariants();
    }

    public void discontinue() {
        this.status = ProductStatus.DISCONTINUED;
        this.updatedAt = LocalDateTime.now();
    }

    private void validateInvariants() {
        if (name.isBlank()) {
            throw new IllegalArgumentException("Product name cannot be blank");
        }
        if (price.isNotPositive()) {
            throw new IllegalArgumentException("Price must be positive");
        }
    }
}

// feature/product/application/service/ProductApplicationService.java
@Service
@Transactional
@RequiredArgsConstructor
public class ProductApplicationService {
    private final ProductRepository productRepository;
    private final ProductMapper mapper;

    public ProductResponse createProduct(CreateProductRequest request) {
        Product aggregate = Product.create(
            request.name(),
            request.description(),
            Money.of(request.price()),
            Stock.of(request.stockQuantity())
        );
        productRepository.save(aggregate);
        return mapper.toResponse(aggregate);
    }

    public ProductResponse updateProduct(String id, UpdateProductRequest request) {
        Product aggregate = productRepository.findById(ProductId.of(id))
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        aggregate.updateDetails(request.name(), Money.of(request.price()));
        return mapper.toResponse(productRepository.save(aggregate));
    }

    public void deleteProduct(String id) {
        productRepository.delete(ProductId.of(id));
    }
}

// feature/product/presentation/rest/ProductController.java
@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {
    private final ProductApplicationService productService;

    @PostMapping
    ResponseEntity<ProductResponse> create(@Valid @RequestBody CreateProductRequest request) {
        ProductResponse body = productService.createProduct(request);
        return ResponseEntity.created(URI.create("/api/products/" + body.id())).body(body);
    }

    @GetMapping("/{id}")
    ProductResponse findById(@PathVariable String id) {
        return productService.findProductById(id);
    }
}
```

**Highlights**
- Separates domain model, application service, and REST layer.
- Encapsulates invariants in domain aggregate.
- Encourages DTO records and dedicated mappers for presentation boundaries.

## Example 3: Advanced Concerns (Audit, Pagination, Batch) 

```java
// infrastructure/persistence/ProductEntity.java
@Entity
@Table(name = "products")
@EntityListeners(AuditingEntityListener.class)
public class ProductEntity extends AbstractPersistable<String> {
    private String name;
    private BigDecimal price;
    private Integer stock;
    private String status;

    @CreatedDate
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;
}

// infrastructure/persistence/ProductSpringDataRepository.java
public interface ProductSpringDataRepository extends JpaRepository<ProductEntity, String> {
    Page<ProductEntity> findByStatus(String status, Pageable pageable);

    @Modifying(clearAutomatically = true)
    @Query("update ProductEntity p set p.stock = :stock where p.id in :ids")
    int updateStockInBatch(@Param("ids") Collection<String> ids, @Param("stock") Integer stock);
}

// application/service/ProductQueryService.java
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class ProductQueryService {
    private final ProductSpringDataRepository repository;
    private final ProductMapper mapper;

    public Page<ProductResponse> findActiveProducts(PageRequest request) {
        return repository.findByStatus("ACTIVE", request)
            .map(mapper::toResponse);
    }

    public int bulkAdjustStock(BulkStockCommand command) {
        return repository.updateStockInBatch(command.ids(), command.stock());
    }
}

// test/ProductControllerIT.java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class ProductControllerIT {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createProductShouldReturn201() throws Exception {
        mockMvc.perform(post("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"name":"Keyboard","price":89.90,"stockQuantity":25}
                """))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"));
    }
}
```

**Highlights**
- Demonstrates Spring Data auditing, derived queries, pagination, and batch updates.
- Shows read/write service split for query heavy workloads.
- Provides integration testing with `MockMvc`.
