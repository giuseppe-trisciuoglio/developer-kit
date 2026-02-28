/**
 * NestJS Service Template
 *
 * Usage: Copy this template and replace `Feature` with your domain name.
 * Implements standard CRUD operations with proper error handling.
 */

import { Injectable, Logger } from '@nestjs/common';
import { FeatureRepository } from './feature.repository';
import { CreateFeatureDto } from './dto/create-feature.dto';
import { UpdateFeatureDto } from './dto/update-feature.dto';
import { FeatureNotFoundException } from './exceptions/feature-not-found.exception';

@Injectable()
export class FeatureService {
  private readonly logger = new Logger(FeatureService.name);

  constructor(private readonly featureRepository: FeatureRepository) {}

  async findAll(): Promise<Feature[]> {
    return this.featureRepository.findAll();
  }

  async findById(id: string): Promise<Feature> {
    const feature = await this.featureRepository.findById(id);

    if (feature === null) {
      throw new FeatureNotFoundException(id);
    }

    return feature;
  }

  async create(dto: CreateFeatureDto): Promise<Feature> {
    this.logger.log(`Creating feature with id: ${dto.constructor.name}`); // Avoid logging full DTOs — may contain PII
    return this.featureRepository.save(dto);
  }

  async update(id: string, dto: UpdateFeatureDto): Promise<Feature> {
    await this.findById(id); // Throws if not found
    return this.featureRepository.update(id, dto);
  }

  async delete(id: string): Promise<void> {
    await this.findById(id); // Throws if not found
    await this.featureRepository.delete(id);
  }
}
