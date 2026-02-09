# AWS RDS Aurora Troubleshooting Guide

## Common Issues and Solutions

### Connection Timeout to Aurora Cluster
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

### Access Denied for User
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

### Database Not Found
**Error:** `Unknown database 'devops'`

**Solutions:**
- Verify initial database name was created with cluster
- Create database manually using MySQL/PostgreSQL client
- Check database name in JDBC URL matches existing database

```sql
-- Connect to Aurora and create database
CREATE DATABASE devops CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### SSL Connection Issues
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

### Too Many Connections
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

### Slow Query Performance
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

### Failover Delays
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