# Next.js App Router - Detailed Examples

This document contains comprehensive, real-world examples for Next.js 16+ App Router development.

## Table of Contents

- [Example 1: Blog with Server Actions](#example-1-blog-with-server-actions)
- [Example 2: E-commerce Product Page with Caching](#example-2-ecommerce-product-page-with-caching)
- [Example 3: Dashboard with Parallel Routes](#example-3-dashboard-with-parallel-routes)
- [Example 4: Image Gallery with Infinite Scroll](#example-4-image-gallery-with-infinite-scroll)
- [Example 5: Real-time Chat App](#example-5-real-time-chat-app)

---

## Example 1: Blog with Server Actions

Complete blog platform with post creation, validation, and optimistic updates.

### Architecture

```
app/
├── blog/
│   ├── page.tsx              # Blog listing
│   ├── [slug]/
│   │   └── page.tsx          # Single post
│   ├── new/
│   │   └── page.tsx          # Create post form
│   └── actions.ts            # Server actions
├── components/
│   ├── PostCard.tsx          # Client component
│   └── CommentForm.tsx       # Comment form
└── lib/
    └── db.ts                 # Database client
```

### Server Actions with Validation

```tsx
// app/blog/actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";

// Validation schemas
const CreatePostSchema = z.object({
  title: z.string()
    .min(5, "Title must be at least 5 characters")
    .max(100, "Title must not exceed 100 characters"),
  content: z.string()
    .min(10, "Content must be at least 10 characters")
    .max(10000, "Content must not exceed 10000 characters"),
  excerpt: z.string().max(200).optional(),
  published: z.boolean().default(false),
});

const CreateCommentSchema = z.object({
  postId: z.string().uuid(),
  author: z.string().min(2, "Author name required"),
  content: z.string().min(5, "Comment must be at least 5 characters"),
});

// Create post action
export async function createPost(prevState: any, formData: FormData) {
  const rawData = {
    title: formData.get("title"),
    content: formData.get("content"),
    excerpt: formData.get("excerpt"),
    published: formData.get("published") === "true",
  };

  const result = CreatePostSchema.safeParse(rawData);

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors,
      message: "Validation failed",
    };
  }

  try {
    const post = await db.post.create({
      data: {
        ...result.data,
        slug: generateSlug(result.data.title),
        authorId: getCurrentUserId(),
      },
    });

    revalidatePath("/blog");
    revalidatePath("/blog/new");

    return {
      success: true,
      post,
      message: "Post created successfully",
    };
  } catch (error) {
    return {
      success: false,
      message: "Failed to create post",
      errors: { _form: ["Database error occurred"] },
    };
  }
}

// Create comment action with optimistic update support
export async function createComment(prevState: any, formData: FormData) {
  const rawData = {
    postId: formData.get("postId"),
    author: formData.get("author"),
    content: formData.get("content"),
  };

  const result = CreateCommentSchema.safeParse(rawData);

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors,
    };
  }

  try {
    const comment = await db.comment.create({
      data: result.data,
    });

    revalidatePath(`/blog/${rawData.postId}`);

    return {
      success: true,
      comment,
    };
  } catch (error) {
    return {
      success: false,
      message: "Failed to create comment",
    };
  }
}

// Delete post action
export async function deletePost(formData: FormData) {
  const id = formData.get("id") as string;

  await db.post.delete({
    where: { id },
  });

  revalidatePath("/blog");
  redirect("/blog");
}

// Helper function to generate URL-friendly slugs
function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function getCurrentUserId(): string {
  // Implement authentication logic
  return "user-id";
}
```

### Blog Listing Page

```tsx
// app/blog/page.tsx
import Link from "next/link";
import { Suspense } from "react";

async function getPosts() {
  const posts = await db.post.findMany({
    where: { published: true },
    orderBy: { createdAt: "desc" },
    include: {
      author: {
        select: { name: true },
      },
      _count: {
        select: { comments: true },
      },
    },
  });

  return posts;
}

export default async function BlogPage() {
  return (
    <div className="blog-container">
      <header className="blog-header">
        <h1>Blog</h1>
        <Link href="/blog/new" className="btn-primary">
          New Post
        </Link>
      </header>

      <Suspense fallback={<PostsSkeleton />}>
        <PostsList />
      </Suspense>
    </div>
  );
}

async function PostsList() {
  const posts = await getPosts();

  return (
    <div className="posts-grid">
      {posts.map(post => (
        <article key={post.id} className="post-card">
          <Link href={`/blog/${post.slug}`}>
            <h2>{post.title}</h2>
            {post.excerpt && <p>{post.excerpt}</p>}
          </Link>
          <div className="post-meta">
            <span>By {post.author.name}</span>
            <time>{new Date(post.createdAt).toLocaleDateString()}</time>
            <span>{post._count.comments} comments</span>
          </div>
        </article>
      ))}
    </div>
  );
}

function PostsSkeleton() {
  return (
    <div className="posts-grid">
      {[1, 2, 3, 4, 5, 6].map(i => (
        <div key={i} className="post-card skeleton">
          <div className="skeleton-title" />
          <div className="skeleton-excerpt" />
          <div className="skeleton-meta" />
        </div>
      ))}
    </div>
  );
}
```

### Create Post Form with Client Components

```tsx
// app/blog/new/page.tsx
"use client";

import { useActionState } from "react";
import { useRouter } from "next/navigation";
import { createPost } from "../actions";

export default function NewPostPage() {
  const router = useRouter();
  const [state, formAction, pending] = useActionState(createPost, null);

  // Redirect on success
  if (state?.success) {
    router.push(`/blog/${state.post.slug}`);
    router.refresh();
  }

  return (
    <div className="container">
      <h1>Create New Post</h1>

      <form action={formAction} className="post-form">
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            disabled={pending}
            aria-invalid={!!state?.errors?.title}
          />
          {state?.errors?.title && (
            <span className="error">{state.errors.title[0]}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="excerpt">Excerpt (optional)</label>
          <textarea
            id="excerpt"
            name="excerpt"
            rows={2}
            disabled={pending}
          />
        </div>

        <div className="form-group">
          <label htmlFor="content">Content</label>
          <textarea
            id="content"
            name="content"
            rows={15}
            disabled={pending}
            aria-invalid={!!state?.errors?.content}
          />
          {state?.errors?.content && (
            <span className="error">{state.errors.content[0]}</span>
          )}
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              name="published"
              value="true"
              disabled={pending}
            />
            Publish immediately
          </label>
        </div>

        {state?.message && !state.success && (
          <div className="alert alert-error">{state.message}</div>
        )}

        <div className="form-actions">
          <button
            type="submit"
            disabled={pending}
            className="btn-primary"
          >
            {pending ? "Creating..." : "Create Post"}
          </button>
          <button
            type="button"
            disabled={pending}
            onClick={() => router.back()}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
```

### Single Post with Comments

```tsx
// app/blog/[slug]/page.tsx
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { CommentSection } from "./CommentSection";

async function getPost(slug: string) {
  const post = await db.post.findUnique({
    where: { slug },
    include: {
      author: {
        select: { name: true, email: true },
      },
      comments: {
        orderBy: { createdAt: "desc" },
      },
    },
  });

  return post;
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getPost(slug);

  if (!post) {
    notFound();
  }

  return (
    <article className="post">
      <header className="post-header">
        <h1>{post.title}</h1>
        <div className="post-meta">
          <span>By {post.author.name}</span>
          <time>
            {new Date(post.createdAt).toLocaleDateString()}
          </time>
        </div>
      </header>

      {post.excerpt && (
        <p className="post-excerpt">{post.excerpt}</p>
      )}

      <div className="post-content">
        {post.content}
      </div>

      <Suspense fallback={<CommentsSkeleton />}>
        <CommentSection postId={post.id} comments={post.comments} />
      </Suspense>
    </article>
  );
}

function CommentsSkeleton() {
  return (
    <div className="comments-section">
      <h2>Comments</h2>
      <div className="comment-skeletons">
        {[1, 2, 3].map(i => (
          <div key={i} className="comment skeleton" />
        ))}
      </div>
    </div>
  );
}
```

### Comment Section with Optimistic Updates

```tsx
// app/blog/[slug]/CommentSection.tsx
"use client";

import { useOptimistic, useActionState } from "react";
import { createComment } from "../../actions";

interface Comment {
  id: string;
  author: string;
  content: string;
  createdAt: Date;
}

export function CommentSection({
  postId,
  comments,
}: {
  postId: string;
  comments: Comment[];
}) {
  const [optimisticComments, addOptimisticComment] = useOptimistic(
    comments,
    (state, newComment: Comment) => [
      { ...newComment, id: "temp", createdAt: new Date() },
      ...state,
    ]
  );

  const [state, formAction, pending] = useActionState(
    createComment.bind(null, postId),
    null
  );

  async function handleSubmit(formData: FormData) {
    formData.append("postId", postId);

    const author = formData.get("author") as string;
    const content = formData.get("content") as string;

    addOptimisticComment({ author, content } as Comment);
    formAction(formData);
  }

  return (
    <section className="comments-section">
      <h2>Comments ({optimisticComments.length})</h2>

      <form action={handleSubmit} className="comment-form">
        <input
          type="text"
          name="author"
          placeholder="Your name"
          required
          disabled={pending}
        />
        <textarea
          name="content"
          placeholder="Write a comment..."
          rows={3}
          required
          disabled={pending}
        />
        <button type="submit" disabled={pending}>
          {pending ? "Posting..." : "Post Comment"}
        </button>
      </form>

      <div className="comments-list">
        {optimisticComments.map(comment => (
          <div key={comment.id} className="comment">
            <div className="comment-header">
              <strong>{comment.author}</strong>
              <time>
                {new Date(comment.createdAt).toLocaleString()}
              </time>
            </div>
            <p>{comment.content}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
```

---

## Example 2: E-commerce Product Page with Caching

High-performance product catalog with intelligent caching and revalidation.

### Product Page with Advanced Caching

```tsx
// app/products/[id]/page.tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";
import { notFound } from "next/navigation";
import { Suspense } from "react";

async function getProduct(id: string) {
  const product = await db.product.findUnique({
    where: { id },
    include: {
      category: true,
      variants: true,
      reviews: {
        take: 10,
        orderBy: { createdAt: "desc" },
      },
    },
  });

  return product;
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Tag for selective revalidation
  cacheTag(`product-${id}`, "products", "catalog");

  // Cache for 1 hour with stale-while-revalidate
  cacheLife({
    stale: 60,
    revalidate: 3600,
  });

  const product = await getProduct(id);

  if (!product) {
    notFound();
  }

  return (
    <div className="product-page">
      <ProductDetail product={product} />

      <Suspense fallback={<ReviewsSkeleton />}>
        <ProductReviews productId={product.id} />
      </Suspense>

      <Suspense fallback={<RecommendationsSkeleton />}>
        <RelatedProducts
          categoryId={product.category.id}
          currentProductId={product.id}
        />
      </Suspense>
    </div>
  );
}

// Separate component with different cache strategy
async function RelatedProducts({
  categoryId,
  currentProductId,
}: {
  categoryId: string;
  currentProductId: string;
}) {
  "use cache";

  cacheTag("related-products", `category-${categoryId}`);
  cacheLife("days");

  const products = await db.product.findMany({
    where: {
      categoryId,
      id: { not: currentProductId },
    },
    take: 4,
  });

  return (
    <section className="related-products">
      <h2>You might also like</h2>
      <div className="products-grid">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
```

### Revalidation API Endpoint

```tsx
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from "next/cache";
import { NextResponse } from "next/server";
import { z } from "zod";

const RevalidateSchema = z.object({
  type: z.enum(["tag", "path"]),
  value: z.string(),
  secret: z.string(),
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const result = RevalidateSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        { error: "Invalid request" },
        { status: 400 }
      );
    }

    // Verify secret to prevent unauthorized revalidation
    if (result.data.secret !== process.env.REVALIDATION_SECRET) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const { type, value } = result.data;

    if (type === "tag") {
      revalidateTag(value);
    } else {
      revalidatePath(value);
    }

    return NextResponse.json({
      revalidated: true,
      now: Date.now(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

### Server Action for Product Updates with Revalidation

```tsx
// app/actions/products.ts
"use server";

import { revalidateTag, revalidatePath } from "next/cache";
import { z } from "zod";

const UpdateProductSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  description: z.string(),
  price: z.number().positive(),
  stock: z.number().int().min(0),
});

export async function updateProduct(prevState: any, formData: FormData) {
  const rawData = {
    id: formData.get("id"),
    name: formData.get("name"),
    description: formData.get("description"),
    price: Number(formData.get("price")),
    stock: Number(formData.get("stock")),
  };

  const result = UpdateProductSchema.safeParse(rawData);

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors,
    };
  }

  try {
    const product = await db.product.update({
      where: { id: result.data.id },
      data: result.data,
    });

    // Revalidate specific product
    revalidateTag(`product-${product.id}`);

    // Revalidate product listings
    revalidateTag("products");

    // Revalidate category pages
    revalidateTag(`category-${product.categoryId}`);

    // Revalidate paths
    revalidatePath(`/products/${product.id}`);
    revalidatePath("/products");

    return {
      success: true,
      product,
    };
  } catch (error) {
    return {
      success: false,
      message: "Failed to update product",
    };
  }
}

export async function updateInventory(
  productId: string,
  quantity: number
) {
  await db.product.update({
    where: { id: productId },
    data: {
      stock: { increment: -quantity },
    },
  });

  // Immediate revalidation for inventory-critical pages
  revalidateTag(`product-${productId}`);
  revalidateTag("low-stock");
}
```

---

## Example 3: Dashboard with Parallel Routes

Complex dashboard with sidebar, multiple panels, and independent data loading.

### Dashboard Layout Structure

```tsx
// app/dashboard/layout.tsx
import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";

export default function DashboardLayout({
  children,
  sidebar,
  stats,
  notifications,
}: {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  stats: React.ReactNode;
  notifications: React.ReactNode;
}) {
  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        {sidebar}
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <h1>Dashboard</h1>
          <nav className="dashboard-nav">
            <Link href="/dashboard/overview">Overview</Link>
            <Link href="/dashboard/analytics">Analytics</Link>
            <Link href="/dashboard/settings">Settings</Link>
          </nav>
        </header>

        <div className="dashboard-panels">
          <div className="panel stats-panel">
            {stats}
          </div>

          <div className="panel notifications-panel">
            {notifications}
          </div>
        </div>

        <div className="dashboard-content">
          {children}
        </div>
      </main>
    </div>
  );
}
```

### Sidebar Slot

```tsx
// app/dashboard/@sidebar/default.tsx
export default function Sidebar() {
  return (
    <nav className="sidebar">
      <Link href="/dashboard" className="sidebar-logo">
        Dashboard
      </Link>

      <ul className="sidebar-menu">
        <li>
          <Link href="/dashboard/overview">
            Overview
          </Link>
        </li>
        <li>
          <Link href="/dashboard/analytics">
            Analytics
          </Link>
        </li>
        <li>
          <Link href="/dashboard/reports">
            Reports
          </Link>
        </li>
        <li>
          <Link href="/dashboard/settings">
            Settings
          </Link>
        </li>
      </ul>
    </nav>
  );
}
```

### Stats Slot with Real-time Data

```tsx
// app/dashboard/@stats/page.tsx
import { Suspense } from "react";

