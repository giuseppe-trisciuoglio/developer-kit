---
name: aws-rds-aurora-spring-data-jpa-configuration
description: Focused guide for configuring AWS RDS Aurora (MySQL/PostgreSQL) with Spring Data JPA. Use when setting up Aurora database connections, configuring datasources, connection pooling, and production-ready settings.
category: aws
tags: [aws, rds, aurora, spring-boot, spring-data-jpa, datasource, configuration, hikari]
version: 2.0.0
allowed-tools: Read, Write, Bash
---

# AWS RDS Aurora Spring Data JPA Configuration

Comprehensive guide for configuring AWS RDS Aurora instances with Spring Data JPA, focusing on connection setup, pooling, security, and production-ready settings.

## When to Use This Skill

Use this skill when:
- Configuring Spring Data JPA with AWS RDS Aurora (MySQL/PostgreSQL)
- Setting up datasource properties for Aurora endpoints
- Configuring HikariCP connection pooling for Aurora
- Implementing environment-specific configurations (dev/prod)
- Setting up SSL connections to Aurora
- Troubleshooting Aurora connection issues
- Configuring security groups for Aurora access
- Managing credentials with AWS Secrets Manager
- Optimizing connection pool settings for Aurora clusters

## Prerequisites

Before configuring Spring Data JPA with AWS RDS Aurora:
1. AWS account with RDS access
2. Spring Boot project (2.7+ or 3.x)
3. Aurora cluster created and running (MySQL or PostgreSQL compatible)
4. Security group configured for database access
5. Database endpoint information available

## AWS RDS Aurora Configuration

### Step 1: Aurora Cluster Setup

#### 1.1 Create Security Group

**Navigate to AWS Console:**
- Go to **EC2 Dashboard** > **Security Groups** > **Create Security Group**

**Inbound Rules for Aurora MySQL:**
```
Type: MYSQL/Aurora (port 3306)
Source: My IP (for development) or specific CIDR block
Description: Allow Aurora MySQL access from application
```

**Inbound Rules for Aurora PostgreSQL:**
```
Type: PostgreSQL (port 5432)
Source: My IP (for development) or specific CIDR block
Description: Allow Aurora PostgreSQL access from application
```

**Outbound Rules:**
```
Type: All traffic
Destination: 0.0.0.0/0
Description: Allow outbound connections
```

**Example Security Group (via AWS CLI):**
```bash
# Create security group
aws ec2 create-security-group \
  --group-name aurora-rds-sg \
  --description "Security group for Aurora MySQL/PostgreSQL access"

# Add inbound rule for Aurora MySQL
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 3306 \
  --cidr YOUR_IP/32

# Add inbound rule for Aurora PostgreSQL
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 5432 \
  --cidr YOUR_IP/32
```

#### 1.2 Create Aurora Cluster

**AWS Console Steps:**
1. Navigate to **RDS Dashboard** > **Create Database**
2. **Choose Database Creation Method**: Standard Create
3. **Engine Type**: Amazon Aurora
4. **Engine Version**: 
   - Aurora (MySQL Compatible) - 8.0.mysql_aurora.3.x
   - Aurora (PostgreSQL Compatible) - 15.x
5. **Templates**: Production, Dev/Test, or Serverless (v2)
6. **DB Cluster Identifier**: `myapp-aurora-cluster`
7. **Master Username**: `admin`
8. **Master Password**: Set a strong password
9. **DB Instance Class**:
   - Serverless v2: Configure ACU (0.5 - 128)
   - Provisioned: `db.r6g.large` or `db.t3.medium`
10. **Multi-AZ Deployment**: Yes (for production high availability)
11. **VPC Security Group**: Select the security group created in Step 1.1
12. **Additional Configuration**:
    - Initial database name: `devops` or your app name
    - DB cluster parameter group: default.aurora-mysql8.0 or default.aurora-postgresql15
    - Backup retention: 7-35 days (production)
    - Enable encryption (recommended)
    - Enable CloudWatch logs: Error, Slow Query, General (MySQL) or PostgreSQL log
    - Enable Enhanced Monitoring (recommended)

