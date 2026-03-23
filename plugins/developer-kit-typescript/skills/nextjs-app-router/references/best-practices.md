# Next.js App Router Best Practices

Comprehensive guide for building production-ready Next.js 16+ applications with App Router.

## Architecture Patterns

### Server vs Client Component Decision Tree

```
Start with Server Component (default)
    │
    ├─ Need React hooks (useState, useEffect)?
    │  └─ YES → Client Component
    │
    ├─ Need browser APIs (window, document, localStorage)?
    │  └─ YES → Client Component
    │
    ├─ Need event handlers (onClick, onSubmit)?
    │  └─ YES → Client Component
    │
    ├─ Need client-only libraries?
    │  └─ YES → Client Component
    │
    └─ NO → Keep as Server Component
```

### Component Composition Strategy

```tsx
// ✅ GOOD: Server Component with Client Component leaves
// app/page.tsx (Server Component)
import UserProfile from "./components/UserProfile"; // Client
import UserPreferences from "./components/UserPreferences"; // Client

export default async function Page() {
  const user = await getCurrentUser();
  const posts = await getUserPosts(user.id);

  return (
    <main>
      <UserProfile user={user} />
      <UserPreferences userId={user.id} />
      <PostsList posts={posts} /> {/* Server Component */}
    </main>
  );
}

// ❌ BAD: Everything as Client Component
"use client";

export default function Page() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetchUser().then(setUser);
    fetchPosts().then(setPosts);
  }, []);

  // Unnecessary client-side fetching
}
```

### Pass Props from Server to Client

```tsx
// ✅ GOOD: Fetch in Server, pass to Client
// app/products/page.tsx (Server)
export default async function ProductsPage() {
  const products = await db.product.findMany();
  return <ProductGrid initialProducts={products} />;
}

// components/ProductGrid.tsx (Client)
"use client";

export default function ProductGrid({ initialProducts }: Props) {
  const [products, setProducts] = useState(initialProducts);

  // Client can now interact with data
}

// ❌ BAD: Fetch in Client Component
"use client";

export default function ProductGrid() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch("/api/products").then(r => r.json()).then(setProducts);
  }, []);

  // Slower initial load, no SEO
}
```

## Data Fetching Best Practices

### Fetch in Server Components

```tsx
// ✅ GOOD: Server-side data fetching
export default async function Page() {
  const data = await fetchData(); // Runs on server
  return <View data={data} />;
}

// ❌ BAD: Client-side fetching (slower, no SEO)
"use client";
export default function Page() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetchData().then(setData);
  }, []);
  return data ? <View data={data} /> : <Loading />;
}
```

### Use React's cache() for Deduplication

```tsx
import { cache } from "react";

// Cache function to prevent duplicate requests
const getCurrentUser = cache(async () => {
  return await db.user.findFirst();
});

// Multiple components can call this
// Only one database query is made
export default async function Dashboard() {
  const user = await getCurrentUser();
  const posts = await getPostsByUser(user.id);

  return <Dashboard user={user} posts={posts} />;
}
```

### Parallelize Independent Fetches

```tsx
// ✅ GOOD: Parallel fetching
export default async function Page() {
  const [user, posts, comments] = await Promise.all([
    fetchUser(),
    fetchPosts(),
    fetchComments(),
  ]);

  return <Dashboard user={user} posts={posts} comments={comments} />;
}

// ❌ BAD: Sequential fetching
export default async function Page() {
  const user = await fetchUser();     // Wait 100ms
  const posts = await fetchPosts();    // Wait 150ms
  const comments = await fetchComments(); // Wait 100ms
  // Total: 350ms instead of 150ms
}
```

### Add Suspense Boundaries

```tsx
// app/loading.tsx
export default function Loading() {
  return <div className="animate-pulse">Loading...</div>;
}

// app/dashboard/page.tsx
import { Suspense } from "react";

export default function DashboardPage() {
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

function StatsSkeleton() {
  return (
    <div className="grid grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-24 bg-gray-200 animate-pulse rounded" />
      ))}
    </div>
  );
}
```

## Server Actions Best Practices

### Always Validate Input

```tsx
"use server";

import { z } from "zod";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export async function register(formData: FormData) {
  const parsed = schema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
  });

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  // Safe to use parsed.data
  const user = await db.user.create({ data: parsed.data });
  return { user };
}
```

### Use Zod for Validation

