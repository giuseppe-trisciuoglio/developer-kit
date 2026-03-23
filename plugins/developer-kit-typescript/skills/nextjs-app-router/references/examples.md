# Next.js App Router Examples

Complete, real-world examples for Next.js 16+ App Router applications.

## Example 1: Blog with Server Actions and Validation

Create a complete blog system with form validation, optimistic updates, and revalidation.

### Server Action with Zod Validation

```tsx
// app/blog/actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

const createPostSchema = z.object({
  title: z.string()
    .min(5, "Title must be at least 5 characters")
    .max(100, "Title must be less than 100 characters"),
  content: z.string()
    .min(10, "Content must be at least 10 characters")
    .max(10000, "Content must be less than 10000 characters"),
  published: z.boolean().default(false),
  tags: z.array(z.string()).default([]),
});

export async function createPost(formData: FormData) {
  "use server";

  const rawTags = formData.get("tags") as string;
  const tags = rawTags ? rawTags.split(",").map(t => t.trim()) : [];

  const parsed = createPostSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
    published: formData.get("published") === "true",
    tags,
  });

  if (!parsed.success) {
    return {
      success: false,
      errors: parsed.error.flatten().fieldErrors,
    };
  }

  try {
    const post = await db.post.create({
      data: {
        ...parsed.data,
        authorId: await getCurrentUserId(),
        slug: generateSlug(parsed.data.title),
      },
    });

    revalidatePath("/blog");
    revalidatePath("/admin");

    if (parsed.data.published) {
      redirect(`/blog/${post.slug}`);
    }

    return { success: true, post };
  } catch (error) {
    console.error("Failed to create post:", error);
    return {
      success: false,
      errors: { _form: ["Failed to create post. Please try again."] },
    };
  }
}

export async function updatePost(id: string, formData: FormData) {
  "use server";

  const post = await db.post.findUnique({ where: { id } });

  if (!post) {
    return {
      success: false,
      errors: { _form: ["Post not found"] },
    };
  }

  const rawTags = formData.get("tags") as string;
  const tags = rawTags ? rawTags.split(",").map(t => t.trim()) : [];

  const parsed = createPostSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
    published: formData.get("published") === "true",
    tags,
  });

  if (!parsed.success) {
    return {
      success: false,
      errors: parsed.error.flatten().fieldErrors,
    };
  }

  try {
    const updated = await db.post.update({
      where: { id },
      data: {
        ...parsed.data,
        slug: generateSlug(parsed.data.title),
      },
    });

    revalidatePath("/blog");
    revalidatePath("/admin");
    revalidatePath(`/blog/${updated.slug}`);

    return { success: true, post: updated };
  } catch (error) {
    return {
      success: false,
      errors: { _form: ["Failed to update post"] },
    };
  }
}

export async function deletePost(id: string) {
  "use server";

  try {
    await db.post.delete({ where: { id } });
    revalidatePath("/blog");
    revalidatePath("/admin");
    return { success: true };
  } catch (error) {
    return {
      success: false,
      errors: { _form: ["Failed to delete post"] },
    };
  }
}
```

### Form Component with useActionState

```tsx
// app/blog/new/page.tsx
"use client";

import { useActionState, useEffect } from "react";
import { createPost } from "../actions";
import { useRouter } from "next/navigation";

type FormState = {
  errors?: Record<string, string[]>;
  success?: boolean;
  post?: Post;
};

export default function NewPostPage() {
  const router = useRouter();
  const [state, formAction, pending] = useActionState<FormState, FormData>(
    createPost,
    {}
  );

  useEffect(() => {
    if (state.success && state.post) {
      router.push(`/blog/${state.post.slug}`);
    }
  }, [state.success, state.post, router]);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Create New Post</h1>

      <form action={formAction} className="space-y-4">
        {/* Title Field */}
        <div>
          <label htmlFor="title" className="block mb-1">
            Title
          </label>
          <input
            type="text"
            id="title"
            name="title"
            className="w-full px-3 py-2 border rounded"
            disabled={pending}
          />
          {state.errors?.title && (
            <span className="text-red-500 text-sm">
              {state.errors.title[0]}
            </span>
          )}
        </div>

        {/* Content Field */}
        <div>
          <label htmlFor="content" className="block mb-1">
            Content
          </label>
          <textarea
            id="content"
            name="content"
            rows={10}
            className="w-full px-3 py-2 border rounded"
            disabled={pending}
          />
          {state.errors?.content && (
            <span className="text-red-500 text-sm">
              {state.errors.content[0]}
            </span>
          )}
        </div>

        {/* Tags Field */}
        <div>
          <label htmlFor="tags" className="block mb-1">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            id="tags"
            name="tags"
            placeholder="react, nextjs, webdev"
            className="w-full px-3 py-2 border rounded"
            disabled={pending}
          />
        </div>

        {/* Published Checkbox */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="published"
            name="published"
            value="true"
            className="mr-2"
            disabled={pending}
          />
          <label htmlFor="published">Publish immediately</label>
        </div>

        {/* Form Errors */}
        {state.errors?._form && (
          <div className="bg-red-50 text-red-600 p-3 rounded">
            {state.errors._form[0]}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={pending}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          {pending ? "Creating..." : "Create Post"}
        </button>
      </form>
    </div>
  );
}
```