**Aurora Cluster via AWS CLI (MySQL Compatible):**
```bash
# Create Aurora MySQL cluster
aws rds create-db-cluster \
  --db-cluster-identifier myapp-aurora-cluster \
  --engine aurora-mysql \
  --engine-version 8.0.mysql_aurora.3.04.0 \
  --master-username admin \
  --master-user-password YourStrongPassword123! \
  --database-name devops \
  --vpc-security-group-ids sg-xxxxx \
  --backup-retention-period 7 \
  --storage-encrypted \
  --enable-cloudwatch-logs-exports '["error","general","slowquery"]'

# Create Aurora MySQL instance
aws rds create-db-instance \
  --db-instance-identifier myapp-aurora-instance-1 \
  --db-instance-class db.r6g.large \
  --engine aurora-mysql \
  --db-cluster-identifier myapp-aurora-cluster \
  --publicly-accessible false
```

**Aurora Serverless v2 (MySQL):**
```bash
# Create Aurora Serverless v2 cluster
aws rds create-db-cluster \
  --db-cluster-identifier myapp-aurora-serverless \
  --engine aurora-mysql \
  --engine-version 8.0.mysql_aurora.3.04.0 \
  --master-username admin \
  --master-user-password YourStrongPassword123! \
  --database-name devops \
  --vpc-security-group-ids sg-xxxxx \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16 \
  --storage-encrypted

# Create serverless instance
aws rds create-db-instance \
  --db-instance-identifier myapp-aurora-serverless-instance \
  --db-instance-class db.serverless \
  --engine aurora-mysql \
  --db-cluster-identifier myapp-aurora-serverless
```

**Aurora PostgreSQL Compatible:**
```bash
# Create Aurora PostgreSQL cluster
aws rds create-db-cluster \
  --db-cluster-identifier myapp-aurora-pg-cluster \
  --engine aurora-postgresql \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password YourStrongPassword123! \
  --database-name devops \
  --vpc-security-group-ids sg-xxxxx \
  --backup-retention-period 7 \
  --storage-encrypted

# Create Aurora PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier myapp-aurora-pg-instance-1 \
  --db-instance-class db.r6g.large \
  --engine aurora-postgresql \
  --db-cluster-identifier myapp-aurora-pg-cluster
```

#### 1.3 Get Aurora Cluster Endpoints

Aurora provides multiple endpoints for different use cases:

**Endpoint Types:**
1. **Cluster Endpoint (Writer)**: Primary instance for write operations
2. **Reader Endpoint**: Load-balanced across read replicas
3. **Instance Endpoints**: Direct connection to specific instances
4. **Custom Endpoints**: User-defined subset of instances

**AWS Console:**
- Go to **RDS** > **Databases** > Select your Aurora cluster
- Under **Connectivity & Security**, find:
  - **Cluster endpoint**: `myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com`
  - **Reader endpoint**: `myapp-aurora-cluster.cluster-ro-abc123xyz.us-east-1.rds.amazonaws.com`

**AWS CLI:**
```bash
# Get cluster endpoint (writer)
aws rds describe-db-clusters \
  --db-cluster-identifier myapp-aurora-cluster \
  --query 'DBClusters[0].Endpoint' \
  --output text

# Get reader endpoint
aws rds describe-db-clusters \
  --db-cluster-identifier myapp-aurora-cluster \
  --query 'DBClusters[0].ReaderEndpoint' \
  --output text
```

### Step 2: Spring Data JPA Dependencies

#### 2.1 Add Required Dependencies

**Maven (pom.xml):**
```xml
<dependencies>
    <!-- Spring Data JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- Aurora MySQL Driver -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <version>8.2.0</version>
        <scope>runtime</scope>
    </dependency>

    <!-- Aurora PostgreSQL Driver (alternative) -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Flyway for database migrations (recommended) -->
    <dependency>
        <groupId>org.flywaydb</groupId>
        <artifactId>flyway-core</artifactId>
    </dependency>
    
    <!-- Flyway MySQL support -->
    <dependency>
        <groupId>org.flywaydb</groupId>
        <artifactId>flyway-mysql</artifactId>
    </dependency>

    <!-- Validation -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
</dependencies>
```

**Gradle (build.gradle):**
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    
    // Aurora MySQL
    runtimeOnly 'com.mysql:mysql-connector-j:8.2.0'
    
    // Aurora PostgreSQL (alternative)
    runtimeOnly 'org.postgresql:postgresql'
    
    // Flyway
    implementation 'org.flywaydb:flyway-core'
    implementation 'org.flywaydb:flyway-mysql'
}
```

#### 2.2 Aurora Datasource Configuration

**application.properties (Aurora MySQL - Cluster Endpoint):**
```properties
# Application Name
spring.application.name=DevOps

