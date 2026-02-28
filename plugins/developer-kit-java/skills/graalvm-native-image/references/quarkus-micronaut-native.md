# Quarkus & Micronaut Native Image Support

Configuration patterns for native-first Java frameworks with GraalVM Native Image.

## Table of Contents

1. [Quarkus Native Build](#quarkus-native-build)
2. [Quarkus Configuration](#quarkus-configuration)
3. [Micronaut Native Build](#micronaut-native-build)
4. [Micronaut Configuration](#micronaut-configuration)
5. [Comparison](#comparison)

---

## Quarkus Native Build

Quarkus is designed native-first and requires minimal GraalVM-specific configuration.

### Building a Native Executable

```bash
# Using Maven (Quarkus Maven plugin handles native build)
./mvnw package -Dnative

# Using Gradle
./gradlew build -Dquarkus.native.enabled=true

# Using Quarkus CLI
quarkus build --native
```

### Container Build (no local GraalVM needed)

```bash
# Build in a container (uses Mandrel/GraalVM image)
./mvnw package -Dnative -Dquarkus.native.container-build=true

# Specify custom builder image
./mvnw package -Dnative \
    -Dquarkus.native.container-build=true \
    -Dquarkus.native.builder-image=quay.io/quarkus/ubi-quarkus-mandrel-builder-image:jdk-21
```

### Multi-Stage Dockerfile

```dockerfile
FROM quay.io/quarkus/ubi-quarkus-mandrel-builder-image:jdk-21 AS builder
COPY --chown=quarkus:quarkus mvnw /code/mvnw
COPY --chown=quarkus:quarkus .mvn /code/.mvn
COPY --chown=quarkus:quarkus pom.xml /code/
COPY --chown=quarkus:quarkus src /code/src
USER quarkus
WORKDIR /code
RUN ./mvnw package -Dnative -DskipTests

FROM quay.io/quarkus/quarkus-micro-image:2.0
WORKDIR /work/
COPY --from=builder /code/target/*-runner /work/application
RUN chmod 775 /work/application
EXPOSE 8080
CMD ["./application", "-Dquarkus.http.host=0.0.0.0"]
```

## Quarkus Configuration

### application.properties

```properties
# Native image build options
quarkus.native.additional-build-args=--no-fallback,-H:+ReportExceptionStackTraces

# Resource inclusion
quarkus.native.resources.includes=templates/**,META-INF/resources/**

# Enable HTTPS support
quarkus.native.enable-https-url-handler=true

# Build memory
quarkus.native.native-image-xmx=8g
```

### Registering Reflection

Quarkus provides annotations to register classes for reflection:

```java
import io.quarkus.runtime.annotations.RegisterForReflection;

@RegisterForReflection
public class MyDto {
    private String name;
    private int age;
    // constructors, getters, setters
}

// Register multiple classes including nested types
@RegisterForReflection(targets = {MyDto.class, OrderDto.class},
                       serialization = true)
public class ReflectionConfig {
}
```

### Testing Native Builds

```java
import io.quarkus.test.junit.QuarkusIntegrationTest;

@QuarkusIntegrationTest
public class NativeMyResourceIT {

    @Test
    public void testHelloEndpoint() {
        given()
            .when().get("/hello")
            .then()
            .statusCode(200)
            .body(is("Hello"));
    }
}
```

Run native integration tests:

```bash
./mvnw verify -Dnative
```

---

## Micronaut Native Build

Micronaut uses compile-time dependency injection and AOT processing, making it highly compatible with GraalVM.

### Building a Native Executable

```bash
# Using Maven
./mvnw package -Dpackaging=native-image

# Using Gradle
./gradlew nativeCompile

# Using Micronaut CLI
mn create-app --build=gradle --jdk=21 --features=graalvm myapp
```

### Gradle Configuration

```kotlin
plugins {
    id("io.micronaut.application") version "4.4.4"
    id("org.graalvm.buildtools.native") version "0.10.6"
}

micronaut {
    runtime("netty")
    testRuntime("junit5")
    processing {
        incremental(true)
        annotations("com.example.*")
    }
}

graalvmNative {
    binaries {
        named("main") {
            buildArgs.add("--no-fallback")
        }
    }
}
```

### Maven Configuration

```xml
<plugin>
    <groupId>io.micronaut.maven</groupId>
    <artifactId>micronaut-maven-plugin</artifactId>
    <configuration>
        <configFile>aot-${packaging}.properties</configFile>
    </configuration>
</plugin>

<profiles>
    <profile>
        <id>native</id>
        <properties>
            <packaging>native-image</packaging>
            <micronaut.runtime>netty</micronaut.runtime>
        </properties>
    </profile>
</profiles>
```

## Micronaut Configuration

### Registering Reflection

Micronaut minimizes reflection, but when needed:

```java
import io.micronaut.core.annotation.ReflectiveAccess;

@ReflectiveAccess
public class MyDto {
    private String name;
    private int age;
}

// Or use @Introspected for bean introspection (preferred)
import io.micronaut.core.annotation.Introspected;

@Introspected
public class MyDto {
    private String name;
    private int age;
}
```

### Resource Inclusion

In `src/main/resources/META-INF/native-image/resource-config.json`:

```json
{
  "resources": {
    "includes": [
      {"pattern": "application\\.yml"},
      {"pattern": "logback\\.xml"},
      {"pattern": "META-INF/.*"}
    ]
  }
}
```

### Docker Build

```bash
# Using Micronaut Gradle plugin
./gradlew dockerBuildNative

# Multi-stage Dockerfile
FROM ghcr.io/graalvm/native-image-community:21 AS builder
WORKDIR /app
COPY . .
RUN ./gradlew nativeCompile --no-daemon

FROM debian:bookworm-slim
COPY --from=builder /app/build/native/nativeCompile/myapp /app/myapp
EXPOSE 8080
ENTRYPOINT ["/app/myapp"]
```

---

## Comparison

| Feature | Quarkus | Micronaut |
|---------|---------|-----------|
| DI approach | Build-time with ArC | Compile-time with annotation processors |
| Native build command | `./mvnw package -Dnative` | `./gradlew nativeCompile` |
| Reflection annotation | `@RegisterForReflection` | `@Introspected` / `@ReflectiveAccess` |
| Container build | Built-in container build support | Docker plugin |
| Dev mode | `quarkus dev` (live reload) | `mn run` with restart |
| Startup time (native) | ~10-50ms | ~10-50ms |
| Typical RSS | ~20-50MB | ~20-50MB |
| GraalVM version | Mandrel (Red Hat distribution) | GraalVM CE/EE |