### Blog Listing Page

```tsx
// app/blog/page.tsx
import Link from "next/link";
import { cache } from "react";

const getPosts = cache(async () => {
  return await db.post.findMany({
    where: { published: true },
    include: { author: true },
    orderBy: { createdAt: "desc" },
  });
});

export default async function BlogPage() {
  const posts = await getPosts();

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-4xl font-bold mb-8">Blog</h1>

      <div className="space-y-6">
        {posts.map(post => (
          <article key={post.id} className="border-b pb-6">
            <Link href={`/blog/${post.slug}`}>
              <h2 className="text-2xl font-semibold hover:text-blue-500">
                {post.title}
              </h2>
            </Link>
            <p className="text-gray-600 mt-2">
              By {post.author.name} • {formatDate(post.createdAt)}
            </p>
            <p className="mt-3">{post.content.substring(0, 200)}...</p>
            <div className="mt-3 flex gap-2">
              {post.tags.map(tag => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-100 text-sm rounded"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
```

## Example 2: E-commerce Product Page with Caching

Create a product catalog page with caching, revalidation, and shopping cart.

### Product Page with Cache

```tsx
// app/products/[id]/page.tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";
import { notFound } from "next/navigation";
import AddToCart from "./AddToCart";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Tag for revalidation
  cacheTag(`product-${id}`, "products", "catalog");

  // Cache for hours
  cacheLife("hours");

  const product = await db.product.findUnique({
    where: { id },
    include: {
      category: true,
      reviews: {
        include: { user: true },
        orderBy: { createdAt: "desc" },
        take: 10,
      },
    },
  });

  if (!product) {
    notFound();
  }

  const relatedProducts = await db.product.findMany({
    where: {
      categoryId: product.categoryId,
      id: { not: product.id },
    },
    take: 4,
  });

  return (
    <div className="max-w-6xl mx-auto p-4">
      {/* Product Details */}
      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <Image
            src={product.image}
            alt={product.name}
            width={600}
            height={600}
            className="rounded"
          />
        </div>

        <div>
          <h1 className="text-3xl font-bold">{product.name}</h1>
          <p className="text-2xl mt-2">${product.price}</p>

          <p className="mt-4 text-gray-700">{product.description}</p>

          <div className="mt-6">
            <AddToCart productId={product.id} />
          </div>

          <div className="mt-6">
            <h3 className="font-semibold">Category</h3>
            <p>{product.category.name}</p>
          </div>

          {product.specifications && (
            <div className="mt-6">
              <h3 className="font-semibold">Specifications</h3>
              <ul className="list-disc list-inside">
                {Object.entries(product.specifications).map(([key, value]) => (
                  <li key={key}>
                    {key}: {value}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Reviews */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold mb-4">Reviews</h2>
        <div className="space-y-4">
          {product.reviews.map(review => (
            <div key={review.id} className="border-b pb-4">
              <div className="flex justify-between">
                <p className="font-semibold">{review.user.name}</p>
                <p className="text-gray-500">{formatDate(review.createdAt)}</p>
              </div>
              <p className="mt-2">{review.comment}</p>
              <p className="text-yellow-500">{"★".repeat(review.rating)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Related Products */}
      {relatedProducts.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-4">Related Products</h2>
          <div className="grid grid-cols-4 gap-4">
            {relatedProducts.map(related => (
              <Link
                key={related.id}
                href={`/products/${related.id}`}
                className="border rounded p-4 hover:shadow-lg"
              >
                <Image
                  src={related.image}
                  alt={related.name}
                  width={200}
                  height={200}
                />
                <h3 className="font-semibold mt-2">{related.name}</h3>
                <p className="text-lg">${related.price}</p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### Add to Cart Server Action

```tsx
// app/actions/cart.ts
"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";

