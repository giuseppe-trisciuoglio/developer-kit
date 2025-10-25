# Spring Boot Actuator Reference

## Predefined Endpoints

### Core Endpoints

#### `/actuator/health`

**Purpose**: Reports application health status

**HTTP Method**: GET

**Response Codes**:
- 200 (UP) - Application is healthy
- 503 (DOWN/OUT_OF_SERVICE) - Application is unhealthy
- 500 (custom statuses) - Based on configuration

**Response Structure**:
```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "validationQuery": "isValid()"
      }
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 251658240000,
        "free": 170198240000,
        "threshold": 10485760
      }
    }
  }
}
```

**Configuration Options**:
```yaml
management:
  endpoint:
    health:
      show-details: always | never | when-authorized
      show-components: always | never | when-authorized
      roles: "ADMIN,MONITOR"
      status:
        order: "down,out-of-service,up,unknown"
        http-mapping:
          down: 503
          out-of-service: 503
      group:
        <groupname>:
          include: "db,diskSpace"
          exclude: "ping"
          show-details: always
```

#### `/actuator/info`

**Purpose**: Displays application information

**HTTP Method**: GET

**Response Example**:
```json
{
  "app": {
    "name": "My Application",
    "description": "Application description",
    "version": "1.0.0"
  },
  "git": {
    "branch": "main",
    "commit": {
      "id": "abc1234",
      "time": "2024-01-15T10:30:00Z"
    }
  },
  "build": {
    "version": "1.0.0",
    "artifact": "my-app",
    "name": "my-app",
    "time": "2024-01-15T09:00:00Z"
  }
}
```

**Configuration**:
```yaml
management:
  info:
    env:
      enabled: true
    git:
      mode: full | simple
      enabled: true
    build:
      enabled: true
```

#### `/actuator/metrics`

**Purpose**: Lists available metrics

**HTTP Method**: GET

**Response Example**:
```json
{
  "names": [
    "jvm.memory.used",
    "jvm.memory.max",
    "jvm.gc.pause",
    "system.cpu.usage",
    "http.server.requests"
  ]
}
```

#### `/actuator/metrics/{metricName}`

**Purpose**: Displays specific metric details

**HTTP Method**: GET

**Query Parameters**:
- `tag=KEY:VALUE` - Filter by tag (can be repeated)

**Response Example**:
```json
{
  "name": "jvm.memory.used",
  "description": "The amount of used memory",
  "baseUnit": "bytes",
  "measurements": [
    {
      "statistic": "VALUE",
      "value": 123456789
    }
  ],
  "availableTags": [
    {
      "tag": "area",
      "values": ["heap", "nonheap"]
    },
    {
      "tag": "id",
      "values": ["PS Eden Space", "PS Old Gen"]
    }
  ]
}
```

#### `/actuator/env`

**Purpose**: Displays environment properties

**HTTP Method**: GET

**Configuration**:
```yaml
management:
  endpoint:
    env:
      show-values: always | never | when-authorized
      roles: "ADMIN"
```

**Response Example**:
```json
{
  "activeProfiles": ["production"],
  "propertySources": [
    {
      "name": "systemProperties",
      "properties": {
        "java.version": {
          "value": "17.0.1"
        }
      }
    },
    {
      "name": "applicationConfig",
      "properties": {
        "server.port": {
          "value": "8080"
        }
      }
    }
  ]
}
```

#### `/actuator/beans`

**Purpose**: Lists all Spring beans

**HTTP Method**: GET

**Response Structure**:
```json
{
  "contexts": {
    "application": {
      "beans": {
        "userService": {
          "aliases": [],
          "scope": "singleton",
          "type": "com.example.service.UserService",
          "resource": "file [UserService.class]",
          "dependencies": ["userRepository", "passwordEncoder"]
        }
      }
    }
  }
}
```

#### `/actuator/conditions`

**Purpose**: Shows auto-configuration report

**HTTP Method**: GET

**Response Sections**:
- `positiveMatches` - Conditions that matched
- `negativeMatches` - Conditions that didn't match
- `unconditionalClasses` - Classes without conditions

#### `/actuator/configprops`

**Purpose**: Displays @ConfigurationProperties beans

**HTTP Method**: GET

**Configuration**:
```yaml
management:
  endpoint:
    configprops:
      show-values: always | never | when-authorized
```

#### `/actuator/threaddump`

**Purpose**: Performs thread dump

**HTTP Method**: GET

**Response Example**:
```json
{
  "threads": [
    {
      "threadName": "main",
      "threadId": 1,
      "blockedTime": -1,
      "blockedCount": 0,
      "waitedTime": -1,
      "waitedCount": 0,
      "lockName": null,
      "lockOwnerId": -1,
      "lockOwnerName": null,
      "inNative": false,
      "suspended": false,
      "threadState": "RUNNABLE",
      "stackTrace": [...]
    }
  ]
}
```

