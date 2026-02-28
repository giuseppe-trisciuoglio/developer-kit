# GraalVM Tracing Agent

Guide for using the GraalVM tracing agent to automatically collect reachability metadata for native image builds.

## Table of Contents

1. [Overview](#overview)
2. [Running the Tracing Agent](#running-the-tracing-agent)
3. [Agent Modes](#agent-modes)
4. [Integration with Build Tools](#integration-with-build-tools)
5. [Filtering and Fine-Tuning](#filtering-and-fine-tuning)

---

## Overview

The GraalVM tracing agent intercepts all dynamic accesses (reflection, resources, JNI, proxies, serialization) during application execution on the JVM and generates the corresponding GraalVM metadata files.

**When to use the tracing agent:**
- Initial native image migration of a complex project
- After adding new libraries with reflection requirements
- When manual metadata configuration is insufficient
- To discover hidden reflection/resource usage

**Important**: The agent only captures code paths exercised during the run. Ensure thorough coverage by running all application features, endpoints, and edge cases.

## Running the Tracing Agent

### Basic Usage

```bash
# Create output directory
mkdir -p src/main/resources/META-INF/native-image

# Run with the tracing agent
java -agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image \
    -jar target/myapp.jar
```

Then exercise all application features (call APIs, trigger scheduled tasks, etc.) before shutting down gracefully.

### With Spring Boot

```bash
# Run Spring Boot app with tracing agent
java -agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image \
    -jar target/myapp.jar

# Exercise all endpoints
curl http://localhost:8080/api/users
curl -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' -d '{"name":"test"}'
curl http://localhost:8080/actuator/health

# Shut down gracefully (Ctrl+C or kill -SIGTERM)
```

### Merging with Existing Config

```bash
# Merge agent output with existing metadata (does not overwrite)
java -agentlib:native-image-agent=config-merge-dir=src/main/resources/META-INF/native-image \
    -jar target/myapp.jar
```

## Agent Modes

### Output Mode (Fresh Config)

Writes new configuration, overwriting any existing files:

```bash
-agentlib:native-image-agent=config-output-dir=<path>
```

### Merge Mode (Append to Existing)

Merges new entries into existing configuration files:

```bash
-agentlib:native-image-agent=config-merge-dir=<path>
```

### Conditional Mode

Generate conditional metadata (only include if a type is reachable):

```bash
-agentlib:native-image-agent=config-output-dir=<path>,experimental-conditional-config-filter-file=filter.json
```

## Integration with Build Tools

### Maven — Run Agent During Tests

```xml
<profiles>
  <profile>
    <id>agent</id>
    <build>
      <plugins>
        <plugin>
          <groupId>org.graalvm.buildtools</groupId>
          <artifactId>native-maven-plugin</artifactId>
          <configuration>
            <agent>
              <enabled>true</enabled>
              <options>
                <option>config-output-dir=src/main/resources/META-INF/native-image</option>
              </options>
            </agent>
          </configuration>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-surefire-plugin</artifactId>
          <configuration>
            <argLine>-agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image</argLine>
          </configuration>
        </plugin>
      </plugins>
    </build>
  </profile>
</profiles>
```

Run with:

```bash
./mvnw -Pagent test
```

### Gradle — Run Agent During Tests

```kotlin
graalvmNative {
    agent {
        defaultMode.set("standard")
        metadataCopy {
            inputTaskNames.add("test")
            outputDirectories.add("src/main/resources/META-INF/native-image")
            mergeWithExisting.set(true)
        }
    }
}
```

Run with:

```bash
# Run tests with agent
./gradlew -Pagent test

# Copy collected metadata
./gradlew metadataCopy
```

## Filtering and Fine-Tuning

### Agent Filter Configuration

Create a filter file to reduce noise in the generated metadata:

```json
{
  "rules": [
    {
      "excludeClasses": "jdk.internal.**"
    },
    {
      "excludeClasses": "sun.**"
    },
    {
      "excludeClasses": "com.sun.**"
    },
    {
      "includeClasses": "com.example.**"
    }
  ]
}
```

Use with:

```bash
java -agentlib:native-image-agent=config-output-dir=<path>,caller-filter-file=filter.json \
    -jar target/myapp.jar
```

### Post-Processing Agent Output

After collecting metadata, review and clean up:

1. **Remove unnecessary entries** — The agent is conservative; many entries may not be needed
2. **Add conditions** — Use `condition.typeReached` to limit when metadata is applied
3. **Verify correctness** — Build the native image and test thoroughly
4. **Commit metadata** — Add the generated files to version control

### Recommended Workflow

```bash
# 1. Run agent with tests for baseline coverage
./mvnw -Pagent test

# 2. Run agent with the full application for runtime coverage
java -agentlib:native-image-agent=config-merge-dir=src/main/resources/META-INF/native-image \
    -jar target/myapp.jar
# Exercise all features, then shut down

# 3. Build native image
./mvnw -Pnative package

# 4. Test the native executable
./target/myapp

# 5. If failures occur, repeat steps 2-4 with additional code paths
```