export async function addToCart(productId: string, quantity: number = 1) {
  const cookieStore = await cookies();
  const cart = JSON.parse(cookieStore.get("cart")?.value || "[]");

  const existingItem = cart.find((item: CartItem) => item.productId === productId);

  if (existingItem) {
    existingItem.quantity += quantity;
  } else {
    cart.push({ productId, quantity });
  }

  cookieStore.set("cart", JSON.stringify(cart), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
  });

  revalidatePath("/cart");
  revalidatePath(`/products/${productId}`);

  return { success: true, cartSize: cart.length };
}
```

```tsx
// app/products/[id]/AddToCart.tsx
"use client";

import { useActionState } from "react";
import { addToCart } from "@/app/actions/cart";

export default function AddToCart({ productId }: { productId: string }) {
  const [state, formAction, pending] = useActionState(
    addToCart.bind(null, productId),
    {}
  );

  return (
    <form action={formAction}>
      <button
        type="submit"
        disabled={pending}
        className="px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {pending ? "Adding..." : "Add to Cart"}
      </button>
    </form>
  );
}
```

### Revalidation Route Handler

```tsx
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from "next/cache";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST(request: Request) {
  const body = await request.json();
  const { type, value } = body;

  // Verify admin session
  const cookieStore = await cookies();
  const session = cookieStore.get("session")?.value;
  if (!session || !await isAdmin(session)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    if (type === "tag") {
      revalidateTag(value);
      return NextResponse.json({
        revalidated: true,
        type: "tag",
        value,
      });
    } else if (type === "path") {
      revalidatePath(value);
      return NextResponse.json({
        revalidated: true,
        type: "path",
        value,
      });
    }

    return NextResponse.json({ error: "Invalid type" }, { status: 400 });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to revalidate" },
      { status: 500 }
    );
  }
}
```

## Example 3: Dashboard with Parallel Routes

Create a dashboard with sidebar, stats, and main content using parallel routes.

### Dashboard Layout

```tsx
// app/dashboard/layout.tsx
import Link from "next/link";
import { Suspense } from "react";

export default function DashboardLayout({
  children,
  sidebar,
  stats,
}: {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  stats: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar Slot */}
      <aside className="w-64 bg-white shadow-md">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold">Dashboard</h1>
        </div>
        <Suspense fallback={<SidebarSkeleton />}>
          {sidebar}
        </Suspense>
      </aside>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Stats Slot */}
        <div className="bg-white shadow-sm border-b">
          <Suspense fallback={<StatsSkeleton />}>
            {stats}
          </Suspense>
        </div>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

function SidebarSkeleton() {
  return (
    <div className="p-4 space-y-2">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-10 bg-gray-200 animate-pulse rounded" />
      ))}
    </div>
  );
}

function StatsSkeleton() {
  return (
    <div className="p-6 grid grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-24 bg-gray-200 animate-pulse rounded" />
      ))}
    </div>
  );
}
```

### Sidebar Slot

```tsx
// app/dashboard/@sidebar/page.tsx
"use client";

import { useSelectedLayoutSegment } from "next/navigation";
import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: "📊" },
  { href: "/dashboard/users", label: "Users", icon: "👥" },
  { href: "/dashboard/products", label: "Products", icon: "📦" },
  { href: "/dashboard/orders", label: "Orders", icon: "🛒" },
  { href: "/dashboard/analytics", label: "Analytics", icon: "📈" },
];

