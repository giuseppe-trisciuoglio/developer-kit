# Next.js App Router - Detailed Code Patterns

This document contains comprehensive code patterns for Next.js 16+ App Router development.

## Table of Contents

- [Server Components Patterns](#server-components-patterns)
- [Client Components Patterns](#client-components-patterns)
- [Server Actions Patterns](#server-actions-patterns)
- [Route Handlers Patterns](#route-handlers-patterns)
- [Caching Patterns](#caching-patterns)
- [Routing Patterns](#routing-patterns)
- [Next.js 16 Async API Patterns](#nextjs-16-async-api-patterns)

---

## Server Components Patterns

### Basic Data Fetching

Server Components are the default and ideal for data fetching.

```tsx
// app/users/page.tsx
async function getUsers() {
  const apiUrl = process.env.API_URL;
  const res = await fetch(`${apiUrl}/users`, {
    // Next.js extends fetch with caching options
    next: { revalidate: 3600 }, // Cache for 1 hour
  });
  return res.json();
}

export default async function UsersPage() {
  const users = await getUsers();
  return (
    <main>
      <h1>Users</h1>
      {users.map(user => <UserCard key={user.id} user={user} />)}
    </main>
  );
}
```

### Parallel Data Fetching

Fetch independent data in parallel for better performance.

```tsx
async function getProduct(id: string) {
  const res = await fetch(`${API_URL}/products/${id}`, {
    next: { revalidate: 3600 },
  });
  return res.json();
}

async function getReviews(productId: string) {
  const res = await fetch(`${API_URL}/reviews?product=${productId}`, {
    next: { revalidate: 60 }, // Shorter cache for reviews
  });
  return res.json();
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Parallel fetching with Promise.all
  const [product, reviews] = await Promise.all([
    getProduct(id),
    getReviews(id),
  ]);

  return (
    <main>
      <ProductDetail product={product} />
      <ReviewsList reviews={reviews} />
    </main>
  );
}
```

### Using React's cache() for Deduplication

Prevent duplicate fetches within the same component tree.

```tsx
import { cache } from "react";

const getSingleProduct = cache(async (id: string) => {
  const res = await fetch(`${API_URL}/products/${id}`);
  return res.json();
});

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // These will dedupe - only one fetch
  const product = await getSingleProduct(id);
  const sameProduct = await getSingleProduct(id);

  return <ProductDetail product={product} />;
}
```

---

## Client Components Patterns

### Using React Hooks

```tsx
"use client";

import { useState, useEffect } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Only runs on client
    document.title = `Count: ${count}`;
  }, [count]);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
      <button onClick={() => setIsVisible(!isVisible)}>
        Toggle Visibility
      </button>
      {isVisible && <p>Visible content</p>}
    </div>
  );
}
```

### Browser APIs Access

```tsx
"use client";

import { useState, useEffect } from "react";

export default function Geolocation() {
  const [location, setLocation] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        position => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        error => {
          console.error("Geolocation error:", error);
        }
      );
    }
  }, []);

  if (!location) return <p>Loading location...</p>;

  return (
    <p>
      Latitude: {location.lat}, Longitude: {location.lng}
    </p>
  );
}
```

### Combining Server and Client Components

Pass server-fetched data as props to Client Components.

```tsx
// Server Component
async function getProduct(id: string) {
  const res = await fetch(`${API_URL}/products/${id}`);
  return res.json();
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await getProduct(id);

  return <ProductClient product={product} />;
}

// Client Component
"use client";

import { useState } from "react";

export function ProductClient({ product }: { product: Product }) {
  const [isLiked, setIsLiked] = useState(false);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <button onClick={() => setIsLiked(!isLiked)}>
        {isLiked ? "♥ Liked" : "♡ Like"}
      </button>
    </div>
  );
}
```

---

## Server Actions Patterns

### Basic Server Action

Define actions in separate files with "use server" directive.

```tsx
// app/actions.ts
"use server";

import { revalidatePath } from "next/cache";
import { db } from "./db";

export async function createUser(formData: FormData) {
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;

  const user = await db.user.create({
    data: { name, email },
  });

  revalidatePath("/users");
  return user;
}
```

### Server Action with Validation

```tsx
// app/actions/users.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";

const CreateUserSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  role: z.enum(["user", "admin"]).default("user"),
});

export async function createUser(prevState: any, formData: FormData) {
  const rawData = {
    name: formData.get("name"),
    email: formData.get("email"),
    role: formData.get("role"),
  };

  const result = CreateUserSchema.safeParse(rawData);

  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
      message: "Validation failed",
    };
  }

  try {
    const user = await db.user.create({
      data: result.data,
    });

    revalidatePath("/users");
    return {
      success: true,
      user,
      message: "User created successfully",
    };
  } catch (error) {
    return {
      message: "Failed to create user",
      errors: { _form: ["Database error occurred"] },
    };
  }
}
```

### Optimistic Updates with useOptimistic

```tsx
"use client";

import { useOptimistic, useActionState } from "react";
import { likePost } from "./actions";

export function LikeButton({ postId, initialLikes }: {
  postId: string;
  initialLikes: number;
}) {
  const [state, formAction] = useActionState(likePost, null);
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    initialLikes,
    (state, newLikes) => state + 1
  );

  async function handleSubmit() {
    addOptimisticLike(1);
    formAction(new FormData());
  }

  return (
    <form action={handleSubmit}>
      <button type="submit">
        ♥ {optimisticLikes} Likes
      </button>
    </form>
  );
}
```

### Server Actions with Error Handling

```tsx
"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";

export async function deleteUser(formData: FormData) {
  const id = formData.get("id") as string;

  if (!id) {
    return {
      success: false,
      error: "User ID is required",
    };
  }

  try {
    await db.user.delete({ where: { id } });
    revalidatePath("/users");

    return {
      success: true,
      message: "User deleted successfully",
    };
  } catch (error) {
    if (error instanceof Error) {
      return {
        success: false,
        error: error.message,
      };
    }
    return {
      success: false,
      error: "An unknown error occurred",
    };
  }
}
```

---

## Route Handlers Patterns

### Basic CRUD Endpoints

```tsx
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

const CreateUserSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
});

// GET all users
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "10");

  const users = await db.user.findMany({
    skip: (page - 1) * limit,
    take: limit,
  });

  return NextResponse.json({
    users,
    page,
    limit,
    total: await db.user.count(),
  });
}

// POST create user
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const result = CreateUserSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        { errors: result.error.flatten().fieldErrors },
        { status: 400 }
      );
    }

    const user = await db.user.create({
      data: result.data,
    });

    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

### Dynamic Route Handlers

```tsx
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from "next/server";

interface RouteParams {
  params: Promise<{ id: string }>;
}

// GET single user
export async function GET(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = await params;
  const user = await db.user.findUnique({ where: { id } });

  if (!user) {
    return NextResponse.json(
      { error: "User not found" },
      { status: 404 }
    );
  }

  return NextResponse.json(user);
}

// PATCH update user
export async function PATCH(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = await params;
  const body = await request.json();

  try {
    const user = await db.user.update({
      where: { id },
      data: body,
    });

    return NextResponse.json(user);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to update user" },
      { status: 500 }
    );
  }
}

// DELETE user
export async function DELETE(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = await params;

  try {
    await db.user.delete({ where: { id } });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to delete user" },
      { status: 500 }
    );
  }
}
```

### Route Handler with Authentication

```tsx
// app/api/protected/route.ts
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function GET(request: NextRequest) {
  const session = await auth();

  if (!session) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    );
  }

  // Process authenticated request
  const data = await getProtectedData(session.user.id);
  return NextResponse.json(data);
}
```

---

## Caching Patterns

### Basic "use cache" Directive

Next.js 16+ introduces explicit caching with the "use cache" directive.

```tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Tag for selective revalidation
  cacheTag(`product-${id}`, "products");

  // Set cache duration
  cacheLife("hours");

  const product = await fetchProduct(id);
  return <ProductDetail product={product} />;
}
```

### Cache Profiles with cacheLife

```tsx
"use cache";

import { cacheLife } from "next/cache";

// Predefined cache profiles
cacheLife("minutes"); // 1 minute
cacheLife("hours"); // 1 hour
cacheLife("days"); // 1 day
cacheLife("max"); // Maximum caching (1 year)

// Custom duration
cacheLife({
  stale: 60, // Serve stale for 60s while revalidating
  revalidate: 3600, // Revalidate every hour
});
```

### Tag-Based Revalidation

```tsx
"use cache";

import { cacheTag } from "next/cache";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Multiple tags for flexible revalidation
  cacheTag(`product-${id}`, "products", "catalog");

  const product = await fetchProduct(id);
  return <ProductDetail product={product} />;
}

// Revalidate on demand
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { tag } = await request.json();
  revalidateTag(tag);
  return NextResponse.json({ revalidated: true });
}
```

### On-Demand Revalidation

```tsx
// Server Action that triggers revalidation
"use server";

