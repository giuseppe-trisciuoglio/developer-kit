# Spring Data JPA - Code Examples

## Example 1: Simple CRUD Application

### Entity Classes

```java
@Entity
@Table(name = "categories")
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 100)
    private String name;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    @OneToMany(mappedBy = "category", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Product> products = new ArrayList<>();
    
    public Category() {}
    
    public Category(String name) {
        this.name = name;
    }
    
    // getters, setters, equals, hashCode
}

@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 255)
    private String name;
    
    @Column(precision = 10, scale = 2)
    private BigDecimal price;
    
    @Column(columnDefinition = "INT DEFAULT 0")
    private Integer stock;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;
    
    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    private LocalDateTime updatedAt;
    
    public Product() {}
    
    public Product(String name, BigDecimal price, Category category) {
        this.name = name;
        this.price = price;
        this.category = category;
    }
    
    // getters, setters
}
```

### Repository Interfaces

```java
@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {
    Optional<Category> findByName(String name);
    boolean existsByName(String name);
}

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory(Category category);
    List<Product> findByCategoryAndPriceGreaterThan(Category category, BigDecimal price);
    Page<Product> findByNameContainingIgnoreCase(String name, Pageable pageable);
    
    @Query("SELECT p FROM Product p WHERE p.stock = 0 ORDER BY p.updatedAt DESC")
    List<Product> findOutOfStockProducts();
    
    @Query("SELECT p FROM Product p WHERE p.price BETWEEN :minPrice AND :maxPrice")
    List<Product> findByPriceRange(
        @Param("minPrice") BigDecimal minPrice,
        @Param("maxPrice") BigDecimal maxPrice
    );
}
```

### Service Layer

```java
@Service
@Transactional
public class ProductService {
    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;
    
    public ProductService(ProductRepository productRepository,
                         CategoryRepository categoryRepository) {
        this.productRepository = productRepository;
        this.categoryRepository = categoryRepository;
    }
    
    @Transactional(readOnly = true)
    public Page<Product> searchProducts(String query, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return productRepository.findByNameContainingIgnoreCase(query, pageable);
    }
    
    @Transactional(readOnly = true)
    public List<Product> getProductsByCategory(Long categoryId) {
        Category category = categoryRepository.findById(categoryId)
            .orElseThrow(() -> new CategoryNotFoundException(categoryId));
        return productRepository.findByCategory(category);
    }
    
    @Transactional(readOnly = true)
    public List<Product> getExpensiveProducts(Long categoryId, BigDecimal minPrice) {
        Category category = categoryRepository.findById(categoryId)
            .orElseThrow(() -> new CategoryNotFoundException(categoryId));
        return productRepository.findByCategoryAndPriceGreaterThan(category, minPrice);
    }
    
    public Product createProduct(CreateProductRequest request) {
        Category category = categoryRepository.findById(request.categoryId())
            .orElseThrow(() -> new CategoryNotFoundException(request.categoryId()));
        
        Product product = new Product(request.name(), request.price(), category);
        return productRepository.save(product);
    }
    
    public Product updateProduct(Long id, UpdateProductRequest request) {
        Product product = productRepository.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));
        
        product.setName(request.name());
        product.setPrice(request.price());
        
        return productRepository.save(product);
    }
    
    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }
    
    @Transactional(readOnly = true)
    public List<Product> getOutOfStockProducts() {
        return productRepository.findOutOfStockProducts();
    }
}

record CreateProductRequest(String name, BigDecimal price, Long categoryId) {}
record UpdateProductRequest(String name, BigDecimal price) {}
```

## Example 2: Complex Query with Auditing

