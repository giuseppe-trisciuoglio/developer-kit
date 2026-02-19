# Server Actions

## Basic Server Action

```tsx
// app/actions.ts
"use server";

export async function createUser(formData: FormData) {
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;

  await db.user.create({
    data: { name, email },
  });

  revalidatePath("/users");
}
```

```tsx
// app/users/page.tsx
import { createUser } from "./actions";

export default function UserForm() {
  return (
    <form action={createUser}>
      <input name="name" placeholder="Name" />
      <input name="email" type="email" placeholder="Email" />
      <button type="submit">Create</button>
    </form>
  );
}
```

## Server Action with Zod Validation

```tsx
// app/actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";

const createUserSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
});

export async function createUser(formData: FormData) {
  const validated = createUserSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
  });

  if (!validated.success) {
    return {
      error: validated.error.flatten().fieldErrors,
    };
  }

  try {
    await db.user.create({
      data: validated.data,
    });

    revalidatePath("/users");
    return { success: true };
  } catch (error) {
    return { error: "Failed to create user" };
  }
}
```

## useActionState Hook (React 19)

```tsx
"use client";

import { useActionState } from "react";
import { createUser } from "./actions";

const initialState = {
  error: null as Record<string, string[]> | null,
  success: false,
};

export default function UserForm() {
  const [state, formAction, pending] = useActionState(createUser, initialState);

  return (
    <form action={formAction}>
      <input name="name" placeholder="Name" />
      {state.error?.name && <span>{state.error.name[0]}</span>}

      <input name="email" type="email" placeholder="Email" />
      {state.error?.email && <span>{state.error.email[0]}</span>}

      <button type="submit" disabled={pending}>
        {pending ? "Creating..." : "Create"}
      </button>

      {state.success && <p>User created!</p>}
    </form>
  );
}
```

## useFormStatus Hook

```tsx
"use client";

import { useFormStatus } from "react-dom";

function SubmitButton() {
  const { pending, data, method, action } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? "Submitting..." : "Submit"}
    </button>
  );
}

export default function Form() {
  return (
    <form action={handleSubmit}>
      <input name="title" />
      <SubmitButton />
    </form>
  );
}
```

## Server Action with bind (arguments extra)

```tsx
// app/actions.ts
"use server";

export async function updateUser(userId: string, formData: FormData) {
  // userId is passed via bind
  const name = formData.get("name");

  await db.user.update({
    where: { id: userId },
    data: { name },
  });

  revalidatePath("/users");
}
```

```tsx
// app/users/[id]/page.tsx
import { updateUser } from "./actions";

export default async function EditUser({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const updateUserWithId = updateUser.bind(null, id);

  return (
    <form action={updateUserWithId}>
      <input name="name" placeholder="New name" />
      <button type="submit">Update</button>
    </form>
  );
}
```

## Optimistic Updates

```tsx
"use client";

import { useOptimistic } from "react";
import { sendMessage } from "./actions";

interface Message {
  id: string;
  text: string;
  sending?: boolean;
}

export default function Chat({ messages }: { messages: Message[] }) {
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage: string) => [
      ...state,
      { id: Math.random().toString(), text: newMessage, sending: true },
    ]
  );

  async function handleSubmit(formData: FormData) {
    const text = formData.get("message") as string;
    addOptimisticMessage(text);
    await sendMessage(text);
  }

  return (
    <div>
      {optimisticMessages.map((msg) => (
        <div key={msg.id} style={{ opacity: msg.sending ? 0.5 : 1 }}>
          {msg.text}
        </div>
      ))}
      <form action={handleSubmit}>
        <input name="message" />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

## Error Handling

```tsx
"use server";

import { redirect } from "next/navigation";

export async function deleteUser(userId: string) {
  try {
    await db.user.delete({ where: { id: userId } });
    revalidatePath("/users");
    redirect("/users");
  } catch (error) {
    throw new Error("Failed to delete user");
  }
}
```

## Cookies and Headers in Server Actions

```tsx
"use server";

import { cookies, headers } from "next/headers";

export async function trackEvent(event: string) {
  const cookieStore = await cookies();
  const headersList = await headers();

  const sessionId = cookieStore.get("session-id")?.value;
  const userAgent = headersList.get("user-agent");

  await analytics.track({
    event,
    sessionId,
    userAgent,
  });
}
```