import { revalidateTag, revalidatePath } from "next/cache";

export async function updateProduct(productId: string, data: any) {
  await db.product.update({
    where: { id: productId },
    data,
  });

  // Revalidate specific product
  revalidateTag(`product-${productId}`);

  // Or revalidate all products
  revalidateTag("products");

  // Or revalidate by path
  revalidatePath(`/products/${productId}`);

  return { success: true };
}
```

---

## Routing Patterns

### Parallel Routes

Create multiple independent route slots using `@folder` convention.

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode;
  team: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <header>Dashboard Header</header>
      <div className="content">
        <main>{children}</main>
        <aside className="panels">
          <div className="team-panel">{team}</div>
          <div className="analytics-panel">{analytics}</div>
        </aside>
      </div>
    </div>
  );
}

// app/dashboard/@team/page.tsx
export default function TeamPage() {
  return <div>Team Section</div>;
}

// app/dashboard/@analytics/page.tsx
export default async function AnalyticsPage() {
  const stats = await getAnalytics();
  return <div>Analytics: {stats.views} views</div>;
}
```

### Intercepting Routes

Show a modal while preserving the underlying page context.

```tsx
// app/photos/[id]/page.tsx
export default function PhotoPage({ params }: {
  params: Promise<{ id: string }>;
}) {
  return <PhotoDetail id={(await params).id} />;
}

// app/(.)photos/[id]/page.tsx - Intercepted route
export default function PhotoModal({ params }: {
  params: Promise<{ id: string }>;
}) {
  return <PhotoModal id={(await params).id} />;
}

// PhotoModal component
"use client";

import { useRouter } from "next/navigation";

export function PhotoModal({ id }: { id: string }) {
  const router = useRouter();

  return (
    <div className="modal-overlay" onClick={() => router.back()}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <img src={`/photos/${id}.jpg`} alt={`Photo ${id}`} />
        <button onClick={() => router.back()}>Close</button>
      </div>
    </div>
  );
}
```

