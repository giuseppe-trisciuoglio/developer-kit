# NestJS Framework Documentation

NestJS is a progressive Node.js framework for building efficient, reliable and scalable server-side applications. Built with TypeScript and fully supporting both TypeScript and JavaScript, it combines elements of Object Oriented Programming (OOP), Functional Programming (FP), and Functional Reactive Programming (FRP). Under the hood, NestJS uses robust HTTP server frameworks like Express (default) or Fastify, providing a level of abstraction while exposing their APIs directly to developers.

The framework provides an out-of-the-box application architecture inspired by Angular, enabling developers to create highly testable, scalable, loosely coupled, and maintainable applications. NestJS leverages dependency injection, decorators, modules, guards, interceptors, and pipes to organize code effectively. It supports multiple transport layers for microservices, integrates seamlessly with databases through TypeORM and Sequelize, and provides first-class support for GraphQL and OpenAPI documentation.

## Core Building Blocks

### Creating a Basic Application

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
 const app = await NestFactory.create(AppModule);
 await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
```

### Controllers - HTTP Request Handling

```typescript
import { Controller, Get, Post, Put, Delete, Body, Param, Query } from '@nestjs/common';
import { CreateCatDto, UpdateCatDto } from './dto';
import { CatsService } from './cats.service';

@Controller('cats')
export class CatsController {
 constructor(private catsService: CatsService) {}

 @Post()
 async create(@Body() createCatDto: CreateCatDto) {
 this.catsService.create(createCatDto);
 return { message: 'Cat created successfully' };
 }

 @Get()
 async findAll(@Query('age') age?: number, @Query('breed') breed?: string) {
 return this.catsService.findAll({ age, breed });
 }

 @Get(':id')
 async findOne(@Param('id') id: string) {
 return this.catsService.findOne(id);
 }

 @Put(':id')
 async update(@Param('id') id: string, @Body() updateCatDto: UpdateCatDto) {
 return this.catsService.update(id, updateCatDto);
 }

 @Delete(':id')
 async remove(@Param('id') id: string) {
 await this.catsService.remove(id);
 return { message: 'Cat removed successfully' };
 }
}
```

### Providers - Business Logic and Services

```typescript
import { Injectable } from '@nestjs/common';
import { Cat } from './interfaces/cat.interface';

@Injectable()
export class CatsService {
 private readonly cats: Cat[] = [];

 create(cat: Cat): void {
 this.cats.push(cat);
 }

 findAll(filter?: { age?: number; breed?: string }): Cat[] {
 if (!filter) return this.cats;

 return this.cats.filter(cat => {
 if (filter.age && cat.age !== filter.age) return false;
 if (filter.breed && cat.breed !== filter.breed) return false;
 return true;
 });
 }

 findOne(id: string): Cat | undefined {
 return this.cats.find(cat => cat.id === id);
 }

 update(id: string, updateData: Partial): Cat {
 const catIndex = this.cats.findIndex(cat => cat.id === id);
 if (catIndex === -1) throw new Error('Cat not found');

 this.cats[catIndex] = { ...this.cats[catIndex], ...updateData };
 return this.cats[catIndex];
 }

 remove(id: string): void {
 const catIndex = this.cats.findIndex(cat => cat.id === id);
 if (catIndex === -1) throw new Error('Cat not found');
 this.cats.splice(catIndex, 1);
 }
}
```

### Modules - Application Organization

```typescript
import { Module } from '@nestjs/common';
import { CatsController } from './cats.controller';
import { CatsService } from './cats.service';

@Module({
 controllers: [CatsController],
 providers: [CatsService],
 exports: [CatsService], // Make service available to other modules
})
export class CatsModule {}

// Root module
import { Module } from '@nestjs/common';
import { CatsModule } from './cats/cats.module';
import { DogsModule } from './dogs/dogs.module';

@Module({
 imports: [CatsModule, DogsModule],
})
export class AppModule {}
```

## Middleware

### Class-Based Middleware

```typescript
import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
 use(req: Request, res: Response, next: NextFunction) {
 console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
 next();
 }
}

