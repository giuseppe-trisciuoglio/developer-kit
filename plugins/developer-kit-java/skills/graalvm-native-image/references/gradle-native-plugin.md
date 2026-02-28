# Gradle GraalVM Native Build Tools Plugin

Complete Gradle configuration for building GraalVM native images using the Native Build Tools plugin.

## Table of Contents

1. [Plugin Setup](#plugin-setup)
2. [Configuration Options](#configuration-options)
3. [Spring Boot Gradle Integration](#spring-boot-gradle-integration)
4. [Testing in Native Mode](#testing-in-native-mode)
5. [Multi-Project Builds](#multi-project-builds)

---

## Plugin Setup

### Kotlin DSL (`build.gradle.kts`)

```kotlin
plugins {
    java
    id("org.graalvm.buildtools.native") version "0.10.6"
}

graalvmNative {
    binaries {
        named("main") {
            imageName.set(project.name)
            mainClass.set("com.example.Application")
            buildArgs.add("--no-fallback")
            buildArgs.add("-H:+ReportExceptionStackTraces")
            javaLauncher.set(javaToolchains.launcherFor {
                languageVersion.set(JavaLanguageVersion.of(21))
                vendor.set(JvmVendorSpec.matching("GraalVM"))
            })
        }
    }
}
```

### Groovy DSL (`build.gradle`)

```groovy
plugins {
    id 'java'
    id 'org.graalvm.buildtools.native' version '0.10.6'
}

graalvmNative {
    binaries {
        main {
            imageName = project.name
            mainClass = 'com.example.Application'
            buildArgs.add('--no-fallback')
            buildArgs.add('-H:+ReportExceptionStackTraces')
        }
    }
}
```

Build with:

```bash
./gradlew nativeCompile
```

The native executable is produced in `build/native/nativeCompile/`.

## Configuration Options

### Binary Configuration

```kotlin
graalvmNative {
    binaries {
        named("main") {
            imageName.set(project.name)
            mainClass.set("com.example.Application")

            // Build arguments
            buildArgs.addAll(
                "--no-fallback",
                "-H:+ReportExceptionStackTraces",
                "--enable-https",
                "-J-Xmx8g"
            )

            // Quick build mode (faster build, slower runtime — dev only)
            quickBuild.set(false)

            // Rich output during build
            richOutput.set(true)

            // Verbose output
            verbose.set(true)

            // Resource includes
            resources {
                autodetect()
                includedPatterns.add("application.*")
                includedPatterns.add("META-INF/.*")
            }
        }
    }

    // GraalVM metadata repository
    metadataRepository {
        enabled.set(true)
        version.set("0.3.14")
    }

    // Toolchain detection
    toolchainDetection.set(true)
}
```

### Java Toolchain Configuration

```kotlin
java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

graalvmNative {
    binaries {
        named("main") {
            javaLauncher.set(javaToolchains.launcherFor {
                languageVersion.set(JavaLanguageVersion.of(21))
                vendor.set(JvmVendorSpec.matching("GraalVM Community"))
            })
        }
    }
}
```

## Spring Boot Gradle Integration

For Spring Boot 3.x projects with Gradle:

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.4.1"
    id("io.spring.dependency-management") version "1.1.7"
    id("org.graalvm.buildtools.native") version "0.10.6"
}

// Spring Boot plugin automatically configures AOT processing
// when GraalVM Native Image plugin is detected
```

Build commands:

```bash
# Compile to native executable
./gradlew nativeCompile

# Build OCI image with Cloud Native Buildpacks
./gradlew bootBuildImage

# Run the native executable
./build/native/nativeCompile/<app-name>

# Run AOT processing only
./gradlew processAot
```

### Custom AOT Configuration

```kotlin
tasks.withType<org.springframework.boot.gradle.tasks.aot.ProcessAot>().configureEach {
    args("--spring.profiles.active=prod")
}

graalvmNative {
    binaries {
        named("main") {
            buildArgs.addAll(
                "--no-fallback",
                "-H:+ReportExceptionStackTraces"
            )
        }
    }
}
```

## Testing in Native Mode

Run JUnit tests compiled as a native executable:

```bash
./gradlew nativeTest
```

Configure test binary:

```kotlin
graalvmNative {
    binaries {
        named("test") {
            buildArgs.addAll(
                "--no-fallback",
                "-H:+ReportExceptionStackTraces"
            )
        }
    }

    // Configure test support
    testSupport.set(true)
}
```

## Multi-Project Builds

For multi-project Gradle builds, apply the plugin only in the executable subproject:

```kotlin
// settings.gradle.kts
pluginManagement {
    plugins {
        id("org.graalvm.buildtools.native") version "0.10.6"
    }
}

// app/build.gradle.kts (executable subproject)
plugins {
    id("org.graalvm.buildtools.native")
}

graalvmNative {
    binaries {
        named("main") {
            imageName.set("my-app")
            mainClass.set("com.example.Application")
        }
    }
}
```
