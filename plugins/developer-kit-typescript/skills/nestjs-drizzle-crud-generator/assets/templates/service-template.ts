import { Injectable, NotFoundException } from '@nestjs/common';
import { Inject } from '@nestjs/common/decorators';
import { eq, isNull, and } from 'drizzle-orm';
import { DrizzleD1Database, DrizzlePgDatabase } from 'drizzle-orm/cloud';
import { {{FeatureName}}Table } from '../schema/{{featureName}}.table';
import {
  Create{{FeatureName}}Dto,
  Update{{FeatureName}}Dto,
  FindAll{{FeatureName}}QueryDto,
} from './dto/{{featureName}}.dto';

export const DrizzleProvider = Symbol('DrizzleProvider');

@Injectable()
export class {{FeatureName}}Service {
  private readonly defaultPageSize: number;
  private readonly maxPageSize: number;
  private readonly includeDeleted: boolean;

  constructor(
    @Inject(DrizzleProvider)
    private readonly db: DrizzleD1Database | DrizzlePgDatabase,
  ) {
    this.defaultPageSize = 10;
    this.maxPageSize = 100;
    this.includeDeleted = false;
  }

  async create(dto: Create{{FeatureName}}Dto): Promise<{{FeatureName}}> {
    const [created] = await this.db
      .insert({{FeatureName}}Table)
      .values(dto as any)
      .returning();
    return created as {{FeatureName}};
  }

  async findAll(
    query: FindAll{{FeatureName}}QueryDto,
  ): Promise<{ rows: {{FeatureName}}[]; total: number }> {
    const { page = 1, limit = this.defaultPageSize, ...filters } = query;
    const offset = (page - 1) * Math.min(limit, this.maxPageSize);

    const whereConditions = [];

    if (!this.includeDeleted) {
      whereConditions.push(isNull({{FeatureName}}Table.deletedAt));
    }

    // Apply filters
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== null) {
        whereConditions.push(
          // @ts-ignore - dynamic field access
          eq({{FeatureName}}Table[key], value),
        );
      }
    }

    const whereClause = and(...whereConditions);

    const [rows, countResult] = await Promise.all([
      this.db
        .select()
        .from({{FeatureName}}Table)
        .where(whereClause)
        .limit(Math.min(limit, this.maxPageSize))
        .offset(offset),
      this.db
        .select({ count: {{FeatureName}}Table.id })
        .from({{FeatureName}}Table)
        .where(whereClause),
    ]);

    const total = countResult.length;

    return {
      rows: rows as {{FeatureName}}[],
      total,
    };
  }

  async findOne(id: string): Promise<{{FeatureName}} | null> {
    const conditions = [eq({{FeatureName}}Table.id, id)];
    if (!this.includeDeleted) {
      conditions.push(isNull({{FeatureName}}Table.deletedAt));
    }

    const [result] = await this.db
      .select()
      .from({{FeatureName}}Table)
      .where(and(...conditions));

    return (result as {{FeatureName}}) || null;
  }

  async update(
    id: string,
    dto: Update{{FeatureName}}Dto,
  ): Promise<{{FeatureName}}> {
    const existing = await this.findOne(id);
    if (!existing) {
      throw new NotFoundException(`{{FeatureName}} with id ${id} not found`);
    }

    const [updated] = await this.db
      .update({{FeatureName}}Table)
      .set({ ...dto, updatedAt: new Date() } as any)
      .where(eq({{FeatureName}}Table.id, id))
      .returning();

    return updated as {{FeatureName}};
  }

  async remove(id: string): Promise<void> {
    const existing = await this.findOne(id);
    if (!existing) {
      throw new NotFoundException(`{{FeatureName}} with id ${id} not found`);
    }

    // Soft delete
    await this.db
      .update({{FeatureName}}Table)
      .set({ deletedAt: new Date() } as any)
      .where(eq({{FeatureName}}Table.id, id));
  }
}
