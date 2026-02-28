# Maven Native Build Tools Configuration

Complete Maven configuration for building GraalVM native images using the Native Build Tools plugin.

## Table of Contents

1. [Native Profile Setup](#native-profile-setup)
2. [Plugin Configuration Options](#plugin-configuration-options)
3. [Spring Boot Maven Integration](#spring-boot-maven-integration)
4. [Testing in Native Mode](#testing-in-native-mode)
5. [Multi-Module Projects](#multi-module-projects)

---

## Native Profile Setup

Add a `native` profile to your `pom.xml` to keep native-specific configuration separate:

```xml
<profiles>
  <profile>
    <id>native</id>
    <build>
      <plugins>
        <plugin>
          <groupId>org.graalvm.buildtools</groupId>
          <artifactId>native-maven-plugin</artifactId>
          <version>0.10.6</version>
          <extensions>true</extensions>
          <executions>
            <execution>
              <id>build-native</id>
              <goals>
                <goal>compile-no-fork</goal>
              </goals>
              <phase>package</phase>
            </execution>
            <execution>
              <id>test-native</id>
              <goals>
                <goal>test</goal>
              </goals>
              <phase>test</phase>
            </execution>
          </executions>
          <configuration>
            <imageName>${project.artifactId}</imageName>
            <mainClass>${exec.mainClass}</mainClass>
            <buildArgs>
              <buildArg>--no-fallback</buildArg>
              <buildArg>-H:+ReportExceptionStackTraces</buildArg>
            </buildArgs>
          </configuration>
        </plugin>
      </plugins>
    </build>
  </profile>
</profiles>
```

## Plugin Configuration Options

### Common Build Arguments

```xml
<configuration>
  <imageName>${project.artifactId}</imageName>
  <mainClass>com.example.Application</mainClass>
  <fallback>false</fallback>
  <verbose>true</verbose>
  <buildArgs>
    <!-- Disable fallback to JVM -->
    <buildArg>--no-fallback</buildArg>
    <!-- Report exception stack traces -->
    <buildArg>-H:+ReportExceptionStackTraces</buildArg>
    <!-- Increase build memory -->
    <buildArg>-J-Xmx8g</buildArg>
    <!-- Enable HTTPS support -->
    <buildArg>--enable-https</buildArg>
    <!-- Quick build mode (dev only, slower runtime) -->
    <buildArg>-Ob</buildArg>
    <!-- Include all resources matching pattern -->
    <buildArg>-H:IncludeResources=application.*</buildArg>
  </buildArgs>
  <!-- GraalVM metadata repository support -->
  <metadataRepository>
    <enabled>true</enabled>
  </metadataRepository>
</configuration>
```

### Metadata Repository Integration

The GraalVM Reachability Metadata Repository provides pre-built metadata for popular libraries:

```xml
<configuration>
  <metadataRepository>
    <enabled>true</enabled>
    <version>0.3.14</version>
  </metadataRepository>
</configuration>
```

## Spring Boot Maven Integration

For Spring Boot 3.x projects, the parent POM includes a `native` profile. Combine with the Spring Boot Maven Plugin:

```xml
<profiles>
  <profile>
    <id>native</id>
    <build>
      <plugins>
        <plugin>
          <groupId>org.springframework.boot</groupId>
          <artifactId>spring-boot-maven-plugin</artifactId>
          <executions>
            <execution>
              <id>process-aot</id>
              <goals>
                <goal>process-aot</goal>
              </goals>
            </execution>
          </executions>
        </plugin>
        <plugin>
          <groupId>org.graalvm.buildtools</groupId>
          <artifactId>native-maven-plugin</artifactId>
        </plugin>
      </plugins>
    </build>
  </profile>
</profiles>
```

Build commands:

```bash
# Compile to native executable
./mvnw -Pnative native:compile

# Build OCI image with Cloud Native Buildpacks
./mvnw -Pnative spring-boot:build-image

# Run AOT processing only (for debugging)
./mvnw -Pnative process-aot
```

## Testing in Native Mode

Run JUnit tests compiled as a native executable:

```bash
# Run native tests
./mvnw -Pnative test

# Or explicitly
./mvnw -Pnative native:test
```

Configure test-specific settings:

```xml
<execution>
  <id>test-native</id>
  <goals>
    <goal>test</goal>
  </goals>
  <phase>test</phase>
  <configuration>
    <buildArgs>
      <buildArg>-H:+ReportExceptionStackTraces</buildArg>
      <buildArg>--no-fallback</buildArg>
    </buildArgs>
  </configuration>
</execution>
```

## Multi-Module Projects

For multi-module Maven projects, configure the native plugin in the module that produces the executable:

```xml
<!-- parent pom.xml -->
<pluginManagement>
  <plugins>
    <plugin>
      <groupId>org.graalvm.buildtools</groupId>
      <artifactId>native-maven-plugin</artifactId>
      <version>0.10.6</version>
    </plugin>
  </plugins>
</pluginManagement>

<!-- child module pom.xml (the executable module) -->
<profiles>
  <profile>
    <id>native</id>
    <build>
      <plugins>
        <plugin>
          <groupId>org.graalvm.buildtools</groupId>
          <artifactId>native-maven-plugin</artifactId>
          <configuration>
            <imageName>${project.artifactId}</imageName>
            <mainClass>com.example.Application</mainClass>
          </configuration>
        </plugin>
      </plugins>
    </build>
  </profile>
</profiles>
```
