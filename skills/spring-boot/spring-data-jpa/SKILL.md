---
name: spring-data-jpa
description: Spring Data JPA expertise for building persistence layers. Use when implementing repositories, query methods, entity relationships, auditing, transactions, pagination, multiple databases, deletion operations, UUID primary keys, and database indexing. Covers repository interfaces, derived queries, custom queries with @Query, one-to-one/many-to-many relationships, pagination and sorting, database auditing, cascade operations, UUID strategies, composite indexes, and Spring Data best practices.
allowed-tools: Read, Write, Bash, Grep
---

# Spring Data JPA

## When to Use

Use this Skill when:
- Designing repository interfaces and data access patterns
- Implementing query methods using derived queries or `@Query`
- Configuring relationships between entities (one-to-one, one-to-many, many-to-many)
- Setting up pagination, sorting, and custom filtering
- Implementing database auditing with timestamps and user tracking
- Handling delete operations, cascading, and orphan removal
- Configuring multiple databases with separate transaction managers
- Building transactional operations with proper exception handling
- Optimizing persistence layer performance with indexes
- Using UUID as primary key for distributed systems
- Defining database indexes for query performance
- Following Spring Data JPA best practices and patterns

## Repository Interfaces

Spring Data JPA provides three main repository interfaces with increasing functionality:

### CrudRepository
Basic CRUD operations for all entities.

```java
@Repository
public interface ProductRepository extends CrudRepository<Product, Long> {
    // save(entity), findById(id), findAll(), count(), delete(entity), exists(id)
}
```

### PagingAndSortingRepository
Extends CrudRepository with pagination and sorting.

```java
@Repository
public interface ProductRepository extends PagingAndSortingRepository<Product, Long> {
    // All CRUD methods plus:
    Page<Product> findAll(Pageable pageable);
    Iterable<Product> findAll(Sort sort);
}

// Usage
Pageable pageable = PageRequest.of(0, 10, Sort.by("name").ascending());
Page<Product> page = repository.findAll(pageable);
```

### JpaRepository
Extends PagingAndSortingRepository with batch operations and flushing.

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    // All methods from CrudRepository and PagingAndSortingRepository plus:
    List<Product> findAll();
    List<Product> saveAll(Iterable<Product> entities);
    void flush();
    void deleteInBatch(Iterable<Product> entities);
}
```

## Query Methods

### Derived Query Methods
Spring Data automatically generates queries from method names following naming conventions.

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Simple lookup
    User findByEmail(String email);
    Optional<User> findByUsername(String username);
    
    // Multiple conditions
    List<User> findByFirstNameAndLastName(String firstName, String lastName);
    
    // Negation
    List<User> findByAgeNot(Integer age);
    List<User> findByEmailIsNull();
    
    // Comparison operators
    List<User> findByAgeGreaterThan(Integer age);
    List<User> findByAgeLessThanEqual(Integer age);
    List<User> findByCreatedDateBetween(LocalDateTime start, LocalDateTime end);
    
    // String operations
    List<User> findByEmailContains(String pattern);
    List<User> findByFirstNameStartingWith(String prefix);
    List<User> findByLastNameEndingWith(String suffix);
    List<User> findByFirstNameIgnoreCase(String firstName);
    
    // Ordering
    List<User> findByStatusOrderByCreatedDateDesc(String status);
    List<User> findByAgeGreaterThanOrderByLastNameAsc(Integer age);
    
    // Delete methods
    long deleteByEmail(String email);
    long deleteByStatusAndAge(String status, Integer age);
}
```

## Custom Queries with @Query

### JPQL Queries
Use Java Persistence Query Language for complex queries.

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("SELECT o FROM Order o WHERE o.status = :status AND o.totalPrice > :minPrice")
    List<Order> findActiveOrdersAbovePrice(
        @Param("status") String status,
        @Param("minPrice") BigDecimal minPrice
    );
    
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.customerId = :customerId")
    List<Order> findOrdersWithItems(@Param("customerId") Long customerId);
    
    @Query("SELECT COUNT(o) FROM Order o WHERE o.status = 'COMPLETED'")
    long countCompletedOrders();
}
```

### Native SQL Queries
Use native SQL for database-specific queries.

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    @Query(value = "SELECT * FROM products WHERE category = :category AND price < :maxPrice", 
           nativeQuery = true)
    List<Product> findProductsByCategory(
        @Param("category") String category,
        @Param("maxPrice") BigDecimal maxPrice
    );
}
```

