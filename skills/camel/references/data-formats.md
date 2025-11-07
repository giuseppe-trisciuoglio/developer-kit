# Data Formats and Transformation

Apache Camel supports numerous data formats for message transformation. This guide covers the most common formats and best practices.

## JSON

### Jackson (Recommended)

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jackson-starter</artifactId>
</dependency>
```

**Marshal/Unmarshal:**
```java
// Unmarshal JSON to POJO
from("kafka:orders")
    .unmarshal().json(JsonLibrary.Jackson, Order.class)
    .to("direct:process");

// Marshal POJO to JSON
from("direct:response")
    .marshal().json(JsonLibrary.Jackson)
    .to("kafka:responses");

// Pretty print
from("direct:pretty")
    .marshal().json(JsonLibrary.Jackson, true)
    .to("file:/data/output");
```

**Configuration:**
```java
@Bean
public JacksonDataFormat jacksonDataFormat() {
    JacksonDataFormat format = new JacksonDataFormat();
    format.setPrettyPrint(true);
    format.setInclude("NON_NULL");
    format.setUnmarshalType(Order.class);
    return format;
}

// In route
from("kafka:orders")
    .unmarshal(jacksonDataFormat())
    .to("direct:process");
```

**Custom ObjectMapper:**
```java
@Bean
public ObjectMapper customObjectMapper() {
    ObjectMapper mapper = new ObjectMapper();
    mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    mapper.registerModule(new JavaTimeModule());
    return mapper;
}

@Bean
public JacksonDataFormat jacksonFormat(ObjectMapper objectMapper) {
    JacksonDataFormat format = new JacksonDataFormat();
    format.setObjectMapper(objectMapper);
    return format;
}
```

### Gson

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-gson-starter</artifactId>
</dependency>
```

```java
from("kafka:events")
    .unmarshal().json(JsonLibrary.Gson, Event.class)
    .to("direct:process");
```

## XML

### Jackson XML

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jacksonxml-starter</artifactId>
</dependency>
```

```java
from("file:/data/xml")
    .unmarshal().jacksonXml(Order.class)
    .to("direct:process")
    .marshal().jacksonXml()
    .to("file:/data/output");
```

### JAXB

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-jaxb-starter</artifactId>
</dependency>
```

**Model:**
```java
@XmlRootElement(name = "order")
@XmlAccessorType(XmlAccessType.FIELD)
public class Order {
    @XmlElement
    private String id;

    @XmlElement
    private Double amount;

    @XmlElement
    private LocalDateTime createdAt;

    // Getters and setters
}
```

**Route:**
```java
from("file:/data/xml")
    .unmarshal().jaxb(Order.class)
    .to("direct:process")
    .marshal().jaxb()
    .to("file:/data/output");
```

**Custom JAXB Context:**
```java
@Bean
public JaxbDataFormat jaxbFormat() {
    JaxbDataFormat format = new JaxbDataFormat();
    format.setContextPath("com.example.model");
    format.setPrettyPrint(true);
    format.setEncoding("UTF-8");
    return format;
}
```

## CSV

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-csv-starter</artifactId>
</dependency>
```

### Basic CSV

```java
from("file:/data/csv?noop=true")
    .unmarshal().csv()
    .split(body())
        .process(exchange -> {
            @SuppressWarnings("unchecked")
            List<String> row = exchange.getIn().getBody(List.class);
            log.info("Row: {}", row);
        })
    .end();
```

### CSV with Headers

```java
CsvDataFormat csv = new CsvDataFormat();
csv.setUseMaps(true); // Use maps instead of lists
csv.setDelimiter(',');
csv.setQuoteDisabled(false);

from("file:/data/csv")
    .unmarshal(csv)
    .split(body())
        .process(exchange -> {
            @SuppressWarnings("unchecked")
            Map<String, String> row = exchange.getIn().getBody(Map.class);
            String name = row.get("name");
            String email = row.get("email");
        })
    .end();
