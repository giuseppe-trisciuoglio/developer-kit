# JMX with Spring Boot Actuator

Java Management Extensions (JMX) provide a standard mechanism to monitor and manage applications. By default, this feature is not enabled. You can turn it on by setting the `spring.jmx.enabled` configuration property to `true`. Spring Boot exposes the most suitable `MBeanServer` as a bean with an ID of `mbeanServer`. Any of your beans that are annotated with Spring JMX annotations (`@ManagedResource`, `@ManagedAttribute`, or `@ManagedOperation`) are exposed to it.

If your platform provides a standard `MBeanServer`, Spring Boot uses that and defaults to the VM `MBeanServer`, if necessary. If all that fails, a new `MBeanServer` is created.

> **NOTE**
> 
> `spring.jmx.enabled` affects only the management beans provided by Spring. Enabling management beans provided by other libraries (for example Log4j2 or Quartz) is independent.

## Basic JMX Configuration

### Enabling JMX

```yaml
spring:
  jmx:
    enabled: true
    default-domain: com.example.myapp

management:
  endpoints:
    jmx:
      exposure:
        include: "*"
  endpoint:
    jmx:
      enabled: true
```

### Custom MBean Server Configuration

```java
@Configuration
public class JmxConfiguration {

    @Bean
    @Primary
    public MBeanServer mbeanServer() {
        MBeanServer server = ManagementFactory.getPlatformMBeanServer();
        return server;
    }

    @Bean
    public JmxMetricsExporter jmxMetricsExporter(MeterRegistry meterRegistry) {
        return new JmxMetricsExporter(meterRegistry);
    }
}
```

## Creating Custom MBeans

### Using @ManagedResource Annotation

```java
@Component
@ManagedResource(
    objectName = "com.example:type=ApplicationMetrics,name=UserService",
    description = "User Service Management Bean"
)
public class UserServiceMBean {

    private final UserService userService;
    private long totalUsers = 0;
    private long activeUsers = 0;

    public UserServiceMBean(UserService userService) {
        this.userService = userService;
    }

    @ManagedAttribute(description = "Total number of users")
    public long getTotalUsers() {
        return userService.getTotalUserCount();
    }

    @ManagedAttribute(description = "Number of active users")
    public long getActiveUsers() {
        return userService.getActiveUserCount();
    }

    @ManagedAttribute(description = "Cache hit ratio")
    public double getCacheHitRatio() {
        return userService.getCacheHitRatio();
    }

    @ManagedOperation(description = "Clear user cache")
    public void clearCache() {
        userService.clearCache();
    }

    @ManagedOperation(description = "Refresh user statistics")
    public String refreshStatistics() {
        userService.refreshStatistics();
        return "Statistics refreshed at " + Instant.now();
    }

    @ManagedOperation(description = "Get user by ID")
    @ManagedOperationParameters({
        @ManagedOperationParameter(name = "userId", description = "User ID")
    })
    public String getUserInfo(Long userId) {
        User user = userService.findById(userId);
        return user != null ? user.toString() : "User not found";
    }
}
```

### Implementing MBean Interface

```java
public interface ApplicationConfigMBean {
    String getEnvironment();
    void setLogLevel(String loggerName, String level);
    boolean isMaintenanceMode();
    void setMaintenanceMode(boolean maintenanceMode);
    void reloadConfiguration();
    Map<String, String> getSystemProperties();
}

@Component
public class ApplicationConfig implements ApplicationConfigMBean {

    private final Environment environment;
    private final LoggingSystem loggingSystem;
    private boolean maintenanceMode = false;

    public ApplicationConfig(Environment environment, LoggingSystem loggingSystem) {
        this.environment = environment;
        this.loggingSystem = loggingSystem;
    }

    @Override
    public String getEnvironment() {
        return String.join(",", environment.getActiveProfiles());
    }

    @Override
    public void setLogLevel(String loggerName, String level) {
        LogLevel logLevel = level != null ? LogLevel.valueOf(level.toUpperCase()) : null;
        loggingSystem.setLogLevel(loggerName, logLevel);
    }

    @Override
    public boolean isMaintenanceMode() {
        return maintenanceMode;
    }

    @Override
    public void setMaintenanceMode(boolean maintenanceMode) {
        this.maintenanceMode = maintenanceMode;
        // Publish event or notify other components
    }

    @Override
    public void reloadConfiguration() {
        // Implement configuration reload logic
        // This could refresh @ConfigurationProperties beans
    }

    @Override
    public Map<String, String> getSystemProperties() {
        return System.getProperties().entrySet().stream()
            .collect(Collectors.toMap(
                e -> String.valueOf(e.getKey()),
                e -> String.valueOf(e.getValue())
            ));
    }

    @PostConstruct
    public void registerMBean() {
        try {
            MBeanServer server = ManagementFactory.getPlatformMBeanServer();
            ObjectName objectName = new ObjectName("com.example:type=ApplicationConfig");
            server.registerMBean(this, objectName);
        } catch (Exception e) {
            throw new RuntimeException("Failed to register MBean", e);
        }
    }
}
```

