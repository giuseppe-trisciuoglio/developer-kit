# Next.js App Router - Best Practices

This document contains comprehensive best practices, constraints, and warnings for Next.js 16+ App Router development.

## Table of Contents

- [Architecture Best Practices](#architecture-best-practices)
- [Performance Best Practices](#performance-best-practices)
- [Security Best Practices](#security-best-practices)
- [Server vs Client Component Guidelines](#server-vs-client-component-guidelines)
- [Data Fetching Best Practices](#data-fetching-best-practices)
- [Caching Best Practices](#caching-best-practices)
- [Constraints and Limitations](#constraints-and-limitations)
- [Common Pitfalls and Warnings](#common-pitfalls-and-warnings)

---

## Architecture Best Practices

### 1. Component Hierarchy Strategy

**Organize components by data requirements:**

```tsx
// ✅ Good: Server Component at the top
async function Page() {
  const data = await fetchData();
  return (
    <div>
      <Header data={data} />
      <ClientComponent initialData={data} />
    </div>
  );
}

// ❌ Bad: Making everything client components
"use client";
function Page() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetchData().then(setData);
  }, []);
  return <div>...</div>;
}
```

**Push Client Components down the tree:**

```tsx
// app/page.tsx - Server Component
import { ProductList } from "@/components/ProductList";

export default async function Page() {
  const products = await getProducts();
  return <ProductList products={products} />;
}

// components/ProductList.tsx - Server Component
export function ProductList({ products }: { products: Product[] }) {
  return (
    <div>
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

// components/ProductCard.tsx - Client Component (only because of onClick)
"use client";

export function ProductCard({ product }: { product: Product }) {
  return (
    <div onClick={() => console.log(product.id)}>
      <h3>{product.name}</h3>
    </div>
  );
}
```

### 2. File Organization

**Follow Next.js conventions:**

```
app/
├── (auth)/                 # Route group (no URL prefix)
│   ├── login/
│   │   └── page.tsx
│   ├── register/
│   │   └── page.tsx
│   └── layout.tsx          # Shared auth layout
├── (dashboard)/            # Route group
│   ├── layout.tsx          # Dashboard layout
│   ├── page.tsx            # /dashboard
│   ├── @stats/            # Parallel route slot
│   │   └── page.tsx
│   └── @notifications/    # Parallel route slot
│       └── page.tsx
├── api/                    # API routes
│   └── users/
│       └── route.ts
├── blog/
│   ├── [slug]/            # Dynamic route
│   │   └── page.tsx
│   └── page.tsx
├── globals.css
├── layout.tsx             # Root layout
└── page.tsx               # Home page
```

### 3. Layout Strategy

**Use layouts efficiently:**

```tsx
// Root layout - wraps entire app
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

// Route group layout - wraps dashboard routes
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

## Performance Best Practices

### 1. Optimize Bundle Size

**Avoid unnecessary client components:**

```tsx
// ❌ Bad: Client component when not needed
"use client";

export function StaticContent() {
  return <div>This never changes</div>;
}

// ✅ Good: Server component (default)
export function StaticContent() {
  return <div>This never changes</div>;
}
```

**Code split client components:**

```tsx
"use client";

import dynamic from "next/dynamic";

// Dynamically import heavy component
const HeavyChart = dynamic(() => import("./HeavyChart"), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Skip SSR if not needed
});

export function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <HeavyChart />
    </div>
  );
}
```

### 2. Image Optimization

**Always use next/image:**

```tsx
import Image from "next/image";

export function ProductImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={500}
      height={500}
      priority // For above-the-fold images
      placeholder="blur" // Or "blur"
    />
  );
}
```

### 3. Font Optimization

**Use next/font:**

```tsx
import { Inter, Roboto } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const roboto = Roboto({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-roboto",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html className={`${inter.variable} ${roboto.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

### 4. Loading States

**Use loading.tsx for Suspense boundaries:**

```tsx
// app/blog/loading.tsx
export default function BlogLoading() {
  return (
    <div className="blog-loading">
      <div className="skeleton-header" />
      <div className="skeleton-grid">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="skeleton-card" />
        ))}
      </div>
    </div>
  );
}
```

**Use Suspense for granular loading:**

```tsx
import { Suspense } from "react";

export default async function Page() {
  return (
    <div>
      <Header />

      <Suspense fallback={<PostsSkeleton />}>
        <Posts />
      </Suspense>

      <Suspense fallback={<CommentsSkeleton />}>
        <Comments />
      </Suspense>
    </div>
  );
}
```

### 5. Streaming and Progressive Rendering

**Leverage async APIs for streaming:**

```tsx
import { Suspense } from "react";

export default async function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Stream in data as it becomes available */}
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>

      <Suspense fallback={<ActivitySkeleton />}>
        <RecentActivity />
      </Suspense>
    </div>
  );
}
```

---

## Security Best Practices

### 1. Server Actions Security

**Always validate and sanitize input:**

```tsx
"use server";

import { z } from "zod";

const CreateUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  role: z.enum(["user", "admin"]).default("user"),
});

export async function createUser(formData: FormData) {
  // Validate input
  const rawData = {
    name: formData.get("name"),
    email: formData.get("email"),
    role: formData.get("role"),
  };

  const result = CreateUserSchema.safeParse(rawData);

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  // Use validated data
  const user = await db.user.create({
    data: result.data,
  });

  return { success: true, user };
}
```

**Implement rate limiting:**

```tsx
// app/actions/rate-limiter.ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "10 s"),
});

export async function checkRateLimit(identifier: string) {
  const { success, remaining } = await ratelimit.limit(identifier);

  if (!success) {
    throw new Error("Rate limit exceeded");
  }

  return remaining;
}

// Usage in server action
"use server";

import { checkRateLimit } from "./rate-limiter";
import { auth } from "@/lib/auth";

export async function createUser(formData: FormData) {
  const session = await auth();

  if (!session?.user?.id) {
    throw new Error("Unauthorized");
  }

  await checkRateLimit(session.user.id);

  // Proceed with user creation
}
```

**Implement authentication checks:**

```tsx
"use server";

import { auth } from "@/lib/auth";

export async function sensitiveAction(formData: FormData) {
  const session = await auth();

  if (!session) {
    return { error: "Unauthorized" };
  }

  // Check user permissions
  if (session.user.role !== "admin") {
    return { error: "Forbidden" };
  }

  // Perform action
}
```

### 2. External Data Fetching

**Always validate external API responses:**

```tsx
// app/products/page.tsx
import { z } from "zod";

// Schema for external API response
const ProductSchema = z.object({
  id: z.string(),
  name: z.string(),
  price: z.number(),
  description: z.string(),
});

const ProductsResponseSchema = z.object({
  products: z.array(ProductSchema),
  total: z.number(),
});

async function getProducts() {
  const apiUrl = process.env.EXTERNAL_API_URL; // Use environment variable
  const res = await fetch(`${apiUrl}/products`);

  if (!res.ok) {
    throw new Error("Failed to fetch products");
  }

  const rawData = await res.json();

  // Validate and parse response
  const result = ProductsResponseSchema.safeParse(rawData);

  if (!result.success) {
    throw new Error("Invalid API response format");
  }

  return result.data;
}
```

**Sanitize user-generated content:**

```tsx
import DOMPurify from "isomorphic-dompurify";

export function renderUserContent(content: string) {
  const sanitized = DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "a"],
    ALLOWED_ATTR: ["href"],
  });

  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### 3. Environment Variables

**Never expose secrets:**

```tsx
// ✅ Good: Use server-side only
async function ServerComponent() {
  const apiKey = process.env.API_KEY; // Only available on server
  const data = await fetchData(apiKey);
  return <DataDisplay data={data} />;
}

// ❌ Bad: Exposing secret to client
"use client";
function ClientComponent() {
  const apiKey = process.env.API_KEY; // Exposed to browser
  // ...
}
```

**Prefix public variables:**

```bash
# .env.local
API_KEY=secret_key_xxx         # Server-only
NEXT_PUBLIC_API_URL=https://... # Exposed to client
```

---

## Server vs Client Component Guidelines

### Decision Tree

**Start with Server Component (default). Convert to Client Component if:**

1. **Needs React hooks**
   ```tsx
   "use client";
   import { useState, useEffect } from "react";
   ```

2. **Needs browser APIs**
   ```tsx
   "use client";
   useEffect(() => {
     const width = window.innerWidth;
   }, []);
   ```

3. **Needs event handlers**
   ```tsx
   "use client";
   <button onClick={handleClick}>Click me</button>
   ```

4. **Needs client-only libraries**
   ```tsx
   "use client";
   import { Chart } from "chart.js";
   ```

### Common Patterns

**Interactive component with server data:**

```tsx
// Server Component
async function ProductPage({ params }: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await getProduct(id);

  return <AddToCartButton productId={product.id} />;
}

// Client Component
"use client";

import { useState } from "react";

export function AddToCartButton({ productId }: { productId: string }) {
  const [added, setAdded] = useState(false);

  return (
    <button onClick={() => setAdded(true)}>
      {added ? "Added!" : "Add to Cart"}
    </button>
  );
}
```

---

## Data Fetching Best Practices

### 1. Fetch in Server Components

```tsx
// ✅ Good: Fetch in Server Component
async function UserPage({ params }: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const user = await getUser(id);
  return <UserProfile user={user} />;
}

// ❌ Bad: Fetch in Client Component
"use client";
function UserPage({ id }: { id: string }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    getUser(id).then(setUser);
  }, [id]);
  // ...
}
```

### 2. Parallelize Independent Fetches

```tsx
// ✅ Good: Parallel fetching with Promise.all
export default async function Dashboard() {
  const [users, posts, comments] = await Promise.all([
    getUsers(),
    getPosts(),
    getComments(),
  ]);

  return <DashboardData users={users} posts={posts} comments={comments} />;
}

// ❌ Bad: Sequential fetching
export default async function Dashboard() {
  const users = await getUsers();
  const posts = await getPosts();
  const comments = await getComments();
  // ...
}
```

### 3. Use React's cache() for Deduplication

```tsx
import { cache } from "react";

const getSingleUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } });
});