```java
@Entity
@Table(name = "orders")
@EntityListeners(AuditingEntityListener.class)
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String orderNumber;
    private String status;  // PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED
    
    @Column(precision = 12, scale = 2)
    private BigDecimal totalAmount;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;
    
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();
    
    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    private LocalDateTime modifiedAt;
    
    @CreatedBy
    @Column(nullable = false, updatable = false)
    private String createdBy;
    
    @LastModifiedBy
    private String modifiedBy;
    
    // getters, setters, methods
}

@Entity
@Table(name = "order_items")
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;
    
    private Integer quantity;
    
    @Column(precision = 10, scale = 2)
    private BigDecimal unitPrice;
    
    // getters, setters
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("""
        SELECT o FROM Order o
        JOIN FETCH o.items i
        JOIN FETCH o.customer
        WHERE o.status = :status
        ORDER BY o.createdAt DESC
        """)
    List<Order> findOrdersWithItems(@Param("status") String status);
    
    @Query("""
        SELECT o FROM Order o
        WHERE o.customer.id = :customerId
        AND o.createdAt BETWEEN :startDate AND :endDate
        """)
    List<Order> findCustomerOrdersByDateRange(
        @Param("customerId") Long customerId,
        @Param("startDate") LocalDateTime startDate,
        @Param("endDate") LocalDateTime endDate
    );
    
    @Query(value = """
        SELECT o.id, o.order_number, SUM(oi.quantity * oi.unit_price) as total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.status = :status
        GROUP BY o.id
        HAVING total > :minAmount
        """, nativeQuery = true)
    List<Map<String, Object>> findHighValueOrdersByStatus(
        @Param("status") String status,
        @Param("minAmount") BigDecimal minAmount
    );
    
    @Modifying
    @Transactional
    @Query("UPDATE Order o SET o.status = :newStatus WHERE o.id = :orderId")
    void updateOrderStatus(
        @Param("orderId") Long orderId,
        @Param("newStatus") String newStatus
    );
    
    @Modifying
    @Transactional
    @Query("""
        DELETE FROM Order o
        WHERE o.status = :status
        AND o.createdAt < :cutoffDate
        """)
    int deleteOldOrders(
        @Param("status") String status,
        @Param("cutoffDate") LocalDateTime cutoffDate
    );
}

@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepository;
    
    @Transactional(readOnly = true)
    public List<Order> getPendingOrders() {
        return orderRepository.findOrdersWithItems("PENDING");
    }
    
    @Transactional(readOnly = true)
    public List<Order> getCustomerOrders(Long customerId, LocalDateTime from, LocalDateTime to) {
        return orderRepository.findCustomerOrdersByDateRange(customerId, from, to);
    }
    
    @Transactional(readOnly = true)
    public List<Map<String, Object>> getHighValueOrders(BigDecimal minAmount) {
        return orderRepository.findHighValueOrdersByStatus("COMPLETED", minAmount);
    }
    
    public void processOrder(Long orderId) {
        orderRepository.updateOrderStatus(orderId, "PROCESSING");
    }
    
    public int cleanupCancelledOrders(LocalDateTime before) {
        return orderRepository.deleteOldOrders("CANCELLED", before);
    }
}
```

## Example 3: Many-to-Many Relationship

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String username;
    private String email;
    
    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();
    
    public void addRole(Role role) {
        this.roles.add(role);
        role.getUsers().add(this);
    }
    
    public void removeRole(Role role) {
        this.roles.remove(role);
        role.getUsers().remove(this);
    }
}

@Entity
@Table(name = "roles")
public class Role {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private String description;
    
    @ManyToMany(mappedBy = "roles")
    private Set<User> users = new HashSet<>();
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    @Query("""
        SELECT DISTINCT u FROM User u
        LEFT JOIN FETCH u.roles
        WHERE u.id = :id
        """)
    Optional<User> findByIdWithRoles(@Param("id") Long id);
    
    @Query("""
        SELECT u FROM User u
        JOIN u.roles r
        WHERE r.name = :roleName
        """)
    List<User> findUsersByRole(@Param("roleName") String roleName);
}

@Service
public class UserManagementService {
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    
    @Transactional
    public void assignRoleToUser(Long userId, Long roleId) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));
        Role role = roleRepository.findById(roleId)
            .orElseThrow(() -> new RoleNotFoundException(roleId));
        
        user.addRole(role);
        userRepository.save(user);
    }
    
    @Transactional
    public void removeRoleFromUser(Long userId, Long roleId) {
        User user = userRepository.findByIdWithRoles(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));
        Role role = user.getRoles().stream()
            .filter(r -> r.getId().equals(roleId))
            .findFirst()
            .orElseThrow(() -> new RoleNotFoundException(roleId));
        
        user.removeRole(role);
        userRepository.save(user);
    }
}
```

## Example 4: Pagination with Dynamic Filtering

```java
public record ProductFilter(
    String name,
    Long categoryId,
    BigDecimal minPrice,
    BigDecimal maxPrice,
    Boolean inStock
) {}

