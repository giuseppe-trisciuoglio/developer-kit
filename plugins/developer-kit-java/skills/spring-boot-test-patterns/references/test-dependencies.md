# Test Dependencies Setup

## Maven Dependencies

### Basic Testing Setup

```xml
<dependencies>
    <!-- Spring Boot Test Starter (includes JUnit 5, Mockito, AssertJ) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Testcontainers Core -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>1.19.0</version>
        <scope>test</scope>
    </dependency>

    <!-- PostgreSQL Testcontainers -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <version>1.19.0</version>
        <scope>test</scope>
    </dependency>

    <!-- MySQL Testcontainers -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>mysql</artifactId>
        <version>1.19.0</version>
        <scope>test</scope>
    </dependency>

    <!-- Additional Dependencies -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
</dependencies>
```

### Gradle Dependencies

```kotlin
dependencies {
    // Spring Boot Test Starter
    testImplementation("org.springframework.boot:spring-boot-starter-test")

    // Testcontainers
    testImplementation("org.testcontainers:junit-jupiter:1.19.0")
    testImplementation("org.testcontainers:postgresql:1.19.0")

    // Additional Dependencies
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-web")
}
```

## Version Selection

- **Spring Boot 3.x**: Use Testcontainers 1.19.x+
- **Spring Boot 2.x**: Use Testcontainers 1.17.x
- Always check [Testcontainers Documentation](https://www.testcontainers.org/) for latest versions

## Optional Testing Dependencies

### H2 In-Memory Database

```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
</dependency>
```

### WireMock for HTTP Mocking

```xml
<dependency>
    <groupId>org.wiremock</groupId>
    <artifactId>wiremock-standalone</artifactId>
    <version>3.5.2</version>
    <scope>test</scope>
</dependency>
```

### Awaitility for Async Testing

```xml
<dependency>
    <groupId>org.awaitility</groupId>
    <artifactId>awaitility</artifactId>
    <version>4.2.0</version>
    <scope>test</scope>
</dependency>
```
