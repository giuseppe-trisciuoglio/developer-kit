# Transaction Management

Transaction management is crucial for ensuring data consistency in Camel routes. This guide covers transaction patterns, configuration, and best practices.

## Spring Transaction Management

### Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jpa</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jpa-starter</artifactId>
</dependency>
```

### Basic Transaction Configuration

```java
@Configuration
@EnableTransactionManagement
public class TransactionConfig {

    @Bean
    public PlatformTransactionManager transactionManager(EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }

    @Bean
    public SpringTransactionPolicy PROPAGATION_REQUIRED(
            PlatformTransactionManager transactionManager) {
        SpringTransactionPolicy policy = new SpringTransactionPolicy();
        policy.setTransactionManager(transactionManager);
        policy.setPropagationBehaviorName("PROPAGATION_REQUIRED");
        return policy;
    }

    @Bean
    public SpringTransactionPolicy PROPAGATION_REQUIRES_NEW(
            PlatformTransactionManager transactionManager) {
        SpringTransactionPolicy policy = new SpringTransactionPolicy();
        policy.setTransactionManager(transactionManager);
        policy.setPropagationBehaviorName("PROPAGATION_REQUIRES_NEW");
        return policy;
    }
}
```

### Transactional Route

```java
@Component
public class TransactionalRoute extends RouteBuilder {

    @Override
    public void configure() {
        from("jms:queue:orders?transacted=true")
            .routeId("transactional-order-processor")
            .transacted("PROPAGATION_REQUIRED")
            .to("jpa:com.example.model.Order")
            .to("sql:INSERT INTO audit_log VALUES (:#${body.id}, :#${body.status})")
            .to("jms:queue:processed");
    }
}
```

## JMS Transactions

### JMS Transaction Configuration

```java
@Configuration
public class JmsConfig {

    @Bean
    public JmsTransactionManager jmsTransactionManager(
            ConnectionFactory connectionFactory) {
        return new JmsTransactionManager(connectionFactory);
    }

    @Bean
    public JmsComponent jms(
            ConnectionFactory connectionFactory,
            JmsTransactionManager transactionManager) {
        JmsComponent component = new JmsComponent();
        component.setConnectionFactory(connectionFactory);
        component.setTransactionManager(transactionManager);
        component.setTransacted(true);
        return component;
    }
}
```

### JMS Transactional Route

```java
from("jms:queue:orders?transacted=true")
    .routeId("jms-transactional")
    .transacted()
    .to("bean:orderService")
    .to("jms:queue:notifications")
    .to("jms:queue:audit");
```

### Rollback on Exception

```java
from("jms:queue:orders?transacted=true")
    .transacted()
    .doTry()
        .to("bean:orderService?method=process")
        .to("jms:queue:processed")
    .doCatch(ValidationException.class)
        .log("Validation failed, rolling back transaction")
        .rollback()
    .doCatch(Exception.class)
        .log("Processing failed, rolling back transaction")
        .rollback()
    .end();
```

## XA (Distributed) Transactions

### XA Configuration

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jta-atomikos</artifactId>
</dependency>
```

```java
@Configuration
public class XAConfig {

    @Bean
    public JtaTransactionManager transactionManager() {
        UserTransactionManager utm = new UserTransactionManager();
        UserTransaction ut = new UserTransactionImp();

        JtaTransactionManager jtaTransactionManager = new JtaTransactionManager();
        jtaTransactionManager.setTransactionManager(utm);
        jtaTransactionManager.setUserTransaction(ut);
        return jtaTransactionManager;
    }

    @Bean
    public SpringTransactionPolicy PROPAGATION_REQUIRED(
            JtaTransactionManager transactionManager) {
        SpringTransactionPolicy policy = new SpringTransactionPolicy();
        policy.setTransactionManager(transactionManager);
        policy.setPropagationBehaviorName("PROPAGATION_REQUIRED");
        return policy;
    }
}
```

### XA Transactional Route

```java
from("jms:queue:orders?transacted=true")
    .transacted("PROPAGATION_REQUIRED")
    .to("jpa:com.example.model.Order")          // Database 1
    .to("jms:queue:inventory-updates")           // JMS
    .to("sql:INSERT INTO audit_db.logs...")      // Database 2
    .to("jms:queue:notifications");              // JMS
```

## Transaction Patterns

### Pattern: Transactional Client

Ensures all operations within a transaction boundary succeed or fail together.

```java
from("jms:queue:orders?transacted=true")
    .transacted()
    .to("jpa:com.example.model.Order")
    .to("jpa:com.example.model.OrderItem")
    .to("jms:queue:order-created");
```

### Pattern: Idempotent Consumer with Transaction

Ensures exactly-once processing with transactional semantics.