@Repository
public interface ProductRepository extends JpaRepository<Product, Long>, ProductCustomRepository {
}

public interface ProductCustomRepository {
    Page<Product> findByFilter(ProductFilter filter, Pageable pageable);
}

@Repository
public class ProductCustomRepositoryImpl implements ProductCustomRepository {
    @PersistenceContext
    private EntityManager entityManager;
    
    @Override
    public Page<Product> findByFilter(ProductFilter filter, Pageable pageable) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Product> cq = cb.createQuery(Product.class);
        Root<Product> root = cq.from(Product.class);
        
        List<Predicate> predicates = new ArrayList<>();
        
        if (filter.name() != null) {
            predicates.add(cb.like(
                cb.lower(root.get("name")),
                "%" + filter.name().toLowerCase() + "%"
            ));
        }
        
        if (filter.categoryId() != null) {
            predicates.add(cb.equal(root.get("category").get("id"), filter.categoryId()));
        }
        
        if (filter.minPrice() != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("price"), filter.minPrice()));
        }
        
        if (filter.maxPrice() != null) {
            predicates.add(cb.lessThanOrEqualTo(root.get("price"), filter.maxPrice()));
        }
        
        if (filter.inStock() != null && filter.inStock()) {
            predicates.add(cb.greaterThan(root.get("stock"), 0));
        }
        
        cq.where(cb.and(predicates.toArray(new Predicate[0])));
        cq.orderBy(cb.desc(root.get("createdAt")));
        
        TypedQuery<Product> query = entityManager.createQuery(cq);
        query.setFirstResult((int) pageable.getOffset());
        query.setMaxResults(pageable.getPageSize());
        
        List<Product> results = query.getResultList();
        long total = getTotal(filter);
        
        return new PageImpl<>(results, pageable, total);
    }
    
    private long getTotal(ProductFilter filter) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Long> cq = cb.createQuery(Long.class);
        Root<Product> root = cq.from(Product.class);
        
        List<Predicate> predicates = new ArrayList<>();
        // Add same predicates as above
        
        cq.select(cb.count(root));
        cq.where(cb.and(predicates.toArray(new Predicate[0])));
        
        return entityManager.createQuery(cq).getSingleResult();
    }
}

@Service
public class ProductSearchService {
    private final ProductRepository productRepository;
    
    @Transactional(readOnly = true)
    public Page<Product> search(ProductFilter filter, int page, int size) {
        Sort sort = Sort.by("createdAt").descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return productRepository.findByFilter(filter, pageable);
    }
}
```

## Example 5: Batch Operations

```java
@Service
@Transactional
public class BatchOperationService {
    private final ProductRepository productRepository;
    private static final int BATCH_SIZE = 50;
    
    public void importProducts(List<ProductDTO> products) {
        for (int i = 0; i < products.size(); i++) {
            Product product = mapToEntity(products.get(i));
            productRepository.save(product);
            
            if ((i + 1) % BATCH_SIZE == 0) {
                productRepository.flush();
            }
        }
    }
    
    public void importProductsBatch(List<ProductDTO> products) {
        List<Product> entities = products.stream()
            .map(this::mapToEntity)
            .collect(Collectors.toList());
        
        productRepository.saveAll(entities);
        productRepository.flush();
    }
    
    public long deleteOldProducts(LocalDateTime cutoffDate) {
        return productRepository.deleteByCreatedAtBefore(cutoffDate);
    }
    
    public int bulkUpdatePrices(List<Long> productIds, BigDecimal newPrice) {
        return productRepository.updatePriceForIds(productIds, newPrice);
    }
    
    private Product mapToEntity(ProductDTO dto) {
        Product product = new Product();
        product.setName(dto.name());
        product.setPrice(dto.price());
        return product;
    }
}

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    long deleteByCreatedAtBefore(LocalDateTime date);
    
    @Modifying
    @Transactional
    @Query("""
        UPDATE Product p
        SET p.price = :newPrice
        WHERE p.id IN :ids
        """)
    int updatePriceForIds(
        @Param("ids") List<Long> ids,
        @Param("newPrice") BigDecimal newPrice
    );
}
```

## Example 6: Entity Graph for Eager Loading

```java
@Entity
public class Post {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String title;
    private String content;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private User author;
    
    @OneToMany(mappedBy = "post", fetch = FetchType.LAZY)
    private List<Comment> comments = new ArrayList<>();
}

