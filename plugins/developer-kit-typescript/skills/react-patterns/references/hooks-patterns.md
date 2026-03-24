# React Hooks Patterns

Detailed patterns for React core hooks and custom hook creation.

## useState

Basic state declaration:

```typescript
const [count, setCount] = useState(0);
```

State with initializer function (expensive computation):

```typescript
const [state, setState] = useState(() => {
  return computeExpensiveValue();
});
```

Multiple state variables:

```typescript
function UserProfile() {
  const [name, setName] = useState('');
  const [age, setAge] = useState(0);
  const [email, setEmail] = useState('');

  return (
    <form>
      <input value={name} onChange={e => setName(e.target.value)} />
      <input type="number" value={age} onChange={e => setAge(Number(e.target.value))} />
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
    </form>
  );
}
```

## useEffect

Basic effect with cleanup:

```typescript
function ChatRoom({ roomId }: { roomId: string }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();

    return () => {
      connection.disconnect();
    };
  }, [roomId]);

  return <div>Connected to {roomId}</div>;
}
```

Effect for subscriptions (run once):

```typescript
function StatusBar() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    function handleOnline() { setIsOnline(true); }
    function handleOffline() { setIsOnline(false); }

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []); // Empty array = run once on mount

  return <h1>{isOnline ? 'Online' : 'Disconnected'}</h1>;
}
```

Data fetching with race condition guard:

```typescript
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    let ignore = false;

    async function fetchUser() {
      const data = await api.getUser(userId);
      if (!ignore) setUser(data);
    }

    fetchUser();
    return () => { ignore = true; };
  }, [userId]);

  return user ? <div>{user.name}</div> : <p>Loading...</p>;
}
```

## useRef

DOM element reference:

```typescript
function TextInput() {
  const inputRef = useRef<HTMLInputElement>(null);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>Focus Input</button>
    </>
  );
}
```

Storing mutable values without re-renders:

```typescript
function Timer() {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startTimer = () => {
    intervalRef.current = setInterval(() => console.log('Tick'), 1000);
  };

  const stopTimer = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
  };

  return (
    <>
      <button onClick={startTimer}>Start</button>
      <button onClick={stopTimer}>Stop</button>
    </>
  );
}
```

## useReducer

For complex state logic:

```typescript
type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'set'; payload: number };

function reducer(state: { count: number }, action: Action) {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    case 'decrement': return { count: state.count - 1 };
    case 'set': return { count: action.payload };
    default: return state;
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0 });

  return (
    <>
      Count: {state.count}
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
    </>
  );
}
```

## Custom Hooks Pattern

Extract reusable logic into custom hooks:

```typescript
// useOnlineStatus.ts
export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    function handleOnline() { setIsOnline(true); }
    function handleOffline() { setIsOnline(false); }

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

// Usage
function StatusBar() {
  const isOnline = useOnlineStatus();
  return <h1>{isOnline ? 'Online' : 'Disconnected'}</h1>;
}
```

Custom hook with parameters:

```typescript
// useFetch.ts
interface FetchResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useFetch<T>(url: string): FetchResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function fetchData() {
      try {
        setLoading(true);
        const res = await fetch(url);
        const result = await res.json();
        if (!ignore) setData(result);
      } catch (err) {
        if (!ignore) setError('Failed to fetch');
      } finally {
        if (!ignore) setLoading(false);
      }
    }

    fetchData();
    return () => { ignore = true; };
  }, [url]);

  return { data, loading, error };
}
```

Utility custom hooks:

```typescript
// useDebounce.ts
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// useLocalStorage.ts
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback((value: T) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  }, [key]);

  return [storedValue, setValue] as const;
}
```

## Common Pitfalls

Missing dependencies:

```typescript
// Wrong: missing userId in deps
useEffect(() => {
  fetchData(userId);
}, []);

// Correct
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

Stale closure:

```typescript
// Wrong: always sees initial count
useEffect(() => {
  const interval = setInterval(() => setCount(count + 1), 1000);
  return () => clearInterval(interval);
}, []);

// Correct: functional update
useEffect(() => {
  const interval = setInterval(() => setCount(c => c + 1), 1000);
  return () => clearInterval(interval);
}, []);
```

Avoid deriving state inside effects:

```typescript
// Wrong: unnecessary effect
useEffect(() => {
  setVisibleTodos(todos.filter(t => !t.completed));
}, [todos]);

// Correct: compute during render
const visibleTodos = todos.filter(t => !t.completed);
```
