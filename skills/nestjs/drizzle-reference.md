### Install Drizzle and Gel Packages

Source: https://orm.drizzle.team/docs/get-started/gel-new

Installs the necessary Drizzle ORM and Gel packages, along with development dependencies like Drizzle Kit and tsx.

```bash
npm i drizzle-orm gel
npm i -D drizzle-kit tsx
```

```bash
yarn add drizzle-orm gel
yarn add -D drizzle-kit tsx
```

```bash
pnpm add drizzle-orm gel
pnpm add -D drizzle-kit tsx
```

```bash
bun add drizzle-orm gel
bun add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Drizzle Kit with bun

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Installs Drizzle ORM and Drizzle Kit using the Bun runtime's package manager, including types for Bun.

```bash
bun add drizzle-orm
bun add -D drizzle-kit @types/bun
```

--------------------------------

### Install Drizzle ORM and Drizzle Kit with npm

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Installs the necessary Drizzle ORM package for database operations and Drizzle Kit for schema management and migrations using npm.

```bash
npm i drizzle-orm
npm i -D drizzle-kit @types/bun
```

--------------------------------

### Install Drizzle ORM and Drizzle Kit with yarn

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Installs the Drizzle ORM and Drizzle Kit packages using yarn, including the types for Bun.

```bash
yarn add drizzle-orm
yarn add -D drizzle-kit @types/bun
```

--------------------------------

### Install Drizzle Packages with bun

Source: https://orm.drizzle.team/docs/get-started/planetscale-new

Installs the necessary Drizzle ORM packages, the PlanetScale database driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
bun add drizzle-orm @planetscale/database dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Drizzle Kit with pnpm

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Installs Drizzle ORM and Drizzle Kit, along with Bun types, using the pnpm package manager.

```bash
pnpm add drizzle-orm
pnpm add -D drizzle-kit @types/bun
```

--------------------------------

### Install Drizzle Packages with pnpm

Source: https://orm.drizzle.team/docs/get-started/planetscale-new

Installs the necessary Drizzle ORM packages, the PlanetScale database driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
pnpm add drizzle-orm @planetscale/database dotenv
pnpm add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle Packages with npm

Source: https://orm.drizzle.team/docs/get-started/planetscale-new

Installs the necessary Drizzle ORM packages, the PlanetScale database driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
npm i drizzle-orm @planetscale/database dotenv
npm i -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and SQLite Cloud Driver (bun)

Source: https://orm.drizzle.team/docs/get-started/sqlite-cloud-new

Installs the necessary Drizzle ORM beta package, the SQLite Cloud driver, dotenv for environment variables, and Drizzle Kit with tsx for development using bun.

```bash
bun add drizzle-orm@beta @sqlitecloud/drivers dotenv
bun add -D drizzle-kit@beta tsx
```

--------------------------------

### Install Drizzle ORM and Supabase Dependencies (bun)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Installs the necessary Drizzle ORM, postgres driver, dotenv for environment variables, and development tools like drizzle-kit and tsx using bun.

```bash
bun add drizzle-orm postgres dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle Packages with yarn

Source: https://orm.drizzle.team/docs/get-started/planetscale-new

Installs the necessary Drizzle ORM packages, the PlanetScale database driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
yarn add drizzle-orm @planetscale/database dotenv
yarn add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and SQLite Cloud Driver (npm)

Source: https://orm.drizzle.team/docs/get-started/sqlite-cloud-new

Installs the necessary Drizzle ORM beta package, the SQLite Cloud driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
npm i drizzle-orm@beta @sqlitecloud/drivers dotenv
npm i -D drizzle-kit@beta tsx
```

--------------------------------

### Database Connection Setup (Basic)

Source: https://orm.drizzle.team/docs/get-started/postgresql-new

Initializes Drizzle ORM with a PostgreSQL connection using the DATABASE_URL from environment variables and the node-postgres driver.

```typescript
import 'dotenv/config';
import { drizzle } from 'drizzle-orm/node-postgres';

const db = drizzle(process.env.DATABASE_URL!);
```

--------------------------------

### Install Drizzle ORM and Supabase Dependencies (pnpm)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Installs the necessary Drizzle ORM, postgres driver, dotenv for environment variables, and development tools like drizzle-kit and tsx using pnpm.

```bash
pnpm add drizzle-orm postgres dotenv
pnpm add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Supabase Dependencies (npm)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Installs the necessary Drizzle ORM, postgres driver, dotenv for environment variables, and development tools like drizzle-kit and tsx using npm.

