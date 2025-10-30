# Spring Data JPA - Reference Documentation

## Repository Interfaces

### Repository Hierarchy

Spring Data JPA provides a clear inheritance hierarchy for repositories:

```
Repository (marker interface)
├── CrudRepository (basic CRUD operations)
│   ├── PagingAndSortingRepository (add pagination/sorting)
│   │   └── JpaRepository (JPA-specific operations)
│   └── ListCrudRepository (Spring Data 3+)
└── Reactive variants (ReactiveCrudRepository, etc.)
```

### CrudRepository

Basic CRUD operations for all entities.

```java
public interface CrudRepository<T, ID extends Serializable> extends Repository<T, ID> {
    // CREATE/UPDATE
    <S extends T> S save(S entity);                    // Save or update entity
    <S extends T> Iterable<S> saveAll(Iterable<S> entities); // Save multiple entities

    // READ
    Optional<T> findById(ID id);                        // Find by primary key
    T getById(ID id);                                   // Returns proxy, never null
    T getReferenceById(ID id);                          // Like getById
    boolean existsById(ID id);                         // Check existence
    Iterable<T> findAll();                             // Find all entities
    Iterable<T> findAllById(Iterable<ID> ids);          // Find by multiple IDs

    // AGGREGATE
    long count();                                      // Count entities

    // DELETE
    void deleteById(ID id);                            // Delete by ID
    void delete(T entity);                             // Delete entity
    void deleteAllById(Iterable<? extends ID> ids);    // Delete by multiple IDs
    void deleteAll(Iterable<? extends T> entities);    // Delete multiple entities
    void deleteAll();                                  // Delete all entities
}
```

### PagingAndSortingRepository

Extends CrudRepository with pagination and sorting capabilities.

```java
public interface PagingAndSortingRepository<T, ID extends Serializable>
    extends CrudRepository<T, ID> {

    // Sorting
    Iterable<T> findAll(Sort sort);                   // Find all with sorting

    // Pagination
    Page<T> findAll(Pageable pageable);                // Find all with pagination
}
```

### JpaRepository

The most comprehensive interface extending PagingAndSortingRepository with JPA-specific operations.

```java
public interface JpaRepository<T, ID extends Serializable>
    extends PagingAndSortingRepository<T, ID> {

    // Enhanced read operations
    List<T> findAll();                                 // Returns List instead of Iterable
    List<T> findAllById(Iterable<ID> ids);            // Returns List instead of Iterable
    List<T> findAll(Sort sort);                       // Returns List instead of Iterable
    Page<T> findAll(Pageable pageable);               // Returns Page

    // Batch operations
    <S extends T> List<S> saveAll(Iterable<S> entities); // Save multiple with return

    // Batch delete operations
    void deleteInBatch(Iterable<T> entities);          // Delete without flushing
    void deleteAllInBatch(Iterable<ID> ids);          // Delete by IDs without flushing
    void deleteAllInBatch();                           // Delete all without flushing

    // Flush operations
    void flush();                                      // Flush to database
    <S extends T> S saveAndFlush(S entity);           // Save and immediately flush
    <S extends T> List<S> saveAllAndFlush(Iterable<S> entities); // Save all and flush
}
```

## Query Methods

### Derived Query Methods

Spring Data automatically generates queries from method names following naming conventions.

#### Simple Lookups
```java
Optional<User> findByEmail(String email);             // Single result
List<User> findByUsername(String username);           // Multiple results
User findFirstByEmail(String email);                // First result
User findTopByOrderByAgeDesc();                      // Top by age descending
```

#### Conditional Operators
```java
// Equality
List<User> findByStatus(String status);
List<User> findByStatusNot(String status);

// Comparison
List<User> findByAgeGreaterThan(Integer age);
List<User> findByAgeLessThanEqual(Integer age);
List<User> findByAgeBetween(Integer min, Integer max);
List<User> findByAgeGreaterThanEqual(25);           // Static comparison

// Null/Empty checks
List<User> findByEmailIsNull();
List<User> findByEmailIsNotNull();
List<User> findByEmailNotEmpty();

// Boolean properties
List<User> findByActiveTrue();
List<User>ByEmailActiveFalse();
```

#### String Operations
```java
// Pattern matching
List<User> findByEmailContaining(String pattern);    // LIKE '%pattern%'
List<User> findByEmailStartsWith(String prefix);     // LIKE 'prefix%'
List<User> findByEmailEndsWith(String suffix);       // LIKE '%suffix'
List<User> findByEmailLike(String pattern);          // Exact LIKE pattern

// Case sensitivity
List<User> findByEmailIgnoreCase(String email);
```

#### Date and Time Operations
```java
// After/Before
List<Order> findByOrderDateAfter(LocalDate date);
List<Order> findByCreatedDateBefore(LocalDateTime dateTime);

// Between
List<Order> findByOrderDateBetween(LocalDate start, LocalDate end);

// Range queries
List<Order> findByTotalPriceGreaterThan(BigDecimal min);
List<Order> findByTotalPriceBetween(BigDecimal min, BigDecimal max);

// Current date comparisons
List<Order> findByCreatedDateBefore(LocalDateTime.now().minusDays(7));
```

#### Ordering
```java
// Simple ordering
List<User> findByStatusOrderByCreatedDateDesc(String status);
List<User> findAllByOrderByLastNameAsc();

// Multiple sort criteria
List<Product> findByCategoryOrderByPriceAscNameDesc(String category);

// Dynamic sorting
List<User> findAll(Sort.by("lastName").ascending());
List<User> findByActiveTrue(Sort.by("createdDate").descending());
```

#### Pagination Integration
```java
Page<User> findByStatus(String status, Pageable pageable);
Slice<User> findByActiveTrue(Pageable pageable);     // No total count
List<User> findTop10ByOrderByCreatedDateDesc();      // Fixed limit
```

#### Delete Operations
```java
// Delete with return count
long deleteByEmail(String email);
long deleteByStatusAndAge(String status, Integer age);

// Delete entities
void deleteByStatus(String status);                  // Bulk delete
```

### Custom Queries with @Query

#### JPQL Queries
Use Java Persistence Query Language for complex queries.

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    // Basic query with named parameters
    @Query("SELECT o FROM Order o WHERE o.status = :status AND o.totalPrice > :minPrice")
    List<Order> findActiveOrdersAbovePrice(
        @Param("status") String status,
        @Param("minPrice") BigDecimal minPrice
    );

    // Query with JOIN FETCH to avoid N+1 problem
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.customerId = :customerId")
    List<Order> findOrdersWithItems(@Param("customerId") Long customerId);

    // Aggregate function
    @Query("SELECT COUNT(o) FROM Order o WHERE o.status = 'COMPLETED'")
    long countCompletedOrders();

    // IN clause
    @Query("SELECT o FROM Order o WHERE o.status IN :statuses")
    List<Order> findByStatuses(@Param("statuses") List<String> statuses);

    // EXISTS clause
    @Query("SELECT o FROM Order o WHERE EXISTS (SELECT 1 FROM o.items i WHERE i.quantity = 0)")
    List<Order> findOrdersWithZeroQuantityItems();
}
```

#### Native SQL Queries
Use native SQL for database-specific queries.

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    // Simple native query
    @Query(value = "SELECT * FROM products WHERE category = :category AND price < :maxPrice",
           nativeQuery = true)
    List<Product> findProductsByCategory(
        @Param("category") String category,
        @Param("maxPrice") BigDecimal maxPrice
    );

    // Native query with mapping
    @Query(value = """
        SELECT p.id, p.name, p.price, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.price > :minPrice
        ORDER BY p.price DESC
        """, nativeQuery = true)
    @QueryResults projection = ProductSummary.class;  // Custom projection
    List<ProductSummary> findExpensiveProductSummaries(@Param("minPrice") BigDecimal minPrice);
}
```

#### Modifying Queries
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

    @Modifying
    @Transactional
    @Query(value = "UPDATE users SET status = 'INACTIVE' WHERE last_login < :cutoff",
           nativeQuery = true)
    int deactivateInactiveUsersNative(@Param("cutoff") LocalDateTime cutoff);
}
```

## Entity Relationships

### One-to-One Relationship

#### Foreign Key Approach
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String email;

    @OneToOne(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "address_id", referencedColumnName = "id")
    private Address address;
}

@Entity
@Table(name = "addresses")
public class Address {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String street;
    private String city;
    private String postalCode;

    @OneToOne(mappedBy = "address")
    private User user;
}
```

