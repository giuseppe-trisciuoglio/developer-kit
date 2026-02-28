# Next.js App Router Patterns

## Route Segment Patterns

### Layouts
Layouts wrap child segments and persist across navigations. Use for shared UI (headers, sidebars, navigation).

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
```

### Loading States
Use `loading.tsx` for instant loading UI with Suspense boundaries.

```tsx
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-4" />
      <div className="h-64 bg-gray-200 rounded" />
    </div>
  );
}
```

### Error Boundaries
Use `error.tsx` for graceful error handling with recovery options.

```tsx
// app/dashboard/error.tsx
'use client';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Not Found Pages
Use `not-found.tsx` for custom 404 pages.

```tsx
// app/dashboard/[id]/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>The requested resource could not be found.</p>
    </div>
  );
}
```

## Data Fetching Patterns

### Server Component Data Fetching
Fetch data directly in Server Components — no `useEffect` needed.

```tsx
// app/products/page.tsx (Server Component)
async function getProducts(): Promise<Product[]> {
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 },
  });
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export default async function ProductsPage() {
  const products = await getProducts();
  return <ProductList products={products} />;
}
```

### Parallel Data Fetching
Avoid waterfalls by fetching independent data in parallel.

```tsx
export default async function DashboardPage() {
  const [stats, recentOrders, notifications] = await Promise.all([
    getStats(),
    getRecentOrders(),
    getNotifications(),
  ]);

  return (
    <div>
      <StatsCards stats={stats} />
      <RecentOrdersTable orders={recentOrders} />
      <NotificationsList notifications={notifications} />
    </div>
  );
}
```

### Streaming with Suspense
Stream independent sections for faster perceived performance.

```tsx
export default async function DashboardPage() {
  return (
    <div>
      <Suspense fallback={<StatsSkeleton />}>
        <StatsSection />
      </Suspense>
      <Suspense fallback={<OrdersSkeleton />}>
        <OrdersSection />
      </Suspense>
    </div>
  );
}

async function StatsSection() {
  const stats = await getStats(); // Can stream independently
  return <StatsCards stats={stats} />;
}
```

## Server Actions Patterns

### Form Handling with Server Actions

```tsx
// app/contacts/actions.ts
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const contactSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  message: z.string().min(10).max(1000),
});

export async function submitContact(formData: FormData) {
  const result = contactSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message'),
  });

  if (!result.success) {
    return { error: result.error.flatten() };
  }

  await db.contact.create({ data: result.data });
  revalidatePath('/contacts');
  return { success: true };
}
```

### Optimistic Updates

```tsx
'use client';

import { useOptimistic } from 'react';

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimistic] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, newTodo]
  );

  async function addTodo(formData: FormData) {
    const title = formData.get('title') as string;
    addOptimistic({ id: 'temp', title, completed: false });
    await createTodo(formData);
  }

  return (
    <form action={addTodo}>
      <input name="title" />
      <button type="submit">Add</button>
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id}>{todo.title}</li>
        ))}
      </ul>
    </form>
  );
}
```

## Route Handler Patterns

### API Route with Proper Validation

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  const result = createUserSchema.safeParse(body);

  if (!result.success) {
    return NextResponse.json(
      { errors: result.error.flatten() },
      { status: 400 }
    );
  }

  const user = await createUser(result.data);
  return NextResponse.json(user, { status: 201 });
}
```

## Metadata Patterns

### Dynamic Metadata

```tsx
// app/products/[id]/page.tsx
import type { Metadata } from 'next';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const product = await getProduct(id);

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      images: [{ url: product.imageUrl }],
    },
  };
}
```

## Caching Patterns

### Static Generation with generateStaticParams

```tsx
export async function generateStaticParams() {
  const products = await getProducts();
  return products.map((product) => ({
    id: product.id,
  }));
}
```

### On-Demand Revalidation with Tags

```typescript
// Data fetching with cache tags
async function getProduct(id: string) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: { tags: [`product-${id}`] },
  });
  return res.json();
}

// Server Action to revalidate
'use server';
import { revalidateTag } from 'next/cache';

export async function updateProduct(id: string, data: ProductData) {
  await db.product.update({ where: { id }, data });
  revalidateTag(`product-${id}`);
}
```