### Modifying Queries
Use `@Modifying` for INSERT, UPDATE, DELETE operations.

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    @Modifying
    @Transactional
    @Query("UPDATE User u SET u.lastLoginDate = :now WHERE u.id = :userId")
    void updateLastLoginDate(
        @Param("userId") Long userId,
        @Param("now") LocalDateTime now
    );
    
    @Modifying
    @Transactional
    @Query("DELETE FROM User u WHERE u.createdDate < :cutoffDate")
    int deleteInactiveUsers(@Param("cutoffDate") LocalDateTime cutoffDate);
}
```

## Entity Relationships

### One-to-One with Foreign Key

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String email;
    
    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "address_id", referencedColumnName = "id")
    private Address address;
}

@Entity
@Table(name = "addresses")
public class Address {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String street;
    private String city;
    
    @OneToOne(mappedBy = "address")
    private User user;
}
```

### One-to-Many Relationship

```java
@Entity
@Table(name = "categories")
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    
    @OneToMany(mappedBy = "category", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Product> products = new ArrayList<>();
}

@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private BigDecimal price;
    
    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;
}
```

### Many-to-Many with Join Table

```java
@Entity
@Table(name = "students")
public class Student {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    
    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
        name = "student_course",
        joinColumns = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id")
    )
    private Set<Course> courses = new HashSet<>();
}

@Entity
@Table(name = "courses")
public class Course {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String title;
    
    @ManyToMany(mappedBy = "courses")
    private Set<Student> students = new HashSet<>();
}
```

### Many-to-Many with Extra Attributes (Join Entity)

```java
@Entity
@Table(name = "student_courses")
public class StudentCourse {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "student_id")
    private Student student;
    
    @ManyToOne
    @JoinColumn(name = "course_id")
    private Course course;
    
    private LocalDateTime enrolledAt;
    private Integer grade;
}

@Entity
public class Student {
    // ...
    @OneToMany(mappedBy = "student", cascade = CascadeType.ALL)
    private List<StudentCourse> enrollments = new ArrayList<>();
}

@Entity
public class Course {
    // ...
    @OneToMany(mappedBy = "course")
    private List<StudentCourse> enrollments = new ArrayList<>();
}
```

## Pagination and Sorting

```java
@Service
public class ProductService {
    private final ProductRepository repository;
    
    public Page<Product> getProductsPage(int page, int size, String sortBy) {
        Sort sort = Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        return repository.findAll(pageable);
    }
    
    public Page<Product> getActiveProductsPaginated(
        String status,
        int page,
        int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("createdDate").descending()
                .and(Sort.by("name").ascending())
        );
        return repository.findByStatus(status, pageable);
    }
    
    public void processPaginatedResults() {
        Pageable pageable = PageRequest.of(0, 100);
        Page<Product> page = repository.findAll(pageable);
        
        while (page.hasContent()) {
            page.getContent().forEach(product -> {
                // Process each product
            });
            
            if (page.hasNext()) {
                page = repository.findAll(page.nextPageable());
            } else {
                break;
            }
        }
    }
}

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    Page<Product> findByStatus(String status, Pageable pageable);
    List<Product> findByCategory(String category, Sort sort);
}
```

## Database Auditing

### Using Spring Data JPA Annotations

```java
@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
public class AuditingConfig {
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
            .map(SecurityContext::getAuthentication)
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName)
            .or(() -> Optional.of("system"));
    }
}

@Entity
@EntityListeners(AuditingEntityListener.class)
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    
    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdDate;
    
    @LastModifiedDate
    private LocalDateTime lastModifiedDate;
    
    @CreatedBy
    @Column(nullable = false, updatable = false)
    private String createdBy;
    
    @LastModifiedBy
    private String lastModifiedBy;
}
```

### Using JPA Lifecycle Callbacks

```java
@Entity
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

### Using Hibernate Envers for Entity Versioning

```java
@Entity
@Audited
public class Document {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String title;
    private String content;
    private String author;
}

@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {
    // Query audit history
    AuditReader getAuditReader();
}

