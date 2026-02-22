# Configuration Properties Testing - Detailed Examples

## Testing Nested Configuration Properties

### Complex Property Structure

```java
@ConfigurationProperties(prefix = "app.database")
@Data
public class DatabaseProperties {
  private String url;
  private String username;
  private Pool pool = new Pool();
  private List<Replica> replicas = new ArrayList<>();

  @Data
  public static class Pool {
    private int maxSize = 10;
    private int minIdle = 5;
    private long connectionTimeout = 30000;
  }

  @Data
  public static class Replica {
    private String name;
    private String url;
    private int priority;
  }
}

class NestedPropertiesTest {

  @Test
  void shouldBindNestedProperties() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.database.url=jdbc:mysql://localhost/db",
        "app.database.username=admin",
        "app.database.pool.maxSize=20",
        "app.database.pool.minIdle=10",
        "app.database.pool.connectionTimeout=60000"
      )
      .withBean(DatabaseProperties.class)
      .run(context -> {
        DatabaseProperties props = context.getBean(DatabaseProperties.class);

        assertThat(props.getUrl()).isEqualTo("jdbc:mysql://localhost/db");
        assertThat(props.getPool().getMaxSize()).isEqualTo(20);
        assertThat(props.getPool().getConnectionTimeout()).isEqualTo(60000L);
      });
  }

  @Test
  void shouldBindListOfReplicas() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.database.replicas[0].name=replica-1",
        "app.database.replicas[0].url=jdbc:mysql://replica1/db",
        "app.database.replicas[0].priority=1",
        "app.database.replicas[1].name=replica-2",
        "app.database.replicas[1].url=jdbc:mysql://replica2/db",
        "app.database.replicas[1].priority=2"
      )
      .withBean(DatabaseProperties.class)
      .run(context -> {
        DatabaseProperties props = context.getBean(DatabaseProperties.class);

        assertThat(props.getReplicas()).hasSize(2);
        assertThat(props.getReplicas().get(0).getName()).isEqualTo("replica-1");
        assertThat(props.getReplicas().get(1).getPriority()).isEqualTo(2);
      });
  }
}
```

## Testing Property Validation

### Validate Configuration with Constraints

```java
@ConfigurationProperties(prefix = "app.server")
@Data
@Validated
public class ServerProperties {
  @NotBlank
  private String host;

  @Min(1)
  @Max(65535)
  private int port = 8080;

  @Positive
  private int threadPoolSize;

  @Email
  private String adminEmail;
}

class ConfigurationValidationTest {

  @Test
  void shouldFailValidationWhenHostIsBlank() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.server.host=",
        "app.server.port=8080",
        "app.server.threadPoolSize=10"
      )
      .withBean(ServerProperties.class)
      .run(context -> {
        assertThat(context).hasFailed()
          .getFailure()
          .hasMessageContaining("host");
      });
  }

  @Test
  void shouldFailValidationWhenPortOutOfRange() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.server.host=localhost",
        "app.server.port=99999",
        "app.server.threadPoolSize=10"
      )
      .withBean(ServerProperties.class)
      .run(context -> {
        assertThat(context).hasFailed();
      });
  }

  @Test
  void shouldPassValidationWithValidConfiguration() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.server.host=localhost",
        "app.server.port=8080",
        "app.server.threadPoolSize=10",
        "app.server.adminEmail=admin@example.com"
      )
      .withBean(ServerProperties.class)
      .run(context -> {
        assertThat(context).hasNotFailed();
        ServerProperties props = context.getBean(ServerProperties.class);
        assertThat(props.getHost()).isEqualTo("localhost");
      });
  }
}
```

## Testing Profile-Specific Configurations

### Environment-Specific Properties

