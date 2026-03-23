# Next.js App Router Patterns

Comprehensive code patterns for Next.js 16+ App Router architecture.

## Server Component Patterns

### Basic Server Component

Server Components are the default in App Router. They run only on the server and cannot use hooks or browser APIs.

```tsx
// app/users/page.tsx
async function getUsers() {
  const apiUrl = process.env.API_URL;
  const res = await fetch(`${apiUrl}/users`, {
    // Next.js caches fetch requests by default
    // Use { cache: "no-store" } to disable caching
  });
  if (!res.ok) {
    throw new Error("Failed to fetch users");
  }
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

### Server Component with Error Handling

```tsx
// app/products/[id]/page.tsx
export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  try {
    const product = await fetchProduct(id);

    if (!product) {
      notFound();
    }

    return <ProductDetail product={product} />;
  } catch (error) {
    console.error("Failed to fetch product:", error);
    throw error; // Let error.tsx handle it
  }
}
```

### Parallel Data Fetching

```tsx
// app/dashboard/page.tsx
import { cache } from "react";

// Use React's cache() to deduplicate requests
const getPosts = cache(async () => {
  return await db.post.findMany();
});

const getUsers = cache(async () => {
  return await db.user.findMany();
});

export default async function DashboardPage() {
  // These fetch in parallel
  const [posts, users] = await Promise.all([
    getPosts(),
    getUsers(),
  ]);

  return <Dashboard posts={posts} users={users} />;
}
```

## Client Component Patterns

### Client Component with State

Add `"use client"` when using hooks, browser APIs, or event handlers.

```tsx
// components/Counter.tsx
"use client";

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### Client Component with Side Effects

```tsx
// components/UserPreferences.tsx
"use client";

import { useEffect, useState } from "react";

export default function UserPreferences() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    // Read from localStorage (browser API)
    const savedTheme = localStorage.getItem("theme") || "light";
    setTheme(savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
  };

  return (
    <button onClick={toggleTheme}>
      Switch to {theme === "light" ? "dark" : "light"} mode
    </button>
  );
}
```

### Client Component Composition

Keep Server Components as the default, use Client Components only at the leaves.

```tsx
// app/page.tsx (Server Component)
import Counter from "./components/Counter";
import UserPreferences from "./components/UserPreferences";

export default function Page() {
  return (
    <main>
      <h1>Welcome</h1>
      <Counter />
      <UserPreferences />
    </main>
  );
}
```

## Route Handler Patterns

### Basic REST API

```tsx
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const users = await db.user.findMany();
    return NextResponse.json(users);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to fetch users" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const user = await db.user.create({ data: body });
    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to create user" },
      { status: 400 }
    );
  }
}
```

### Dynamic Route Handler

```tsx
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from "next/server";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = await params;

  try {
    const user = await db.user.findUnique({ where: { id } });

    if (!user) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(user);
  } catch (error) {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function PUT(
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
      { status: 400 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = await params;

  try {
    await db.user.delete({ where: { id } });
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to delete user" },
      { status: 400 }
    );
  }
}
```

### Route Handler with Authentication

```tsx
// app/api/protected/route.ts
import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function GET(request: NextRequest) {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("session")?.value;

  if (!sessionToken) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    );
  }

  // Verify session...
  const user = await getCurrentUser(sessionToken);

  return NextResponse.json({ user });
}
```

## Next.js 16 Async API Patterns

### Using Cookies and Headers

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

### Async Params and SearchParams

Params and searchParams are Promise-based in Next.js 16.

```tsx
// app/products/[id]/page.tsx
export default async function ProductPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ sort?: string; filter?: string }>;
}) {
  const { id } = await params;
  const { sort, filter } = await searchParams;

  const product = await fetchProduct(id, { sort, filter });

  return <ProductDetail product={product} />;
}
```

### Setting Cookies in Server Actions

```tsx
// app/actions.ts
"use server";

import { cookies } from "next/headers";

export async function login(formData: FormData) {
  const email = formData.get("email");
  const password = formData.get("password");

  // Authenticate...
  const sessionToken = await authenticate(email, password);

  const cookieStore = await cookies();
  cookieStore.set("session", sessionToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7, // 1 week
  });
}
```

## Caching Patterns

### Basic Cache Configuration

```tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Tag for revalidation
  cacheTag(`product-${id}`, "products");

  // Set cache duration
  cacheLife("hours");

  const product = await fetchProduct(id);
  return <ProductDetail product={product} />;
}
```

### On-Demand Revalidation

```tsx
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { tag } = await request.json();

  if (!tag) {
    return NextResponse.json(
      { error: "Tag is required" },
      { status: 400 }
    );
  }

  revalidateTag(tag);

  return NextResponse.json({ revalidated: true, tag });
}
```