#### `/actuator/heapdump`

**Purpose**: Downloads heap dump file

**HTTP Method**: GET

**Response**: Binary file (application/octet-stream)

**Note**: Can be large, use with caution in production

#### `/actuator/prometheus`

**Purpose**: Exports metrics in Prometheus format

**HTTP Method**: GET

**Accept Headers**:
- `application/openmetrics-text;version=1.0.0`
- `text/plain;version=0.0.4` (default)

**Query Parameters**:
- `includedNames` - Comma-separated metric names to include

**Response Example**:
```text
# HELP jvm_memory_used_bytes The amount of used memory
# TYPE jvm_memory_used_bytes gauge
jvm_memory_used_bytes{area="heap",id="PS Eden Space",} 1.23456789E8
jvm_memory_used_bytes{area="heap",id="PS Old Gen",} 5.4321098E7
```

#### `/actuator/loggers`

**Purpose**: View and modify logging levels

**HTTP Methods**: GET, POST

**GET Response**:
```json
{
  "levels": ["OFF", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"],
  "loggers": {
    "ROOT": {
      "configuredLevel": "INFO",
      "effectiveLevel": "INFO"
    },
    "com.example": {
      "configuredLevel": "DEBUG",
      "effectiveLevel": "DEBUG"
    }
  }
}
```

**POST Request** (change log level):
```bash
curl -X POST http://localhost:8080/actuator/loggers/com.example \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel": "DEBUG"}'
```

#### `/actuator/scheduledtasks`

**Purpose**: Lists scheduled tasks

**HTTP Method**: GET

**Response Example**:
```json
{
  "cron": [
    {
      "runnable": {
        "target": "com.example.tasks.CleanupTask.execute"
      },
      "expression": "0 0 2 * * ?",
      "nextExecution": {
        "time": "2024-01-16T02:00:00Z"
      }
    }
  ],
  "fixedDelay": [
    {
      "runnable": {
        "target": "com.example.tasks.SyncTask"
      },
      "initialDelay": 0,
      "interval": 60000,
      "lastExecution": {
        "time": "2024-01-15T10:30:00Z",
        "status": "SUCCESS"
      },
      "nextExecution": {
        "time": "2024-01-15T10:31:00Z"
      }
    }
  ],
  "fixedRate": []
}
```

#### `/actuator/sessions`

**Purpose**: Lists HTTP sessions (requires Spring Session)

**HTTP Methods**: GET, DELETE

**GET Response**:
```json
{
  "sessions": [
    {
      "id": "4db5efcc-96cb-4d05-a52c-80db3e77a301",
      "attributeNames": ["SPRING_SECURITY_CONTEXT"],
      "creationTime": "2024-01-15T10:00:00Z",
      "lastAccessedTime": "2024-01-15T10:30:00Z",
      "maxInactiveInterval": 1800,
      "expired": false
    }
  ]
}
```

**DELETE Request** (invalidate session):
```bash
curl -X DELETE http://localhost:8080/actuator/sessions/4db5efcc-96cb-4d05-a52c-80db3e77a301
```

#### `/actuator/startup`

**Purpose**: Shows application startup information

**HTTP Method**: POST

**Note**: Clears buffer after each invocation

**Response Example**:
```json
{
  "springBootVersion": "3.2.0",
  "timeline": {
    "startTime": "2024-01-15T10:00:00.000Z",
    "events": [
      {
        "startTime": "2024-01-15T10:00:00.100Z",
        "endTime": "2024-01-15T10:00:00.150Z",
        "duration": "PT0.05S",
        "startupStep": {
          "name": "spring.boot.application.starting",
          "id": 0,
          "tags": [
            {
              "key": "mainApplicationClass",
              "value": "com.example.Application"
            }
          ]
        }
      }
    ]
  }
}
```

#### `/actuator/shutdown`

**Purpose**: Gracefully shuts down the application

**HTTP Method**: POST

**Configuration** (disabled by default):
```yaml
management:
  endpoint:
    shutdown:
      enabled: true
```

**Response**:
```json
{
  "message": "Shutting down, bye..."
}
```

### Specialized Endpoints

#### `/actuator/flyway`

**Purpose**: Shows Flyway migration information

**HTTP Method**: GET

**Requires**: Flyway dependency

**Response Example**:
```json
{
  "contexts": {
    "application": {
      "flywayBeans": {
        "flyway": {
          "migrations": [
            {
              "type": "SQL",
              "checksum": 12345,
              "version": "1",
              "description": "Initial schema",
              "script": "V1__Initial_schema.sql",
              "state": "SUCCESS",
              "installedOn": "2024-01-15T09:00:00Z",
              "executionTime": 250
            }
          ]
        }
      }
    }
  }
}
```

