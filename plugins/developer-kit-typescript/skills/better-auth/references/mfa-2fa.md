# Better Auth MFA/2FA Guide

## Overview

Better Auth provides comprehensive Multi-Factor Authentication (MFA) support through the `twoFactor` plugin. This includes TOTP-based authentication, backup codes for recovery, and trusted device management.

## Installation

```bash
npm install better-auth
```

The twoFactor plugin is included in the main better-auth package.

## Server Configuration

### Basic Setup

```typescript
import { betterAuth } from "better-auth";
import { twoFactor } from "better-auth/plugins";

export const auth = betterAuth({
  appName: "My App",
  plugins: [
    twoFactor({
      issuer: "My App",  // Displayed in authenticator apps
      otpOptions: {
        async sendOTP({ user, otp }, ctx) {
          // Required: Send OTP to user via email, SMS, etc.
          await sendEmail({
            to: user.email,
            subject: 'Your verification code',
            body: `Your code is: ${otp}`
          });
        }
      }
    })
  ]
});
```

### Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `issuer` | string | No | App name displayed in authenticator apps (default: "Better Auth") |
| `otpOptions.sendOTP` | function | Yes | Async function to send OTP to user |
| `otpOptions.digits` | number | No | Number of OTP digits (default: 6) |
| `otpOptions.period` | number | No | OTP validity period in seconds (default: 30) |

## Client-Side Implementation

### Enable 2FA

```typescript
import { authClient } from "@/lib/auth/client";

// Enable 2FA for current user
const enable2FA = async (password: string) => {
  const { data, error } = await authClient.twoFactor.enable({
    password
  });

  if (data) {
    // Display TOTP URI as QR code
    const qrCodeUrl = data.totpURI;
    // Example: otpauth://totp/MyApp:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=MyApp

    // Show backup codes (single-use recovery codes)
    console.log('Save these backup codes securely:');
    data.backupCodes.forEach((code: string) => {
      console.log(code);
    });
  }
};
```

**Response:**
- `totpURI`: URI for QR code generation
- `backupCodes`: Array of single-use recovery codes

### Verify TOTP

```typescript
const verifyTOTP = async (code: string, trustDevice: boolean = true) => {
  const { data, error } = await authClient.twoFactor.verifyTotp({
    code,
    trustDevice  // Trust device for 30 days
  });

  if (data) {
    // 2FA verified, user is authenticated
    router.push('/dashboard');
  }
};
```

### Verify with OTP (Email/SMS)

```typescript
const verifyOTP = async (code: string) => {
  const { data, error } = await authClient.twoFactor.verifyOtp({
    code,
    trustDevice: true
  });

  if (data) {
    router.push('/dashboard');
  }
};
```

### Use Backup Code

```typescript
const recoverWithBackupCode = async (code: string) => {
  const { data, error } = await authClient.twoFactor.verifyBackupCode({
    code
  });

  if (data) {
    // User can disable 2FA or set up new authenticator
    router.push('/settings/2fa');
  }
};
```

### Get TOTP URI

```typescript
const getTOTPUri = async (password: string) => {
  const { data, error } = await authClient.twoFactor.getTotpUri({
    password
  });

  if (data) {
    // Display QR code from data.totpURI
    displayQRCode(data.totpURI);
  }
};
```

### Disable 2FA

```typescript
const disable2FA = async (password: string) => {
  const { data, error } = await authClient.twoFactor.disable({
    password
  });

  if (data) {
    // 2FA disabled
  }
};
```

## Trusted Devices

### How It Works

- Pass `trustDevice: true` when verifying 2FA
- Device is trusted for **30 days**
- Trust period refreshes on each successful sign-in
- Device-specific (not user-wide)

### Implementation

```typescript
const signInWith2FA = async (code: string) => {
  const { data, error } = await authClient.twoFactor.verifyTotp({
    code,
    trustDevice: true  // Device won't require 2FA for 30 days
  });

  if (data) {
    // User authenticated, device is now trusted
  }
};
```

### Applicable Endpoints

- `verifyTotp` - TOTP code verification
- `verifyOtp` - OTP (email/SMS) verification
- `verifyBackupCode` - Backup code verification

## API Endpoints

### POST /two-factor/enable
Enable 2FA for current user.

**Body:**
```json
{
  "password": "user-password",
  "issuer": "My App"  // Optional
}
```

**Response:**
```json
{
  "totpURI": "otpauth://totp/...",
  "backupCodes": ["CODE1", "CODE2", "CODE3", "CODE4", "CODE5"]
}
```

### POST /two-factor/verify-totp
Verify TOTP code.

**Body:**
```json
{
  "code": "123456",
  "trustDevice": true
}
```

### POST /two-factor/verify-otp
Verify OTP sent via email/SMS.

**Body:**
```json
{
  "code": "123456",
  "trustDevice": true
}
```

### POST /two-factor/verify-backup-code
Verify single-use backup code.

**Body:**
```json
{
  "code": "BACKUP-CODE"
}
```

### POST /two-factor/disable
Disable 2FA for current user.

**Body:**
```json
{
  "password": "user-password"
}
```

### POST /two-factor/get-totp-uri
Get TOTP URI for reconfiguring authenticator.

**Body:**
```json
{
  "password": "user-password"
}
```

## Security Best Practices

1. **Backup Codes**
   - Display immediately after enabling 2FA
   - Store in secure location (password manager)
   - Cannot be retrieved later

2. **OTP Delivery**
   - Use secure channels (HTTPS)
   - Implement rate limiting
   - Set short expiration times

3. **TOTP Configuration**
   - Use 6 digits (standard)
   - 30-second period (standard)
   - Allow ±1 period drift for clock skew

4. **Trusted Devices**
   - Clear trust on password change
   - Allow users to view/revoke trusted devices
   - Consider shorter trust period for sensitive apps

## React Component Example

```tsx
'use client';

import { useState } from 'react';
import { authClient } from '@/lib/auth/client';

export function TwoFactorSetup() {
  const [step, setStep] = useState<'password' | 'qr' | 'backup'>('password');
  const [password, setPassword] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);

  const handleEnable = async () => {
    const { data, error } = await authClient.twoFactor.enable({ password });

    if (data) {
      setQrCode(data.totpURI);
      setBackupCodes(data.backupCodes);
      setStep('qr');
    }
  };

  return (
    <div>
      {step === 'password' && (
        <div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
          />
          <button onClick={handleEnable}>Enable 2FA</button>
        </div>
      )}

      {step === 'qr' && (
        <div>
          <img src={`/api/qr?data=${encodeURIComponent(qrCode)}`} alt="Scan with authenticator" />
          <button onClick={() => setStep('backup')}>I&apos;ve scanned the code</button>
        </div>
      )}

      {step === 'backup' && (
        <div>
          <h3>Save these backup codes securely:</h3>
          <ul>
            {backupCodes.map((code) => (
              <li key={code}>{code}</li>
            ))}
          </ul>
          <p>These codes can be used to recover your account if you lose access to your authenticator.</p>
        </div>
      )}
    </div>
  );
}
```

## Troubleshooting

### "Invalid TOTP code"
- Check device time synchronization
- Ensure authenticator app uses correct time
- Try regenerating TOTP URI

### "Backup code already used"
- Each backup code is single-use
- Use a different backup code
- Disable and re-enable 2FA to generate new codes

### "Device not trusted"
- `trustDevice` must be `true` during verification
- Check browser cookie settings
- Clear cookies and re-authenticate
