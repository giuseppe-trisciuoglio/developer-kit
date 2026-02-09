# React Learning Guide

Progressive learning path from React basics to advanced React 19 features.

## Getting Started

### Installation

Choose one of the following methods to start a new React project:

```bash
# Create React App (traditional)
npx create-react-app my-app
cd my-app

# Vite (recommended for new projects)
npm create vite@latest my-app -- --template react
cd my-app
npm install

# Next.js (full-stack React)
npx create-next-app@latest

# React Router (new v7 full-stack)
npx create-react-router@latest
```

### Basic Concepts

#### Your First Component

```jsx
// MyComponent.js
function MyComponent() {
  return <h1>Hello, React!</h1>;
}

export default MyComponent;
```

#### Using Components

```jsx
// App.js
import MyComponent from './MyComponent';

function App() {
  return (
    <div>
      <MyComponent />
      <p>Welcome to React</p>
    </div>
  );
}
```

#### JSX Rules

1. **Single Parent Element**: Components must return one parent element
   ```jsx
   // Use fragments to avoid extra divs
   return (
     <>
       <h1>Title</h1>
       <p>Content</p>
     </>
   );
   ```

2. **Close All Tags**: All tags must be closed
   ```jsx
   <img src="image.jpg" alt="description" />
   <br />
   ```

3. **camelCase Properties**: HTML attributes become camelCase
   ```jsx
   <div className="container">
     <input readOnly={true} />
   </div>
   ```

## Core Concepts

### Props - Passing Data to Components

```jsx
// Greeting.js
function Greeting({ name, age }) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      <p>You are {age} years old.</p>
    </div>
  );
}

// Usage
<Greeting name="Alice" age={30} />
```

### State - Managing Component Data

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

### Handling Events

```jsx
function Button() {
  const handleClick = () => {
    alert('Button clicked!');
  };

  const handleMouseOver = () => {
    console.log('Mouse is over button');
  };

  return (
    <button
      onClick={handleClick}
      onMouseOver={handleMouseOver}
    >
      Click me
    </button>
  );
}
```

### Conditional Rendering

```jsx
function Welcome({ isLoggedIn }) {
  if (isLoggedIn) {
    return <h1>Welcome back!</h1>;
  }
  return <h1>Please sign in.</h1>;
}

// Using ternary operator
function Status({ status }) {
  return (
    <div>
      {status === 'loading' ? (
        <p>Loading...</p>
      ) : status === 'success' ? (
        <p>Success!</p>
      ) : (
        <p>Error occurred</p>
      )}
    </div>
  );
}

// Using logical AND
function Notification({ message }) {
  return (
    <div>
      {message && <p className="notification">{message}</p>}
    </div>
  );
}
```

### Lists and Keys

```jsx
function ShoppingList({ items }) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={item.id}>
          {item.name} - ${item.price}
        </li>
      ))}
    </ul>
  );
}

// Data
const items = [
  { id: 1, name: 'Bread', price: 2.50 },
  { id: 2, name: 'Milk', price: 3.00 },
  { id: 3, name: 'Eggs', price: 4.50 }
];
```

## Working with Forms

### Controlled Components

```jsx
import { useState } from 'react';

function Form() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Submitted:', { name, email });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>
          Name:
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
      </div>
      <div>
        <label>
          Email:
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}
```

### React 19 Form Actions

```jsx
// server/actions.js
'use server';

export async function createContact(formData) {
  const name = formData.get('name');
  const email = formData.get('email');

  // Save to database
  await db.contacts.create({ name, email });

  return { success: true };
}

// components/ContactForm.js
'use client';

import { useFormState } from 'react';
import { createContact } from '../server/actions';

function ContactForm() {
  const [state, formAction] = useFormState(createContact, null);

  return (
    <form action={formAction}>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <button type="submit">Add Contact</button>
      {state?.success && <p>Contact added!</p>}
    </form>
  );
}
```

## Side Effects with useEffect

### Basic Usage

```jsx
import { useState, useEffect } from 'react';

function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(s => s + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <p>Timer: {seconds}s</p>;
}
```

### Data Fetching

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;

    async function fetchUser() {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        if (!ignore) {
          setUser(userData);
        }
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    fetchUser();

    return () => {
      ignore = true;
    };
  }, [userId]);

  if (loading) return <p>Loading...</p>;
  if (!user) return <p>User not found</p>;

  return <div>{user.name}</div>;
}
```

## Advanced Patterns

### Custom Hooks

```jsx
// hooks/useLocalStorage.js
import { useState } from 'react';

export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
}

// Usage
import { useLocalStorage } from './hooks/useLocalStorage';

function App() {
  const [name, setName] = useLocalStorage('name', '');

  return (
    <input
      value={name}
      onChange={(e) => setName(e.target.value)}
      placeholder="Enter your name"
    />
  );
}
```

### Context for State Management

```jsx
// contexts/ThemeContext.js
import { createContext, useContext } from 'react';

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// Usage
function App() {
  return (
    <ThemeProvider>
      <Header />
      <Main />
    </ThemeProvider>
  );
}

function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <header className={theme}>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        Toggle Theme
      </button>
    </header>
  );
}
```

## React 19 Features

### use() Hook for Resources

```jsx
import { Suspense, use } from 'react';

// Data fetching function
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

function UserProfile({ userId }) {
  // Directly use the promise in component
  const user = use(fetchUser(userId));

  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<div>Loading profile...</div>}>
      <UserProfile userId="123" />
    </Suspense>
  );
}
```

### useOptimistic for Optimistic UI

```jsx
import { useOptimistic } from 'react';