// Usage
AuditReader auditReader = ((AuditQueryCreator) documentRepository).getAuditReader();
List<Number> revisions = auditReader.getRevisions(Document.class, documentId);
Document historicalVersion = auditReader.find(Document.class, documentId, revision);
```

## Transactions and Deletion

### Transaction Management

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentRepository paymentRepository;
    
    @Transactional
    public Order createOrder(Order order, Payment payment) {
        Order savedOrder = orderRepository.save(order);
        payment.setOrderId(savedOrder.getId());
        paymentRepository.save(payment);
        return savedOrder;
    }
    
    @Transactional(readOnly = true)
    public Order getOrderWithDetails(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new EntityNotFoundException("Order not found"));
    }
    
    @Transactional(rollbackFor = PaymentException.class)
    public void processPayment(Long orderId) throws PaymentException {
        Order order = orderRepository.findById(orderId)
            .orElseThrow();
        order.setStatus("PROCESSING");
        orderRepository.save(order);
        // Payment processing that may throw PaymentException
    }
}
```

### Delete Operations

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    // Delete by ID
    void deleteById(Long id);
    
    // Delete all
    void deleteAll();
    
    // Derived delete method
    long deleteByStatus(String status);
    long deleteByCreatedDateBefore(LocalDateTime date);
    
    // Custom delete query
    @Modifying
    @Transactional
    @Query("DELETE FROM Order o WHERE o.status = :status AND o.totalPrice < :minPrice")
    int deleteOldPendingOrders(
        @Param("status") String status,
        @Param("minPrice") BigDecimal minPrice
    );
}

@Service
public class OrderService {
    private final OrderRepository orderRepository;
    
    @Transactional
    public void deleteOrder(Long orderId) {
        orderRepository.deleteById(orderId);
    }
    
    @Transactional
    public long cleanupExpiredOrders() {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(30);
        return orderRepository.deleteByCreatedDateBefore(cutoffDate);
    }
    
    @Transactional
    public int deleteInactiveOrders() {
        return orderRepository.deleteOldPendingOrders("PENDING", BigDecimal.valueOf(10));
    }
}
```

### Cascade and Orphan Removal

```java
@Entity
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @OneToMany(mappedBy = "category", 
               cascade = CascadeType.ALL,     // Delete children when parent deleted
               orphanRemoval = true)           // Delete children when removed from collection
    private List<Product> products = new ArrayList<>();
}

@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;
}

// Usage
Category category = categoryRepository.findById(1L).orElseThrow();
categoryRepository.delete(category);  // Products automatically deleted
```

## UUID as Primary Key

UUID (Universally Unique Identifier) is an excellent choice for distributed systems where entities are created across multiple services.

### Modern Approach (Hibernate 6.2+ with JPA 3.1)

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    private String email;
    private String username;
}

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByEmail(String email);
}

@Service
public class UserService {
    private final UserRepository repository;
    
    public User createUser(CreateUserRequest request) {
        User user = new User();
        user.setEmail(request.email());
        user.setUsername(request.username());
        // UUID generated automatically
        return repository.save(user);
    }
    
    public User getUser(UUID id) {
        return repository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }
}
```

### Hibernate-Specific Approach (Earlier Versions)

With `@UuidGenerator`, you can control UUID version:

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @UuidGenerator(style = UuidGenerator.Style.TIME)  // Version 1: Time-based
    private UUID id;
    
    private String orderNumber;
    private LocalDateTime createdAt;
}

@Entity
@Table(name = "products")
public class Product {
    @Id
    @UuidGenerator(style = UuidGenerator.Style.RANDOM)  // Version 4: Random
    private UUID id;
    
    private String name;
    private BigDecimal price;
}

@Entity
@Table(name = "events")
public class Event {
    @Id
    @UuidGenerator  // Default: RANDOM (Version 4)
    private UUID id;
    
    private String eventType;
}
```

### Using String for UUID Storage

```java
@Entity
@Table(name = "transactions")
public class Transaction {
    @Id
    @UuidGenerator
    @Column(columnDefinition = "VARCHAR(36)")
    private String id;
    
    private BigDecimal amount;
    private String status;
}

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, String> {
    List<Transaction> findByStatus(String status);
}
```

### UUID vs Sequential ID Comparison

```java
// UUID: Better for distributed systems
@Entity
public class Article {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;  // Good for: microservices, distributed DBs, offline-first
}

// Sequential: Better for single database
@Entity
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;  // Good for: single database, better index performance
}

// Hybrid approach
@Entity
public class Blog {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;  // Unique identifier
    
