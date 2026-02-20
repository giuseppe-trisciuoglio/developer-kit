import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  Patch,
  Post,
  Query,
} from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { ZodCustomPipe } from '@your-org/server-utils';

import { {{FeatureName}}Service } from './{{featureName}}.service';
import {
  Create{{FeatureName}}Dto,
  Create{{FeatureName}}Schema,
  Update{{FeatureName}}Dto,
  Update{{FeatureName}}Schema,
  FindAll{{FeatureName}}QueryDto,
  FindAll{{FeatureName}}QuerySchema,
} from './dto/{{featureName}}.dto';

@ApiTags('{{featureName}}')
@Controller('{{featureName}}')
export class {{FeatureName}}Controller {
  constructor(private readonly service: {{FeatureName}}Service) {}

  @Post()
  async create(
    @Body(new ZodCustomPipe(Create{{FeatureName}}Schema))
    dto: Create{{FeatureName}}Dto,
  ) {
    return this.service.create(dto);
  }

  @Get()
  async findAll(
    @Query(new ZodCustomPipe(FindAll{{FeatureName}}QuerySchema))
    query: FindAll{{FeatureName}}QueryDto,
  ) {
    return this.service.findAll(query);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.service.findOne(id);
  }

  @Patch(':id')
  async update(
    @Param('id') id: string,
    @Body(new ZodCustomPipe(Update{{FeatureName}}Schema))
    dto: Update{{FeatureName}}Dto,
  ) {
    return this.service.update(id, dto);
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    return this.service.remove(id);
  }
}