// Apply in module
import { Module, NestModule, MiddlewareConsumer, RequestMethod } from '@nestjs/common';

@Module({
 imports: [CatsModule],
})
export class AppModule implements NestModule {
 configure(consumer: MiddlewareConsumer) {
 consumer
 .apply(LoggerMiddleware)
 .exclude(
 { path: 'cats', method: RequestMethod.GET },
 'cats/{*splat}',
 )
 .forRoutes(CatsController);
 }
}
```

### Functional Middleware

```typescript
import { Request, Response, NextFunction } from 'express';

export function logger(req: Request, res: Response, next: NextFunction) {
 console.log(`Request...`);
 next();
}

// Apply in module
consumer.apply(logger).forRoutes(CatsController);

// Global middleware
const app = await NestFactory.create(AppModule);
app.use(logger);
await app.listen(3000);
```

## Exception Filters

### Built-in Exception Handling

```typescript
import { Controller, Get, Post, Body, HttpException, HttpStatus } from '@nestjs/common';

@Controller('cats')
export class CatsController {
 @Get()
 async findAll() {
 throw new HttpException('Forbidden', HttpStatus.FORBIDDEN);
 }

 @Post()
 async create(@Body() createCatDto: CreateCatDto) {
 throw new HttpException({
 status: HttpStatus.FORBIDDEN,
 error: 'This is a custom message',
 }, HttpStatus.FORBIDDEN);
 }
}
```

### Custom Exception Filter

```typescript
import { ExceptionFilter, Catch, ArgumentsHost, HttpException } from '@nestjs/common';
import { Request, Response } from 'express';

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
 catch(exception: HttpException, host: ArgumentsHost) {
 const ctx = host.switchToHttp();
 const response = ctx.getResponse();
 const request = ctx.getRequest();
 const status = exception.getStatus();

 response.status(status).json({
 statusCode: status,
 timestamp: new Date().toISOString(),
 path: request.url,
 message: exception.message,
 });
 }
}

// Apply to controller or method
import { UseFilters } from '@nestjs/common';

@Post()
@UseFilters(new HttpExceptionFilter())
async create(@Body() createCatDto: CreateCatDto) {
 throw new ForbiddenException();
}

// Global exception filter
const app = await NestFactory.create(AppModule);
app.useGlobalFilters(new HttpExceptionFilter());

// Global with dependency injection
@Module({
 providers: [
 {
 provide: APP_FILTER,
 useClass: HttpExceptionFilter,
 },
 ],
})
export class AppModule {}
```

### Catch-All Exception Filter

```typescript
import { Catch, ArgumentsHost, HttpException, HttpStatus } from '@nestjs/common';
import { HttpAdapterHost } from '@nestjs/core';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
 constructor(private readonly httpAdapterHost: HttpAdapterHost) {}

 catch(exception: unknown, host: ArgumentsHost): void {
 const { httpAdapter } = this.httpAdapterHost;
 const ctx = host.switchToHttp();

 const httpStatus = exception instanceof HttpException
 ? exception.getStatus()
 : HttpStatus.INTERNAL_SERVER_ERROR;

 const responseBody = {
 statusCode: httpStatus,
 timestamp: new Date().toISOString(),
 path: httpAdapter.getRequestUrl(ctx.getRequest()),
 message: exception instanceof Error ? exception.message : 'Internal server error',
 };

 httpAdapter.reply(ctx.getResponse(), responseBody, httpStatus);
 }
}
```

## Pipes

### Built-in Transformation Pipes

```typescript
import { Controller, Get, Param, Query, ParseIntPipe, ParseUUIDPipe } from '@nestjs/common';

@Controller('cats')
export class CatsController {
 @Get(':id')
 async findOne(@Param('id', ParseIntPipe) id: number) {
 return this.catsService.findOne(id);
 }

 @Get('user/:uuid')
 async findByUser(@Param('uuid', ParseUUIDPipe) uuid: string) {
 return this.catsService.findByUser(uuid);
 }

 @Get()
 async findAll(@Query('page', ParseIntPipe) page: number) {
 return this.catsService.findAll(page);
 }
}
```

### Validation Pipe with class-validator

```typescript
import { IsString, IsInt, Min, Max } from 'class-validator';