```java
@Bean
public IdempotentRepository idempotentRepository(DataSource dataSource) {
    return JdbcMessageIdRepository.jdbcMessageIdRepository(
        dataSource, "orderProcessor");
}

from("jms:queue:orders?transacted=true")
    .transacted()
    .idempotentConsumer(header("MessageId"))
        .messageIdRepositoryRef("idempotentRepository")
        .to("jpa:com.example.model.Order")
        .to("jms:queue:processed")
    .end();
```

### Pattern: Compensating Transaction (Saga)

When distributed transactions are not feasible, use compensating transactions.

```java
@Component
public class SagaRoute extends RouteBuilder {

    @Override
    public void configure() {
        from("direct:create-order")
            .routeId("order-saga")
            .doTry()
                .to("direct:reserve-inventory")
                .to("direct:charge-customer")
                .to("direct:ship-order")
                .to("direct:complete-order")
            .doCatch(Exception.class)
                .to("direct:compensate")
            .end();

        from("direct:compensate")
            .routeId("saga-compensation")
            .log("Starting compensation")
            .to("direct:release-inventory")
            .to("direct:refund-customer")
            .to("direct:cancel-order");
    }
}
```

## Error Handling in Transactions

### Automatic Rollback

```java
onException(Exception.class)
    .handled(true)
    .markRollbackOnly()
    .to("jms:queue:errors");

from("jms:queue:orders?transacted=true")
    .transacted()
    .to("bean:orderService")
    .to("jms:queue:processed");
```

### Selective Rollback

```java
onException(ValidationException.class)
    .handled(true)
    .markRollbackOnly()
    .to("jms:queue:validation-errors");

onException(RetryableException.class)
    .handled(false)  // Let transaction rollback and retry
    .maximumRedeliveries(3);

from("jms:queue:orders?transacted=true")
    .transacted()
    .to("bean:orderService")
    .to("jms:queue:processed");
```

### Continue on Exception

```java
onException(NonCriticalException.class)
    .handled(true)
    .continued(true)  // Don't rollback, continue processing
    .log("Non-critical error, continuing");

from("jms:queue:orders?transacted=true")
    .transacted()
    .to("bean:orderService")
    .to("jms:queue:processed");
```

## Transaction Propagation

### PROPAGATION_REQUIRED (Default)

Joins existing transaction or creates new one.

```java
from("direct:outer")
    .transacted("PROPAGATION_REQUIRED")
    .to("direct:inner");

from("direct:inner")
    .transacted("PROPAGATION_REQUIRED")  // Joins outer transaction
    .to("jpa:com.example.model.Entity");
```

### PROPAGATION_REQUIRES_NEW

Always creates a new transaction, suspending the current one.

```java
from("direct:outer")
    .transacted("PROPAGATION_REQUIRED")
    .to("jpa:com.example.model.Order")
    .to("direct:audit");

from("direct:audit")
    .transacted("PROPAGATION_REQUIRES_NEW")  // New transaction
    .to("jpa:com.example.model.AuditLog");   // Commits independently
```

### PROPAGATION_NOT_SUPPORTED

Suspends current transaction if exists.

```java
from("direct:outer")
    .transacted("PROPAGATION_REQUIRED")
    .to("jpa:com.example.model.Order")
    .to("direct:log");

from("direct:log")
    .transacted("PROPAGATION_NOT_SUPPORTED")  // Suspend transaction
    .log("Logging outside transaction");
```

## Isolation Levels

```java
@Bean
public SpringTransactionPolicy readCommitted(
        PlatformTransactionManager transactionManager) {
    SpringTransactionPolicy policy = new SpringTransactionPolicy();
    policy.setTransactionManager(transactionManager);
    policy.setPropagationBehaviorName("PROPAGATION_REQUIRED");
    policy.setIsolationLevelName("ISOLATION_READ_COMMITTED");
    return policy;
}

from("direct:query")
    .transacted("readCommitted")
    .to("jpa:com.example.model.Order?query=SELECT o FROM Order o WHERE o.status = 'PENDING'");
```

## Transaction Timeout

```java
@Bean
public SpringTransactionPolicy timeoutPolicy(
        PlatformTransactionManager transactionManager) {
    SpringTransactionPolicy policy = new SpringTransactionPolicy();
    policy.setTransactionManager(transactionManager);
    policy.setTimeout(30);  // 30 seconds
    return policy;
}

from("jms:queue:long-running?transacted=true")
    .transacted("timeoutPolicy")
    .to("bean:longRunningService");
```

## Testing Transactions

### Transactional Test