#### Shared Primary Key Approach
```java
@Entity
@Table(name = "employees")
public class Employee {
    @Id
    private Long id;  // Shared with profile

    @Column(nullable = false)
    private String firstName;

    @OneToOne(mappedBy = "employee", fetch = FetchType.LAZY)
    private EmployeeProfile profile;
}

@Entity
@Table(name = "employee_profiles")
public class EmployeeProfile {
    @Id
    private Long id;  // Same as employee ID

    @Column(length = 500)
    private String bio;

    @OneToOne(fetch = FetchType.LAZY)
    @MapsId  // Maps to employee.id
    @JoinColumn(name = "id")
    private Employee employee;
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

    @Column(nullable = false, length = 100)
    private String name;

    @OneToMany(mappedBy = "category",
               cascade = CascadeType.ALL,
               orphanRemoval = true,
               fetch = FetchType.LAZY)
    private List<Product> products = new ArrayList<>();

    // Helper methods
    public void addProduct(Product product) {
        products.add(product);
        product.setCategory(this);
    }

    public void removeProduct(Product product) {
        products.remove(product);
        product.setCategory(null);
    }
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

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;
}
```

### Many-to-Many Relationship

#### Simple Join Table
```java
@Entity
@Table(name = "students")
public class Student {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
        name = "student_course",
        joinColumns = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id")
    )
    private Set<Course> courses = new HashSet<>();

    public void addCourse(Course course) {
        courses.add(course);
        course.getStudents().add(this);
    }

    public void removeCourse(Course course) {
        courses.remove(course);
        course.getStudents().remove(this);
    }
}

@Entity
@Table(name = "courses")
public class Course {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String title;

    @ManyToMany(mappedBy = "courses")
    private Set<Student> students = new HashSet<>();
}
```

#### Join Table with Additional Attributes
```java
@Entity
@Table(name = "enrollments")
public class Enrollment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @ManyToOne
    @JoinColumn(name = "course_id", nullable = false)
    private Course course;

    @Column(nullable = false)
    private LocalDateTime enrolledAt;

    @Column(precision = 3, scale = 2)
    private Double grade;  // Can be null

    @Column(length = 20)
    private String status;  // ACTIVE, WITHDRAWN, COMPLETED

    // Composite primary key (alternative approach)
    @EmbeddedId
    private EnrollmentId enrollmentId;

    @ManyToOne
    @JoinColumn(name = "student_id", insertable = false, updatable = false)
    private Student student;

    @ManyToOne
    @JoinColumn(name = "course_id", insertable = false, updatable = false)
    private Course course;
}

@Embeddable
public class EnrollmentId implements Serializable {
    private Long studentId;
    private Long courseId;

    // equals(), hashCode() implementation
}
```

### Bidirectional Relationships

#### Best Practices
```java
@Entity
public class Department {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @OneToMany(mappedBy = "department", cascade = CascadeType.ALL)
    private List<Employee> employees = new ArrayList<>();

    // Helper method for consistency
    public void addEmployee(Employee employee) {
        employees.add(employee);
        employee.setDepartment(this);
    }
}

@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @ManyToOne
    @JoinColumn(name = "department_id", nullable = false)
    private Department department;
}
```

## Pagination and Sorting

### Pagination Basics

```java
@Service
public class ProductService {
    private final ProductRepository repository;

    public Page<Product> getProductsPage(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return repository.findAll(pageable);
    }

    public Page<Product> getProductsWithSorting(int page, int size, String sortField) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sortField));
        return repository.findAll(pageable);
    }

    public Page<Product> getProductsWithMultiSort(int page, int size) {
        Sort sort = Sort.by("price").ascending()
                      .and(Sort.by("name").ascending());
        Pageable pageable = PageRequest.of(page, size, sort);
        return repository.findAll(pageable);
    }
}
```

### Advanced Pagination

```java
@Service
public class OrderService {
    private final OrderRepository repository;

    public Page<Order> getOrdersByStatus(String status, int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("createdDate").descending());
        return repository.findByStatus(status, pageable);
    }

    public Slice<Order> getRecentOrders(int page, int size) {
        // Slice doesn't count total elements (more efficient for large datasets)
        Pageable pageable = PageRequest.of(page, size);
        return repository.findByStatus("NEW", pageable);
    }

    public Stream<Order> streamAllOrders() {
        // Stream for large datasets
        return repository.streamAllBy();
    }
}
```

### Custom Pagination Queries

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    @Query("SELECT u FROM User u WHERE u.active = true")
    Page<User> findActiveUsers(Pageable pageable);

    @Query(value = "SELECT * FROM users WHERE created_at > :date",
           nativeQuery = true)
    Page<User> findUsersCreatedAfter(@Param("date") LocalDateTime date, Pageable pageable);
}
```

## Database Auditing

### Spring Data JPA Auditing

#### Configuration
```java
@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
@EnableJpaRepositories(repositoryFactoryBeanClass = CustomRepositoryFactoryBean.class)
public class AuditingConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
            .map(SecurityContext::getAuthentication)
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName)
            .or(() -> Optional.of("system"));
    }

    @Bean
    public JpaTransactionManager transactionManager(EntityManagerFactory emf) {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(emf);
        return transactionManager;
    }
}
```

#### Auditing Entities
```java
@Entity
@EntityListeners(AuditingEntityListener.class)
public class BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdDate;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime lastModifiedDate;

    @CreatedBy
    @Column(nullable = false, updatable = false, length = 50)
    private String createdBy;

    @LastModifiedBy
    @Column(nullable = false, length = 50)
    private String lastModifiedBy;

    @Version
    private Long version;  // Optimistic locking
}

@Entity
public class Product extends BaseEntity {
    @Column(nullable = false, length = 255)
    private String name;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Enumerated(EnumType.STRING)
    private ProductStatus status;
}

public enum ProductStatus {
    ACTIVE, INACTIVE, DISCONTINUED
}
```

#### Custom Auditor Provider
```java
@Component
public class CustomAuditorProvider implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        // Try to get from security context first
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated()) {
            return Optional.of(authentication.getName());
        }

        // Fallback to system user or throw exception
        return Optional.of("system");
    }
}
```

### JPA Lifecycle Callbacks

```java
@Entity
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 20)
    private String status;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (status == null) {
            status = "PENDING";
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    @PreRemove
    protected void onRemove() {
        // Cleanup logic before deletion
    }

    @PostLoad
    protected void onLoad() {
        // Post-load processing
    }
}
```

### Hibernate Envers for Auditing

#### Configuration
```java
@Configuration
@EnableJpaRepositories(repositoryFactoryBeanClass = EnversRepositoryFactoryBean.class)
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
public class EnversConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
            .map(SecurityContext::getAuthentication)
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName);
    }
}
```

#### Audited Entities
```java
@Entity
@Audited
@RevisionEntity(EntityRevisionListener.class)
public class Document {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Enumerated(EnumType.STRING)
    private DocumentStatus status;

    @ManyToOne
    @JoinColumn(name = "author_id", nullable = false)
    private User author;
}

@RevisionEntity
public class EntityRevisionListener implements RevisionListener {
    @Override
    public void newRevision(Object revisionEntity) {
        EntityRevision revision = (EntityRevision) revisionEntity;
        revision.setRevisionDate(LocalDateTime.now());
        revision.setUsername(SecurityContextHolder.getContext()
            .getAuthentication().getName());
    }
}

@Entity
public class EntityRevision {
    @Id
    @GeneratedValue
    private Integer id;

    private LocalDateTime revisionDate;

    @Column(length = 50)
    private String username;
}
```

#### Repository Usage
```java
public interface DocumentRepository extends JpaRepository<Document, Long>,
                                            JpaEntityRepository<Document, Long, Integer> {

    @Query("SELECT d FROM Document d WHERE d.id = :id AND d.revisionNumber <= :revision")
    Document findHistoricalVersion(@Param("id") Long id, @Param("revision") Integer revision);

    List<Number> findRevisions(Long documentId);

    <T> T findRevision(Class<T> entityClass, Number revision);
}

@Service
public class DocumentAuditService {
    private final DocumentRepository documentRepository;
    private final AuditReader auditReader;