```bash
npm i drizzle-orm postgres dotenv
npm i -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and SQLite Cloud Driver (pnpm)

Source: https://orm.drizzle.team/docs/get-started/sqlite-cloud-new

Installs the necessary Drizzle ORM beta package, the SQLite Cloud driver, dotenv for environment variables, and Drizzle Kit with tsx for development using pnpm.

```bash
pnpm add drizzle-orm@beta @sqlitecloud/drivers dotenv
pnpm add -D drizzle-kit@beta tsx
```

--------------------------------

### Install Drizzle ORM and SQLite Cloud Driver (yarn)

Source: https://orm.drizzle.team/docs/get-started/sqlite-cloud-new

Installs the necessary Drizzle ORM beta package, the SQLite Cloud driver, dotenv for environment variables, and Drizzle Kit with tsx for development using yarn.

```bash
yarn add drizzle-orm@beta @sqlitecloud/drivers dotenv
yarn add -D drizzle-kit@beta tsx
```

--------------------------------

### Install Drizzle Packages (bun)

Source: https://orm.drizzle.team/docs/get-started/vercel-new

Installs the necessary Drizzle ORM packages and development tools using bun. This includes the core Drizzle ORM library, the Vercel Postgres driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
bun add drizzle-orm @vercel/postgres dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Supabase Dependencies (yarn)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Installs the necessary Drizzle ORM, postgres driver, dotenv for environment variables, and development tools like drizzle-kit and tsx using yarn.

```bash
yarn add drizzle-orm postgres dotenv
yarn add -D drizzle-kit tsx
```

--------------------------------

### Initialize Gel Project

Source: https://orm.drizzle.team/docs/get-started/gel-new

Initializes a new Gel project. This command is used to set up the basic structure for a Gel database project.

```bash
npx gel project init
```

```bash
yarn gel project init
```

```bash
pnpm gel project init
```

```bash
bunx gel project init
```

--------------------------------

### Install Drizzle ORM and TiDB Serverless Packages (bun)

Source: https://orm.drizzle.team/docs/connect-tidb

Installs the necessary Drizzle ORM and TiDB Serverless packages using bun. It also installs drizzle-kit as a development dependency for schema management and migrations.

```bash
bun add drizzle-orm @tidbcloud/serverless
bun add -D drizzle-kit
```

--------------------------------

### PostgreSQL Connection URL Example

Source: https://orm.drizzle.team/docs/guides/postgresql-local-setup

This is the standard format for a PostgreSQL database connection URL. Replace the placeholders with your specific credentials and host information.

```sql
postgres://:@:/
```

```sql
postgres://postgres:mypassword@localhost:5432/postgres
```

--------------------------------

### Drizzle Kit Configuration for PostgreSQL

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Configuration file for Drizzle Kit, specifying the output directory for migrations, the schema file location, the database dialect (PostgreSQL), and database credentials.

```typescript
import 'dotenv/config';
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
 out: './drizzle',
 schema: './src/db/schema.ts',
 dialect: 'postgresql',
 dbCredentials: {
 url: process.env.DATABASE_URL!,
 },
});
```

--------------------------------

### Install Drizzle ORM and Drizzle Kit Packages

Source: https://orm.drizzle.team/docs/connect-cloudflare-d1

Installs the necessary Drizzle ORM and Drizzle Kit packages for project setup. Drizzle ORM is used for database interactions, while Drizzle Kit provides tooling for schema management and migrations.

```npm
npm i drizzle-orm
npm i -D drizzle-kit
```

```yarn
yarn add drizzle-orm
yarn add -D drizzle-kit
```

```pnpm
pnpm add drizzle-orm
pnpm add -D drizzle-kit
```

```bun
bun add drizzle-orm
bun add -D drizzle-kit
```

--------------------------------

### Configure MySQL Database URL

Source: https://orm.drizzle.team/docs/guides/mysql-local-setup

This is the standard format for a MySQL connection URL. Replace the placeholders with your specific credentials and host information. The example provided shows how to construct the URL for the previously started Docker container.

```plaintext
mysql://:@:/
```

```plaintext
mysql://root:mypassword@localhost:3306/mysql
```

--------------------------------

### Database Connection Setup (with Config)

Source: https://orm.drizzle.team/docs/get-started/postgresql-new

Initializes Drizzle ORM with a PostgreSQL connection, passing specific node-postgres connection options like SSL configuration.

```typescript
import 'dotenv/config';
import { drizzle } from 'drizzle-orm/node-postgres';

// You can specify any property from the node-postgres connection options
const db = drizzle({
 connection: {
 connectionString: process.env.DATABASE_URL!,
 ssl: true
 }
});
```

--------------------------------

### Install Drizzle ORM and Drizzle Kit with npm/yarn/pnpm/bun

Source: https://orm.drizzle.team/docs/get-started/bun-sqlite-new

Commands to install Drizzle ORM and Drizzle Kit, essential for ORM functionality and schema management. Drizzle Kit requires @types/bun for TypeScript projects.

```npm
npm i drizzle-orm
npm i -D drizzle-kit @types/bun
```

```yarn
yarn add drizzle-orm
yarn add -D drizzle-kit @types/bun
```

```pnpm
pnpm add drizzle-orm
pnpm add -D drizzle-kit @types/bun
```

```bun
bun add drizzle-orm
bun add -D drizzle-kit @types/bun
```

--------------------------------

### Run Docker Container with User and Database

Source: https://orm.drizzle.team/docs/guides/postgresql-local-setup

This shows how to start a PostgreSQL container with a specific user and database name. If not provided, default values are used.

```bash
docker run --name drizzle-postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -d -p 5432:5432 postgres
```

--------------------------------

### Install Drizzle Packages (npm)

Source: https://orm.drizzle.team/docs/get-started/vercel-new

Installs the necessary Drizzle ORM packages and development tools using npm. This includes the core Drizzle ORM library, the Vercel Postgres driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
npm i drizzle-orm @vercel/postgres dotenv
npm i -D drizzle-kit tsx
```

--------------------------------

### Project File Structure for Drizzle ORM

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Basic file structure for a Drizzle ORM project using Bun SQL. It shows the location of schema definitions, migration files, configuration files, and environment variables.

```tree
📦
 ├ 📂 drizzle
 ├ 📂 src
 │ ├ 📂 db
 │ │ └ 📜 schema.ts
 │ └ 📜 index.ts
 ├ 📜 .env
 ├ 📜 drizzle.config.ts
 ├ 📜 package.json
 └ 📜 tsconfig.json
```

--------------------------------

### Install Drizzle ORM and MySQL2 Dependencies (npm)

Source: https://orm.drizzle.team/docs/get-started/mysql-new

Installs the necessary Drizzle ORM packages, the mysql2 driver, dotenv for environment variables, and drizzle-kit and tsx for development.

```bash
npm i drizzle-orm mysql2 dotenv
npm i -D drizzle-kit tsx
```

--------------------------------

### Configure Drizzle Kit

Source: https://orm.drizzle.team/docs/get-started/gel-new

Sets up the Drizzle Kit configuration file. This TypeScript file specifies the database dialect and other project-specific settings for Drizzle Kit.

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
 dialect: 'gel',
});
```

--------------------------------

### Install Drizzle ORM and MySQL2 Dependencies (bun)

Source: https://orm.drizzle.team/docs/get-started/mysql-new

Installs the necessary Drizzle ORM packages, the mysql2 driver, dotenv for environment variables, and drizzle-kit and tsx for development using Bun.

```bash
bun add drizzle-orm mysql2 dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle Packages (pnpm)