// Multiple components can call this without duplicate fetches
async function Component1() {
  const user = await getSingleUser("123");
  // ...
}

async function Component2() {
  const user = await getSingleUser("123"); // Deduped!
  // ...
}
```

### 4. Add Suspense Boundaries

```tsx
import { Suspense } from "react";

export default async function Page() {
  return (
    <div>
      <Suspense fallback={<UserSkeleton />}>
        <User />
      </Suspense>

      <Suspense fallback={<PostsSkeleton />}>
        <Posts />
      </Suspense>
    </div>
  );
}
```

---

## Caching Best Practices

### 1. Use "use cache" for Static Content

```tsx
"use cache";

import { cacheLife } from "next/cache";

export default async function ProductList() {
  cacheLife("days");

  const products = await getProducts();
  return <ProductsDisplay products={products} />;
}
```

### 2. Use Tags for Revalidation

```tsx
"use cache";

import { cacheTag } from "next/cache";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  cacheTag(`product-${id}`, "products");

  const product = await getProduct(id);
  return <ProductDetail product={product} />;
}
```

### 3. Implement Revalidation on Updates

```tsx
"use server";

import { revalidateTag, revalidatePath } from "next/cache";

export async function updateProduct(id: string, data: any) {
  await db.product.update({
    where: { id },
    data,
  });

  // Revalidate specific product
  revalidateTag(`product-${id}`);

  // Revalidate all products
  revalidateTag("products");

  // Revalidate by path
  revalidatePath(`/products/${id}`);
}
```

---

## Constraints and Limitations

### Server Components Constraints

**Cannot use:**
- React hooks (useState, useEffect, useContext, etc.)
- Browser APIs (window, document, localStorage, etc.)
- Event handlers (onClick, onSubmit, etc.)
- Client-only libraries

```tsx
// ❌ Invalid Server Component
export default function BadComponent() {
  const [count, setCount] = useState(0); // Error!
  useEffect(() => { }, []); // Error!
  return <button onClick={() => setCount(1)}>Click</button>; // Error!
}
```

**Cannot be async:**

```tsx
// ❌ Invalid Client Component
"use client";

