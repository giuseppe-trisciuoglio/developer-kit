# Rule: API Validation and DTOs

## Context

Input validation is critical for security and data integrity. NestJS provides `ValidationPipe` with `class-validator` to enforce validation rules declaratively via DTO decorators.

## Guidelines

### ValidationPipe Configuration
- Enable `ValidationPipe` globally in `main.ts` with these options:
  - `transform: true` — auto-transform payloads to DTO instances
  - `whitelist: true` — strip properties not defined in the DTO
  - `forbidNonWhitelisted: true` — reject requests with unknown properties
  - `forbidUnknownValues: true` — reject unknown objects

### DTO Design
- Create separate DTOs for each operation: `CreateOrderDto`, `UpdateOrderDto`, `OrderResponseDto`
- Use `class-validator` decorators on every property (`@IsString()`, `@IsNumber()`, `@IsEmail()`, etc.)
- Use `class-transformer` decorators for type coercion (`@Type()`, `@Transform()`)
- Use `@IsOptional()` for optional fields — combine with a validation decorator
- Use `PartialType()`, `PickType()`, `OmitType()` from `@nestjs/mapped-types` to derive DTOs

### Nested Validation
- Use `@ValidateNested()` with `@Type(() => NestedDto)` for nested objects
- Use `@IsArray()` with `@ValidateNested({ each: true })` for arrays of objects

### Validation Location
- Validate at the API boundary (controllers) — never deep inside business logic
- Let `ValidationPipe` handle formatting error responses automatically
- Use `@UsePipes()` for endpoint-specific pipe configurations

## Examples

### ✅ Correct — Global ValidationPipe Setup

```typescript
// main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(
    new ValidationPipe({
      transform: true,
      whitelist: true,
      forbidNonWhitelisted: true,
      forbidUnknownValues: true,
    }),
  );

  await app.listen(3000);
}
```

### ✅ Correct — DTO with Validation Decorators

```typescript
// order/dto/create-order.dto.ts
import { IsString, IsNumber, IsPositive, ValidateNested, IsArray } from 'class-validator';
import { Type } from 'class-transformer';

export class OrderItemDto {
  @IsString()
  readonly productId: string;

  @IsNumber()
  @IsPositive()
  readonly quantity: number;
}

export class CreateOrderDto {
  @IsString()
  readonly customerId: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  readonly items: OrderItemDto[];
}
```

### ✅ Correct — Derived DTOs with Mapped Types

```typescript
import { PartialType, OmitType } from '@nestjs/mapped-types';

// UpdateOrderDto has all CreateOrderDto fields as optional
export class UpdateOrderDto extends PartialType(CreateOrderDto) {}

// CreateOrderDto without customerId (set from auth context)
export class InternalCreateOrderDto extends OmitType(CreateOrderDto, ['customerId']) {}
```

### ✅ Correct — Controller Using DTOs

```typescript
@Controller('orders')
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @Post()
  async create(@Body() dto: CreateOrderDto): Promise<OrderResponseDto> {
    return this.orderService.create(dto);
  }

  @Patch(':id')
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateOrderDto,
  ): Promise<OrderResponseDto> {
    return this.orderService.update(id, dto);
  }
}
```

### ❌ Incorrect — No Validation on DTO

```typescript
// Missing class-validator decorators — no validation occurs
export class CreateOrderDto {
  customerId: string;  // No @IsString()
  quantity: number;    // No @IsNumber(), no @IsPositive()
}
```

### ❌ Incorrect — Manual Validation in Controller

```typescript
@Post()
async create(@Body() body: any) {
  // Wrong: manual validation instead of using ValidationPipe + DTOs
  if (!body.customerId || typeof body.customerId !== 'string') {
    throw new BadRequestException('customerId is required');
  }
  if (!body.quantity || body.quantity < 0) {
    throw new BadRequestException('quantity must be positive');
  }
  return this.orderService.create(body);
}
```
