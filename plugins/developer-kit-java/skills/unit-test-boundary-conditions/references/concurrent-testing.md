# Concurrent Boundary Testing Reference

## Null and Race Conditions

```java
import java.util.concurrent.*;

class ConcurrentBoundaryTest {

  @Test
  void shouldHandleNullInConcurrentMap() {
    ConcurrentHashMap<String, String> map = new ConcurrentHashMap<>();

    map.put("key", "value");
    assertThat(map.get("nonexistent")).isNull();
  }

  @Test
  void shouldHandleConcurrentModification() {
    List<Integer> list = new CopyOnWriteArrayList<>(List.of(1, 2, 3, 4, 5));

    for (int num : list) {
      if (num == 3) {
        list.add(6);
      }
    }

    assertThat(list).hasSize(6);
  }

  @Test
  void shouldHandleEmptyBlockingQueue() throws InterruptedException {
    BlockingQueue<String> queue = new LinkedBlockingQueue<>();

    assertThat(queue.poll()).isNull();
  }
}
```

## Thread Safety Patterns

```java
class ThreadSafetyBoundaryTest {

  @Test
  void shouldHandleAtomicOperations() {
    AtomicInteger counter = new AtomicInteger(0);

    counter.incrementAndGet();
    counter.addAndGet(Integer.MAX_VALUE);

    assertThat(counter.get()).isGreaterThan(0);
  }

  @Test
  void shouldHandleSynchronizedBlocks() {
    Object lock = new Object();
    int[] count = {0};

    synchronized (lock) {
      count[0]++;
    }

    assertThat(count[0]).isEqualTo(1);
  }
}
```