    public List<DocumentRevision> getDocumentHistory(Long documentId) {
        List<Number> revisions = auditReader.getRevisions(Document.class, documentId);
        return revisions.stream()
            .map(revision -> new DocumentRevision(
                revision,
                auditReader.find(Document.class, documentId, revision),
                auditReader.getRevisionDateForRevision(revision)
            ))
            .collect(Collectors.toList());
    }
}
```

## Transactions and Deletion

### Transaction Management

#### Transaction Configuration
```java
@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentRepository paymentRepository;
    private final InventoryService inventoryService;

    @Transactional
    public Order createOrder(Order order, List<Payment> payments) {
        // Start transaction
        Order savedOrder = orderRepository.save(order);

        // Process payments
        payments.forEach(payment -> {
            payment.setOrderId(savedOrder.getId());
            paymentRepository.save(payment);
        });

        // Update inventory
        inventoryService.reserveItems(savedOrder.getItems());

        return savedOrder;
    }

    @Transactional(readOnly = true)
    public Order getOrderWithDetails(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new EntityNotFoundException("Order not found: " + orderId));
    }

    @Transactional(rollbackFor = {PaymentException.class, InventoryException.class})
    public void processPayment(Long orderId) throws PaymentException {
        Order order = getOrderWithDetails(orderId);

        // Process payment logic
        paymentService.process(order.getPayments());

        // Update order status
        order.setStatus("PROCESSING");
        orderRepository.save(order);

        // This will trigger rollback if thrown
        if (paymentFailed) {
            throw new PaymentException("Payment processing failed");
        }
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOrderCreation(Order order) {
        // Always creates new transaction
        auditLogRepository.save(new AuditLog("ORDER_CREATED", order.getId()));
    }
}
```

#### Propagation Types
```java
@Service
public class TransactionalService {

    @Transactional
    public void methodA() {
        methodB();  // Runs in same transaction
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void methodB() {
        // Runs in new transaction
    }

    @Transactional(propagation = Propagation.NESTED)
    public void methodC() {
        // Runs in nested transaction (savepoint)
    }

    @Transactional(propagation = Propagation.SUPPORTS)
    public void methodD() {
        // Runs in existing transaction or none
    }
}
```

#### Isolation Levels
```java
@Service
public class OrderService {

    @Transactional(isolation = Isolation.READ_COMMITTED)
    public Order getOrderWithConsistentData(Long orderId) {
        // Read committed isolation - prevents dirty reads
        return orderRepository.findById(orderId).orElseThrow();
    }

    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void processInventoryUpdate(List<InventoryItem> items) {
        // Serializable isolation - prevents all concurrency issues
        items.forEach(inventoryService::updateStock);
    }

    @Transactional(timeout = 30)  // 30 seconds timeout
    public void processLongRunningTask() {
        // Long-running operation with timeout
        externalApiService.callExternalSystem();
    }
}
```

### Delete Operations

#### Repository Delete Methods
```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    // Basic delete operations
    void deleteById(Long id);
    void delete(Order entity);
    void deleteAllById(Iterable<Long> ids);
    void deleteAll(Iterable<Order> entities);
    void deleteAll();

    // Derived delete queries
    long deleteByStatus(String status);
    long deleteByCreatedDateBefore(LocalDateTime date);
    long deleteByTotalPriceLessThan(BigDecimal threshold);

    // Custom delete query
    @Modifying
    @Transactional
    @Query("DELETE FROM Order o WHERE o.status = :status AND o.totalPrice < :minPrice")
    int deleteOldPendingOrders(
        @Param("status") String status,
        @Param("minPrice") BigDecimal minPrice
    );
}
```

#### Service Layer Delete Operations
```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;

    @Transactional
    public void deleteOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));

        // Delete related items first (or use cascade)
        orderItemRepository.deleteByOrderId(orderId);

        // Delete order
        orderRepository.delete(order);
    }

    @Transactional
    public long cleanupExpiredOrders(LocalDateTime cutoffDate) {
        return orderRepository.deleteByCreatedDateBefore(cutoffDate);
    }

    @Transactional
    public int cleanupOldPendingOrders(BigDecimal minPrice) {
        return orderRepository.deleteOldPendingOrders("PENDING", minPrice);
    }

    @Transactional
    public void batchDeleteOrders(List<Long> orderIds) {
        // Batch delete for better performance
        orderRepository.deleteAllById(orderIds);
    }
}
```

#### Cascade and Orphan Removal
```java
@Entity
@Table(name = "categories")
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @OneToMany(mappedBy = "category",
               cascade = CascadeType.ALL,     // Cascade save/update/delete
               orphanRemoval = true)           // Remove children when removed from collection
    private List<Product> products = new ArrayList<>();

    @OneToMany(mappedBy = "category",
               cascade = CascadeType.PERSIST,  // Only cascade save operations
               orphanRemoval = false)
    private List<Product> inactiveProducts = new ArrayList<>();

    public void addProduct(Product product) {
        products.add(product);
        product.setCategory(this);
    }

    public void removeProduct(Product product) {
        products.remove(product);
        product.setCategory(null);  // Triggers orphan removal
    }
}

@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 255)
    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;

    // Bidirectional relationship management
    public void setCategory(Category category) {
        if (this.category != null) {
            this.category.removeProduct(this);
        }
        this.category = category;
        if (category != null) {
            category.addProduct(this);
        }
    }
}
```

### Batch Operations

```java
@Service
public class BatchOrderService {
    private final OrderRepository orderRepository;

    @Transactional
    public void batchUpdateOrders(List<OrderUpdate> updates) {
        // Use batch processing for large updates
        int batchSize = 50;
        for (int i = 0; i < updates.size(); i++) {
            OrderUpdate update = updates.get(i);

            Order order = orderRepository.findById(update.orderId())
                .orElseThrow();

            order.setStatus(update.status());
            order.setNotes(update.notes());

            if (i % batchSize == 0) {
                orderRepository.flush();  // Flush periodically
                orderRepository.clear();   // Clear persistence context
            }
        }
    }

    @Transactional
    public void batchDeleteOrdersByStatus(List<String> statuses) {
        // Batch delete by status
        statuses.forEach(status ->
            orderRepository.deleteByStatus(status));
    }
}
```

## UUID as Primary Key

### Modern Approach (Hibernate 6.2+ with JPA 3.1)

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, length = 100, unique = true)
    private String email;

    @Column(length = 50)
    private String username;

    @Enumerated(EnumType.STRING)
    private UserStatus status;

    @CreatedDate
    private LocalDateTime createdDate;
}

@Entity
@Table(name = "sessions")
public class UserSession {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(nullable = false, unique = true)
    private String token;

    @Column(name = "expires_at", nullable = false)
    private LocalDateTime expiresAt;
}

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByEmail(String email);
    Optional<User> findByUsername(String username);
    List<User> findByStatus(UserStatus status);
}

@Service
public class UserService {
    private final UserRepository repository;

    public User createUser(CreateUserRequest request) {
        if (repository.findByEmail(request.email()).isPresent()) {
            throw new EmailAlreadyExistsException(request.email());
        }

        User user = new User();
        user.setEmail(request.email());
        user.setUsername(request.username());
        user.setStatus(UserStatus.ACTIVE);

        return repository.save(user);
    }

    public User getUser(UUID id) {
        return repository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }
}
```

### Hibernate-Specific UUID Generation

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @UuidGenerator(style = UuidGenerator.Style.TIME)  // Version 1: Time-based
    private UUID id;

    @Column(nullable = false, length = 50, unique = true)
    private String orderNumber;

    @Column(precision = 12, scale = 2)
    private BigDecimal totalAmount;

    @CreatedDate
    private LocalDateTime createdAt;
}

@Entity
@Table(name = "products")
public class Product {
    @Id
    @UuidGenerator(style = UuidGenerator.Style.RANDOM)  // Version 4: Random
    private UUID id;

    @Column(nullable = false, length = 255)
    private String name;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "sku", length = 50, unique = true)
    private String sku;
}

@Entity
@Table(name = "events")
public class SystemEvent {
    @Id
    @UuidGenerator  // Default: RANDOM (Version 4)
    private UUID id;

    @Column(nullable = false, length = 50)
    private String eventType;

    @Column(columnDefinition = "TEXT")
    private String eventData;

    @CreatedDate
    private LocalDateTime timestamp;
}
```

### UUID Storage Options

```java
@Entity
@Table(name = "transactions")
public class Transaction {
    @Id
    @UuidGenerator
    @Column(columnDefinition = "VARCHAR(36)")  // Store as string for some databases
    private String id;

    @Column(precision = 19, scale = 4)  // High precision for financial data
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    private TransactionStatus status;

    @Column(name = "reference_id", length = 36)
    private String referenceId;  // Secondary UUID field
}

@Entity
@Table(name = "audit_logs")
public class AuditLog {
    @Id
    @UuidGenerator
    private UUID id;  // Native UUID type (PostgreSQL, etc.)

    @Column(name = "entity_id", length = 36)  // May need VARCHAR for MySQL
    private String entityId;  // Foreign key as string for compatibility

