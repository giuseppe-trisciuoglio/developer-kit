# Better Auth Examples

This document contains detailed examples for implementing Better Auth in various scenarios.

## Table of Contents

1. [Complete NestJS Auth Setup](#example-1-complete-nestjs-auth-setup)
2. [Next.js Middleware for Route Protection](#example-2-nextjs-middleware-for-route-protection)
3. [Server Component with Session](#example-3-server-component-with-session)
4. [Adding Two-Factor Authentication](#example-4-adding-two-factor-authentication)
5. [TOTP Verification with Trusted Device](#example-5-totp-verification-with-trusted-device)
6. [Passkey Authentication Setup](#example-6-passkey-authentication-setup)
7. [Passkey Conditional UI (Autofill)](#example-7-passkey-conditional-ui-autofill)
8. [Backup Codes for 2FA Recovery](#example-8-backup-codes-for-2fa-recovery)

---

## Example 1: Complete NestJS Auth Setup

**Input:** Developer needs to set up Better Auth in a new NestJS project with PostgreSQL.

**Process:**

```typescript
// 1. Create auth instance
export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
    schema: { ...schema }
  }),
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }
  }
});

// 2. Create auth controller
@Controller('auth')
export class AuthController {
  @All('*')
  async handleAuth(@Req() req: Request, @Res() res: Response) {
    return auth.handler(req);
  }
}
```

**Output:** Fully functional auth endpoints at `/auth/*` with GitHub OAuth support.

---

## Example 2: Next.js Middleware for Route Protection

**Input:** Protect dashboard routes in Next.js App Router.

**Process:**

```typescript
// middleware.ts
import { auth } from '@/lib/auth';

export default auth((req) => {
  if (!req.auth && req.nextUrl.pathname.startsWith('/dashboard')) {
    const newUrl = new URL('/sign-in', req.nextUrl.origin);
    return Response.redirect(newUrl);
  }
});

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*']
};
```

**Output:** Unauthenticated users are redirected to `/sign-in` when accessing `/dashboard/*`.

---

## Example 3: Server Component with Session

**Input:** Display user data in a Next.js Server Component.

**Process:**

```typescript
// app/dashboard/page.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth();

  if (!session) {
    redirect('/sign-in');
  }

  return (
    <div>
      <h1>Welcome, {session.user.name}</h1>
      <p>Email: {session.user.email}</p>
    </div>
  );
}
```

**Output:** Renders user information only for authenticated users, redirects others to sign-in.

---

## Example 4: Adding Two-Factor Authentication

**Input:** Enable 2FA for enhanced account security.

**Process:**

```typescript
// Enable 2FA plugin
export const auth = betterAuth({
  plugins: [
    twoFactor({
      issuer: 'MyApp',
      otpOptions: {
        digits: 6,
        period: 30
      }
    })
  ]
});

// Client-side enable 2FA
const { data, error } = await authClient.twoFactor.enable({
  password: 'user-password'
});
```

**Output:** Users can enable TOTP-based 2FA and verify with authenticator apps.

---

## Example 5: TOTP Verification with Trusted Device

**Input:** User has enabled 2FA and wants to sign in, marking the device as trusted.

**Process:**

```typescript
// Server-side: Configure 2FA with OTP sending
export const auth = betterAuth({
  plugins: [
    twoFactor({
      issuer: 'MyApp',
      otpOptions: {
        async sendOTP({ user, otp }, ctx) {
          // Send OTP via email, SMS, or other method
          await sendEmail({
            to: user.email,
            subject: 'Your verification code',
            body: `Code: ${otp}`
          });
        }
      }
    })
  ]
});

// Client-side: Verify TOTP and trust device
const verify2FA = async (code: string) => {
  const { data, error } = await authClient.twoFactor.verifyTotp({
    code,
    trustDevice: true  // Device trusted for 30 days
  });

  if (data) {
    // Redirect to dashboard
    router.push('/dashboard');
  }
};
```

**Output:** User is authenticated, device is trusted for 30 days (no 2FA prompt on next sign-ins).

---

## Example 6: Passkey Authentication Setup

**Input:** Enable passkey (WebAuthn) authentication for passwordless login.

**Process:**

```typescript
// Server-side: Configure passkey plugin
import { passkey } from '@better-auth/passkey';

export const auth = betterAuth({
  plugins: [
    passkey({
      rpID: 'example.com',      // Relying Party ID (your domain)
      rpName: 'My App',         // Display name
      advanced: {
        webAuthnChallengeCookie: 'my-app-passkey'
      }
    })
  ]
});

// Client-side: Register passkey
const registerPasskey = async () => {
  const { data, error } = await authClient.passkey.register({
    name: 'My Device'
  });

  if (data) {
    console.log('Passkey registered successfully');
  }
};

// Client-side: Sign in with passkey
const signInWithPasskey = async () => {
  await authClient.signIn.passkey({
    autoFill: true,  // Enable conditional UI
    fetchOptions: {
      onSuccess() {
        router.push('/dashboard');
      }
    }
  });
};
```

**Output:** Users can register and authenticate with passkeys (biometric, PIN, or security key).

---

## Example 7: Passkey Conditional UI (Autofill)

**Input:** Implement passkey autofill in sign-in form for seamless authentication.

**Process:**

```tsx
// Component with conditional UI support
'use client';

import { useEffect } from 'react';
import { authClient } from '@/lib/auth/client';

export default function SignInPage() {
  useEffect(() => {
    // Check for conditional mediation support
    if (!PublicKeyCredential.isConditionalMediationAvailable ||
        !PublicKeyCredential.isConditionalMediationAvailable()) {
      return;
    }

    // Enable passkey autofill
    void authClient.signIn.passkey({ autoFill: true });
  }, []);

  return (
    <form>
      <label htmlFor="email">Email:</label>
      <input
        type="email"
        name="email"
        autoComplete="username webauthn"
      />
      <label htmlFor="password">Password:</label>
      <input
        type="password"
        name="password"
        autoComplete="current-password webauthn"
      />
      <button type="submit">Sign In</button>
    </form>
  );
}
```

**Output:** Browser automatically suggests passkeys when user focuses on input fields.

---

## Example 8: Backup Codes for 2FA Recovery

**Input:** User needs backup codes to recover account if authenticator app is lost.

**Process:**

```typescript
// Enable 2FA - backup codes are generated automatically
const enable2FA = async (password: string) => {
  const { data, error } = await authClient.twoFactor.enable({
    password
  });

  if (data) {
    // IMPORTANT: Display backup codes to user immediately
    console.log('Backup codes (save these securely):');
    data.backupCodes.forEach((code: string) => {
      console.log(code);
    });

    // Show TOTP URI as QR code
    const qrCodeUrl = data.totpURI;
    displayQRCode(qrCodeUrl);
  }
};

// Recover with backup code
const recoverWithBackupCode = async (code: string) => {
  const { data, error } = await authClient.twoFactor.verifyBackupCode({
    code
  });

  if (data) {
    // Allow user to disable 2FA or set up new authenticator
    router.push('/settings/2fa');
  }
};
```

**Output:** User receives single-use backup codes for account recovery.

---

## See Also

- [NestJS Setup](./nestjs-setup.md) - Complete NestJS backend setup
- [Next.js Setup](./nextjs-setup.md) - Complete Next.js frontend setup
- [MFA/2FA](./mfa-2fa.md) - Multi-factor authentication details
- [Passkey](./passkey.md) - Passkey authentication details
- [Plugins](./plugins.md) - Plugin configuration
- [Schema](./schema.md) - Database schema setup
