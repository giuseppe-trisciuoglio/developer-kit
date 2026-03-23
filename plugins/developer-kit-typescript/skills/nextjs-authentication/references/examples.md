# Examples

This document contains comprehensive code examples for Next.js authentication patterns.

## Example 1: Complete Protected Dashboard

**Input:** User needs a dashboard accessible only to authenticated users

**Implementation:**

```tsx
// app/dashboard/page.tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";
import { getUserTodos } from "@/app/lib/data";

export default async function DashboardPage() {
  const session = await auth();

  if (!session?.user?.id) {
    redirect("/login");
  }

  const todos = await getUserTodos(session.user.id);

  return (
    <main>
      <h1>Welcome, {session.user.name}</h1>
      <p>Email: {session.user.email}</p>
      <TodoList todos={todos} />
    </main>
  );
}
```

**Output:** Dashboard renders only for authenticated users, with their specific data.

## Example 2: Role-Based Admin Panel

**Input:** Admin panel should be accessible only to users with "admin" role

**Implementation:**

```tsx
// app/admin/page.tsx
import { auth } from "@/auth";
import { unauthorized } from "next/navigation";

export default async function AdminPage() {
  const session = await auth();

  if (session?.user?.role !== "admin") {
    unauthorized();
  }

  return (
    <main>
      <h1>Admin Panel</h1>
      <p>Welcome, administrator {session.user.name}</p>
    </main>
  );
}
```

**Output:** Only admin users see the panel; others get 401 error.

## Example 3: Secure Server Action with Form

**Input:** Form submission should only work for authenticated users

**Implementation:**

```tsx
// app/components/create-todo-form.tsx
"use server";

import { auth } from "@/auth";
import { revalidatePath } from "next/cache";

export async function createTodo(formData: FormData) {
  const session = await auth();

  if (!session?.user?.id) {
    throw new Error("Unauthorized");
  }

  const title = formData.get("title") as string;

  await db.todo.create({
    data: {
      title,
      userId: session.user.id,
    },
  });

  revalidatePath("/dashboard");
}

// Usage in component
export function CreateTodoForm() {
  return (
    <form action={createTodo}>
      <input name="title" placeholder="New todo..." required />
      <button type="submit">Add Todo</button>
    </form>
  );
}
```

**Output:** Todo created only for authenticated user; unauthorized requests throw error.

## Example 4: OAuth Sign-In Button

**Input:** User should be able to sign in with GitHub

**Implementation:**

```tsx
// components/auth/sign-in-button.tsx
"use client";

import { signIn, signOut, useSession } from "next-auth/react";

export function AuthButton() {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return <button disabled>Loading...</button>;
  }

  if (session) {
    return (
      <button onClick={() => signOut()}>
        Sign out {session.user?.name}
      </button>
    );
  }

  return (
    <button onClick={() => signIn("github")}>
      Sign in with GitHub
    </button>
  );
}
```

**Output:** Button shows "Sign in with GitHub" for unauthenticated users, "Sign out {name}" for authenticated users.

## Example 5: Credentials Provider Login

**Input:** Implement email/password login

**Implementation:**

```tsx
// auth.ts
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const user = await db.user.findUnique({
          where: { email: credentials.email },
        });

        if (!user || !user.password) {
          return null;
        }

        const isValid = await bcrypt.compare(
          credentials.password,
          user.password
        );

        return isValid
          ? { id: user.id, email: user.email, name: user.name }
          : null;
      },
    }),
  ],
});
```

**Output:** Users can authenticate with email/password against your database.
