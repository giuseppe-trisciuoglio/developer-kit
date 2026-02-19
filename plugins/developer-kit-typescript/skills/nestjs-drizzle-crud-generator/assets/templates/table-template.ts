import { pgTable, text, timestamp, uuid, boolean, integer, real } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const {{FeatureName}}Table = pgTable('{{tableName}}', {
  id: uuid('id').primaryKey().defaultRandom(),
{{TableFields}}{{TableFieldsSuffix}}
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  deletedAt: timestamp('deleted_at'),
});

export const {{FeatureName}}Relations = relations({{FeatureName}}Table, ({ many }) => ({
{{RelationFields}}
}));

export type {{FeatureName}} = typeof {{FeatureName}}Table.$inferSelect;
export type New{{FeatureName}} = typeof {{FeatureName}}Table.$inferInsert;
