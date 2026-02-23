# Application Events Test Examples

## Example 1: Capture published event with Mockito

```java
package com.example.events;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.context.ApplicationEventPublisher;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class AccountServiceEventPublisherTest {

    @Mock
    private ApplicationEventPublisher eventPublisher;

    @InjectMocks
    private AccountService accountService;

    @Test
    void shouldPublishAccountCreatedEvent() {
        accountService.createAccount("alice@example.com");

        ArgumentCaptor<AccountCreatedEvent> captor = ArgumentCaptor.forClass(AccountCreatedEvent.class);
        verify(eventPublisher).publishEvent(captor.capture());

        AccountCreatedEvent event = captor.getValue();
        assertThat(event.email()).isEqualTo("alice@example.com");
        assertThat(event.source()).isEqualTo("AccountService");
    }

    static class AccountService {
        private final ApplicationEventPublisher publisher;

        AccountService(ApplicationEventPublisher publisher) {
            this.publisher = publisher;
        }

        void createAccount(String email) {
            publisher.publishEvent(new AccountCreatedEvent("AccountService", email));
        }
    }

    record AccountCreatedEvent(String source, String email) {
    }
}
```

## Example 2: Test listener side effects directly

```java
package com.example.events;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.context.event.EventListener;

import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class AccountCreatedListenerTest {

    @Mock
    private WelcomeEmailSender welcomeEmailSender;

    @InjectMocks
    private AccountCreatedListener listener;

    @Test
    void shouldSendWelcomeEmailWhenEventReceived() {
        listener.onAccountCreated(new AccountCreatedEvent("AccountService", "alice@example.com"));

        verify(welcomeEmailSender).send("alice@example.com");
    }

    static class AccountCreatedListener {
        private final WelcomeEmailSender welcomeEmailSender;

        AccountCreatedListener(WelcomeEmailSender welcomeEmailSender) {
            this.welcomeEmailSender = welcomeEmailSender;
        }

        @EventListener
        void onAccountCreated(AccountCreatedEvent event) {
            welcomeEmailSender.send(event.email());
        }
    }

    interface WelcomeEmailSender {
        void send(String email);
    }

    record AccountCreatedEvent(String source, String email) {
    }
}
```

## Example 3: Async listener test with `CountDownLatch`

```java
package com.example.events;

import org.junit.jupiter.api.Test;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;

class AsyncListenerPatternTest {

    @Test
    void shouldCompleteAsyncListenerWork() throws Exception {
        CountDownLatch latch = new CountDownLatch(1);
        ExecutorService executor = Executors.newSingleThreadExecutor();

        AsyncListener listener = new AsyncListener(latch);
        executor.submit(() -> listener.onEvent(new ReportReadyEvent("R-100")));

        boolean completed = latch.await(1, TimeUnit.SECONDS);
        executor.shutdownNow();

        assertThat(completed).isTrue();
        assertThat(listener.getLastReportId()).isEqualTo("R-100");
    }

    static class AsyncListener {
        private final CountDownLatch latch;
        private volatile String lastReportId;

        AsyncListener(CountDownLatch latch) {
            this.latch = latch;
        }

        void onEvent(ReportReadyEvent event) {
            this.lastReportId = event.reportId();
            latch.countDown();
        }

        String getLastReportId() {
            return lastReportId;
        }
    }

    record ReportReadyEvent(String reportId) {
    }
}
```