    @Column(unique = true)
    private Long sequentialId;  // For URL-friendly slugs
}
```

## Database Indexing

Indexes significantly improve query performance by enabling faster data retrieval.

### Basic Index Definition

```java
@Entity
@Table(
    name = "products",
    indexes = {
        @Index(columnList = "name")
    }
)
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(length = 255)
    private String name;
    
    private BigDecimal price;
}
```

### Named Indexes

```java
@Entity
@Table(
    name = "users",
    indexes = {
        @Index(name = "idx_email", columnList = "email"),
        @Index(name = "idx_username", columnList = "username")
    }
)
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, length = 100)
    private String email;
    
    @Column(unique = true, length = 100)
    private String username;
}
```

### Multi-column Indexes

```java
@Entity
@Table(
    name = "orders",
    indexes = {
        // Index on single column
        @Index(name = "idx_status", columnList = "status"),
        
        // Composite index for common query: (status, created_date)
        @Index(name = "idx_status_created", columnList = "status, created_date DESC"),
        
        // Another composite index
        @Index(name = "idx_customer_date", columnList = "customer_id, created_date")
    }
)
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(length = 20)
    private String status;  // PENDING, PROCESSING, SHIPPED
    
    private LocalDateTime createdDate;
    
    @ManyToOne
    private Customer customer;
    
    private BigDecimal totalAmount;
}
```

### Index Sorting and Uniqueness

```java
@Entity
@Table(
    name = "products",
    indexes = {
        // Ascending index (default)
        @Index(name = "idx_price_asc", columnList = "price ASC"),
        
        // Descending index for recent items first
        @Index(name = "idx_created_desc", columnList = "created_date DESC"),
        
        // Unique index
        @Index(name = "idx_sku_unique", columnList = "sku", unique = true),
        
        // Multi-column unique index
        @Index(
            name = "idx_category_code_unique",
            columnList = "category_id, product_code",
            unique = true
        ),
        
        // Mixed sort order
        @Index(
            name = "idx_category_price",
            columnList = "category_id ASC, price DESC"
        )
    }
)
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, length = 50)
    private String sku;
    
    private String name;
    
    @Column(precision = 10, scale = 2)
    private BigDecimal price;
    
    private LocalDateTime createdDate;
    
    @ManyToOne
    private Category category;
}
```

### Indexes for Search and Filtering

```java
@Entity
@Table(
    name = "articles",
    indexes = {
        // For full-text search
        @Index(name = "idx_title", columnList = "title"),
        @Index(name = "idx_content", columnList = "content"),
        
        // For filtering and sorting
        @Index(name = "idx_status_published", columnList = "status, published_date DESC"),
        @Index(name = "idx_author_date", columnList = "author_id, published_date DESC"),
        
        // For range queries
        @Index(name = "idx_published_date", columnList = "published_date DESC"),
        
        // For pagination
        @Index(name = "idx_id_date", columnList = "id, published_date")
    }
)
public class Article {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String title;
    
    @Column(columnDefinition = "TEXT")
    private String content;
    
    private String status;  // DRAFT, PUBLISHED, ARCHIVED
    
    private LocalDateTime publishedDate;
    
    @ManyToOne
    private User author;
}

@Repository
public interface ArticleRepository extends JpaRepository<Article, Long> {
    // Will use idx_status_published
    Page<Article> findByStatusOrderByPublishedDateDesc(
        String status,
        Pageable pageable
    );
    
    // Will use idx_author_date
    List<Article> findByAuthorOrderByPublishedDateDesc(
        User author,
        Pageable pageable
    );
    
    // Will use idx_published_date
    List<Article> findByPublishedDateAfterOrderByPublishedDateDesc(
        LocalDateTime date
    );
    
    @Query("""
        SELECT a FROM Article a
        WHERE a.status = :status
        AND a.publishedDate BETWEEN :start AND :end
        ORDER BY a.publishedDate DESC
        """)
    Page<Article> findPublishedInDateRange(
        @Param("status") String status,
        @Param("start") LocalDateTime start,
        @Param("end") LocalDateTime end,
        Pageable pageable
    );
}

@Service
@Transactional(readOnly = true)
public class ArticleSearchService {
    private final ArticleRepository repository;
    
    public Page<Article> getPublishedArticles(int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("publishedDate").descending());
        return repository.findByStatusOrderByPublishedDateDesc("PUBLISHED", pageable);
    }
    
    public List<Article> getArticlesByAuthor(User author, int limit) {
        return repository.findByAuthorOrderByPublishedDateDesc(author)
            .stream()
            .limit(limit)
            .collect(Collectors.toList());
    }
}
```

### Indexes on Relationships

```java
@Entity
@Table(
    name = "comments",
    indexes = {
        // Index for finding comments by article
        @Index(name = "idx_article_id", columnList = "article_id"),
        
        // Index for finding recent comments
        @Index(name = "idx_article_created", columnList = "article_id, created_date DESC"),
        
        // Composite for common queries
        @Index(name = "idx_article_approved", columnList = "article_id, approved")
    }
)
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "article_id", nullable = false)
    private Article article;
    
    private String text;
    
    private boolean approved;
    
    private LocalDateTime createdDate;
}

