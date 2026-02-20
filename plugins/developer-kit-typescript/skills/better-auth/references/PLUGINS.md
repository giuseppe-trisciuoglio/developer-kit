# Better Auth Plugins Guide

Better Auth supports various plugins for extending authentication functionality. This guide covers the most commonly used plugins.

## Available Plugins

- Two-Factor Authentication (2FA)
- Organization
- SSO (Single Sign-On)
- Magic Link
- Passkey
- Email Verification
- Phone Verification
- Anonymous User

## Two-Factor Authentication (2FA)

### Installation

```bash
npm install @otp-plugin/react
```

### Backend Configuration

```typescript
// src/auth/auth.instance.ts
import { betterAuth } from 'better-auth';
import { twoFactor } from 'better-auth/plugins';

export const auth = betterAuth({
  // ... other config
  plugins: [
    twoFactor({
      // 2FA configuration
      totp: {
        enabled: true,
        issuer: 'YourApp',
      },
      sms: {
        enabled: false, // Enable if using SMS
      },
    }),
  ],
});
```

### Database Schema Update

```typescript
// Add to schema.ts
export const totp = pgTable('totp', {
  id: text('id').notNull().primaryKey(),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  secret: text('secret').notNull(),
  createdAt: timestamp('createdAt').defaultNow(),
});
```

### Frontend Usage

```tsx
'use client';

import { authClient } from '@/lib/auth/client';

export function TwoFactorSetup() {
  const enable2FA = async () => {
    const { data, error } = await authClient.twoFactor.enable();
    // Show QR code to user from data.secret
  };

  const verify2FA = async (code: string) => {
    const { data, error } = await authClient.twoFactor.verify({
      code,
    });
  };

  return (
    <div>
      <button onClick={enable2FA}>Enable 2FA</button>
    </div>
  );
}
```

## Organization Plugin

### Backend Configuration

```typescript
import { betterAuth } from 'better-auth';
import { organization } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    organization({
      // Organization configuration
      avatar: {
        enabled: true,
      },
      currency: 'USD',
    }),
  ],
});
```

### Database Schema

```typescript
// Add to schema.ts
export const organizations = pgTable('organizations', {
  id: text('id').notNull().primaryKey(),
  name: text('name').notNull(),
  slug: text('slug').notNull().unique(),
  logo: text('logo'),
  createdAt: timestamp('createdAt').defaultNow(),
  members: text('members').array(),
});

export const member = pgTable('member', {
  id: text('id').notNull().primaryKey(),
  organizationId: text('organizationId')
    .notNull()
    .references(() => organizations.id, { onDelete: 'cascade' }),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  role: text('role').notNull(), // owner, admin, member
  createdAt: timestamp('createdAt').defaultNow(),
});
```

### Frontend Usage

```tsx
'use client';

import { authClient } from '@/lib/auth/client';

export function OrganizationManager() {
  const createOrg = async (name: string) => {
    const { data, error } = await authClient.organization.create({
      name,
      slug: name.toLowerCase().replace(/\s+/g, '-'),
    });
  };

  const inviteMember = async (email: string) => {
    const { data, error } = await authClient.organization.inviteMember({
      email,
      role: 'member',
    });
  };

  return (
    <div>
      <button onClick={() => createOrg('My Org')}>
        Create Organization
      </button>
    </div>
  );
}
```

## SSO (Single Sign-On)

### Backend Configuration

```typescript
import { betterAuth } from 'better-auth';
import { sso } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    sso({
      // SSO configuration
    }),
  ],
});
```

### SAML Setup

```typescript
// For enterprise SSO with SAML
export const auth = betterAuth({
  plugins: [
    sso({
      saml: {
        enabled: true,
      },
    }),
  ],
});
```

## Magic Link Plugin

### Backend Configuration

```typescript
import { betterAuth } from 'better-auth';
import { magicLink } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        // Send email with magic link
        await sendEmail({
          to: email,
          subject: 'Sign in to Your App',
          html: `<a href="${url}">Sign in</a>`,
        });
      },
      // Magic link expiration (default 24h)
      expiresIn: 1000 * 60 * 15, // 15 minutes
    }),
  ],
});
```

### Frontend Usage

```tsx
'use client';

import { authClient } from '@/lib/auth/client';

export function MagicLinkSignIn() {
  const sendMagicLink = async (email: string) => {
    const { data, error } = await authClient.magicLink.send({
      email,
    });

    if (!error) {
      alert('Check your email for a sign-in link');
    }
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const email = e.target.email.value;
      sendMagicLink(email);
    }}>
      <input name="email" type="email" required />
      <button type="submit">Send Magic Link</button>
    </form>
  );
}
```

## Passkey Plugin

### Backend Configuration

```typescript
import { betterAuth } from 'better-auth';
import { passkey } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    passkey({
      // Passkey configuration
    }),
  ],
});
```

### Frontend Usage

```tsx
'use client';

import { authClient } from '@/lib/auth/client';

export function PasskeyAuth() {
  const registerPasskey = async () => {
    const { data, error } = await authClient.passkey.register();
  };

  const signInWithPasskey = async () => {
    const { data, error } = await authClient.passkey.signIn();
  };

  return (
    <div>
      <button onClick={signInWithPasskey}>
        Sign in with Passkey
      </button>
    </div>
  );
}
```

## Email Verification Plugin

### Backend Configuration

```typescript
import { betterAuth } from 'better-auth';
import { emailVerification } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    emailVerification({
      sendVerificationEmail: async ({ user, url }) => {
        await sendEmail({
          to: user.email,
          subject: 'Verify your email',
          html: `<a href="${url}">Verify email</a>`,
        });
      },
      // Send verification email on sign up
      sendOnSignUp: true,
    }),
  ],
});
```

### Frontend Usage

```tsx
'use client';

import { authClient } from '@/lib/auth/client';

export function EmailVerification() {
  const resendVerification = async () => {
    const { data, error } = await authClient.emailVerification.send({
      email: 'user@example.com',
    });
  };

  const verifyEmail = async (code: string) => {
    const { data, error } = await authClient.emailVerification.verify({
      code,
    });
  };

  return (
    <div>
      <button onClick={resendVerification}>
        Resend verification email
      </button>
    </div>
  );
}
```

## Plugin Combination Example

```typescript
import { betterAuth } from 'better-auth';
import { twoFactor, organization, magicLink, passkey } from 'better-auth/plugins';

export const auth = betterAuth({
  database: drizzleAdapter(schema, {
    provider: 'postgresql',
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  socialProviders: {
    github: {
      clientId: process.env.AUTH_GITHUB_CLIENT_ID!,
      clientSecret: process.env.AUTH_GITHUB_CLIENT_SECRET!,
      enabled: true,
    },
  },
  plugins: [
    twoFactor({
      totp: { enabled: true },
    }),
    organization({
      avatar: { enabled: true },
    }),
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        // Custom email sending logic
      },
    }),
    passkey(),
  ],
});
```

## Plugin-Specific Migrations

After adding plugins, remember to generate new migrations:

```bash
npx drizzle-kit generate
npx drizzle-kit migrate
```

## Environment Variables for Plugins

```bash
# .env
# 2FA
TWO_FACTOR_SECRET=your-totp-secret

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@example.com

# SSO (SAML)
SAML_CERT_PATH=/path/to/cert.pem
SAML_KEY_PATH=/path/to/key.pem
```
