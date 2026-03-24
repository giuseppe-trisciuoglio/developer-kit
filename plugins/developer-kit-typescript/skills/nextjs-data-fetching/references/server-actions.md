# Server Actions Reference

Server Actions for mutations with error handling, form validation, and cache revalidation.

## Basic Mutation

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

## Form with Client-Side Error Handling

```tsx
// app/posts/CreatePostForm.tsx
'use client';

import { createPost } from '../actions/posts';
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Post'}
    </button>
  );
}

export function CreatePostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <SubmitButton />
    </form>
  );
}
```

## Form with useActionState for Error Handling

```tsx
// app/actions/posts.ts
'use server';

'use server';

import { revalidateTag } from 'next/cache';
import { z } from 'zod';

const PostSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string().min(1).max(5000),
});

export type ActionState = {
  errors?: { title?: string[]; content?: string[] };
  message?: string;
};

export async function createPost(prevState: ActionState, formData: FormData) {
  const validated = PostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  });

  if (!validated.success) {
    return {
      errors: validated.error.flatten().fieldErrors,
      message: 'Validation failed',
    };
  }

  const response = await fetch('https://api.example.com/posts', {
    method: 'POST',
    body: JSON.stringify(validated.data),
  });

  if (!response.ok) {
    return { message: 'Failed to create post' };
  }

  revalidateTag('posts');
  return { message: 'Post created' };
}
```

```tsx
// app/posts/NewPostForm.tsx
'use client';

import { useActionState } from 'react';
import { createPost } from '../actions/posts';

export function NewPostForm() {
  const [state, formAction, isPending] = useActionState(createPost, {});

  return (
    <form action={formAction}>
      <input name="title" placeholder="Title" />
      {state.errors?.title && <span>{state.errors.title[0]}</span>}

      <textarea name="content" placeholder="Content" />
      {state.errors?.content && <span>{state.errors.content[0]}</span>}

      {state.message && <span>{state.message}</span>}

      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create Post'}
      </button>
    </form>
  );
}
```

## Delete Action

```tsx
// app/actions/posts.ts
export async function deletePost(postId: string) {
  const response = await fetch(`/api/posts/${postId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete post');
  }

  revalidateTag('posts');
}
```