```tsx
import { z } from "zod";

// Define schema
const createUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  age: z.number().min(18).max(120),
  role: z.enum(["user", "admin"]),
  interests: z.array(z.string()).default([]),
});

// Use in Server Action
export async function createUser(formData: FormData) {
  const result = createUserSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    age: parseInt(formData.get("age") as string),
    role: formData.get("role"),
    interests: formData.getAll("interests"),
  });

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  // Type-safe: result.data is fully typed
  const user = await db.user.create({ data: result.data });
  return { success: true, user };
}
```

### Revalidate After Mutations

```tsx
"use server";

import { revalidatePath, revalidateTag } from "next/cache";

export async function deletePost(id: string) {
  await db.post.delete({ where: { id } });

  // Revalidate specific path
  revalidatePath("/blog");
  revalidatePath(`/blog/${id}`);

  // Or revalidate by tag
  revalidateTag("posts");

  return { success: true };
}
```

### Return Consistent Response Shape

```tsx
type ActionResponse<T = any> = {
  success: boolean;
  data?: T;
  errors?: Record<string, string[]>;
  message?: string;
};

export async function updateUser(
  id: string,
  formData: FormData
): Promise<ActionResponse<User>> {
  try {
    const data = parseFormData(formData);
    const user = await db.user.update({ where: { id }, data });

    revalidatePath("/users");

    return {
      success: true,
      data: user,
      message: "User updated successfully",
    };
  } catch (error) {
    return {
      success: false,
      errors: { _form: ["Failed to update user"] },
    };
  }
}
```

## Caching Strategies

### Use "use cache" for Expensive Operations

```tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function ExpensivePage() {
  // Tag for revalidation
  cacheTag("expensive-data", "all-data");

  // Set cache duration
  cacheLife("hours"); // "minutes", "hours", "days", "max"

  const data = await expensiveOperation();

  return <View data={data} />;
}
```

### Choose Appropriate Cache Duration

```tsx
// Static content (rarely changes)
cacheLife("max"); // Cache indefinitely

// Product catalog (changes occasionally)
cacheLife("days"); // Cache for days

// News feed (changes frequently)
cacheLife("minutes"); // Cache for minutes

// Real-time data (no caching)
// Don't use "use cache"
```

### Implement On-Demand Revalidation

```tsx
// Server Action or Route Handler
import { revalidateTag, revalidatePath } from "next/cache";

// Revalidate by tag
export async function updateProduct() {
  await db.product.update({ /* ... */ });

  // Revalidate all product pages
  revalidateTag("products");
}

// Revalidate by path
export async function publishPost() {
  await db.post.update({ /* ... */ });

  // Revalidate specific pages
  revalidatePath("/blog");
  revalidatePath("/blog/feed");
}
```

## Route Handlers Best Practices

### Use Route Handlers for External APIs

```tsx
// ✅ GOOD: Route Handler for API proxy
// app/api/github/[username]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ username: string }> }
) {
  const { username } = await params;

  const response = await fetch(`https://api.github.com/users/${username}`, {
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
    },
  });

  if (!response.ok) {
    return NextResponse.json(
      { error: "Failed to fetch user" },
      { status: response.status }
    );
  }

  const data = await response.json();
  return NextResponse.json(data);
}
```

### Validate Route Handler Inputs

```tsx
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

