import { z } from 'zod';
import { createZodDto } from 'nestjs-zod/dto';

export const Create{{FeatureName}}Schema = z.object({
{{CreateFields}}
}).strict();

export const Update{{FeatureName}}Schema = Create{{FeatureName}}Schema.partial();

export const FindAll{{FeatureName}}QuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(10),
{{FilterFields}}
}).strict();

export type Create{{FeatureName}}Dto = z.infer<typeof Create{{FeatureName}}Schema>;
export type Update{{FeatureName}}Dto = z.infer<typeof Update{{FeatureName}}Schema>;
export type FindAll{{FeatureName}}QueryDto = z.infer<typeof FindAll{{FeatureName}}QuerySchema>;

export class Create{{FeatureName}}Dto extends createZodDto(Create{{FeatureName}}Schema) {}
export class Update{{FeatureName}}Dto extends createZodDto(Update{{FeatureName}}Schema) {}
export class FindAll{{FeatureName}}QueryDto extends createZodDto(FindAll{{FeatureName}}QuerySchema) {}
