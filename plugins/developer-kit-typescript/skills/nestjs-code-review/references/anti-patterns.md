# NestJS Anti-Patterns

## Controller Anti-Patterns

### Fat Controllers
Business logic in controllers makes code untestable and violates single responsibility.

```typescript
// ❌ Anti-pattern: Business logic in controller
@Post('register')
async register(@Body() dto: RegisterDto) {
  const existing = await this.userRepo.findOne({ email: dto.email });
  if (existing) throw new ConflictException('Email exists');

  const salt = await bcrypt.genSalt(10);
  const hash = await bcrypt.hash(dto.password, salt);

  const user = this.userRepo.create({ ...dto, password: hash });
  await this.userRepo.save(user);

  const token = this.jwtService.sign({ sub: user.id });
  await this.emailService.sendWelcome(user.email);

  return { user, token };
}
```

**Fix**: Move all logic to a service, keep the controller thin.

### Direct Repository Access in Controllers
Controllers should never access repositories directly — always go through a service layer.

```typescript
// ❌ Anti-pattern
@Controller('products')
export class ProductController {
  constructor(
    @InjectRepository(Product)
    private readonly productRepo: Repository<Product>,
  ) {}
}

// ✅ Fix: Inject the service instead
@Controller('products')
export class ProductController {
  constructor(private readonly productService: ProductService) {}
}
```

## Service Anti-Patterns

### God Service
A service that handles too many concerns becomes a maintenance nightmare.

```typescript
// ❌ Anti-pattern: Service handling users, orders, payments, emails
@Injectable()
export class AppService {
  async createUser() { /* ... */ }
  async processOrder() { /* ... */ }
  async chargePayment() { /* ... */ }
  async sendEmail() { /* ... */ }
  async generateReport() { /* ... */ }
}
```

**Fix**: Split into focused services — `UserService`, `OrderService`, `PaymentService`, etc.

### Tight Coupling to Infrastructure
Services that directly depend on infrastructure (HTTP clients, file system, specific databases) are hard to test and replace.

```typescript
// ❌ Anti-pattern: Direct infrastructure dependency
@Injectable()
export class NotificationService {
  async send(userId: string, message: string) {
    const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
      method: 'POST',
      headers: { Authorization: `Bearer ${process.env.SENDGRID_KEY}` },
      body: JSON.stringify({ to: userId, content: message }),
    });
    return response.json();
  }
}

// ✅ Fix: Use an interface/abstraction
interface EmailProvider {
  send(to: string, content: string): Promise<void>;
}

@Injectable()
export class NotificationService {
  constructor(
    @Inject('EMAIL_PROVIDER')
    private readonly emailProvider: EmailProvider,
  ) {}

  async send(userId: string, message: string): Promise<void> {
    const user = await this.userService.findOne(userId);
    await this.emailProvider.send(user.email, message);
  }
}
```

## Dependency Injection Anti-Patterns

### Manual Instantiation
Bypassing the DI container loses lifecycle management and testability.

```typescript
// ❌ Anti-pattern
@Injectable()
export class OrderService {
  private logger = new Logger(); // Not managed by DI
  private cache = new CacheService(); // Not injectable, not mockable

  async process() {
    this.logger.log('Processing');
  }
}
```

### Circular Dependencies
Two services depending on each other create circular dependency issues.

```typescript
// ❌ Anti-pattern: Circular dependency
@Injectable()
export class UserService {
  constructor(private orderService: OrderService) {}
}

@Injectable()
export class OrderService {
  constructor(private userService: UserService) {}
}

// ✅ Fix: Use forwardRef or restructure with events
@Injectable()
export class OrderService {
  constructor(
    @Inject(forwardRef(() => UserService))
    private userService: UserService,
  ) {}
}

// ✅ Better fix: Break the cycle with an event
@Injectable()
export class OrderService {
  constructor(private eventEmitter: EventEmitter2) {}

  async create(dto: CreateOrderDto) {
    const order = await this.save(dto);
    this.eventEmitter.emit('order.created', { userId: dto.userId });
  }
}
```

## Module Anti-Patterns

### Monolithic AppModule
Placing all controllers, services, and entities in AppModule destroys modularity.

```typescript
// ❌ Anti-pattern
@Module({
  imports: [TypeOrmModule.forFeature([User, Order, Product, Invoice, Report])],
  controllers: [UserCtrl, OrderCtrl, ProductCtrl, InvoiceCtrl, ReportCtrl],
  providers: [UserSvc, OrderSvc, ProductSvc, InvoiceSvc, ReportSvc],
})
export class AppModule {}
```

### Over-Exporting
Exporting everything from a module breaks encapsulation.

```typescript
// ❌ Anti-pattern: Exporting internal implementation details
@Module({
  providers: [UserService, UserRepository, PasswordHasher, UserMapper],
  exports: [UserService, UserRepository, PasswordHasher, UserMapper],
})
export class UserModule {}

// ✅ Fix: Export only the public API
@Module({
  providers: [UserService, UserRepository, PasswordHasher, UserMapper],
  exports: [UserService], // Only what other modules need
})
export class UserModule {}
```

## Error Handling Anti-Patterns

### Swallowing Errors
Catching errors without proper handling or logging hides bugs.

```typescript
// ❌ Anti-pattern
async findUser(id: string) {
  try {
    return await this.repo.findOne(id);
  } catch (error) {
    return null; // Error silently swallowed
  }
}
```

### Exposing Internal Errors
Sending raw error messages or stack traces to clients leaks internal details.

```typescript
// ❌ Anti-pattern
catch (error) {
  throw new HttpException(error.stack, 500); // Stack trace exposed
}
```

## Testing Anti-Patterns

### Testing Implementation Instead of Behavior
Tests that assert on internal method calls are brittle and break on refactoring.

```typescript
// ❌ Anti-pattern: Testing implementation
it('should call repository.save', async () => {
  await service.create(dto);
  expect(mockRepo.save).toHaveBeenCalledWith(expect.objectContaining(dto));
});

// ✅ Fix: Test behavior
it('should create a user and return it', async () => {
  const result = await service.create(dto);
  expect(result.email).toBe(dto.email);
  expect(result.id).toBeDefined();
});
```

### No Test Isolation
Tests that depend on shared state or execution order are fragile.

```typescript
// ❌ Anti-pattern: Shared mutable state between tests
describe('UserService', () => {
  const users = []; // Shared state

  it('creates a user', () => {
    users.push(createUser()); // Mutates shared state
    expect(users).toHaveLength(1);
  });

  it('checks user count', () => {
    expect(users).toHaveLength(1); // Depends on previous test
  });
});
```

## Configuration Anti-Patterns

### Hardcoded Configuration
Configuration values hardcoded in source code can't be changed per environment.

```typescript
// ❌ Anti-pattern
@Injectable()
export class DatabaseService {
  private readonly host = 'localhost';
  private readonly port = 5432;
  private readonly password = 'secretpassword';
}

// ✅ Fix: Use ConfigModule
@Injectable()
export class DatabaseService {
  constructor(private readonly configService: ConfigService) {}

  getConfig() {
    return {
      host: this.configService.getOrThrow('DB_HOST'),
      port: this.configService.get('DB_PORT', 5432),
    };
  }
}
```