```tsx
// Call from Server Action or Route Handler
import { revalidateTag, revalidatePath } from "next/cache";

// Revalidate by tag
revalidateTag("products");

// Revalidate by path
revalidatePath("/products");
```

## Parallel Route Patterns

### Basic Parallel Routes

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
      <nav>{/* Navigation */}</nav>
      <div className="content">
        {children}
        <div className="grid grid-cols-2">
          <div className="team-slot">{team}</div>
          <div className="analytics-slot">{analytics}</div>
        </div>
      </div>
    </div>
  );
}
```

```tsx
// app/dashboard/@team/page.tsx
export default function TeamPage() {
  return <div>Team Section</div>;
}

// app/dashboard/@analytics/page.tsx
export default async function AnalyticsPage() {
  const data = await fetchAnalytics();
  return <AnalyticsDashboard data={data} />;
}
```

### Default Slot for Parallel Routes

```tsx
// app/dashboard/@default/page.tsx
export default function DefaultPage() {
  return <div>Select a team member</div>;
}

// app/dashboard/@team/[memberId]/page.tsx
export default async function TeamMemberPage({
  params,
}: {
  params: Promise<{ memberId: string }>;
}) {
  const { memberId } = await params;
  const member = await fetchTeamMember(memberId);

  return <TeamMemberDetail member={member} />;
}
```

## Integration Patterns

### Server Component + Client Component

```tsx
// app/users/page.tsx (Server Component)
import UserList from "./components/UserList";

export default async function UsersPage() {
  const users = await db.user.findMany();
  return <UserList initialUsers={users} />;
}
```

```tsx
// components/UserList.tsx (Client Component)
"use client";

import { useState } from "react";

type UserListProps = {
  initialUsers: User[];
};

export default function UserList({ initialUsers }: UserListProps) {
  const [users, setUsers] = useState(initialUsers);

  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

### Server Action + Form Validation

```tsx
// app/actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";

const createUserSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  role: z.enum(["user", "admin"]),
});

export async function createUser(formData: FormData) {
  const parsed = createUserSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    role: formData.get("role"),
  });

  if (!parsed.success) {
    return {
      success: false,
      errors: parsed.error.flatten().fieldErrors,
    };
  }

  try {
    const user = await db.user.create({ data: parsed.data });
    revalidatePath("/users");
    return { success: true, user };
  } catch (error) {
    return {
      success: false,
      errors: { _form: ["Failed to create user"] },
    };
  }
}
```

## File Organization Best Practices

```
app/
├── (auth)/                    # Route group (auth routes)
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
├── (main)/                    # Route group (main routes)
│   ├── layout.tsx            # Shared layout for main routes
│   ├── page.tsx              # Home page
│   ├── about/
│   │   └── page.tsx
│   └── dashboard/
│       ├── layout.tsx        # Dashboard-specific layout
│       ├── page.tsx          # Dashboard home
│       ├── @analytics/       # Parallel route slot
│       │   └── page.tsx
│       └── @stats/           # Parallel route slot
│           └── page.tsx
├── api/                       # API routes
│   ├── users/
│   │   ├── route.ts
│   │   └── [id]/
│   │       └── route.ts
│   └── revalidate/
│       └── route.ts
├── actions/                   # Server Actions (convention)
│   ├── users.ts
│   └── posts.ts
├── layout.tsx                # Root layout
├── loading.tsx               # Root loading boundary
├── error.tsx                 # Root error boundary
└── not-found.tsx             # Custom 404 page
```

## Error Handling Patterns

### Error Boundary with error.tsx

```tsx
// app/error.tsx
"use client"; // Error boundaries must be Client Components

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Application error:", error);
  }, [error]);

  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Try-Catch in Server Components

```tsx
export default async function Page() {
  let data;

  try {
    data = await fetchData();
  } catch (error) {
    console.error("Failed to fetch data:", error);
    return <ErrorFallback message="Failed to load data" />;
  }

  return <DataDisplay data={data} />;
}
```

## Performance Patterns

### Loading States with Suspense

```tsx
// app/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 w-1/2 mb-2"></div>
      <div className="h-4 bg-gray-200 w-5/6"></div>
    </div>
  );
}
```

```tsx
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

async function Stats() {
  const data = await fetchStats();
  return <StatsDisplay data={data} />;
}

function StatsSkeleton() {
  return <div className="h-32 bg-gray-200 animate-pulse" />;
}
```

### Image and Font Optimization

```tsx
import Image from "next/image";
import { geistSans, geistMono } from "@/app/fonts";

export default function Page() {
  return (
    <main className={`${geistSans.variable} ${geistMono.variable}`}>
      <Image
        src="/hero.jpg"
        alt="Hero"
        width={1200}
        height={600}
        priority // For above-the-fold images
        placeholder="blur" // Or blurDataURL
      />
    </main>
  );
}
```
