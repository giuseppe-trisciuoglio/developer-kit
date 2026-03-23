---
name: nestjs
description: Provides comprehensive NestJS framework patterns with Drizzle ORM integration. Use when building NestJS applications, setting up APIs, implementing authentication, working with databases, or integrating Drizzle ORM. Covers controllers, providers, modules, middleware, guards, interceptors, testing, microservices, GraphQL, and database patterns.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# NestJS Framework with Drizzle ORM

## Overview

This skill provides comprehensive guidance for building NestJS applications with TypeScript, including integration with Drizzle ORM for database operations.

## When to Use
- Building REST APIs or GraphQL servers with NestJS
- Setting up authentication and authorization
- Implementing middleware, guards, or interceptors
- Working with databases (Drizzle ORM)
- Creating microservices architecture
- Writing unit and integration tests
- Setting up OpenAPI/Swagger documentation

## Instructions

1. **Start with Module Structure**: Define your feature modules with clear boundaries
2. **Implement Controllers**: Create controllers to handle HTTP requests and define routes
3. **Create Services**: Build business logic in injectable service classes
4. **Configure Database**: Set up Drizzle ORM with proper schema definitions
5. **Add Validation**: Implement DTOs with class-validator for input validation
6. **Implement Guards**: Add authentication and authorization guards as needed
7. **Write Tests**: Create unit and e2e tests for all components
8. **Configure OpenAPI**: Add Swagger decorators for API documentation

## Examples

### Complete CRUD Module

```typescript
// 1. Define the entity schema (with Drizzle)
export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  price: real('price').notNull(),
  createdAt: timestamp('created_at').defaultNow(),
});

// 2. Create the DTO
export class CreateProductDto {
  @IsString()
  @IsNotEmpty()
  name: string;

  @IsNumber()
  @Min(0)
  price: number;
}

// 3. Implement the service
@Injectable()
export class ProductsService {
  constructor(private db: DatabaseService) {}

  async create(dto: CreateProductDto) {
    return this.db.database.insert(products).values(dto).returning();
  }
}

// 4. Create the controller
@Controller('products')
export class ProductsController {
  constructor(private service: ProductsService) {}

  @Post()
  create(@Body() dto: CreateProductDto) {
    return this.service.create(dto);
  }
}
```

## Constraints and Warnings

- **Database Connections**: Always use connection pooling for production
- **Async Operations**: All database operations are async; handle errors properly
- **DTOs Required**: Never accept raw objects in controllers; always use DTOs
- **Module Imports**: Be careful with circular dependencies between modules
- **Guards Order**: Auth guards should run before role guards
- **Transaction Scope**: Keep transactions as short as possible to avoid deadlocks
- **Environment Variables**: Never hardcode database credentials or secrets

## References

For detailed patterns and examples, see:
- [patterns.md](references/patterns.md) - Core architecture, database integration, auth, validation, exception handling, advanced patterns
- [testing.md](references/testing.md) - Unit and E2E testing patterns
- [migrations.md](references/migrations.md) - Database migrations with Drizzle
- [best-practices.md](references/best-practices.md) - Comprehensive best practices