# Aurora MySQL Datasource - Cluster Endpoint (Writer)
spring.datasource.url=jdbc:mysql://myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:3306/devops
spring.datasource.username=admin
spring.datasource.password=${DB_PASSWORD}
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA/Hibernate Configuration
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.open-in-view=false

# HikariCP Connection Pool Configuration (Optimized for Aurora)
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=20000
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.max-lifetime=1200000
spring.datasource.hikari.leak-detection-threshold=60000
spring.datasource.hikari.pool-name=AuroraHikariPool

# Flyway Configuration
spring.flyway.enabled=true
spring.flyway.baseline-on-migrate=true
spring.flyway.locations=classpath:db/migration
spring.flyway.validate-on-migrate=true

# Logging (Production)
logging.level.org.hibernate.SQL=WARN
logging.level.com.zaxxer.hikari=INFO
```

**application.properties (Aurora MySQL - Read/Write Split):**
```properties
# Aurora MySQL - Writer Endpoint
spring.datasource.writer.jdbc-url=jdbc:mysql://myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:3306/devops
spring.datasource.writer.username=admin
spring.datasource.writer.password=${DB_PASSWORD}
spring.datasource.writer.driver-class-name=com.mysql.cj.jdbc.Driver

# Aurora MySQL - Reader Endpoint (Read Replicas)
spring.datasource.reader.jdbc-url=jdbc:mysql://myapp-aurora-cluster.cluster-ro-abc123xyz.us-east-1.rds.amazonaws.com:3306/devops
spring.datasource.reader.username=admin
spring.datasource.reader.password=${DB_PASSWORD}
spring.datasource.reader.driver-class-name=com.mysql.cj.jdbc.Driver

# HikariCP for Writer
spring.datasource.writer.hikari.maximum-pool-size=15
spring.datasource.writer.hikari.minimum-idle=5

# HikariCP for Reader
spring.datasource.reader.hikari.maximum-pool-size=25
spring.datasource.reader.hikari.minimum-idle=10
```

**application.properties (Aurora PostgreSQL):**
```properties
# Application Name
spring.application.name=DevOps

# Aurora PostgreSQL Datasource
spring.datasource.url=jdbc:postgresql://myapp-aurora-pg-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:5432/devops
spring.datasource.username=admin
spring.datasource.password=${DB_PASSWORD}
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA/Hibernate Configuration
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.properties.hibernate.jdbc.lob.non_contextual_creation=true
spring.jpa.open-in-view=false

# HikariCP Connection Pool
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=20000
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.max-lifetime=1200000
```

**application.yml (Aurora MySQL):**
```yaml
spring:
  application:
    name: DevOps
  
  datasource:
    url: jdbc:mysql://myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:3306/devops
    username: admin
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
    
    hikari:
      pool-name: AuroraHikariPool
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 20000
      idle-timeout: 300000
      max-lifetime: 1200000
      leak-detection-threshold: 60000
      connection-test-query: SELECT 1
  
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    open-in-view: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect
        format_sql: true
        jdbc:
          batch_size: 20
        order_inserts: true
        order_updates: true
  
  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
    validate-on-migrate: true

logging:
  level:
    org.hibernate.SQL: WARN
    com.zaxxer.hikari: INFO
```

**application.yml (Aurora PostgreSQL):**
```yaml
spring:
  application:
    name: DevOps
  
  datasource:
    url: jdbc:postgresql://myapp-aurora-pg-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:5432/devops
    username: admin
    password: ${DB_PASSWORD}
    driver-class-name: org.postgresql.Driver
    
    hikari:
      pool-name: AuroraPgHikariPool
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 20000
      idle-timeout: 300000
      max-lifetime: 1200000
  
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    open-in-view: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
        jdbc:
          lob.non_contextual_creation: true
  
  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
```

### Step 3: Advanced Aurora Configuration

#### 3.1 Read/Write Split Configuration

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

#### 3.2 SSL/TLS Configuration

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

## Environment-Specific Configuration

### Development vs Production Profiles

**application-dev.properties (Local Development):**
```properties
# Local MySQL for development
spring.datasource.url=jdbc:mysql://localhost:3306/devops_dev
spring.datasource.username=root
spring.datasource.password=root

# Enable DDL auto-update in development
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