## Application Metrics via JMX

### Custom Metrics MBean

```java
@Component
@ManagedResource(
    objectName = "com.example:type=Performance,name=ApplicationMetrics",
    description = "Application Performance Metrics"
)
public class ApplicationMetricsMBean {

    private final MeterRegistry meterRegistry;
    private final Counter requestCounter;
    private final Timer responseTimer;
    private final Gauge activeConnections;

    public ApplicationMetricsMBean(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestCounter = Counter.builder("application.requests.total")
            .description("Total number of requests")
            .register(meterRegistry);
        this.responseTimer = Timer.builder("application.response.time")
            .description("Response time")
            .register(meterRegistry);
        this.activeConnections = Gauge.builder("application.connections.active")
            .description("Active connections")
            .register(meterRegistry, this, ApplicationMetricsMBean::getActiveConnectionsCount);
    }

    @ManagedAttribute(description = "Total requests processed")
    public long getTotalRequests() {
        return (long) requestCounter.count();
    }

    @ManagedAttribute(description = "Average response time in milliseconds")
    public double getAverageResponseTime() {
        return responseTimer.mean(TimeUnit.MILLISECONDS);
    }

    @ManagedAttribute(description = "95th percentile response time")
    public double getResponse95thPercentile() {
        return responseTimer.percentile(0.95, TimeUnit.MILLISECONDS);
    }

    @ManagedAttribute(description = "Current active connections")
    public long getActiveConnections() {
        return getActiveConnectionsCount();
    }

    @ManagedAttribute(description = "JVM memory usage percentage")
    public double getMemoryUsagePercentage() {
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        return (double) heapUsage.getUsed() / heapUsage.getMax() * 100;
    }

    @ManagedOperation(description = "Reset request counter")
    public void resetRequestCounter() {
        // Note: Micrometer counters cannot be reset, this would require custom implementation
        // or using a different metric type
    }

    private long getActiveConnectionsCount() {
        // Implementation to get actual active connections
        return 42; // Placeholder
    }
}
```

### Database Connection Pool MBean

```java
@Component
@ManagedResource(
    objectName = "com.example:type=Database,name=ConnectionPool",
    description = "Database Connection Pool Metrics"
)
public class DatabaseConnectionPoolMBean {

    private final DataSource dataSource;

    public DatabaseConnectionPoolMBean(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @ManagedAttribute(description = "Active connections")
    public int getActiveConnections() {
        if (dataSource instanceof HikariDataSource) {
            return ((HikariDataSource) dataSource).getHikariPoolMXBean().getActiveConnections();
        }
        return -1; // Not supported
    }

    @ManagedAttribute(description = "Idle connections")
    public int getIdleConnections() {
        if (dataSource instanceof HikariDataSource) {
            return ((HikariDataSource) dataSource).getHikariPoolMXBean().getIdleConnections();
        }
        return -1; // Not supported
    }

    @ManagedAttribute(description = "Total connections")
    public int getTotalConnections() {
        if (dataSource instanceof HikariDataSource) {
            return ((HikariDataSource) dataSource).getHikariPoolMXBean().getTotalConnections();
        }
        return -1; // Not supported
    }

    @ManagedAttribute(description = "Threads awaiting connection")
    public int getThreadsAwaitingConnection() {
        if (dataSource instanceof HikariDataSource) {
            return ((HikariDataSource) dataSource).getHikariPoolMXBean().getThreadsAwaitingConnection();
        }
        return -1; // Not supported
    }

    @ManagedOperation(description = "Suspend connection pool")
    public void suspendPool() {
        if (dataSource instanceof HikariDataSource) {
            ((HikariDataSource) dataSource).getHikariPoolMXBean().suspendPool();
        }
    }

    @ManagedOperation(description = "Resume connection pool")
    public void resumePool() {
        if (dataSource instanceof HikariDataSource) {
            ((HikariDataSource) dataSource).getHikariPoolMXBean().resumePool();
        }
    }
}
```

