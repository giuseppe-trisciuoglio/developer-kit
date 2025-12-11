# React Reference Guide

Complete reference for React hooks, APIs, and patterns including React 19 features.

## Core Hooks Reference

### useState

```typescript
const [state, setState] = useState(initialState);
const [state, setState] = useState(() => computeInitialState());
```

**Parameters:**
- `initialState`: Initial state value or function
- Returns: `[state, setState]` tuple

**Examples:**
```typescript
// Basic counter
const [count, setCount] = useState(0);

// With function initializer
const [data, setData] = useState(() => {
  return JSON.parse(localStorage.getItem('data') || '[]');
});

// Object state
const [user, setUser] = useState({
  name: '',
  email: '',
  age: 0
});
```

### useEffect

```typescript
useEffect(() => {
  // Side effect logic
  return () => {
    // Cleanup
  };
}, [dependencies]);
```

**Parameters:**
- Setup function (can return cleanup function)
- Dependency array (optional)

**Common Patterns:**
```typescript
// Data fetching
useEffect(() => {
  let ignore = false;

  async function fetchData() {
    const result = await api.getData();
    if (!ignore) {
      setData(result);
    }
  }

  fetchData();

  return () => {
    ignore = true;
  };
}, []);

// Subscriptions
useEffect(() => {
  const subscription = eventSource.subscribe(handleEvent);
  return () => subscription.unsubscribe();
}, [handleEvent]);

// DOM manipulation
useEffect(() => {
  const element = ref.current;
  if (element) {
    element.focus();
  }
}, []);
```

### useContext

```typescript
const value = useContext(MyContext);
```

**Usage:**
```typescript
// Create context
const ThemeContext = createContext('light');

// Provider
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

// Consumer
function Button() {
  const theme = useContext(ThemeContext);
  return <button className={theme}>Click me</button>;
}
```

### useReducer

```typescript
const [state, dispatch] = useReducer(reducer, initialState);
const [state, dispatch] = useReducer(reducer, initialState, init);
```

**Example:**
```typescript
interface State {
  count: number;
}

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'set'; payload: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    case 'decrement':
      return { count: state.count - 1 };
    case 'set':
      return { count: action.payload };
    default:
      return state;
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

### useRef

```typescript
const ref = useRef(initialValue);
```

**Use Cases:**
```typescript
// DOM reference
const inputRef = useRef<HTMLInputElement>(null);

// Mutable value
const timerRef = useRef<NodeJS.Timeout | null>(null);

// Previous value
const prevValueRef = useRef();

useEffect(() => {
  prevValueRef.current = value;
});
```

### useMemo

```typescript
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
```

### useCallback

```typescript
const memoizedCallback = useCallback(
  () => doSomething(a, b),
  [a, b]
);
```

### useLayoutEffect

```typescript
useLayoutEffect(() => {
  // Runs synchronously after DOM mutations
});
```

## React 19 Hooks

### use

```typescript
const value = use(resource);
```

**Reading Promises:**
```typescript
function Message({ messagePromise }) {
  const message = use(messagePromise);
  return <p>{message}</p>;
}
```

**Reading Context:**
```typescript
function ThemeButton() {
  if (condition) {
    const theme = use(ThemeContext);
    return <button className={theme}>Click</button>;
  }
  return <button>Click</button>;
}
```

### useOptimistic

```typescript
const [optimisticState, addOptimistic] = useOptimistic(
  state,
  updateFn
);
```

### useFormStatus

```typescript
const { pending, data, method, action } = useFormStatus();
```

### useFormState

```typescript
const [state, formAction] = useFormState(
  actionFn,
  initialState,
  permalink?
);
```

## Advanced Hooks

### useImperativeHandle

```typescript
useImperativeHandle(ref, createHandle, [deps]);
```

### useId

```typescript
const id = useId();
```

### useDebugValue

```typescript
useDebugValue(value, formatFn);
```

### useDeferredValue

```typescript
const deferredValue = useDeferredValue(value);
```

### useTransition

```typescript
const [isPending, startTransition] = useTransition();
```

## Component APIs

### memo

```typescript
const MemoizedComponent = memo(Component, areEqual?);
```

### forwardRef

```typescript
const RefComponent = forwardRef((props, ref) => {
  return <div ref={ref}>{props.children}</div>;
});
```

### lazy

```typescript
const LazyComponent = lazy(() => import('./Component'));
```

## Server Components APIs

### Server Actions

```typescript
'use server';

async function myAction(formData: FormData) {
  // Server-side logic
}
```

### Server Component Directives

```typescript
// Default: Server Component
export default async function ServerComponent() {
  const data = await fetch('...');
  return <div>{data}</div>;
}

// Client Component
'use client';

