---
globs: "src/**/*.ts"
---
# Rule: NestJS API Design

## Context
Enforce best practices for NestJS API design: DTO serialization, pipes for input transformation, interceptors for cross-cutting concerns, and API versioning.

## Guidelines

### DTOs and Serialization
- **Never** return entity objects directly from controllers — use response DTOs
- Use `class-transformer` with `@Exclude()` and `@Expose()` to control serialized fields
- Enable `ClassSerializerInterceptor` globally to auto-serialize responses
- Use `@SerializeOptions({ groups: [...] })` for role-based field visibility

```typescript
// ✅ Entity with serialization control
@Entity()
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  email: string;

  @Column()
  @Exclude()
  passwordHash: string;

  @Column()
  @Exclude()
  internalNotes: string;
}

// ✅ Explicit response DTO
export class UserResponseDto {
  @Expose() id: string;
  @Expose() email: string;
  @Expose() name: string;

  @Expose()
  @Transform(({ obj }) => obj.posts?.length || 0)
  postCount: number;
}
```

### Pipes for Input Transformation
- Use built-in pipes: `ParseIntPipe`, `ParseUUIDPipe`, `DefaultValuePipe`, `ParseEnumPipe`
- Create custom pipes for business-specific transformations (dates, normalization)
- Enable global `ValidationPipe` with `whitelist`, `transform`, and `forbidNonWhitelisted`

```typescript
// ✅ Built-in pipes
@Get(':id')
findOne(@Param('id', ParseUUIDPipe) id: string): Promise<User> {
  return this.usersService.findOne(id);
}

@Get()
findAll(
  @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
  @Query('limit', new DefaultValuePipe(10), ParseIntPipe) limit: number,
): Promise<User[]> {
  return this.usersService.findAll(page, limit);
}

// ✅ Global ValidationPipe
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true,
    transform: true,
    forbidNonWhitelisted: true,
    transformOptions: { enableImplicitConversion: true },
  }),
);
```

### Interceptors for Cross-Cutting Concerns
- Use interceptors for logging, response transformation, caching, and timeouts
- **Never** duplicate cross-cutting logic inside every controller method
- Register global interceptors via `APP_INTERCEPTOR` provider token
- Use `@UseInterceptors()` for controller/route-specific interceptors

```typescript
// ✅ Logging interceptor
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger('HTTP');

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const req = context.switchToHttp().getRequest();
    const now = Date.now();

    return next.handle().pipe(
      tap(() => {
        const res = context.switchToHttp().getResponse();
        this.logger.log(`${req.method} ${req.url} ${res.statusCode} - ${Date.now() - now}ms`);
      }),
    );
  }
}

// ✅ Response transformation interceptor
@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, { data: T }> {
  intercept(context: ExecutionContext, next: CallHandler): Observable<{ data: T }> {
    return next.handle().pipe(
      map((data) => ({
        data,
        meta: {
          timestamp: new Date().toISOString(),
          path: context.switchToHttp().getRequest().url,
        },
      })),
    );
  }
}

// ✅ Timeout interceptor
@Injectable()
export class TimeoutInterceptor implements NestInterceptor {
  intercept(_context: ExecutionContext, next: CallHandler): Observable<unknown> {
    return next.handle().pipe(
      timeout(5000),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          throw new RequestTimeoutException('Request timed out');
        }
        throw err;
      }),
    );
  }
}
```

### API Versioning
- Use NestJS built-in versioning for breaking changes (`VersioningType.URI`, `HEADER`, or `MEDIA_TYPE`)
- **Never** manually prefix routes with `/v1/`, `/v2/` — use `@Version()` decorator
- Use `VERSION_NEUTRAL` for routes available in all versions
- Add deprecation headers (`Sunset`, `Deprecation`) to old versions

```typescript
// ✅ Enable versioning
app.enableVersioning({
  type: VersioningType.URI,
  defaultVersion: '1',
});

// ✅ Version-specific controllers
@Controller('users')
@Version('1')
export class UsersV1Controller { ... }

@Controller('users')
@Version('2')
export class UsersV2Controller { ... }

// ✅ Per-route versioning
@Controller('users')
export class UsersController {
  @Get(':id')
  @Version(['1', '2'])
  findOne(@Param('id') id: string): Promise<User> { ... }

  @Post()
  @Version(VERSION_NEUTRAL)
  create(@Body() dto: CreateUserDto): Promise<User> { ... }
}
```

## Examples

### ✅ Good
```typescript
@Controller('users')
export class UsersController {
  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string): Promise<UserResponseDto> {
    return this.usersService.findOne(id);
  }

  @Get()
  findAll(@Query() query: FindUsersQueryDto): Promise<UserResponseDto[]> {
    return this.usersService.findAll(query);
  }

  @Post()
  create(@Body() dto: CreateUserDto): Promise<UserResponseDto> {
    return this.usersService.create(dto);
  }
}
```

### ❌ Bad
```typescript
@Controller('users')
export class UsersController {
  @Get(':id')
  async findOne(@Param('id') id: string): Promise<User> {
    // Returns entity directly — exposes passwordHash, internalNotes
    return this.usersService.findById(id);
  }

  @Get()
  async findAll(@Query('page') page: string, @Query('limit') limit: string) {
    // Manual parsing — error-prone, no validation
    const pageNum = parseInt(page) || 1;
    const limitNum = parseInt(limit) || 10;
    return this.usersService.findAll(pageNum, limitNum);
  }
}
```