## Security and JMX

### Securing JMX Access

```yaml
spring:
  jmx:
    enabled: true

management:
  endpoints:
    jmx:
      exposure:
        include: "health,info,metrics"
        exclude: "env,configprops"  # Exclude sensitive endpoints

# JMX-specific security
com.sun.management.jmxremote.port: 9999
com.sun.management.jmxremote.authenticate: true
com.sun.management.jmxremote.ssl: false
com.sun.management.jmxremote.access.file: /path/to/jmxremote.access
com.sun.management.jmxremote.password.file: /path/to/jmxremote.password
```

### Custom JMX Security

```java
@Configuration
public class JmxSecurityConfiguration {

    @Bean
    public JMXConnectorServer jmxConnectorServer() throws Exception {
        JMXServiceURL url = new JMXServiceURL("service:jmx:rmi://localhost:9999");
        
        Map<String, Object> environment = new HashMap<>();
        environment.put(JMXConnectorServer.AUTHENTICATOR, new CustomJMXAuthenticator());
        
        JMXConnectorServer server = JMXConnectorServerFactory.newJMXConnectorServer(
            url, environment, ManagementFactory.getPlatformMBeanServer());
        
        server.start();
        return server;
    }

    private static class CustomJMXAuthenticator implements JMXAuthenticator {
        @Override
        public Subject authenticate(Object credentials) {
            if (!(credentials instanceof String[])) {
                throw new SecurityException("Credentials must be String[]");
            }
            
            String[] creds = (String[]) credentials;
            if (creds.length != 2) {
                throw new SecurityException("Credentials must contain username and password");
            }
            
            String username = creds[0];
            String password = creds[1];
            
            // Implement your authentication logic
            if ("admin".equals(username) && "password".equals(password)) {
                return new Subject();
            }
            
            throw new SecurityException("Authentication failed");
        }
    }
}
```

## Monitoring and Alerting with JMX

### Health Check MBean

```java
@Component
@ManagedResource(
    objectName = "com.example:type=Health,name=ApplicationHealth",
    description = "Application Health Monitoring"
)
public class ApplicationHealthMBean {

    private final HealthEndpoint healthEndpoint;
    private final List<String> healthIssues = new ArrayList<>();

    public ApplicationHealthMBean(HealthEndpoint healthEndpoint) {
        this.healthEndpoint = healthEndpoint;
    }

    @ManagedAttribute(description = "Overall application health status")
    public String getHealthStatus() {
        HealthComponent health = healthEndpoint.health();
        return health.getStatus().getCode();
    }

    @ManagedAttribute(description = "Detailed health information")
    public String getHealthDetails() {
        HealthComponent health = healthEndpoint.health();
        return health.toString();
    }

    @ManagedAttribute(description = "Database health status")
    public String getDatabaseHealth() {
        HealthComponent health = healthEndpoint.healthForPath("db");
        return health != null ? health.getStatus().getCode() : "UNKNOWN";
    }

    @ManagedAttribute(description = "Current health issues")
    public String[] getHealthIssues() {
        return healthIssues.toArray(new String[0]);
    }

    @ManagedOperation(description = "Refresh health status")
    public void refreshHealth() {
        HealthComponent health = healthEndpoint.health();
        healthIssues.clear();
        
        if (health instanceof CompositeHealthComponent) {
            CompositeHealthComponent composite = (CompositeHealthComponent) health;
            composite.getComponents().forEach((name, component) -> {
                if (!Status.UP.equals(component.getStatus())) {
                    healthIssues.add(name + ": " + component.getStatus().getCode());
                }
            });
        }
    }

    @PostConstruct
    public void init() {
        refreshHealth();
    }
}
```