function TodoList({ todos, addTodo }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, { ...newTodo, pending: true }]
  );

  const handleSubmit = async (formData) => {
    const text = formData.get('text');
    const newTodo = { id: Date.now(), text };

    // Add optimistically
    addOptimisticTodo(newTodo);

    // Actually add
    await addTodo(newTodo);
  };

  return (
    <div>
      <form action={handleSubmit}>
        <input name="text" placeholder="Add todo..." />
        <button type="submit">Add</button>
      </form>

      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id} style={{ opacity: todo.pending ? 0.5 : 1 }}>
            {todo.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### useFormStatus for Form States

```jsx
'use client';

import { useFormStatus } from 'react';

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}

function ContactForm() {
  return (
    <form action={submitContact}>
      <input name="email" type="email" required />
      <textarea name="message" required />
      <SubmitButton />
    </form>
  );
}
```

## Server Components (React 19)

### Server vs Client Components

```jsx
// Server Component (default)
// This runs on the server
async function BlogPost({ id }) {
  const post = await fetchPost(id); // Can directly await
  const comments = await fetchComments(id);

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
      <CommentForm postId={id} />
      <CommentsList comments={comments} />
    </article>
  );
}

// Client Component
'use client';
import { useState } from 'react';

function CommentForm({ postId }) {
  const [comment, setComment] = useState('');

  // Client-side interactivity
  return (
    <form action={addComment}>
      <input
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Write a comment..."
      />
      <button type="submit">Post</button>
    </form>
  );
}
```

## Performance Optimization

### Code Splitting

```jsx
import { lazy, Suspense } from 'react';

// Lazy load component
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <LazyComponent />
      </Suspense>
    </div>
  );
}
```

### React.memo for Component Memoization

```jsx
import { memo } from 'react';

const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  return <div>{/* Expensive rendering */}</div>;
});

// Custom comparison
const ListComponent = memo(List, (prevProps, nextProps) => {
  // Only re-render if items length changed
  return prevProps.items.length === nextProps.items.length;
});
```

### useMemo and useCallback

```jsx
import { useMemo, useCallback } from 'react';

function Parent({ items, onItemClick }) {
  const expensiveValue = useMemo(() => {
    return items.reduce((sum, item) => sum + item.value, 0);
  }, [items]);

  const handleClick = useCallback((id) => {
    onItemClick(id);
  }, [onItemClick]);

  return (
    <div>
      <p>Total: {expensiveValue}</p>
      <Child items={items} onClick={handleClick} />
    </div>
  );
}
```

## Testing React Components

### Basic Testing

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Counter from './Counter';

test('increments counter', () => {
  render(<Counter />);

  const button = screen.getByText('Increment');
  const count = screen.getByText('Count: 0');

  fireEvent.click(button);

  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

### Testing Custom Hooks

```jsx
import { renderHook, act } from '@testing-library/react';
import useCounter from './useCounter';

test('should increment counter', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});
```

## Best Practices

### Do's

1. **Use Functional Components** with hooks
2. **Keep Components Small** and focused
3. **Extract Logic** into custom hooks
4. **Use TypeScript** for type safety
5. **Write Tests** for components
6. **Optimize Only When Necessary** - profile first

### Don'ts

1. **Don't Mutate State** directly
2. **Don't Use Index as Key** for lists with additions/removals
3. **Don't Create Functions** in render (use useCallback)
4. **Don't Ignore ESLint Rules** for React hooks
5. **Don't Over-optimize** prematurely

## Common Patterns

### Compound Components

```jsx
function Menu({ children }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <MenuContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="menu">{children}</div>
    </MenuContext.Provider>
  );
}

function MenuButton({ children }) {
  const { isOpen, setIsOpen } = useContext(MenuContext);

  return (
    <button onClick={() => setIsOpen(!isOpen)}>
      {children}
    </button>
  );
}

function MenuItems({ children }) {
  const { isOpen } = useContext(MenuContext);

  return isOpen ? <ul>{children}</ul> : null;
}

// Usage
<Menu>
  <MenuButton>Open Menu</MenuButton>
  <MenuItems>
    <li>Item 1</li>
    <li>Item 2</li>
  </MenuItems>
</Menu>
```

### Render Props

```jsx
function MouseTracker({ render }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    setPosition({ x: e.clientX, y: e.clientY });
  };

  return (
    <div onMouseMove={handleMouseMove}>
      {render(position)}
    </div>
  );
}

// Usage
<MouseTracker
  render={({ x, y }) => (
    <h1>Mouse position: {x}, {y}</h1>
  )}
/>
```

## Learning Resources

### Documentation
- [Official React Documentation](https://react.dev)
- [React 19 Blog Post](https://react.dev/blog/2024/04/25/react-19)
- [TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

### Practice Projects
1. **Todo App** - Basic state management
2. **Weather App** - API integration
3. **E-commerce Site** - Complex state and routing
4. **Chat Application** - Real-time updates
5. **Blog Platform** - Server Components

### Common Interview Questions
1. What is the virtual DOM?
2. How does React reconcile changes?
3. What are hooks and why were they introduced?
4. Explain useEffect and its dependency array
5. What's the difference between controlled and uncontrolled components?
6. How do you optimize React performance?
7. What are Server Components in React 19?

## Next Steps

1. **Master the Basics**: Components, props, state, events
2. **Learn Hooks**: useState, useEffect, useContext, custom hooks
3. **Explore Ecosystem**: React Router, Redux, React Query
4. **Study Advanced Topics**: Performance, testing, patterns
5. **Stay Updated**: React 19 features, Server Components, React Compiler

Remember: The best way to learn React is by building projects. Start small and gradually increase complexity as you become more comfortable with the concepts.