    @Column(nullable = false, length = 100)
    private String action;

    @Column(columnDefinition = "TEXT")
    private String changes;

    @CreatedDate
    private LocalDateTime timestamp;
}
```

### UUID vs Sequential ID Comparison

```java
// UUID Entity: Better for distributed systems
@Entity
@Table(name = "articles")
public class Article {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;  // Good for: microservices, distributed DBs, offline-first

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @ManyToOne
    private User author;
}

// Sequential Entity: Better for single database
@Entity
@Table(name = "comments")
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;  // Good for: single database, better index performance

    @Column(nullable = false, columnDefinition = "TEXT")
    private String text;

    @ManyToOne
    private Article article;
}

// Hybrid approach: Best of both worlds
@Entity
@Table(name = "blogs")
public class Blog {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;  // Unique identifier

    @Column(unique = true, name = "slug")
    private String slug;  // URL-friendly, sequential-like identifier

    @Column(nullable = false, length = 200)
    private String title;

    @ManyToOne
    private User owner;
}
```

### Performance Considerations

```java
@Service
public class UserService {
    private final UserRepository repository;

    // Batch operations with UUIDs
    @Transactional
    public List<User> batchCreateUsers(List<CreateUserRequest> requests) {
        List<User> users = requests.stream()
            .map(request -> {
                User user = new User();
                user.setEmail(request.email());
                user.setUsername(request.username());
                return user;
            })
            .collect(Collectors.toList());

        return repository.saveAll(users);
    }

    // Index optimization for UUID queries
    @Transactional(readOnly = true)
    public Page<User> findUsersByEmailPattern(String pattern, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return repository.findByEmailContaining(pattern, pageable);
    }

    // Cache UUID lookups
    @Cacheable(value = "users", key = "#id")
    public User getUser(UUID id) {
        return repository.findById(id).orElseThrow();
    }
}
```

## Database Indexing

### Basic Index Definitions

```java
@Entity
@Table(
    name = "products",
    indexes = {
        @Index(name = "idx_product_name", columnList = "name"),
        @Index(name = "idx_product_category", columnList = "category_id")
    }
)
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 255)
    private String name;

    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "created_date")
    private LocalDateTime createdDate;
}

@Entity
@Table(
    name = "users",
    indexes = {
        // Unique index for email
        @Index(name = "idx_user_email_unique", columnList = "email", unique = true),

        // Index for username (unique)
        @Index(name = "idx_user_username", columnList = "username", unique = true),

        // Index for status filtering
        @Index(name = "idx_user_status", columnList = "status")
    }
)
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100, unique = true)
    private String email;

    @Column(length = 50, unique = true)
    private String username;

    @Enumerated(EnumType.STRING)
    private UserStatus status;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
```

### Composite Indexes

```java
@Entity
@Table(
    name = "orders",
    indexes = {
        // Single column indexes
        @Index(name = "idx_order_status", columnList = "status"),
        @Index(name = "idx_order_customer", columnList = "customer_id"),

        // Composite index for common query pattern
        @Index(name = "idx_status_customer_created",
               columnList = "status, customer_id, created_at DESC"),

        // Another composite index
        @Index(name = "idx_order_created_status",
               columnList = "created_at DESC, status"),

        // Index for reporting queries
        @Index(name = "idx_order_report",
               columnList = "status, total_amount, created_at")
    }
)
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 20)
    private String status;  // PENDING, PROCESSING, COMPLETED, CANCELLED

    @ManyToOne
    @JoinColumn(name = "customer_id")
    private Customer customer;

    @Column(precision = 12, scale = 2)
    private BigDecimal totalAmount;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Enumerated(EnumType.STRING)
    private OrderType type;  // RETAIL, WHOLESALE, B2B
}

@Entity
@Table(
    name = "order_items",
    indexes = {
        // Index for finding items by order
        @Index(name = "idx_order_item_order", columnList = "order_id"),

        // Composite index for order and product queries
        @Index(name = "idx_order_item_order_product",
               columnList = "order_id, product_id"),

        // Index for price-based queries
        @Index(name = "idx_order_item_price",
               columnList = "unit_price DESC, quantity"),

        // Index for inventory sync
        @Index(name = "idx_order_item_product_created",
               columnList = "product_id, created_at DESC")
    }
)
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @ManyToOne
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @Column(nullable = false)
    private Integer quantity;

    @Column(precision = 10, scale = 2, name = "unit_price")
    private BigDecimal unitPrice;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
```

### Index Sorting and Uniqueness

```java
@Entity
@Table(
    name = "products",
    indexes = {
        // Ascending indexes (default)
        @Index(name = "idx_product_price_asc", columnList = "price ASC"),
        @Index(name = "idx_product_name_asc", columnList = "name ASC"),

        // Descending indexes for "newest first" queries
        @Index(name = "idx_product_created_desc",
               columnList = "created_at DESC"),

        // Unique indexes
        @Index(name = "idx_product_sku_unique",
               columnList = "sku", unique = true),
        @Index(name = "idx_product_code_unique",
               columnList = "product_code", unique = true),

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
        ),

        // Index for search
        @Index(
            name = "idx_product_search",
            columnList = "name, description"
        )
    }
)
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, length = 50)
    private String sku;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @ManyToOne
    private Category category;

    @Column(name = "product_code", length = 20)
    private String productCode;
}
```

### Indexes for Search and Filtering

```java
@Entity
@Table(
    name = "articles",
    indexes = {
        // Full-text search indexes
        @Index(name = "idx_article_title", columnList = "title"),
        @Index(name = "idx_article_content", columnList = "content"),
        @Index(name = "idx_article_author", columnList = "author_id"),

        // Indexes for filtering and sorting
        @Index(name = "idx_article_status_date",
               columnList = "status, published_at DESC"),
        @Index(name = "idx_author_date",
               columnList = "author_id, published_at DESC"),
        @Index(name = "idx_category_date",
               columnList = "category_id, published_at DESC"),

        // Range query indexes
        @Index(name = "idx_article_published_range",
               columnList = "published_at DESC"),
        @Index(name = "idx_article_created_range",
               columnList = "created_at DESC"),

        // Pagination optimization
        @Index(name = "idx_article_id_date",
               columnList = "id, published_at DESC"),

        // Status-specific indexes
        @Index(name = "idx_article_published",
               columnList = "status = 'PUBLISHED'"),
        @Index(name = "idx_article_draft",
               columnList = "status = 'DRAFT'")
    }
)
public class Article {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Enumerated(EnumType.STRING)
    private ArticleStatus status;  // DRAFT, PUBLISHED, ARCHIVED

    @Column(name = "published_at")
    private LocalDateTime publishedDate;

    @Column(name = "created_at")
    private LocalDateTime createdDate;

    @ManyToOne
    private User author;

    @ManyToOne
    private Category category;

    @Column(length = 100)
    private String slug;  // URL-friendly identifier

    @Column(length = 50)
    private String excerpt;
}

@Repository
public interface ArticleRepository extends JpaRepository<Article, Long> {
    // Uses idx_article_status_date
    Page<Article> findByStatusOrderByPublishedDateDesc(
        String status,
        Pageable pageable
    );

    // Uses idx_author_date
    Page<Article> findByAuthorOrderByPublishedDateDesc(
        User author,
        Pageable pageable
    );

    // Uses idx_article_published_range
    List<Article> findByPublishedDateAfterOrderByPublishedDateDesc(
        LocalDateTime date
    );

    // Custom query that benefits from multiple indexes
    @Query("""
        SELECT a FROM Article a
        WHERE a.status = :status
        AND a.publishedDate BETWEEN :start AND :end
        AND a.category = :category
        ORDER BY a.publishedDate DESC
        """)
    Page<Article> findPublishedInCategoryAndDateRange(
        @Param("status") String status,
        @Param("start") LocalDateTime start,
        @Param("end") LocalDateTime end,
        @Param("category") Category category,
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

    public Page<Article> getArticlesByAuthor(User author, int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("publishedDate").descending());
        return repository.findByAuthorOrderByPublishedDateDesc(author, pageable);
    }