@Entity
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String text;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private Post post;
    
    @ManyToOne(fetch = FetchType.LAZY)
    private User author;
}

@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    // Using EntityGraph annotation
    @EntityGraph(attributePaths = {"author", "comments"})
    Optional<Post> findById(Long id);
    
    @EntityGraph(attributePaths = {"author", "comments", "comments.author"})
    List<Post> findAll();
    
    // Using @Query with JOIN FETCH
    @Query("""
        SELECT DISTINCT p FROM Post p
        JOIN FETCH p.author
        JOIN FETCH p.comments c
        JOIN FETCH c.author
        WHERE p.id = :id
        """)
    Optional<Post> findByIdWithDetails(@Param("id") Long id);
}

@Service
@Transactional(readOnly = true)
public class PostService {
    private final PostRepository postRepository;
    
    public Post getPostWithComments(Long id) {
        return postRepository.findById(id)
            .orElseThrow(() -> new PostNotFoundException(id));
    }
}
```

## Example 7: Transaction Propagation

```java
@Service
public class OrderProcessingService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
    private final InventoryService inventoryService;
    
    @Transactional
    public void processOrder(Long orderId) throws PaymentException {
        Order order = orderRepository.findById(orderId)
            .orElseThrow();
        
        try {
            processPayment(order);
            updateInventory(order);
            order.setStatus("COMPLETED");
            orderRepository.save(order);
        } catch (PaymentException e) {
            order.setStatus("PAYMENT_FAILED");
            orderRepository.save(order);
            throw e;
        }
    }
    
    @Transactional(propagation = Propagation.REQUIRED)
    private void processPayment(Order order) throws PaymentException {
        paymentService.charge(order.getCustomer(), order.getTotalAmount());
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    private void updateInventory(Order order) {
        order.getItems().forEach(item -> {
            inventoryService.decreaseStock(item.getProduct().getId(), item.getQuantity());
        });
    }
}
```

## Example 8: UUID Primary Keys

```java
@Entity
@Table(name = "articles", indexes = {
    @Index(name = "idx_author_created", columnList = "author_id, created_date DESC"),
    @Index(name = "idx_status", columnList = "status")
})
public class Article {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    private String title;
    private String content;
    private String status;  // DRAFT, PUBLISHED
    
    private LocalDateTime createdDate;
    private LocalDateTime publishedDate;
    
    @ManyToOne
    private User author;
}

@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_email", columnList = "email", unique = true),
    @Index(name = "idx_username", columnList = "username", unique = true)
})
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    @Column(unique = true, length = 100)
    private String email;
    
    @Column(unique = true, length = 100)
    private String username;
    
    private String firstName;
    private String lastName;
}

@Repository
public interface ArticleRepository extends JpaRepository<Article, UUID> {
    // Indexes support these queries efficiently
    List<Article> findByStatusOrderByPublishedDateDesc(String status);
    List<Article> findByAuthorOrderByCreatedDateDesc(User author);
    Page<Article> findByStatusAndPublishedDateAfter(
        String status,
        LocalDateTime date,
        Pageable pageable
    );
}

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByEmail(String email);
    Optional<User> findByUsername(String username);
}

@Service
@Transactional
public class ArticleService {
    private final ArticleRepository articleRepository;
    private final UserRepository userRepository;
    
    public Article createArticle(CreateArticleRequest request, UUID authorId) {
        User author = userRepository.findById(authorId)
            .orElseThrow(() -> new UserNotFoundException(authorId));
        
        Article article = new Article();
        article.setTitle(request.title());
        article.setContent(request.content());
        article.setStatus("DRAFT");
        article.setCreatedDate(LocalDateTime.now());
        article.setAuthor(author);
        
        return articleRepository.save(article);  // UUID generated automatically
    }
    
    @Transactional(readOnly = true)
    public Page<Article> getPublishedArticles(int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("publishedDate").descending());
        return articleRepository.findByStatusAndPublishedDateAfter(
            "PUBLISHED",
            LocalDateTime.now().minusDays(30),
            pageable
        );
    }
    
    @Transactional(readOnly = true)
    public Article getArticle(UUID id) {
        return articleRepository.findById(id)
            .orElseThrow(() -> new ArticleNotFoundException(id));
    }
}