export default async function BadComponent() {
  const data = await fetchData(); // Error!
  return <div>{data}</div>;
}
```

### Next.js 16 Async API Constraints

**All Next.js APIs are async:**

```tsx
import { cookies, headers, draftMode } from "next/headers";

// ❌ Wrong (will return Promise object)
export default function Page() {
  const cookieStore = cookies(); // Returns Promise!
  // ...
}

// ✅ Correct
export default async function Page() {
  const cookieStore = await cookies(); // Await the Promise
  // ...
}
```

**Params are Promise-based:**

```tsx
// ❌ Wrong
export default function Page({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params; // Error!
}

// ✅ Correct
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params; // Await the Promise
}
```

---

## Common Pitfalls and Warnings

### 1. Forgetting to await Async APIs

```tsx
// ❌ Wrong
export default async function Page() {
  const cookieStore = cookies(); // Forgot await
  const session = cookieStore.get("session"); // Will be undefined!
  // ...
}

// ✅ Correct
export default async function Page() {
  const cookieStore = await cookies(); // Await it
  const session = cookieStore.get("session"); // Works!
  // ...
}
```

### 2. Using Browser APIs in Server Components

```tsx
// ❌ Wrong
export default function Page() {
  const width = window.innerWidth; // Runtime error!
  return <div>Width: {width}</div>;
}

