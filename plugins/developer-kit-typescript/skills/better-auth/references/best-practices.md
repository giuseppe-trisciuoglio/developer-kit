# Better Auth Best Practices

Security guidelines, best practices, troubleshooting, and constraints.

## Table of Contents

1. [Best Practices](#best-practices)
2. [Constraints and Warnings](#constraints-and-warnings)
3. [Troubleshooting](#troubleshooting)

---

## Best Practices

1. **Environment Variables**: Always use environment variables for sensitive data (secrets, database URLs, OAuth credentials)

2. **Secret Generation**: Use strong, unique secrets for Better Auth. Generate with `openssl rand -base64 32`

3. **HTTPS Required**: OAuth callbacks require HTTPS in production. Use `ngrok` or similar for local testing

4. **Session Security**: Configure appropriate session expiration times based on your security requirements

5. **Database Indexing**: Add indexes on frequently queried fields (email, userId) for performance

6. **Error Handling**: Implement proper error handling for auth failures without revealing sensitive information

7. **Rate Limiting**: Add rate limiting to auth endpoints to prevent brute force attacks

8. **CSRF Protection**: Better Auth includes CSRF protection. Always use the provided methods for state changes

9. **Type Safety**: Leverage TypeScript types from Better Auth for full type safety across frontend and backend

10. **Testing**: Test auth flows thoroughly including success cases, error cases, and edge conditions

---

## Constraints and Warnings

### Security Notes

- **Never commit secrets**: Add `.env` to `.gitignore` and never commit OAuth secrets or database credentials
- **Validate redirect URLs**: Always validate OAuth redirect URLs to prevent open redirects
- **Hash passwords**: Better Auth handles password hashing automatically. Never implement your own
- **Session storage**: For production, use Redis or another scalable session store
- **HTTPS Only**: Always use HTTPS for authentication in production
- **OAuth Secrets**: Keep OAuth client secrets secure. Rotate them periodically
- **Email Verification**: Always implement email verification for password-based auth

### Known Limitations

- Better Auth requires Node.js 18+ for Next.js App Router support
- Some OAuth providers require specific redirect URL formats
- Passkeys require HTTPS and compatible browsers
- Organization features require additional database tables

---

## Troubleshooting

### 1. "Session not found" errors

**Problem**: Session data is not being persisted or retrieved correctly.

**Solution**:
- Verify database connection is working
- Check session table exists and has data
- Ensure `BETTER_AUTH_SECRET` is set consistently
- Verify cookie domain settings match your application domain

### 2. OAuth callback fails with "Invalid state"

**Problem**: OAuth state mismatch during callback.

**Solution**:
- Clear cookies and try again
- Ensure `BETTER_AUTH_URL` is set correctly in environment
- Check that redirect URI in OAuth app matches exactly
- Verify no reverse proxy is modifying callbacks

### 3. TypeScript type errors with auth()

**Problem**: Type inference not working correctly.

**Solution**:
- Ensure TypeScript 5+ is installed
- Use `npx better-auth typegen` to generate types
- Restart TypeScript server in your IDE
- Check that `better-auth` versions match on frontend and backend

### 4. Migration fails with "table already exists"

**Problem**: Drizzle migration conflicts.

**Solution**:
- Drop existing tables and re-run migration
- Or use `drizzle-kit push` for development
- For production, write manual migration to handle existing tables

### 5. CORS errors from frontend to backend

**Problem**: Frontend cannot communicate with backend auth endpoints.

**Solution**:
- Configure CORS in NestJS backend
- Add frontend origin to allowed origins
- Ensure credentials are included: `credentials: 'include'`

### 6. Social provider returns "redirect_uri_mismatch"

**Problem**: OAuth app configuration mismatch.

**Solution**:
- Update OAuth app with exact callback URL
- Include both http://localhost and production URLs
- For ngrok/local testing, update OAuth app each time URL changes

---

## See Also

- [Examples](./examples.md) - Detailed implementation examples
- [Patterns](./patterns.md) - Common patterns and configuration
- [NestJS Setup](./nestjs-setup.md) - Complete NestJS backend setup
- [Next.js Setup](./nextjs-setup.md) - Complete Next.js frontend setup
- [MFA/2FA](./mfa-2fa.md) - Multi-factor authentication details
- [Passkey](./passkey.md) - Passkey authentication details
