# Better Auth Patterns

Common implementation patterns, version requirements, and configuration reference.

## Table of Contents

1. [Protected Route Pattern](#protected-route-pattern)
2. [Session Management Pattern](#session-management-pattern)
3. [Version Requirements](#version-requirements)
4. [Environment Variables](#environment-variables)

---

## Protected Route Pattern

### NestJS Guard

```typescript
@Controller('dashboard')
@UseGuards(AuthGuard)
export class DashboardController {
  @Get()
  getDashboard(@Request() req) {
    return req.user;
  }
}
```

### Next.js Server Component

```typescript
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function Dashboard() {
  const session = await auth();
  if (!session) {
    redirect('/sign-in');
  }
  return <div>Welcome {session.user.name}</div>;
}
```

---

## Session Management Pattern

### Get Session in API Route

```typescript
const session = await auth.api.getSession({
  headers: await headers()
});
```

### Get Session in Server Component

```typescript
const session = await auth();
```

### Get Session in Client Component

```typescript
'use client';
import { useSession } from '@/lib/auth/client';
const { data: session } = useSession();
```

---

## Version Requirements

### Backend Dependencies

```json
{
  "dependencies": {
    "better-auth": "^1.2.0",
    "@auth/drizzle-adapter": "^1.0.0",
    "drizzle-orm": "^0.35.0",
    "pg": "^8.12.0",
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/config": "^3.0.0"
  },
  "devDependencies": {
    "drizzle-kit": "^0.24.0",
    "@types/pg": "^8.11.0"
  }
}
```

### Frontend Dependencies

```json
{
  "dependencies": {
    "better-auth": "^1.2.0",
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }
}
```

### Database

- PostgreSQL 14+ recommended
- For local development: Docker PostgreSQL or Postgres.app

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000

# OAuth Providers
AUTH_GITHUB_CLIENT_ID=your-github-client-id
AUTH_GITHUB_CLIENT_SECRET=your-github-client-secret

AUTH_GOOGLE_CLIENT_ID=your-google-client-id
AUTH_GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email (for magic links and verification)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@example.com

# Session (optional, for Redis)
REDIS_URL=redis://localhost:6379
```

---

## See Also

- [Examples](./examples.md) - Detailed implementation examples
- [Best Practices](./best-practices.md) - Security and operational best practices
- [NestJS Setup](./nestjs-setup.md) - Complete NestJS backend setup
- [Next.js Setup](./nextjs-setup.md) - Complete Next.js frontend setup
