# React Performance Patterns

Performance optimization patterns including React Compiler, memoization, and concurrent features.

## React Compiler

React Compiler (available in React 19) automatically memoizes components. Write clean, idiomatic React and let the compiler optimize.

### Setup

```bash
npm install -D babel-plugin-react-compiler@latest
npm install -D eslint-plugin-react-hooks@latest
```

```javascript
// babel.config.js
module.exports = {
  plugins: [
    'babel-plugin-react-compiler', // Must run first!
  ],
};

// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: ['babel-plugin-react-compiler'],
      },
    }),
  ],
});
```

Incremental adoption:

```javascript
// babel.config.js — only compile specific directories
module.exports = {
  plugins: [],
  overrides: [
    {
      test: './src/components/**/*.{js,jsx,ts,tsx}',
      plugins: ['babel-plugin-react-compiler']
    }
  ]
};
```

### With vs Without Compiler

```typescript
// Before React Compiler — manual memoization needed
const ExpensiveComponent = memo(function ExpensiveComponent({ data, onUpdate }) {
  const processedData = useMemo(() => {
    return data.map(item => ({ ...item, computed: expensiveCalculation(item) }));
  }, [data]);

  const handleClick = useCallback((id) => {
    onUpdate(id);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} item={item} onClick={handleClick} />
      ))}
    </div>
  );
});

// After React Compiler — clean idiomatic code, compiler handles it
function ExpensiveComponent({ data, onUpdate }) {
  const processedData = data.map(item => ({
    ...item,
    computed: expensiveCalculation(item)
  }));

  const handleClick = (id) => {
    onUpdate(id);
  };

  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} item={item} onClick={handleClick} />
      ))}
    </div>
  );
}
```

## Manual Memoization (Without Compiler)

### React.memo

```typescript
const ExpensiveComponent = memo(function ExpensiveComponent({ data }: { data: Item[] }) {
  return <div>{/* expensive rendering */}</div>;
});

// Custom comparison function
const ListComponent = memo(List, (prevProps, nextProps) => {
  return prevProps.items.length === nextProps.items.length;
});
```

### useMemo for Expensive Computations

```typescript
function DataTable({ data }: { data: Item[] }) {
  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => a.name.localeCompare(b.name));
  }, [data]); // Only recompute when data changes

  return <table>{/* render sortedData */}</table>;
}
```

### useCallback for Function Stability

```typescript
function Parent({ items }: { items: Item[] }) {
  const [selected, setSelected] = useState<string | null>(null);

  const handleClick = useCallback((id: string) => {
    setSelected(id);
  }, []); // No deps needed — setSelected is stable

  return items.map(item => (
    <Item key={item.id} item={item} onClick={handleClick} />
  ));
}
```

## Concurrent Features

### useTransition for Non-Urgent Updates

Mark state updates as non-urgent to keep the UI responsive:

```typescript
function SearchableList({ items }: { items: Item[] }) {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [filteredItems, setFilteredItems] = useState(items);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value); // Immediate update

    startTransition(() => {
      setFilteredItems(
        items.filter(item =>
          item.name.toLowerCase().includes(e.target.value.toLowerCase())
        )
      );
    });
  };

  return (
    <div>
      <input value={query} onChange={handleChange} placeholder="Search..." />
      {isPending && <div>Filtering...</div>}
      <ul>
        {filteredItems.map(item => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### useDeferredValue for Expensive UI

Defer an expensive computation to keep input responsive:

```typescript
function DataGrid({ data }: { data: DataRow[] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const deferredSearchTerm = useDeferredValue(searchTerm);

  const filteredData = useMemo(() => {
    return data.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(deferredSearchTerm.toLowerCase())
      )
    );
  }, [data, deferredSearchTerm]);

  return (
    <div>
      <input
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
        className={searchTerm !== deferredSearchTerm ? 'stale' : ''}
      />
      <DataGridRows data={filteredData} />
    </div>
  );
}
```

### useTransition vs useDeferredValue

| | useTransition | useDeferredValue |
|---|---|---|
| Use when | You control the state update | You receive value as prop |
| Shows pending | Yes (`isPending`) | No (visual stale indicator) |
| Pattern | Wrap `setState` calls | Wrap the value |

## Lazy Loading

```typescript
import { lazy, Suspense } from 'react';

const LazyDashboard = lazy(() => import('./Dashboard'));
const LazySettings = lazy(() => import('./Settings'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyDashboard />
    </Suspense>
  );
}
```

## Browser Observer Hooks

### useResizeObserver

```typescript
function useResizeObserver(elementRef: React.RefObject<HTMLElement>) {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

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

### useIntersectionObserver

```typescript
function useIntersectionObserver(
  elementRef: React.RefObject<HTMLElement>,
  options?: IntersectionObserverInit
) {
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

## Avoid Unnecessary Effects

Compute derived state during render, not in effects:

```typescript
// Wrong: effect for derived state
function TodoList({ todos }: { todos: Todo[] }) {
  const [visibleTodos, setVisibleTodos] = useState<Todo[]>([]);

  useEffect(() => {
    setVisibleTodos(todos.filter(t => !t.completed));
  }, [todos]);
}

// Correct: compute during render
function TodoList({ todos }: { todos: Todo[] }) {
  const visibleTodos = todos.filter(t => !t.completed);
  return <ul>{/* render visibleTodos */}</ul>;
}
```

## Performance Checklist

- Profile with React DevTools before optimizing
- Avoid premature optimization — measure first
- With React Compiler: remove manual `useMemo`, `useCallback`, `memo`
- Without React Compiler: wrap expensive computations with `useMemo`
- Use `useTransition` for filtering/sorting large lists
- Use `useDeferredValue` when value comes from props or external state
- Use `lazy()` and `Suspense` for code splitting large components
- Keep component render functions pure — no side effects
- Use stable keys for lists (avoid index when items can be added/removed)
