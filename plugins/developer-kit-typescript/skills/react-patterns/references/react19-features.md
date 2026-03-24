# React 19 Features

Patterns for React 19's new hooks, Server Components, Server Actions, and form handling.

## use() Hook

Read a Promise or Context value during render:

```typescript
import { use } from 'react';

// Reading a Promise
function MessageComponent({ messagePromise }: { messagePromise: Promise<string> }) {
  const message = use(messagePromise);
  return <p>{message}</p>;
}

// Reading Context conditionally (unlike useContext, can be called in conditionals)
function Button({ condition }: { condition: boolean }) {
  if (condition) {
    const theme = use(ThemeContext);
    return <button className={theme}>Click</button>;
  }
  return <button>Click</button>;
}
```

Must be wrapped in Suspense when reading promises:

```typescript
function App() {
  const messagePromise = fetchMessage();
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <MessageComponent messagePromise={messagePromise} />
    </Suspense>
  );
}
```

## useOptimistic

Optimistic UI updates for async operations:

```typescript
import { useOptimistic } from 'react';

function TodoList({ todos, addTodo }: { todos: Todo[]; addTodo: (t: Todo) => Promise<void> }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, { ...newTodo, pending: true }]
  );

  const handleSubmit = async (formData: FormData) => {
    const newTodo = { id: Date.now(), text: formData.get('text') as string };
    addOptimisticTodo(newTodo); // Immediate UI update
    await addTodo(newTodo);     // Actual backend call
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

## useFormStatus

Access form submission status in child components:

```typescript
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
    <form action={submitForm}>
      <input name="email" type="email" />
      <SubmitButton /> {/* Must be inside the <form> */}
    </form>
  );
}
```

## useFormState / useActionState

Manage form state with server action results:

```typescript
import { useFormState } from 'react'; // React 19: useActionState

async function submitAction(prevState: string | null, formData: FormData) {
  const email = formData.get('email') as string;

  if (!email.includes('@')) {
    return 'Invalid email address';
  }

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

## Server Actions

Define server-side functions for mutations and form handling:

```typescript
// app/actions.ts
'use server';

import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  if (!title || !content) {
    return { error: 'Title and content are required' };
  }

  const post = await db.post.create({ data: { title, content } });

  revalidatePath('/posts');
  redirect(`/posts/${post.id}`);
}
```

Server Action with Zod validation:

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
    return {
      error: 'Validation failed',
      fieldErrors: result.error.flatten().fieldErrors
    };
  }

  try {
    const order = await createOrder(result.data);
    await updateInventory(result.data.items);
    await sendConfirmationEmail(order);
    revalidatePath('/orders');
    return { success: true, orderId: order.id };
  } catch {
    return { error: 'Payment failed' };
  }
}
```

## Server Components

Components that run exclusively on the server:

```typescript
// app/posts/page.tsx — Server Component (default)
async function PostsPage() {
  const posts = await db.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 10
  });

  return (
    <div>
      <h1>Latest Posts</h1>
      <PostsList posts={posts} />
    </div>
  );
}
```

Mixed Server/Client architecture:

```typescript
// Server Component — handles data fetching
async function ProductPage({ id }: { id: string }) {
  const product = await fetchProduct(id);
  const related = await fetchRelatedProducts(id);

  return (
    <div>
      <ProductDetails product={product} />
      <RelatedProducts products={related} />
    </div>
  );
}

// Client Component — handles interactivity
'use client';

function ProductDetails({ product }: { product: Product }) {
  const [quantity, setQuantity] = useState(1);
  const [isAdded, setIsAdded] = useState(false);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>${product.price}</p>
      <input type="number" value={quantity} onChange={e => setQuantity(Number(e.target.value))} min="1" />
      <AddToCartButton productId={product.id} quantity={quantity} onAdded={() => setIsAdded(true)} />
      {isAdded && <p>Added to cart!</p>}
    </div>
  );
}
```

## Migration from React 18 to 19

1. Update dependencies:
```bash
npm install react@19 react-dom@19
```

2. Replace manual optimistic updates with `useOptimistic`:

```typescript
// Before (React 18)
function TodoList({ todos, addTodo }) {
  const [optimisticTodos, setOptimisticTodos] = useState(todos);

  const handleAdd = async (text) => {
    const newTodo = { id: Date.now(), text };
    setOptimisticTodos([...optimisticTodos, newTodo]);
    await addTodo(newTodo);
  };
}

// After (React 19)
function TodoList({ todos, addTodo }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, newTodo]
  );

  const handleAdd = async (formData) => {
    const newTodo = { id: Date.now(), text: formData.get('text') };
    addOptimisticTodo(newTodo);
    await addTodo(newTodo);
  };
}
```

3. Enable React Compiler and remove manual memoization (see performance-patterns.md)

## Common Pitfalls

```typescript
// Wrong: use() outside render
function handleClick() {
  const data = use(promise); // Error: can only be called in render
}

// Correct
function Component({ promise }) {
  const data = use(promise); // Called during render
  return <div>{data}</div>;
}

// Wrong: missing 'use server'
export async function myAction() {
  // This runs on the client!
}

// Correct
'use server';
export async function myAction() {
  // Runs on the server
}

// Wrong: browser APIs in Server Component
export default async function ServerComponent() {
  const width = window.innerWidth; // Error: window is not defined
  return <div>{width}</div>;
}

// Correct: delegate to Client Component
export default async function ServerComponent() {
  const data = await fetchData();
  return <ClientComponent data={data} />;
}
```
