# Spring Boot Native Image Support

Complete guide for building Spring Boot 3.x applications as GraalVM native images with AOT processing.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AOT Processing](#aot-processing)
3. [RuntimeHints Registration](#runtimehints-registration)
4. [Common Annotations](#common-annotations)
5. [Conditional Beans in Native](#conditional-beans-in-native)
6. [Testing Native Applications](#testing-native-applications)
7. [Cloud Native Buildpacks](#cloud-native-buildpacks)

---

## Prerequisites

- Spring Boot 3.0+ (recommended: 3.4+)
- GraalVM JDK 21+ or GraalVM CE with `native-image` installed
- Native Build Tools plugin (Maven or Gradle)

Spring Boot 3.x provides first-class GraalVM Native Image support. The `spring-boot-starter-parent` includes a `native` profile with all necessary configurations.

## AOT Processing

Spring Boot AOT processing generates optimized code at build time that replaces runtime reflection:

**What AOT does:**
- Evaluates `@Conditional` annotations at build time
- Generates bean definitions as source code
- Creates reflection hints for the remaining dynamic access
- Pre-computes component scanning and auto-configuration

**Important constraints:**
- Bean definitions must be fixed at build time
- `@Profile` conditions are evaluated during AOT — active profiles must be specified at build time
- `@ConditionalOnProperty` is evaluated at build time
- Classpath must remain the same between AOT processing and runtime

### Configuring Active Profiles at Build Time

```xml
<!-- Maven -->
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <executions>
        <execution>
            <id>process-aot</id>
            <configuration>
                <profiles>prod</profiles>
            </configuration>
        </execution>
    </executions>
</plugin>
```

```kotlin
// Gradle
tasks.withType<org.springframework.boot.gradle.tasks.aot.ProcessAot>().configureEach {
    args("--spring.profiles.active=prod")
}
```

## RuntimeHints Registration

When Spring Boot's automatic hint detection is insufficient, register hints manually:

### Using `RuntimeHintsRegistrar`

```java
import org.springframework.aot.hint.RuntimeHints;
import org.springframework.aot.hint.RuntimeHintsRegistrar;
import org.springframework.context.annotation.ImportRuntimeHints;

@ImportRuntimeHints(MyRuntimeHints.class)
@Configuration
public class AppConfig {
    // ...
}

public class MyRuntimeHints implements RuntimeHintsRegistrar {

    @Override
    public void registerHints(RuntimeHints hints, ClassLoader classLoader) {
        // Register reflection
        hints.reflection()
            .registerType(MyDto.class,
                builder -> builder
                    .withMembers(MemberCategory.INVOKE_DECLARED_CONSTRUCTORS,
                                 MemberCategory.INVOKE_DECLARED_METHODS,
                                 MemberCategory.DECLARED_FIELDS));

        // Register resources
        hints.resources()
            .registerPattern("templates/*.html")
            .registerPattern("static/**");

        // Register serialization
        hints.serialization()
            .registerType(MySerializableClass.class);

        // Register proxies
        hints.proxies()
            .registerJdkProxy(MyInterface.class);
    }
}
```

### Using `@RegisterReflectionForBinding`

A convenience annotation to register reflection hints for DTOs and data classes:

```java
@RestController
@RegisterReflectionForBinding({UserDto.class, OrderDto.class, AddressDto.class})
public class UserController {

    @GetMapping("/users/{id}")
    public UserDto getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
}
```

### Using `@Reflective`

Mark individual classes for reflection registration:

```java
@Reflective
public class MyDto {
    private String name;
    private int age;
    // getters, setters, constructors
}
```

## Common Annotations

| Annotation | Purpose |
|-----------|---------|
| `@RegisterReflectionForBinding` | Register DTOs for reflection (constructors, methods, fields) |
| `@Reflective` | Mark a class for reflection registration |
| `@ImportRuntimeHints` | Import a `RuntimeHintsRegistrar` implementation |
| `@AotTestAttributes` | Provide test attributes during AOT processing |

## Conditional Beans in Native

Beans using `@Conditional` annotations are evaluated at build time during AOT:

```java
// This works — condition is resolved at build time
@Configuration
@Profile("prod")
public class ProdConfig {
    @Bean
    public DataSource dataSource() { /* ... */ }
}

// This requires the property to be available at build time
@Configuration
@ConditionalOnProperty(name = "feature.enabled", havingValue = "true")
public class FeatureConfig {
    @Bean
    public FeatureService featureService() { /* ... */ }
}
```

**Best practice**: For native images, prefer environment variables over properties for runtime-switchable configuration.

## Testing Native Applications

### Native Test Execution

Run JUnit tests in native mode to verify AOT-compiled tests:

```bash
# Maven
./mvnw -Pnative test

# Gradle
./gradlew nativeTest
```

### Test-Specific AOT Processing

```bash
# Maven
./mvnw -Pnative spring-boot:process-test-aot

# Gradle
./gradlew processTestAot
```

### RuntimeHints Testing

Verify that runtime hints are correctly registered without building a native image:

```java
import org.springframework.aot.hint.RuntimeHints;
import org.springframework.aot.hint.predicate.RuntimeHintsPredicates;

@Test
void shouldRegisterHints() {
    RuntimeHints hints = new RuntimeHints();
    new MyRuntimeHints().registerHints(hints, getClass().getClassLoader());

    assertThat(RuntimeHintsPredicates.reflection()
        .onType(MyDto.class)
        .withMemberCategories(MemberCategory.INVOKE_DECLARED_CONSTRUCTORS))
        .accepts(hints);

    assertThat(RuntimeHintsPredicates.resource()
        .forResource("templates/index.html"))
        .accepts(hints);
}
```

## Cloud Native Buildpacks

Build OCI images with Paketo Buildpacks (no local GraalVM installation needed):

```bash
# Maven
./mvnw -Pnative spring-boot:build-image \
    -Dspring-boot.build-image.imageName=myapp:native

# Gradle
./gradlew bootBuildImage \
    --imageName=myapp:native
```

Configure the builder in `pom.xml`:

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <image>
            <builder>paketobuildpacks/builder-jammy-tiny:latest</builder>
            <env>
                <BP_NATIVE_IMAGE>true</BP_NATIVE_IMAGE>
                <BP_NATIVE_IMAGE_BUILD_ARGUMENTS>
                    --no-fallback -H:+ReportExceptionStackTraces
                </BP_NATIVE_IMAGE_BUILD_ARGUMENTS>
            </env>
        </image>
    </configuration>
</plugin>
```
