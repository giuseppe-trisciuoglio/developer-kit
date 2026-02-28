# GraalVM Native Image Skills Guide

Quick reference to the GraalVM Native Image skill for building high-performance native executables from Java applications. See individual skill files for complete details.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **graalvm-native-image** | Build native executables from Java applications, optimize cold start times, reduce memory footprint, configure native build tools, resolve reflection/resource issues |

---

## graalvm-native-image

**File**: `skills/graalvm-native-image/SKILL.md`

Build native executables from Java applications using GraalVM Native Image, dramatically reducing startup time and memory consumption.

**When to use:**
- Converting JVM-based Java applications to native executables
- Optimizing cold start times for serverless or containerized deployments
- Reducing memory footprint (RSS) of Java microservices
- Configuring Maven or Gradle with GraalVM Native Build Tools
- Resolving `ClassNotFoundException`, `NoSuchMethodException`, or missing resource errors in native builds
- Generating or editing `reflect-config.json`, `resource-config.json`, or other GraalVM metadata files
- Using the GraalVM tracing agent to collect reachability metadata
- Implementing `RuntimeHints` for Spring Boot native support
- Building native images with Quarkus or Micronaut

---

## Quick Start

### Maven Projects

Add the native profile to `pom.xml`:

```bash
./mvnw -Pnative package
```

### Gradle Projects

Apply the native plugin:

```bash
./gradlew nativeCompile
```

---

## Framework Support

### Spring Boot

- Use Spring Boot 3.x+ with built-in GraalVM support
- Register reflection hints via `RuntimeHintsRegistrar`
- Run AOT processing with `process-aot` goal

### Quarkus & Micronaut

- Native-first frameworks with minimal additional configuration
- Built-in GraalVM support out of the box

---

## Common Workflows

### Building a Native Executable

```
1. graalvm-native-image         → Analyze project and detect framework
2. Configure build tools        → Maven native profile or Gradle plugin
3. Run native build            → ./mvnw -Pnative package
4. Fix metadata issues        → Iterative error resolution
5. Validate and benchmark      → Measure startup and memory
```

### Resolving Build Errors

```
1. Execute native build       → ./mvnw -Pnative package
2. Parse build errors         → Identify root cause
3. Apply fixes               → Update metadata files
4. Rebuild and verify         → Repeat until success
5. Use tracing agent          → For complex projects
```

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **AOT Compilation** | Ahead-of-time compilation to native executable |
| **Closed-world assumption** | All code paths must be known at build time |
| **Reachability Metadata** | Configuration for reflection, resources, proxies |
| **Tracing Agent** | Tool to automatically collect reachability metadata |

---

## Performance Improvements

| Metric | JVM | Native | Improvement |
|--------|-----|--------|-------------|
| Startup time | ~2-5s | ~50-200ms | 10-100x |
| Memory (RSS) | ~200-500MB | ~30-80MB | 3-10x |
| Binary size | JRE + JARs | Single binary | Simplified |

---

## Technology Stack

- **GraalVM**: 21+
- **Java**: 17+ (21+ recommended)
- **Build Tools**: Maven 3.6+, Gradle 8+
- **Frameworks**: Spring Boot 3.x, Quarkus, Micronaut
- **Native Build Tools**: 0.10.x

---

## References

- [Maven Native Profile](skills/graalvm-native-image/references/maven-native-profile.md)
- [Gradle Native Plugin](skills/graalvm-native-image/references/gradle-native-plugin.md)
- [Spring Boot Native](skills/graalvm-native-image/references/spring-boot-native.md)
- [Quarkus & Micronaut](skills/graalvm-native-image/references/quarkus-micronaut-native.md)
- [Reflection & Resource Config](skills/graalvm-native-image/references/reflection-resource-config.md)
- [Tracing Agent](skills/graalvm-native-image/references/tracing-agent.md)

---

**Note**: For complete patterns and examples, see the individual skill file at `skills/graalvm-native-image/SKILL.md`
