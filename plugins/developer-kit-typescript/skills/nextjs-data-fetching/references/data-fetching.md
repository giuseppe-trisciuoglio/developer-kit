# Data Fetching Patterns

## Server Component Fetching (Default)

Fetch directly in async Server Components when the data is needed for the first render and no browser-only state is required.

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts');
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

Use this as the baseline approach for content pages, dashboards, and route-level data requirements.

## Parallel Data Fetching

Fetch multiple independent resources in parallel to reduce total waiting time.

```tsx
async function getDashboardData() {
  const [user, posts, analytics] = await Promise.all([
    fetch('/api/user').then((r) => r.json()),
    fetch('/api/posts').then((r) => r.json()),
    fetch('/api/analytics').then((r) => r.json()),
  ]);

  return { user, posts, analytics };
}

export default async function DashboardPage() {
  const { user, posts, analytics } = await getDashboardData();
  // Render dashboard
}
```

Use this pattern whenever requests do not depend on one another.

## Sequential Data Fetching (When Dependencies Exist)

Fetch sequentially only when a later request requires data from an earlier one.

```tsx
async function getUserPosts(userId: string) {
  const user = await fetch(`/api/users/${userId}`).then((r) => r.json());
  const posts = await fetch(`/api/users/${userId}/posts`).then((r) => r.json());

  return { user, posts };
}
```

Document the dependency explicitly so the slower path is intentional.

## Pattern Selection

Use this checklist when choosing the fetch shape:

- Start with a Server Component when the page can render from server data alone.
- Use `Promise.all()` for unrelated requests.
- Keep sequential requests only for real dependencies.
- Split large pages into smaller async components when separate Suspense boundaries improve UX.

## Example: Dashboard with Parallel Requests

**Input:** Build a dashboard showing user profile, stats, and recent activity.

```tsx
// app/dashboard/page.tsx
async function getDashboardData() {
  const [user, stats, activity] = await Promise.all([
    fetch('/api/user').then((r) => r.json()),
    fetch('/api/stats').then((r) => r.json()),
    fetch('/api/activity').then((r) => r.json()),
  ]);
  return { user, stats, activity };
}

export default async function DashboardPage() {
  const { user, stats, activity } = await getDashboardData();
  return (
    <div className="dashboard">
      <UserProfile user={user} />
      <StatsCards stats={stats} />
      <ActivityFeed activity={activity} />
    </div>
  );
}
```

**Output:** All requests execute concurrently, reducing total load time.