@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {
    // Uses idx_article_id
    List<Comment> findByArticle(Article article);
    
    // Uses idx_article_created
    List<Comment> findByArticleOrderByCreatedDateDesc(Article article);
    
    // Uses idx_article_approved
    long countByArticleAndApproved(Article article, boolean approved);
}
```

## Multiple Databases

### Configuration for Multiple Databases

```java
@Configuration
@PropertySource("classpath:persistence-multiple-db.properties")
@EnableJpaRepositories(
    basePackages = "com.example.users.repository",
    entityManagerFactoryRef = "usersEntityManager",
    transactionManagerRef = "usersTransactionManager"
)
public class UsersDbConfig {
    
    @Bean
    @ConfigurationProperties(prefix = "users.datasource")
    public DataSource usersDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    public LocalContainerEntityManagerFactoryBean usersEntityManager(
            DataSource usersDataSource) {
        LocalContainerEntityManagerFactoryBean em = 
            new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(usersDataSource);
        em.setPackagesToScan("com.example.users.model");
        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        em.setJpaProperties(hibernateProperties());
        return em;
    }
    
    @Bean
    public PlatformTransactionManager usersTransactionManager(
            @Qualifier("usersEntityManager") 
            LocalContainerEntityManagerFactoryBean usersEntityManager) {
        return new JpaTransactionManager(usersEntityManager.getObject());
    }
    
    private Properties hibernateProperties() {
        Properties properties = new Properties();
        properties.setProperty("hibernate.dialect", 
            "org.hibernate.dialect.MySQL8Dialect");
        properties.setProperty("hibernate.hbm2ddl.auto", "validate");
        properties.setProperty("hibernate.show_sql", "false");
        return properties;
    }
}

@Configuration
@EnableJpaRepositories(
    basePackages = "com.example.products.repository",
    entityManagerFactoryRef = "productsEntityManager",
    transactionManagerRef = "productsTransactionManager"
)
public class ProductsDbConfig {
    // Similar configuration for products database
}

// properties file
users.datasource.url=jdbc:mysql://localhost:3306/users_db
users.datasource.username=root
users.datasource.password=password
users.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

products.datasource.url=jdbc:mysql://localhost:3306/products_db
products.datasource.username=root
products.datasource.password=password
products.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
```

## Best Practices

### Entity Design
- Use constructor injection exclusively, never field injection
- Prefer immutable fields with `final` modifiers
- Use Java records (16+) or `@Value` for DTOs
- Always provide `@Id` and `@GeneratedValue` for primary keys
- Use `@Table` and `@Column` annotations explicitly for clarity

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "name", nullable = false, length = 255)
    private String name;
    
    @Column(name = "price", precision = 10, scale = 2)
    private BigDecimal price;
    
    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "created_date", nullable = false, updatable = false)
    private LocalDateTime createdDate;
}
```

### Repository Queries
- Use derived queries for simple conditions
- Use `@Query` for complex queries to avoid long method names
- Always use `@Param` for query parameters
- Return `Optional<T>` for single results
- Use `@Transactional` on modifying operations
- Prefer `List<T>` over `Iterable<T>` for return types

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Good: Simple derived query
    Optional<User> findByEmail(String email);
    
    // Good: Complex query with @Query
    @Query("""
        SELECT u FROM User u 
        WHERE u.status = :status 
        AND u.createdDate >= :startDate
        ORDER BY u.createdDate DESC
        """)
    List<User> findActiveUsersSince(
        @Param("status") String status,
        @Param("startDate") LocalDateTime startDate
    );
    
    // Avoid: Long method name
    // List<User> findByStatusAndCreatedDateGreaterThanAndLastLoginDateLessThan(...)
}
```

### Pagination Best Practices
- Use `PageRequest` with `Sort` for controlled queries
- Set reasonable page sizes (10-100 items)
- Always check `hasContent()` and `hasNext()` when iterating
- Use `Slice<T>` when you only need next/previous, not total count

```java
Pageable pageable = PageRequest.of(
    pageNumber,           // zero-indexed
    pageSize,            // reasonable size
    Sort.by("id").descending()
);