const querySchema = z.object({
  limit: z.coerce.number().min(1).max(100).default(20),
  offset: z.coerce.number().min(0).default(0),
});

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const result = querySchema.safeParse({
    limit: searchParams.get("limit"),
    offset: searchParams.get("offset"),
  });

  if (!result.success) {
    return NextResponse.json(
      { error: "Invalid query parameters", issues: result.error.issues },
      { status: 400 }
    );
  }

  const { limit, offset } = result.data;
  const items = await db.item.findMany({
    take: limit,
    skip: offset,
  });

  return NextResponse.json(items);
}
```

### Handle Errors Gracefully

```tsx
export async function GET(request: NextRequest) {
  try {
    const data = await fetchData();
    return NextResponse.json(data);
  } catch (error) {
    console.error("API error:", error);

    // Don't expose internal errors to client
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

## File Organization

### Route Groups for Shared Layouts

```
app/
├── (auth)/                 # Auth routes group
│   ├── login/
│   │   └── page.tsx
│   ├── register/
│   │   └── page.tsx
│   └── layout.tsx          # Auth-specific layout
├── (dashboard)/            # Dashboard routes group
│   ├── layout.tsx          # Dashboard layout with sidebar
│   ├── page.tsx            # Dashboard home
│   ├── users/
│   │   └── page.tsx
│   └── settings/
│       └── page.tsx
├── (marketing)/            # Public pages group
│   ├── about/
│   │   └── page.tsx
│   ├── pricing/
│   │   └── page.tsx
│   └── layout.tsx          # Marketing layout
└── layout.tsx              # Root layout
```

### Parallel Routes for Complex Layouts

```
app/
├── dashboard/
│   ├── layout.tsx          # Receives children, sidebar, stats
│   ├── page.tsx            # Main content
│   ├── @sidebar/           # Sidebar slot
│   │   └── page.tsx
│   └── @stats/             # Stats slot
│       └── page.tsx
├── shop/
│   ├── layout.tsx          # Receives children, filters
│   ├── page.tsx
│   ├── @filters/           # Filters slot
│   │   └── page.tsx
│   └── @products/          # Products slot
│       └── page.tsx
```

### Organize Server Actions

```
app/
├── actions/
│   ├── users.ts            # User-related actions
│   ├── posts.ts            # Post-related actions
│   ├── auth.ts             # Authentication actions
│   └── index.ts            # Export all actions
```

```tsx
// app/actions/index.ts
export * from "./users";
export * from "./posts";
export * from "./auth";

// Usage
import { createUser, deleteUser } from "@/app/actions";
```

## Error Handling

### Always Use Error Boundaries

```tsx
// app/error.tsx
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Error:", error);
  }, [error]);

  return (
    <div className="p-4">
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Handle Not Found

```tsx
// app/not-found.tsx
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="text-center py-12">
      <h2 className="text-2xl font-bold">Page Not Found</h2>
      <p className="text-gray-600 mt-2">
        The page you're looking for doesn't exist.
      </p>
      <Link href="/" className="text-blue-500 hover:underline mt-4 inline-block">
        Go home
      </Link>
    </div>
  );
}

// Usage in pages
import { notFound } from "next/navigation";

export default async function ProductPage({ params }: Props) {
  const product = await db.product.findUnique({
    where: { id: params.id },
  });

  if (!product) {
    notFound(); // Triggers not-found.tsx
  }

  return <ProductDetail product={product} />;
}
```

### Global Error Boundary

```tsx
// app/global-error.tsx
"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <h2>Something went terribly wrong!</h2>
        <button onClick={reset}>Try again</button>
      </body>
    </html>
  );
}
```

## Performance Optimization

### Use Loading States

```tsx
// app/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 w-3/4"></div>
      <div className="h-4 bg-gray-200 w-full"></div>
      <div className="h-4 bg-gray-200 w-5/6"></div>
    </div>
  );
}
```

### Optimize Images

```tsx
import Image from "next/image";

// ✅ GOOD: Use Next.js Image component
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // For above-the-fold images
  placeholder="blur" // Or provide blurDataURL
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>

// ❌ BAD: Use regular img tag
<img src="/hero.jpg" alt="Hero" width={1200} height={600} />
```

### Optimize Fonts

```tsx
// app/layout.tsx
import { GeistSans, GeistMono } from "next/font/google";

