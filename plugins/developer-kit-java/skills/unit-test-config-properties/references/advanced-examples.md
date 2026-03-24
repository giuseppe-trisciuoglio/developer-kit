# Advanced ConfigurationProperties Testing Examples

## Nested Configuration Properties

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

## Profile-Specific Configurations

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

## Map-Based Properties

```java
@ConfigurationProperties(prefix = "app.feature-flags")
@Data
public class FeatureFlagProperties {
  private Map<String, Boolean> flags = new HashMap<>();
  private Map<String, FeatureConfig> features = new HashMap<>();

  @Data
  public static class FeatureConfig {
    private boolean enabled;
    private String description;
    private List<String> allowedUsers;
  }
}

class MapPropertiesTest {

  @Test
  void shouldBindSimpleBooleanMap() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.feature-flags.flags.dark-mode=true",
        "app.feature-flags.flags.beta-features=false"
      )
      .withBean(FeatureFlagProperties.class)
      .run(context -> {
        FeatureFlagProperties props = context.getBean(FeatureFlagProperties.class);
        assertThat(props.getFlags()).containsEntry("dark-mode", true);
        assertThat(props.getFlags()).containsEntry("beta-features", false);
      });
  }

  @Test
  void shouldBindNestedMapStructures() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.feature-flags.features.payment.enabled=true",
        "app.feature-flags.features.payment.description=Payment module",
        "app.feature-flags.features.payment.allowedUsers[0]=admin",
        "app.feature-flags.features.payment.allowedUsers[1]=finance"
      )
      .withBean(FeatureFlagProperties.class)
      .run(context -> {
        FeatureFlagProperties props = context.getBean(FeatureFlagProperties.class);
        FeatureFlagProperties.FeatureConfig payment = props.getFeatures().get("payment");
        assertThat(payment.isEnabled()).isTrue();
        assertThat(payment.getDescription()).isEqualTo("Payment module");
        assertThat(payment.getAllowedUsers()).containsExactly("admin", "finance");
      });
  }
}
```

## Default Values Testing

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

## DataSize and Duration Advanced Patterns

```java
@ConfigurationProperties(prefix = "app.upload")
@Data
public class UploadProperties {
  private DataSize maxFileSize = DataSize.ofMegabytes(10);
  private DataSize maxTotalSize = DataSize.ofGigabytes(1);
  private Duration timeout = Duration.ofSeconds(30);
  private List<DataSize> allowedExtensions;
}

class DataSizeDurationTest {

  @Test
  void shouldConvertVariousDurationFormats() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.upload.timeout=2h30m",
        "app.upload.maxFileSize=25MB",
        "app.upload.maxTotalSize=5GB"
      )
      .withBean(UploadProperties.class)
      .run(context -> {
        UploadProperties props = context.getBean(UploadProperties.class);
        assertThat(props.getTimeout()).isEqualTo(Duration.ofHours(2).plusMinutes(30));
        assertThat(props.getMaxFileSize()).isEqualTo(DataSize.ofMegabytes(25));
        assertThat(props.getMaxTotalSize()).isEqualTo(DataSize.ofGigabytes(5));
      });
  }

  @Test
  void shouldHandleIsoDurationFormat() {
    new ApplicationContextRunner()
      .withPropertyValues("app.upload.timeout=PT1H30M")
      .withBean(UploadProperties.class)
      .run(context -> {
        assertThat(context.getBean(UploadProperties.class).getTimeout())
          .isEqualTo(Duration.ofHours(1).plusMinutes(30));
      });
  }
}
```

## References

- [Spring Boot ConfigurationProperties](https://docs.spring.io/spring-boot/docs/current/reference/html/configuration-metadata.html)
- [ApplicationContextRunner Testing](https://docs.spring.io/spring-boot/docs/current/api/org/springframework/boot/test/context/runner/ApplicationContextRunner.html)
- [Spring Boot Validation](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.validation)
- [Relaxed Binding](https://docs.spring.io/spring-boot/docs/current/reference/html/configuration-metadata.html#configuration-metadata.annotation-processor)
