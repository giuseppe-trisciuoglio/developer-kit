import { Test, TestingModule } from '@nestjs/testing';
import { {{FeatureName}}Service } from './{{featureName}}.service';
import { DrizzleProvider } from './{{featureName}}.service';
import { {{FeatureName}}Table } from '../schema/{{featureName}}.table';

describe('{{FeatureName}}Service', () => {
  let service: {{FeatureName}}Service;
  let mockDb: {
    select: jest.Mock;
    insert: jest.Mock;
    update: jest.Mock;
    delete: jest.Mock;
  };

  const mock{{FeatureName}} = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    {{MockFields}}
    createdAt: new Date(),
    updatedAt: new Date(),
    deletedAt: null,
  };

  beforeEach(async () => {
    mockDb = {
      select: jest.fn().mockReturnValue({
        from: jest.fn().mockReturnValue({
          where: jest.fn().mockReturnValue({
            returning: jest.fn().mockResolvedValue([]),
            limit: jest.fn().mockReturnValue({
              offset: jest.fn().mockReturnValue({
                returning: jest.fn().mockResolvedValue([]),
              }),
            }),
          }),
        }),
      }),
      insert: jest.fn().mockReturnValue({
        values: jest.fn().mockReturnValue({
          returning: jest.fn().mockResolvedValue([mock{{FeatureName}}]),
        }),
      }),
      update: jest.fn().mockReturnValue({
        set: jest.fn().mockReturnValue({
          where: jest.fn().mockReturnValue({
            returning: jest.fn().mockResolvedValue([mock{{FeatureName}}]),
          }),
        }),
      }),
      delete: jest.fn().mockReturnValue({
        where: jest.fn().mockReturnValue({
          returning: jest.fn().mockResolvedValue([]),
        }),
      }),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        {{FeatureName}}Service,
        {
          provide: DrizzleProvider,
          useValue: mockDb,
        },
      ],
    }).compile();

    service = module.get<{{FeatureName}}Service>({{FeatureName}}Service);
  });

  describe('create', () => {
    it('should create a new {{featureName}}', async () => {
      const dto = {{CreateDtoMock}};

      const result = await service.create(dto as any);

      expect(mockDb.insert).toHaveBeenCalled();
      expect(result).toEqual(mock{{FeatureName}});
    });
  });

  describe('findAll', () => {
    it('should return paginated results', async () => {
      const query = { page: 1, limit: 10 };

      const result = await service.findAll(query as any);

      expect(result.rows).toEqual([mock{{FeatureName}}]);
      expect(result.total).toBeGreaterThanOrEqual(0);
    });

    it('should return empty array when no results', async () => {
      mockDb.select.mockReturnValue({
        from: jest.fn().mockReturnValue({
          where: jest.fn().mockReturnValue({
            returning: jest.fn().mockResolvedValue([]),
            limit: jest.fn().mockReturnValue({
              offset: jest.fn().mockReturnValue({
                returning: jest.fn().mockResolvedValue([]),
              }),
            }),
          }),
        }),
      });

      const query = { page: 1, limit: 10 };
      const result = await service.findAll(query as any);

      expect(result.rows).toEqual([]);
      expect(result.total).toBe(0);
    });
  });

  describe('findOne', () => {
    it('should return a {{featureName}} by id', async () => {
      const result = await service.findOne(mock{{FeatureName}}.id);

      expect(result).toEqual(mock{{FeatureName}});
    });

    it('should return null for non-existent id', async () => {
      mockDb.select.mockReturnValue({
        from: jest.fn().mockReturnValue({
          where: jest.fn().mockReturnValue({
            returning: jest.fn().mockResolvedValue([]),
          }),
        }),
      });

      const result = await service.findOne('non-existent-id');

      expect(result).toBeNull();
    });
  });

  describe('update', () => {
    it('should update a {{featureName}}', async () => {
      const dto = {{UpdateDtoMock}};

      const result = await service.update(mock{{FeatureName}}.id, dto as any);

      expect(mockDb.update).toHaveBeenCalled();
      expect(result).toEqual(mock{{FeatureName}});
    });

    it('should throw NotFoundException for non-existent id', async () => {
      mockDb.select.mockReturnValue({
        from: jest.fn().mockReturnValue({
          where: jest.fn().mockReturnValue({
            returning: jest.fn().mockResolvedValue([]),
          }),
        }),
      });

      await expect(
        service.update('non-existent-id', {} as any),
      ).rejects.toThrow('not found');
    });
  });

  describe('remove', () => {
    it('should soft delete a {{featureName}}', async () => {
      await service.remove(mock{{FeatureName}}.id);

      expect(mockDb.update).toHaveBeenCalled();
    });

    it('should throw NotFoundException for non-existent id', async () => {
      mockDb.select.mockReturnValue({
        from: jest.fn().mockReturnValue({
          where: jest.fn().mockReturnValue({
            returning: jest.fn().mockResolvedValue([]),
          }),
        }),
      });

      await expect(service.remove('non-existent-id')).rejects.toThrow(
        'not found',
      );
    });
  });
});
