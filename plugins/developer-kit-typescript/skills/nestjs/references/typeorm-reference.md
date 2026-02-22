# TypeORM Reference

This reference documents TypeORM integration with NestJS. For Drizzle ORM patterns, see [drizzle-reference.md](drizzle-reference.md).

## TypeORM Setup

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

## Entity Definition

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

## Repository Pattern

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
  ) {}

  async findAll(): Promise<User[]> {
    return this.usersRepository.find({ relations: ['photos'] });
  }

  async findOne(id: string): Promise<User> {
    const user = await this.usersRepository.findOne({
      where: { id },
      relations: ['photos'],
    });
    if (!user) throw new NotFoundException('User not found');
    return user;
  }

  async create(userData: CreateUserDto): Promise<User> {
    const user = this.usersRepository.create(userData);
    return this.usersRepository.save(user);
  }

  async update(id: string, updateData: UpdateUserDto): Promise<User> {
    await this.usersRepository.update(id, updateData);
    return this.findOne(id);
  }

  async remove(id: string): Promise<void> {
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

## Database Transactions

```typescript
import { DataSource } from 'typeorm';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User) private usersRepository: Repository<User>,
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

## Async Configuration

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

## Testing with Repository Mocks

```typescript
describe('UsersService', () => {
  let service: UsersService;
  let repository: Repository<User>;

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
    repository = module.get(getRepositoryToken(User));
  });

  it('should find all users', async () => {
    const users = [{ id: '1', email: 'test@example.com' }];
    mockRepository.find.mockResolvedValue(users);

    expect(await service.findAll()).toEqual(users);
    expect(repository.find).toHaveBeenCalled();
  });
});
```

## Relationships

### One-to-Many / Many-to-One

```typescript
// User entity
@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @OneToMany(() => Photo, photo => photo.user)
  photos: Photo[];
}

// Photo entity
@Entity()
export class Photo {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  url: string;

  @ManyToOne(() => User, user => user.photos)
  user: User;
}
```

### Many-to-Many

```typescript
@Entity()
export class Student {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @ManyToMany(() => Course, course => course.students)
  @JoinTable()
  courses: Course[];
}

@Entity()
export class Course {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @ManyToMany(() => Student, student => student.courses)
  students: Student[];
}
```

## Query Builder Examples

```typescript
// Basic query builder
const users = await this.dataSource
  .getRepository(User)
  .createQueryBuilder('user')
  .where('user.isActive = :isActive', { isActive: true })
  .leftJoinAndSelect('user.photos', 'photo')
  .orderBy('user.createdAt', 'DESC')
  .skip(0)
  .take(10)
  .getMany();

// Join with relations
const userWithPhotos = await this.dataSource
  .getRepository(User)
  .findOne({
    where: { id: userId },
    relations: ['photos', 'posts'],
  });
```

## Best Practices

1. Use `synchronize: true` only in development
2. Always use transactions for multi-table operations
3. Use repository pattern for better testability
4. Define proper indexes on frequently queried columns
5. Use lazy loading sparingly - prefer eager loading with `relations`
6. Keep entities simple and let services handle business logic