export class CreateCatDto {
 @IsString()
 name: string;

 @IsInt()
 @Min(0)
 @Max(30)
 age: number;

 @IsString()
 breed: string;
}

// Apply validation pipe
import { Controller, Post, Body, UsePipes, ValidationPipe } from '@nestjs/common';

@Controller('cats')
export class CatsController {
 @Post()
 @UsePipes(new ValidationPipe())
 async create(@Body() createCatDto: CreateCatDto) {
 return this.catsService.create(createCatDto);
 }
}

// Global validation pipe
async function bootstrap() {
 const app = await NestFactory.create(AppModule);
 app.useGlobalPipes(new ValidationPipe({
 whitelist: true,
 forbidNonWhitelisted: true,
 transform: true,
 }));
 await app.listen(3000);
}

// With dependency injection
@Module({
 providers: [
 {
 provide: APP_PIPE,
 useClass: ValidationPipe,
 },
 ],
})
export class AppModule {}
```

### Custom Transformation Pipe

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class ParseIntPipe implements PipeTransform {
 transform(value: string, metadata: ArgumentMetadata): number {
 const val = parseInt(value, 10);
 if (isNaN(val)) {
 throw new BadRequestException('Validation failed (numeric string is expected)');
 }
 return val;
 }
}

@Get(':id')
async findOne(@Param('id', new ParseIntPipe()) id: number) {
 return this.catsService.findOne(id);
}
```

### Schema Validation with Zod

```typescript
import { PipeTransform, ArgumentMetadata, BadRequestException } from '@nestjs/common';
import { ZodSchema } from 'zod';

export class ZodValidationPipe implements PipeTransform {
 constructor(private schema: ZodSchema) {}

 transform(value: unknown, metadata: ArgumentMetadata) {
 try {
 const parsedValue = this.schema.parse(value);
 return parsedValue;
 } catch (error) {
 throw new BadRequestException('Validation failed');
 }
 }
}

// Define schema
import { z } from 'zod';

export const createCatSchema = z.object({
 name: z.string(),
 age: z.number().min(0).max(30),
 breed: z.string(),
}).required();

export type CreateCatDto = z.infer;

// Use in controller
@Post()
@UsePipes(new ZodValidationPipe(createCatSchema))
async create(@Body() createCatDto: CreateCatDto) {
 return this.catsService.create(createCatDto);
}
```

## Guards

### Authentication Guard

```typescript
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { Observable } from 'rxjs';

@Injectable()
export class AuthGuard implements CanActivate {
 canActivate(context: ExecutionContext): boolean | Promise | Observable {
 const request = context.switchToHttp().getRequest();
 const token = request.headers.authorization;

 if (!token) {
 throw new UnauthorizedException('No token provided');
 }

 try {
 // Validate token logic here
 const user = this.validateToken(token);
 request.user = user;
 return true;
 } catch (error) {
 throw new UnauthorizedException('Invalid token');
 }
 }

 private validateToken(token: string) {
 // Token validation logic
 return { id: '123', username: 'john' };
 }
}

// Apply guard
import { Controller, Get, UseGuards } from '@nestjs/common';

@Controller('cats')
@UseGuards(AuthGuard)
export class CatsController {
 @Get()
 findAll() {
 return this.catsService.findAll();
 }
}
```

### Role-Based Authorization Guard

```typescript
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

// Custom decorator
export const Roles = Reflector.createDecorator();

@Injectable()
export class RolesGuard implements CanActivate {
 constructor(private reflector: Reflector) {}

 canActivate(context: ExecutionContext): boolean {
 const roles = this.reflector.get(Roles, context.getHandler());
 if (!roles) {
 return true;
 }

 const request = context.switchToHttp().getRequest();
 const user = request.user;

 return this.matchRoles(roles, user.roles);
 }

 private matchRoles(requiredRoles: string[], userRoles: string[]): boolean {
 return requiredRoles.some(role => userRoles.includes(role));
 }
}

// Use in controller
@Post()
@Roles(['admin'])
@UseGuards(RolesGuard)
async create(@Body() createCatDto: CreateCatDto) {
 return this.catsService.create(createCatDto);
}

// Global guard with DI
@Module({
 providers: [
 {
 provide: APP_GUARD,
 useClass: RolesGuard,
 },
 ],
})
export class AppModule {}
```