### Route Groups

Organize routes without affecting URL structure.

```tsx
// app/(marketing)/about/page.tsx -> /about
// app/(marketing)/contact/page.tsx -> /contact
// app/(dashboard)/profile/page.tsx -> /profile

// Shared layout for marketing routes
// app/(marketing)/layout.tsx
export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="marketing">
      <Navigation />
      {children}
      <Footer />
    </div>
  );
}

// Different layout for dashboard routes
// app/(dashboard)/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <Sidebar />
      <main>{children}</main>
    </div>
  );
}
```

---

## Next.js 16 Async API Patterns

### Async cookies(), headers(), draftMode()

All Next.js APIs are async in version 16.

```tsx
import { cookies, headers, draftMode } from "next/headers";

export default async function Page() {
  const cookieStore = await cookies();
  const headersList = await headers();
  const { isEnabled } = await draftMode();

  const session = cookieStore.get("session")?.value;
  const userAgent = headersList.get("user-agent");

  return (
    <div>
      <p>Session: {session}</p>
      <p>User Agent: {userAgent}</p>
      <p>Draft Mode: {isEnabled ? "Enabled" : "Disabled"}</p>
    </div>
  );
}
```

### Async params and searchParams

Route parameters are Promise-based in Next.js 16.

```tsx
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ sort?: string; filter?: string }>;
}) {
  const { slug } = await params;
  const { sort, filter } = await searchParams;

  const data = await fetchData({ slug, sort, filter });
  return <PageContent data={data} />;
}
```

### Streaming with Suspense

Leverage async APIs for progressive rendering.

```tsx
import { Suspense } from "react";

export default async function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<ActivitySkeleton />}>
        <RecentActivity />
      </Suspense>
    </div>
  );
}

async function Stats() {
  const stats = await getStats();
  return <StatsDisplay stats={stats} />;
}

async function RecentActivity() {
  const activities = await getRecentActivity();
  return <ActivityList activities={activities} />;
}
```

---

## See Also

- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)
- [Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions)
- [Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [Caching](https://nextjs.org/docs/app/building-your-application/caching)
- [Parallel Routes](https://nextjs.org/docs/app/building-your-application/routing/parallel-routes)
