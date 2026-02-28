/**
 * NestJS Domain Module Template
 *
 * Usage: Copy this template and replace `Feature` with your domain name.
 * Example: OrderModule, UserModule, ProductModule
 */

import { Module } from '@nestjs/common';
import { FeatureController } from './feature.controller';
import { FeatureService } from './feature.service';
import { FeatureRepository } from './feature.repository';
import { DatabaseModule } from '../database/database.module';

@Module({
  imports: [DatabaseModule],
  controllers: [FeatureController],
  providers: [FeatureService, FeatureRepository],
  exports: [FeatureService],
})
export class FeatureModule {}