## Interceptors

### Logging Interceptor

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
 intercept(context: ExecutionContext, next: CallHandler): Observable {
 const request = context.switchToHttp().getRequest();
 const { method, url } = request;
 const now = Date.now();

 console.log(`[${method}] ${url} - Start`);

 return next.handle().pipe(
 tap(() => {
 console.log(`[${method}] ${url} - Completed in ${Date.now() - now}ms`);
 }),
 );
 }
}

@UseInterceptors(LoggingInterceptor)
@Controller('cats')
export class CatsController {}
```

### Response Transformation Interceptor

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Response {
 data: T;
 timestamp: string;
 path: string;
}

@Injectable()
export class TransformInterceptor implements NestInterceptor> {
 intercept(context: ExecutionContext, next: CallHandler): Observable> {
 const request = context.switchToHttp().getRequest();

 return next.handle().pipe(
 map(data => ({
 data,
 timestamp: new Date().toISOString(),
 path: request.url,
 })),
 );
 }
}

// Result: GET /cats returns { data: [...], timestamp: "...", path: "/cats" }
```

### Cache Interceptor

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable, of } from 'rxjs';

@Injectable()
export class CacheInterceptor implements NestInterceptor {
 private cache = new Map();

 intercept(context: ExecutionContext, next: CallHandler): Observable {
 const request = context.switchToHttp().getRequest();
 const cacheKey = `${request.method}:${request.url}`;

 if (this.cache.has(cacheKey)) {
 console.log('Returning cached response');
 return of(this.cache.get(cacheKey));
 }

 return next.handle().pipe(
 tap(response => {
 this.cache.set(cacheKey, response);
 }),
 );
 }
}
```

### Timeout Interceptor

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, RequestTimeoutException } from '@nestjs/common';
import { Observable, throwError, TimeoutError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';

@Injectable()
export class TimeoutInterceptor implements NestInterceptor {
 intercept(context: ExecutionContext, next: CallHandler): Observable {
 return next.handle().pipe(
 timeout(5000),
 catchError(err => {
 if (err instanceof TimeoutError) {
 return throwError(() => new RequestTimeoutException('Request timeout'));
 }
 return throwError(() => err);
 }),
 );
 }
}
```

## Dependency Injection

### Constructor Injection

```typescript
@Injectable()
export class CatsService {
 constructor(
 private readonly dogsService: DogsService,
 private readonly configService: ConfigService,
 ) {}

 async findAll() {
 const config = this.configService.get('database');
 return this.catsRepository.find();
 }
}
```

### Custom Provider with Token

```typescript
const CONNECTION = 'DATABASE_CONNECTION';

@Module({
 providers: [
 {
 provide: CONNECTION,
 useValue: {
 host: 'localhost',
 port: 5432,
 database: 'test',
 },
 },
 ],
})
export class DatabaseModule {}

// Inject custom provider
@Injectable()
export class CatsRepository {
 constructor(@Inject(CONNECTION) private connection: any) {}
}
```

### Factory Provider

```typescript
@Module({
 providers: [
 {
 provide: 'DATABASE_CONNECTION',
 useFactory: async (configService: ConfigService) => {
 const config = configService.get('database');
 const connection = await createConnection(config);
 return connection;
 },
 inject: [ConfigService],
 },
 ],
})
export class DatabaseModule {}
```

### Async Provider

```typescript
@Module({
 providers: [
 {
 provide: 'ASYNC_CONNECTION',
 useFactory: async () => {
 const connection = await createAsyncConnection();
 return connection;
 },
 },
 ],
})
export class AppModule {}
```

### Class Provider with Conditional Logic

```typescript
const configServiceProvider = {
 provide: ConfigService,
 useClass: process.env.NODE_ENV === 'development'
 ? DevelopmentConfigService
 : ProductionConfigService,
};

@Module({
 providers: [configServiceProvider],
})
export class AppModule {}
```

