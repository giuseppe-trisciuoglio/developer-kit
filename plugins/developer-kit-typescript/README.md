# Developer Kit TypeScript

TypeScript/JavaScript full-stack development with NestJS, React, and React Native.

## Overview

The `developer-kit-typescript` plugin provides comprehensive support for TypeScript and JavaScript development, including NestJS backend, React frontend, React Native mobile, and modern UI frameworks.

## Agents

### NestJS Backend
- nestjs-backend-development-expert
- nestjs-code-review-expert
- nestjs-database-expert
- nestjs-security-expert
- nestjs-testing-expert
- nestjs-unit-testing-expert

### React/React Native
- react-frontend-development-expert
- react-software-architect-review
- expo-react-native-development-expert

### TypeScript Core
- typescript-refactor-expert
- typescript-security-expert
- typescript-software-architect-review
- typescript-documentation-expert

## Commands

- `devkit.typescript.code-review` - TypeScript code review
- `devkit.react.code-review` - React code review
- `devkit.ts.security-review` - TypeScript security review

## Skills

### Backend (NestJS)
- **nestjs** - NestJS framework patterns
- **nestjs-best-practices** - Comprehensive NestJS best practices including modular architecture, dependency injection scoping, exception filters, DTO validation, and Drizzle ORM integration
- **clean-architecture** - Clean Architecture, Hexagonal Architecture, and DDD patterns for NestJS backend applications

### Authentication
- **better-auth** - Comprehensive Better Auth integration for NestJS backend and Next.js frontend with Drizzle ORM + PostgreSQL

### Frontend (React & Next.js)
- **react-patterns** - React 19 design patterns
- **shadcn-ui** - shadcn/ui component library
- **tailwind-css-patterns** - Tailwind CSS patterns
- **nextjs-app-router** - Next.js App Router patterns and fundamentals
- **nextjs-authentication** - Authentication implementation with Auth.js/NextAuth
- **nextjs-data-fetching** - Data fetching strategies with React Query/TanStack Query
- **nextjs-performance** - Performance optimization and Core Web Vitals
- **nextjs-deployment** - Deployment patterns, Docker, and CI/CD

### Monorepo
- **nx-monorepo** - Nx monorepo management with generators, affected commands, Module Federation, and CI/CD
- **turborepo-monorepo** - Turborepo monorepo management with turbo.json, framework integration, and caching

### Database & ORM
- **drizzle-orm-patterns** - Complete Drizzle ORM patterns for schema, queries, relations, transactions, and migrations
- **nestjs-drizzle-crud-generator** - Automated NestJS CRUD module generation with Drizzle ORM

### AWS Lambda Integration
- **aws-lambda-typescript-integration** - AWS Lambda integration patterns for TypeScript with NestJS adapters and Serverless Framework

### Design System
- **tailwind-design-system** - Tailwind CSS design system patterns and token management

### Core/Shared
- **typescript-docs** - TypeScript documentation standards

## Rules

Standardized coding rules that auto-activate via `globs:` path-scoped matching for consistent code quality.

### TypeScript Core
- **naming-conventions** (`**/*.ts`) — TypeScript identifier naming standards (strict typing, no `any`)
- **project-structure** (`**/*.ts`) — Domain-driven module organization
- **language-best-practices** (`**/*.ts`) — Modern TypeScript features and clean code patterns
- **error-handling** (`**/*.ts`) — Result pattern, exception hierarchies, error response strategies

### NestJS
- **nestjs-architecture** (`src/**/*.ts`) — Modular design, Core/Shared module separation, circular dependency prevention
- **nestjs-api-design** (`src/**/*.ts`) — RESTful API design, DTO validation, response transformation
- **nestjs-security** (`src/**/*.ts`) — Authentication guards, authorization, input sanitization
- **nestjs-testing** (`**/*.spec.ts`) — Unit/integration testing patterns with Jest

### React & Frontend
- **react-component-conventions** (`**/*.tsx`) — Component composition, hooks patterns, prop design
- **react-data-fetching** (`**/*.{ts,tsx}`) — Data fetching strategies with TanStack Query
- **react-routing-conventions** (`**/*.tsx`) — Route organization and navigation patterns
- **tailwind-styling-conventions** (`**/*.tsx`) — Tailwind CSS class ordering and responsive design

### Data & ORM
- **drizzle-orm-conventions** (`**/*.schema.ts`) — Schema design, migrations, query patterns
- **shared-dto-conventions** (`**/*.dto.ts`) — DTO design, validation, serialization

### Monorepo & Infrastructure
- **nx-monorepo-conventions** (`**/*.ts`) — Nx workspace organization, library boundaries, affected commands
- **i18n-conventions** (`**/*.{ts,tsx}`) — Internationalization patterns and translation management

## Dependencies

- `developer-kit` (required)
