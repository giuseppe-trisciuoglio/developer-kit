# NestJS Skill Workflow Optimization Guide

## Overview

This document outlines optimized workflows for building NestJS applications with Drizzle ORM by leveraging parallel execution, subagent delegation, and dependency management strategies.

## Key Optimization Principles

### 1. Parallel Execution Strategy

Tasks that can be executed simultaneously:
- **Package Installation**: Install NestJS, Drizzle, testing, and development dependencies in parallel
- **Module Scaffolding**: Create folder structures for multiple modules concurrently
- **Interface/Type Definition**: Define DTOs and interfaces while setting up database schemas
- **Test Preparation**: Set up test configuration while writing implementation code

### 2. Sequential Dependencies

Tasks that must follow a specific order:
1. **Project Setup**: `npm install → nest new → cd project → install additional packages`
2. **Database Setup**: `.env → drizzle.config.ts → schema → migrations → database service → repositories`
3. **Feature Development**: `DTOs → Repository → Service → Controller → Module → Guards`
4. **Testing**: `Unit tests → Integration tests → E2E tests`

## Optimized Workflow Examples

### Workflow 1: New NestJS Project with Drizzle ORM

```yaml
Phase 1: Parallel Setup (Agents: 2-3)
  Agent 1: Project Initialization
    - Create NestJS project
    - Install core dependencies
    - Configure TypeScript
    - Set up basic folder structure

  Agent 2: Database Preparation
    - Install Drizzle packages
    - Configure environment files
    - Set up drizzle.config.ts
    - Prepare database connection

Phase 2: Core Configuration (Sequential)
  - Database schema definition
  - Migration generation
  - Database service setup

Phase 3: Parallel Feature Development (Agents: 2-4)
  Agent 1: Data Layer
    - Repository implementation
    - Service layer logic
    - Unit tests for data layer

  Agent 2: API Layer
    - Controller implementation
    - DTOs and validation
    - Route protection

  Agent 3: Security
    - Authentication setup
    - Guards implementation
    - Security middleware

  Agent 4: Documentation
    - OpenAPI decorators
    - API documentation
    - README generation

Phase 4: Integration & Testing (Parallel)
  - Integration tests
  - E2E test scenarios
  - Performance optimization
```

### Workflow 2: Adding New Feature Module

```yaml
Step 1: Parallel Preparation
  - Define feature requirements
  - Create module folder structure
  - Prepare DTOs and interfaces
  - Set up test files

Step 2: Data Layer (Database Agent)
  - Create/update schema
  - Generate migrations
  - Implement repository
  - Write repository tests

Step 3: Business Logic (Service Agent)
  - Implement service methods
  - Add business validation
  - Handle transactions
  - Write unit tests

Step 4: API Layer (Controller Agent)
  - Create controller endpoints
  - Add validation pipes
  - Implement guards
  - Write integration tests

Step 5: Security Integration (Security Agent)
  - Add route protection
  - Implement role-based access
  - Add audit logging
  - Security tests

Step 6: Documentation (Documentation Agent)
  - Add OpenAPI decorators
  - Update API docs
  - Create examples
  - Review documentation
```

## Subagent Delegation Patterns

### When to Delegate to Database Agent
- Setting up new database connections
- Complex schema migrations
- Query optimization
- Transaction management
- Database testing setup

### When to Delegate to Security Agent
- Implementing authentication
- Setting up authorization
- Security audit requirements
- OAuth integration
- Vulnerability fixes

### When to Delegate to Testing Agent
- Comprehensive test suite creation
- Test infrastructure setup
- CI/CD test integration
- Performance testing
- Test data management

## Best Practices for Optimization

### 1. Dependency Management
```typescript
// Use async configuration for parallel setup
@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    DatabaseModule,
    AuthModule,
  ],
})
export class AppModule {}
```

### 2. Modular Architecture
```typescript
// Keep modules independent for parallel development
@Module({
  imports: [DatabaseModule],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],
})
export class UsersModule {}
```

### 3. Configuration-Driven Development
```typescript
// Enable environment-specific parallel development
export default () => ({
  database: {
    url: process.env.DATABASE_URL,
    poolSize: parseInt(process.env.DB_POOL_SIZE) || 10,
  },
  features: {
    auth: process.env.ENABLE_AUTH === 'true',
    caching: process.env.ENABLE_CACHE === 'true',
  },
});
```

### 4. Test-Driven Parallel Development
```typescript
// Write tests alongside implementation
describe('UsersService', () => {
  // Test setup can run in parallel with service implementation
  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [UsersService, MockRepository],
    }).compile();
  });
});
```

## Performance Optimization Techniques

### 1. Database Optimizations
- Use connection pooling
- Implement query batching
- Add proper indexes
- Use database transactions wisely

### 2. API Optimizations
- Implement caching strategies
- Use pagination
- Add compression middleware
- Optimize serialization

### 3. Testing Optimizations
- Parallel test execution
- Test database reuse
- Mock external services
- Selective test runs

## Monitoring and Feedback

### 1. Workflow Metrics
- Track time spent in each phase
- Measure parallel execution efficiency
- Monitor bottlenecks
- Collect agent performance data

### 2. Quality Gates
- Code reviews before merging
- Automated testing
- Security scans
- Performance benchmarks

## Conclusion

By following these optimized workflows and leveraging specialized subagents, NestJS development with Drizzle ORM can be significantly accelerated while maintaining high code quality and architectural integrity. The key is understanding task dependencies, maximizing parallel execution, and delegating specialized work to expert subagents.