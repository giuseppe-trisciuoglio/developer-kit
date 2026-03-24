# Drizzle Migrations

Database migration patterns for NestJS with Drizzle ORM.

## Generating Migrations

```bash
npx drizzle-kit generate
```

## Running Migrations

```typescript
// src/migrations/migration.service.ts
import { Injectable } from '@nestjs/common';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { DatabaseService } from '../db/database.service';

@Injectable()
export class MigrationService {
  constructor(private db: DatabaseService) {}

  async runMigrations() {
    try {
      await migrate(this.db.database, { migrationsFolder: './drizzle' });
      console.log('Migrations completed successfully');
    } catch (error) {
      console.error('Migration failed:', error);
      throw error;
    }
  }
}
```

## Migration Best Practices

1. **Always backup before migrating** - Protect production data
2. **Test migrations locally first** - Catch issues early
3. **Make migrations reversible** - Use `down` migrations when possible
4. **Keep migrations small** - Easier to debug and rollback
5. **Version control migrations** - Track schema changes in git