```java
@Configuration
@Profile("prod")
class ProductionConfiguration {
  @Bean
  public SecurityProperties securityProperties() {
    SecurityProperties props = new SecurityProperties();
    props.setEnableTwoFactor(true);
    props.setMaxLoginAttempts(3);
    return props;
  }
}

@Configuration
@Profile("dev")
class DevelopmentConfiguration {
  @Bean
  public SecurityProperties securityProperties() {
    SecurityProperties props = new SecurityProperties();
    props.setEnableTwoFactor(false);
    props.setMaxLoginAttempts(999);
    return props;
  }
}

class ProfileBasedConfigurationTest {

  @Test
  void shouldLoadProductionConfiguration() {
    new ApplicationContextRunner()
      .withPropertyValues("spring.profiles.active=prod")
      .withUserConfiguration(ProductionConfiguration.class)
      .run(context -> {
        SecurityProperties props = context.getBean(SecurityProperties.class);

        assertThat(props.isEnableTwoFactor()).isTrue();
        assertThat(props.getMaxLoginAttempts()).isEqualTo(3);
      });
  }

  @Test
  void shouldLoadDevelopmentConfiguration() {
    new ApplicationContextRunner()
      .withPropertyValues("spring.profiles.active=dev")
      .withUserConfiguration(DevelopmentConfiguration.class)
      .run(context -> {
        SecurityProperties props = context.getBean(SecurityProperties.class);

        assertThat(props.isEnableTwoFactor()).isFalse();
        assertThat(props.getMaxLoginAttempts()).isEqualTo(999);
      });
  }
}
```

## Testing Type Conversion

### Property Type Binding

```java
@ConfigurationProperties(prefix = "app.features")
@Data
public class FeatureProperties {
  private Duration cacheExpiry = Duration.ofMinutes(10);
  private DataSize maxUploadSize = DataSize.ofMegabytes(100);
  private List<String> enabledFeatures;
  private Map<String, String> featureFlags;
  private Charset fileEncoding = StandardCharsets.UTF_8;
}

class TypeConversionTest {

  @Test
  void shouldConvertStringToDuration() {
    new ApplicationContextRunner()
      .withPropertyValues("app.features.cacheExpiry=30s")
      .withBean(FeatureProperties.class)
      .run(context -> {
        FeatureProperties props = context.getBean(FeatureProperties.class);
        assertThat(props.getCacheExpiry()).isEqualTo(Duration.ofSeconds(30));
      });
  }

  @Test
  void shouldConvertStringToDataSize() {
    new ApplicationContextRunner()
      .withPropertyValues("app.features.maxUploadSize=50MB")
      .withBean(FeatureProperties.class)
      .run(context -> {
        FeatureProperties props = context.getBean(FeatureProperties.class);
        assertThat(props.getMaxUploadSize()).isEqualTo(DataSize.ofMegabytes(50));
      });
  }

  @Test
  void shouldConvertCommaDelimitedListToList() {
    new ApplicationContextRunner()
      .withPropertyValues("app.features.enabledFeatures=feature1,feature2,feature3")
      .withBean(FeatureProperties.class)
      .run(context -> {
        FeatureProperties props = context.getBean(FeatureProperties.class);
        assertThat(props.getEnabledFeatures())
          .containsExactly("feature1", "feature2", "feature3");
      });
  }
}
```

## Testing Property Binding with Default Values

### Verify Default Configuration

```java
@ConfigurationProperties(prefix = "app.cache")
@Data
public class CacheProperties {
  private long ttlSeconds = 300;
  private int maxSize = 1000;
  private boolean enabled = true;
  private String cacheType = "IN_MEMORY";
}

class DefaultValuesTest {

  @Test
  void shouldUseDefaultValuesWhenNotSpecified() {
    new ApplicationContextRunner()
      .withBean(CacheProperties.class)
      .run(context -> {
        CacheProperties props = context.getBean(CacheProperties.class);

        assertThat(props.getTtlSeconds()).isEqualTo(300L);
        assertThat(props.getMaxSize()).isEqualTo(1000);
        assertThat(props.isEnabled()).isTrue();
        assertThat(props.getCacheType()).isEqualTo("IN_MEMORY");
      });
  }

  @Test
  void shouldOverrideDefaultValuesWithProvidedProperties() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.cache.ttlSeconds=600",
        "app.cache.cacheType=REDIS"
      )
      .withBean(CacheProperties.class)
      .run(context -> {
        CacheProperties props = context.getBean(CacheProperties.class);

        assertThat(props.getTtlSeconds()).isEqualTo(600L);
        assertThat(props.getCacheType()).isEqualTo("REDIS");
        assertThat(props.getMaxSize()).isEqualTo(1000); // Default unchanged
      });
  }
}
```