# Smaller connection pool for local dev
spring.datasource.hikari.maximum-pool-size=5
spring.datasource.hikari.minimum-idle=2
```

**application-prod.properties (Aurora Production):**
```properties
# Aurora Cluster Endpoint (Production)
spring.datasource.url=jdbc:mysql://${AURORA_ENDPOINT}:3306/${DB_NAME}
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}

# Validate schema only in production
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.open-in-view=false

# Production-optimized connection pool
spring.datasource.hikari.maximum-pool-size=30
spring.datasource.hikari.minimum-idle=10
spring.datasource.hikari.connection-timeout=20000
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.max-lifetime=1200000
spring.datasource.hikari.leak-detection-threshold=60000

# Enable Flyway migrations
spring.flyway.enabled=true
spring.flyway.validate-on-migrate=true
```

**Environment Variables Setup:**
```bash
# Production environment variables
export AURORA_ENDPOINT=myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com
export DB_NAME=devops
export DB_USERNAME=admin
export DB_PASSWORD=YourStrongPassword123!
export SPRING_PROFILES_ACTIVE=prod
```

### AWS Secrets Manager Integration

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

## Aurora-Specific Best Practices

### 1. Connection Pool Optimization for Aurora

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

### 2. Failover Handling

Aurora automatically handles failover between instances. Configure connection retry:

```properties
# Connection retry configuration
spring.datasource.hikari.connection-timeout=30000
spring.datasource.url=jdbc:mysql://cluster-endpoint:3306/db?failOverReadOnly=false&maxReconnects=3&connectTimeout=30000
```

### 3. Read Replica Load Balancing

Use reader endpoint for distributing read traffic across replicas:

```properties
# Reader endpoint for read-heavy workloads
spring.datasource.reader.url=jdbc:mysql://cluster-ro-endpoint:3306/db
```

### 4. Security Best Practices

**Never hardcode credentials:**
```properties
# BAD - Never do this
spring.datasource.password=MyPassword123!

# GOOD - Use environment variables
spring.datasource.password=${DB_PASSWORD}

# BETTER - Use AWS Secrets Manager
aws.secretsmanager.secret-name=prod/aurora/credentials
```

**Enable IAM Database Authentication:**
```properties
spring.datasource.url=jdbc:mysql://cluster-endpoint:3306/db?useAwsIam=true
```

### 5. SSL/TLS Configuration

**Enable SSL for secure communication:**
```properties
# Aurora MySQL SSL
spring.datasource.url=jdbc:mysql://cluster-endpoint:3306/db?useSSL=true&requireSSL=true

# Aurora PostgreSQL SSL
spring.datasource.url=jdbc:postgresql://cluster-endpoint:5432/db?ssl=true&sslmode=require
```

### 6. Performance Optimization

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

### 7. Monitoring and Logging

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

## Troubleshooting Aurora Connection Issues

### Common Issues and Solutions

#### 1. Connection Timeout to Aurora Cluster
**Error:** `Communications link failure` or `Connection timed out`

**Solutions:**
- Verify security group inbound rules allow traffic on port 3306 (MySQL) or 5432 (PostgreSQL)
- Check Aurora cluster endpoint is correct (cluster vs instance endpoint)
- Ensure your IP/CIDR is whitelisted in security group
- Verify VPC and subnet configuration
- Check if Aurora cluster is in the same VPC or VPC peering is configured

```bash
# Test connection from EC2/local machine
telnet myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com 3306
```

#### 2. Access Denied for User
**Error:** `Access denied for user 'admin'@'...'`

**Solutions:**
- Verify master username and password are correct
- Check if IAM authentication is required but not configured
- Reset master password in Aurora console if needed
- Verify user permissions in database

```sql
-- Check user permissions
SHOW GRANTS FOR 'admin'@'%';
```

#### 3. Database Not Found
**Error:** `Unknown database 'devops'`

**Solutions:**
- Verify initial database name was created with cluster
- Create database manually using MySQL/PostgreSQL client
- Check database name in JDBC URL matches existing database

```sql
-- Connect to Aurora and create database
CREATE DATABASE devops CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4. SSL Connection Issues
**Error:** `SSL connection error` or `Certificate validation failed`

**Solutions:**
```properties
# Option 1: Disable SSL verification (NOT recommended for production)
spring.datasource.url=jdbc:mysql://...?useSSL=false

# Option 2: Properly configure SSL with RDS certificate
spring.datasource.url=jdbc:mysql://...?useSSL=true&requireSSL=true&verifyServerCertificate=true&trustCertificateKeyStoreUrl=file:///path/to/global-bundle.pem

# Option 3: Trust all certificates (NOT recommended for production)
spring.datasource.url=jdbc:mysql://...?useSSL=true&requireSSL=true&verifyServerCertificate=false
```