async function getDashboardStats() {
  const [users, orders, revenue] = await Promise.all([
    db.user.count(),
    db.order.count(),
    db.order.aggregate({
      _sum: { total: true },
    }),
  ]);

  return {
    users,
    orders,
    revenue: revenue._sum.total || 0,
  };
}

export default async function StatsPanel() {
  return (
    <div className="stats-panel">
      <h2>Statistics</h2>

      <Suspense fallback={<StatsSkeleton />}>
        <StatsData />
      </Suspense>
    </div>
  );
}

async function StatsData() {
  const stats = await getDashboardStats();

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <p className="stat-label">Total Users</p>
        <p className="stat-value">{stats.users}</p>
      </div>

      <div className="stat-card">
        <p className="stat-label">Total Orders</p>
        <p className="stat-value">{stats.orders}</p>
      </div>

      <div className="stat-card">
        <p className="stat-label">Revenue</p>
        <p className="stat-value">${stats.revenue.toLocaleString()}</p>
      </div>
    </div>
  );
}

function StatsSkeleton() {
  return (
    <div className="stats-grid">
      {[1, 2, 3].map(i => (
        <div key={i} className="stat-card skeleton">
          <div className="skeleton-label" />
          <div className="skeleton-value" />
        </div>
      ))}
    </div>
  );
}
```

### Notifications Slot

```tsx
// app/dashboard/@notifications/page.tsx
import { Suspense } from "react";

