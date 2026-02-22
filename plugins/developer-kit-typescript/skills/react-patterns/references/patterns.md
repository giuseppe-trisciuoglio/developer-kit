# React 19 Features & Advanced Patterns

## React 19 New Features

### use() Hook - Reading Resources

```typescript
import { use } from 'react';

// Reading a Promise in a component
function MessageComponent({ messagePromise }) {
  const message = use(messagePromise);
  return <p>{message}</p>;
}

// Reading Context conditionally
function Button() {
  if (condition) {
    const theme = use(ThemeContext);
    return <button className={theme}>Click</button>;
  }
  return <button>Click</button>;
}
```

### useFormStatus Hook - Form State

```typescript
import { useFormStatus } from 'react';

function SubmitButton() {
  const { pending, data } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}

function ContactForm() {
  return (
    <form action={submitForm}>
      <input name="email" type="email" />
      <SubmitButton />
    </form>
  );
}
```

### useFormState Hook - Form State Management

```typescript
import { useFormState } from 'react';

async function submitAction(prevState: string | null, formData: FormData) {
  const email = formData.get('email') as string;
  if (!email.includes('@')) return 'Invalid email address';
  await submitToDatabase(email);
  return null;
}

function EmailForm() {
  const [state, formAction] = useFormState(submitAction, null);
  return (
    <form action={formAction}>
      <input name="email" type="email" />
      <button type="submit">Subscribe</button>
      {state && <p className="error">{state}</p>}
    </form>
  );
}
```

### Server Actions

```typescript
// app/actions.ts
'use server';

import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  if (!title || !content) return { error: 'Title and content are required' };

  const post = await db.post.create({ data: { title, content } });
  revalidatePath('/posts');
  redirect(`/posts/${post.id}`);
}
```

### Server Components

```typescript
// Server Component for data fetching
async function PostsPage() {
  const posts = await db.post.findMany({ orderBy: { createdAt: 'desc' }, take: 10 });
  return (
    <div>
      <h1>Latest Posts</h1>
      <PostsList posts={posts} />
    </div>
  );
}

// Client Component for interactivity
'use client';
function PostsList({ posts }: { posts: Post[] }) {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id} onClick={() => setSelectedId(post.id)}
            className={selectedId === post.id ? 'selected' : ''}>
          {post.title}
        </li>
      ))}
    </ul>
  );
}
```

### Server Actions with Validation

```typescript
'use server';
import { z } from 'zod';

const checkoutSchema = z.object({
  items: z.array(z.object({
    productId: z.string(),
    quantity: z.number().min(1)
  })),
  shippingAddress: z.object({
    street: z.string().min(1),
    city: z.string().min(1),
    zipCode: z.string().regex(/^\d{5}$/)
  }),
  paymentMethod: z.enum(['credit', 'paypal', 'apple'])
});

export async function processCheckout(prevState: any, formData: FormData) {
  const rawData = {
    items: JSON.parse(formData.get('items') as string),
    shippingAddress: {
      street: formData.get('street'),
      city: formData.get('city'),
      zipCode: formData.get('zipCode')
    },
    paymentMethod: formData.get('paymentMethod')
  };

  const result = checkoutSchema.safeParse(rawData);
  if (!result.success) {
    return { error: 'Validation failed', fieldErrors: result.error.flatten().fieldErrors };
  }

  try {
    const order = await createOrder(result.data);
    revalidatePath('/orders');
    return { success: true, orderId: order.id };
  } catch (error) {
    return { error: 'Payment failed' };
  }
}
```

## React Compiler

### Automatic Optimization

```typescript
// Before React Compiler - manual memoization needed
const ExpensiveComponent = memo(function ExpensiveComponent({ data, onUpdate }) {
  const processedData = useMemo(() => {
    return data.map(item => ({ ...item, computed: expensiveCalculation(item) }));
  }, [data]);
  const handleClick = useCallback((id) => { onUpdate(id); }, [onUpdate]);
  // ...
});

// After React Compiler - no manual optimization needed
function ExpensiveComponent({ data, onUpdate }) {
  const processedData = data.map(item => ({
    ...item, computed: expensiveCalculation(item)
  }));
  const handleClick = (id) => { onUpdate(id); };
  // ...
}
```

### Installation and Setup

```bash
npm install -D babel-plugin-react-compiler@latest
npm install -D eslint-plugin-react-hooks@latest
```

```javascript
// babel.config.js
module.exports = {
  plugins: ['babel-plugin-react-compiler'],
};

// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react({
      babel: { plugins: ['babel-plugin-react-compiler'] },
    }),
  ],
});
```

## Concurrent Features

### useTransition for Non-Urgent Updates

```typescript
import { useTransition, useState } from 'react';

function SearchableList({ items }: { items: Item[] }) {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [filteredItems, setFilteredItems] = useState(items);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    startTransition(() => {
      setFilteredItems(items.filter(item =>
        item.name.toLowerCase().includes(e.target.value.toLowerCase())
      ));
    });
  };

  return (
    <div>
      <input type="text" value={query} onChange={handleChange} />
      {isPending && <div>Filtering...</div>}
      <ul>{filteredItems.map(item => <li key={item.id}>{item.name}</li>)}</ul>
    </div>
  );
}
```

### useDeferredValue for Expensive UI

```typescript
import { useDeferredValue, useMemo } from 'react';

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
      <input value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
      <DataGridRows data={filteredData} isStale={searchTerm !== deferredSearchTerm} />
    </div>
  );
}
```

## Testing React 19 Features

### Testing Server Actions

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import ContactForm from './ContactForm';

describe('ContactForm', () => {
  it('submits form with server action', async () => {
    render(<ContactForm />);
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.click(screen.getByText('Submit'));
    expect(mockSubmitForm).toHaveBeenCalledWith(expect.any(FormData));
  });
});
```

## Migration Guide: React 18 to 19

1. **Update Dependencies**: `npm install react@19 react-dom@19`
2. **Adopt Server Components**: Identify data-fetching components, remove client-side code
3. **Replace Manual Optimistic Updates**: Use `useOptimistic` hook
4. **Enable React Compiler**: Install babel-plugin-react-compiler, remove manual memoization

## React 19 Pitfalls

```typescript
// WRONG: using use() outside of render
function handleClick() { const data = use(promise); }

// CORRECT: called during render
function Component({ promise }) {
  const data = use(promise);
  return <div>{data}</div>;
}

// WRONG: missing 'use server'
export async function myAction() { /* runs on client */ }

// CORRECT
'use server';
export async function myAction() { /* runs on server */ }

// WRONG: browser APIs in Server Component
export default async function ServerComponent() {
  const width = window.innerWidth; // Error
}

// CORRECT: separate concerns
export default async function ServerComponent() {
  const data = await fetchData();
  return <ClientComponent data={data} />;
}
```
