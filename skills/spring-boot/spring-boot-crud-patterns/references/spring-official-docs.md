# Spring Official Documentation Excerpts

Curated excerpts sourced from Spring guides and reference documentation relevant to CRUD service design.

## Spring Guide: Building a RESTful Web Service
- **Source**: https://spring.io/guides/gs/rest-service
- **Focus**: Minimal Spring Boot REST controller and application bootstrap.

```java
package com.example.restservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class RestServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(RestServiceApplication.class, args);
    }
}
```

## Spring Guide: Running Executable JARs
- **Source**: https://spring.io/guides/gs/rest-service
- **Focus**: Build and run workflow for shipping a CRUD service as a standalone artifact.

```bash
./mvnw clean package
java -jar target/gs-rest-service-0.1.0.jar

./gradlew build
java -jar build/libs/gs-rest-service-0.1.0.jar
```

## Spring Guide: Reactive REST Testing with WebTestClient
- **Source**: https://spring.io/guides/gs/reactive-rest-service
- **Focus**: Example of validating REST endpoints with WebTestClient and AssertJ.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GreetingRouterTest {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void testHello() {
        webTestClient.get()
            .uri("/hello")
            .exchange()
            .expectStatus().isOk()
            .expectBody(Greeting.class)
            .value(greeting -> assertThat(greeting.getMessage()).isEqualTo("Hello, Spring!"));
    }
}
```

## Spring Boot Reference: JPA Configuration
- **Source**: https://github.com/spring-projects/spring-boot/blob/main/documentation/spring-boot-docs/src/docs/antora/modules/how-to/pages/data-access.adoc
- **Focus**: Common configuration flags for Hibernate DDL and SQL logging.

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: update
      naming:
        physical-strategy: "com.example.MyPhysicalNamingStrategy"
    show-sql: true
    properties:
      hibernate:
        globally_quoted_identifiers: true
```