Source: https://orm.drizzle.team/docs/get-started/vercel-new

Installs the necessary Drizzle ORM packages and development tools using pnpm. This includes the core Drizzle ORM library, the Vercel Postgres driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
pnpm add drizzle-orm @vercel/postgres dotenv
pnpm add -D drizzle-kit tsx
```

--------------------------------

### Setup SQLite Cloud Connection String

Source: https://orm.drizzle.team/docs/get-started/sqlite-cloud-new

Defines the environment variable for the SQLite Cloud database connection string in the .env file.

```dotenv
SQLITE_CLOUD_CONNECTION_STRING=
```

--------------------------------

### Install Drizzle ORM and Dependencies (bun)

Source: https://orm.drizzle.team/docs/get-started/turso-database-new

Installs the essential Drizzle ORM packages and development tools using bun. This command includes the beta versions of `drizzle-orm` and `drizzle-kit`, as well as `@tursodatabase/database`, `dotenv`, and `tsx` for the project.

```bash
bun add drizzle-orm@beta @tursodatabase/database dotenv
bun add -D drizzle-kit@beta tsx
```

--------------------------------

### Install Drizzle ORM and Dependencies (bun)

Source: https://orm.drizzle.team/docs/get-started/d1-new

Installs the necessary Drizzle ORM packages and development tools using bun. `drizzle-orm` and `dotenv` are for runtime, while `drizzle-kit` and `tsx` are for development.

```bash
bun add drizzle-orm dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Neon Packages (bun)

Source: https://orm.drizzle.team/docs/get-started/neon-new

Installs the core Drizzle ORM package, the Neon serverless driver, dotenv for environment variables, and development tools like Drizzle Kit and tsx using bun.

```bash
bun add drizzle-orm @neondatabase/serverless dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Configure Drizzle Kit

Source: https://orm.drizzle.team/docs/get-started/sqlite-cloud-new

Sets up the Drizzle Kit configuration file, specifying the migration output directory, schema file location, dialect, and database credentials.

```typescript
import 'dotenv/config';
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
 out: './drizzle',
 schema: './src/db/schema.ts',
 dialect: 'sqlite',
 dbCredentials: {
 url: process.env.SQLITE_CLOUD_CONNECTION_STRING!,
 },
});
```

--------------------------------

### Database Connection Setup (using Pool)

Source: https://orm.drizzle.team/docs/get-started/postgresql-new

Initializes Drizzle ORM with a PostgreSQL connection managed by a node-postgres Pool, allowing for connection pooling.

```typescript
import 'dotenv/config';
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

const pool = new Pool({
 connectionString: process.env.DATABASE_URL!,
});
const db = drizzle({ client: pool });
```

--------------------------------

### Install Drizzle ORM and Neon Serverless Driver (bun)

Source: https://orm.drizzle.team/docs/connect-neon

Installs the Drizzle ORM and the Neon serverless driver using bun. Also installs drizzle-kit as a development dependency.

```bash
bun add drizzle-orm @neondatabase/serverless
bun add -D drizzle-kit
```

--------------------------------

### Install Drizzle Packages (yarn)

Source: https://orm.drizzle.team/docs/get-started/vercel-new

Installs the necessary Drizzle ORM packages and development tools using yarn. This includes the core Drizzle ORM library, the Vercel Postgres driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
yarn add drizzle-orm @vercel/postgres dotenv
yarn add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Neon Serverless Driver (npm)

Source: https://orm.drizzle.team/docs/connect-neon

Installs the Drizzle ORM and the Neon serverless driver using npm. Also installs drizzle-kit as a development dependency.

```bash
npm i drizzle-orm @neondatabase/serverless
npm i -D drizzle-kit
```

--------------------------------

### Install Drizzle ORM and MySQL2 Dependencies (pnpm)

Source: https://orm.drizzle.team/docs/get-started/mysql-new

Installs the necessary Drizzle ORM packages, the mysql2 driver, dotenv for environment variables, and drizzle-kit and tsx for development using pnpm.

```bash
pnpm add drizzle-orm mysql2 dotenv
pnpm add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Dependencies (npm)

Source: https://orm.drizzle.team/docs/get-started/turso-database-new

Installs the necessary Drizzle ORM packages and development tools using npm. It includes the beta versions of `drizzle-orm` and `drizzle-kit`, along with `@tursodatabase/database`, `dotenv`, and `tsx` for development.

```bash
npm i drizzle-orm@beta @tursodatabase/database dotenv
npm i -D drizzle-kit@beta tsx
```

--------------------------------

### Install Drizzle ORM and TiDB Serverless Packages (npm)

Source: https://orm.drizzle.team/docs/connect-tidb

Installs the necessary Drizzle ORM and TiDB Serverless packages using npm. It also installs drizzle-kit as a development dependency for schema management and migrations.

```bash
npm i drizzle-orm @tidbcloud/serverless
npm i -D drizzle-kit
```

--------------------------------

### Seeding and Querying Database with Drizzle ORM (TypeScript)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Demonstrates how to interact with a PostgreSQL database using Drizzle ORM in TypeScript. It includes operations for inserting a new user, selecting all users, updating a user's age, and deleting a user. This example assumes a `usersTable` schema and uses environment variables for database connection.

```typescript
import 'dotenv/config';
import { drizzle } from 'drizzle-orm/postgres-js';
import { eq } from 'drizzle-orm';
import { usersTable } from './db/schema';

const db = drizzle(process.env.DATABASE_URL!);

async function main() {
 const user: typeof usersTable.$inferInsert = {
 name: 'John',
 age: 30,
 email: 'john@example.com',
 };

 await db.insert(usersTable).values(user);
 console.log('New user created!')

 const users = await db.select().from(usersTable);
 console.log('Getting all users from the database: ', users)
 /*
 const users: {
 id: number;
 name: string;
 age: number;
 email: string;
 }[]
 */

 await db
 .update(usersTable)
 .set({
 age: 31,
 })
 .where(eq(usersTable.email, user.email));
 console.log('User info updated!')

 await db.delete(usersTable).where(eq(usersTable.email, user.email));
 console.log('User deleted!')
}

main();
```