```

### CSV to POJO

```java
@CsvRecord(separator = ",")
public class Customer {
    @DataField(pos = 1)
    private String id;

    @DataField(pos = 2)
    private String name;

    @DataField(pos = 3, pattern = "yyyy-MM-dd")
    private Date birthDate;

    // Getters and setters
}

from("file:/data/customers.csv")
    .unmarshal().bindy(BindyType.Csv, Customer.class)
    .split(body())
        .to("jpa:com.example.model.Customer")
    .end();
```

## Avro

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-avro-starter</artifactId>
</dependency>
```

**Schema (order.avsc):**
```json
{
  "type": "record",
  "name": "Order",
  "namespace": "com.example.avro",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "customerId", "type": "string"}
  ]
}
```

**Route:**
```java
from("kafka:orders")
    .unmarshal().avro("com.example.avro.Order")
    .to("direct:process")
    .marshal().avro()
    .to("kafka:processed-orders");
```

## Protobuf

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-protobuf-starter</artifactId>
</dependency>
```

**Proto Definition:**
```protobuf
syntax = "proto3";

package com.example.proto;

message Order {
  string id = 1;
  double amount = 2;
  string customer_id = 3;
}
```

**Route:**
```java
from("kafka:orders")
    .unmarshal().protobuf(OrderProto.Order.class)
    .to("direct:process")
    .marshal().protobuf()
    .to("kafka:processed-orders");
```

## YAML

**Dependencies:**
```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-snakeyaml-starter</artifactId>
</dependency>
```

```java
from("file:/data/yaml")
    .unmarshal().yaml(YAMLLibrary.SnakeYAML, Config.class)
    .to("direct:process");

from("direct:config")
    .marshal().yaml(YAMLLibrary.SnakeYAML)
    .to("file:/data/output");
```

## Base64

```java
from("direct:encode")
    .marshal().base64()
    .to("jms:queue:encoded");

from("jms:queue:encoded")
    .unmarshal().base64()
    .to("direct:process");
```

## Compression

### GZip

```java
from("file:/data/input")
    .marshal().gzipDeflater()
    .to("file:/data/compressed");

from("file:/data/compressed")
    .unmarshal().gzipDeflater()
    .to("direct:process");
```

### Zip

```java
from("file:/data/input?noop=true")
    .marshal().zipFile()
    .to("file:/data/archive");

from("file:/data/archive?noop=true")
    .unmarshal().zipFile()
    .to("direct:process");
```

## Custom Data Formats

### Implementing Custom Format

```java
public class CustomDataFormat implements DataFormat {

