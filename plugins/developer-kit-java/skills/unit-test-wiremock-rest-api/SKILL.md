---
name: unit-test-wiremock-rest-api
description: Provides patterns for unit testing external REST APIs using WireMock to mock HTTP endpoints. Use when testing service integrations with external APIs.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing REST APIs with WireMock

## Overview

This skill defines deterministic outbound HTTP client tests using WireMock.
It validates request contracts and error handling without calling real external services.

## When to Use

Use this skill when:
- Testing service classes that call third-party REST APIs
- Verifying outbound method, path, headers, and body
- Testing 4xx/5xx response handling and fallback behavior
- Running stable API integration tests in CI

Trigger phrases:
- "wiremock test"
- "mock external api"
- "test rest client error handling"
- "verify outbound request"

## Instructions

1. Add WireMock dependency and use JUnit 5 extension support.
2. Start WireMock with dynamic port using `WireMockExtension`.
3. Inject `wireMock.getRuntimeInfo().getHttpBaseUrl()` into the client under test.
4. Define stubs with explicit method, path, status, and payload.
5. Execute client method and assert mapped result or domain exception.
6. Verify request details using `verify(...)` with matchers.

## Examples

```java
@Test
void shouldCallExternalEndpoint() {
  stubFor(get(urlEqualTo("/customers/42"))
    .willReturn(aResponse().withStatus(200).withBody("{\"id\":42}")));

  Customer c = client.getCustomer(42L);

  assertThat(c.id()).isEqualTo(42L);
  verify(getRequestedFor(urlEqualTo("/customers/42")));
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Keep client logic in a dedicated adapter class for focused tests.
- Assert both returned result and outbound request contract.
- Map transport exceptions to domain-level exceptions.

## Constraints and Warnings

- WireMock stubs must match exact URL and method or tests may fail with false negatives.
- Dynamic ports require passing runtime base URL into the client; hardcoded ports are brittle.
- Default timeouts in HTTP clients may differ from production configuration.
- Verify JSON payload matching carefully to avoid over-strict whitespace-sensitive assertions.

## Constraints

- Do not perform real network calls in unit tests.
- Do not depend on third-party rate limits or sandbox uptime.
- Keep tests deterministic and isolated by scenario.

## References

- [Examples](references/examples.md) - Complete runnable test examples
