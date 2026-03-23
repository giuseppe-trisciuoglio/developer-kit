---
name: react-patterns
description: Provides comprehensive React 19 patterns covering Server Components, Actions, use() hook, useOptimistic, useFormStatus, useFormState, React Compiler, concurrent features, Suspense, and modern TypeScript development. Proactively use for any React development, component architecture, state management, performance optimization, or when implementing React 19's latest features.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# React Development Patterns

Build modern React 19 applications with Server Components, Actions, concurrent features, and TypeScript.

## When to Use

- Building React 19 components with TypeScript/JavaScript
- Managing component state with hooks (useState, useReducer, useContext)
- Implementing React 19 features (use(), useOptimistic, useFormStatus, useActionState)
- Optimizing performance with useMemo, useCallback, or React Compiler
- Creating custom hooks for reusable logic
- Working with Server Components, Server Actions, and Suspense
- Building forms with new form hooks and server-side mutations

## Quick Reference

| Pattern | Hook / API | Use Case |
|---------|-----------|----------|
| Local state | `useState` | Simple component state |
| Complex state | `useReducer` | Multi-action state machines |
| Side effects | `useEffect` | Subscriptions, data fetching |
| Shared state | `useContext` / `createContext` | Cross-component data |
| DOM access | `useRef` | Focus, measurements, timers |
| Performance | `useMemo` / `useCallback` | Expensive computations |
| Non-urgent updates | `useTransition` | Search/filter on large lists |
| Defer expensive UI | `useDeferredValue` | Stale-while-updating |
| Read resources | `use()` (React 19) | Promises and context in render |
| Optimistic UI | `useOptimistic` (React 19) | Instant feedback on mutations |
| Form status | `useFormStatus` (React 19) | Pending state in child components |
| Form state | `useActionState` (React 19) | Server action results |
| Auto-memoization | React Compiler | Eliminates manual memo/callback |

## Instructions

1. **Identify Component Type**: Determine if Server Component or Client Component is needed
2. **Select Hooks**: Use appropriate hooks for state management and side effects
3. **Type Props**: Define TypeScript interfaces for all component props
4. **Handle Async**: Wrap data-fetching components in Suspense boundaries
5. **Optimize**: Use React Compiler or manual memoization for expensive renders
6. **Handle Errors**: Add ErrorBoundary for graceful error handling

## Examples

### Server Component with Client Interaction

```tsx
// Server Component (default) — async, fetches data
async function ProductPage({ id }: { id: string }) {
  const product = await db.product.findUnique({ where: { id } });

  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={product.id} />
    </div>
  );
}

// Client Component — handles interactivity
'use client';
function AddToCartButton({ productId }: { productId: string }) {
  const [isPending, startTransition] = useTransition();

  const handleAdd = () => {
    startTransition(async () => {
      await addToCart(productId);
    });
  };

  return (
    <button onClick={handleAdd} disabled={isPending}>
      {isPending ? 'Adding...' : 'Add to Cart'}
    </button>
  );
}
```

### useOptimistic for Instant Feedback

```tsx
'use client';
import { useOptimistic } from 'react';

function TodoList({ todos, addTodo }: { todos: Todo[]; addTodo: (t: Todo) => Promise<void> }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, { ...newTodo, pending: true }]
  );

  const handleSubmit = async (formData: FormData) => {
    const newTodo = { id: Date.now(), text: formData.get('text') as string };
    addOptimisticTodo(newTodo);  // Immediate UI update
    await addTodo(newTodo);      // Actual backend call
  };

  return (
    <form action={handleSubmit}>
      {optimisticTodos.map(todo => (
        <div key={todo.id} style={{ opacity: todo.pending ? 0.5 : 1 }}>
          {todo.text}
        </div>
      ))}
      <input type="text" name="text" />
      <button type="submit">Add</button>
    </form>
  );
}
```

### Server Action with Form

```tsx
// app/actions.ts
'use server';
import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const schema = z.object({
  title: z.string().min(5),
  content: z.string().min(10),
});

export async function createPost(prevState: any, formData: FormData) {
  const parsed = schema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  });

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  await db.post.create({ data: parsed.data });
  revalidatePath('/posts');
  return { success: true };
}

// app/blog/new/page.tsx
'use client';
import { useActionState } from 'react';
import { createPost } from '../actions';

export default function NewPostPage() {
  const [state, formAction, pending] = useActionState(createPost, {});

  return (
    <form action={formAction}>
      <input name="title" placeholder="Title" />
      {state.errors?.title && <span>{state.errors.title[0]}</span>}
      <textarea name="content" placeholder="Content" />
      <button type="submit" disabled={pending}>
        {pending ? 'Publishing...' : 'Publish'}
      </button>
    </form>
  );
}
```

### Custom Hook

```tsx
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
```

### useTransition for Non-Urgent Updates

```tsx
function SearchableList({ items }: { items: Item[] }) {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [filteredItems, setFilteredItems] = useState(items);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    startTransition(() => {
      setFilteredItems(items.filter(i => i.name.toLowerCase().includes(e.target.value.toLowerCase())));
    });
  };

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <span>Filtering...</span>}
      <ul>{filteredItems.map(i => <li key={i.id}>{i.name}</li>)}</ul>
    </div>
  );
}
```

## Best Practices

### Server vs Client Decision

- Start with Server Component (no directive needed)
- Add `'use client'` only for: hooks, browser APIs, event handlers

### State Management

- Keep state minimal — compute derived values during render, not in effects
- Use `useReducer` for state with multiple related actions
- Lift state up to the nearest common ancestor

### Effects

- Use effects only for external system synchronization
- Always specify correct dependency arrays
- Return cleanup functions for subscriptions and timers
- Never mutate state directly — always create new references

### Performance

- With React Compiler: avoid manual `useMemo`, `useCallback`, `memo`
- Without React Compiler: use `useMemo` for expensive computations, `useCallback` for stable callbacks
- Use `useTransition` for low-priority state updates
- Use stable IDs as list keys, not array indices

### React 19 Specifics

- Wrap `use(promise)` components in Suspense boundaries
- Use `useActionState` for form-server action integration
- Validate Server Action inputs — they are public endpoints
- Pass serializable data from Server to Client Components

## Constraints and Warnings

- **Server Components**: Cannot use hooks, event handlers, or browser APIs
- **use() Hook**: Can only be called during render, not in callbacks or effects
- **Server Actions**: Must include `'use server'` directive; always validate inputs
- **State Mutations**: Never mutate state directly — always create new references
- **Effect Dependencies**: Include all dependencies in `useEffect` dependency arrays
- **Memory Leaks**: Always clean up subscriptions and event listeners in useEffect return

## References

Consult these files for detailed patterns:

- **[references/hooks-patterns.md](references/hooks-patterns.md)** — useState, useEffect, useRef, useReducer, custom hooks, common pitfalls
- **[references/component-patterns.md](references/component-patterns.md)** — Props, composition, lifting state, context, compound components, error boundaries
- **[references/react19-features.md](references/react19-features.md)** — use(), useOptimistic, useFormStatus, useActionState, Server Actions, Server Components, migration guide
- **[references/performance-patterns.md](references/performance-patterns.md)** — React Compiler setup, useMemo, useCallback, useTransition, useDeferredValue, lazy loading
- **[references/typescript-patterns.md](references/typescript-patterns.md)** — Typed props, generic components, event handlers, discriminated unions, context typing
- **[references/learn.md](references/learn.md)** — Progressive learning guide from basics to advanced React 19
- **[references/reference.md](references/reference.md)** — Complete API reference for all React hooks and component APIs