    public List<Article> getRecentArticles(int limit) {
        return repository.findByPublishedDateAfterOrderByPublishedDateDesc(
            LocalDateTime.now().minusMonths(1)
        ).stream().limit(limit).collect(Collectors.toList());
    }
}
```

### Indexes on Relationships

```java
@Entity
@Table(
    name = "comments",
    indexes = {
        // Index for finding comments by article (most common query)
        @Index(name = "idx_comment_article", columnList = "article_id"),

        // Composite index for recent comments by article
        @Index(name = "idx_comment_article_created",
               columnList = "article_id, created_at DESC"),

        // Index for approved comments filtering
        @Index(name = "idx_comment_article_approved",
               columnList = "article_id, approved"),

        // Index for finding user comments
        @Index(name = "idx_comment_user", columnList = "user_id"),

        // Index for moderation
        @Index(name = "idx_comment_status_created",
               columnList = "status, created_at DESC"),

        // Index for spam detection
        @Index(name = "idx_comment_user_article",
               columnList = "user_id, article_id"),

        // Index for sentiment analysis
        @Index(name = "idx_comment_sentiment",
               columnList = "sentiment_score")
    }
)
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "article_id", nullable = false)
    private Article article;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(columnDefinition = "TEXT")
    private String text;

    @Column(name = "created_at")
    private LocalDateTime createdDate;

    private boolean approved;

    @Column(name = "approved_at")
    private LocalDateTime approvedDate;

    @Enumerated(EnumType.STRING)
    private CommentStatus status;  // PENDING, APPROVED, REJECTED, SPAM

    private Integer sentimentScore;  // For sentiment analysis
}

@Entity
@Table(
    name = "categories",
    indexes = {
        // Basic index
        @Index(name = "idx_category_name", columnList = "name"),

        // Composite index for product queries
        @Index(name = "idx_category_products_count",
               columnList = "parent_id, product_count DESC"),

        // Index for hierarchical navigation
        @Index(name = "idx_category_hierarchy",
               columnList = "parent_id, sort_order"),

        // Index for search
        @Index(name = "idx_category_search",
               columnList = "name, description, slug"),

        // Index for statistics
        @Index(name = "idx_category_stats",
               columnList = "is_active, product_count, created_at")
    }
)
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(length = 200)
    private String description;

    @Column(name = "slug", length = 100, unique = true)
    private String slug;

    @ManyToOne
    @JoinColumn(name = "parent_id")
    private Category parent;

    private Integer sortOrder;

    private boolean isActive;

    @Column(name = "product_count")
    private Long productCount;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}

@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {
    // Uses idx_comment_article
    List<Comment> findByArticle(Article article);

    // Uses idx_comment_article_created
    List<Comment> findByArticleOrderByCreatedDateDesc(Article article);

    // Uses idx_comment_article_approved
    long countByArticleAndApproved(Article article, boolean approved);

    // Uses idx_comment_user
    List<Comment> findByUser(User user);

    // Uses idx_comment_status_created
    List<Comment> findByStatusOrderByCreatedDateDesc(CommentStatus status);

    // Multiple indexes considered by query optimizer
    @Query("""
        SELECT c FROM Comment c
        WHERE c.article = :article
        AND c.approved = true
        ORDER BY c.createdDate DESC
        """)
    List<Comment> findApprovedCommentsByArticle(
        @Param("article") Article article,
        Pageable pageable
    );
}
```

### Index Best Practices

```java
@Entity
@Table(
    name = "products",
    indexes = {
        // Rule 1: Index on columns used in WHERE clauses
        @Index(name = "idx_product_status", columnList = "status"),

        // Rule 2: Index columns used in JOIN conditions
        @Index(name = "idx_product_category", columnList = "category_id"),

        // Rule 3: Create composite indexes for common multi-column queries
        @Index(name = "idx_category_status",
               columnList = "category_id, status"),

        // Rule 4: Include sorting columns in composite indexes
        @Index(name = "idx_status_created",
               columnList = "status, created_at DESC"),

        // Rule 5: Avoid over-indexing - only index what's frequently queried
        @Index(name = "idx_product_popularity",
               columnList = "view_count, sales_count DESC"),

        // Rule 6: Use partial indexes for filtered queries
        @Index(name = "idx_active_products",
               columnList = "status = 'ACTIVE'"),

        // Rule 7: Consider covering indexes for common query patterns
        @Index(name = "idx_product_covering",
               columnList = "category_id, name, price")
    }
)
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 255)
    private String name;

    @Enumerated(EnumType.STRING)
    private ProductStatus status;

    @ManyToOne
    private Category category;

    private Double viewCount;
    private Double salesCount;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}

// Example queries that benefit from proper indexing
@Service
public class ProductService {
    private final ProductRepository repository;

    // Benefits from idx_category_status
    public List<Product> getActiveProductsByCategory(Category category) {
        return repository.findByCategoryAndStatus(category, "ACTIVE");
    }

    // Benefits from idx_status_created
    public Page<Product> getRecentActiveProducts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("createdAt").descending());
        return repository.findByStatus("ACTIVE", pageable);
    }

    // Benefits from idx_product_popularity
    public List<Product> getPopularProducts(int limit) {
        return repository.findTop10ByOrderBySalesCountDesc()
            .stream()
            .limit(limit)
            .collect(Collectors.toList());
    }
}
```

## Multiple Database Configuration

### Basic Configuration for Multiple Databases

#### Primary Database Configuration
```java
@Configuration
@EnableJpaRepositories(
    basePackages = "com.example.users.repository",
    entityManagerFactoryRef = "usersEntityManager",
    transactionManagerRef = "usersTransactionManager"
)
@PropertySource("classpath:application-users.properties")
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

        HibernateJpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        em.setJpaVendorAdapter(vendorAdapter);

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
        properties.setProperty("hibernate.format_sql", "true");
        return properties;
    }
}
```

#### Secondary Database Configuration
```java
@Configuration
@EnableJpaRepositories(
    basePackages = "com.example.products.repository",
    entityManagerFactoryRef = "productsEntityManager",
    transactionManagerRef = "productsTransactionManager"
)
@PropertySource("classpath:application-products.properties")
public class ProductsDbConfig {

    @Bean
    @ConfigurationProperties(prefix = "products.datasource")
    public DataSource productsDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean productsEntityManager(
            DataSource productsDataSource) {
        LocalContainerEntityManagerFactoryBean em =
            new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(productsDataSource);
        em.setPackagesToScan("com.example.products.model");

        HibernateJpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        em.setJpaVendorAdapter(vendorAdapter);

        em.setJpaProperties(hibernateProperties());

        return em;
    }

    @Bean
    public PlatformTransactionManager productsTransactionManager(
            @Qualifier("productsEntityManager")
            LocalContainerEntityManagerFactoryBean productsEntityManager) {
        return new JpaTransactionManager(productsEntityManager.getObject());
    }

    private Properties hibernateProperties() {
        Properties properties = new Properties();
        properties.setProperty("hibernate.dialect",
            "org.hibernate.dialect.PostgreSQLDialect");
        properties.setProperty("hibernate.hbm2ddl.auto", "update");
        properties.setProperty("hibernate.show_sql", "false");
        return properties;
    }
}
```

#### Properties Configuration
```properties
# users.properties
users.datasource.url=jdbc:mysql://localhost:3306/users_db
users.datasource.username=root
users.datasource.password=password
users.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# products.properties
products.datasource.url=jdbc:postgresql://localhost:5432/products_db
products.datasource.username=postgres
products.datasource.password=postgres
products.datasource.driver-class-name=org.postgresql.Driver
```

### Entity Configuration for Multiple Databases

```java
// Users database entities
@Entity
@Table(name = "users", schema = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100, unique = true)
    private String email;

    @Column(length = 50, unique = true)
    private String username;

    @Enumerated(EnumType.STRING)
    private UserStatus status;

    @CreatedDate
    private LocalDateTime createdDate;

    @LastModifiedDate
    private LocalDateTime lastModifiedDate;
}

@Entity
@Table(name = "user_profiles", schema = "users")
public class UserProfile {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;

    @Column(length = 100)
    private String firstName;

    @Column(length = 100)
    private String lastName;

    @Column(length = 20)
    private String phoneNumber;

    @Enumerated(EnumType.STRING)
    private LanguagePreference language;
}

// Products database entities
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

    @ManyToOne
    private Category category;

    private Boolean isActive;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}

@Entity
@Table(name = "categories")
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @ManyToOne
    private Category parent;

    private Integer sortOrder;

    private Boolean isActive;
}
```

### Repository Configuration

```java
// Users repositories
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    Optional<User> findByUsername(String username);
    List<User> findByStatus(UserStatus status);
}

@Repository
public interface UserProfileRepository extends JpaRepository<UserProfile, Long> {
    Optional<UserProfile> findByUserId(Long userId);
}

// Products repositories
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory(Category category);
    List<Product> findByIsActiveTrue();
    Page<Product> findByIsActiveTrue(Pageable pageable);
}

