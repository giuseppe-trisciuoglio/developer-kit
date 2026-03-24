# WireMock Advanced Examples

Additional patterns for complex WireMock testing scenarios.

## Error Scenario Testing (4xx/5xx)

```java
@Test
void shouldHandleNotFoundError() {
  wireMock.stubFor(get(urlEqualTo("/api/users/999"))
    .willReturn(aResponse()
      .withStatus(404)
      .withBody("{\"error\":\"User not found\"}")));

  ApiClient client = new ApiClient(wireMock.getRuntimeInfo().getHttpBaseUrl());

  assertThatThrownBy(() -> client.getUser(999))
    .isInstanceOf(UserNotFoundException.class)
    .hasMessageContaining("User not found");
}

@Test
void shouldHandleServerError() {
  wireMock.stubFor(get(urlEqualTo("/api/data"))
    .willReturn(aResponse()
      .withStatus(500)
      .withBody("{\"error\":\"Internal server error\"}")));

  ApiClient client = new ApiClient(wireMock.getRuntimeInfo().getHttpBaseUrl());

  assertThatThrownBy(() -> client.fetchData())
    .isInstanceOf(ServerErrorException.class);
}
```

## Request Body Verification

```java
@Test
void shouldVerifyRequestBody() {
  wireMock.stubFor(post(urlEqualTo("/api/users"))
    .willReturn(aResponse()
      .withStatus(201)
      .withBody("{\"id\":123,\"name\":\"Alice\"}")));

  ApiClient client = new ApiClient(wireMock.getRuntimeInfo().getHttpBaseUrl());
  UserResponse response = client.createUser("Alice");

  assertThat(response.getId()).isEqualTo(123);

  wireMock.verify(postRequestedFor(urlEqualTo("/api/users"))
    .withRequestBody(matchingJsonPath("$.name", equalTo("Alice")))
    .withHeader("Content-Type", containing("application/json")));
}
```

## Timeout Simulation

```java
@Test
void shouldHandleTimeout() {
  wireMock.stubFor(get(urlEqualTo("/api/slow"))
    .willReturn(aResponse()
      .withFixedDelay(5000)
      .withStatus(200)));

  // Configure client timeout < 5000ms
  assertThatThrownBy(() -> client.fetchSlowEndpoint())
    .isInstanceOf(SocketTimeoutException.class);
}
```

## Partial Response Matching

```java
@Test
void shouldMatchPartialRequestBody() {
  wireMock.stubFor(post(urlEqualTo("/api/orders"))
    .withRequestBody(matchingJsonPath("$.items[*]", equalTo("[1,2,3]")))
    .willReturn(aResponse()
      .withStatus(201)));

  ApiClient client = new ApiClient(wireMock.getRuntimeInfo().getHttpBaseUrl());
  client.createOrder(List.of(1, 2, 3));

  wireMock.verify(postRequestedFor(urlEqualTo("/api/orders")));
}
```

## Scenarios (Stateful Behavior)

```java
@Test
void shouldSupportStatefulScenarios() {
  wireMock.stubFor(get(urlEqualTo("/api/status"))
    .inScenario("OrderWorkflow")
    .whenScenarioStateIs(STARTED)
    .willSetStateTo("PROCESSING")
    .willReturn(aResponse()
      .withStatus(202)
      .withBody("{\"status\":\"processing\"}")));

  wireMock.stubFor(get(urlEqualTo("/api/status"))
    .inScenario("OrderWorkflow")
    .whenScenarioStateIs("PROCESSING")
    .willSetStateTo("COMPLETED")
    .willReturn(aResponse()
      .withStatus(200)
      .withBody("{\"status\":\"completed\"}")));

  // First call
  client.getOrderStatus();
  wireMock.verify(getRequestedFor(urlEqualTo("/api/status"))
    .inScenario("OrderWorkflow"));

  // Second call
  client.getOrderStatus();
  wireMock.verify(getRequestedFor(urlEqualTo("/api/status")));
}
```
