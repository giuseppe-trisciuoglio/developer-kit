# OAuth Provider Configurations

Configuration examples for popular OAuth providers with Auth.js 5.

## GitHub

### Setup

1. Go to GitHub Settings → Developer Settings → OAuth Apps → New OAuth App
2. Set Homepage URL: `http://localhost:3000` (development)
3. Set Authorization callback URL: `http://localhost:3000/api/auth/callback/github`

### Configuration

```typescript
// auth.ts
import GitHub from "next-auth/providers/github";

providers: [
  GitHub({
    clientId: process.env.GITHUB_ID!,
    clientSecret: process.env.GITHUB_SECRET!,
    // Allow linking accounts with same email
    allowDangerousEmailAccountLinking: true,
  }),
]
```

### Environment Variables

```bash
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"
```

### Custom Profile Data

```typescript
GitHub({
  clientId: process.env.GITHUB_ID!,
  clientSecret: process.env.GITHUB_SECRET!,
  profile(profile) {
    return {
      id: profile.id.toString(),
      name: profile.name || profile.login,
      email: profile.email,
      image: profile.avatar_url,
      // Custom fields
      username: profile.login,
      githubUrl: profile.html_url,
    };
  },
})
```

## Google

### Setup

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URI: `http://localhost:3000/api/auth/callback/google`

### Configuration

```typescript
// auth.ts
import Google from "next-auth/providers/google";

providers: [
  Google({
    clientId: process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    allowDangerousEmailAccountLinking: true,
    // Request additional scopes
    authorization: {
      params: {
        prompt: "consent",
        access_type: "offline",
        response_type: "code",
        scope: [
          "openid",
          "https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/calendar.readonly",
        ].join(" "),
      },
    },
  }),
]
```

### Environment Variables

```bash
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

### Access Google APIs

```typescript
// In callbacks
async jwt({ token, account }) {
  if (account) {
    token.accessToken = account.access_token;
    token.refreshToken = account.refresh_token;
  }

  // Refresh token if expired
  if (token.expiresAt && Date.now() > (token.expiresAt as number) * 1000) {
    const response = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: process.env.GOOGLE_CLIENT_ID!,
        client_secret: process.env.GOOGLE_CLIENT_SECRET!,
        grant_type: "refresh_token",
        refresh_token: token.refreshToken as string,
      }),
    });

    const tokens = await response.json();
    token.accessToken = tokens.access_token;
    token.expiresAt = Math.floor(Date.now() / 1000 + tokens.expires_in);
  }

  return token;
},
```

## Discord

### Configuration

```typescript
import Discord from "next-auth/providers/discord";

providers: [
  Discord({
    clientId: process.env.DISCORD_CLIENT_ID!,
    clientSecret: process.env.DISCORD_CLIENT_SECRET!,
    authorization: {
      params: {
        scope: "identify email guilds",
      },
    },
    profile(profile) {
      return {
        id: profile.id,
        name: profile.global_name || profile.username,
        email: profile.email,
        image: profile.avatar
          ? `https://cdn.discordapp.com/avatars/${profile.id}/${profile.avatar}.png`
          : null,
        discordId: profile.id,
        discriminator: profile.discriminator,
      };
    },
  }),
]
```

## Auth0

### Configuration

```typescript
import Auth0 from "next-auth/providers/auth0";

providers: [
  Auth0({
    clientId: process.env.AUTH0_CLIENT_ID!,
    clientSecret: process.env.AUTH0_CLIENT_SECRET!,
    issuer: process.env.AUTH0_ISSUER!,
    authorization: {
      params: {
        audience: process.env.AUTH0_AUDIENCE,
      },
    },
  }),
]
```

### Environment Variables

```bash
AUTH0_CLIENT_ID="your-auth0-client-id"
AUTH0_CLIENT_SECRET="your-auth0-client-secret"
AUTH0_ISSUER="https://your-domain.auth0.com"
AUTH0_AUDIENCE="https://your-api-identifier"
```

## Microsoft Entra ID (Azure AD)

### Configuration

```typescript
import MicrosoftEntraID from "next-auth/providers/microsoft-entra-id";

