---
globs: "src/**/*.ts"
---
# Rule: NestJS Security

## Context
Enforce security best practices for NestJS applications: JWT authentication, guard-based authorization, input validation, rate limiting, and output sanitization.

## Guidelines

### JWT Authentication
- Use `@nestjs/jwt` with `@nestjs/passport` — **never** hardcode secrets
- Load secrets from `ConfigService` via `JwtModule.registerAsync()`
- Keep access tokens short-lived (15 minutes) and use refresh tokens for session continuity
- Include only minimal, non-sensitive data in JWT payload (`sub`, `email`, `roles`)
- **Never** include passwords, SSNs, or sensitive data in tokens
- Validate that the user still exists and is active on every request

```typescript
// ✅ Secure JWT configuration
JwtModule.registerAsync({
  imports: [ConfigModule],
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    secret: config.get<string>('JWT_SECRET'),
    signOptions: {
      expiresIn: '15m',
      issuer: config.get<string>('JWT_ISSUER'),
    },
  }),
});

// ✅ Validate user on every request
async validate(payload: JwtPayload): Promise<User> {
  const user = await this.usersService.findById(payload.sub);
  if (!user || !user.isActive) {
    throw new UnauthorizedException('User not found or inactive');
  }
  return user;
}
```

### Guards for Authentication & Authorization
- Use guards instead of manual auth checks in every handler
- Register `JwtAuthGuard` and `RolesGuard` globally via `APP_GUARD`
- Use `@Public()` decorator to opt-out specific routes from authentication
- Use `@Roles()` decorator for role-based access control

```typescript
// ✅ Declarative access control
@Controller('admin')
@Roles(Role.Admin)
export class AdminController {
  @Get('users')
  getUsers(): Promise<User[]> { ... }

  @Delete('users/:id')
  deleteUser(@Param('id') id: string): Promise<void> { ... }

  @Public()
  @Get('health')
  health(): { status: string } {
    return { status: 'ok' };
  }
}
```

### Input Validation
- **Always** validate incoming data with `class-validator` decorators on DTOs
- Enable global `ValidationPipe` with `whitelist: true` and `forbidNonWhitelisted: true`
- Validate route parameters with param DTOs or built-in pipes (`ParseUUIDPipe`)
- Use `@Transform()` for input sanitization (trim, lowercase emails)

```typescript
// ✅ Well-validated DTO
export class CreateUserDto {
  @IsString()
  @IsNotEmpty()
  @MinLength(2)
  @MaxLength(100)
  @Transform(({ value }) => value?.trim())
  name: string;

  @IsEmail()
  @Transform(({ value }) => value?.toLowerCase().trim())
  email: string;

  @IsString()
  @MinLength(8)
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
    message: 'Password must contain uppercase, lowercase, and number',
  })
  password: string;
}
```

### Rate Limiting
- Use `@nestjs/throttler` to limit request rates — apply globally via `APP_GUARD`
- Use stricter limits for auth endpoints (login, forgot-password)
- Use `@SkipThrottle()` for health checks and internal endpoints
- Override per-endpoint with `@Throttle()` for fine-grained control

```typescript
// ✅ Global throttler with multiple windows
ThrottlerModule.forRoot([
  { name: 'short', ttl: 1000, limit: 3 },
  { name: 'medium', ttl: 10000, limit: 20 },
  { name: 'long', ttl: 60000, limit: 100 },
]);

// ✅ Strict limits for sensitive endpoints
@Post('login')
@Throttle({ short: { limit: 5, ttl: 60000 } })
async login(@Body() dto: LoginDto): Promise<TokenResponse> { ... }

@Post('forgot-password')
@Throttle({ short: { limit: 3, ttl: 3600000 } })
async forgotPassword(@Body() dto: ForgotPasswordDto): Promise<void> { ... }
```

### Output Sanitization (XSS Prevention)
- Sanitize user-generated HTML content before storage using `sanitize-html`
- Use `@Transform()` in DTOs to strip or whitelist HTML tags
- Set proper `Content-Type: application/json` headers
- Use `helmet` middleware for CSP headers
- **Never** reflect raw user input in error messages

```typescript
// ✅ Sanitize on input
export class CreatePostDto {
  @IsString()
  @Transform(({ value }) => sanitizeHtml(value, { allowedTags: [] }))
  title: string;

  @IsString()
  @Transform(({ value }) =>
    sanitizeHtml(value, {
      allowedTags: ['p', 'br', 'b', 'i', 'a'],
      allowedAttributes: { a: ['href'] },
    }),
  )
  content: string;
}

// ✅ Helmet with CSP
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
      },
    },
  }),
);
```

## Examples

### ✅ Good
```typescript
// Secure controller with guards, validated input, and safe output
@Controller('users')
export class UsersController {
  @Post()
  create(@Body() dto: CreateUserDto): Promise<UserResponseDto> {
    return this.usersService.create(dto);
  }

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string): Promise<UserResponseDto> {
    return this.usersService.findOne(id);
  }
}
```

### ❌ Bad
```typescript
@Controller('users')
export class UsersController {
  @Post()
  create(@Body() body: any) {
    // No validation, no DTO, accepts anything
    return this.usersService.create(body);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const user = await this.usersService.findById(id);
    if (!user) {
      // Reflects raw user input in error — XSS risk
      throw new NotFoundException(`User ${id} not found`);
    }
    return user; // Returns entity directly — exposes sensitive fields
  }
}
```