### Notification MBean

```java
@Component
@ManagedResource(
    objectName = "com.example:type=Notifications,name=AlertManager",
    description = "Application Alert Management"
)
public class AlertManagerMBean extends NotificationBroadcasterSupport {

    private final AtomicLong sequenceNumber = new AtomicLong(0);
    private boolean alertsEnabled = true;

    @ManagedAttribute(description = "Are alerts enabled")
    public boolean isAlertsEnabled() {
        return alertsEnabled;
    }

    @ManagedAttribute(description = "Enable or disable alerts")
    public void setAlertsEnabled(boolean alertsEnabled) {
        this.alertsEnabled = alertsEnabled;
    }

    @ManagedOperation(description = "Send test alert")
    public void sendTestAlert() {
        sendAlert("TEST", "Test alert from JMX", "INFO");
    }

    public void sendAlert(String type, String message, String severity) {
        if (!alertsEnabled) {
            return;
        }

        Notification notification = new Notification(
            type,
            this,
            sequenceNumber.incrementAndGet(),
            System.currentTimeMillis(),
            message
        );
        
        notification.setUserData(Map.of(
            "severity", severity,
            "timestamp", Instant.now().toString()
        ));

        sendNotification(notification);
    }

    @Override
    public MBeanNotificationInfo[] getNotificationInfo() {
        return new MBeanNotificationInfo[]{
            new MBeanNotificationInfo(
                new String[]{"HEALTH", "PERFORMANCE", "SECURITY", "TEST"},
                Notification.class.getName(),
                "Application alerts and notifications"
            )
        };
    }
}
```

## Best Practices

1. **Naming Convention**: Use consistent ObjectName patterns
2. **Security**: Always secure JMX access in production
3. **Performance**: Be mindful of expensive operations in MBean methods
4. **Documentation**: Provide clear descriptions for attributes and operations
5. **Error Handling**: Handle exceptions gracefully in MBean operations
6. **Resource Management**: Properly manage resources in MBean operations
7. **Monitoring**: Monitor JMX itself for availability and performance

### Production JMX Configuration

```yaml
# Production JMX configuration
spring:
  jmx:
    enabled: true
    default-domain: "com.mycompany.myapp"

management:
  endpoints:
    jmx:
      exposure:
        include: "health,info,metrics"
        exclude: "env,configprops,beans"
  endpoint:
    jmx:
      enabled: true

# JVM JMX settings (set as JVM arguments)
# -Dcom.sun.management.jmxremote=true
# -Dcom.sun.management.jmxremote.port=9999
# -Dcom.sun.management.jmxremote.authenticate=true
# -Dcom.sun.management.jmxremote.ssl=true
# -Dcom.sun.management.jmxremote.access.file=/etc/jmx/jmxremote.access
# -Dcom.sun.management.jmxremote.password.file=/etc/jmx/jmxremote.password
```

### JMX Client Example

```java
public class JmxClient {

    public static void main(String[] args) throws Exception {
        String url = "service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi";
        JMXServiceURL serviceURL = new JMXServiceURL(url);
        
        Map<String, Object> environment = new HashMap<>();
        environment.put(JMXConnector.CREDENTIALS, new String[]{"admin", "password"});
        
        try (JMXConnector connector = JMXConnectorFactory.connect(serviceURL, environment)) {
            MBeanServerConnection connection = connector.getMBeanServerConnection();
            
            // Get application health
            ObjectName healthName = new ObjectName("com.example:type=Health,name=ApplicationHealth");
            String healthStatus = (String) connection.getAttribute(healthName, "HealthStatus");
            System.out.println("Health Status: " + healthStatus);
            
            // Invoke operation
            connection.invoke(healthName, "refreshHealth", null, null);
            
            // Listen for notifications
            ObjectName alertName = new ObjectName("com.example:type=Notifications,name=AlertManager");
            connection.addNotificationListener(alertName, 
                (notification, handback) -> {
                    System.out.println("Alert: " + notification.getMessage());
                }, null, null);
        }
    }
}
```