record CreateArticleRequest(String title, String content) {}
```

## Example 9: Index Optimization

```java
@Entity
@Table(name = "orders", indexes = {
    // Single column index
    @Index(name = "idx_status", columnList = "status"),
    
    // Composite index for common query pattern
    @Index(name = "idx_customer_date", columnList = "customer_id, created_date DESC"),
    
    // For date range queries
    @Index(name = "idx_created_date", columnList = "created_date DESC"),
    
    // Unique index
    @Index(name = "idx_order_number", columnList = "order_number", unique = true),
    
    // Multi-column ordering
    @Index(name = "idx_status_amount", columnList = "status ASC, total_amount DESC")
})
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, length = 50)
    private String orderNumber;
    
    @Column(length = 20)
    private String status;  // PENDING, PROCESSING, SHIPPED, DELIVERED
    
    private LocalDateTime createdDate;
    
    @Column(precision = 12, scale = 2)
    private BigDecimal totalAmount;
    
    @ManyToOne
    @JoinColumn(name = "customer_id")
    private Customer customer;
}

@Entity
@Table(name = "order_items", indexes = {
    // Index on foreign key for JOIN performance
    @Index(name = "idx_order_id", columnList = "order_id"),
    
    // Composite index for finding items by order and status
    @Index(name = "idx_order_status", columnList = "order_id, status"),
    
    // Index on product foreign key
    @Index(name = "idx_product_id", columnList = "product_id")
})
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "order_id")
    private Order order;
    
    @ManyToOne
    @JoinColumn(name = "product_id")
    private Product product;
    
    private Integer quantity;
    private String status;
}

@Entity
@Table(name = "customers", indexes = {
    @Index(name = "idx_email", columnList = "email", unique = true),
    @Index(name = "idx_country_city", columnList = "country, city")
})
public class Customer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String firstName;
    private String lastName;
    
    @Column(unique = true)
    private String email;
    
    private String country;
    private String city;
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    // Uses idx_status
    List<Order> findByStatus(String status);
    
    // Uses idx_customer_date
    List<Order> findByCustomerOrderByCreatedDateDesc(
        Customer customer,
        Pageable pageable
    );
    
    // Uses idx_created_date
    Page<Order> findByCreatedDateAfterOrderByCreatedDateDesc(
        LocalDateTime date,
        Pageable pageable
    );
    
    // Uses idx_status_amount
    List<Order> findByStatusOrderByTotalAmountDesc(String status);
    
    // Custom query using indexes
    @Query("""
        SELECT o FROM Order o
        WHERE o.status = :status
        AND o.createdDate BETWEEN :start AND :end
        ORDER BY o.totalAmount DESC
        """)
    List<Order> findHighValueOrdersInPeriod(
        @Param("status") String status,
        @Param("start") LocalDateTime start,
        @Param("end") LocalDateTime end
    );
}

@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {
    // Uses idx_email
    Optional<Customer> findByEmail(String email);
    
    // Uses idx_country_city
    List<Customer> findByCountryAndCity(String country, String city);
}

@Service
@Transactional(readOnly = true)
public class OrderAnalyticsService {
    private final OrderRepository orderRepository;
    
    public Page<Order> getRecentOrders(int page, int size) {
        LocalDateTime weekAgo = LocalDateTime.now().minusDays(7);
        Pageable pageable = PageRequest.of(page, size);
        return orderRepository.findByCreatedDateAfterOrderByCreatedDateDesc(
            weekAgo,
            pageable
        );  // Uses idx_created_date
    }
    
    public List<Order> getPendingOrders() {
        return orderRepository.findByStatus("PENDING");  // Uses idx_status
    }
    
    public List<Order> getHighValueOrders(LocalDateTime from, LocalDateTime to) {
        return orderRepository.findHighValueOrdersInPeriod(
            "COMPLETED",
            from,
            to
        );  // Uses idx_status_amount
    }
    
    @Transactional
    public void optimizeIndexUsage() {
        // These queries benefit from composite indexes
        List<Order> customerOrders = orderRepository.findByCustomerOrderByCreatedDateDesc(
            new Customer(),
            PageRequest.of(0, 50)
        );  // Uses idx_customer_date
    }
}
```

These examples demonstrate real-world usage patterns for Spring Data JPA, from simple CRUD operations to complex scenarios involving relationships, auditing, pagination, batch processing, UUID keys, and index optimization.