#### `/actuator/liquibase`

**Purpose**: Shows Liquibase changelog information

**HTTP Method**: GET

**Requires**: Liquibase dependency

#### `/actuator/caches`

**Purpose**: Lists available caches

**HTTP Methods**: GET, DELETE

**Response Example**:
```json
{
  "cacheManagers": {
    "cacheManager": {
      "caches": {
        "users": {
          "target": "org.springframework.cache.concurrent.ConcurrentMapCache"
        },
        "products": {
          "target": "org.springframework.cache.concurrent.ConcurrentMapCache"
        }
      }
    }
  }
}
```

**DELETE Request** (clear cache):
```bash
curl -X DELETE http://localhost:8080/actuator/caches/users
```

## Health Indicator Details

### Built-in Health Indicators

| Indicator | Auto-configured When | Purpose |
|-----------|---------------------|---------|
| DiskSpaceHealthIndicator | Always | Disk space monitoring |
| PingHealthIndicator | Always | Basic application availability |
| DataSourceHealthIndicator | DataSource bean exists | Database connectivity |
| MongoHealthIndicator | MongoDB client exists | MongoDB connectivity |
| RedisHealthIndicator | Redis connection factory exists | Redis connectivity |
| CassandraHealthIndicator | Cassandra session exists | Cassandra connectivity |
| ElasticsearchHealthIndicator | Elasticsearch client exists | Elasticsearch connectivity |
| RabbitHealthIndicator | RabbitMQ connection factory exists | RabbitMQ connectivity |
| SolrHealthIndicator | Solr client exists | Solr connectivity |
| MailHealthIndicator | JavaMailSender exists | Mail server connectivity |

### Health Status Hierarchy

Default ordering (highest to lowest severity):
1. DOWN
2. OUT_OF_SERVICE
3. UP
4. UNKNOWN

Custom statuses can be added and ordered:
```yaml
management:
  endpoint:
    health:
      status:
        order: "fatal,down,out-of-service,warning,unknown,up"
```

### Health Status HTTP Mapping

Default mappings:
- DOWN → 503
- OUT_OF_SERVICE → 503
- UP → 200
- UNKNOWN → 200
- Custom statuses → 200 (unless explicitly mapped)

## Metrics Details

### JVM Metrics

| Metric | Description |
|--------|-------------|
| jvm.memory.used | Memory currently in use |
| jvm.memory.max | Maximum available memory |
| jvm.memory.committed | Memory committed for JVM |
| jvm.gc.pause | GC pause times |
| jvm.gc.memory.allocated | Memory allocated after last GC |
| jvm.gc.memory.promoted | Memory promoted to old generation |
| jvm.threads.live | Current number of live threads |
| jvm.threads.daemon | Current number of daemon threads |
| jvm.threads.peak | Peak number of threads |
| jvm.threads.states | Thread states distribution |
| jvm.classes.loaded | Current classes loaded |
| jvm.classes.unloaded | Total classes unloaded |
| jvm.buffer.count | Buffer pool count |
| jvm.buffer.memory.used | Buffer pool memory used |

### System Metrics

| Metric | Description |
|--------|-------------|
| system.cpu.count | Number of processors |
| system.cpu.usage | System CPU usage |
| system.load.average.1m | System load average |
| process.cpu.usage | Process CPU usage |
| process.start.time | Process start time |
| process.uptime | Process uptime |
| process.files.open | Open file descriptors |
| process.files.max | Max file descriptors |

### HTTP Metrics

| Metric | Description |
|--------|-------------|
| http.server.requests | HTTP request metrics (count, duration) |

Available tags:
- `method` - HTTP method (GET, POST, etc.)
- `uri` - URI pattern
- `status` - HTTP status code
- `outcome` - Request outcome (SUCCESS, CLIENT_ERROR, SERVER_ERROR)
- `exception` - Exception class (if thrown)

### Database Metrics (JDBC)

| Metric | Description |
|--------|-------------|
| jdbc.connections.active | Active connections |
| jdbc.connections.idle | Idle connections |
| jdbc.connections.min | Minimum connections |
| jdbc.connections.max | Maximum connections |

### Tomcat Metrics

| Metric | Description |
|--------|-------------|
| tomcat.sessions.created | Sessions created |
| tomcat.sessions.active.current | Current active sessions |
| tomcat.sessions.active.max | Max active sessions |
| tomcat.sessions.expired | Expired sessions |
| tomcat.sessions.rejected | Rejected sessions |
| tomcat.threads.busy | Busy threads |
| tomcat.threads.current | Current threads |
| tomcat.threads.config.max | Max threads configured |

### Custom Meter Types

#### Counter
Monotonically increasing value:
```java
Counter.builder("orders.created")
    .description("Total orders created")
    .tag("type", "online")
    .register(registry);
```

