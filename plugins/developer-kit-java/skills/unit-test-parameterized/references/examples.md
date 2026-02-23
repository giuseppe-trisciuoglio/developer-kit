# Parameterized Test Examples

## Example 1: `@ValueSource` for simple scalar inputs

```java
package com.example.param;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.assertj.core.api.Assertions.assertThat;

class StringNormalizerTest {

    @ParameterizedTest(name = "should trim and lowercase: {0}")
    @ValueSource(strings = {" Alice ", "BOB", "  carol"})
    void shouldNormalizeNames(String input) {
        String result = normalize(input);
        assertThat(result).isEqualTo(input.trim().toLowerCase());
    }

    private String normalize(String value) {
        return value == null ? null : value.trim().toLowerCase();
    }
}
```

## Example 2: `@CsvSource` for input-output pairs

```java
package com.example.param;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.assertj.core.api.Assertions.assertThat;

class TaxCalculatorTest {

    @ParameterizedTest(name = "net={0}, rate={1}, expected={2}")
    @CsvSource({
            "100.00, 0.10, 10.00",
            "80.00, 0.20, 16.00",
            "15.50, 0.05, 0.78"
    })
    void shouldComputeTax(String netAmount, String rate, String expectedTax) {
        String tax = calculateTax(netAmount, rate);
        assertThat(tax).isEqualTo(expectedTax);
    }

    private String calculateTax(String netAmount, String rate) {
        java.math.BigDecimal net = new java.math.BigDecimal(netAmount);
        java.math.BigDecimal percent = new java.math.BigDecimal(rate);
        return net.multiply(percent).setScale(2, java.math.RoundingMode.HALF_UP).toPlainString();
    }
}
```

## Example 3: `@MethodSource` for complex objects

```java
package com.example.param;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;

class ShippingPolicyTest {

    @ParameterizedTest(name = "{0}")
    @MethodSource("shippingCases")
    void shouldResolveShippingTier(String caseName, Order order, ShippingTier expectedTier) {
        ShippingTier tier = resolveTier(order);
        assertThat(tier).isEqualTo(expectedTier);
    }

    static Stream<Arguments> shippingCases() {
        return Stream.of(
                Arguments.of("small standard order", new Order(20.0, false), ShippingTier.STANDARD),
                Arguments.of("large order free express", new Order(250.0, true), ShippingTier.EXPRESS),
                Arguments.of("large non-priority order", new Order(250.0, false), ShippingTier.STANDARD)
        );
    }

    private ShippingTier resolveTier(Order order) {
        if (order.priority() && order.total() >= 200.0) {
            return ShippingTier.EXPRESS;
        }
        return ShippingTier.STANDARD;
    }

    record Order(double total, boolean priority) {
    }

    enum ShippingTier {
        STANDARD,
        EXPRESS
    }
}
```

## Example 4: `@EnumSource` for all enum states

```java
package com.example.param;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

import static org.assertj.core.api.Assertions.assertThat;

class WorkflowStateTest {

    @ParameterizedTest
    @EnumSource(WorkflowStatus.class)
    void shouldExposeDisplayLabel(WorkflowStatus status) {
        assertThat(status.displayLabel()).isNotBlank();
    }

    enum WorkflowStatus {
        NEW("New"),
        RUNNING("Running"),
        DONE("Done"),
        FAILED("Failed");

        private final String displayLabel;

        WorkflowStatus(String displayLabel) {
            this.displayLabel = displayLabel;
        }

        String displayLabel() {
            return displayLabel;
        }
    }
}
```
