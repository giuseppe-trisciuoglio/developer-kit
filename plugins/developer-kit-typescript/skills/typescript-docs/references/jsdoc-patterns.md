# JSDoc Documentation Patterns

## Interface Documentation

```typescript
/**
 * Represents a user in the authentication system
 * @interface User
 *
 * @property id - Unique identifier (UUID v4)
 * @property email - User's email address (validated format)
 * @property roles - Array of user roles for RBAC
 * @property metadata - Additional user data (preferences, settings)
 *
 * @example
 * ```typescript
 * const user: User = {
 *   id: "550e8400-e29b-41d4-a716-446655440000",
 *   email: "user@example.com",
 *   roles: ["user", "admin"],
 *   metadata: {
 *     theme: "dark",
 *     language: "en"
 *   }
 * };
 * ```
 *
 * @see {@link UserRole} for role definitions
 * @see {@link UserService} for user operations
 */
export interface User {
  id: string;
  email: string;
  roles: UserRole[];
  metadata: Record<string, unknown>;
}
```

## Function Documentation

```typescript
/**
 * Authenticates a user with email and password
 * @param email - User's email address
 * @param password - User's password (min 8 characters)
 * @param options - Additional authentication options
 * @returns Promise resolving to authentication result
 *
 * @throws {InvalidCredentialsError} If email/password don't match
 * @throws {AccountLockedError} If account is locked after failed attempts
 * @throws {RateLimitExceededError} If too many attempts made
 *
 * @remarks
 * Implements secure authentication with:
 * - Bcrypt password hashing (cost factor 12)
 * - Rate limiting (5 attempts per 15 minutes)
 * - Account lockout after 3 consecutive failures
 * - JWT token generation with 15-minute expiry
 *
 * @example
 * ```typescript
 * try {
 *   const result = await authenticateUser("user@example.com", "password123");
 *   console.log(`Authenticated: ${result.user.email}`);
 * } catch (error) {
 *   if (error instanceof InvalidCredentialsError) {
 *     // Handle invalid credentials
 *   }
 * }
 * ```
 *
 * @security
 * - Passwords are never logged or stored in plain text
 * - Uses timing-attack safe comparison
 * - Implements CSRF protection for web requests
 *
 * @performance
 * - Average response time: ~200ms
 * - Uses connection pooling for database queries
 * - Caches user permissions for 5 minutes
 */
export async function authenticateUser(
  email: string,
  password: string,
  options?: AuthOptions
): Promise<AuthResult> {
  // Implementation
}
```

## Class Documentation

```typescript
/**
 * Service for managing user authentication and authorization
 *
 * @remarks
 * This service handles:
 * - User authentication with JWT tokens
 * - Password reset flows
 * - Multi-factor authentication
 * - Session management
 * - Role-based access control
 *
 * @example
 * ```typescript
 * const authService = new AuthService(config);
 *
 * // Authenticate user
 * const token = await authService.login(email, password);
 *
 * // Verify token
 * const user = await authService.verifyToken(token);
 * ```
 *
 * @security
 * - All passwords hashed with bcrypt
 * - JWT tokens signed with RS256
 * - Rate limiting on authentication endpoints
 * - Secure session management
 *
 * @performance
 * - Uses Redis for session storage
 * - Implements connection pooling
 * - Caches user permissions
 */
export class AuthService {
  /**
   * Creates an instance of AuthService
   * @param config - Service configuration
   * @param config.jwtSecret - Secret key for JWT signing
   * @param config.tokenExpiry - Token expiry duration
   * @param config.refreshTokenExpiry - Refresh token expiry
   */
  constructor(private readonly config: AuthConfig) {}

  /**
   * Authenticates a user and returns access tokens
   * @param credentials - User credentials
   * @returns Authentication result with tokens
   */
  async login(credentials: LoginCredentials): Promise<AuthResult> {
    // Implementation
  }
}
```

## Advanced TypeScript Documentation

### Generic Constraints

```typescript
/**
 * Repository base class for TypeScript entities
 * @template T - Entity type (must extend BaseEntity)
 * @template K - Primary key type (string | number)
 *
 * @remarks
 * Provides CRUD operations with type safety.
 * All methods return Result types for explicit error handling.
 *
 * @example
 * ```typescript
 * class UserRepository extends BaseRepository<User, string> {
 *   async findByEmail(email: string): Promise<Result<User, RepositoryError>> {
 *     // Implementation
 *   }
 * }
 * ```
 */
export abstract class BaseRepository<T extends BaseEntity, K extends string | number> {
  /**
   * Finds an entity by its primary key
   * @param id - Primary key value
   * @returns Result containing entity or error
   */
  abstract findById(id: K): Promise<Result<T, RepositoryError>>;
}
```

### Union Types and Discriminated Unions

```typescript
/**
 * Represents different types of API responses
 * @variant success - Successful response with data
 * @variant error - Error response with error details
 * @variant pending - Pending response for async operations
 *
 * @example
 * ```typescript
 * type ApiResponse<T> = SuccessResponse<T> | ErrorResponse | PendingResponse;
 *
 * function handleResponse<T>(response: ApiResponse<T>) {
 *   switch (response.status) {
 *     case 'success':
 *       console.log(response.data);
 *       break;
 *     case 'error':
 *       console.error(response.error);
 *       break;
 *     case 'pending':
 *       console.log('Loading...');
 *       break;
 *   }
 * }
 * ```
 */
export type ApiResponse<T> =
  | { status: 'success'; data: T }
  | { status: 'error'; error: ApiError }
  | { status: 'pending'; progress?: number };
```
