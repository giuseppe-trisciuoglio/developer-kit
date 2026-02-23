# JSON Serialization Test Examples

## Example 1: `@JsonTest` round-trip with `JacksonTester`

```java
package com.example.json;

import com.fasterxml.jackson.annotation.JsonFormat;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.json.JsonTest;
import org.springframework.boot.test.json.JacksonTester;

import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;

@JsonTest
class InvoiceJsonTest {

    @Autowired
    private JacksonTester<InvoiceDto> json;

    @Test
    void shouldSerializeInvoice() throws Exception {
        InvoiceDto dto = new InvoiceDto("INV-100", LocalDate.of(2026, 2, 23), InvoiceStatus.PAID);

        assertThat(json.write(dto)).extractingJsonPathStringValue("@.invoiceNumber").isEqualTo("INV-100");
        assertThat(json.write(dto)).extractingJsonPathStringValue("@.issuedDate").isEqualTo("2026-02-23");
        assertThat(json.write(dto)).extractingJsonPathStringValue("@.status").isEqualTo("PAID");
    }

    @Test
    void shouldDeserializeInvoice() throws Exception {
        String payload = "{" +
                "\"invoiceNumber\":\"INV-200\"," +
                "\"issuedDate\":\"2026-01-10\"," +
                "\"status\":\"DRAFT\"" +
                "}";

        InvoiceDto dto = json.parseObject(payload);

        assertThat(dto.invoiceNumber()).isEqualTo("INV-200");
        assertThat(dto.issuedDate()).isEqualTo(LocalDate.of(2026, 1, 10));
        assertThat(dto.status()).isEqualTo(InvoiceStatus.DRAFT);
    }

    record InvoiceDto(String invoiceNumber,
                      @JsonFormat(pattern = "yyyy-MM-dd") LocalDate issuedDate,
                      InvoiceStatus status) {
    }

    enum InvoiceStatus {
        DRAFT,
        PAID
    }
}
```

## Example 2: Custom serializer and deserializer with `ObjectMapper`

```java
package com.example.json;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;

class MoneyJsonMappingTest {

    @Test
    void shouldSerializeAndDeserializeMoneyAsDecimalString() throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        SimpleModule module = new SimpleModule();
        module.addSerializer(Money.class, new MoneySerializer());
        module.addDeserializer(Money.class, new MoneyDeserializer());
        mapper.registerModule(module);

        Payment payment = new Payment("ORD-1", new Money(new BigDecimal("12.34")));
        String json = mapper.writeValueAsString(payment);

        assertThat(json).contains("\"amount\":\"12.34\"");

        Payment parsed = mapper.readValue(json, Payment.class);
        assertThat(parsed.amount().value()).isEqualByComparingTo(new BigDecimal("12.34"));
    }

    record Payment(String orderId, @JsonSerialize(using = MoneySerializer.class) @JsonDeserialize(using = MoneyDeserializer.class) Money amount) {
    }

    record Money(BigDecimal value) {
    }

    static class MoneySerializer extends JsonSerializer<Money> {
        @Override
        public void serialize(Money value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
            gen.writeString(value.value().setScale(2).toPlainString());
        }
    }

    static class MoneyDeserializer extends JsonDeserializer<Money> {
        @Override
        public Money deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
            return new Money(new BigDecimal(p.getValueAsString()));
        }
    }
}
```
