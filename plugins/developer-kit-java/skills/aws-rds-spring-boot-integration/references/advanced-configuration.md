# AWS RDS Aurora Advanced Configuration

## Read/Write Split Configuration

For applications with heavy read operations, configure separate datasources:

**Multi-Datasource Configuration Class:**
```java
@Configuration
public class AuroraDataSourceConfig {

    @Primary
    @Bean(name = "writerDataSource")
    @ConfigurationProperties("spring.datasource.writer")
    public DataSource writerDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean(name = "readerDataSource")
    @ConfigurationProperties("spring.datasource.reader")
    public DataSource readerDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Primary
    @Bean(name = "writerEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean writerEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("writerDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .packages("com.example.domain")
                .persistenceUnit("writer")
                .build();
    }

    @Bean(name = "readerEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean readerEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("readerDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .packages("com.example.domain")
                .persistenceUnit("reader")
                .build();
    }

    @Primary
    @Bean(name = "writerTransactionManager")
    public PlatformTransactionManager writerTransactionManager(
            @Qualifier("writerEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }

    @Bean(name = "readerTransactionManager")
    public PlatformTransactionManager readerTransactionManager(
            @Qualifier("readerEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}
```

**Usage in Repository:**
```java
@Repository
public interface UserReadRepository extends JpaRepository<User, Long> {
    // Read operations automatically use reader endpoint
}

@Repository
public interface UserWriteRepository extends JpaRepository<User, Long> {
    // Write operations use writer endpoint
}
```

## SSL/TLS Configuration

Enable SSL for secure connections to Aurora:

**Aurora MySQL with SSL:**
```properties
spring.datasource.url=jdbc:mysql://myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:3306/devops?useSSL=true&requireSSL=true&verifyServerCertificate=true
```

**Aurora PostgreSQL with SSL:**
```properties
spring.datasource.url=jdbc:postgresql://myapp-aurora-pg-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:5432/devops?ssl=true&sslmode=require
```

**Download RDS Certificate:**
```bash
# Download RDS CA certificate
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem

# Configure in application
spring.datasource.url=jdbc:mysql://...?useSSL=true&trustCertificateKeyStoreUrl=file:///path/to/global-bundle.pem
```

## AWS Secrets Manager Integration

**Add AWS SDK Dependency:**
```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>secretsmanager</artifactId>
    <version>2.20.0</version>
</dependency>
```

**Secrets Manager Configuration:**
```java
@Configuration
public class AuroraDataSourceConfig {

    @Value("${aws.secretsmanager.secret-name}")
    private String secretName;

    @Value("${aws.region}")
    private String region;

    @Bean
    public DataSource dataSource() {
        Map<String, String> credentials = getAuroraCredentials();

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(credentials.get("url"));
        config.setUsername(credentials.get("username"));
        config.setPassword(credentials.get("password"));
        config.setMaximumPoolSize(20);
        config.setMinimumIdle(5);
        config.setConnectionTimeout(20000);

        return new HikariDataSource(config);
    }

    private Map<String, String> getAuroraCredentials() {
        SecretsManagerClient client = SecretsManagerClient.builder()
            .region(Region.of(region))
            .build();

        GetSecretValueRequest request = GetSecretValueRequest.builder()
            .secretId(secretName)
            .build();

        GetSecretValueResponse response = client.getSecretValue(request);
        String secretString = response.secretString();

        // Parse JSON secret
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(secretString, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse secret", e);
        }
    }
}
```

**application.properties (Secrets Manager):**
```properties
aws.secretsmanager.secret-name=prod/aurora/credentials
aws.region=us-east-1
```

## Database Migration with Flyway

### Setup Flyway

**Create Migration Directory:**
```
src/main/resources/db/migration/
├── V1__create_users_table.sql
├── V2__add_phone_column.sql
└── V3__create_orders_table.sql
```

**V1__create_users_table.sql:**
```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**V2__add_phone_column.sql:**
```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

**Flyway Configuration:**
```properties
spring.jpa.hibernate.ddl-auto=validate
spring.flyway.enabled=true
spring.flyway.baseline-on-migrate=true
spring.flyway.locations=classpath:db/migration
spring.flyway.validate-on-migrate=true
```

## Connection Pool Optimization for Aurora

**Recommended HikariCP Settings:**
```properties
# Aurora-optimized connection pool
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=20000
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.max-lifetime=1200000
spring.datasource.hikari.leak-detection-threshold=60000
spring.datasource.hikari.connection-test-query=SELECT 1
```

**Formula for Pool Size:**
```
connections = ((core_count * 2) + effective_spindle_count)
For Aurora: Use 20-30 connections per application instance
```

## Failover Handling

Aurora automatically handles failover between instances. Configure connection retry:

```properties
# Connection retry configuration
spring.datasource.hikari.connection-timeout=30000
spring.datasource.url=jdbc:mysql://cluster-endpoint:3306/db?failOverReadOnly=false&maxReconnects=3&connectTimeout=30000
```

## Read Replica Load Balancing

Use reader endpoint for distributing read traffic across replicas:

```properties
# Reader endpoint for read-heavy workloads
spring.datasource.reader.url=jdbc:mysql://cluster-ro-endpoint:3306/db
```

## Performance Optimization

**Enable batch operations:**
```properties
spring.jpa.properties.hibernate.jdbc.batch_size=20
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
spring.jpa.properties.hibernate.batch_versioned_data=true
```

**Disable open-in-view pattern:**
```properties
spring.jpa.open-in-view=false
```

**Production logging configuration:**
```properties
# Disable SQL logging in production
logging.level.org.hibernate.SQL=WARN
logging.level.org.springframework.jdbc=WARN

# Enable HikariCP metrics
logging.level.com.zaxxer.hikari=INFO
logging.level.com.zaxxer.hikari.pool=DEBUG
```

**Enable Spring Boot Actuator for metrics:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```properties
management.endpoints.web.exposure.include=health,metrics,info
management.endpoint.health.show-details=always
```