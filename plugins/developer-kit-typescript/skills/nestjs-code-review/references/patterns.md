# NestJS Best Practice Patterns

## Controller Patterns

### Thin Controllers
Controllers should only handle HTTP concerns — route mapping, request parsing, response formatting. All business logic belongs in services.

```typescript
// ✅ Thin controller delegating to service
@Controller('orders')
@ApiTags('Orders')
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create an order' })
  @ApiResponse({ status: 201, type: OrderResponseDto })
  async create(
    @Body(ValidationPipe) dto: CreateOrderDto,
    @CurrentUser() user: AuthUser,
  ): Promise<OrderResponseDto> {
    return this.orderService.create(dto, user.id);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get order by ID' })
  async findOne(
    @Param('id', ParseUUIDPipe) id: string,
  ): Promise<OrderResponseDto> {
    return this.orderService.findOneOrFail(id);
  }
}
```

### Proper HTTP Status Codes
- `200` — Successful GET, PUT, PATCH
- `201` — Successful POST that creates a resource
- `204` — Successful DELETE with no response body
- `400` — Validation failure
- `401` — Missing or invalid authentication
- `403` — Valid authentication but insufficient permissions
- `404` — Resource not found
- `409` — Conflict (duplicate resource)
- `422` — Unprocessable entity (business rule violation)

## Service Patterns

### Single Responsibility Services
Each service should own one domain concern. Avoid "god services" that handle multiple unrelated operations.

```typescript
@Injectable()
export class OrderService {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly paymentService: PaymentService,
    private readonly eventEmitter: EventEmitter2,
  ) {}

  async create(dto: CreateOrderDto, userId: string): Promise<Order> {
    const order = await this.orderRepository.create({ ...dto, userId });
    await this.paymentService.processPayment(order);
    this.eventEmitter.emit('order.created', new OrderCreatedEvent(order));
    return order;
  }
}
```

### Transaction Management
Use database transactions for operations that must be atomic.

```typescript
@Injectable()
export class TransferService {
  constructor(private readonly dataSource: DataSource) {}

  async transfer(from: string, to: string, amount: number): Promise<void> {
    await this.dataSource.transaction(async (manager) => {
      await manager.decrement(Account, { id: from }, 'balance', amount);
      await manager.increment(Account, { id: to }, 'balance', amount);
    });
  }
}
```

## Module Patterns

### Feature Module Organization
Each feature should be a self-contained module with clear exports.

```typescript
@Module({
  imports: [
    TypeOrmModule.forFeature([Order, OrderItem]),
    PaymentModule,
  ],
  controllers: [OrderController],
  providers: [OrderService, OrderRepository],
  exports: [OrderService], // Only export what other modules need
})
export class OrderModule {}
```

### Dynamic Module Pattern
Use for configurable shared modules.

```typescript
@Module({})
export class CacheModule {
  static forRoot(options: CacheOptions): DynamicModule {
    return {
      module: CacheModule,
      global: true,
      providers: [
        { provide: CACHE_OPTIONS, useValue: options },
        CacheService,
      ],
      exports: [CacheService],
    };
  }
}
```

## Guard and Interceptor Patterns

### Composable Guards
Stack guards for layered security.

```typescript
@UseGuards(JwtAuthGuard, RolesGuard, ThrottlerGuard)
@Roles(Role.ADMIN)
@Controller('admin')
export class AdminController {}
```

### Response Transformation Interceptor
Standardize API responses.

```typescript
@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, ApiResponse<T>> {
  intercept(context: ExecutionContext, next: CallHandler): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map(data => ({
        success: true,
        data,
        timestamp: new Date().toISOString(),
      })),
    );
  }
}
```

## DTO Patterns

### Request DTOs with Validation
Always validate incoming data with class-validator decorators.

```typescript
export class CreateUserDto {
  @IsString()
  @IsNotEmpty()
  @MaxLength(100)
  @ApiProperty({ example: 'John Doe' })
  name: string;

  @IsEmail()
  @ApiProperty({ example: 'john@example.com' })
  email: string;

  @IsString()
  @MinLength(12)
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
    message: 'Password must contain uppercase, lowercase, and number',
  })
  password: string;

  @IsEnum(UserRole)
  @IsOptional()
  @ApiPropertyOptional({ enum: UserRole, default: UserRole.USER })
  role?: UserRole = UserRole.USER;
}
```

### Response DTOs with Exclusion
Never expose internal fields (passwords, internal IDs) in responses.

```typescript
export class UserResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty()
  name: string;

  @ApiProperty()
  email: string;

  @ApiProperty({ enum: UserRole })
  role: UserRole;

  @Exclude()
  password: string;

  @Exclude()
  deletedAt: Date;

  constructor(partial: Partial<UserResponseDto>) {
    Object.assign(this, partial);
  }
}
```

## Error Handling Patterns

### Domain Exception Classes
Create domain-specific exceptions for clear error semantics.

```typescript
export class OrderNotFoundException extends NotFoundException {
  constructor(orderId: string) {
    super(`Order with ID ${orderId} not found`);
  }
}

export class InsufficientBalanceException extends UnprocessableEntityException {
  constructor(required: number, available: number) {
    super(`Insufficient balance: required ${required}, available ${available}`);
  }
}
```

### Global Exception Filter
Centralize error formatting for consistent API responses.

```typescript
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    const message = exception instanceof HttpException
      ? exception.message
      : 'Internal server error';

    response.status(status).json({
      success: false,
      statusCode: status,
      message,
      timestamp: new Date().toISOString(),
    });
  }
}
```