## Database Integration

### TypeORM Setup

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
 imports: [
 TypeOrmModule.forRoot({
 type: 'postgres',
 host: 'localhost',
 port: 5432,
 username: 'postgres',
 password: 'password',
 database: 'nest_db',
 entities: [__dirname + '/**/*.entity{.ts,.js}'],
 synchronize: true, // Don't use in production
 logging: true,
 }),
 ],
})
export class AppModule {}
```

### Entity Definition

```typescript
import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn, OneToMany } from 'typeorm';
import { Photo } from '../photos/photo.entity';

@Entity('users')
export class User {
 @PrimaryGeneratedColumn('uuid')
 id: string;

 @Column({ unique: true })
 email: string;

 @Column()
 firstName: string;

 @Column()
 lastName: string;

 @Column({ default: true })
 isActive: boolean;

 @CreateDateColumn()
 createdAt: Date;

 @UpdateDateColumn()
 updatedAt: Date;

 @OneToMany(() => Photo, photo => photo.user)
 photos: Photo[];
}
```

### Repository Pattern

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';

@Injectable()
export class UsersService {
 constructor(
 @InjectRepository(User)
 private usersRepository: Repository,
 ) {}

 async findAll(): Promise {
 return this.usersRepository.find({ relations: ['photos'] });
 }

 async findOne(id: string): Promise {
 const user = await this.usersRepository.findOne({
 where: { id },
 relations: ['photos'],
 });
 if (!user) throw new NotFoundException('User not found');
 return user;
 }

 async create(userData: CreateUserDto): Promise {
 const user = this.usersRepository.create(userData);
 return this.usersRepository.save(user);
 }

 async update(id: string, updateData: UpdateUserDto): Promise {
 await this.usersRepository.update(id, updateData);
 return this.findOne(id);
 }

 async remove(id: string): Promise {
 const result = await this.usersRepository.delete(id);
 if (result.affected === 0) {
 throw new NotFoundException('User not found');
 }
 }
}

@Module({
 imports: [TypeOrmModule.forFeature([User])],
 providers: [UsersService],
 controllers: [UsersController],
 exports: [UsersService],
})
export class UsersModule {}
```

### Database Transactions

```typescript
import { DataSource } from 'typeorm';

@Injectable()
export class UsersService {
 constructor(
 @InjectRepository(User) private usersRepository: Repository,
 private dataSource: DataSource,
 ) {}

 async createUserWithPhotos(userData: CreateUserDto, photos: CreatePhotoDto[]) {
 const queryRunner = this.dataSource.createQueryRunner();
 await queryRunner.connect();
 await queryRunner.startTransaction();

 try {
 const user = await queryRunner.manager.save(User, userData);

 for (const photoData of photos) {
 await queryRunner.manager.save(Photo, { ...photoData, user });
 }

 await queryRunner.commitTransaction();
 return user;
 } catch (err) {
 await queryRunner.rollbackTransaction();
 throw err;
 } finally {
 await queryRunner.release();
 }
 }
}
```

### Async Configuration

```typescript
TypeOrmModule.forRootAsync({
 imports: [ConfigModule],
 useFactory: (configService: ConfigService) => ({
 type: 'postgres',
 host: configService.get('DB_HOST'),
 port: configService.get('DB_PORT'),
 username: configService.get('DB_USERNAME'),
 password: configService.get('DB_PASSWORD'),
 database: configService.get('DB_NAME'),
 entities: [__dirname + '/**/*.entity{.ts,.js}'],
 synchronize: configService.get('DB_SYNC') === 'true',
 }),
 inject: [ConfigService],
})
```

## Testing

### Unit Testing with Mocks

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { CatsController } from './cats.controller';
import { CatsService } from './cats.service';