@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {
    List<Category> findByParentIsNull();
    List<Category> findByParent(Category parent);
    List<Category> findByIsActiveTrueOrderBySortOrderAsc();
}
```

### Service Layer Configuration

```java
@Service
@Transactional("usersTransactionManager")
public class UserService {
    private final UserRepository userRepository;
    private final UserProfileRepository userProfileRepository;

    public UserService(UserRepository userRepository,
                     UserProfileRepository userProfileRepository) {
        this.userRepository = userRepository;
        this.userProfileRepository = userProfileRepository;
    }

    @Transactional(value = "usersTransactionManager", rollbackFor = Exception.class)
    public User createUser(UserCreateRequest request) {
        User user = new User();
        user.setEmail(request.email());
        user.setUsername(request.username());
        user.setStatus(UserStatus.ACTIVE);

        User savedUser = userRepository.save(user);

        UserProfile profile = new UserProfile();
        profile.setUser(savedUser);
        profile.setFirstName(request.firstName());
        profile.setLastName(request.lastName());
        profile.setLanguage(request.language());

        userProfileRepository.save(profile);

        return savedUser;
    }

    @Transactional(value = "usersTransactionManager", readOnly = true)
    public Optional<User> getUserByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    @Transactional(value = "usersTransactionManager")
    public void updateUserProfile(Long userId, ProfileUpdateRequest request) {
        UserProfile profile = userProfileRepository.findByUserId(userId)
            .orElseThrow(() -> new UserProfileNotFoundException(userId));

        profile.setFirstName(request.firstName());
        profile.setLastName(request.lastName());
        profile.setPhoneNumber(request.phoneNumber());

        userProfileRepository.save(profile);
    }
}

@Service
@Transactional("productsTransactionManager")
public class ProductService {
    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;

    public ProductService(ProductRepository productRepository,
                         CategoryRepository categoryRepository) {
        this.productRepository = productRepository;
        this.categoryRepository = categoryRepository;
    }

    @Transactional(value = "productsTransactionManager", readOnly = true)
    public Page<Product> getActiveProducts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return productRepository.findByIsActiveTrue(pageable);
    }

    @Transactional(value = "productsTransactionManager")
    public Product createProduct(ProductCreateRequest request) {
        Category category = categoryRepository.findById(request.categoryId())
            .orElseThrow(() -> new CategoryNotFoundException(request.categoryId()));

        Product product = new Product();
        product.setName(request.name());
        product.setPrice(request.price());
        product.setCategory(category);
        product.setIsActive(true);

        return productRepository.save(product);
    }

    @Transactional(value = "productsTransactionManager")
    public void updateProduct(Long productId, ProductUpdateRequest request) {
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));

        product.setName(request.name());
        product.setPrice(request.price());
        product.setUpdatedAt(LocalDateTime.now());

        productRepository.save(product);
    }
}
```

### Cross-Database Transactions

```java
@Service
public class OrderService {
    private final UserService userService;
    private final ProductService productService;
    private final OrderRepository orderRepository;

    @Transactional
    public Order createOrder(OrderRequest request) {
        // Start transaction (will handle cross-database operations)
        Order order = new Order();
        order.setOrderNumber(generateOrderNumber());
        order.setTotalAmount(request.totalAmount());
        order.setStatus(OrderStatus.PENDING);

        // Get user from users database
        User user = userService.getUserByEmail(request.userEmail())
            .orElseThrow(() -> new UserNotFoundException(request.userEmail()));

        // Get products from products database
        List<Product> products = request.productIds().stream()
            .map(productId -> productService.getProductById(productId)
                .orElseThrow(() -> new ProductNotFoundException(productId)))
            .collect(Collectors.toList());

        // Calculate total amount and validate
        BigDecimal calculatedTotal = products.stream()
            .map(Product::getPrice)
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        if (!calculatedTotal.equals(request.totalAmount())) {
            throw new OrderAmountMismatchException();
        }

        // Save order in products database
        Order savedOrder = orderRepository.save(order);

        // Create order items (cross-database operation)
        products.forEach(product -> {
            OrderItem item = new OrderItem();
            item.setOrder(savedOrder);
            item.setProduct(product);
            item.setQuantity(1); // Simplified for example
            item.setUnitPrice(product.getPrice());

            orderRepository.saveOrderItem(item); // Custom method
        });

        return savedOrder;
    }

    @Transactional(value = "usersTransactionManager")
    @Transactional(value = "productsTransactionManager", propagation = Propagation.REQUIRES_NEW)
    public void processPayment(Order order, Payment payment) {
        // Payment processing logic
        // Updates both user and product databases
    }
}
```

### Database-Specific Configuration

```java
// Custom Hibernate configuration for each database
@Configuration
public class HibernateConfig {

    @Bean
    @Primary
    public HibernateJpaVendorAdapter primaryJpaVendorAdapter() {
        HibernateJpaVendorAdapter adapter = new HibernateJpaVendorAdapter();
        adapter.setDatabasePlatform("org.hibernate.dialect.MySQL8Dialect");
        return adapter;
    }

    @Bean
    public HibernateJpaVendorAdapter secondaryJpaVendorAdapter() {
        HibernateJpaVendorAdapter adapter = new HibernateJpaVendorAdapter();
        adapter.setDatabasePlatform("org.hibernate.dialect.PostgreSQLDialect");
        return adapter;
    }

    @Bean
    public JpaProperties jpaProperties() {
        return new JpaProperties();
    }
}

// DataSource routing for dynamic database selection
@Component
public class DataSourceRouter extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        return DatabaseContextHolder.getCurrentDatabase();
    }
}

@Component
public class DatabaseContextHolder {
    private static final ThreadLocal<DatabaseType> CONTEXT = new ThreadLocal<>();

    public static void setCurrentDatabase(DatabaseType databaseType) {
        CONTEXT.set(databaseType);
    }

    public static DatabaseType getCurrentDatabase() {
        return CONTEXT.get();
    }

    public static void clear() {
        CONTEXT.remove();
    }
}

public enum DatabaseType {
    USERS, PRODUCTS
}

// Dynamic database selection aspect
@Aspect
@Component
public class DatabaseAspect {

    @Around("@annotation(selectDatabase)")
    public Object selectDatabase(ProceedingJoinPoint joinPoint,
                                SelectDatabase selectDatabase) throws Throwable {
        DatabaseType databaseType = selectDatabase.value();
        DatabaseType previousType = DatabaseContextHolder.getCurrentDatabase();

        try {
            DatabaseContextHolder.setCurrentDatabase(databaseType);
            return joinPoint.proceed();
        } finally {
            DatabaseContextHolder.setCurrentDatabase(previousType);
        }
    }
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface SelectDatabase {
    DatabaseType value();
}
```

### Advanced Configuration with Connection Pooling

```java
@Configuration
@EnableConfigurationProperties(DbProperties.class)
public class MultiDatabaseConfig {

    @Bean
    @Primary
    @ConfigurationProperties(prefix = "primary.datasource.hikari")
    public HikariDataSource primaryDataSource(DbProperties dbProperties) {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(dbProperties.getPrimary().getUrl());
        dataSource.setUsername(dbProperties.getPrimary().getUsername());
        dataSource.setPassword(dbProperties.getPrimary().getPassword());
        dataSource.setDriverClassName(dbProperties.getPrimary().getDriverClassName());

        // Connection pool settings
        dataSource.setMaximumPoolSize(20);
        dataSource.setMinimumIdle(5);
        dataSource.setConnectionTimeout(30000);
        dataSource.setIdleTimeout(600000);
        dataSource.setMaxLifetime(1800000);

        return dataSource;
    }

    @Bean
    @ConfigurationProperties(prefix = "secondary.datasource.hikari")
    public HikariDataSource secondaryDataSource(DbProperties dbProperties) {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(dbProperties.getSecondary().getUrl());
        dataSource.setUsername(dbProperties.getSecondary().getUsername());
        dataSource.setPassword(dbProperties.getSecondary().getPassword());
        dataSource.setDriverClassName(dbProperties.getSecondary().getDriverClassName());

        // Different connection pool settings for secondary DB
        dataSource.setMaximumPoolSize(10);
        dataSource.setMinimumIdle(2);
        dataSource.setConnectionTimeout(20000);

        return dataSource;
    }
}

@ConfigurationProperties
@Data
public class DbProperties {
    private DataSourceConfig primary;
    private DataSourceConfig secondary;

    @Data
    public static class DataSourceConfig {
        private String url;
        private String username;
        private String password;
        private String driverClassName;
    }
}
```

## Examples

### Complete CRUD Service

```java
@Service
@Transactional("usersTransactionManager")
public class UserService {
    private final UserRepository repository;
    private final UserProfileRepository profileRepository;
    private final RoleRepository roleRepository;

