# State Management in Sagas

## Saga State Entity

Persist saga state for recovery and monitoring:

```java
@Entity
@Table(name = "saga_state")
public class SagaState {

    @Id
    private String sagaId;

    @Enumerated(EnumType.STRING)
    private SagaStatus status;

    @Column(columnDefinition = "TEXT")
    private String currentStep;

    @Column(columnDefinition = "TEXT")
    private String compensationSteps;

    private Instant startedAt;
    private Instant completedAt;

    @Version
    private Long version;
}

public enum SagaStatus {
    STARTED,
    PROCESSING,
    COMPENSATING,
    COMPLETED,
    FAILED,
    CANCELLED
}
```

## Saga State Machine with Spring Statemachine

Define saga state transitions explicitly:

```java
@Configuration
@EnableStateMachine
public class SagaStateMachineConfig
    extends StateMachineConfigurerAdapter<SagaStatus, SagaEvent> {

    @Override
    public void configure(
        StateMachineStateConfigurer<SagaStatus, SagaEvent> states)
        throws Exception {

        states
            .withStates()
            .initial(SagaStatus.STARTED)
            .states(EnumSet.allOf(SagaStatus.class))
            .end(SagaStatus.COMPLETED)
            .end(SagaStatus.FAILED);
    }

    @Override
    public void configure(
        StateMachineTransitionConfigurer<SagaStatus, SagaEvent> transitions)
        throws Exception {

        transitions
            .withExternal()
                .source(SagaStatus.STARTED)
                .target(SagaStatus.PROCESSING)
                .event(SagaEvent.ORDER_CREATED)
            .and()
            .withExternal()
                .source(SagaStatus.PROCESSING)
                .target(SagaStatus.COMPLETED)
                .event(SagaEvent.ALL_STEPS_COMPLETED)
            .and()
            .withExternal()
                .source(SagaStatus.PROCESSING)
                .target(SagaStatus.COMPENSATING)
                .event(SagaEvent.STEP_FAILED)
            .and()
            .withExternal()
                .source(SagaStatus.COMPENSATING)
                .target(SagaStatus.FAILED)
                .event(SagaEvent.COMPENSATION_COMPLETED);
    }
}
```

## State Transitions

### Successful Saga Flow

```
STARTED → PROCESSING → COMPLETED
```

### Failed Saga with Compensation

```
STARTED → PROCESSING → COMPENSATING → FAILED
```

### Saga with Retry

```
STARTED → PROCESSING → PROCESSING (retry) → COMPLETED
```

## Persisting Saga Context

Store context data for saga execution:

```java
@Entity
@Table(name = "saga_context")
public class SagaContext {

    @Id
    private String sagaId;

    @Column(columnDefinition = "TEXT")
    private String contextData; // JSON-serialized

    private Instant createdAt;
    private Instant updatedAt;

    public <T> T getContextData(Class<T> type) {
        return JsonUtils.fromJson(contextData, type);
    }

    public void setContextData(Object data) {
        this.contextData = JsonUtils.toJson(data);
    }
}

@Service
public class SagaContextService {

    private final SagaContextRepository repository;

    public void saveContext(String sagaId, Object context) {
        SagaContext sagaContext = new SagaContext(sagaId);
        sagaContext.setContextData(context);
        repository.save(sagaContext);
    }

    public <T> T loadContext(String sagaId, Class<T> type) {
        return repository.findById(sagaId)
            .map(ctx -> ctx.getContextData(type))
            .orElseThrow(() -> new SagaContextNotFoundException(sagaId));
    }
}
```

## Handling Saga Timeouts

Detect and handle sagas that exceed expected duration:

```java
@Service
public class SagaTimeoutHandler {

    private final SagaStateRepository repository;
    private static final Duration MAX_SAGA_DURATION = Duration.ofMinutes(30);

    @Scheduled(fixedDelay = 60000) // Check every minute
    public void detectTimeouts() {
        Instant timeout = Instant.now().minus(MAX_SAGA_DURATION);

        List<SagaState> timedOutSagas = repository
            .findByStatusAndStartedAtBefore(SagaStatus.PROCESSING, timeout);

        timedOutSagas.forEach(saga -> {
            logger.warn("Saga {} timed out", saga.getSagaId());
            compensateSaga(saga);
        });
    }

    private void compensateSaga(SagaState saga) {
        saga.setStatus(SagaStatus.COMPENSATING);
        repository.save(saga);
        // Trigger compensation logic
    }
}
```

## Saga Recovery

Recover sagas from failures:

```java
@Service
public class SagaRecoveryService {

    private final SagaStateRepository stateRepository;
    private final CommandGateway commandGateway;

    @Scheduled(fixedDelay = 30000) // Check every 30 seconds
    public void recoverFailedSagas() {
        List<SagaState> failedSagas = stateRepository
            .findByStatus(SagaStatus.FAILED);

        failedSagas.forEach(saga -> {
            if (canBeRetried(saga)) {
                logger.info("Retrying saga {}", saga.getSagaId());
                retrySaga(saga);
            }
        });
    }

    private boolean canBeRetried(SagaState saga) {
        return saga.getRetryCount() < 3;
    }

    private void retrySaga(SagaState saga) {
        saga.setStatus(SagaStatus.STARTED);
        saga.setRetryCount(saga.getRetryCount() + 1);
        stateRepository.save(saga);
        // Send retry command
    }
}
```

## Saga State Query

Query sagas for monitoring:

```java
@Repository
public interface SagaStateRepository extends JpaRepository<SagaState, String> {

    List<SagaState> findByStatus(SagaStatus status);

    List<SagaState> findByStatusAndStartedAtBefore(
        SagaStatus status, Instant before);

    Page<SagaState> findByStatus(SagaStatus status, Pageable pageable);

    long countByStatus(SagaStatus status);

    long countByStatusAndStartedAtBefore(SagaStatus status, Instant before);
}

@RestController
@RequestMapping("/api/sagas")
public class SagaMonitoringController {

    private final SagaStateRepository repository;

    @GetMapping("/status/{status}")
    public List<SagaState> getSagasByStatus(
            @PathVariable SagaStatus status) {
        return repository.findByStatus(status);
    }

    @GetMapping("/stuck")
    public List<SagaState> getStuckSagas() {
        Instant oneHourAgo = Instant.now().minus(Duration.ofHours(1));
        return repository.findByStatusAndStartedAtBefore(
            SagaStatus.PROCESSING, oneHourAgo);
    }
}
```

## Database Schema for State Management

```sql
CREATE TABLE saga_state (
    saga_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    current_step TEXT,
    compensation_steps TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    version BIGINT,
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
);

CREATE TABLE saga_context (
    saga_id VARCHAR(255) PRIMARY KEY,
    context_data LONGTEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    FOREIGN KEY (saga_id) REFERENCES saga_state(saga_id)
);

CREATE INDEX idx_saga_state_status_started
    ON saga_state(status, started_at);
```