const geistSans = GeistSans({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = GeistMono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

### Enable React Compiler

```tsx
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true,
  },
};

export default nextConfig;
```

## Security Best Practices

### Validate All User Input

```tsx
// ❌ BAD: Never trust user input
export async function deleteUser(formData: FormData) {
  const id = formData.get("id") as string;
  await db.user.delete({ where: { id } }); // SQL injection risk!
}

// ✅ GOOD: Validate and sanitize
import { z } from "zod";

const schema = z.string().uuid();

export async function deleteUser(formData: FormData) {
  const id = schema.safeParse(formData.get("id"));

  if (!id.success) {
    return { error: "Invalid user ID" };
  }

  await db.user.delete({ where: { id: id.data } });
}
```

### Use Environment Variables

```tsx
// ❌ BAD: Hardcoded secrets
const apiKey = "sk-1234567890abcdef";

// ✅ GOOD: Environment variables
const apiKey = process.env.API_KEY!;

// Validate at runtime
if (!process.env.API_KEY) {
  throw new Error("API_KEY environment variable is not set");
}
```

### Secure Server Actions

```tsx
// ❌ BAD: No authorization check
export async function deletePost(id: string) {
  await db.post.delete({ where: { id } });
}

// ✅ GOOD: Check permissions
export async function deletePost(id: string) {
  const currentUser = await getCurrentUser();

  const post = await db.post.findUnique({ where: { id } });

  if (!post || post.authorId !== currentUser.id) {
    return { error: "Unauthorized" };
  }

  await db.post.delete({ where: { id } });
}
```

### Secure Route Handlers

```tsx
// ❌ BAD: Public access to sensitive data
export async function GET(request: NextRequest) {
  const users = await db.user.findMany();
  return NextResponse.json(users);
}

// ✅ GOOD: Check authentication
export async function GET(request: NextRequest) {
  const cookieStore = await cookies();
  const session = cookieStore.get("session")?.value;

  if (!session || !await verifySession(session)) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    );
  }

  const users = await db.user.findMany();
  return NextResponse.json(users);
}
```

## Testing Best Practices

### Test Server Actions

```tsx
// __tests__/actions/user.test.ts
import { createUser } from "@/app/actions/users";

describe("createUser", () => {
  it("should create a user with valid data", async () => {
    const formData = new FormData();
    formData.set("name", "John Doe");
    formData.set("email", "john@example.com");

    const result = await createUser(formData);

    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty("id");
  });

  it("should return errors for invalid data", async () => {
    const formData = new FormData();
    formData.set("email", "invalid-email");

    const result = await createUser(formData);

    expect(result.success).toBe(false);
    expect(result.errors).toHaveProperty("email");
  });
});
```

### Test Route Handlers

```tsx
// __tests__/api/users.test.ts
import { GET, POST } from "@/app/api/users/route";

describe("/api/users", () => {
  it("should return users list", async () => {
    const request = new Request("http://localhost:3000/api/users");
    const response = await GET(request);

    expect(response.status).toBe(200);

    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
  });
});
```

## Deployment Best Practices

### Set Correct Environment Variables

```bash
# .env.local (development)
DATABASE_URL="postgresql://localhost:5432/dev"
NEXT_PUBLIC_API_URL="http://localhost:3000"

# .env.production (production)
DATABASE_URL="postgresql://prod-server:5432/prod"
NEXT_PUBLIC_API_URL="https://api.example.com"
```

### Enable Production Optimizations

```tsx
// next.config.ts
const nextConfig: NextConfig = {
  // Enable production optimizations
  swcMinify: true,

  // Optimize images
  images: {
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
  },

  // Enable React Compiler
  experimental: {
    reactCompiler: true,
  },
};
```

### Monitor Performance

```tsx
// app/layout.tsx
import { Analytics } from "@vercel/analytics/react";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

## Common Pitfalls

### ❌ Don't Fetch in Client Components Unnecessarily

```tsx
// ❌ BAD
"use client";
export default function Page() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch("/api/data").then(r => r.json()).then(setData);
  }, []);
}

// ✅ GOOD
export default async function Page() {
  const data = await fetch("/api/data").then(r => r.json());
  return <View data={data} />;
}
```

### ❌ Don't Forget to Await Params

```tsx
// ❌ BAD (Next.js 16)
export default async function Page({ params }: { params: { id: string } }) {
  const { id } = params; // Error! params is a Promise
}

// ✅ GOOD
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
}
```

### ❌ Don't Use Browser APIs in Server Components

```tsx
// ❌ BAD
export default function Page() {
  const width = window.innerWidth; // Error!
}

// ✅ GOOD
"use client";
export default function Page() {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    setWidth(window.innerWidth);
  }, []);
}
```

### ❌ Don't Skip Error Handling

```tsx
// ❌ BAD
export default async function Page() {
  const data = await fetchData();
  return <View data={data} />;
}

// ✅ GOOD
export default async function Page() {
  try {
    const data = await fetchData();
    return <View data={data} />;
  } catch (error) {
    console.error("Failed to fetch:", error);
    return <ErrorFallback />;
  }
}
```

## Quick Checklist

Before deploying, ensure:

- [ ] All forms use Server Actions with validation
- [ ] Sensitive data is fetched in Server Components
- [ ] Error boundaries are in place (error.tsx, global-error.tsx)
- [ ] Loading states are implemented (loading.tsx)
- [ ] Images use Next.js Image component
- [ ] Fonts are optimized with next/font
- [ ] Environment variables are properly configured
- [ ] Route handlers validate inputs
- [ ] Caching strategy is appropriate
- [ ] Authentication/authorization is implemented
- [ ] Tests cover critical paths
- [ ] Performance is monitored
- [ ] Build succeeds without warnings
