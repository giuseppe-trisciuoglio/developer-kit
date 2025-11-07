# Camel Components Reference

Apache Camel provides 280+ components for integrating with various systems and protocols. This reference covers the most commonly used components in Spring Boot applications.

## Messaging Components

### JMS (Java Message Service)

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jms-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-artemis</artifactId>
</dependency>
```

**URI Syntax:**
```
jms:[queue|topic]:destinationName[?options]
```

**Examples:**
```java
// Producer
from("direct:send")
    .to("jms:queue:orders");

// Consumer
from("jms:queue:orders?concurrentConsumers=5")
    .to("direct:process");

// Request-Reply
from("direct:request")
    .to("jms:queue:request-queue?replyTo=response-queue&requestTimeout=5000");
```

**Configuration:**
```yaml
spring:
  artemis:
    mode: embedded
    broker-url: tcp://localhost:61616
    user: admin
    password: admin

camel:
  component:
    jms:
      connection-factory: jmsConnectionFactory
      concurrent-consumers: 10
      max-concurrent-consumers: 20
```

### Kafka

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-kafka-starter</artifactId>
</dependency>
```

**URI Syntax:**
```
kafka:topic[?options]
```

**Examples:**
```java
// Producer
from("direct:publish")
    .to("kafka:events?brokers=localhost:9092");

// Consumer
from("kafka:orders?brokers=localhost:9092&groupId=order-processor&autoOffsetReset=earliest")
    .to("direct:process");

// With headers and key
from("direct:publish")
    .setHeader(KafkaConstants.KEY, simple("${body.id}"))
    .setHeader(KafkaConstants.PARTITION_KEY, constant(0))
    .to("kafka:orders?brokers=localhost:9092");
```

**Configuration:**
```yaml
camel:
  component:
    kafka:
      brokers: localhost:9092
      auto-offset-reset: earliest
      group-id: my-consumer-group
      enable-auto-commit: false
      session-timeout-ms: 30000
```

### AMQP (RabbitMQ)

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-spring-rabbitmq-starter</artifactId>
</dependency>
```

**URI Syntax:**
```
spring-rabbitmq:exchangeName[?options]
```

**Examples:**
```java
from("direct:send")
    .to("spring-rabbitmq:orders?routingKey=new-order");

from("spring-rabbitmq:orders?queues=order-queue&concurrentConsumers=5")
    .to("direct:process");
```

## HTTP/REST Components

### HTTP Client

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-http-starter</artifactId>
</dependency>
```

**URI Syntax:**
```
http://hostname[:port][/path][?options]
```

**Examples:**
```java
// GET request
from("direct:fetch")
    .to("http://api.example.com/users/${header.userId}");

// POST with JSON body
from("direct:create")
    .setHeader(Exchange.HTTP_METHOD, constant("POST"))
    .setHeader(Exchange.CONTENT_TYPE, constant("application/json"))
    .marshal().json()
    .to("http://api.example.com/users");

// With authentication
from("direct:secure")
    .to("http://api.example.com/data?authUsername=user&authPassword=pass&authMethod=Basic");
```

