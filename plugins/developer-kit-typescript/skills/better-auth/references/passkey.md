# Better Auth Passkey (WebAuthn) Guide

## Overview

Better Auth supports passkey authentication through the `@better-auth/passkey` plugin. Passkeys provide passwordless authentication using biometrics (fingerprint, face recognition), device PIN, or physical security keys.

## Installation

```bash
npm install @better-auth/passkey
```

## Server Configuration

### Basic Setup

```typescript
import { betterAuth } from "better-auth";
import { passkey } from "@better-auth/passkey";

export const auth = betterAuth({
  plugins: [
    passkey({
      rpID: 'example.com',      // Your domain (Relying Party ID)
      rpName: 'My App',         // Display name in passkey prompts
    })
  ]
});
```

### Advanced Configuration

```typescript
import { betterAuth } from "better-auth";
import { passkey } from "@better-auth/passkey";

export const auth = betterAuth({
  plugins: [
    passkey({
      rpID: 'example.com',
      rpName: 'My App',
      advanced: {
        // Custom cookie name for WebAuthn challenge
        webAuthnChallengeCookie: 'my-app-passkey'
      }
    })
  ]
});
```

### Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `rpID` | string | Yes | Relying Party ID (your domain) |
| `rpName` | string | Yes | Display name shown in passkey prompts |
| `advanced.webAuthnChallengeCookie` | string | No | Custom cookie name for challenge |

## Client Configuration

### Setup Auth Client

```typescript
import { createAuthClient } from 'better-auth/client';
import { passkeyClient } from '@better-auth/passkey/client';

export const authClient = createAuthClient({
  plugins: [passkeyClient()],
});
```

## Passkey Registration

### Register New Passkey

```typescript
const registerPasskey = async () => {
  const { data, error } = await authClient.passkey.register({
    name: 'My MacBook Pro'  // Descriptive name for this passkey
  });

  if (data) {
    console.log('Passkey registered successfully');
  } else {
    console.error('Registration failed:', error);
  }
};
```

### User Experience

1. Browser prompts user to verify (Touch ID, Face ID, PIN, etc.)
2. Passkey is created and stored on the device
3. Public key is sent to server for storage
4. User can now sign in with this passkey

## Passkey Authentication

### Sign In with Passkey

```typescript
const signInWithPasskey = async () => {
  await authClient.signIn.passkey({
    fetchOptions: {
      onSuccess() {
        window.location.href = '/dashboard';
      },
      onError(context) {
        console.error('Authentication failed:', context.error.message);
      }
    }
  });
};
```

### Sign In with Conditional UI (Autofill)

Conditional UI allows the browser to automatically suggest passkeys when users interact with input fields.

```tsx
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
    void authClient.signIn.passkey({
      autoFill: true
    });
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

### Key Requirements for Conditional UI

1. **Input field attributes**: Add `autoComplete="... webauthn"` to inputs
2. **Component mount**: Call `signIn.passkey({ autoFill: true })` on mount
3. **Browser support**: Check `PublicKeyCredential.isConditionalMediationAvailable()`

## Managing Passkeys

### List User Passkeys

```typescript
const listPasskeys = async () => {
  const { data, error } = await authClient.passkey.listUserPasskeys();

  if (data) {
    data.passkeys.forEach((passkey) => {
      console.log(`ID: ${passkey.id}, Name: ${passkey.name}`);
    });
  }
};
```

### Delete Passkey

```typescript
const deletePasskey = async (passkeyId: string) => {
  const { data, error } = await authClient.passkey.delete({
    id: passkeyId
  });

  if (data) {
    console.log('Passkey deleted');
  }
};
```

### Update Passkey Name

```typescript
const updatePasskeyName = async (passkeyId: string, newName: string) => {
  const { data, error } = await authClient.passkey.update({
    id: passkeyId,
    name: newName
  });

  if (data) {
    console.log('Passkey name updated');
  }
};
```

## React Component Examples

### Passkey Registration Button

```tsx
'use client';

import { useState } from 'react';
import { authClient } from '@/lib/auth/client';

export function RegisterPasskeyButton() {
  const [isRegistering, setIsRegistering] = useState(false);

  const handleRegister = async () => {
    setIsRegistering(true);

    const { data, error } = await authClient.passkey.register({
      name: `${navigator.platform} - ${new Date().toLocaleDateString()}`
    });

    setIsRegistering(false);

    if (data) {
      alert('Passkey registered successfully!');
    } else {
      alert(`Registration failed: ${error?.message}`);
    }
  };

  return (
    <button
      onClick={handleRegister}
      disabled={isRegistering}
    >
      {isRegistering ? 'Registering...' : 'Register Passkey'}
    </button>
  );
}
```

### Passkey Sign In Button

```tsx
'use client';

