import { DynamicModule, Module } from '@nestjs/common';
import { AsyncFeatureModuleOptions } from '@nestjs/common/interfaces/features/async-options.interface';
import { DatabaseModule } from '@your-org/server-database';

import { {{FeatureName}}Controller } from './controllers';
import { {{FeatureName}}Service } from './services';
import { {{FeatureName}}Table } from './schema';

export const FEATURE_OPTIONS = '{{featureName}}.feature-options';

export interface {{FeatureName}}FeatureOptions {
  defaultPageSize?: number;
  maxPageSize?: number;
  includeDeleted?: boolean;
}

export type Async{{FeatureName}}ModuleOptions = AsyncFeatureModuleOptions<{{FeatureName}}FeatureOptions>;

@Module({})
export class {{FeatureName}}FeatureModule {
  static forRootAsync(options: Async{{FeatureName}}ModuleOptions): DynamicModule {
    return {
      global: true,
      module: {{FeatureName}}FeatureModule,
      imports: [DatabaseModule.forFeature([{{FeatureName}}Table])],
      controllers: [{{FeatureName}}Controller],
      providers: [
        {
          provide: FEATURE_OPTIONS,
          useFactory: options.useFactory,
          inject: options.inject,
        },
        {{FeatureName}}Service,
      ],
      exports: [{{FeatureName}}Service],
    };
  }
}
