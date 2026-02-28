# NestJS Code Review Checklist

## Module Structure
- [ ] Each feature has its own module with clear boundaries
- [ ] Modules export only the necessary public API
- [ ] No circular module dependencies
- [ ] Shared utilities are in a dedicated SharedModule
- [ ] Global modules (`@Global()`) are used sparingly
- [ ] Lazy-loaded modules for performance-critical applications

## Controllers
- [ ] Controllers are thin — no business logic
- [ ] Proper HTTP methods and status codes
- [ ] All parameters validated with pipes (ParseUUIDPipe, ParseIntPipe, etc.)
- [ ] Request bodies validated with DTOs and ValidationPipe
- [ ] OpenAPI decorators present (@ApiTags, @ApiOperation, @ApiResponse)
- [ ] Proper error responses documented
- [ ] No direct repository or database access
- [ ] Route versioning applied consistently

## Services
- [ ] Single responsibility — each service owns one domain concern
- [ ] Constructor injection for all dependencies
- [ ] No direct instantiation (`new`) of injectable services
- [ ] Proper error handling with domain-specific exceptions
- [ ] Transaction management for atomic operations
- [ ] Logging with proper context (Logger with class name)
- [ ] No hardcoded values — use ConfigService

## DTOs and Validation
- [ ] Request DTOs with class-validator decorators
- [ ] Response DTOs that exclude sensitive fields
- [ ] Proper type definitions (no `any`)
- [ ] Validation error messages are user-friendly
- [ ] Nested objects properly validated with @ValidateNested and @Type
- [ ] Array items validated with @ArrayMinSize, @ArrayMaxSize
- [ ] Optional fields marked with @IsOptional

## Dependency Injection
- [ ] All services use constructor injection
- [ ] Proper provider scoping (Singleton, Request, Transient)
- [ ] Custom providers use proper tokens (string or Symbol)
- [ ] No circular dependencies (or resolved with forwardRef)
- [ ] Interface-based injection with @Inject token for abstraction

## Guards and Authorization
- [ ] All protected routes have authentication guards
- [ ] Role-based authorization uses guards + decorators, not inline checks
- [ ] Guards are composable and reusable
- [ ] Custom decorators for extracting user context (@CurrentUser)
- [ ] Public routes explicitly marked with @Public or similar

## Interceptors and Middleware
- [ ] Cross-cutting concerns handled by interceptors (logging, caching, transformation)
- [ ] Response format is consistent across all endpoints
- [ ] Middleware used for request-level concerns (CORS, compression, logging)
- [ ] No business logic in interceptors or middleware

## Error Handling
- [ ] Global exception filter registered
- [ ] Domain-specific exception classes extend HttpException
- [ ] Error responses don't expose internal details (stack traces, SQL errors)
- [ ] Proper HTTP status codes for different error types
- [ ] Unhandled promise rejections caught
- [ ] Meaningful error messages for debugging

## Database Integration
- [ ] Repository pattern separates data access from business logic
- [ ] Queries use parameterized inputs (no string concatenation)
- [ ] Database transactions for multi-step operations
- [ ] Migrations exist for schema changes
- [ ] Connection pooling configured for production
- [ ] No N+1 query problems (use eager loading or batch queries)

## Security
- [ ] Input validation on all endpoints
- [ ] Authentication guard on protected routes
- [ ] Rate limiting configured (ThrottlerModule)
- [ ] CORS properly configured
- [ ] Security headers (helmet) enabled
- [ ] Sensitive data not logged
- [ ] Environment variables for secrets

## Testing
- [ ] Unit tests for services with mocked dependencies
- [ ] Integration tests for controllers with e2e setup
- [ ] Guard and pipe tests
- [ ] Test coverage meets project thresholds
- [ ] Tests are independent and isolated
- [ ] Mocking strategy is consistent

## Performance
- [ ] Database queries optimized (indexes, selected fields)
- [ ] Caching applied for frequently accessed data
- [ ] Async operations don't block the event loop
- [ ] Pagination implemented for list endpoints
- [ ] Large payloads use streaming when appropriate
- [ ] Connection pools properly sized

## Documentation
- [ ] OpenAPI/Swagger decorators on all endpoints
- [ ] API examples in decorators
- [ ] README updated for new features
- [ ] Inline comments for complex business logic only