--------------------------------

### Install Drizzle ORM and SQLite Packages (bun)

Source: https://orm.drizzle.team/docs/get-started/sqlite-new

Installs the necessary Drizzle ORM, libsql client, dotenv, and development packages using bun. This command is for setting up a new project or adding dependencies to an existing one.

```bash
bun add drizzle-orm @libsql/client dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Manage Gel Migrations

Source: https://orm.drizzle.team/docs/get-started/gel-new

Commands to manage Gel database migrations. 'migration create' generates a migration file, and 'migration apply' applies pending migrations to the database.

```bash
gel migration create
```

```bash
gel migration apply
```

--------------------------------

### Initialize Drizzle ORM with Bun SQL

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Initializes the Drizzle ORM instance using the connection URL from the environment variables for Bun SQL.

```typescript
import 'dotenv/config';
import { drizzle } from 'drizzle-orm/bun-sql';

const db = drizzle(process.env.DATABASE_URL!);
```

--------------------------------

### Install Drizzle ORM and TiDB Serverless Packages (pnpm)

Source: https://orm.drizzle.team/docs/connect-tidb

Installs the necessary Drizzle ORM and TiDB Serverless packages using pnpm. It also installs drizzle-kit as a development dependency for schema management and migrations.

```bash
pnpm add drizzle-orm @tidbcloud/serverless
pnpm add -D drizzle-kit
```

--------------------------------

### Install Drizzle and PGlite Packages (npm, yarn, pnpm, bun)

Source: https://orm.drizzle.team/docs/get-started/pglite-new

Provides commands to install the necessary Drizzle ORM packages, the PGlite driver, dotenv for environment variables, and Drizzle Kit with tsx for development.

```bash
npm i drizzle-orm @electric-sql/pglite dotenv
npm i -D drizzle-kit tsx
```

```bash
yarn add drizzle-orm @electric-sql/pglite dotenv
yarn add -D drizzle-kit tsx
```

```bash
pnpm add drizzle-orm @electric-sql/pglite dotenv
pnpm add -D drizzle-kit tsx
```

```bash
bun add drizzle-orm @electric-sql/pglite dotenv
bun add -D drizzle-kit tsx
```

--------------------------------

### Initialize Drizzle ORM Connection (Async)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Initializes an asynchronous Drizzle ORM connection using the 'postgres-js' driver and the DATABASE_URL from environment variables.

```typescript
import { drizzle } from 'drizzle-orm'

async function main() {
 const db = drizzle('postgres-js', process.env.DATABASE_URL);
}