async function getNotifications() {
  const notifications = await db.notification.findMany({
    where: { userId: getCurrentUserId() },
    orderBy: { createdAt: "desc" },
    take: 5,
  });

  return notifications;
}

export default async function NotificationsPanel() {
  return (
    <div className="notifications-panel">
      <h2>Notifications</h2>

      <Suspense fallback={<NotificationsSkeleton />}>
        <NotificationsList />
      </Suspense>
    </div>
  );
}

async function NotificationsList() {
  const notifications = await getNotifications();

  if (notifications.length === 0) {
    return <p>No new notifications</p>;
  }

  return (
    <ul className="notifications-list">
      {notifications.map(notification => (
        <li
          key={notification.id}
          className={notification.read ? "read" : "unread"}
        >
          <p>{notification.message}</p>
          <time>
            {new Date(notification.createdAt).toLocaleString()}
          </time>
        </li>
      ))}
    </ul>
  );
}

function NotificationsSkeleton() {
  return (
    <ul className="notifications-list">
      {[1, 2, 3, 4, 5].map(i => (
        <li key={i} className="notification skeleton" />
      ))}
    </ul>
  );
}

function getCurrentUserId(): string {
  // Implement authentication logic
  return "user-id";
}
```

### Main Content Area

```tsx
// app/dashboard/overview/page.tsx
import { Suspense } from "react";

