# NestJS Best Practices

Comprehensive best practices for NestJS development.

## Core Principles

1. **Always use constructor injection** - Never use property injection
2. **Use DTOs for data transfer** - Define interfaces for request/response
3. **Implement proper error handling** - Use exception filters
4. **Validate all inputs** - Use validation pipes
5. **Keep modules focused** - Single responsibility principle
6. **Use environment variables** - Never hardcode credentials
7. **Write comprehensive tests** - Unit and integration tests
8. **Use transactions for complex operations** - Maintain data consistency
9. **Implement proper logging** - Use interceptors for cross-cutting concerns
10. **Use type safety** - Leverage TypeScript features

## Database Best Practices

- **Connection pooling** - Always use pooling for production workloads
- **Index frequently queried columns** - Improve query performance
- **Use migrations for schema changes** - Never modify schema manually
- **Implement soft deletes** - Preserve data history
- **Use transactions** - Ensure data consistency

## Security Best Practices

- **Never expose stack traces** - In production error responses
- **Validate all inputs** - Prevent injection attacks
- **Use parameterized queries** - Drizzle does this automatically
- **Implement rate limiting** - Prevent abuse
- **Use HTTPS** - Encrypt data in transit