main();
```

--------------------------------

### Generate and Apply Database Migrations with drizzle-kit

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Generates SQL migration files based on schema changes and then applies these migrations to the database. This process is managed via separate commands.

```bash
npx drizzle-kit generate
```

```bash
npx drizzle-kit migrate
```

--------------------------------

### Install Drizzle ORM and MySQL2 Dependencies (yarn)

Source: https://orm.drizzle.team/docs/get-started/mysql-new

Installs the necessary Drizzle ORM packages, the mysql2 driver, dotenv for environment variables, and drizzle-kit and tsx for development using Yarn.

```bash
yarn add drizzle-orm mysql2 dotenv
yarn add -D drizzle-kit tsx
```

--------------------------------

### List Docker Images

Source: https://orm.drizzle.team/docs/guides/postgresql-local-setup

After pulling an image, this command lists all downloaded Docker images on your system, allowing you to verify the PostgreSQL image and its details.

```bash
docker images
```

--------------------------------

### Turso CLI: Authenticate and Create Database

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-turso

Commands to authenticate with the Turso service and create a new database. Requires Turso CLI installation. The database name 'drizzle-turso-db' is used as an example.

```bash
turso auth signup
turso auth login
turso db create drizzle-turso-db
turso db show drizzle-turso-db
turso db tokens create drizzle-turso-db
```

--------------------------------

### Install Drizzle ORM and Neon Packages (npm)

Source: https://orm.drizzle.team/docs/get-started/neon-new

Installs the core Drizzle ORM package, the Neon serverless driver, dotenv for environment variables, and development tools like Drizzle Kit and tsx using npm.

```bash
npm i drizzle-orm @neondatabase/serverless dotenv
npm i -D drizzle-kit tsx
```

--------------------------------

### Start Netlify Development Server

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-netlify-edge-functions-neon

Launches the Netlify dev server for local testing of edge functions and site deployment. This command allows for simulating the Netlify environment locally.

```bash
netlify dev
```

--------------------------------

### Install Drizzle ORM and Neon Serverless Driver (pnpm)

Source: https://orm.drizzle.team/docs/connect-neon

Installs the Drizzle ORM and the Neon serverless driver using pnpm. Also installs drizzle-kit as a development dependency.

```bash
pnpm add drizzle-orm @neondatabase/serverless
pnpm add -D drizzle-kit
```

--------------------------------

### SQL Generated Migration File Example

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-turso

An example of a SQL file generated by Drizzle Kit for database migrations. It includes CREATE TABLE statements for 'posts' and 'users', defining their columns, constraints, foreign keys, and unique indexes.

```sql
CREATE TABLE `posts` (
 `id` integer PRIMARY KEY NOT NULL,
 `title` text NOT NULL,
 `content` text NOT NULL,
 `user_id` integer NOT NULL,
 `created_at` text DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
 `updated_at` integer,
 FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `users` (
 `id` integer PRIMARY KEY NOT NULL,
 `name` text NOT NULL,
 `age` integer NOT NULL,
 `email` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `users_email_unique` ON `users` (`email`);
```

--------------------------------

### Run TypeScript Script with Bun

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Executes a TypeScript file using the Bun runtime environment. This command is used to run the main application script after setting up database operations.

```bash
bun src/index.ts
```

--------------------------------

### Initialize New Netlify Project

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-netlify-edge-functions-neon

Initializes a new Netlify project using the Netlify CLI. This command guides the user through setting up a new site and choosing deployment options.

```bash
netlify init
```

--------------------------------

### Install Drizzle ORM and Neon Packages (pnpm)

Source: https://orm.drizzle.team/docs/get-started/neon-new

Installs the core Drizzle ORM package, the Neon serverless driver, dotenv for environment variables, and development tools like Drizzle Kit and tsx using pnpm.

```bash
pnpm add drizzle-orm @neondatabase/serverless dotenv
pnpm add -D drizzle-kit tsx
```

--------------------------------

### Generated Drizzle Schema for Gel

Source: https://orm.drizzle.team/docs/get-started/gel-new

Example of a schema file generated by Drizzle Kit after pulling from a Gel database. It defines a 'users' table with UUID, smallint, and text fields.

```typescript
import { gelTable, uniqueIndex, uuid, smallint, text } from "drizzle-orm/gel-core"
import { sql } from "drizzle-orm"

export const users = gelTable("users", {
 id: uuid().default(sql`uuid_generate_v4()`).primaryKey().notNull(),
 age: smallint(),
 email: text().notNull(),
 name: text(),
}, (table) => [
 uniqueIndex("a8c6061c-f37f-11ef-9249-0d78f6c1807b;schemaconstr").using("btree", table.id.asc().nullsLast().op("uuid_ops")),
]);
```

--------------------------------

### Install Drizzle ORM and SQLite Packages (pnpm)

Source: https://orm.drizzle.team/docs/get-started/sqlite-new

Installs the necessary Drizzle ORM, libsql client, dotenv, and development packages using pnpm. This command is for setting up a new project or adding dependencies to an existing one.

```bash
pnpm add drizzle-orm @libsql/client dotenv
pnpm add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and TiDB Serverless Packages (yarn)

Source: https://orm.drizzle.team/docs/connect-tidb

Installs the necessary Drizzle ORM and TiDB Serverless packages using yarn. It also installs drizzle-kit as a development dependency for schema management and migrations.

```bash
yarn add drizzle-orm @tidbcloud/serverless
yarn add -D drizzle-kit
```

--------------------------------

### Install Drizzle ORM and Vercel Postgres Packages

Source: https://orm.drizzle.team/docs/connect-vercel-postgres

Installs the Drizzle ORM and the Vercel Postgres driver using npm, yarn, pnpm, or bun. Also installs drizzle-kit as a development dependency.

```npm
npm i drizzle-orm @vercel/postgres
npm i -D drizzle-kit
```

```yarn
yarn add drizzle-orm @vercel/postgres
yarn add -D drizzle-kit
```

```pnpm
pnpm add drizzle-orm @vercel/postgres
pnpm add -D drizzle-kit
```

```bun
bun add drizzle-orm @vercel/postgres
bun add -D drizzle-kit
```

--------------------------------

### Initialize Drizzle ORM with Bun SQL Connection Options

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Initializes Drizzle ORM with specific connection options for Bun SQL, allowing configuration of the connection object.

```typescript
import 'dotenv/config';
import { drizzle } from 'drizzle-orm/bun-sql';

// You can specify any property from the bun sql connection options
const db = drizzle({ connection: { url: process.env.DATABASE_URL! }});
```

--------------------------------

### Install Drizzle ORM and Dependencies (pnpm)

Source: https://orm.drizzle.team/docs/get-started/d1-new

Installs the necessary Drizzle ORM packages and development tools using pnpm. `drizzle-orm` and `dotenv` are for runtime, while `drizzle-kit` and `tsx` are for development.

```bash
pnpm add drizzle-orm dotenv
pnpm add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Neon Serverless Driver (yarn)

Source: https://orm.drizzle.team/docs/connect-neon

Installs the Drizzle ORM and the Neon serverless driver using yarn. Also installs drizzle-kit as a development dependency.

```bash
yarn add drizzle-orm @neondatabase/serverless
yarn add -D drizzle-kit
```

--------------------------------

### Install Drizzle ORM and SQLite Packages (npm)

Source: https://orm.drizzle.team/docs/get-started/sqlite-new

Installs the necessary Drizzle ORM, libsql client, dotenv, and development packages using npm. This command is for setting up a new project or adding dependencies to an existing one.

```bash
npm i drizzle-orm @libsql/client dotenv
npm i -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and libSQL Client Packages

Source: https://orm.drizzle.team/docs/connect-turso

Installs the necessary Drizzle ORM and libSQL client packages for different package managers. This is the first step to connect Drizzle to Turso Cloud.

```npm
npm i drizzle-orm @libsql/client
npm i -D drizzle-kit
```

```yarn
yarn add drizzle-orm @libsql/client
yarn add -D drizzle-kit
```

```pnpm
pnpm add drizzle-orm @libsql/client
pnpm add -D drizzle-kit
```

```bun
bun add drizzle-orm @libsql/client
bun add -D drizzle-kit
```

--------------------------------

### Initialize Drizzle ORM Connection (Sync)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Initializes a synchronous Drizzle ORM connection by explicitly creating a postgres client and passing it to the Drizzle instance.

```typescript
import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'

async function main() {
 const client = postgres(process.env.DATABASE_URL)
 const db = drizzle({ client });
}

main();
```

--------------------------------

### Install Drizzle ORM and Dependencies (npm)

Source: https://orm.drizzle.team/docs/get-started/d1-new

Installs the necessary Drizzle ORM packages and development tools using npm. `drizzle-orm` and `dotenv` are for runtime, while `drizzle-kit` and `tsx` are for development.

```bash
npm i drizzle-orm dotenv
npm i -D drizzle-kit tsx
```

--------------------------------

### Initialize Drizzle with SingleStore (Basic)

Source: https://orm.drizzle.team/docs/get-started/singlestore-new

Initializes Drizzle ORM with a SingleStore database connection using the DATABASE_URL from environment variables.

```typescript
import 'dotenv/config';
import { drizzle } from "drizzle-orm/singlestore";

const db = drizzle(process.env.DATABASE_URL);
```

--------------------------------

### Environment Variable Setup

Source: https://orm.drizzle.team/docs/get-started/vercel-new

Defines the database connection URL in a `.env` file. For Vercel Postgres, it's crucial to name the variable `POSTGRES_URL`. The value can be obtained from the Vercel Postgres storage tab.

```dotenv
POSTGRES_URL=
```

--------------------------------

### Database Connection URL in .env

Source: https://orm.drizzle.team/docs/get-started/bun-sql-new

Specifies the database connection string in the .env file, which Drizzle ORM will use to connect to the database.

```dotenv
DATABASE_URL=
```

--------------------------------

### Install Drizzle ORM and Dependencies (yarn)

Source: https://orm.drizzle.team/docs/get-started/d1-new

Installs the necessary Drizzle ORM packages and development tools using yarn. `drizzle-orm` and `dotenv` are for runtime, while `drizzle-kit` and `tsx` are for development.

```bash
yarn add drizzle-orm dotenv
yarn add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Neon Packages (yarn)

Source: https://orm.drizzle.team/docs/get-started/neon-new

Installs the core Drizzle ORM package, the Neon serverless driver, dotenv for environment variables, and development tools like Drizzle Kit and tsx using yarn.

```bash
yarn add drizzle-orm @neondatabase/serverless dotenv
yarn add -D drizzle-kit tsx
```

--------------------------------

### Start PostgreSQL Docker Container

Source: https://orm.drizzle.team/docs/guides/postgresql-local-setup

This command starts a new PostgreSQL container named 'drizzle-postgres'. It sets the password, runs in detached mode, and maps port 5432 from the container to the host.

```bash
docker run --name drizzle-postgres -e POSTGRES_PASSWORD=mypassword -d -p 5432:5432 postgres
```

--------------------------------

### Run TypeScript Files using tsx Command

Source: https://orm.drizzle.team/docs/get-started/gel-new

This section provides commands to execute TypeScript files using the 'tsx' tool across different package managers (npm, yarn, pnpm, bun). It's a convenient way to run scripts without a full TypeScript compilation step. Ensure 'tsx' is installed in your project.

```bash
npx tsx src/index.ts
```

```bash
yarn tsx src/index.ts
```

```bash
pnpm tsx src/index.ts
```

```bash
bunx tsx src/index.ts
```

--------------------------------

### Install Drizzle ORM and AWS SDK for PostgreSQL (bun)

Source: https://orm.drizzle.team/docs/connect-aws-data-api-pg

Installs the Drizzle ORM package and the AWS SDK client for RDS Data using bun. Also installs drizzle-kit as a development dependency for schema management.

```bash
bun add drizzle-orm @aws-sdk/client-rds-data
bun add -D drizzle-kit
```

--------------------------------

### Initialize Drizzle ORM with Existing PlanetScale Client

Source: https://orm.drizzle.team/docs/get-started/planetscale-new

Initializes the Drizzle ORM instance by providing an existing PlanetScale client instance. This allows for more control over the client configuration.

```typescript
import { drizzle } from "drizzle-orm/planetscale-serverless";
import { Client } from "@planetscale/database";

const client = new Client({
 host: process.env.DATABASE_HOST!,
 username: process.env.DATABASE_USERNAME!,
 password: process.env.DATABASE_PASSWORD!,
});

const db = drizzle({ client: client });
```

--------------------------------

### Configure Drizzle Kit for SQLite

Source: https://orm.drizzle.team/docs/get-started/bun-sqlite-new

Sets up the drizzle.config.ts file for Drizzle Kit. Specifies the output directory for migrations, schema file location, dialect (sqlite), and database credentials.

```typescript
import 'dotenv/config';
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
 out: './drizzle',
 schema: './src/db/schema.ts',
 dialect: 'sqlite',
 dbCredentials: {
 url: process.env.DB_FILE_NAME!,
 },
});
```

--------------------------------

### Install Drizzle ORM and SQLite Packages (yarn)

Source: https://orm.drizzle.team/docs/get-started/sqlite-new

Installs the necessary Drizzle ORM, libsql client, dotenv, and development packages using yarn. This command is for setting up a new project or adding dependencies to an existing one.

```bash
yarn add drizzle-orm @libsql/client dotenv
yarn add -D drizzle-kit tsx
```

--------------------------------

### Install Drizzle ORM and Dependencies (pnpm)

Source: https://orm.drizzle.team/docs/get-started/turso-database-new

Installs the necessary Drizzle ORM packages and development tools using pnpm. This command adds the beta versions of `drizzle-orm` and `drizzle-kit`, along with `@tursodatabase/database`, `dotenv`, and `tsx` to the project's dependencies.

```bash
pnpm add drizzle-orm@beta @tursodatabase/database dotenv
pnpm add -D drizzle-kit@beta tsx
```

--------------------------------

### Install Drizzle ORM and AWS SDK for PostgreSQL (npm)

Source: https://orm.drizzle.team/docs/connect-aws-data-api-pg

Installs the Drizzle ORM package and the AWS SDK client for RDS Data using npm. Also installs drizzle-kit as a development dependency for schema management.

```bash
npm i drizzle-orm @aws-sdk/client-rds-data
npm i -D drizzle-kit
```

--------------------------------

### Initialize Drizzle ORM with PlanetScale Serverless Driver

Source: https://orm.drizzle.team/docs/get-started/planetscale-new

Initializes the Drizzle ORM instance using the PlanetScale serverless driver. It reads connection details from environment variables.

```typescript
import { drizzle } from "drizzle-orm/planetscale-serverless";