```java
@CamelSpringBootTest
@SpringBootTest
@Transactional
class TransactionalRouteTest {

    @Autowired
    private ProducerTemplate producer;

    @Autowired
    private CamelContext context;

    @Autowired
    private EntityManager entityManager;

    @Test
    @Rollback  // Rollback after test
    void testTransactionalRoute() {
        Order order = new Order("123", 100.0);
        producer.sendBody("direct:create-order", order);

        entityManager.flush();
        Order saved = entityManager.find(Order.class, "123");
        assertNotNull(saved);
    }

    @Test
    void testRollbackOnError() {
        Order invalidOrder = new Order(null, -100.0);

        assertThrows(Exception.class, () ->
            producer.sendBody("direct:create-order", invalidOrder)
        );

        // Verify transaction was rolled back
        Order notSaved = entityManager.find(Order.class, null);
        assertNull(notSaved);
    }
}
```

## Best Practices

### 1. Keep Transactions Short

```java
// Good: Short transaction
from("jms:queue:orders?transacted=true")
    .transacted()
    .to("jpa:com.example.model.Order")
    .to("jms:queue:processed");

// Bad: Long-running transaction
from("jms:queue:orders?transacted=true")
    .transacted()
    .to("http://slow-external-service")  // Network I/O
    .delay(5000)                          // Long delay
    .to("jpa:com.example.model.Order");
```

### 2. Use Appropriate Propagation

```java
// Audit should succeed even if main transaction fails
from("direct:process")
    .transacted("PROPAGATION_REQUIRED")
    .to("bean:processOrder")
    .to("direct:audit-success");

from("direct:audit-success")
    .transacted("PROPAGATION_REQUIRES_NEW")
    .to("jpa:com.example.model.AuditLog");
```

### 3. Handle Deadlocks

```java
onException(CannotAcquireLockException.class)
    .handled(false)
    .maximumRedeliveries(5)
    .redeliveryDelay(1000)
    .backOffMultiplier(2)
    .retryAttemptedLogLevel(LoggingLevel.WARN);

from("jms:queue:orders?transacted=true")
    .transacted()
    .to("jpa:com.example.model.Order");
```

### 4. Avoid Mixed Transaction Managers

```java
// Bad: Mixing JPA and JMS without XA
from("jms:queue:orders")
    .to("jpa:com.example.model.Order")    // Local JPA transaction
    .to("jms:queue:processed");            // Separate JMS transaction

// Good: Use XA or separate transactions explicitly
from("jms:queue:orders?transacted=true")
    .transacted("PROPAGATION_REQUIRED")  // XA transaction
    .to("jpa:com.example.model.Order")
    .to("jms:queue:processed");
```

### 5. Log Transaction Boundaries

```java
from("jms:queue:orders?transacted=true")
    .routeId("transactional-processor")
    .log("Starting transaction for order: ${body.id}")
    .transacted()
    .to("jpa:com.example.model.Order")
    .to("jms:queue:processed")
    .log("Transaction completed for order: ${body.id}");
```

### 6. Monitor Transaction Performance

```java
from("jms:queue:orders?transacted=true")
    .transacted()
    .to("micrometer:timer:transaction.duration?action=start")
    .to("jpa:com.example.model.Order")
    .to("jms:queue:processed")
    .to("micrometer:timer:transaction.duration?action=stop");
```

## Common Pitfalls

### ❌ Non-Transactional Resource in Transaction

```java
// JMS is transacted, but HTTP is not
from("jms:queue:orders?transacted=true")
    .transacted()
    .to("http://external-service")  // Not transactional!
    .to("jpa:com.example.model.Order");
```

### ❌ Wrong Transaction Manager

```java
// Using JPA transaction manager for JMS
from("jms:queue:orders")
    .transacted("jpaTxManager")  // Wrong manager!
    .to("jms:queue:processed");
```

### ❌ Forgetting Transaction Attribute

```java
// Missing transacted() DSL
from("jms:queue:orders?transacted=true")
    // Missing .transacted()
    .to("jpa:com.example.model.Order");
```

## Transaction Monitoring

```java
@Component
public class TransactionMonitor {

    @Autowired
    private PlatformTransactionManager transactionManager;

    @Scheduled(fixedRate = 60000)
    public void monitorTransactions() {
        if (transactionManager instanceof AbstractPlatformTransactionManager) {
            AbstractPlatformTransactionManager tm =
                (AbstractPlatformTransactionManager) transactionManager;

            log.info("Transaction Manager Status: {}",
                tm.getClass().getSimpleName());
        }
    }
}
```

## References

- [Spring Transaction Management](https://docs.spring.io/spring-framework/docs/current/reference/html/data-access.html#transaction)
- [Camel Transactional Client](https://camel.apache.org/components/latest/eips/transactional-client.html)
- [JTA Transactions](https://www.atomikos.com/Documentation/SpringIntegration)
