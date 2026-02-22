---
name: nestjs
version: 2.2.0
description: Provides comprehensive NestJS framework patterns with Drizzle ORM integration. Use when building NestJS applications, setting up APIs, implementing authentication, working with databases, or integrating Drizzle ORM. Covers controllers, providers, modules, middleware, guards, interceptors, testing, microservices, GraphQL, and database patterns.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
category: backend
tags: [nestjs, typescript, backend, api, orm, drizzle, typeorm]
---

# NestJS Framework with Drizzle ORM

## Overview

Comprehensive guidance for building NestJS applications with TypeScript, including integration with Drizzle ORM for database operations. Covers module structure, controllers, services, authentication, testing, and advanced patterns.

## When to Use

- Building REST APIs or GraphQL servers with NestJS
- Setting up authentication and authorization
- Implementing middleware, guards, or interceptors
- Working with databases (Drizzle ORM)
- Creating microservices architecture
- Writing unit and integration tests

## Instructions

1. **Start with Module Structure**: Define feature modules with clear boundaries
2. **Implement Controllers**: Create controllers for HTTP requests and routes
3. **Create Services**: Build business logic in injectable service classes
4. **Configure Database**: Set up Drizzle ORM with proper schema definitions
5. **Add Validation**: Implement DTOs with class-validator for input validation
6. **Implement Guards**: Add authentication and authorization guards
7. **Write Tests**: Create unit and e2e tests for all components

## Examples

### Complete CRUD Module

```typescript
// 1. Schema (Drizzle)
export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  price: real('price').notNull(),
  createdAt: timestamp('created_at').defaultNow(),
});

// 2. DTO
export class CreateProductDto {
  @IsString() @IsNotEmpty() name: string;
  @IsNumber() @Min(0) price: number;
}

// 3. Service
@Injectable()
export class ProductsService {
  constructor(private db: DatabaseService) {}
  async create(dto: CreateProductDto) {
    return this.db.database.insert(products).values(dto).returning();
  }
}

// 4. Controller
@Controller('products')
export class ProductsController {
  constructor(private service: ProductsService) {}
  @Post()
  create(@Body() dto: CreateProductDto) { return this.service.create(dto); }
}
```

### JWT Auth Guard

```typescript
@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private jwtService: JwtService) {}

  canActivate(context: ExecutionContext) {
    const request = context.switchToHttp().getRequest();
    const token = request.headers.authorization?.split(' ')[1];
    if (!token) return false;
    try {
      request.user = this.jwtService.verify(token);
      return true;
    } catch { return false; }
  }
}
```

## Constraints and Warnings

- **Database Connections**: Always use connection pooling for production
- **DTOs Required**: Never accept raw objects in controllers; always use DTOs
- **Module Imports**: Be careful with circular dependencies between modules
- **Guards Order**: Auth guards should run before role guards
- **Transaction Scope**: Keep transactions as short as possible
- **Environment Variables**: Never hardcode database credentials or secrets

## Best Practices

1. Always use constructor injection
2. Use DTOs for data transfer - define interfaces for request/response
3. Implement proper error handling with exception filters
4. Validate all inputs with validation pipes
5. Keep modules focused - single responsibility
6. Use transactions for complex operations
7. Write comprehensive unit and integration tests

## References

Consult these files for detailed patterns and examples:

- **[references/examples.md](references/examples.md)** - Drizzle ORM setup, database service, repository pattern, complete module examples, migrations, transactions, soft deletes
- **[references/reference.md](references/reference.md)** - Core architecture, validation pipes, exception filters, interceptors, custom decorators, microservices, GraphQL, testing patterns
- **[references/drizzle-reference.md](references/drizzle-reference.md)** - Drizzle ORM reference (recommended)
- **[references/typeorm-reference.md](references/typeorm-reference.md)** - TypeORM reference (legacy)
- **[references/workflow-optimization.md](references/workflow-optimization.md)** - Workflow optimization patterns
