# Better Auth Social Providers Guide

Better Auth supports 40+ social login providers. This guide covers the most commonly used providers and their setup.

## Supported Providers

- **GitHub**
- **Google**
- **Microsoft** (Azure AD)
- **Facebook**
- **Twitter / X**
- **Apple**
- **Discord**
- **LinkedIn**
- **Spotify**
- **Twitch**
- **GitLab**
- **Bitbucket**
- **Amazon**
- **Yahoo**
- **Yandex**
- And 25+ more

## GitHub OAuth Setup

### 1. Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Your App Name
   - **Homepage URL**: `http://localhost:3000` (dev) or your production URL
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`

### 2. Configure Environment Variables

```bash
# .env
AUTH_GITHUB_CLIENT_ID=your_github_client_id
AUTH_GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 3. Enable in Better Auth

```typescript
// src/auth/auth.instance.ts
import { betterAuth } from 'better-auth';

export const auth = betterAuth({
  socialProviders: {
    github: {
      clientId: process.env.AUTH_GITHUB_CLIENT_ID!,
      clientSecret: process.env.AUTH_GITHUB_CLIENT_SECRET!,
      enabled: true,
    },
  },
});
```

### 4. Frontend Sign In

```tsx
'use client';

import { authClient } from '@/lib/auth/client';

export function GitHubSignIn() {
  const handleGitHubSignIn = async () => {
    await authClient.signIn.social({
      provider: 'github',
      callbackURL: '/dashboard',
    });
  };

  return (
    <button onClick={handleGitHubSignIn}>
      Continue with GitHub
    </button>
  );
}
```

## Google OAuth Setup

### 1. Create Google OAuth Client

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Configure consent screen if prompted
6. Application type: Web application
7. Add authorized redirect URI: `http://localhost:3000/api/auth/callback/google`

### 2. Configure Environment Variables

```bash
# .env
AUTH_GOOGLE_CLIENT_ID=your_google_client_id
AUTH_GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 3. Enable in Better Auth

```typescript
export const auth = betterAuth({
  socialProviders: {
    google: {
      clientId: process.env.AUTH_GOOGLE_CLIENT_ID!,
      clientSecret: process.env.AUTH_GOOGLE_CLIENT_SECRET!,
      enabled: true,
    },
  },
});
```

## Microsoft (Azure AD) Setup

### 1. Create Azure AD App

1. Go to https://portal.azure.com/
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Redirect URI: `http://localhost:3000/api/auth/callback/microsoft`
5. Copy Application (client) ID
6. Generate client secret

### 2. Configure Environment Variables

```bash
# .env
AUTH_MICROSOFT_CLIENT_ID=your_microsoft_client_id
AUTH_MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
AUTH_MICROSOFT_TENANT_ID=common # or your tenant ID
```

### 3. Enable in Better Auth

```typescript
export const auth = betterAuth({
  socialProviders: {
    microsoft: {
      clientId: process.env.AUTH_MICROSOFT_CLIENT_ID!,
      clientSecret: process.env.AUTH_MICROSOFT_CLIENT_SECRET!,
      tenantId: process.env.AUTH_MICROSOFT_TENANT_ID || 'common',
      enabled: true,
    },
  },
});
```

## Facebook OAuth Setup

### 1. Create Facebook App

1. Go to https://developers.facebook.com/apps/
2. Create app (type: Consumer)
3. Add "Facebook Login" product
4. Set redirect URI: `http://localhost:3000/api/auth/callback/facebook`

### 2. Configure Environment Variables

```bash
# .env
AUTH_FACEBOOK_CLIENT_ID=your_facebook_app_id
AUTH_FACEBOOK_CLIENT_SECRET=your_facebook_app_secret
```

## Apple Sign In Setup

### 1. Create Apple Sign In Service ID

1. Go to https://developer.apple.com/account/resources/
2. Create "Services ID"
3. Configure Sign In with Apple
4. Set redirect URL: `https://yourdomain.com/api/auth/callback/apple`

### 2. Configure Environment Variables

```bash
# .env
AUTH_APPLE_CLIENT_ID=your_apple_client_id
AUTH_APPLE_CLIENT_SECRET=your_apple_client_secret # Generated from JWT
AUTH_APPLE_KEY_ID=your_apple_key_id
AUTH_APPLE_TEAM_ID=your_apple_team_id
```

### 3. Generate Apple Client Secret

Apple requires a JWT signed with your private key:

```typescript
import jwt from 'jsonwebtoken';
import fs from 'fs';

function generateAppleClientSecret() {
  const privateKey = fs.readFileSync('./AuthKey.p8');

  const token = jwt.sign({}, privateKey, {
    algorithm: 'ES256',
    keyid: process.env.AUTH_APPLE_KEY_ID,
    issuer: process.env.AUTH_APPLE_TEAM_ID,
    audience: 'https://appleid.apple.com',
    subject: process.env.AUTH_APPLE_CLIENT_ID,
    expiresIn: '180d',
  });

  return token;
}
```

## Discord OAuth Setup

### 1. Create Discord Application

1. Go to https://discord.com/developers/applications
2. Create application
3. OAuth2 > Redirects: `http://localhost:3000/api/auth/callback/discord`

### 2. Configure Environment Variables

