# Testcontainers Configuration

## Spring Boot 3.5+ `@ServiceConnection`

```java
@TestConfiguration
public class TestContainerConfig {

    @Bean
    @ServiceConnection
    public PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>(DockerImageName.parse("postgres:16-alpine"))
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
    }

    @Bean
    @ServiceConnection
    public GenericContainer<?> redisContainer() {
        return new GenericContainer<>(DockerImageName.parse("redis:7-alpine"))
            .withExposedPorts(6379);
    }
}
```

Apply with `@Import(TestContainerConfig.class)` on test classes.

## Traditional `@DynamicPropertySource`

```java
@Testcontainers
class UserServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"))
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

## Multiple Containers

```java
@Testcontainers
class MultiContainerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        "postgres:16-alpine")
        .withDatabaseName("testdb");

    @Container
    static GenericContainer<?> redis = new GenericContainer<>(
        "redis:7-alpine")
        .withExposedPorts(6379);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.redis.host", redis::getHost);
        registry.add("spring.redis.port", redis::getFirstMappedPort);
    }
}
```

## Container Reuse Strategy

```java
@Testcontainers(disableWithoutDocker = true)
class ContainerConfig {

    static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"))
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test")
        .withReuse(true);

    @BeforeAll
    static void startAll() {
        POSTGRES.start();
    }

    @AfterAll
    static void stopAll() {
        POSTGRES.stop();
    }
}
```

Enable reuse with environment variable: `TESTCONTAINERS_REUSE_ENABLE=true`

## MySQL Container

```java
@Container
static MySQLContainer<?> mysql = new MySQLContainer<>(
    DockerImageName.parse("mysql:8.0"))
    .withDatabaseName("testdb")
    .withUsername("test")
    .withPassword("test");
```

## MongoDB Container

```java
@Container
static MongoDBContainer<?> mongodb = new MongoDBContainer<>(
    DockerImageName.parse("mongo:6.0"))
    .withExposedPorts(27017);
```

## Kafka Container

```java
@Container
static KafkaContainer kafka = new KafkaContainer(
    DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));

@DynamicPropertySource
static void kafkaProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
}
```

## Container Initialization

```java
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
    "postgres:16-alpine")
    .withDatabaseName("testdb")
    .withUsername("test")
    .withPassword("test")
    .withInitScript("sql/init-test.sql") // Run init script
    .withCommand("postgres", "-c", "max_connections=200"); // Custom config
```

## Network Configuration

```java
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
    "postgres:16-alpine")
    .withNetwork(Network.SHARED)
    .withNetworkAliases("pgdb"); // Access via hostname
```