describe('CatsController', () => {
 let catsController: CatsController;
 let catsService: CatsService;

 beforeEach(async () => {
 const module: TestingModule = await Test.createTestingModule({
 controllers: [CatsController],
 providers: [CatsService],
 }).compile();

 catsService = module.get(CatsService);
 catsController = module.get(CatsController);
 });

 describe('findAll', () => {
 it('should return an array of cats', async () => {
 const result = [{ name: 'Test Cat', age: 2, breed: 'Persian' }];
 jest.spyOn(catsService, 'findAll').mockImplementation(() => Promise.resolve(result));

 expect(await catsController.findAll()).toBe(result);
 });
 });

 describe('create', () => {
 it('should create a cat', async () => {
 const catDto = { name: 'New Cat', age: 1, breed: 'Siamese' };
 jest.spyOn(catsService, 'create').mockImplementation(() => Promise.resolve(catDto));

 expect(await catsController.create(catDto)).toEqual(catDto);
 });
 });
});
```

### Testing with Provider Override

```typescript
describe('CatsController', () => {
 let controller: CatsController;

 const mockCatsService = {
 findAll: jest.fn(() => [{ name: 'Test', age: 2, breed: 'Persian' }]),
 findOne: jest.fn((id) => ({ id, name: 'Test', age: 2, breed: 'Persian' })),
 create: jest.fn((dto) => ({ id: '123', ...dto })),
 };

 beforeEach(async () => {
 const module: TestingModule = await Test.createTestingModule({
 controllers: [CatsController],
 providers: [CatsService],
 })
 .overrideProvider(CatsService)
 .useValue(mockCatsService)
 .compile();

 controller = module.get(CatsController);
 });

 it('should be defined', () => {
 expect(controller).toBeDefined();
 });
});
```

### End-to-End Testing

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';

describe('CatsController (e2e)', () => {
 let app: INestApplication;

 beforeAll(async () => {
 const moduleFixture: TestingModule = await Test.createTestingModule({
 imports: [AppModule],
 }).compile();

 app = moduleFixture.createNestApplication();
 await app.init();
 });

 afterAll(async () => {
 await app.close();
 });

 it('/cats (GET)', () => {
 return request(app.getHttpServer())
 .get('/cats')
 .expect(200)
 .expect((res) => {
 expect(Array.isArray(res.body)).toBe(true);
 });
 });

 it('/cats (POST)', () => {
 return request(app.getHttpServer())
 .post('/cats')
 .send({ name: 'Test Cat', age: 2, breed: 'Persian' })
 .expect(201)
 .expect((res) => {
 expect(res.body).toHaveProperty('id');
 expect(res.body.name).toBe('Test Cat');
 });
 });

 it('/cats/:id (GET)', () => {
 return request(app.getHttpServer())
 .get('/cats/123')
 .expect(200)
 .expect((res) => {
 expect(res.body).toHaveProperty('id', '123');
 });
 });
});
```

### Testing with Repository Mocks

```typescript
describe('UsersService', () => {
 let service: UsersService;
 let repository: Repository;

 const mockRepository = {
 find: jest.fn(),
 findOne: jest.fn(),
 create: jest.fn(),
 save: jest.fn(),
 update: jest.fn(),
 delete: jest.fn(),
 };

 beforeEach(async () => {
 const module: TestingModule = await Test.createTestingModule({
 providers: [
 UsersService,
 {
 provide: getRepositoryToken(User),
 useValue: mockRepository,
 },
 ],
 }).compile();

 service = module.get(UsersService);
 repository = module.get>(getRepositoryToken(User));
 });

 it('should find all users', async () => {
 const users = [{ id: '1', email: 'test@example.com' }];
 mockRepository.find.mockResolvedValue(users);

 expect(await service.findAll()).toEqual(users);
 expect(repository.find).toHaveBeenCalled();
 });
});
```

## Microservices

### TCP Microservice Setup

```typescript
import { NestFactory } from '@nestjs/core';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';
import { AppModule } from './app.module';

async function bootstrap() {
 const app = await NestFactory.createMicroservice(
 AppModule,
 {
 transport: Transport.TCP,
 options: {
 host: '127.0.0.1',
 port: 8877,
 },
 },
 );
 await app.listen();
}
bootstrap();
```

### Message Pattern Handler