### REST DSL

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-servlet-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jackson-starter</artifactId>
</dependency>
```

**Examples:**
```java
@Override
public void configure() {
    restConfiguration()
        .component("servlet")
        .bindingMode(RestBindingMode.json)
        .dataFormatProperty("prettyPrint", "true")
        .contextPath("/api")
        .port(8080);

    rest("/users")
        .get("/{id}")
            .to("direct:getUser")
        .post()
            .type(User.class)
            .to("direct:createUser")
        .put("/{id}")
            .type(User.class)
            .to("direct:updateUser")
        .delete("/{id}")
            .to("direct:deleteUser");
}
```

**Configuration:**
```yaml
camel:
  servlet:
    mapping:
      context-path: /api/*
```

## Database Components

### SQL Component

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-sql-starter</artifactId>
</dependency>
```

**URI Syntax:**
```
sql:select * from table where id=:#id[?options]
```

**Examples:**
```java
// Query
from("direct:query")
    .to("sql:SELECT * FROM orders WHERE customer_id = :#${body.customerId}")
    .to("direct:process-results");

// Insert
from("direct:insert")
    .to("sql:INSERT INTO orders (id, amount, status) VALUES (:#${body.id}, :#${body.amount}, 'NEW')");

// Polling consumer
from("sql:SELECT * FROM orders WHERE status = 'PENDING'?delay=5000&onConsume=UPDATE orders SET status='PROCESSING' WHERE id=:#id")
    .to("direct:process-order");
```

### JPA Component

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jpa-starter</artifactId>
</dependency>
```

**Examples:**
```java
// Persist entity
from("direct:save")
    .to("jpa:com.example.Order");

// Query with JPQL
from("direct:find-orders")
    .to("jpa:com.example.Order?query=SELECT o FROM Order o WHERE o.status = 'PENDING'");

// Polling consumer
from("jpa:com.example.Order?consumeDelete=false&delay=5000&query=SELECT o FROM Order o WHERE o.status = 'NEW'")
    .to("direct:process-order");
```

## File Components

### File Component

**URI Syntax:**
```
file:directoryName[?options]
```

**Examples:**
```java
// Read files
from("file:/data/input?noop=true&include=.*\\.csv$")
    .to("direct:process");

// Write files
from("direct:export")
    .to("file:/data/output?fileName=${header.orderId}.json");

// Move processed files
from("file:/data/input?move=.done&moveFailed=.error")
    .to("direct:process");

// Read and delete
from("file:/data/temp?delete=true")
    .to("direct:cleanup");
```

**Configuration:**
```yaml
camel:
  component:
    file:
      auto-create: true
```

### FTP/SFTP Components

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-ftp-starter</artifactId>
</dependency>
```

**Examples:**
```java
// FTP consumer
from("ftp://user@ftp.example.com/orders?password=secret&delay=60000")
    .to("direct:process");

// SFTP producer
from("direct:upload")
    .to("sftp://user@sftp.example.com/uploads?privateKeyFile=/path/to/key&passphrase=secret");
```

## Cloud and Integration Components

### AWS S3

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-aws2-s3-starter</artifactId>
</dependency>
```

**Examples:**
```java
from("direct:upload")
    .to("aws2-s3://my-bucket?accessKey={{aws.accessKey}}&secretKey={{aws.secretKey}}&region=us-east-1");

from("aws2-s3://my-bucket?accessKey={{aws.accessKey}}&secretKey={{aws.secretKey}}&delay=5000&deleteAfterRead=false")
    .to("direct:process");
```

### AWS SQS

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-aws2-sqs-starter</artifactId>
</dependency>
```

**Examples:**
```java
from("direct:send")
    .to("aws2-sqs://my-queue?accessKey={{aws.accessKey}}&secretKey={{aws.secretKey}}&region=us-east-1");

from("aws2-sqs://my-queue?accessKey={{aws.accessKey}}&secretKey={{aws.secretKey}}&delay=1000&maxMessagesPerPoll=10")
    .to("direct:process");
```

### MongoDB

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-mongodb-starter</artifactId>
</dependency>
```

**Examples:**
```java
// Insert
from("direct:save")
    .to("mongodb:myDb?database=orders&collection=orders&operation=insert");

// Find
from("direct:find")
    .to("mongodb:myDb?database=orders&collection=orders&operation=findAll");

// Tailable cursor (change stream)
from("mongodb:myDb?database=orders&collection=orders&tailTrackIncreasingField=timestamp")
    .to("direct:process-changes");
```

## Data Format Components

### JSON (Jackson)

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jackson-starter</artifactId>
</dependency>
```

**Examples:**
```java
from("direct:json")
    .unmarshal().json(JsonLibrary.Jackson, Order.class)
    .process(exchange -> {
        Order order = exchange.getIn().getBody(Order.class);
        // Process order
    })
    .marshal().json(JsonLibrary.Jackson)
    .to("jms:queue:orders");
```

### XML

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jacksonxml-starter</artifactId>
</dependency>
```

**Examples:**
```java
from("direct:xml")
    .unmarshal().jacksonXml(Order.class)
    .to("direct:process")
    .marshal().jacksonXml()
    .to("file:/data/output");
```

### CSV

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-csv-starter</artifactId>
</dependency>
```

**Examples:**
```java
from("file:/data/csv?noop=true")
    .unmarshal().csv()
    .split(body())
    .to("direct:process-row");
```

## Scheduling Components

### Timer

**URI Syntax:**
```
timer:name[?options]
```

**Examples:**
```java
// Fire every 5 seconds
from("timer:myTimer?period=5000")
    .to("direct:scheduled-task");

// Fire once after delay
from("timer:oneTime?repeatCount=1&delay=10000")
    .to("direct:startup-task");
```

### Quartz

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-quartz-starter</artifactId>
</dependency>
```

**Examples:**
```java
// Cron expression: every day at 2 AM
from("quartz:myJob?cron=0+0+2+*+*+?")
    .to("direct:daily-batch");

// Simple schedule
from("quartz:myTimer?trigger.repeatInterval=30000&trigger.repeatCount=-1")
    .to("direct:periodic-task");
```

## Internal Components

### Direct

Routes within the same CamelContext (synchronous).

```java
from("direct:start")
    .to("direct:process");

from("direct:process")
    .to("log:processing");
```

### SEDA (Staged Event-Driven Architecture)

Asynchronous routing within the same CamelContext using queues.

```java
from("direct:async")
    .to("seda:queue?concurrentConsumers=5");

from("seda:queue")
    .to("direct:process");
```

### VM

Similar to SEDA but can work across multiple CamelContexts in the same JVM.

```java
from("vm:shared-queue?concurrentConsumers=3")
    .to("direct:process");
```

## Validation and Transformation

### Bean Component

Invoke Spring beans for processing.

```java
from("direct:process")
    .bean(OrderService.class, "processOrder")
    .to("jms:queue:processed");
```

### Validator

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-bean-validator-starter</artifactId>
</dependency>
```

```java
from("direct:validate")
    .to("bean-validator://validate")
    .to("direct:process");
```

## Monitoring Components

### Micrometer

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-micrometer-starter</artifactId>
</dependency>
```

**Examples:**
```java
from("direct:metered")
    .to("micrometer:counter:order.received")
    .to("direct:process")
    .to("micrometer:timer:order.processing.time");
```

## Component Selection Guidelines

1. **Messaging**: Choose based on existing infrastructure (Kafka for event streaming, JMS for reliable messaging, RabbitMQ for flexible routing)
2. **HTTP**: Use `http` component for external APIs, REST DSL for exposing endpoints
3. **Database**: JPA for ORM operations, SQL for direct queries and batch operations
4. **Files**: File component for local filesystem, FTP/SFTP for remote systems, S3 for cloud storage
5. **Scheduling**: Timer for simple periodic tasks, Quartz for complex cron-based scheduling
6. **Internal Routing**: Direct for synchronous, SEDA for asynchronous within same context

## Common Configuration Patterns

### Component-Level Configuration

```yaml
camel:
  component:
    kafka:
      brokers: localhost:9092
      auto-offset-reset: earliest
    http:
      connection-timeout: 5000
      socket-timeout: 30000
```

### Endpoint-Level Configuration

```java
from("kafka:orders?brokers=${kafka.brokers}&groupId=${kafka.groupId}&autoOffsetReset=earliest")
    .to("direct:process");
```

### Property Placeholders

```java
from("{{source.endpoint}}")
    .to("{{target.endpoint}}");
```

```yaml
source:
  endpoint: jms:queue:input
target:
  endpoint: kafka:output
```

## References

- [Camel Components List](https://camel.apache.org/components/latest/)
- [Spring Boot Starters](https://camel.apache.org/camel-spring-boot/latest/)
