# Auth.js 5 Setup Guide

Complete setup guide for Auth.js 5 with Next.js App Router.

## Installation

```bash
npm install next-auth@beta
# or specific version
npm install @auth/nextjs@latest
```

## Project Structure

```
my-app/
├── auth.ts                    # Main auth configuration
├── middleware.ts              # Route protection
├── types/
│   └── next-auth.d.ts         # TypeScript type extensions
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/ # API route handler
│   │           └── route.ts
│   ├── login/
│   │   └── page.tsx           # Custom login page
│   ├── dashboard/
│   │   └── page.tsx           # Protected page
│   └── layout.tsx             # Root layout with SessionProvider
├── components/
│   └── auth/
│       ├── sign-in-button.tsx
│       └── user-avatar.tsx
└── lib/
    ├── auth.ts                # Auth utilities
    └── dal.ts                 # Data Access Layer
```

## Complete Configuration

### 1. TypeScript Types

```typescript
// types/next-auth.d.ts
import { DefaultSession, DefaultUser } from "next-auth";
import { JWT } from "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      role: "user" | "admin" | "moderator";
      permissions: string[];
    } & DefaultSession["user"];
  }

  interface User extends DefaultUser {
    role?: "user" | "admin" | "moderator";
    permissions?: string[];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string;
    role?: "user" | "admin" | "moderator";
    permissions?: string[];
  }
}
```

### 2. Auth Configuration

```typescript
// auth.ts
import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma";

// Providers
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut,
} = NextAuth({
  // Database adapter (optional - for database sessions)
  adapter: PrismaAdapter(prisma),

  // Session configuration
  session: {
    strategy: "jwt", // or "database"
    maxAge: 30 * 24 * 60 * 60, // 30 days
    updateAge: 24 * 60 * 60, // 24 hours
  },

  // Cookie configuration
  cookies: {
    sessionToken: {
      name: `__Secure-next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        secure: process.env.NODE_ENV === "production",
      },
    },
  },

  // Authentication providers
  providers: [
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
      allowDangerousEmailAccountLinking: true,
    }),
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      allowDangerousEmailAccountLinking: true,
    }),
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

        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
        });

        if (!user || !user.password) {
          return null;
        }

        const isPasswordValid = await bcrypt.compare(
          credentials.password as string,
          user.password
        );

        if (!isPasswordValid) {
          return null;
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image,
          role: user.role,
        };
      },
    }),
  ],

  // Callbacks for customizing behavior
  callbacks: {
    async signIn({ user, account, profile }) {
      // Allow OAuth sign-ins without restrictions
      if (account?.provider !== "credentials") {
        return true;
      }

      // Additional validation for credentials provider
      return true;
    },

    async redirect({ url, baseUrl }) {
      // Allows relative callback URLs
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      // Allows callback URLs on the same origin
      else if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    },

    async jwt({ token, user, account, trigger, session }) {
      // Persist user data to token
      if (user) {
        token.id = user.id;
        token.role = user.role;
        token.permissions = user.permissions;
      }

      // Handle session updates
      if (trigger === "update" && session) {
        token.name = session.name;
        token.image = session.image;
      }

      return token;
    },

    async session({ session, token }) {
      // Send token data to session
      if (token) {
        session.user.id = token.id as string;
        session.user.role = token.role as "user" | "admin" | "moderator";
        session.user.permissions = token.permissions as string[];
      }
      return session;
    },
  },

  // Custom pages
  pages: {
    signIn: "/login",
    signOut: "/logout",
    error: "/error", // Error code passed in query string as ?error=
    verifyRequest: "/verify-email", // (used for check email message)
    newUser: "/welcome", // New users will be directed here on first sign in
  },

  // Events for logging or side effects
  events: {
    async signIn(message) {
      console.log("User signed in:", message.user.email);
    },
    async signOut(message) {
      console.log("User signed out:", message.token.email);
    },
    async createUser(message) {
      console.log("New user created:", message.user.email);
    },
  },

  // Debug mode (only in development)
  debug: process.env.NODE_ENV === "development",
});
```

### 3. API Route Handler

```typescript
// app/api/auth/[...nextauth]/route.ts
export { GET, POST } from "@/auth";
```

### 4. Middleware Configuration

```typescript
// middleware.ts
import { auth } from "@/auth";
import { NextResponse } from "next/server";