    public UserService(UserRepository repository,
                     UserProfileRepository profileRepository,
                     RoleRepository roleRepository) {
        this.repository = repository;
        this.profileRepository = profileRepository;
        this.roleRepository = roleRepository;
    }

    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        return repository.findAll();
    }

    @Transactional(readOnly = true)
    public Page<User> getUsersPage(int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("createdDate").descending());
        return repository.findAll(pageable);
    }

    @Transactional(readOnly = true)
    public User getUser(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found: " + id));
    }

    @Transactional(value = "usersTransactionManager", rollbackFor = Exception.class)
    public User createUser(CreateUserRequest request) {
        if (repository.findByEmail(request.email()).isPresent()) {
            throw new EmailAlreadyExistsException(request.email());
        }

        User user = new User();
        user.setEmail(request.email());
        user.setUsername(request.username());
        user.setStatus(UserStatus.ACTIVE);

        // Set default roles
        List<Role> defaultRoles = roleRepository.findByNameIn(Arrays.asList("USER"));
        user.setRoles(new HashSet<>(defaultRoles));

        User savedUser = repository.save(user);

        // Create profile
        UserProfile profile = new UserProfile();
        profile.setUser(savedUser);
        profile.setFirstName(request.firstName());
        profile.setLastName(request.lastName());
        profile.setLanguage(request.language());

        profileRepository.save(profile);

        return savedUser;
    }

    @Transactional(value = "usersTransactionManager", rollbackFor = Exception.class)
    public User updateUser(Long id, UpdateUserRequest request) {
        User user = getUser(id);

        if (!request.email().equals(user.getEmail()) &&
            repository.findByEmail(request.email()).isPresent()) {
            throw new EmailAlreadyExistsException(request.email());
        }

        user.setEmail(request.email());
        user.setUsername(request.username());
        user.setStatus(request.status());

        User updatedUser = repository.save(user);

        // Update profile
        UserProfile profile = profileRepository.findByUserId(id)
            .orElseThrow(() -> new UserProfileNotFoundException(id));

        profile.setFirstName(request.firstName());
        profile.setLastName(request.lastName());
        profile.setLanguage(request.language());

        profileRepository.save(profile);

        return updatedUser;
    }

    @Transactional(value = "usersTransactionManager", rollbackFor = Exception.class)
    public void deleteUser(Long id) {
        User user = getUser(id);

        // Soft delete by setting status
        user.setStatus(UserStatus.DELETED);
        repository.save(user);

        // Delete profile
        profileRepository.deleteByUserId(id);
    }

    @Transactional(value = "usersTransactionManager", readOnly = true)
    public long countByStatus(UserStatus status) {
        return repository.countByStatus(status);
    }

    @Transactional(value = "usersTransactionManager", readOnly = true)
    public List<User> searchUsers(UserSearchCriteria criteria) {
        if (criteria.isEmpty()) {
            return repository.findAll();
        }

        return repository.findByEmailContainingOrUsernameContainingOrFirstNameContainingOrLastNameContaining(
            criteria.searchTerm(),
            criteria.searchTerm(),
            criteria.searchTerm(),
            criteria.searchTerm()
        );
    }
}
```

### Search with Multiple Criteria

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    // Derived query methods
    List<Product> findByCategory(Category category);
    List<Product> findByPriceGreaterThan(BigDecimal price);
    List<Product> findByStatusAndPriceBetween(ProductStatus status,
                                            BigDecimal minPrice, BigDecimal maxPrice);

    // Custom search query
    @Query("""
        SELECT p FROM Product p
        WHERE (:name IS NULL OR LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%')))
        AND (:category IS NULL OR p.category.id = :category)
        AND (:minPrice IS NULL OR p.price >= :minPrice)
        AND (:maxPrice IS NULL OR p.price <= :maxPrice)
        AND (:status IS NULL OR p.status = :status)
        AND p.isActive = true
        ORDER BY p.createdAt DESC
        """)
    Page<Product> searchProducts(
        @Param("name") String name,
        @Param("category") Long category,
        @Param("minPrice") BigDecimal minPrice,
        @Param("maxPrice") BigDecimal maxPrice,
        @Param("status") ProductStatus status,
        Pageable pageable
    );

    // Native query for complex filtering
    @Query(value = """
        SELECT p.* FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE (:name IS NULL OR LOWER(p.name) LIKE LOWER(CONCAT('%', :name, '%')))
        AND (:category IS NULL OR c.id = :category)
        AND (:minPrice IS NULL OR p.price >= :minPrice)
        AND (:maxPrice IS NULL OR p.price <= :maxPrice)
        AND (:status IS NULL OR p.status = :status)
        AND p.is_active = true
        ORDER BY p.created_at DESC
        """, nativeQuery = true)
    Page<Product> searchProductsNative(
        @Param("name") String name,
        @Param("category") Long category,
        @Param("minPrice") BigDecimal minPrice,
        @Param("maxPrice") BigDecimal maxPrice,
        @Param("status") String status,
        Pageable pageable
    );
}

@Service
public class ProductSearchService {
    private final ProductRepository repository;

    public Page<Product> search(ProductSearchCriteria criteria, int page, int size) {
        Pageable pageable = PageRequest.of(page, size,
            Sort.by("createdAt").descending());

        return repository.searchProducts(
            criteria.name(),
            criteria.categoryId(),
            criteria.minPrice(),
            criteria.maxPrice(),
            criteria.status(),
            pageable
        );
    }

    public List<Product> findPopularProducts(int limit) {
        return repository.findTop10ByOrderBySalesCountDesc()
            .stream()
            .limit(limit)
            .collect(Collectors.toList());
    }

    public List<Product> findRelatedProducts(Product product, int limit) {
        return repository.findByCategoryAndIdNot(product.getCategory(), product.getId())
            .stream()
            .limit(limit)
            .collect(Collectors.toList());
    }
}

// Search criteria DTO
public record ProductSearchCriteria(
    @NotBlank String name,
    Long categoryId,
    BigDecimal minPrice,
    BigDecimal maxPrice,
    String status
) {}

// Search criteria builder
public class ProductSearchCriteriaBuilder {
    private String name;
    private Long categoryId;
    private BigDecimal minPrice;
    private BigDecimal maxPrice;
    private String status;

    public ProductSearchCriteriaBuilder name(String name) {
        this.name = name;
        return this;
    }

    public ProductSearchCriteriaBuilder categoryId(Long categoryId) {
        this.categoryId = categoryId;
        return this;
    }

    public ProductSearchCriteriaBuilder priceRange(BigDecimal min, BigDecimal max) {
        this.minPrice = min;
        this.maxPrice = max;
        return this;
    }

    public ProductSearchCriteriaBuilder status(String status) {
        this.status = status;
        return this;
    }

    public ProductSearchCriteria build() {
        return new ProductSearchCriteria(name, categoryId, minPrice, maxPrice, status);
    }
}
```

## Best Practices