#### 5. Too Many Connections
**Error:** `Too many connections` or `Connection pool exhausted`

**Solutions:**
- Review Aurora instance max_connections parameter
- Optimize HikariCP pool size
- Check for connection leaks in application code

```properties
# Reduce pool size
spring.datasource.hikari.maximum-pool-size=15
spring.datasource.hikari.minimum-idle=5

# Enable leak detection
spring.datasource.hikari.leak-detection-threshold=60000
```

**Check Aurora max_connections:**
```sql
SHOW VARIABLES LIKE 'max_connections';
-- Default for Aurora: depends on instance class
-- db.r6g.large: ~1000 connections
```

#### 6. Slow Query Performance
**Error:** Queries taking longer than expected

**Solutions:**
- Enable slow query log in Aurora parameter group
- Review connection pool settings
- Check Aurora instance metrics in CloudWatch
- Optimize queries and add indexes

```properties
# Enable query logging (development only)
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE
```

#### 7. Failover Delays
**Error:** Application freezes during Aurora failover

**Solutions:**
- Configure connection timeout appropriately
- Use cluster endpoint (not instance endpoint)
- Implement connection retry logic

```properties
spring.datasource.hikari.connection-timeout=20000
spring.datasource.hikari.validation-timeout=5000
spring.datasource.url=jdbc:mysql://...?failOverReadOnly=false&maxReconnects=3
```

## Testing Aurora Connection

### Connection Test with Spring Boot Application

**Create a Simple Test Endpoint:**
```java
@RestController
@RequestMapping("/api/health")
public class DatabaseHealthController {
    
    @Autowired
    private DataSource dataSource;
    
    @GetMapping("/db-connection")
    public ResponseEntity<Map<String, Object>> testDatabaseConnection() {
        Map<String, Object> response = new HashMap<>();
        
        try (Connection connection = dataSource.getConnection()) {
            response.put("status", "success");
            response.put("database", connection.getCatalog());
            response.put("url", connection.getMetaData().getURL());
            response.put("connected", true);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("status", "failed");
            response.put("error", e.getMessage());
            response.put("connected", false);
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(response);
        }
    }
}
```

**Test with cURL:**
```bash
curl http://localhost:8080/api/health/db-connection
```

### Verify Aurora Connection with MySQL/PostgreSQL Client

**MySQL Client Connection:**
```bash
# Connect to Aurora MySQL cluster
mysql -h myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com \
      -P 3306 \
      -u admin \
      -p devops

# Verify connection
SHOW DATABASES;
SELECT @@version;
SHOW VARIABLES LIKE 'aurora_version';
```

**PostgreSQL Client Connection:**
```bash
# Connect to Aurora PostgreSQL
psql -h myapp-aurora-pg-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com \
     -p 5432 \
     -U admin \
     -d devops

# Verify connection
\l
SELECT version();
```

## Summary

This AWS RDS Aurora Spring Data JPA configuration skill covers:

1. **Aurora Cluster Setup**: Security groups, cluster creation, endpoint types (cluster, reader, instance)
2. **Spring Data JPA Configuration**: Dependencies, datasource properties optimized for Aurora
3. **HikariCP Connection Pooling**: Production-ready pool settings for Aurora workloads
4. **Read/Write Split**: Multi-datasource configuration for read replica load balancing
5. **SSL/TLS Security**: Secure connections to Aurora with certificate validation
6. **Environment Configuration**: Development vs production profiles with environment variables
7. **AWS Secrets Manager**: Secure credential management without hardcoding
8. **Performance Optimization**: Batch operations, connection pooling, failover handling
9. **Monitoring**: Logging, metrics, and health checks for Aurora connections
10. **Troubleshooting**: Common Aurora connection issues and solutions
11. **Testing**: Connection validation endpoints and database client verification

**Key Aurora Features:**
- **Cluster Endpoint**: Write operations (primary instance)
- **Reader Endpoint**: Read operations (load-balanced across replicas)
- **Automatic Failover**: Built-in high availability with minimal downtime
- **Serverless v2**: Auto-scaling capacity based on workload
- **Multi-AZ**: Cross-availability zone replication for disaster recovery

All patterns follow Spring Boot best practices and AWS Aurora recommendations for production-ready, high-availability applications.
