---
name: react-patterns
description: Provides comprehensive React 19 patterns covering Server Components, Actions, use() hook, useOptimistic, useFormStatus, useFormState, React Compiler, concurrent features, Suspense, and modern TypeScript development. Proactively use for any React development, component architecture, state management, performance optimization, or when implementing React 19's latest features.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# React Development Patterns

## Overview

Expert guide for building modern React 19 applications with new concurrent features, Server Components, Actions, and advanced patterns. Covers everything from basic hooks to advanced server-side rendering and React Compiler optimization.

## When to Use

- Building React 19 components with TypeScript/JavaScript
- Managing component state with useState, useReducer, useRef
- Handling side effects with useEffect
- Optimizing performance with useMemo and useCallback
- Creating custom hooks for reusable logic
- Using React 19's new features (use(), useOptimistic, useFormStatus)
- Implementing Server Components and Actions
- Working with Suspense and concurrent rendering

## Instructions

1. **Identify Component Type**: Determine if Server Component or Client Component is needed
2. **Start with Hooks**: Use appropriate hooks for state management and side effects
3. **Implement Component Logic**: Build component with proper TypeScript typing
4. **Add Event Handlers**: Create stable references with useCallback where needed
5. **Optimize Performance**: Use useMemo for expensive computations
6. **Handle Errors**: Implement error boundaries for graceful error handling

## Examples

### Server Component with Client Interaction

```tsx
// Server Component (default)
async function ProductPage({ id }: { id: string }) {
  const product = await db.product.findUnique({ where: { id } });
  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={product.id} />
    </div>
  );
}

// Client Component
'use client';
import { useTransition } from 'react';

function AddToCartButton({ productId }: { productId: string }) {
  const [isPending, startTransition] = useTransition();
  const handleAdd = () => {
    startTransition(async () => { await addToCart(productId); });
  };
  return (
    <button onClick={handleAdd} disabled={isPending}>
      {isPending ? 'Adding...' : 'Add to Cart'}
    </button>
  );
}
```

### React 19 useOptimistic

```typescript
import { useOptimistic } from 'react';

function TodoList({ todos, addTodo }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, newTodo]
  );

  const handleSubmit = async (formData) => {
    const newTodo = { id: Date.now(), text: formData.get('text') };
    addOptimisticTodo(newTodo);
    await addTodo(newTodo);
  };

  return (
    <form action={handleSubmit}>
      {optimisticTodos.map(todo => <div key={todo.id}>{todo.text}</div>)}
      <input type="text" name="text" />
      <button type="submit">Add Todo</button>
    </form>
  );
}
```

## Constraints and Warnings

- **Server vs Client**: Server Components cannot use hooks, event handlers, or browser APIs
- **use() Hook**: Can only be called during render, not in callbacks or effects
- **Server Actions**: Must include 'use server' directive at the top of the file
- **State Mutations**: Never mutate state directly; always create new references
- **Effect Dependencies**: Always include all dependencies in useEffect arrays
- **Key Stability**: Use stable IDs for list keys, not array indices
- **Memory Leaks**: Always clean up subscriptions and event listeners in useEffect

## Best Practices

### General
1. Specify correct dependencies in useEffect
2. Keep state minimal and avoid redundant state
3. Keep components small and focused
4. Extract complex logic into reusable custom hooks
5. Use TypeScript for type safety
6. Never mutate state directly
7. Use effects only for synchronization with external systems

### React 19 Specific
1. Use Server Components for data fetching and static content
2. Mark components as 'use client' only when necessary
3. Use Server Actions for mutations and form submissions
4. Implement useOptimistic for better UX
5. Use useFormState and useFormStatus for complex forms
6. Leverage useTransition for non-urgent updates

## References

Consult these files for detailed patterns and examples:

- **[references/examples.md](references/examples.md)** - Core hooks (useState, useEffect, useRef), custom hooks, component composition, TypeScript patterns, common patterns
- **[references/patterns.md](references/patterns.md)** - React 19 features (use(), useFormStatus, useFormState, Server Actions, Server Components), React Compiler, concurrent features, testing, migration guide
- **[references/learn.md](references/learn.md)** - Learning resources
- **[references/reference.md](references/reference.md)** - API reference

### External References
- React 19 Official Docs: https://react.dev/blog/2024/04/25/react-19
- React Server Components: https://react.dev/reference/rsc/server-components
- React Compiler: https://react.dev/learn/react-compiler
- TypeScript with React: https://react-typescript-cheatsheet.netlify.app/
