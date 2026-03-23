# Framework-Specific Documentation Patterns

## NestJS Documentation

### Guard Documentation

```typescript
/**
 * Guard for protecting routes with JWT authentication
 *
 * @guard
 * @remarks
 * Validates JWT tokens from Authorization header.
 * Attaches user data to request object.
 *
 * @usageNotes
 * Apply to controllers or methods:
 * ```typescript
 * @Controller('users')
 * @UseGuards(JwtAuthGuard)
 * export class UserController {
 *   @Get('profile')
 *   getProfile(@Request() req) {
 *     return req.user;
 *   }
 * }
 * ```
 *
 * @security
 * - Validates token signature
 * - Checks token expiration
 * - Prevents token replay attacks
 *
 * @performance
 * - Caches validation results for 5 minutes
 * - Uses Redis for distributed caching
 */
@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private jwtService: JwtService) {}

  /**
   * Validates JWT token and extracts user data
   * @param context - Execution context
   * @returns True if authentication successful
   */
  async canActivate(context: ExecutionContext): Promise<boolean> {
    // Implementation
  }
}
```

### Decorator Documentation

```typescript
/**
 * Decorator for rate limiting endpoints
 * @decorator
 * @param options - Rate limiting options
 *
 * @usageNotes
 * Apply to controller methods:
 * ```typescript
 * @Controller('users')
 * export class UserController {
 *   @Get()
 *   @RateLimit({ points: 100, duration: 60 })
 *   async findAll() {
 *     // Implementation
 *   }
 * }
 * ```
 *
 * @see {@link RateLimitInterceptor}
 * @see {@link RateLimitOptions}
 */
export const RateLimit = (options: RateLimitOptions) =>
  applyDecorators(
    UseInterceptors(RateLimitInterceptor),
    SetMetadata('rateLimit', options)
  );
```

## React Component Documentation

```typescript
/**
 * User profile card component
 * @component
 * @param {UserProfileProps} props - Component props
 * @param {User} props.user - User data to display
 * @param {boolean} props.editable - Whether profile is editable
 * @param {function} props.onEdit - Edit button click handler
 *
 * @example
 * ```tsx
 * export default function Dashboard() {
 *   const { user } = useAuth();
 *
 *   return (
 *     <div>
 *       <h1>User Profile</h1>
 *       <UserProfile
 *         user={user}
 *         editable={true}
 *         onEdit={() => console.log('Edit clicked')}
 *       />
 *     </div>
 *   );
 * }
 * ```
 *
 * @performance
 * - Memoized with React.memo
 * - Lazy loads avatar images
 * - Optimistic UI updates
 *
 * @accessibility
 * - Full keyboard navigation
 * - ARIA labels for screen readers
 * - High contrast support
 */
export const UserProfile = React.memo<UserProfileProps>(
  ({ user, editable, onEdit }) => {
    // Implementation
  }
);
```

### Custom Hook Documentation

```typescript
/**
 * Custom hook for managing form state with validation
 * @hook
 * @param schema - Yup validation schema
 * @param initialValues - Initial form values
 * @returns Form state and handlers
 *
 * @example
 * ```tsx
 * function LoginForm() {
 *   const { values, errors, handleSubmit, handleChange } = useForm({
 *     schema: loginSchema,
 *     initialValues: { email: '', password: '' }
 *   });
 *
 *   return (
 *     <form onSubmit={handleSubmit}>
 *       <input
 *         name="email"
 *         value={values.email}
 *         onChange={handleChange}
 *       />
 *       {errors.email && <span>{errors.email}</span>}
 *     </form>
 *   );
 * }
 * ```
 *
 * @performance
 * - Memoized validation to prevent unnecessary re-renders
 * - Debounced validation for better UX
 * - Optimistic updates for better perceived performance
 */
export function useForm<T>({
  schema,
  initialValues
}: UseFormOptions<T>): UseFormReturn<T> {
  // Implementation
}
```

## Express Middleware Documentation

```typescript
/**
 * Rate limiting middleware with Redis backend
 * @middleware
 * @param options - Rate limiting options
 * @param options.windowMs - Time window in milliseconds
 * @param options.max - Maximum requests per window
 * @param options.keyGenerator - Function to generate rate limit key
 *
 * @example
 * ```typescript
 * app.use('/api', rateLimit({
 *   windowMs: 15 * 60 * 1000, // 15 minutes
 *   max: 100, // limit each IP to 100 requests per windowMs
 *   keyGenerator: (req) => req.ip
 * }));
 * ```
 *
 * @errorResponses
 * - `429` - Too many requests
 * - `500` - Redis connection error
 *
 * @security
 * - Prevents DoS attacks
 * - Implements sliding window algorithm
 * - Distributed across multiple servers
 */
export function rateLimit(options: RateLimitOptions): RequestHandler {
  // Implementation
}
```

## Angular Documentation

### Service Documentation

```typescript
/**
 * Service for managing user sessions
 * @injectable
 * @providedIn root
 *
 * @remarks
 * Handles user authentication state across the application.
 * Automatically refreshes tokens before expiry.
 *
 * @example
 * ```typescript
 * export class AppComponent {
 *   constructor(private authService: AuthService) {}
 *
 *   async login() {
 *     await this.authService.login(credentials);
 *   }
 * }
 * ```
 *
 * @security
 * - Stores tokens in secure storage
 * - Implements token refresh logic
 * - Handles logout on all tabs (broadcast channel)
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Implementation
}
```
