# React Hooks Best Practices and Common Mistakes

## useState

### Functional Updates for Derived State
Use functional updates when the new state depends on the previous state.

```tsx
// ❌ May cause stale state in async contexts
setCount(count + 1);

// ✅ Always uses latest state
setCount(prev => prev + 1);
```

### Lazy Initialization
Use a function for expensive initial state computation.

```tsx
// ❌ Runs on every render
const [data, setData] = useState(expensiveComputation(props));

// ✅ Runs only on first render
const [data, setData] = useState(() => expensiveComputation(props));
```

## useEffect

### Always Include Cleanup Functions
When subscribing to external resources, always clean up.

```tsx
useEffect(() => {
  const controller = new AbortController();

  async function fetchData() {
    const res = await fetch('/api/data', { signal: controller.signal });
    const data = await res.json();
    setData(data);
  }

  fetchData();

  return () => controller.abort(); // Cleanup on unmount
}, []);
```

### Correct Dependency Arrays
Include all values from the component scope that change over time and are used in the effect.

```tsx
// ❌ Missing dependency — stale closure
useEffect(() => {
  const interval = setInterval(() => {
    setCount(count + 1); // count is stale
  }, 1000);
  return () => clearInterval(interval);
}, []); // count missing from deps

// ✅ Functional update avoids stale closure
useEffect(() => {
  const interval = setInterval(() => {
    setCount(prev => prev + 1); // Always uses latest
  }, 1000);
  return () => clearInterval(interval);
}, []); // No external dependency needed
```

### Avoid Using useEffect for Data Fetching
Prefer TanStack Query, SWR, or Server Components for data fetching.

```tsx
// ❌ Manual data fetching with useEffect
const [users, setUsers] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  let cancelled = false;
  fetchUsers()
    .then(data => { if (!cancelled) setUsers(data); })
    .catch(err => { if (!cancelled) setError(err); })
    .finally(() => { if (!cancelled) setLoading(false); });
  return () => { cancelled = true; };
}, []);

// ✅ TanStack Query handles loading, error, caching, refetching
const { data: users, isLoading, error } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
});
```

## useMemo and useCallback

### When to Use useMemo
Use `useMemo` for expensive computations that depend on specific values.

```tsx
// ✅ Appropriate: Expensive filtering/sorting
const filteredItems = useMemo(
  () => items.filter(item => item.category === category).sort(sortByDate),
  [items, category]
);

// ❌ Unnecessary: Simple calculations
const fullName = useMemo(() => `${first} ${last}`, [first, last]);
// Just do: const fullName = `${first} ${last}`;
```

### When to Use useCallback
Use `useCallback` when passing callbacks to memoized child components.

```tsx
// ✅ Appropriate: Passed to React.memo component
const handleSelect = useCallback((id: string) => {
  setSelected(id);
}, []);

<MemoizedList items={items} onSelect={handleSelect} />

// ❌ Unnecessary: Not passed to memoized child
const handleClick = useCallback(() => {
  console.log('clicked');
}, []);

<button onClick={handleClick}>Click</button>
// Just do: <button onClick={() => console.log('clicked')}>Click</button>
```

## useRef

### Storing Mutable Values Without Re-renders
Use refs for values that don't trigger re-renders.

```tsx
function Timer() {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [count, setCount] = useState(0);

  function start() {
    intervalRef.current = setInterval(() => {
      setCount(prev => prev + 1);
    }, 1000);
  }

  function stop() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  }

  return (
    <div>
      <p>{count}</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
    </div>
  );
}
```

## Custom Hooks

### Extracting Reusable Logic

```tsx
// ✅ Reusable hook encapsulating complex logic
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchInput() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  const { data } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => searchAPI(debouncedQuery),
    enabled: debouncedQuery.length > 2,
  });
}
```

## Common Mistakes Summary

| Mistake | Impact | Fix |
|---------|--------|-----|
| Missing useEffect cleanup | Memory leaks, stale updates | Always return cleanup function |
| Wrong dependency array | Stale closures, infinite loops | Include all used values |
| useEffect for data fetching | Race conditions, no caching | Use TanStack Query / SWR |
| useMemo everywhere | Code complexity, no benefit | Only for expensive computations |
| useCallback without memo | No performance benefit | Only with React.memo children |
| State for derived values | Unnecessary re-renders | Compute during render |
| Mutating state directly | Silent bugs, no re-render | Always create new references |
