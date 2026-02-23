# WireMock REST API Test Examples

## Example 1: Stub success response and verify outbound request

```java
package com.example.integration;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;
import org.wiremock.junit5.WireMockExtension;

import static com.github.tomakehurst.wiremock.client.WireMock.aResponse;
import static com.github.tomakehurst.wiremock.client.WireMock.equalTo;
import static com.github.tomakehurst.wiremock.client.WireMock.get;
import static com.github.tomakehurst.wiremock.client.WireMock.getRequestedFor;
import static com.github.tomakehurst.wiremock.client.WireMock.stubFor;
import static com.github.tomakehurst.wiremock.client.WireMock.urlEqualTo;
import static com.github.tomakehurst.wiremock.core.WireMockConfiguration.wireMockConfig;
import static org.assertj.core.api.Assertions.assertThat;

class CustomerApiClientTest {

    @RegisterExtension
    static WireMockExtension wireMock = WireMockExtension.newInstance()
            .options(wireMockConfig().dynamicPort())
            .build();

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void shouldFetchCustomerById() throws Exception {
        stubFor(get(urlEqualTo("/customers/42"))
                .withHeader("Authorization", equalTo("Bearer test-token"))
                .willReturn(aResponse()
                        .withStatus(200)
                        .withHeader("Content-Type", "application/json")
                        .withBody("{" +
                                "\"id\":42," +
                                "\"name\":\"Alice\"," +
                                "\"email\":\"alice@example.com\"" +
                                "}")));

        CustomerApiClient client = new CustomerApiClient(
                wireMock.getRuntimeInfo().getHttpBaseUrl(),
                "test-token",
                new RestTemplate(),
                objectMapper
        );

        Customer customer = client.getCustomer(42L);

        assertThat(customer.id()).isEqualTo(42L);
        assertThat(customer.name()).isEqualTo("Alice");

        wireMock.verify(getRequestedFor(urlEqualTo("/customers/42"))
                .withHeader("Authorization", equalTo("Bearer test-token")));
    }

    static class CustomerApiClient {
        private final String baseUrl;
        private final String token;
        private final RestTemplate restTemplate;
        private final ObjectMapper objectMapper;

        CustomerApiClient(String baseUrl, String token, RestTemplate restTemplate, ObjectMapper objectMapper) {
            this.baseUrl = baseUrl;
            this.token = token;
            this.restTemplate = restTemplate;
            this.objectMapper = objectMapper;
        }

        Customer getCustomer(Long id) throws Exception {
            HttpHeaders headers = new HttpHeaders();
            headers.setBearerAuth(token);
            headers.setAccept(java.util.List.of(MediaType.APPLICATION_JSON));

            ResponseEntity<String> response = restTemplate.exchange(
                    baseUrl + "/customers/" + id,
                    HttpMethod.GET,
                    new HttpEntity<>(headers),
                    String.class
            );

            return objectMapper.readValue(response.getBody(), Customer.class);
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    record Customer(Long id, String name, String email) {
    }
}
```

## Example 2: Map HTTP 404 to domain exception

```java
package com.example.integration;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.springframework.http.HttpMethod;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;
import org.wiremock.junit5.WireMockExtension;

import static com.github.tomakehurst.wiremock.client.WireMock.aResponse;
import static com.github.tomakehurst.wiremock.client.WireMock.get;
import static com.github.tomakehurst.wiremock.client.WireMock.stubFor;
import static com.github.tomakehurst.wiremock.client.WireMock.urlEqualTo;
import static com.github.tomakehurst.wiremock.core.WireMockConfiguration.wireMockConfig;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class CustomerApiErrorHandlingTest {

    @RegisterExtension
    static WireMockExtension wireMock = WireMockExtension.newInstance()
            .options(wireMockConfig().dynamicPort())
            .build();

    @Test
    void shouldThrowDomainExceptionWhenCustomerMissing() {
        stubFor(get(urlEqualTo("/customers/99"))
                .willReturn(aResponse().withStatus(404).withBody("not found")));

        ExternalCustomerService service = new ExternalCustomerService(
                wireMock.getRuntimeInfo().getHttpBaseUrl(),
                new RestTemplate()
        );

        assertThatThrownBy(() -> service.requireCustomer(99L))
                .isInstanceOf(CustomerMissingException.class)
                .hasMessage("Customer 99 not found in external system");
    }

    static class ExternalCustomerService {
        private final String baseUrl;
        private final RestTemplate restTemplate;

        ExternalCustomerService(String baseUrl, RestTemplate restTemplate) {
            this.baseUrl = baseUrl;
            this.restTemplate = restTemplate;
        }

        String requireCustomer(Long id) {
            try {
                return restTemplate.execute(baseUrl + "/customers/" + id, HttpMethod.GET, null, response -> "ok");
            } catch (HttpClientErrorException.NotFound ex) {
                throw new CustomerMissingException("Customer " + id + " not found in external system");
            }
        }
    }

    static class CustomerMissingException extends RuntimeException {
        CustomerMissingException(String message) {
            super(message);
        }
    }
}
```