```typescript
import { Controller } from '@nestjs/common';
import { MessagePattern, Payload, Ctx, NatsContext } from '@nestjs/microservices';

@Controller()
export class MathController {
 @MessagePattern({ cmd: 'sum' })
 accumulate(@Payload() data: number[]): number {
 return (data || []).reduce((a, b) => a + b, 0);
 }

 @MessagePattern({ cmd: 'multiply' })
 multiply(@Payload() data: { a: number; b: number }): number {
 return data.a * data.b;
 }
}
```

### Event Pattern Handler

```typescript
@Controller()
export class NotificationsController {
 @EventPattern('user_created')
 async handleUserCreated(@Payload() data: CreateUserEvent) {
 console.log('New user created:', data);
 // Send welcome email
 await this.emailService.sendWelcome(data.email);
 }

 @EventPattern('order_placed')
 async handleOrderPlaced(@Payload() data: OrderPlacedEvent) {
 console.log('Order placed:', data);
 // Process order
 await this.orderService.process(data);
 }
}
```

### Microservice Client

```typescript
import { Module } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';

@Module({
 imports: [
 ClientsModule.register([
 {
 name: 'MATH_SERVICE',
 transport: Transport.TCP,
 options: {
 host: '127.0.0.1',
 port: 8877,
 },
 },
 ]),
 ],
 controllers: [AppController],
})
export class AppModule {}

// Use in controller
import { Controller, Get, Inject } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';
import { Observable } from 'rxjs';

@Controller()
export class AppController {
 constructor(@Inject('MATH_SERVICE') private client: ClientProxy) {}

 @Get('sum')
 accumulate(): Observable {
 const pattern = { cmd: 'sum' };
 const payload = [1, 2, 3, 4, 5];
 return this.client.send(pattern, payload);
 }

 @Get('notify')
 async notify() {
 this.client.emit('user_created', { id: '123', email: 'user@example.com' });
 return { message: 'Notification sent' };
 }
}
```

### Redis Transport

```typescript
// Microservice
const app = await NestFactory.createMicroservice(
 AppModule,
 {
 transport: Transport.REDIS,
 options: {
 host: 'localhost',
 port: 6379,
 },
 },
);

// Client
ClientsModule.register([
 {
 name: 'REDIS_SERVICE',
 transport: Transport.REDIS,
 options: {
 host: 'localhost',
 port: 6379,
 },
 },
])
```

## GraphQL

### Apollo GraphQL Setup

```typescript
import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { join } from 'path';

@Module({
 imports: [
 GraphQLModule.forRoot({
 driver: ApolloDriver,
 autoSchemaFile: join(process.cwd(), 'src/schema.gql'),
 sortSchema: true,
 playground: true,
 }),
 ],
})
export class AppModule {}
```

### GraphQL Resolvers (Code First)

```typescript
import { Resolver, Query, Mutation, Args, ID } from '@nestjs/graphql';
import { ObjectType, Field, Int } from '@nestjs/graphql';

@ObjectType()
export class Cat {
 @Field(() => ID)
 id: string;

 @Field()
 name: string;

 @Field(() => Int)
 age: number;

 @Field()
 breed: string;
}

@Resolver(() => Cat)
export class CatsResolver {
 constructor(private catsService: CatsService) {}

 @Query(() => [Cat], { name: 'cats' })
 async findAll() {
 return this.catsService.findAll();
 }

 @Query(() => Cat, { name: 'cat' })
 async findOne(@Args('id', { type: () => ID }) id: string) {
 return this.catsService.findOne(id);
 }

 @Mutation(() => Cat)
 async createCat(
 @Args('name') name: string,
 @Args('age', { type: () => Int }) age: number,
 @Args('breed') breed: string,
 ) {
 return this.catsService.create({ name, age, breed });
 }

 @Mutation(() => Boolean)
 async removeCat(@Args('id', { type: () => ID }) id: string) {
 await this.catsService.remove(id);
 return true;
 }
}
```

### GraphQL Input Types

```typescript
import { InputType, Field, Int } from '@nestjs/graphql';

@InputType()
export class CreateCatInput {
 @Field()
 name: string;

 @Field(() => Int)
 age: number;

 @Field()
 breed: string;
}

@Mutation(() => Cat)
async createCat(@Args('input') input: CreateCatInput) {
 return this.catsService.create(input);
}
```

