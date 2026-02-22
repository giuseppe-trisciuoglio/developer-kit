# Next.js App Router Examples

## Example 1: Create Blog Post with Server Action

**Input:** Create a form to submit blog posts with validation

**Output:**
```tsx
// app/blog/actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";

const schema = z.object({
  title: z.string().min(5),
  content: z.string().min(10),
});

export async function createPost(formData: FormData) {
  const parsed = schema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
  });

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  await db.post.create({ data: parsed.data });
  revalidatePath("/blog");
  return { success: true };
}
```

```tsx
// app/blog/new/page.tsx
"use client";

import { useActionState } from "react";
import { createPost } from "../actions";

export default function NewPostPage() {
  const [state, formAction, pending] = useActionState(createPost, {});

  return (
    <form action={formAction}>
      <input name="title" placeholder="Title" />
      {state.errors?.title && <span>{state.errors.title[0]}</span>}

      <textarea name="content" placeholder="Content" />
      {state.errors?.content && <span>{state.errors.content[0]}</span>}

      <button type="submit" disabled={pending}>
        {pending ? "Publishing..." : "Publish"}
      </button>
    </form>
  );
}
```

## Example 2: Product Page with Caching

**Input:** Create a cached product page with revalidation

**Output:**
```tsx
// app/products/[id]/page.tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";
import { notFound } from "next/navigation";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  cacheTag(`product-${id}`, "products");
  cacheLife("hours");

  const product = await db.product.findUnique({ where: { id } });

  if (!product) {
    notFound();
  }

  return (
    <article>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p>${product.price}</p>
    </article>
  );
}
```

```tsx
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { tag } = await request.json();
  revalidateTag(tag);
  return NextResponse.json({ revalidated: true });
}
```

## Example 3: Dashboard with Parallel Routes

**Input:** Create a dashboard with sidebar and main content areas

**Output:**
```tsx
// app/dashboard/layout.tsx
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
    <div className="flex">
      <aside className="w-64">{sidebar}</aside>
      <main className="flex-1">
        <div className="grid grid-cols-3">{stats}</div>
        {children}
      </main>
    </div>
  );
}
```

```tsx
// app/dashboard/@sidebar/page.tsx
export default function Sidebar() {
  return <nav>{/* Navigation links */}</nav>;
}

// app/dashboard/@stats/page.tsx
export default async function Stats() {
  const stats = await fetchStats();
  return (
    <>
      <div>Users: {stats.users}</div>
      <div>Orders: {stats.orders}</div>
      <div>Revenue: {stats.revenue}</div>
    </>
  );
}
```