export function ClientComponent() {
  const [state, setState] = useState();
  return <div>{state}</div>;
}
```

## Common Patterns

### Custom Hook Template

```typescript
function useCustomHook(initialValue) {
  const [state, setState] = useState(initialValue);

  // Custom logic
  const updateValue = useCallback((newValue) => {
    setState(newValue);
  }, []);

  return [state, updateValue];
}
```

### Data Fetching Hook

```typescript
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;

    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(url);
        const result = await response.json();
        if (!ignore) {
          setData(result);
        }
      } catch (err) {
        if (!ignore) {
          setError(err);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      ignore = true;
    };
  }, [url]);

  return { data, loading, error };
}
```

### Local Storage Hook

```typescript
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  }, [key]);

  return [storedValue, setValue];
}
```

### Debounce Hook

```typescript
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

## Performance Optimization

### Component Memoization

```typescript
// With memo
const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  return <div>{processData(data)}</div>;
});

// Custom comparison
const ListComponent = memo(List, (prevProps, nextProps) => {
  return prevProps.items.length === nextProps.items.length;
});
```

### Callback Optimization

```typescript
function Parent({ items }) {
  const [selected, setSelected] = useState(null);

  const handleClick = useCallback((id) => {
    setSelected(id);
  }, []);

  return items.map(item => (
    <Item key={item.id} item={item} onClick={handleClick} />
  ));
}
```

### Memo Optimization

```typescript
function ExpensiveCalculation({ data, filter }) {
  const filteredData = useMemo(() => {
    return data.filter(item => item.type === filter);
  }, [data, filter]);

  const summary = useMemo(() => {
    return filteredData.reduce((acc, item) => acc + item.value, 0);
  }, [filteredData]);

  return <div>Total: {summary}</div>;
}
```

## Error Handling

### Error Boundaries

```typescript
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}
```

### Error Handling with Hooks

```typescript
function useErrorHandler() {
  const [error, setError] = useState(null);

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((error) => {
    setError(error);
  }, []);

  return { error, handleError, resetError };
}
```

## TypeScript Integration

### Component Props Types

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant,
  size = 'md',
  onClick,
  children,
  disabled = false
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
```

### Generic Components

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string | number;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}
```

### Hook Return Types

```typescript
interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

function useApi<T>(url: string): UseApiResult<T> {
  // Implementation
}
```

## Testing Utilities

### Render with Providers

```typescript
function renderWithProviders(
  ui: React.ReactElement,
  options: RenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <Router>
          {children}
        </Router>
      </Provider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}
```

### Testing Custom Hooks

```typescript
import { renderHook, act } from '@testing-library/react';

test('useCounter increments', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});
```

## Common Gotchas

### Dependency Array Rules

```typescript
// ❌ Missing dependencies
useEffect(() => {
  fetchData(userId);
}, []); // Missing userId

// ✅ Correct
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

### Stale Closure

```typescript
// ❌ Stale closure
useEffect(() => {
  const interval = setInterval(() => {
    setCount(count + 1); // Always sees initial count
  }, 1000);
  return () => clearInterval(interval);
}, []);

// ✅ Functional update
useEffect(() => {
  const interval = setInterval(() => {
    setCount(c => c + 1);
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### Infinite Re-renders

```typescript
// ❌ Infinite loop
useEffect(() => {
  setData(processData(data));
}, [data]);

// ✅ Correct approach
useEffect(() => {
  setData(processData(data));
}, [someOtherDependency]);
```

## Browser APIs Integration

### Resize Observer

```typescript
function useResizeObserver(elementRef) {
  const [dimensions, setDimensions] = useState({
    width: 0,
    height: 0
  });

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new ResizeObserver(entries => {
      const entry = entries[0];
      setDimensions({
        width: entry.contentRect.width,
        height: entry.contentRect.height
      });
    });

    observer.observe(element);

    return () => observer.disconnect();
  }, [elementRef]);

  return dimensions;
}
```

### Intersection Observer

```typescript
function useIntersectionObserver(elementRef, options) {
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => setIsIntersecting(entry.isIntersecting),
      options
    );

    observer.observe(element);

    return () => observer.disconnect();
  }, [elementRef, options]);

  return isIntersecting;
}
```

## Migration Checklist

### React 18 to 19 Migration

- [ ] Update dependencies to React 19
- [ ] Replace manual optimistic updates with `useOptimistic`
- [ ] Migrate form handling to use Server Actions
- [ ] Add `'use client'` directive to client components
- [ ] Enable React Compiler for performance
- [ ] Update ESLint configuration for new hooks
- [ ] Test concurrent features properly
- [ ] Verify hydration behavior with Suspense

### Class Components to Hooks Migration

- [ ] Convert `this.state` to `useState`
- [ ] Replace `componentDidMount` with `useEffect`
- [ ] Convert `componentDidUpdate` to `useEffect` with dependencies
- [ ] Replace `componentWillUnmount` with cleanup in `useEffect`
- [ ] Convert methods to useCallback if passed as props
- [ ] Replace context consumers with `useContext`
- [ ] Convert refs using `useRef`
- [ ] Replace HOCs with custom hooks where appropriate