### Entity Design

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", nullable = false, length = 255)
    private String name;

    @Column(name = "price", precision = 10, scale = 2, nullable = false)
    private BigDecimal price;

    @Column(name = "created_date", nullable = false, updatable = false)
    private LocalDateTime createdDate;

    @Column(name = "updated_date")
    private LocalDateTime updatedDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;

    @Enumerated(EnumType.STRING)
    private ProductStatus status;

    // Constructor injection pattern
    public Product(String name, BigDecimal price, Category category) {
        this.name = name;
        this.price = price;
        this.category = category;
        this.status = ProductStatus.ACTIVE;
        this.createdDate = LocalDateTime.now();
        this.updatedDate = LocalDateTime.now();
    }

    // Business logic methods
    public void updatePrice(BigDecimal newPrice) {
        if (newPrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Price must be positive");
        }
        this.price = newPrice;
        this.updatedDate = LocalDateTime.now();
    }

    public void activate() {
        this.status = ProductStatus.ACTIVE;
        this.updatedDate = LocalDateTime.now();
    }

    public void deactivate() {
        this.status = ProductStatus.INACTIVE;
        this.updatedDate = LocalDateTime.now();
    }

    // equals() and hashCode() based on id
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Product product = (Product) o;
        return Objects.equals(id, product.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
```

### Repository Queries

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
        @Param("status") UserStatus status,
        @Param("startDate") LocalDateTime startDate
    );

    // Good: Using projection for better performance
    @Query("""
        SELECT new com.example.dto.UserSummary(u.id, u.email, u.status, u.createdDate)
        FROM User u
        WHERE u.status = :status
        """)
    List<UserSummary> findUserSummariesByStatus(@Param("status") UserStatus status);

    // Avoid: Long method name
    // List<User> findByStatusAndCreatedDateGreaterThanAndLastLoginDateLessThan(...)

    // Avoid: Not using Optional for single results
    // User findByEmail(String email);  // Should return Optional<User>
}
```

### Pagination Best Practices

```java
@Service
public class ProductService {
    private final ProductRepository repository;

    public Page<Product> getProducts(int page, int size) {
        // Validate pagination parameters
        if (page < 0) {
            throw new IllegalArgumentException("Page number must be non-negative");
        }
        if (size <= 0 || size > 100) {
            throw new IllegalArgumentException("Page size must be between 1 and 100");
        }

        Pageable pageable = PageRequest.of(page, size,
            Sort.by("id").ascending());
        return repository.findAll(pageable);
    }

    public List<Product> getRecentProducts(int limit) {
        // Use list for smaller datasets where you need exact count
        if (limit <= 0 || limit > 100) {
            throw new IllegalArgumentException("Limit must be between 1 and 100");
        }

        return repository.findTop10ByOrderByCreatedAtDesc()
            .stream()
            .limit(limit)
            .collect(Collectors.toList());
    }

    public Slice<Product> getRecentProductsWithCursor(Long lastId, int size) {
        // Use cursor-based pagination for better performance
        Sort sort = Sort.by("id").ascending();
        Pageable pageable = PageRequest.of(0, size, sort);

        if (lastId != null) {
            return repository.findByIdGreaterThan(lastId, pageable);
        } else {
            return repository.findAll(pageable);
        }
    }
}
```

### Transaction Management

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentRepository paymentRepository;

    @Transactional
    public Order createOrder(Order order, Payment payment) {
        // Validate business rules
        if (order.getItems().isEmpty()) {
            throw new EmptyOrderException("Order must contain at least one item");
        }

        // Calculate total amount
        BigDecimal total = order.getItems().stream()
            .map(item -> item.getPrice().multiply(new BigDecimal(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        if (total.compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidOrderAmountException("Order total must be positive");
        }

        // Set order details
        order.setTotalAmount(total);
        order.setStatus(OrderStatus.PENDING);
        order.setOrderNumber(generateOrderNumber());

        // Save order
        Order savedOrder = orderRepository.save(order);

        // Process payment
        payment.setOrderId(savedOrder.getId());
        payment.setAmount(total);
        paymentRepository.save(payment);

        return savedOrder;
    }

    @Transactional(readOnly = true)
    public Order getOrderWithDetails(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    @Transactional(rollbackFor = {PaymentException.class, InventoryException.class})
    public void processPayment(Long orderId) throws PaymentException {
        Order order = getOrderWithDetails(orderId);

        // Process payment logic
        paymentService.process(order.getPayment());

        // Update order status
        order.setStatus(OrderStatus.PROCESSING);
        order.setUpdatedAt(LocalDateTime.now());

        orderRepository.save(order);

        // This will trigger rollback if thrown
        if (paymentFailed) {
            throw new PaymentException("Payment processing failed");
        }

        // Update inventory after successful payment
        inventoryService.reserveItems(order.getItems());
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOrderCreation(Order order) {
        // Always creates new transaction
        auditLogRepository.save(new AuditLog("ORDER_CREATED", order.getId()));
    }
}
```

### N+1 Query Problem Solutions

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    // Solution 1: Use JOIN FETCH
    @Query("""
        SELECT DISTINCT o FROM Order o
        JOIN FETCH o.items
        JOIN FETCH o.customer
        WHERE o.id = :orderId
        """)
    Optional<Order> findOrderWithItemsAndCustomer(@Param("orderId") Long orderId);

    // Solution 2: Use EntityGraph
    @EntityGraph(attributePaths = {"items", "customer", "items.product"})
    Optional<Order> findWithDetailsById(Long orderId);

    // Solution 3: Use batch loading
    @Query("SELECT o FROM Order o WHERE o.customer.id = :customerId")
    List<Order> findByCustomerId(@Param("customerId") Long customerId);

    // Solution 4: Use DTO projection
    @Query("""
        SELECT new com.example.dto.OrderSummary(
            o.id, o.orderNumber, o.totalAmount, o.status,
            c.firstName, c.lastName
        ) FROM Order o
        JOIN o.customer c
        WHERE o.customer.id = :customerId
        """)
    List<OrderSummary> findOrderSummariesByCustomerId(@Param("customerId") Long customerId);
}

@Service
public class OrderService {
    private final OrderRepository orderRepository;

    // Solution using JOIN FETCH
    @Transactional(readOnly = true)
    public Order getOrderWithDetails(Long orderId) {
        return orderRepository.findOrderWithItemsAndCustomer(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    // Solution using batch loading
    @Transactional(readOnly = true)
    public List<Order> getCustomerOrdersWithDetails(Long customerId) {
        List<Order> orders = orderRepository.findByCustomerId(customerId);

        // Batch load items for all orders
        Map<Long, List<OrderItem>> orderItems = orderRepository.findOrderItemsByOrderIds(
            orders.stream().map(Order::getId).collect(Collectors.toList())
        );

        // Batch load products for all items
        Map<Long, Product> products = orderRepository.findProductsByItemIds(
            orderItems.values().stream()
                .flatMap(List::stream)
                .map(OrderItem::getId)
                .collect(Collectors.toList())
        );

        // Associate items with their orders
        orders.forEach(order -> {
            List<OrderItem> items = orderItems.getOrDefault(order.getId(), Collections.emptyList());
            items.forEach(item -> {
                item.setProduct(products.get(item.getProductId()));
                order.addItem(item);
            });
        });

        return orders;
    }

    // Solution using DTO projection (most efficient)
    @Transactional(readOnly = true)
    public List<OrderSummary> getCustomerOrderSummaries(Long customerId) {
        return orderRepository.findOrderSummariesByCustomerId(customerId);
    }
}
```

### Exception Handling

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

    public Product createProduct(ProductCreateRequest request) {
        // Validate business rules
        if (request.name() == null || request.name().trim().isEmpty()) {
            throw new InvalidProductException("Product name cannot be empty");
        }

        if (request.price() == null || request.price().compareTo(BigDecimal.ZERO) < 0) {
            throw new InvalidProductException("Product price must be non-negative");
        }

        if (repository.findByNameIgnoreCase(request.name()).isPresent()) {
            throw new DuplicateProductException("Product with name '" + request.name() + "' already exists");
        }

        Product product = new Product();
        product.setName(request.name());
        product.setPrice(request.price());
        product.setDescription(request.description());
        product.setStatus(ProductStatus.ACTIVE);

        return repository.save(product);
    }

    public Product updateProduct(Long id, ProductUpdateRequest request) {
        Product product = getProduct(id);

        if (request.name() != null) {
            if (!request.name().equals(product.getName()) &&
                repository.findByNameIgnoreCase(request.name()).isPresent()) {
                throw new DuplicateProductException("Product with name '" + request.name() + "' already exists");
            }
            product.setName(request.name());
        }

        if (request.price() != null) {
            if (request.price().compareTo(BigDecimal.ZERO) < 0) {
                throw new InvalidProductException("Product price must be non-negative");
            }
            product.setPrice(request.price());
        }

        if (request.description() != null) {
            product.setDescription(request.description());
        }

        return repository.save(product);
    }

    @Transactional(rollbackFor = Exception.class)
    public void deleteProduct(Long id) {
        Product product = getProduct(id);

        // Check if product can be deleted (e.g., has orders)
        if (orderService.hasOrdersForProduct(id)) {
            throw new ProductDeletionException("Cannot delete product with existing orders");
        }

        repository.delete(product);
    }
}

// Custom exceptions
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}

public class DuplicateProductException extends RuntimeException {
    public DuplicateProductException(String message) {
        super(message);
    }
}

public class InvalidProductException extends RuntimeException {
    public InvalidProductException(String message) {
        super(message);
    }
}

public class ProductDeletionException extends RuntimeException {
    public ProductDeletionException(String message) {
        super(message);
    }
}
```

## References

- [Spring Data JPA Official Documentation](https://spring.io/projects/spring-data-jpa)
- [Hibernate Documentation](https://hibernate.org/)
- [JPA Specification](https://jakarta.ee/specifications/persistence/)
- [Spring Data Commons Reference](https://docs.spring.io/spring-data/commons/docs/current/reference/html/)
- [Database Indexing Guide](https://use-the-index-luke.com/)