```bash
# .env
AUTH_DISCORD_CLIENT_ID=your_discord_client_id
AUTH_DISCORD_CLIENT_SECRET=your_discord_client_secret
```

## LinkedIn OAuth Setup

### 1. Create LinkedIn App

1. Go to https://www.linkedin.com/developers/
2. Create app
3. Auth redirect URLs: `http://localhost:3000/api/auth/callback/linkedin`

### 2. Configure Environment Variables

```bash
# .env
AUTH_LINKEDIN_CLIENT_ID=your_linkedin_client_id
AUTH_LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

## Production Configuration

For production, update your callback URLs:

```typescript
export const auth = betterAuth({
  socialProviders: {
    github: {
      clientId: process.env.AUTH_GITHUB_CLIENT_ID!,
      clientSecret: process.env.AUTH_GITHUB_CLIENT_SECRET!,
      enabled: true,
      redirectURI: `${process.env.BETTER_AUTH_URL}/api/auth/callback/github`,
    },
    google: {
      clientId: process.env.AUTH_GOOGLE_CLIENT_ID!,
      clientSecret: process.env.AUTH_GOOGLE_CLIENT_SECRET!,
      enabled: true,
      redirectURI: `${process.env.BETTER_AUTH_URL}/api/auth/callback/google`,
    },
  },
});
```

## Multiple Providers Example

```typescript
export const auth = betterAuth({
  socialProviders: {
    github: {
      clientId: process.env.AUTH_GITHUB_CLIENT_ID!,
      clientSecret: process.env.AUTH_GITHUB_CLIENT_SECRET!,
      enabled: true,
    },
    google: {
      clientId: process.env.AUTH_GOOGLE_CLIENT_ID!,
      clientSecret: process.env.AUTH_GOOGLE_CLIENT_SECRET!,
      enabled: true,
    },
    microsoft: {
      clientId: process.env.AUTH_MICROSOFT_CLIENT_ID!,
      clientSecret: process.env.AUTH_MICROSOFT_CLIENT_SECRET!,
      enabled: true,
    },
    discord: {
      clientId: process.env.AUTH_DISCORD_CLIENT_ID!,
      clientSecret: process.env.AUTH_DISCORD_CLIENT_SECRET!,
      enabled: true,
    },
  },
});
```

## Custom Provider Configuration

Some providers require additional configuration:

```typescript
export const auth = betterAuth({
  socialProviders: {
    google: {
      clientId: process.env.AUTH_GOOGLE_CLIENT_ID!,
      clientSecret: process.env.AUTH_GOOGLE_CLIENT_SECRET!,
      enabled: true,
      // Additional scopes
      scopes: ['openid', 'profile', 'email'],
      // Access type
      accessType: 'offline',
      // Prompt
      prompt: 'consent',
    },
  },
});
```

## Provider-Specific Scopes

Different providers support different scopes:

```typescript
// Google scopes
google: {
  scopes: ['openid', 'profile', 'email'],
}

// GitHub scopes
github: {
  scopes: ['read:user', 'user:email'],
}

// Microsoft scopes
microsoft: {
  scopes: ['openid', 'profile', 'email'],
}

// Discord scopes
discord: {
  scopes: ['identify', 'email'],
}
```

## Testing OAuth Locally

### Using ngrok for HTTPS

Some providers (like Apple) require HTTPS for OAuth callbacks:

```bash
# Install ngrok
npm install -g ngrok

# Start ngrok
ngrok http 3000

# Use the HTTPS URL for OAuth configuration
# e.g., https://abc123.ngrok.io
```

Update your environment:

```bash
# .env.local
NEXT_PUBLIC_APP_URL=https://abc123.ngrok.io
BETTER_AUTH_URL=https://abc123.ngrok.io
```

## Troubleshooting

### "redirect_uri_mismatch" Error

- Ensure redirect URI matches exactly (including trailing slashes)
- For ngrok, update OAuth app each time URL changes
- Check both allowed redirect URIs and authorized JavaScript origins

### "Invalid client" Error

- Verify client ID and secret are correct
- Check for extra spaces in environment variables
- Ensure OAuth app is not in test mode (for some providers)

### Scope Issues

- Request only the scopes you need
- Some scopes require additional verification with the provider
- Check provider documentation for required scopes

## Environment Variables Template

```bash
# GitHub
AUTH_GITHUB_CLIENT_ID=
AUTH_GITHUB_CLIENT_SECRET=

# Google
AUTH_GOOGLE_CLIENT_ID=
AUTH_GOOGLE_CLIENT_SECRET=

# Microsoft
AUTH_MICROSOFT_CLIENT_ID=
AUTH_MICROSOFT_CLIENT_SECRET=
AUTH_MICROSOFT_TENANT_ID=common

# Facebook
AUTH_FACEBOOK_CLIENT_ID=
AUTH_FACEBOOK_CLIENT_SECRET=

# Discord
AUTH_DISCORD_CLIENT_ID=
AUTH_DISCORD_CLIENT_SECRET=

# LinkedIn
AUTH_LINKEDIN_CLIENT_ID=
AUTH_LINKEDIN_CLIENT_SECRET=

# Apple
AUTH_APPLE_CLIENT_ID=
AUTH_APPLE_CLIENT_SECRET=
AUTH_APPLE_KEY_ID=
AUTH_APPLE_TEAM_ID=
```