import { useState } from 'react';
import { authClient } from '@/lib/auth/client';
import { useRouter } from 'next/navigation';

export function PasskeySignInButton() {
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const router = useRouter();

  const handleSignIn = async () => {
    setIsAuthenticating(true);

    await authClient.signIn.passkey({
      fetchOptions: {
        onSuccess() {
          router.push('/dashboard');
        },
        onError(context) {
          alert(`Authentication failed: ${context.error.message}`);
          setIsAuthenticating(false);
        }
      }
    });
  };

  return (
    <button
      onClick={handleSignIn}
      disabled={isAuthenticating}
      className="passkey-button"
    >
      {isAuthenticating ? 'Authenticating...' : 'Sign in with Passkey'}
    </button>
  );
}
```

### Passkey Management Panel

```tsx
'use client';

import { useEffect, useState } from 'react';
import { authClient } from '@/lib/auth/client';

interface Passkey {
  id: string;
  name: string;
  createdAt: Date;
}

export function PasskeyManagement() {
  const [passkeys, setPasskeys] = useState<Passkey[]>([]);

  useEffect(() => {
    loadPasskeys();
  }, []);

  const loadPasskeys = async () => {
    const { data } = await authClient.passkey.listUserPasskeys();
    if (data) {
      setPasskeys(data.passkeys);
    }
  };

  const handleDelete = async (id: string) => {
    const confirmed = confirm('Delete this passkey?');
    if (!confirmed) return;

    const { data } = await authClient.passkey.delete({ id });
    if (data) {
      setPasskeys(passkeys.filter((p) => p.id !== id));
    }
  };

  return (
    <div>
      <h2>Your Passkeys</h2>
      <ul>
        {passkeys.map((passkey) => (
          <li key={passkey.id}>
            {passkey.name}
            <button onClick={() => handleDelete(passkey.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## API Endpoints

### POST /passkey/register
Register a new passkey for the current user.

**Body:**
```json
{
  "name": "My Device"
}
```

### POST /sign-in/passkey
Authenticate using a registered passkey.

**Body:**
```json
{
  "autoFill": false
}
```

### GET /passkey/list
List all passkeys registered for the current user.

### POST /passkey/delete
Delete a specific passkey.

**Body:**
```json
{
  "id": "passkey-id"
}
```

### POST /passkey/update
Update the name of a passkey.

**Body:**
```json
{
  "id": "passkey-id",
  "name": "New Name"
}
```

## Security Considerations

### HTTPS Requirement
- Passkeys **require HTTPS** in production
- Use `ngrok` or similar for local HTTPS testing

### Relying Party ID
- Must match the actual domain (no wildcards)
- For localhost testing, use `localhost`
- For production, use your actual domain

### Cross-Device Authentication
- Passkeys synced via cloud (Apple ID, Google account) work across devices
- Platform authenticators (Touch ID, Face ID) are device-specific
- Security keys (YubiKey) work on any device with USB/NFC

### Backup Authentication
- Always provide alternative authentication (password, email)
- Some users may lose access to their passkey device

## Browser Support

| Browser | Passkey Support | Conditional UI |
|---------|----------------|----------------|
| Chrome 108+ | Yes | Yes |
| Safari 16+ | Yes | Yes |
| Firefox 122+ | Yes | Limited |
| Edge 108+ | Yes | Yes |

## Platform Support

### iOS/macOS
- Touch ID / Face ID
- iCloud Keychain sync
- Security keys (NFC, Lightning, USB-C)

### Android
- Fingerprint / Face unlock
- Google Password Manager sync
- Security keys (NFC, USB)

### Windows
- Windows Hello (PIN, fingerprint, face)
- Security keys (USB, NFC)

## Troubleshooting

### "NotAllowedError"
- User cancelled the operation
- No authenticator available
- Browser security settings blocking WebAuthn

### "SecurityError"
- `rpID` doesn't match current domain
- Not using HTTPS in production
- Invalid origin

### Conditional UI not working
- Check browser support with `isConditionalMediationAvailable()`
- Ensure `autoComplete="webauthn"` is on input fields
- Verify user has registered passkeys

### Passkey not appearing
- Check if passkey is synced to current device
- Verify same user account (Apple ID, Google account)
- Try manual sign-in button instead of conditional UI

## Best Practices

1. **Hybrid Approach**: Support both passkeys and passwords
2. **Clear Labels**: Use descriptive passkey names (device + date)
3. **Conditional UI**: Enable autofill for better UX
4. **Fallback**: Always provide password fallback
5. **Security**: Enforce HTTPS in production
6. **Testing**: Test on multiple devices and browsers