    @Override
    public void marshal(Exchange exchange, Object graph, OutputStream stream)
            throws Exception {
        String data = convertToCustomFormat(graph);
        stream.write(data.getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public Object unmarshal(Exchange exchange, InputStream stream)
            throws Exception {
        String data = new String(stream.readAllBytes(), StandardCharsets.UTF_8);
        return parseCustomFormat(data);
    }

    private String convertToCustomFormat(Object object) {
        // Custom serialization logic
        return object.toString();
    }

    private Object parseCustomFormat(String data) {
        // Custom deserialization logic
        return data;
    }
}
```

**Usage:**
```java
@Bean
public CustomDataFormat customFormat() {
    return new CustomDataFormat();
}

from("direct:custom")
    .marshal(customFormat())
    .to("file:/data/output");
```

## Content Type Conversion

### Type Converter

```java
from("file:/data/input")
    .convertBodyTo(String.class)
    .to("direct:process");

from("direct:bytes")
    .convertBodyTo(byte[].class)
    .to("file:/data/output");

from("direct:stream")
    .convertBodyTo(InputStream.class)
    .to("http://upload-service");
```

### Custom Type Converter

```java
@Converter
public class OrderConverter {

    @Converter
    public static Order toOrder(String text) {
        // Parse text to Order
        return new Order();
    }

    @Converter
    public static String fromOrder(Order order) {
        // Convert Order to text
        return order.toString();
    }
}
```

**Register:**
```java
@Configuration
public class ConverterConfig {

    @Bean
    public TypeConverters orderTypeConverter() {
        return new OrderConverter();
    }
}
```

## Data Format Best Practices

### 1. Choose Appropriate Format

| Format | Use Case | Pros | Cons |
|--------|----------|------|------|
| JSON | REST APIs, web services | Human-readable, widely supported | Larger size |
| Avro | Kafka, data streaming | Compact, schema evolution | Binary format |
| Protobuf | Microservices, gRPC | Very compact, fast | Requires schema |
| CSV | Data exports, reporting | Simple, Excel compatible | Limited data types |
| XML | Legacy systems, SOAP | Structured, self-describing | Verbose |

### 2. Configure for Performance

```java
// Jackson: Disable features for better performance
ObjectMapper mapper = new ObjectMapper();
mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
mapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, true);

// Reuse data format instances
@Bean
public JacksonDataFormat orderFormat() {
    JacksonDataFormat format = new JacksonDataFormat(Order.class);
    format.setObjectMapper(mapper);
    return format;
}
```

### 3. Handle Errors Gracefully

```java
onException(JsonProcessingException.class)
    .handled(true)
    .log(LoggingLevel.ERROR, "JSON parsing failed: ${exception.message}")
    .setBody(simple("${body}")) // Keep original body
    .to("jms:queue:parse-errors");

from("kafka:orders")
    .doTry()
        .unmarshal().json(JsonLibrary.Jackson, Order.class)
        .to("direct:process")
    .doCatch(Exception.class)
        .log("Failed to parse order: ${exception.message}")
        .to("direct:error-handler")
    .end();
```

### 4. Validate After Unmarshalling

```java
from("kafka:orders")
    .unmarshal().json(JsonLibrary.Jackson, Order.class)
    .to("bean-validator://validate")
    .to("direct:process");
```

### 5. Use Streaming for Large Files

```java
from("file:/data/large-files")
    .split(body().tokenize("\n"))
        .streaming()
        .unmarshal().json(JsonLibrary.Jackson, Record.class)
        .to("direct:process-record")
    .end();
```

### 6. Compression for Large Payloads

```java
from("direct:large-payload")
    .marshal().gzipDeflater()
    .to("kafka:compressed-data");

from("kafka:compressed-data")
    .unmarshal().gzipDeflater()
    .unmarshal().json(JsonLibrary.Jackson, Data.class)
    .to("direct:process");
```

## Data Transformation Patterns

### Pattern: Format Translation

```java
from("file:/data/xml")
    .unmarshal().jacksonXml(Order.class)
    .marshal().json(JsonLibrary.Jackson)
    .to("kafka:orders-json");
```

### Pattern: Enrichment During Transformation

```java
from("kafka:raw-orders")
    .unmarshal().json(JsonLibrary.Jackson, RawOrder.class)
    .enrich("direct:lookup-customer", (original, resource) -> {
        RawOrder order = original.getIn().getBody(RawOrder.class);
        Customer customer = resource.getIn().getBody(Customer.class);

        EnrichedOrder enriched = new EnrichedOrder(order, customer);
        original.getIn().setBody(enriched);
        return original;
    })
    .marshal().json(JsonLibrary.Jackson)
    .to("kafka:enriched-orders");
```

### Pattern: Conditional Formatting

```java
from("direct:format")
    .choice()
        .when(header("format").isEqualTo("xml"))
            .marshal().jacksonXml()
        .when(header("format").isEqualTo("json"))
            .marshal().json(JsonLibrary.Jackson)
        .when(header("format").isEqualTo("csv"))
            .marshal().csv()
        .otherwise()
            .marshal().string()
    .end()
    .to("direct:output");
```

## References

- [Camel Data Formats](https://camel.apache.org/components/latest/dataformats/)
- [Jackson Documentation](https://github.com/FasterXML/jackson-docs)
- [Apache Avro](https://avro.apache.org/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