const db = drizzle({ connection: {
 host: process.env.DATABASE_HOST!,
 username: process.env.DATABASE_USERNAME!,
 password: process.env.DATABASE_PASSWORD!,
}});
```

--------------------------------

### Running the Application

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-nile

This command starts the Node.js web application using `tsx`, allowing you to test the implemented API endpoints.

```bash
npx tsx src/app.ts
```

--------------------------------

### Install Drizzle ORM and PostgreSQL Dependencies (bun)

Source: https://orm.drizzle.team/docs/get-started/nile-new

Installs the core Drizzle ORM package, the 'pg' driver for PostgreSQL, 'dotenv' for environment variables, and development dependencies like 'drizzle-kit', 'tsx', and '@types/pg' using bun.

```bash
bun add drizzle-orm pg dotenv
bun add -D drizzle-kit tsx @types/pg
```

--------------------------------

### Push Migrations with Multiple Config Files (bun)

Source: https://orm.drizzle.team/docs/drizzle-kit-push

Provides examples of pushing database migrations using multiple Drizzle Kit configuration files with bun.

```bash
bunx drizzle-kit push --config=drizzle-dev.config.ts
bunx drizzle-kit push --config=drizzle-prod.config.ts
```

--------------------------------

### PlanetScale Database Connection Variables

Source: https://orm.drizzle.team/docs/get-started/planetscale-new

Defines the environment variables required to connect to the PlanetScale database. These include the host, username, and password.

```env
DATABASE_HOST=
DATABASE_USERNAME=
DATABASE_PASSWORD=
```

--------------------------------

### Drizzle ORM Configuration Example (TypeScript)

Source: https://orm.drizzle.team/docs/drizzle-kit-migrate

Provides an example TypeScript configuration file for Drizzle ORM. It specifies the database dialect, schema location, credentials, and migration table/schema settings. This file is essential for defining your database connection and migration strategy.

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
 dialect: "postgresql",
 schema: "./src/schema.ts",
 dbCredentials: {
 url: "postgresql://user:password@host:port/dbname"
 },
 migrations: {
 table: 'journal',
 schema: 'drizzle',
 },
});
```

