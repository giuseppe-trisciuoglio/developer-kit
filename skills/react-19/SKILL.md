---
name: react-19-patterns
description: Expert patterns for React 19 including hooks (useState, useEffect, useRef, useCallback, useMemo), component composition, state management, effects, and modern React development best practices. Use when building React components, managing state, handling side effects, or implementing React patterns.
language: typescript,javascript
framework: react
license: MIT
---

# React 19 Development Patterns

Expert guide for building modern React 19 applications with hooks, component composition, and best practices.

## When to Use

- Building React 19 components with TypeScript/JavaScript
- Managing component state with useState and useReducer
- Handling side effects with useEffect
- Optimizing performance with useMemo and useCallback
- Creating custom hooks for reusable logic
- Implementing component composition patterns
- Working with refs using useRef

## Core Hooks Patterns

### useState - State Management

Basic state declaration and updates:

```typescript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

State with initializer function (expensive computation):

```typescript
const [state, setState] = useState(() => {
  const initialState = computeExpensiveValue();
  return initialState;
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
    
    // Cleanup function
    return () => {
      connection.disconnect();
    };
  }, [roomId]); // Dependency array
  
  return <div>Connected to {roomId}</div>;
}
```

Effect with multiple dependencies:

```typescript
function ChatRoom({ roomId, serverUrl }: { roomId: string; serverUrl: string }) {
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    
    return () => connection.disconnect();
  }, [roomId, serverUrl]); // Re-run when either changes
  
  return <h1>Welcome to {roomId}</h1>;
}
```

Effect for subscriptions:

```typescript
function StatusBar() {
  const [isOnline, setIsOnline] = useState(true);
  
  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
    }
    
    function handleOffline() {
      setIsOnline(false);
    }
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []); // Empty array = run once on mount
  
  return <h1>{isOnline ? '✅ Online' : '❌ Disconnected'}</h1>;
}
```

### useRef - Persistent References

Storing mutable values without re-renders:

```typescript
import { useRef } from 'react';

function Timer() {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const startTimer = () => {
    intervalRef.current = setInterval(() => {
      console.log('Tick');
    }, 1000);
  };
  
  const stopTimer = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
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

## Custom Hooks Pattern

Extract reusable logic into custom hooks:

```typescript
// useOnlineStatus.ts
import { useState, useEffect } from 'react';

export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);
  
  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
    }
    
    function handleOffline() {
      setIsOnline(false);
    }
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return isOnline;
}

// Usage in components
function StatusBar() {
  const isOnline = useOnlineStatus();
  return <h1>{isOnline ? '✅ Online' : '❌ Disconnected'}</h1>;
}

function SaveButton() {
  const isOnline = useOnlineStatus();
  return (
    <button disabled={!isOnline}>
      {isOnline ? 'Save' : 'Reconnecting...'}
    </button>
  );
}
```

Custom hook with parameters:

```typescript
// useChatRoom.ts
import { useEffect } from 'react';

interface ChatOptions {
  serverUrl: string;
  roomId: string;
}

export function useChatRoom({ serverUrl, roomId }: ChatOptions) {
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    
    return () => connection.disconnect();
  }, [serverUrl, roomId]);
}

// Usage
function ChatRoom({ roomId }: { roomId: string }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');
  
  useChatRoom({ serverUrl, roomId });
  
  return (
    <>
      <input value={serverUrl} onChange={e => setServerUrl(e.target.value)} />
      <h1>Welcome to {roomId}</h1>
    </>
  );
}
```

## Component Composition Patterns

### Props and Children

Basic component with props:

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  children: React.ReactNode;
}