## OpenAPI/Swagger Documentation

### Basic Swagger Setup

```typescript
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
 const app = await NestFactory.create(AppModule);

 const config = new DocumentBuilder()
 .setTitle('Cats API')
 .setDescription('The cats API documentation')
 .setVersion('1.0')
 .addTag('cats')
 .addBearerAuth()
 .build();

 const documentFactory = () => SwaggerModule.createDocument(app, config);
 SwaggerModule.setup('api', app, documentFactory);

 await app.listen(3000);
}
bootstrap();
// Access at http://localhost:3000/api
```

### API Decorators

```typescript
import { ApiTags, ApiOperation, ApiResponse, ApiProperty, ApiBearerAuth } from '@nestjs/swagger';

export class CreateCatDto {
 @ApiProperty({ example: 'Fluffy', description: 'The name of the cat' })
 name: string;

 @ApiProperty({ example: 3, description: 'The age of the cat' })
 age: number;

 @ApiProperty({ example: 'Persian', description: 'The breed of the cat' })
 breed: string;
}

@ApiTags('cats')
@Controller('cats')
export class CatsController {
 @Post()
 @ApiOperation({ summary: 'Create a new cat' })
 @ApiResponse({ status: 201, description: 'The cat has been successfully created.', type: Cat })
 @ApiResponse({ status: 400, description: 'Bad Request.' })
 @ApiBearerAuth()
 async create(@Body() createCatDto: CreateCatDto) {
 return this.catsService.create(createCatDto);
 }

 @Get()
 @ApiOperation({ summary: 'Get all cats' })
 @ApiResponse({ status: 200, description: 'Return all cats.', type: [Cat] })
 async findAll() {
 return this.catsService.findAll();
 }
}
```

## Configuration

### Environment Configuration

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
 imports: [
 ConfigModule.forRoot({
 isGlobal: true,
 envFilePath: ['.env.local', '.env'],
 ignoreEnvFile: process.env.NODE_ENV === 'production',
 }),
 ],
})
export class AppModule {}

// Use in service
@Injectable()
export class AppService {
 constructor(private configService: ConfigService) {}

 getDatabaseConfig() {
 return {
 host: this.configService.get('DB_HOST'),
 port: this.configService.get('DB_PORT'),
 };
 }
}
```

### Custom Configuration Files

```typescript
export default () => ({
 port: parseInt(process.env.PORT, 10) || 3000,
 database: {
 host: process.env.DATABASE_HOST || 'localhost',
 port: parseInt(process.env.DATABASE_PORT, 10) || 5432,
 username: process.env.DATABASE_USERNAME,
 password: process.env.DATABASE_PASSWORD,
 },
 jwt: {
 secret: process.env.JWT_SECRET,
 expiresIn: '7d',
 },
});

// Import in module
import configuration from './config/configuration';

@Module({
 imports: [
 ConfigModule.forRoot({
 load: [configuration],
 }),
 ],
})
export class AppModule {}

// Access nested config
const dbHost = this.configService.get('database.host');
```

## Summary

NestJS provides a comprehensive framework for building scalable server-side applications with a focus on maintainability and testability. The framework's modular architecture, combined with dependency injection and decorators, enables developers to structure applications effectively. Core building blocks include controllers for handling HTTP requests, providers for business logic, modules for organization, and middleware for request processing. Advanced features like guards, interceptors, and pipes enable cross-cutting concerns such as authentication, logging, validation, and transformation.

The framework excels in enterprise applications through its support for microservices architecture with multiple transport layers, database integration via TypeORM and Sequelize, GraphQL API development, and comprehensive testing utilities. NestJS's decorator-based approach and TypeScript support provide excellent developer experience with type safety and IDE integration. The framework's extensibility allows integration with various libraries and tools while maintaining clean architecture principles. Whether building REST APIs, GraphQL servers, microservices, or WebSocket applications, NestJS provides the tools and patterns needed for production-ready applications with proper error handling, validation, logging, and documentation through OpenAPI/Swagger integration.