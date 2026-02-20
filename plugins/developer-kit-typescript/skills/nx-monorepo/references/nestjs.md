# NestJS Backend Reference

## Create NestJS Application

### Basic Setup

```bash
# Using Node plugin with NestJS framework
nx g @nx/node:app my-api --framework=nest

# Using NestJS plugin directly
nx g @nx/nest:app my-api

# With directory
nx g @nx/nest:app my-api --directory=apps/api
```

### NestJS Library

```bash
# NestJS library
nx g @nx/nest:lib auth --directory=libs/backend

# With import path
nx g @nx/nest:lib shared-backend --importPath=@myorg/shared-backend
```

## Project Configuration

### project.json for NestJS App

```json
{
  "name": "api",
  "projectType": "application",
  "sourceRoot": "apps/api/src",
  "targets": {
    "build": {
      "executor": "@nx/js:tsc",
      "outputs": ["{workspaceRoot}/dist/apps/api"],
      "options": {
        "assets": ["apps/api/src/assets"],
        "main": "apps/api/src/main.ts",
        "tsConfig": "apps/api/tsconfig.app.json"
      },
      "configurations": {
        "production": {
          "optimization": true,
          "extractLicenses": true,
          "inspect": false
        }
      }
    },
    "serve": {
      "executor": "@nx/js:node",
      "options": {
        "buildTarget": "api:build"
      }
    },
    "test": {
      "executor": "@nx/jest:jest",
      "options": {
        "jestConfig": "apps/api/jest.config.ts"
      }
    },
    "lint": {
      "executor": "@nx/linter:eslint"
    }
  }
}
```

### Webpack Configuration (Optional)

For webpack bundling, configure `nx-webpack.config.js`:

```javascript
const { NxWebpackPlugin } = require('@nx/webpack');
const { join } = require('path');

module.exports = {
  output: {
    path: join(__dirname, '../../dist/apps/api'),
  },
  plugins: [
    new NxWebpackPlugin({
      target: 'node',
      compiler: 'tsc',
      transformers: [
        {
          name: '@nestjs/swagger/plugin',
          options: {
            dtoFileNameSuffix: ['.dto.ts', '.entity.ts'],
          },
        },
      ],
    }),
  ],
};
```

## NestJS Generators

### Resource Generator (All-in-One)

```bash
# Creates module, controller, service
nx g @nx/nest:resource users --project=my-api

# Creates with specific path
nx g @nx/nest:resource products --project=my-api --path=products
```

### Individual Generators

```bash
# Module
nx g @nx/nest:module auth --project=my-api

# Controller
nx g @nx/nest:controller users --project=my-api

# Service
nx g @nx/nest:service email --project=my-api

# Interface
nx g @nx/nest:interface user --project=my-api

# Class (DTO/Entity)
nx g @nx/nest:class create-user-dto --project=my-api
```

### Subdirectory Structure

```bash
# Create in subdirectory
nx g @nx/nest:controller admin/users --project=my-api
# Creates: apps/api/src/admin/users/users.controller.ts
```

## Swagger Integration

### Setup Swagger

```typescript
// apps/api/src/main.ts
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app/app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Swagger configuration
  const config = new DocumentBuilder()
    .setTitle('API Documentation')
    .setDescription('My API description')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);

  await app.listen(3000);
}
bootstrap();
```

### DTO with Swagger Decorators

```typescript
// apps/api/src/users/dto/create-user.dto.ts
import { ApiProperty } from '@nestjs/swagger';

export class CreateUserDto {
  @ApiProperty({ example: 'john@example.com' })
  email: string;

  @ApiProperty({ example: 'John Doe' })
  name: string;

  @ApiProperty({ example: 'P@ssw0rd!' })
  password: string;
}
```

## Testing

### Unit Tests

```bash
# Run tests
nx test my-api

# Watch mode
nx test my-api --watch

# Coverage
nx test my-api --coverage
```

### E2E Tests

```bash
# Add E2E to NestJS app
nx g @nx/jest:app my-api-e2e --project=my-api

# Run E2E
nx e2e my-api-e2e
```

### Example Test

```typescript
// apps/api/src/users/users.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { UsersService } from './users.service';

describe('UsersService', () => {
  let service: UsersService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [UsersService],
    }).compile();

    service = module.get<UsersService>(UsersService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  it('should create a user', () => {
    const user = service.create({
      email: 'test@example.com',
      name: 'Test User',
    });
    expect(user).toHaveProperty('id');
  });
});
```

## Common Patterns

### Microservices

```bash
# Create microservice app
nx g @nx/node:app auth-microservice --framework=nest
```

Configuration:

```typescript
// apps/auth-microservice/src/main.ts
import { NestFactory } from '@nestjs/core';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { AppModule } from './app/app.module';

async function bootstrap() {
  const app = await NestFactory.createMicroservice<MicroserviceOptions>(
    AppModule,
    {
      transport: Transport.TCP,
      options: { host: '127.0.0.1', port: 8877 },
    },
  );
  await app.listen();
}
bootstrap();
```

### Shared Backend Library

```bash
# Create shared library
nx g @nx/nest:lib shared-backend --importPath=@myorg/shared-backend

# Add interfaces/dto
nx g @nx/nest:interface user --project=shared-backend
nx g @nx/nest:class create-user-dto --project=shared-backend

# Use in API
// apps/api/src/users/users.service.ts
import { CreateUserDto } from '@myorg/shared-backend';
```

### Environment Configuration

```typescript
// apps/api/src/config/configuration.ts
export default () => ({
  port: parseInt(process.env.PORT, 10) || 3000,
  database: {
    host: process.env.DATABASE_HOST || 'localhost',
    port: parseInt(process.env.DATABASE_PORT, 10) || 5432,
  },
});
```

### TypeORM Integration

```bash
# Install TypeORM
npm install @nestjs/typeorm typeorm
```

Configuration:

```typescript
// apps/api/src/app/app.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: 'localhost',
      port: 5432,
      username: 'user',
      password: 'pass',
      database: 'mydb',
      autoLoadEntities: true,
    }),
  ],
})
export class AppModule {}
```

## Running NestJS App

```bash
# Development with watch
nx serve my-api

# Production build
nx build my-api --configuration=production

# Run production
node dist/apps/api/main.js
```

## Common Tasks

### Add Validation

```bash
npm install class-validator class-transformer
```

```typescript
// dto/create-user.dto.ts
import { IsEmail, IsString, MinLength } from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  email: string;

  @IsString()
  @MinLength(2)
  name: string;
}
```

### Add Guard

```bash
nx g @nx/nest:guard auth --project=my-api
```

### Add Interceptor

```bash
nx g @nx/nest:interceptor logging --project=my-api
```

### Add Pipe

```bash
nx g @nx/nest:pipe validation --project=my-api
```
