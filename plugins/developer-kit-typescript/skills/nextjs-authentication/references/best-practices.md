# Best Practices

Comprehensive best practices for Next.js authentication with Auth.js 5.

## Best Practices

1. **Use Server Components by default** - Access session directly without client-side JavaScript
2. **Minimize Client Components** - Only use `useSession()` for reactive session updates
3. **Cache session checks** - Use React's `cache()` for repeated lookups in the same render
4. **Middleware for optimistic checks** - Redirect quickly, but always re-verify in Server Actions
5. **Treat Server Actions like API endpoints** - Always authenticate before mutations
6. **Never hardcode secrets** - Use environment variables for all credentials
7. **Implement proper error handling** - Return appropriate HTTP status codes
8. **Use TypeScript type extensions** - Extend NextAuth types for custom fields
9. **Separate auth logic** - Create a DAL (Data Access Layer) for consistent checks
10. **Test authentication flows** - Mock `auth()` function in unit tests

## Constraints and Warnings

### Critical Limitations

- **Middleware runs on Edge runtime** - Cannot use Node.js APIs like database drivers
- **Server Components cannot set cookies** - Use Server Actions for cookie operations
- **Session callback timing** - Only called on session creation/access, not every request

### Common Mistakes

```tsx
// ❌ WRONG: Setting cookies in Server Component
export default async function Page() {
  cookies().set("key", "value"); // Won't work
}

// ✅ CORRECT: Use Server Action
async function setCookieAction() {
  "use server";
  cookies().set("key", "value");
}
```

```typescript
// ❌ WRONG: Database queries in Middleware
export default auth(async (req) => {
  const user = await db.user.findUnique(); // Won't work in Edge
});

// ✅ CORRECT: Use only Edge-compatible APIs
export default auth(async (req) => {
  const session = req.auth; // This works
});
```

### Security Considerations

- Always verify authentication in Server Actions - middleware alone is not enough
- Use `unauthorized()` for unauthenticated access, `redirect()` for other cases
- Store sensitive tokens in `httpOnly` cookies
- Validate all user input before processing
- Use HTTPS in production
- Set appropriate cookie `sameSite` attributes
