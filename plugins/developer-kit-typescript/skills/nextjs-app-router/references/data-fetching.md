# Data Fetching Patterns

## Server Components Fetching

```tsx
// app/users/page.tsx
async function getUsers() {
  const res = await fetch(`${process.env.API_URL}/users`, {
    // Cache configuration
    next: { revalidate: 3600, tags: ["users"] },
  });

  if (!res.ok) throw new Error("Failed to fetch users");
  return res.json();
}

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

## Database Query (Server Component)

```tsx
// app/posts/page.tsx
import { db } from "@/lib/db";

async function getPosts() {
  return db.post.findMany({
    where: { published: true },
    include: { author: true },
    orderBy: { createdAt: "desc" },
  });
}

export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <main>
      {posts.map((post) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>By {post.author.name}</p>
        </article>
      ))}
    </main>
  );
}
```

## Parallel Data Fetching

```tsx
// app/dashboard/page.tsx
import { Suspense } from "react";

async function getRevenue() {
  // Simulated delay
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return { total: 50000 };
}

async function getOrders() {
  await new Promise((resolve) => setTimeout(resolve, 1500));
  return [{ id: 1, amount: 100 }];
}

async function RevenueCard() {
  const revenue = await getRevenue();
  return <div>Revenue: ${revenue.total}</div>;
}

async function OrdersCard() {
  const orders = await getOrders();
  return <div>Orders: {orders.length}</div>;
}

export default function DashboardPage() {
  return (
    <div>
      <Suspense fallback={<p>Loading revenue...</p>}>
        <RevenueCard />
      </Suspense>
      <Suspense fallback={<p>Loading orders...</p>}>
        <OrdersCard />
      </Suspense>
    </div>
  );
}
```

## Sequential Data Fetching (Dependent)

```tsx
// app/user/[id]/posts/page.tsx
async function getUser(id: string) {
  const res = await fetch(`${process.env.API_URL}/users/${id}`);
  return res.json();
}

async function getPosts(userId: string) {
  const res = await fetch(
    `${process.env.API_URL}/users/${userId}/posts`
  );
  return res.json();
}

export default async function UserPostsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Sequential: attendi l'utente prima di fetchare i post
  const user = await getUser(id);
  const posts = await getPosts(user.id);

  return (
    <div>
      <h1>Posts by {user.name}</h1>
      {posts.map((post) => (
        <article key={post.id}>{post.title}</article>
      ))}
    </div>
  );
}
```

## Request Memoization (React cache)

```tsx
import { cache } from "react";

// Stessa richiesta deduplicata automaticamente
const getUser = cache(async (id: string) => {
  console.log("Fetching user", id); // Chiama una sola volta per richiesta
  return db.user.findUnique({ where: { id } });
});

// Componente 1
async function UserProfile({ id }: { id: string }) {
  const user = await getUser(id);
  return <div>{user?.name}</div>;
}

// Componente 2 (stessa richiesta, deduplicata)
async function UserAvatar({ id }: { id: string }) {
  const user = await getUser(id); // Non fetcha di nuovo
  return <img src={user?.avatar} />;
}

// Pagina parent
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <>
      <UserProfile id={id} />
      <UserAvatar id={id} />
    </>
  );
}
```

## Error Handling

```tsx
// app/error.tsx
"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

```tsx
// app/users/page.tsx
async function getUsers() {
  try {
    const res = await fetch(`${process.env.API_URL}/users`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (error) {
    // Log per monitoring
    console.error("Failed to fetch users:", error);
    // Rethrow per attivare error.tsx
    throw new Error("Unable to load users. Please try again later.");
  }
}
```

## Loading UI

```tsx
// app/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-8 bg-gray-200 rounded" />
        ))}
      </div>
    </div>
  );
}
```

## Streaming with Suspense

```tsx
// app/components/Skeleton.tsx
export function CardSkeleton() {
  return (
    <div className="animate-pulse p-4 border rounded">
      <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-full"></div>
    </div>
  );
}
```

```tsx
// app/page.tsx
import { Suspense } from "react";
import { CardSkeleton } from "./components/Skeleton";
import { ProductList } from "./components/ProductList";

export default function HomePage() {
  return (
    <div>
      <header>
        <h1>Welcome</h1>
      </header>

      {/> Static content renders immediately </}
      <section>About our store...</section>

      {/> Dynamic content streams in </}
      <Suspense fallback={<CardSkeleton />}>
        <ProductList />
      </Suspense>
    </div>
  );
}
```