providers: [
  MicrosoftEntraID({
    clientId: process.env.AZURE_AD_CLIENT_ID!,
    clientSecret: process.env.AZURE_AD_CLIENT_SECRET!,
    tenantId: process.env.AZURE_AD_TENANT_ID!,
    authorization: {
      params: {
        scope: "openid profile email User.Read",
      },
    },
  }),
]
```

### Environment Variables

```bash
AZURE_AD_CLIENT_ID="your-azure-client-id"
AZURE_AD_CLIENT_SECRET="your-azure-client-secret"
AZURE_AD_TENANT_ID="your-azure-tenant-id"
```

## Apple

### Configuration

```typescript
import Apple from "next-auth/providers/apple";

providers: [
  Apple({
    clientId: process.env.APPLE_ID!,
    clientSecret: {
      appleId: process.env.APPLE_ID!,
      teamId: process.env.APPLE_TEAM_ID!,
      privateKey: process.env.APPLE_PRIVATE_KEY!,
      keyId: process.env.APPLE_KEY_ID!,
    },
    checks: ["pkce", "state"],
    profile(profile) {
      return {
        id: profile.sub,
        name: profile.name
          ? `${profile.name.firstName} ${profile.name.lastName}`
          : null,
        email: profile.email,
        image: null,
      };
    },
  }),
]
```

### Environment Variables

```bash
APPLE_ID="your-service-id"
APPLE_TEAM_ID="your-team-id"
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----"
APPLE_KEY_ID="your-key-id"
```

## LinkedIn

### Configuration

```typescript
import LinkedIn from "next-auth/providers/linkedin";

providers: [
  LinkedIn({
    clientId: process.env.LINKEDIN_CLIENT_ID!,
    clientSecret: process.env.LINKEDIN_CLIENT_SECRET!,
    authorization: {
      params: {
        scope: "openid profile email",
      },
    },
    profile(profile) {
      return {
        id: profile.sub,
        name: profile.name,
        email: profile.email,
        image: profile.picture,
      };
    },
  }),
]
```

## Twitter (X)

### Configuration

```typescript
import Twitter from "next-auth/providers/twitter";

providers: [
  Twitter({
    clientId: process.env.TWITTER_CLIENT_ID!,
    clientSecret: process.env.TWITTER_CLIENT_SECRET!,
    version: "2.0", // OAuth 2.0
    profile(profile) {
      return {
        id: profile.data.id,
        name: profile.data.name,
        email: profile.data.email,
        image: profile.data.profile_image_url?.replace("_normal", ""),
        username: profile.data.username,
      };
    },
  }),
]
```

## Multiple Providers with Account Linking

```typescript
// auth.ts
import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";

import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import Discord from "next-auth/providers/discord";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
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
    Discord({
      clientId: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
      allowDangerousEmailAccountLinking: true,
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile, email, credentials }) {
      // Allow all OAuth sign-ins
      if (account?.provider !== "credentials") {
        return true;
      }

      // Additional validation for credentials
      return true;
    },
  },
});
```

## Provider-Specific UI Components

### Social Login Buttons

```tsx
// components/auth/social-login.tsx
"use client";

import { signIn } from "next-auth/react";
import { Github, Chrome } from "lucide-react";

export function SocialLogin() {
  return (
    <div className="grid gap-2">
      <button
        onClick={() => signIn("github", { callbackUrl: "/dashboard" })}
        className="flex items-center justify-center gap-2 rounded-lg border p-2 hover:bg-gray-50"
      >
        <Github className="h-5 w-5" />
        Continue with GitHub
      </button>
      <button
        onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
        className="flex items-center justify-center gap-2 rounded-lg border p-2 hover:bg-gray-50"
      >
        <Chrome className="h-5 w-5" />
        Continue with Google
      </button>
    </div>
  );
}
```

### Login Page with OAuth

```tsx
// app/login/page.tsx
import { SocialLogin } from "@/components/auth/social-login";
import { CredentialsForm } from "@/components/auth/credentials-form";

export default function LoginPage() {
  return (
    <div className="mx-auto max-w-sm space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold">Sign In</h1>
        <p className="text-gray-500">Choose your sign-in method</p>
      </div>

      <SocialLogin />

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <CredentialsForm />
    </div>
  );
}
```