--------------------------------

### Install Drizzle ORM and Dependencies (yarn)

Source: https://orm.drizzle.team/docs/get-started/turso-database-new

Installs the required Drizzle ORM packages and development tools using yarn. This command ensures that the beta versions of `drizzle-orm` and `drizzle-kit`, along with `@tursodatabase/database`, `dotenv`, and `tsx`, are included in the project dependencies.

```bash
yarn add drizzle-orm@beta @tursodatabase/database dotenv
yarn add -D drizzle-kit@beta tsx
```

--------------------------------

### Example SQL Migration File for Drizzle ORM

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-neon

Illustrates the structure of a SQL migration file generated by Drizzle Kit. This example shows the creation of two tables, 'posts_table' and 'users_table', including primary keys, constraints, and foreign key relationships.

```sql
CREATE TABLE IF NOT EXISTS "posts_table" (
 "id" serial PRIMARY KEY NOT NULL,
 "title" text NOT NULL,
 "content" text NOT NULL,
 "user_id" integer NOT NULL,
 "created_at" timestamp DEFAULT now() NOT NULL,
 "updated_at" timestamp NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "users_table" (
 "id" serial PRIMARY KEY NOT NULL,
 "name" text NOT NULL,
 "age" integer NOT NULL,
 "email" text NOT NULL,
 CONSTRAINT "users_table_email_unique" UNIQUE("email")
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "posts_table" ADD CONSTRAINT "posts_table_user_id_users_table_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users_table"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
```

--------------------------------

### Install postgres package (bun)

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-supabase

Installs the postgres package using bun, a Node.js driver for PostgreSQL that Drizzle ORM can use.

```bash
bun add postgres
```

--------------------------------

### Install @libsql/client Package

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-turso

Installs the '@libsql/client' package, which is the official driver for interacting with libSQL-compatible databases like Turso. This client enables Drizzle ORM to communicate with the database.

```npm
npm i @libsql/client
```

```yarn
yarn add @libsql/client
```

```pnpm
pnpm add @libsql/client
```

```bun
bun add @libsql/client
```

--------------------------------

### Initialize Drizzle Connection with Existing Driver

Source: https://orm.drizzle.team/docs/get-started/turso-database-new

Demonstrates how to initialize Drizzle ORM when you already have an existing database client instance. This is useful for integrating Drizzle with pre-configured database connections or custom driver setups.

```typescript
import 'dotenv/config';
import { Database } from '@tursodatabase/database';
import { drizzle } from 'drizzle-orm/tursodatabase/database';

const client = new Database(process.env.DB_FILE_NAME!);
const db = drizzle({ client });
```

--------------------------------

### Install Drizzle and Gel Packages (bun)

Source: https://orm.drizzle.team/docs/get-started-gel

Installs the necessary Drizzle ORM and Gel packages for bun projects. Includes the development dependency for Drizzle Kit.

```bash
bun add drizzle-orm gel
bun add -D drizzle-kit
```

--------------------------------

### Install Drizzle ORM and PostgreSQL Dependencies (npm)

Source: https://orm.drizzle.team/docs/get-started/nile-new

Installs the core Drizzle ORM package, the 'pg' driver for PostgreSQL, 'dotenv' for environment variables, and development dependencies like 'drizzle-kit', 'tsx', and '@types/pg'.

```bash
npm i drizzle-orm pg dotenv
npm i -D drizzle-kit tsx @types/pg
```

--------------------------------

### Drizzle Kit Generate Migration Process

Source: https://orm.drizzle.team/docs/drizzle-kit-generate

Visual representation of the `drizzle-kit generate` process, outlining steps from reading migration folders to generating SQL files.

```ascii-art
┌────────────────────────┐
│ $ drizzle-kit generate │
└─┬──────────────────────┘
 │
 └ 1. read previous migration folders
 2. find diff between current and previous scheama
 3. prompt developer for renames if necessary
 ┌ 4. generate SQL migration and persist to file
 │ ┌─┴───────────────────────────────────────┐
 │ 📂 drizzle
 │ ├ 📂 _meta
 │ └ 📜 0000_premium_mister_fear.sql
 v
```

--------------------------------

### Install Drizzle ORM and mysql2 driver

Source: https://orm.drizzle.team/docs/get-started-singlestore

