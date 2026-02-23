# Utility Methods Test Examples (JUnit 5)

Each class below is self-contained and runnable with JUnit 5. Static utility methods are included as nested classes to keep examples portable.

## Example 1: String utility static methods

```java
package com.example.util;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

class StringUtilsTest {

    @Test
    void capitalizeReturnsCapitalizedValue() {
        assertEquals("Hello", StringUtils.capitalize("hello"));
    }

    @Test
    void capitalizeReturnsInputForNullOrBlank() {
        assertNull(StringUtils.capitalize(null));
        assertEquals("", StringUtils.capitalize(""));
        assertEquals("   ", StringUtils.capitalize("   "));
    }

    static final class StringUtils {
        private StringUtils() {
        }

        static String capitalize(String value) {
            if (value == null || value.isBlank()) {
                return value;
            }
            return value.substring(0, 1).toUpperCase() + value.substring(1);
        }
    }
}
```

## Example 2: Number helper static methods

```java
package com.example.util;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class NumberUtilsTest {

    @Test
    void percentageHandlesNormalAndZeroTotal() {
        assertEquals(12.5, NumberUtils.percentage(25.0, 200.0));
        assertEquals(0.0, NumberUtils.percentage(10.0, 0.0));
    }

    @Test
    void requireInRangeThrowsForOutOfRangeValues() {
        IllegalArgumentException ex = assertThrows(
                IllegalArgumentException.class,
                () -> NumberUtils.requireInRange(11, 0, 10)
        );
        assertEquals("value must be between 0 and 10", ex.getMessage());
    }

    static final class NumberUtils {
        private NumberUtils() {
        }

        static double percentage(double value, double total) {
            if (total == 0.0) {
                return 0.0;
            }
            return (value / total) * 100.0;
        }

        static int requireInRange(int value, int min, int max) {
            if (value < min || value > max) {
                throw new IllegalArgumentException("value must be between " + min + " and " + max);
            }
            return value;
        }
    }
}
```

## Example 3: Date utility static methods

```java
package com.example.util;

import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DateUtilsTest {

    private static final Clock FIXED_CLOCK = Clock.fixed(
            Instant.parse("2025-01-10T12:00:00Z"),
            ZoneOffset.UTC
    );

    @Test
    void daysUntilReturnsPositiveDays() {
        LocalDate start = LocalDate.of(2025, 1, 10);
        LocalDate end = LocalDate.of(2025, 1, 15);

        assertEquals(5, DateUtils.daysUntil(start, end));
    }

    @Test
    void isPastUsesInjectedClockForDeterministicTests() {
        assertTrue(DateUtils.isPast(LocalDate.of(2025, 1, 9), FIXED_CLOCK));
    }

    static final class DateUtils {
        private DateUtils() {
        }

        static long daysUntil(LocalDate from, LocalDate to) {
            return to.toEpochDay() - from.toEpochDay();
        }

        static boolean isPast(LocalDate value, Clock clock) {
            return value.isBefore(LocalDate.now(clock));
        }
    }
}
```

## Example 4: Email validator helper static methods

```java
package com.example.util;

import org.junit.jupiter.api.Test;

import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class EmailValidatorTest {

    @Test
    void isValidReturnsTrueForWellFormedEmail() {
        assertTrue(EmailValidator.isValid("dev@example.com"));
    }

    @Test
    void isValidReturnsFalseForNullOrMalformedEmail() {
        assertFalse(EmailValidator.isValid(null));
        assertFalse(EmailValidator.isValid("invalid-email"));
        assertFalse(EmailValidator.isValid("dev@"));
    }

    static final class EmailValidator {
        private static final Pattern SIMPLE_EMAIL =
                Pattern.compile("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$");

        private EmailValidator() {
        }

        static boolean isValid(String email) {
            return email != null && SIMPLE_EMAIL.matcher(email).matches();
        }
    }
}
```

## Example 5: Collection helper static methods

```java
package com.example.util;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

class CollectionUtilsTest {

    @Test
    void firstOrNullReturnsFirstElementOrNull() {
        assertEquals("a", CollectionUtils.firstOrNull(List.of("a", "b")));
        assertNull(CollectionUtils.firstOrNull(List.of()));
        assertNull(CollectionUtils.firstOrNull(null));
    }

    @Test
    void deduplicatePreservesEncounterOrder() {
        assertEquals(List.of("a", "b", "c"), CollectionUtils.deduplicate(List.of("a", "b", "a", "c", "b")));
    }

    static final class CollectionUtils {
        private CollectionUtils() {
        }

        static <T> T firstOrNull(List<T> values) {
            if (values == null || values.isEmpty()) {
                return null;
            }
            return values.get(0);
        }

        static <T> List<T> deduplicate(List<T> values) {
            if (values == null) {
                return List.of();
            }
            Set<T> set = new LinkedHashSet<>(values);
            return new ArrayList<>(set);
        }
    }
}
```