// Define route groups
const publicRoutes = ["/", "/login", "/register", "/forgot-password"];
const authRoutes = ["/login", "/register"];
const protectedRoutes = ["/dashboard", "/profile", "/settings"];
const adminRoutes = ["/admin"];
const apiAuthPrefix = "/api/auth";

export default auth((req) => {
  const { nextUrl } = req;
  const isLoggedIn = !!req.auth;
  const pathname = nextUrl.pathname;

  // Allow all API auth routes
  if (pathname.startsWith(apiAuthPrefix)) {
    return NextResponse.next();
  }

  // Check if route is public
  const isPublicRoute = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  // Check if route requires authentication
  const isProtectedRoute = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  // Check if route requires admin role
  const isAdminRoute = adminRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  // Check if it's an auth route (login/register)
  const isAuthRoute = authRoutes.includes(pathname);

  // Redirect logged-in users away from auth pages
  if (isLoggedIn && isAuthRoute) {
    return NextResponse.redirect(new URL("/dashboard", nextUrl));
  }

  // Redirect unauthenticated users to login
  if (!isLoggedIn && isProtectedRoute) {
    const callbackUrl = encodeURIComponent(pathname);
    return NextResponse.redirect(
      new URL(`/login?callbackUrl=${callbackUrl}`, nextUrl)
    );
  }

  // Check admin access
  if (isAdminRoute && req.auth?.user?.role !== "admin") {
    return NextResponse.redirect(new URL("/unauthorized", nextUrl));
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip static files and images
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
```

### 5. Data Access Layer

```typescript
// lib/dal.ts
import { auth } from "@/auth";
import { cache } from "react";
import { redirect } from "next/navigation";

/**
 * Verify current session - cached for same render
 */
export const verifySession = cache(async () => {
  const session = await auth();

  if (!session?.user) {
    return null;
  }

  return session;
});

/**
 * Require authentication - redirects to login if not authenticated
 */
export async function requireAuth() {
  const session = await verifySession();

  if (!session) {
    redirect("/login");
  }

  return session;
}

/**
 * Require specific role
 */
export async function requireRole(role: string) {
  const session = await verifySession();

  if (!session) {
    redirect("/login");
  }

  if (session.user.role !== role) {
    redirect("/unauthorized");
  }

  return session;
}

/**
 * Get current user with data
 */
export async function getCurrentUser() {
  const session = await requireAuth();

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: {
      id: true,
      email: true,
      name: true,
      image: true,
      role: true,
      createdAt: true,
    },
  });

  if (!user) {
    throw new Error("User not found");
  }

  return user;
}
```

### 6. Auth Utilities

```typescript
// lib/auth.ts
import bcrypt from "bcryptjs";

/**
 * Hash a password
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}

/**
 * Verify a password
 */
export async function verifyPassword(
  password: string,
  hashedPassword: string
): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword);
}

/**
 * Generate a secure random token
 */
export function generateToken(length: number = 32): string {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}
```

## Environment Variables

```bash
# .env.local

# NextAuth.js
AUTH_SECRET="your-secret-key-here"  # Generate with: openssl rand -base64 32
AUTH_URL="http://localhost:3000"

# OAuth Providers
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"

GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Database (if using database sessions)
DATABASE_URL="postgresql://user:password@localhost:5432/mydb"

# Email (if using email provider)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
FROM_EMAIL="noreply@yourapp.com"
```

## Client Component Setup

For client components that need session access:

```typescript
// components/providers/session-provider.tsx
"use client";

import { SessionProvider as NextAuthSessionProvider } from "next-auth/react";
import { ReactNode } from "react";

export function SessionProvider({ children }: { children: ReactNode }) {
  return <NextAuthSessionProvider>{children}</NextAuthSessionProvider>;
}
```

```typescript
// app/layout.tsx
import { SessionProvider } from "@/components/providers/session-provider";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
```