Installs the necessary Drizzle ORM packages and the `mysql2` driver for SingleStore integration using npm, yarn, pnpm, or bun.

```npm
npm i drizzle-orm mysql2
npm i -D drizzle-kit
```

```yarn
yarn add drizzle-orm mysql2
yarn add -D drizzle-kit
```

```pnpm
pnpm add drizzle-orm mysql2
pnpm add -D drizzle-kit
```

```bun
bun add drizzle-orm mysql2
bun add -D drizzle-kit
```

--------------------------------

### Start MySQL Docker Container

Source: https://orm.drizzle.team/docs/guides/mysql-local-setup

This command starts a MySQL container named 'drizzle-mysql' in detached mode. It sets the root password, maps port 3306 on the host to the container's port 3306 for external access, and uses the 'mysql' image. Optional environment variables can create databases and users upon container creation.

```bash
docker run --name drizzle-mysql -e MYSQL_ROOT_PASSWORD=mypassword -d -p 3306:3306 mysql
```

```bash
docker ps
```

--------------------------------

### Initialize Supabase Project

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-supabase-edge-functions

Initializes a new Supabase project locally. This command creates a 'supabase' folder containing configuration files for your Supabase project.

```bash
supabase init
```

--------------------------------

### Install Drizzle ORM and PostgreSQL Dependencies (pnpm)

Source: https://orm.drizzle.team/docs/get-started/nile-new

Installs the core Drizzle ORM package, the 'pg' driver for PostgreSQL, 'dotenv' for environment variables, and development dependencies like 'drizzle-kit', 'tsx', and '@types/pg' using pnpm.

```bash
pnpm add drizzle-orm pg dotenv
pnpm add -D drizzle-kit tsx @types/pg
```

--------------------------------

### Set up Bun:SQLite Database Connection Variable

Source: https://orm.drizzle.team/docs/get-started/bun-sqlite-new

Defines the database file name for Bun:SQLite in the .env file. This variable is used to configure the database connection string for Drizzle ORM.

```env
DB_FILE_NAME=mydb.sqlite
```

--------------------------------

### Install Neon Serverless Driver

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-neon

Installs the Neon serverless driver, which is required for connecting Drizzle ORM to a Neon Postgres database. Supports multiple package managers.

```npm
npm i @neondatabase/serverless
```

```yarn
yarn add @neondatabase/serverless
```

```pnpm
pnpm add @neondatabase/serverless
```

```bun
bun add @neondatabase/serverless
```

--------------------------------

### Install Express Package

Source: https://orm.drizzle.team/docs/tutorials/drizzle-with-nile

Installs the 'express' package, a minimal and flexible Node.js web application framework, using common package managers.

```npm
npm i express
```

```yarn
yarn add express
```

```pnpm
pnpm add express
```

```bun
bun add express
```

--------------------------------

### Drizzle Configuration File

Source: https://orm.drizzle.team/docs/get-started/vercel-new

Sets up the `drizzle.config.ts` file, which Drizzle Kit uses for database operations. It specifies the migration output directory (`out`), schema file location (`schema`), database dialect (`dialect`), and credentials (including the `POSTGRES_URL` from environment variables).

```typescript
import 'dotenv/config';
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
 out: './drizzle',
 schema: './src/db/schema.ts',
 dialect: 'postgresql',
 dbCredentials: {
 url: process.env.POSTGRES_URL!,
 },
});
```

--------------------------------

### Initialize Drizzle ORM Database Connection in TypeScript

Source: https://orm.drizzle.team/docs/get-started/gel-new

This snippet demonstrates how to initialize a connection to your database using Drizzle ORM and a 'gel' client. It requires the 'drizzle-orm/gel' and 'gel' packages. The output is a configured Drizzle database instance.

```typescript
import { drizzle } from "drizzle-orm/gel";
import { createClient } from "gel";

const gelClient = createClient();
const db = drizzle({ client: gelClient });
```

--------------------------------

### Install Drizzle ORM and Drizzle Kit with bun

Source: https://orm.drizzle.team/docs/connect-bun-sqlite

Installs Drizzle ORM and Drizzle Kit using the Bun runtime. Bun provides a fast alternative for package installation and JavaScript execution.

```bash
bun add drizzle-orm
bun add -D drizzle-kit
```

--------------------------------

### Initialize SingleStore driver with connection options

Source: https://orm.drizzle.team/docs/get-started-singlestore

Initializes the Drizzle ORM driver for SingleStore by providing connection options, including the database URI, and shows a sample query.

```typescript
import { drizzle } from "drizzle-orm/singlestore";

// You can specify any property from the mysql2 connection options
const db = drizzle({ connection:{ uri: process.env.DATABASE_URL }});

const response = await db.select().from(...)
```

--------------------------------

### Initialize Drizzle ORM Connection (Supabase Pool Mode)

Source: https://orm.drizzle.team/docs/get-started/supabase-new

Initializes a Drizzle ORM connection for Supabase with 'Transaction' pool mode enabled, disabling 'prepare' as it's not supported in this configuration.

```typescript
import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'

async function main() {
 // Disable prefetch as it is not supported for "Transaction" pool mode
 const client = postgres(process.env.DATABASE_URL, { prepare: false })
 const db = drizzle({ client });
}

main();
```

--------------------------------

### Pull PostgreSQL Docker Image

Source: https://orm.drizzle.team/docs/guides/postgresql-local-setup

This command fetches the latest PostgreSQL Docker image from Docker Hub. You can also specify a particular version using tags, for example, `postgres:15`.

```bash
docker pull postgres
```

```bash
docker pull postgres:15
```

--------------------------------

### Install Drizzle ORM and PostgreSQL Dependencies (yarn)

Source: https://orm.drizzle.team/docs/get-started/nile-new

Installs the core Drizzle ORM package, the 'pg' driver for PostgreSQL, 'dotenv' for environment variables, and development dependencies like 'drizzle-kit', 'tsx', and '@types/pg' using yarn.

```bash
yarn add drizzle-orm pg dotenv
yarn add -D drizzle-kit tsx @types/pg
```