Page<Product> page = repository.findAll(pageable);
List<Product> items = page.getContent();
long totalElements = page.getTotalElements();
int totalPages = page.getTotalPages();
```

### Transaction Management
- Mark read-only queries with `@Transactional(readOnly = true)`
- Use explicit transaction boundaries with `@Transactional`
- Avoid long-running transactions
- Specify rollback conditions when needed

```java
@Transactional(readOnly = true)
public Product getProduct(Long id) {
    return repository.findById(id).orElseThrow();
}

@Transactional
public Product updateProduct(Long id, ProductUpdate update) {
    Product product = repository.findById(id).orElseThrow();
    product.setName(update.name());
    product.setPrice(update.price());
    return repository.save(product);
}
```

### N+1 Query Problem
- Use `JOIN FETCH` or `@EntityGraph` to eagerly load relationships
- Avoid lazy loading in loops

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("""
        SELECT DISTINCT o FROM Order o 
        JOIN FETCH o.items 
        WHERE o.customerId = :customerId
        """)
    List<Order> findOrdersWithItems(@Param("customerId") Long customerId);
    
    @EntityGraph(attributePaths = {"items", "customer"})
    List<Order> findByStatus(String status);
}
```

### Exception Handling
- Spring Data throws `DataAccessException` hierarchy
- Use `EmptyResultDataAccessException` for missing entities
- Provide meaningful error messages

```java
@Service
public class ProductService {
    private final ProductRepository repository;
    
    public Product getProduct(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> 
                new ResourceNotFoundException("Product not found: " + id)
            );
    }
}
```

## Examples

### Complete CRUD Service

```java
@Service
@Transactional
public class ProductService {
    private final ProductRepository repository;
    private final CategoryRepository categoryRepository;
    
    public ProductService(ProductRepository repository, 
                         CategoryRepository categoryRepository) {
        this.repository = repository;
        this.categoryRepository = categoryRepository;
    }
    
    @Transactional(readOnly = true)
    public List<Product> getAllProducts() {
        return repository.findAll();
    }
    
    @Transactional(readOnly = true)
    public Page<Product> getProductsPage(int page, int size) {
        return repository.findAll(PageRequest.of(page, size,
            Sort.by("createdDate").descending()));
    }
    
    @Transactional(readOnly = true)
    public Product getProduct(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
    }
    
    public Product createProduct(CreateProductRequest request) {
        Category category = categoryRepository.findById(request.categoryId())
            .orElseThrow();
        
        Product product = new Product();
        product.setName(request.name());
        product.setPrice(request.price());
        product.setCategory(category);
        
        return repository.save(product);
    }
    
    public Product updateProduct(Long id, UpdateProductRequest request) {
        Product product = getProduct(id);
        product.setName(request.name());
        product.setPrice(request.price());
        return repository.save(product);
    }
    
    public void deleteProduct(Long id) {
        repository.deleteById(id);
    }
    
    public long deleteExpiredProducts(LocalDateTime before) {
        return repository.deleteByCreatedDateBefore(before);
    }
}
```

### Search with Multiple Criteria

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    @Query("""
        SELECT p FROM Product p 
        WHERE (:name IS NULL OR LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%')))
        AND (:category IS NULL OR p.category.id = :category)
        AND (:minPrice IS NULL OR p.price >= :minPrice)
        AND (:maxPrice IS NULL OR p.price <= :maxPrice)
        ORDER BY p.createdDate DESC
        """)
    Page<Product> searchProducts(
        @Param("name") String name,
        @Param("category") Long category,
        @Param("minPrice") BigDecimal minPrice,
        @Param("maxPrice") BigDecimal maxPrice,
        Pageable pageable
    );
}

@Service
public class ProductSearchService {
    private final ProductRepository repository;
    
    public Page<Product> search(ProductSearchCriteria criteria, int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("createdDate").descending());
        
        return repository.searchProducts(
            criteria.name(),
            criteria.categoryId(),
            criteria.minPrice(),
            criteria.maxPrice(),
            pageable
        );
    }
}
```

## References

- See [reference.md](reference.md) for detailed API documentation
- See [examples.md](examples.md) for additional code examples
- [Spring Data JPA Official Documentation](https://spring.io/projects/spring-data-jpa)
- [Hibernate Documentation](https://hibernate.org/)