async function getRecentActivity() {
  const activities = await db.activity.findMany({
    orderBy: { createdAt: "desc" },
    take: 10,
  });

  return activities;
}

export default async function OverviewPage() {
  return (
    <div className="overview-page">
      <h2>Overview</h2>

      <Suspense fallback={<ActivitySkeleton />}>
        <RecentActivity />
      </Suspense>
    </div>
  );
}

async function RecentActivity() {
  const activities = await getRecentActivity();

  return (
    <section className="recent-activity">
      <h3>Recent Activity</h3>

      <ul className="activity-list">
        {activities.map(activity => (
          <li key={activity.id}>
            <span className="activity-type">{activity.type}</span>
            <span className="activity-description">
              {activity.description}
            </span>
            <time>
              {new Date(activity.createdAt).toLocaleString()}
            </time>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

---

## Example 4: Image Gallery with Infinite Scroll

Photo gallery with progressive loading and infinite scroll pagination.

### Gallery Listing

```tsx
// app/gallery/page.tsx
import { ImageGrid } from "@/components/ImageGrid";
import { LoadMoreButton } from "@/components/LoadMoreButton";
import { getImages } from "@/lib/images";

const PAGE_SIZE = 12;

export default async function GalleryPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page = "1" } = await searchParams;
  const currentPage = parseInt(page);

  const { images, totalPages } = await getImages({
    page: currentPage,
    limit: PAGE_SIZE,
  });

  return (
    <div className="gallery-page">
      <h1>Image Gallery</h1>

      <ImageGrid images={images} />

      {currentPage < totalPages && (
        <LoadMoreButton
          currentPage={currentPage}
          totalPages={totalPages}
        />
      )}
    </div>
  );
}
```

### Client-Side Infinite Scroll Component

```tsx
// components/LoadMoreButton.tsx
"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState, useRef } from "react";

export function LoadMoreButton({
  currentPage,
  totalPages,
}: {
  currentPage: number;
  totalPages: number;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(currentPage);
  const observerTarget = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && page < totalPages && !isLoading) {
          loadMore();
        }
      },
      { threshold: 1.0 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => observer.disconnect();
  }, [page, totalPages, isLoading]);

  function loadMore() {
    setIsLoading(true);
    const nextPage = page + 1;

    router.push(`${pathname}?page=${nextPage}`, {
      scroll: false,
    });

    setPage(nextPage);
    setIsLoading(false);
  }

  return (
    <div ref={observerTarget} className="load-more">
      {isLoading && <p>Loading more images...</p>}
    </div>
  );
}
```

---

## Example 5: Real-time Chat App

Chat application with Server Actions for message sending and polling for updates.

### Chat Room Page

```tsx
// app/chat/[roomId]/page.tsx
import { getMessages } from "@/lib/chat";
import { ChatWindow } from "@/components/ChatWindow";
import { MessageInput } from "@/components/MessageInput";

export default async function ChatRoomPage({
  params,
}: {
  params: Promise<{ roomId: string }>;
}) {
  const { roomId } = await params;
  const messages = await getMessages(roomId);

  return (
    <div className="chat-room">
      <ChatWindow roomId={roomId} initialMessages={messages} />
      <MessageInput roomId={roomId} />
    </div>
  );
}
```

### Send Message Server Action

```tsx
// app/actions/chat.ts
"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";

const MessageSchema = z.object({
  roomId: z.string().uuid(),
  content: z.string().min(1).max(1000),
  userId: z.string().uuid(),
});

export async function sendMessage(prevState: any, formData: FormData) {
  const rawData = {
    roomId: formData.get("roomId"),
    content: formData.get("content"),
    userId: formData.get("userId"),
  };

  const result = MessageSchema.safeParse(rawData);

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors,
    };
  }

  try {
    const message = await db.message.create({
      data: result.data,
    });

    revalidatePath(`/chat/${result.data.roomId}`);

    return {
      success: true,
      message,
    };
  } catch (error) {
    return {
      success: false,
      message: "Failed to send message",
    };
  }
}
```

---

## See Also

- [Next.js Examples](https://github.com/vercel/next.js/tree/canary/examples)
- [App Router Examples](https://nextjs.org/docs/app/building-your-application/routing/colocation)
- [Server Actions Examples](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions)
- [Caching Examples](https://nextjs.org/docs/app/building-your-application/caching)
