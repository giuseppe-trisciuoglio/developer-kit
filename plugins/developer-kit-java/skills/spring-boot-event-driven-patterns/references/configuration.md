# Event-Driven Architecture Configuration

## Basic Configuration

### application.properties

```properties
# Server Configuration
server.port=8080

# Kafka Configuration
spring.kafka.bootstrap-servers=localhost:9092
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer

# Spring Cloud Stream Configuration
spring.cloud.stream.kafka.binder.brokers=localhost:9092
```

### application.yml

```yaml
server:
  port: 8080

spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "*"

  cloud:
    stream:
      kafka:
        binder:
          brokers: localhost:9092
      bindings:
        productCreated-in-0:
          destination: product-events
          group: order-service
```

## Advanced Configuration

### Kafka Producer Configuration

```yaml
spring:
  kafka:
    producer:
      acks: all
      retries: 3
      properties:
        retry.backoff.ms: 1000
      enable.idempotence: true
      compression-type: snappy
```

### Kafka Consumer Configuration

```yaml
spring:
  kafka:
    consumer:
      auto-offset-reset: earliest
      enable-auto-commit: false
      max-poll-records: 100
    listener:
      ack-mode: manual_immediate
```

### Error Handling Configuration

```yaml
spring:
  kafka:
    producer:
      properties:
        retries: 3
        retry.backoff.ms: 1000
    consumer:
      properties:
        max.poll.interval.ms: 300000
```

## Spring Cloud Stream Bindings

### Producer Binding

```yaml
spring:
  cloud:
    stream:
      bindings:
        productCreated-out-0:
          destination: product-events
          producer:
            partition-count: 3
```

### Consumer Binding

```yaml
spring:
  cloud:
    stream:
      bindings:
        productCreated-in-0:
          destination: product-events
          group: order-service
          consumer:
            max-attempts: 3
            back-off-initial-interval: 1000
```

## Environment-Specific Configuration

### Development

```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
```

### Production

```yaml
spring:
  kafka:
    bootstrap-servers: kafka1.prod.example.com:9092,kafka2.prod.example.com:9092,kafka3.prod.example.com:9092
    properties:
      security.protocol: SSL
      ssl.truststore.location: /etc/kafka/truststore.jks
      ssl.keystore.location: /etc/kafka/keystore.jks
```