function Button({ variant = 'primary', size = 'md', onClick, children }: ButtonProps) {
  return (
    <button 
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

Composition with children:

```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {children}
    </div>
  );
}

// Usage
function UserProfile() {
  return (
    <Card>
      <h2>John Doe</h2>
      <p>Software Engineer</p>
    </Card>
  );
}
```

### Lifting State Up

Shared state between siblings:

```typescript
function Parent() {
  const [activeIndex, setActiveIndex] = useState(0);
  
  return (
    <>
      <Panel
        isActive={activeIndex === 0}
        onShow={() => setActiveIndex(0)}
      >
        Panel 1 content
      </Panel>
      <Panel
        isActive={activeIndex === 1}
        onShow={() => setActiveIndex(1)}
      >
        Panel 2 content
      </Panel>
    </>
  );
}

interface PanelProps {
  isActive: boolean;
  onShow: () => void;
  children: React.ReactNode;
}

function Panel({ isActive, onShow, children }: PanelProps) {
  return (
    <div>
      <button onClick={onShow}>Show</button>
      {isActive && <div>{children}</div>}
    </div>
  );
}
```

## Performance Optimization

### Avoid Unnecessary Effects

❌ Bad - Using effect for derived state:

```typescript
function TodoList({ todos }: { todos: Todo[] }) {
  const [visibleTodos, setVisibleTodos] = useState<Todo[]>([]);
  
  useEffect(() => {
    setVisibleTodos(todos.filter(t => !t.completed));
  }, [todos]); // Unnecessary effect
  
  return <ul>{/* ... */}</ul>;
}
```

✅ Good - Compute during render:

```typescript
function TodoList({ todos }: { todos: Todo[] }) {
  const visibleTodos = todos.filter(t => !t.completed); // Direct computation
  
  return <ul>{/* ... */}</ul>;
}
```

### useMemo for Expensive Computations

```typescript
import { useMemo } from 'react';

function DataTable({ data }: { data: Item[] }) {
  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => a.name.localeCompare(b.name));
  }, [data]); // Only recompute when data changes
  
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
  }, [count]); // Recreate only when count changes
  
  return <ExpensiveChild onClick={handleClick} />;
}
```

## TypeScript Best Practices

### Type-Safe Props

```typescript
interface UserProps {
  id: string;
  name: string;
  email: string;
  age?: number; // Optional
}

function User({ id, name, email, age }: UserProps) {
  return (
    <div>
      <h2>{name}</h2>
      <p>{email}</p>
      {age && <p>Age: {age}</p>}
    </div>
  );
}
```

### Generic Components

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Usage
<List 
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
/>
```

### Event Handlers

```typescript
function Form() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle form submission
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

## Common Patterns

### Controlled Components

```typescript
function ControlledInput() {
  const [value, setValue] = useState('');
  
  return (
    <input 
      value={value}
      onChange={e => setValue(e.target.value)}
    />
  );
}
```

### Conditional Rendering

```typescript
function Greeting({ isLoggedIn }: { isLoggedIn: boolean }) {
  return (
    <div>
      {isLoggedIn ? (
        <UserGreeting />
      ) : (
        <GuestGreeting />
      )}
    </div>
  );
}
```

### Lists and Keys

```typescript
function UserList({ users }: { users: User[] }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          {user.name}
        </li>
      ))}
    </ul>
  );
}
```

## Best Practices

1. **Dependency Arrays**: Always specify correct dependencies in useEffect
2. **State Structure**: Keep state minimal and avoid redundant state
3. **Component Size**: Keep components small and focused
4. **Custom Hooks**: Extract complex logic into reusable custom hooks
5. **TypeScript**: Use TypeScript for type safety
6. **Keys**: Use stable IDs as keys for list items, not array indices
7. **Immutability**: Never mutate state directly
8. **Effects**: Use effects only for synchronization with external systems
9. **Performance**: Profile before optimizing with useMemo/useCallback

## Common Pitfalls

❌ **Missing Dependencies**:
```typescript
useEffect(() => {
  // Uses 'count' but doesn't include it in deps
  console.log(count);
}, []); // Wrong!
```

❌ **Mutating State**:
```typescript
const [items, setItems] = useState([]);
items.push(newItem); // Wrong! Mutates state
setItems(items); // Won't trigger re-render
```

✅ **Correct Approach**:
```typescript
setItems([...items, newItem]); // Create new array
```

## References

- React Official Docs: https://react.dev
- React Hooks Reference: https://react.dev/reference/react
- TypeScript with React: https://react-typescript-cheatsheet.netlify.app/