export default function Sidebar() {
  const segment = useSelectedLayoutSegment();

  return (
    <nav className="p-4">
      <ul className="space-y-1">
        {navItems.map(item => {
          const isActive = item.href === `/dashboard${segment ? `/${segment}` : ""}`;

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded transition-colors ${
                  isActive
                    ? "bg-blue-500 text-white"
                    : "hover:bg-gray-100"
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
```

### Stats Slot

```tsx
// app/dashboard/@stats/page.tsx
import { cache } from "react";

const getStats = cache(async () => {
  const [users, products, orders, revenue] = await Promise.all([
    db.user.count(),
    db.product.count(),
    db.order.count(),
    db.order.aggregate({ _sum: { total: true } }),
  ]);

  return {
    users,
    products,
    orders,
    revenue: revenue._sum.total || 0,
  };
});

export default async function Stats() {
  const stats = await getStats();

  const statItems = [
    { label: "Total Users", value: stats.users, color: "bg-blue-500" },
    { label: "Products", value: stats.products, color: "bg-green-500" },
    { label: "Orders", value: stats.orders, color: "bg-yellow-500" },
    { label: "Revenue", value: `$${stats.revenue.toLocaleString()}`, color: "bg-purple-500" },
  ];

  return (
    <div className="p-6 grid grid-cols-4 gap-4">
      {statItems.map(item => (
        <div key={item.label} className="bg-white rounded-lg shadow p-6">
          <div className={`inline-block p-3 rounded-full ${item.color} text-white mb-2`}>
            📊
          </div>
          <h3 className="text-gray-500 text-sm">{item.label}</h3>
          <p className="text-2xl font-bold">{item.value}</p>
        </div>
      ))}
    </div>
  );
}
```

### Overview Page

```tsx
// app/dashboard/page.tsx
import { Suspense } from "react";
import RecentOrders from "./RecentOrders";
import TopProducts from "./TopProducts";

export default function DashboardPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard Overview</h2>

      <div className="grid md:grid-cols-2 gap-6">
        <Suspense fallback={<LoadingSpinner />}>
          <RecentOrders />
        </Suspense>

        <Suspense fallback={<LoadingSpinner />}>
          <TopProducts />
        </Suspense>
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="bg-white rounded-lg shadow p-6 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
    </div>
  );
}
```

```tsx
// app/dashboard/RecentOrders.tsx
async function RecentOrders() {
  const orders = await db.order.findMany({
    take: 10,
    orderBy: { createdAt: "desc" },
    include: { user: true },
  });

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="font-semibold">Recent Orders</h3>
      </div>
      <div className="p-4">
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-500">
              <th className="pb-2">Order ID</th>
              <th className="pb-2">Customer</th>
              <th className="pb-2">Total</th>
              <th className="pb-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(order => (
              <tr key={order.id} className="border-t">
                <td className="py-2">#{order.id}</td>
                <td className="py-2">{order.user.name}</td>
                <td className="py-2">${order.total}</td>
                <td className="py-2">
                  <span className={`px-2 py-1 rounded text-sm ${
                    order.status === "completed" ? "bg-green-100 text-green-700" :
                    order.status === "pending" ? "bg-yellow-100 text-yellow-700" :
                    "bg-red-100 text-red-700"
                  }`}>
                    {order.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

## Example 4: Authentication Flow

### Login Page with Server Actions

```tsx
// app/login/actions.ts
"use server";

import { z } from "zod";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const loginSchema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export async function login(formData: FormData) {
  const parsed = loginSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
  });

  if (!parsed.success) {
    return {
      success: false,
      errors: parsed.error.flatten().fieldErrors,
    };
  }

  const { email, password } = parsed.data;

  const user = await db.user.findUnique({ where: { email } });

  if (!user || !await verifyPassword(user.password, password)) {
    return {
      success: false,
      errors: { _form: ["Invalid email or password"] },
    };
  }

  const sessionToken = await createSession(user.id);
  const cookieStore = await cookies();

  cookieStore.set("session", sessionToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7, // 1 week
    path: "/",
  });

  redirect("/dashboard");
}

export async function logout() {
  const cookieStore = await cookies();
  cookieStore.delete("session");
  redirect("/login");
}
```

```tsx
// app/login/page.tsx
"use client";

import { useActionState } from "react";
import { login } from "./actions";

export default function LoginPage() {
  const [state, formAction, pending] = useActionState(login, {});

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6">Sign In</h1>

        <form action={formAction} className="space-y-4">
          <div>
            <label htmlFor="email" className="block mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              className="w-full px-3 py-2 border rounded"
              disabled={pending}
              required
            />
            {state.errors?.email && (
              <span className="text-red-500 text-sm">
                {state.errors.email[0]}
              </span>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block mb-1">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              className="w-full px-3 py-2 border rounded"
              disabled={pending}
              required
            />
            {state.errors?.password && (
              <span className="text-red-500 text-sm">
                {state.errors.password[0]}
              </span>
            )}
          </div>

          {state.errors?._form && (
            <div className="bg-red-50 text-red-600 p-3 rounded text-sm">
              {state.errors._form[0]}
            </div>
          )}

          <button
            type="submit"
            disabled={pending}
            className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
          >
            {pending ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm">
          Don't have an account?{" "}
          <a href="/register" className="text-blue-500 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
```

### Protected Route Middleware

```tsx
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  const session = request.cookies.get("session")?.value;
  const { pathname } = request.url;

  // Public routes
  if (pathname.startsWith("/login") || pathname.startsWith("/register")) {
    if (session) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  // Protected routes
  if (pathname.startsWith("/dashboard") || pathname.startsWith("/api")) {
    if (!session) {
      return NextResponse.redirect(new URL("/login", request.url));
    }

    // Verify session is valid
    const user = await getUserFromSession(session);
    if (!user) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

## Example 5: Search and Filtering

### Search Page with Server Actions

```tsx
// app/search/page.tsx
import { Suspense } from "react";
import SearchResults from "./SearchResults";
import SearchFilters from "./SearchFilters";

interface SearchParams {
  query?: string;
  category?: string;
  minPrice?: string;
  maxPrice?: string;
  sort?: string;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Search Products</h1>

      <div className="flex gap-6">
        {/* Filters Sidebar */}
        <aside className="w-64 flex-shrink-0">
          <SearchFilters currentParams={params} />
        </aside>

        {/* Results */}
        <main className="flex-1">
          <Suspense fallback={<ResultsSkeleton />}>
            <SearchResults params={params} />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
```

```tsx
// app/search/SearchResults.tsx
export default async function SearchResults({
  params,
}: {
  params: SearchParams;
}) {
  const products = await searchProducts(params);

  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No products found</p>
      </div>
    );
  }

  return (
    <div>
      <p className="mb-4 text-gray-600">
        Found {products.length} products
      </p>

      <div className="grid grid-cols-3 gap-4">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}

async function searchProducts(params: SearchParams) {
  const where: any = {};

  if (params.query) {
    where.OR = [
      { name: { contains: params.query, mode: "insensitive" } },
      { description: { contains: params.query, mode: "insensitive" } },
    ];
  }

  if (params.category) {
    where.categoryId = params.category;
  }

  if (params.minPrice || params.maxPrice) {
    where.price = {};
    if (params.minPrice) where.price.gte = parseFloat(params.minPrice);
    if (params.maxPrice) where.price.lte = parseFloat(params.maxPrice);
  }

  const orderBy: any = {};
  if (params.sort === "price-asc") orderBy.price = "asc";
  else if (params.sort === "price-desc") orderBy.price = "desc";
  else orderBy.createdAt = "desc";

  return await db.product.findMany({
    where,
    orderBy,
    include: { category: true },
  });
}
```

```tsx
// app/search/SearchFilters.tsx
"use client";

import { useRouter, useSearchParams } from "next/navigation";

export default function SearchFilters({
  currentParams,
}: {
  currentParams: SearchParams;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function updateFilters(updates: Record<string, string>) {
    const params = new URLSearchParams(searchParams.toString());

    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });

    router.push(`/search?${params.toString()}`);
  }

  return (
    <div className="bg-white p-4 rounded shadow">
      <h3 className="font-semibold mb-4">Filters</h3>

      <div className="space-y-4">
        <div>
          <label className="block mb-1">Search</label>
          <input
            type="text"
            defaultValue={currentParams.query}
            onChange={(e) => updateFilters({ query: e.target.value })}
            placeholder="Search products..."
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label className="block mb-1">Category</label>
          <select
            defaultValue={currentParams.category}
            onChange={(e) => updateFilters({ category: e.target.value })}
            className="w-full px-3 py-2 border rounded"
          >
            <option value="">All Categories</option>
            <option value="1">Electronics</option>
            <option value="2">Clothing</option>
            <option value="3">Books</option>
          </select>
        </div>

        <div>
          <label className="block mb-1">Price Range</label>
          <div className="flex gap-2">
            <input
              type="number"
              defaultValue={currentParams.minPrice}
              onChange={(e) => updateFilters({ minPrice: e.target.value })}
              placeholder="Min"
              className="w-1/2 px-3 py-2 border rounded"
            />
            <input
              type="number"
              defaultValue={currentParams.maxPrice}
              onChange={(e) => updateFilters({ maxPrice: e.target.value })}
              placeholder="Max"
              className="w-1/2 px-3 py-2 border rounded"
            />
          </div>
        </div>

        <div>
          <label className="block mb-1">Sort By</label>
          <select
            defaultValue={currentParams.sort}
            onChange={(e) => updateFilters({ sort: e.target.value })}
            className="w-full px-3 py-2 border rounded"
          >
            <option value="">Newest</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
          </select>
        </div>
      </div>
    </div>
  );
}
```

## Utility Functions

```tsx
// lib/utils.ts
export function formatDate(date: Date | string): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date));
}

export function generateSlug(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim();
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + "...";
}
```