// ✅ Correct
"use client";

export default function Page() {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    setWidth(window.innerWidth);
  }, []);

  return <div>Width: {width}</div>;
}
```

### 3. Server Actions Without Validation

```tsx
// ❌ Wrong - No validation
"use server";

export async function createUser(formData: FormData) {
  const name = formData.get("name"); // Could be anything!
  const email = formData.get("email"); // Not validated!

  await db.user.create({ data: { name, email } });
}

// ✅ Correct - With validation
"use server";

import { z } from "zod";

const CreateUserSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
});

export async function createUser(formData: FormData) {
  const rawData = {
    name: formData.get("name"),
    email: formData.get("email"),
  };

  const result = CreateUserSchema.safeParse(rawData);

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  await db.user.create({ data: result.data });
}
```

### 4. Exposing Secrets to Client

```tsx
// ❌ Wrong - Exposes secret
"use client";

export function ApiComponent() {
  const apiKey = process.env.API_KEY; // Visible in browser!
  // ...
}

// ✅ Correct - Server-side only
async function ServerComponent() {
  const apiKey = process.env.API_KEY; // Safe
  const data = await fetchData(apiKey);
  return <ClientComponent data={data} />;
}
```

### 5. Invalid Client Component Data Fetching

```tsx
// ❌ Wrong - Direct data fetching in Client Component
"use client";

export default function UserPage({ id }: { id: string }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${id}`)
      .then(res => res.json())
      .then(setUser);
  }, [id]);

  if (!user) return <div>Loading...</div>;
  return <UserProfile user={user} />;
}

// ✅ Correct - Server Component data fetching
async function UserPage({ params }: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const user = await getUser(id);

  return <UserProfile user={user} />;
}
```

### 6. Missing Error Boundaries

```tsx
// ❌ Wrong - No error handling
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const data = await fetchData(id); // Could throw!

  return <DataDisplay data={data} />;
}

// ✅ Correct - With error.tsx
// app/error.tsx
export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

---

## See Also

- [Next.js Performance](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Security Best Practices](https://nextjs.org/docs/app/building-your-application/configuring/security)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching)
- [Caching and Revalidation](https://nextjs.org/docs/app/building-your-application/caching)