#### Gauge
Current value that can go up or down:
```java
Gauge.builder("queue.size", queue, Queue::size)
    .description("Queue size")
    .register(registry);
```

#### Timer
Duration of events:
```java
Timer.builder("order.processing")
    .description("Order processing time")
    .publishPercentiles(0.5, 0.95, 0.99)
    .register(registry);
```

#### DistributionSummary
Distribution of values:
```java
DistributionSummary.builder("order.amount")
    .description("Order amounts")
    .baseUnit("EUR")
    .publishPercentiles(0.5, 0.95, 0.99)
    .register(registry);
```

#### LongTaskTimer
Long-running task duration:
```java
LongTaskTimer.builder("batch.job")
    .description("Batch job execution")
    .register(registry);
```

## Configuration Properties Reference

### Endpoint Exposure

```yaml
management:
  endpoints:
    # Enable/disable all endpoints
    enabled-by-default: true
    
    # JMX exposure
    jmx:
      exposure:
        include: "*"
        exclude: "shutdown"
    
    # Web (HTTP) exposure
    web:
      exposure:
        include: "health,info"
        exclude: "env,beans"
      base-path: "/actuator"
      path-mapping:
        health: "healthcheck"
      cors:
        allowed-origins: "https://example.com"
        allowed-methods: "GET,POST"
```

### Endpoint Configuration

```yaml
management:
  endpoint:
    # Individual endpoint settings
    health:
      enabled: true
      show-details: when-authorized
      show-components: always
      roles: "ADMIN"
      cache:
        time-to-live: "10s"
    
    info:
      enabled: true
      cache:
        time-to-live: "5s"
    
    shutdown:
      enabled: false  # Disabled by default
```

### Server Configuration

```yaml
management:
  server:
    # Run on different port
    port: 8081
    
    # SSL configuration
    ssl:
      enabled: true
      key-store: classpath:keystore.p12
      key-store-password: secret
    
    # Address binding
    address: 127.0.0.1
```

### Metrics Configuration

```yaml
management:
  metrics:
    # Enable/disable metrics
    enable:
      jvm: true
      process: true
      system: true
      tomcat: true
      logback: true
    
    # Common tags for all metrics
    tags:
      application: ${spring.application.name}
      environment: production
      region: eu-west-1
    
    # Distribution statistics
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5, 0.95, 0.99
      slo:
        http.server.requests: 50ms, 100ms, 200ms
    
    # Export configuration
    export:
      prometheus:
        enabled: true
        step: 1m
        descriptions: true
      
      datadog:
        enabled: false
        api-key: ${DATADOG_API_KEY}
        uri: https://api.datadoghq.eu
        step: 30s
      
      graphite:
        enabled: false
        host: localhost
        port: 2004
      
      influx:
        enabled: false
        uri: http://localhost:8086
        db: mydb
```

### Info Configuration

```yaml
management:
  info:
    # Environment info
    env:
      enabled: true
    
    # Git info
    git:
      mode: full  # or "simple"
      enabled: true
    
    # Build info
    build:
      enabled: true
    
    # Java info
    java:
      enabled: true
    
    # OS info
    os:
      enabled: true
```

## Security Best Practices

1. **Separate Management Port**: Use different port for actuator endpoints
   ```yaml
   management:
     server:
       port: 8081
   ```

2. **Minimal Exposure**: Only expose needed endpoints
   ```yaml
   management:
     endpoints:
       web:
         exposure:
           include: "health,info,metrics"
   ```

3. **Authentication Required**: Secure all endpoints except health
   ```java
   http.authorizeHttpRequests(auth -> auth
       .requestMatchers("/actuator/health").permitAll()
       .requestMatchers("/actuator/**").hasRole("ADMIN")
   );
   ```

4. **Sanitize Sensitive Data**: Hide sensitive values
   ```yaml
   management:
     endpoint:
       env:
         show-values: never
       configprops:
         show-values: when-authorized
   ```

5. **Disable Write Operations**: In production, disable destructive endpoints
   ```yaml
   management:
     endpoint:
       shutdown:
         enabled: false
   ```

6. **Use HTTPS**: Enable SSL for management port
   ```yaml
   management:
     server:
       ssl:
         enabled: true
   ```

7. **IP Restrictions**: Limit access to specific IPs
8. **Role-Based Access**: Use fine-grained role permissions
9. **Audit Logging**: Log access to sensitive endpoints
10. **Regular Review**: Periodically review exposed endpoints

## Common Patterns

### Production Configuration

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"
  endpoint:
    health:
      show-details: never
      probes:
        enabled: true
  server:
    port: 8081
  metrics:
    export:
      prometheus:
        enabled: true
```

### Development Configuration

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
```

### Kubernetes Configuration

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        liveness:
          include: "livenessState"
        readiness:
          include: "readinessState,db,redis"
```
