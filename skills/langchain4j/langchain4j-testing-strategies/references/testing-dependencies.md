# Testing Dependencies

## Maven Configuration

```xml
<dependencies>
    <!-- Core LangChain4J -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j</artifactId>
    </dependency>

    <!-- Testing utilities -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-test</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Testcontainers for integration tests -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers-bom</artifactId>
        <version>${testcontainers.version}</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Ollama for local testing -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-ollama</artifactId>
        <version>${langchain4j.version}</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>ollama</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Additional test dependencies -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.9.3</version>
        <scope>test</scope>
    </dependency>

    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>5.3.1</version>
        <scope>test</scope>
    </dependency>

    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.24.1</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

## Gradle Configuration

```gradle
dependencies {
    // Core LangChain4J
    implementation "dev.langchain4j:langchain4j:${langchain4jVersion}"

    // Testing utilities
    testImplementation "dev.langchain4j:langchain4j-test"

    // Testcontainers
    testImplementation "org.testcontainers:junit-jupiter"
    testImplementation "org.testcontainers:ollama"

    // Ollama for local testing
    testImplementation "dev.langchain4j:langchain4j-ollama:${langchain4jVersion}"

    // Additional test dependencies
    testImplementation "org.junit.jupiter:junit-jupiter:5.9.3"
    testImplementation "org.mockito:mockito-core:5.3.1"
    testImplementation "org.assertj:assertj-core:3.24.1"
}
```

## Test Configuration Properties

```properties
# application-test.properties
spring.profiles.active=test
langchain4j.ollama.base-url=http://localhost:11434
langchain4j.openai.api-key=test-key
langchain4j.openai.model-name=gpt-4.1
```