/**
 * NestJS Controller Template
 *
 * Usage: Copy this template and replace `Feature` with your domain name.
 * Implements standard REST endpoints with proper validation and response types.
 */

import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Param,
  Body,
  ParseUUIDPipe,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { FeatureService } from './feature.service';
import { CreateFeatureDto } from './dto/create-feature.dto';
import { UpdateFeatureDto } from './dto/update-feature.dto';
import { FeatureResponseDto } from './dto/feature-response.dto';

@Controller('features')
export class FeatureController {
  constructor(private readonly featureService: FeatureService) {}

  @Get()
  async findAll(): Promise<FeatureResponseDto[]> {
    return this.featureService.findAll();
  }

  @Get(':id')
  async findById(
    @Param('id', ParseUUIDPipe) id: string,
  ): Promise<FeatureResponseDto> {
    return this.featureService.findById(id);
  }

  @Post()
  async create(@Body() dto: CreateFeatureDto): Promise<FeatureResponseDto> {
    return this.featureService.create(dto);
  }

  @Patch(':id')
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateFeatureDto,
  ): Promise<FeatureResponseDto> {
    return this.featureService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  async delete(@Param('id', ParseUUIDPipe) id: string): Promise<void> {
    return this.featureService.delete(id);
  }
}
