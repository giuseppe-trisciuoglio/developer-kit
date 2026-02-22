# React Core Patterns & Examples

## Core Hooks Patterns

### useState - State Management

Basic state:

```typescript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(count + 1)}>Count: {count}</button>
  );
}
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

### useEffect - Side Effects

Basic effect with cleanup:

```typescript
import { useEffect } from 'react';

function ChatRoom({ roomId }: { roomId: string }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();
    return () => { connection.disconnect(); };
  }, [roomId]);

  return <div>Connected to {roomId}</div>;
}
```

Effect for subscriptions:

```typescript
function StatusBar() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return <h1>{isOnline ? 'Online' : 'Disconnected'}</h1>;
}
```

### useRef - Persistent References

Storing mutable values:

```typescript
import { useRef } from 'react';

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

DOM element references:

```typescript
function TextInput() {
  const inputRef = useRef<HTMLInputElement>(null);
  const focusInput = () => inputRef.current?.focus();

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>Focus Input</button>
    </>
  );
}
```

## Custom Hooks Pattern

```typescript
// useOnlineStatus.ts
import { useState, useEffect } from 'react';

export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

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
export function useChatRoom({ serverUrl, roomId }: ChatOptions) {
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => connection.disconnect();
  }, [serverUrl, roomId]);
}
```

## Component Composition Patterns

### Props and Children

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  children: React.ReactNode;
}

function Button({ variant = 'primary', size = 'md', onClick, children }: ButtonProps) {
  return (
    <button className={`btn btn-${variant} btn-${size}`} onClick={onClick}>
      {children}
    </button>
  );
}
```

### Lifting State Up

```typescript
function Parent() {
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <>
      <Panel isActive={activeIndex === 0} onShow={() => setActiveIndex(0)}>Panel 1</Panel>
      <Panel isActive={activeIndex === 1} onShow={() => setActiveIndex(1)}>Panel 2</Panel>
    </>
  );
}
```

## Performance Optimization

### Avoid Unnecessary Effects

```typescript
// BAD - Using effect for derived state
function TodoList({ todos }: { todos: Todo[] }) {
  const [visibleTodos, setVisibleTodos] = useState<Todo[]>([]);
  useEffect(() => {
    setVisibleTodos(todos.filter(t => !t.completed));
  }, [todos]);
}

// GOOD - Compute during render
function TodoList({ todos }: { todos: Todo[] }) {
  const visibleTodos = todos.filter(t => !t.completed);
}
```

### useMemo for Expensive Computations

```typescript
import { useMemo } from 'react';

function DataTable({ data }: { data: Item[] }) {
  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => a.name.localeCompare(b.name));
  }, [data]);
  return <table>{/* render sortedData */}</table>;
}
```

### useCallback for Function Stability

```typescript
import { useCallback } from 'react';

function Parent() {
  const [count, setCount] = useState(0);
  const handleClick = useCallback(() => {
    console.log('Clicked', count);
  }, [count]);
  return <ExpensiveChild onClick={handleClick} />;
}
```

## TypeScript Best Practices

### Generic Components

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => <li key={index}>{renderItem(item)}</li>)}
    </ul>
  );
}
```

### Event Handlers

```typescript
function Form() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };
  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} />
    </form>
  );
}
```

## Common Pitfalls

### Missing Dependencies

```typescript
// WRONG
useEffect(() => { console.log(count); }, []);

// CORRECT
useEffect(() => { console.log(count); }, [count]);
```

### Mutating State

```typescript
// WRONG
items.push(newItem);
setItems(items); // Won't trigger re-render

// CORRECT
setItems([...items, newItem]);
```
