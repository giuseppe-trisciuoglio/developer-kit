# Server Actions for Mutations

Use Server Actions when a form or user interaction writes data and the UI needs the server to own the mutation logic.

## Basic Mutation Pattern

Perform the mutation on the server, validate success, and then invalidate the related cache entries.

```tsx
// app/actions/posts.ts
'use server';

import { revalidateTag } from 'next/cache';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  const response = await fetch('https://api.example.com/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content }),
  });

  if (!response.ok) {
    throw new Error('Failed to create post');
  }

  revalidateTag('posts');
  return response.json();
}
```

Keep the invalidation tag aligned with the corresponding read path.

## Form Integration

Bind the Server Action directly to the form when the browser can submit without custom client orchestration.

```tsx
// app/posts/CreatePostForm.tsx
'use client';

import { createPost } from '../actions/posts';

export function CreatePostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

## When to Prefer Server Actions

Use Server Actions when you need:

- Server-owned validation and mutation logic
- Cache invalidation immediately after writes
- Simpler forms without a custom API round trip in the client

Prefer client-side mutations only when the interaction truly needs optimistic state, local undo flows, or non-form event orchestration.

## Example: Contact Form Submission

**Input:** Create a contact form that submits data and refreshes the cache.

```tsx
// app/actions/contact.ts
'use server';

import { revalidateTag } from 'next/cache';

export async function submitContact(formData: FormData) {
  const data = {
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message'),
  };

  await fetch('https://api.example.com/contact', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  revalidateTag('messages');
}
```

```tsx
// app/contact/page.tsx
import { submitContact } from '../actions/contact';

export default function ContactPage() {
  return (
    <form action={submitContact}>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <textarea name="message" placeholder="Message" required />
      <button type="submit">Send</button>
    </form>
  );
}
```

**Output:** The form submits on the server and invalidates the related cache tag on success.
