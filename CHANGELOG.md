# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **New TypeScript Code Review Skills** (`developer-kit-typescript`):
  - `nestjs-code-review`: NestJS code review with controller, service, module, guard, and DI pattern analysis
  - `nextjs-code-review`: Next.js App Router review covering Server/Client Components, Server Actions, caching, and performance
  - `react-code-review`: React 19 component review with hooks, accessibility, state management, and TypeScript integration
  - `typescript-security-review`: Security audit for TypeScript/Node.js covering OWASP Top 10, XSS, injection, JWT, and dependency scanning
  - Each skill includes reference documentation (patterns, anti-patterns, checklists)

- **Standardized Coding Rules for Language Plugins** (PR #112, closes #109):
  - Added `rules/` directory with path-scoped coding rules to 4 language plugins
  - **Java** (`developer-kit-java`): 4 rules — naming-conventions, project-structure, language-best-practices, error-handling (Java 17+, Spring Boot, constructor DI, Records)
  - **Python** (`developer-kit-python`): 4 rules — naming-conventions, project-structure, language-best-practices, error-handling (PEP 8, type hints, Pydantic, async patterns)
  - **PHP** (`developer-kit-php`): 4 rules — naming-conventions, project-structure, language-best-practices, error-handling (PSR-12, PSR-4, PHP 8.1+, readonly properties)
  - **TypeScript** (`developer-kit-typescript`): 16 rules — core (naming-conventions, project-structure, language-best-practices, error-handling), NestJS (architecture, api-design, security, testing), React (component-conventions, data-fetching, routing-conventions), Tailwind (styling-conventions), Data (drizzle-orm-conventions, shared-dto-conventions), Infra (nx-monorepo-conventions, i18n-conventions)
  - Rules use Claude Code `.claude/rules/` compatible format with `globs:` frontmatter for automatic path-scoped activation

- **New RuleValidator** (`.skills-validator-check`):
  - Added `RuleValidator` for validating rule files structure and content
  - Validates `globs:` frontmatter, required sections (Guidelines, Examples), and formatting
  - Extended `ValidatorFactory` to include rule validation pattern
  - Added comprehensive test suite for rule validation

### Changed

- **Updated plugin.json manifests**: All 4 language plugin manifests now include `rules` array with component references
- **Updated install-claude.sh**: Rules are deployed to `.claude/rules/[plugin-name]/` with conflict resolution
- **Updated Makefile**: `list-plugins` and `list-components` targets now display rules count
- **Extended MCP scan checker**: Security scanning now covers rule files

## [2.4.0] - 2026-02-28

### Added

- **New Spring Boot Project Creator skill** (`developer-kit-java`):
  - `spring-boot-project-creator`: Automated Spring Boot project generation with customizable dependencies
  - Supports Spring Boot 3.x with Java 17+
  - Interactive dependency selection (Web, Data JPA, Security, Actuator, etc.)
  - Best practices enforcement and project structure templates

- **New GraalVM Native Image skill** (`developer-kit-java`):
  - `graalvm-native-image`: Comprehensive skill for building GraalVM native executables from Java applications
  - Covers: Maven/Gradle project analysis, Native Build Tools configuration, framework-specific patterns (Spring Boot AOT, Quarkus, Micronaut)
  - GraalVM reachability metadata (reflect-config, resource-config)
  - Iterative fix engine for resolving native build failures
  - Tracing agent for automatic metadata collection
  - Docker integration with multi-stage builds

- **New GitHub Issue Workflow skill** (`developer-kit-core`):
  - `github-issue-workflow`: Skill for creating and managing GitHub issues with workflow automation
  - Plugin manifest updated to integrate new skill
  - Security hardening: treats issue bodies as untrusted input with content-isolation, mandatory user confirmation, and prompt injection prevention

- **New `developer-kit-tools` plugin** (PR #106):
  - New plugin for external tools integration (CLI utilities, APIs, third-party services)
  - `notebooklm`: Google NotebookLM integration skill for generating audio summaries, podcasts, and study guides from source documents
  - Enforces user-provided sources and includes security guidance for content handling

- **Context7 Integration**: Added `context7.json` for claim skills repository

- **Enhanced Security Scanning**:
  - Added MCP scan checker for per-skill security analysis
  - Implemented PR-level security scanning (only changed skills)
  - Added Gen Agent Trust Hub security check
  - New security scan workflow for CI integration

- **MCP-Scan Security Integration** (`.skills-validator-check`):
  - New `mcp_scan_checker.py` script for security scanning of skills
  - Integrates with [mcp-scan](https://github.com/invariantlabs-ai/mcp-scan) from Invariant Labs
  - Detects prompt injection attacks, malware payloads, sensitive data handling issues, and hard-coded secrets
  - Supports scanning all skills (`--all`), specific plugins (`--plugin`), specific paths (`--path`), or changed skills only (`--changed`)
  - Per-skill scanning with clear output and summary statistics
  - JSON output parsing with structured results
  - Classifies W004 "not in registry" as informational (expected for custom skills)

- **GitHub Actions Security Scan Workflow** (`.github/workflows/security-scan.yml`):
  - Automated security scanning on push to main/develop and pull requests
  - PRs scan only changed skills for efficiency
  - Push events scan all skills
  - Uses `uvx` runner for mcp-scan execution

- **Makefile Security Targets**:
  - `make security-scan`: Run MCP-Scan on all skills
  - `make security-scan-changed`: Run MCP-Scan only on changed skills
- **Resolved 14 MCP-Scan Security Failures**:
  - W007 - Insecure credential handling: Replaced hardcoded apiKey/password with env var references in RAG
  - W012 - External URL/code execution risks: Pinned Docker images (LocalStack 3.8.1, ollama 0.5.4, qdrant v1.13.2), npm packages (@modelcontextprotocol 0.6.2), and GitHub Actions (trivy-action, snyk/actions)
  - W011 - Third-party content exposure: Added content validation/filtering warnings across skills (RAG, Bedrock, Messaging, MCP patterns, Qdrant, Spring AI MCP, TS Lambda, Next.js, shadcn-ui)
- Disabled Trust Hub security check returning HTTP 400
- Replaced hardcoded credentials with environment variable references

### Changed

- **Enhanced README Badges**: Added security scan and plugin-validation badges
- **Added Marketplace Links**: Added 'Listed on' marketplace links to README

### Security

- **Resolved 14 MCP-Scan Security Failures**:
  - W007 - Insecure credential handling: Replaced hardcoded apiKey/password with env var references in RAG
  - W012 - External URL/code execution risks: Pinned Docker images (LocalStack 3.8.1, ollama 0.5.4, qdrant v1.13.2), npm packages (@modelcontextprotocol 0.6.2), and GitHub Actions (trivy-action, snyk/actions)
  - W011 - Third-party content exposure: Added content validation/filtering warnings across skills (RAG, Bedrock, Messaging, MCP patterns, Qdrant, Spring AI MCP, TS Lambda, Next.js, shadcn-ui)

- **Fixed Trust Hub Security Check**: Disabled Trust Hub API check returning HTTP 400 (incompatible with raw GitHub URLs)

## [2.3.0] - 2026-02-25

### Added

- **New AWS CLI Beast Mode skill** (`developer-kit-aws`):
  - `aws-cli-beast`: Comprehensive AWS CLI mastery for advanced cloud engineers
  - Covers EC2, Lambda, S3, DynamoDB, RDS, VPC, IAM, Bedrock, and CloudWatch
  - Features advanced JMESPath queries, bulk operations, waiters, and security-first patterns
  - Includes reference guides: compute-mastery, data-ops-beast, networking-security-hardened, automation-patterns
  - Provides shell aliases and helper scripts for daily AWS operations

- **New AWS Cost Optimization skill** (`developer-kit-aws`):
  - `aws-cost-optimization`: Structured AWS cost optimization guidance using five pillars (right-sizing, elasticity, pricing models, storage optimization, monitoring) and twelve actionable best practices
  - Covers AWS native tools: Cost Explorer, Budgets, Compute Optimizer, Trusted Advisor, Cost Anomaly Detection
  - Includes FinOps practices, EC2/EBS/S3 optimization, Savings Plans evaluation

- **Enhanced Skill Validation System**:
  - Added support for agentskills.io/specification validation
  - New skill validator with improved compliance checking

- **CI/CD Security Integration**:
  - Added Gen Agent Trust Hub security check for affected skills
  - Automated security validation in CI pipeline

- **GitHub Repository Improvements**:
  - Added GitHub issue templates for standardized bug reports and feature requests
  - Updated README.md with comprehensive Developer Kit workflows documentation

### Fixed

- **Skill Metadata Corrections**:
  - Removed invalid frontmatter fields from SKILL.md files across plugins
  - Corrected name mismatch in `developer-kit-php` clean-architecture skill

## [2.2.0] - 2026-02-20

### Added
- **New Better Auth skill** (`developer-kit-typescript`):
  - `better-auth`: Comprehensive Better Auth integration for NestJS backend and Next.js frontend with Drizzle ORM + PostgreSQL
  - Complete authentication flow with email/password, OAuth providers, JWT tokens, and session management
  - Backend patterns for NestJS with Better Auth integration, protected routes, and role-based access control
  - Frontend patterns for Next.js App Router with Better Auth client, React hooks, and middleware
  - Database schema with Drizzle ORM for users, sessions, accounts, and verification tokens

- **Enhanced Validation System** (`.skills-validator-check`):
  - Added `KebabCaseValidator`: Validates markdown filenames follow kebab-case naming convention
  - Added `SkillPackageValidator`: Detects prohibited `.skill` package files that shouldn't be committed
  - Added `PluginVersionValidator`: Ensures plugin.json version aligns with marketplace.json version
  - Added `PluginJsonValidator`: Verifies all components (skills, agents, commands) are properly registered in plugin.json
  - Added empty skill folder detection to identify malformed skill directories

- **New Draw.io Logical Diagrams skill** (`developer-kit-core`):
  - `drawio-logical-diagrams`: Professional logical flow diagrams and system architecture diagrams in draw.io XML format
  - Supports flowcharts, BPMN, UML (class, sequence, activity), DFD, and system interaction diagrams
  - Includes shape styles reference and diagram templates

- **New Next.js Skills** (5 comprehensive skills for `developer-kit-typescript`):
  - `nextjs-app-router`: Next.js 16+ App Router patterns, file-based routing, nested layouts, Server Components, Server Actions, and `"use cache"` directive
  - `nextjs-authentication`: Authentication implementation with Auth.js 5 (NextAuth.js), JWT, OAuth providers, RBAC, and session management
  - `nextjs-data-fetching`: Data fetching patterns with Server Components, SWR, React Query, ISR, and revalidation strategies
  - `nextjs-performance`: Performance optimization with Core Web Vitals (LCP, INP, CLS), `next/image`, `next/font`, streaming with Suspense, and bundle optimization
  - `nextjs-deployment`: Deployment patterns with Docker multi-stage builds, GitHub Actions CI/CD, environment variables, preview deployments, and OpenTelemetry monitoring

- **New Drizzle ORM Skills** (2 skills for `developer-kit-typescript`):
  - `drizzle-orm-patterns`: Complete Drizzle ORM patterns for schema definitions, CRUD operations, relations (one-to-one, one-to-many, many-to-many), type-safe queries, transactions, and migrations with Drizzle Kit
  - `nestjs-drizzle-crud-generator`: Automated NestJS CRUD module generation with Drizzle ORM via Python script, including controllers, services, Zod-validated DTOs, schema, and unit tests

- **New Monorepo Skills** (2 skills for `developer-kit-typescript`):
  - `nx-monorepo`: Complete Nx workspace patterns including configuration, generators, affected commands, Module Federation, CI/CD integration, remote caching with Nx Cloud, and framework-specific guides for NestJS, React, and TypeScript
  - `turborepo-monorepo`: Complete Turborepo patterns including turbo.json configuration, task dependencies, Next.js and NestJS integration, testing with Vitest/Jest, CI/CD, and remote caching with Vercel

- **New AWS Lambda Integration Skills** (4 skills across multiple plugins):
  - `aws-lambda-typescript-integration` (`developer-kit-typescript`): AWS Lambda patterns for TypeScript with NestJS adapters, Express/Fastify adapters, raw TypeScript handlers, and Serverless Framework deployment
  - `aws-lambda-java-integration` (`developer-kit-java`): AWS Lambda patterns for Java with Micronaut Framework (cold start < 1s) and Raw Java handlers (cold start < 500ms), API Gateway/ALB support
  - `aws-lambda-python-integration` (`developer-kit-python`): AWS Lambda patterns for Python with AWS Chalice Framework (cold start < 200ms) and Raw Python handlers (cold start < 100ms)
  - `aws-lambda-php-integration` (`developer-kit-php`): AWS Lambda patterns for PHP with Bref Framework and Raw PHP handlers, Symfony integration

- **New Monorepo Documentation**: Comprehensive `guide-skills-monorepo.md` for `developer-kit-typescript` with best practices for both Nx and Turborepo architectures

### Changed
- **Refactored AWS skill directory structure** (`developer-kit-aws`):
  - Moved `aws-drawio-architecture-diagrams` skill from `skills/aws-cloudformation/` to `skills/aws/` directory
  - Better separation between CloudFormation IaC skills and general AWS skills
- Updated `developer-kit-typescript` plugin.json with 11 new skills and 11 new keywords (nextjs, drizzle, monorepo, aws, lambda, serverless)
- Updated `developer-kit-python` plugin.json with `aws` and `lambda` keywords
- Enhanced frontend documentation (`guide-skills-frontend.md`) with Next.js Development Skills section
- Updated all plugin manifests to include new skills
- Updated documentation component counts across all plugins:
  - Total components: **92 skills, 43 agents, 36 commands** (was 77 skills, 43 agents, 36 commands at v2.1.0)

### Fixed
- Resolved security issues in authentication patterns (better-auth skill)
- Resolved review findings from component audit (naming conventions, schema compliance)
- Corrected XML syntax error in draw.io decision diamond example
- Minor bug fixes in TypeScript skill configurations

## [2.1.0] - 2026-02-14

### Added
- **New Clean Architecture skills** across multiple languages:
  - PHP Clean Architecture patterns (Clean Architecture, Hexagonal Architecture, DDD)
  - Python Clean Architecture patterns with FastAPI/Flask examples
  - TypeScript/NestJS Clean Architecture with Domain-Driven Design
  - Java/Spring Boot Clean Architecture with enterprise patterns
- **New AWS Architecture Diagrams skill**:
  - Professional AWS architecture diagram creation in draw.io format
  - Well-Architected Framework visualization patterns
  - Infrastructure as Code diagram representations
- **New shadcn-ui Chart component**:
  - Recharts integration for data visualization
  - Line, bar, pie, area, and radar chart components
  - Responsive chart patterns with Tailwind CSS
- **New CLAUDE.md handler skill**:
  - Project instruction management and optimization
  - Best practices for maintaining project guidelines

### Changed
- Enhanced skill documentation with clearer scope definitions
- Improved multi-language Clean Architecture coverage

### Fixed
- YAML parser warning in wordpress-sage-theme skill
- Clean Architecture skill configuration issues

## [2.0.0] - 2026-02-07

### Changed
- **Complete restructuring to multi-plugin architecture**:
  - Restructured codebase from monolithic to multi-plugin system organized by language/technology
  - Created 10 self-contained plugins in `plugins/` directory:
    - **developer-kit-core**: Core agents and commands (brainstorm, refactor, debugging, LRA workflow, GitHub integration)
    - **developer-kit-java**: Java/Spring Boot/LangChain4J/AWS SDK skills and agents
    - **developer-kit-typescript**: NestJS/React/React Native/TypeScript skills and agents
    - **developer-kit-python**: Python skills and agents
    - **developer-kit-php**: PHP/WordPress/Laravel/Symfony skills and agents
    - **developer-kit-aws**: AWS/CloudFormation skills and agents
    - **developer-kit-ai**: Prompt engineering, RAG, chunking strategies
    - **developer-kit-devops**: Docker, GitHub Actions
    - **developer-kit-project-management**: LRA workflow commands
    - **github-spec-kit**: GitHub specification tools
  - Moved all agents to respective plugin directories
  - Reorganized all commands by category within each plugin
  - Split all skills by language/technology
  - Updated `marketplace.json` with new 10 plugin references
  - Updated Makefile for multi-plugin installation support
  - Added plugin-specific documentation (README.md, guide-agents.md, guide-commands.md) for each plugin

### Fixed
- Minor bug fixes

## [1.25.1] - 2026-02-05

### Fixed

- Added wordpress-sage-theme skill to marketplace.json

## [1.25.0] - 2026-02-03

### Added
- **New Brainstorming Command**:
  - `/devkit.brainstorm`: Transform ideas into fully formed designs through structured dialogue
  - 9-phase systematic approach with specialist agents:
    1. Context Discovery
    2. Idea Refinement
    3. Approach Exploration
    4. Codebase Exploration (uses `developer-kit:general-code-explorer` agent)
    5. Design Presentation (validated incrementally)
    6. Documentation Generation (uses `developer-kit:document-generator-expert` agent)
    7. Document Review (uses `developer-kit:general-code-reviewer` agent)
    8. Next Steps Recommendation
    9. Summary
  - Creates professional design documents at `docs/plans/YYYY-MM-DD--design.md`
  - Codebase exploration ensures designs are based on actual code patterns (not assumptions)
  - Professional documentation generated by specialist agent
  - Document review phase ensures quality before proceeding
  - Automatic recommendation for next development command with pre-filled arguments
  - Language-agnostic design - works with any technology stack
  - One question at a time approach with multiple choice options
  - Incremental validation of design sections (200-300 words each)
  - Always proposes 2-3 approaches with trade-offs before settling
  - Integrates seamlessly with `/devkit.feature-development`, `/devkit.fix-debugging`, and `/devkit.refactor`

### Changed
- **Improved Command Robustness**:
  - Made "Current Context" section optional in all workflow commands
  - Removed automatic git execution (`!` prefix) that could fail in newly initialized repositories
  - Commands now gather context information conditionally when available:
    - `/devkit.feature-development`
    - `/devkit.fix-debugging`
    - `/devkit.refactor`
    - `/devkit.brainstorm`
  - Prevents errors when working with projects without git history

## [1.24.0] - 2026-02-01

### Added
- **New PHP Agents** (5 new specialized agents):
  - `php-code-review-expert`: Expert PHP code reviewer specializing in code quality, security, performance, and modern PHP best practices. Reviews PHP codebases (Laravel, Symfony) for bugs, logic errors, security vulnerabilities, and quality issues using confidence-based filtering
  - `php-refactor-expert`: Expert PHP code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and modern PHP 8.3+ best practices for Laravel and Symfony
  - `php-security-expert`: Expert security auditor specializing in PHP application security, DevSecOps, and compliance frameworks. Masters vulnerability assessment, threat modeling, secure authentication (OAuth2/JWT), OWASP standards, and security automation for Laravel and Symfony
  - `php-software-architect-expert`: Expert PHP software architect specializing in Clean Architecture, Domain-Driven Design (DDD), and modern PHP patterns. Reviews PHP codebases (Laravel, Symfony) for architectural integrity, proper module organization, and SOLID principles
  - `wordpress-development-expert`: Expert WordPress developer specializing in custom plugin and theme development. Masters WordPress coding standards, hooks/filters architecture, Gutenberg blocks, REST API, WooCommerce integration, and site/portal development
- **New WordPress Sage Theme Skill**:
  - `wordpress-sage-theme`: Comprehensive WordPress Sage theme development skill
  - Sage 10+ theme architecture with modern Blade templates
  - ACF (Advanced Custom Fields) integration patterns
  - Bud (Vite-based) build system configuration
  - Blade templating engine patterns for WordPress themes
  - Starter layouts and page templates
  - Reference documentation for Sage, Blade, ACF, and Bud
  - Asset compilation and optimization strategies
- **Enhanced Spring Boot Code Review** (contributed by @zmlgit):
  - Added transaction management checks (JTA, @Transactional, isolation levels)
  - Added event handling patterns verification (Spring Events, @EventListener)
  - Added AOP (Aspect-Oriented Programming) patterns review
  - Added JPA pitfalls detection (N+1 queries, lazy loading, entity lifecycle)
  - Added MyBatis integration patterns and best practices
- **Enhanced PHP/Laravel Support**:
  - PHP 8.3+ specific patterns (readonly classes, enums, constructor property promotion)
  - Modern PHP patterns (match expressions, named arguments, attributes, first-class callables)
  - Laravel-specific patterns (Eloquent ORM, query scopes, service container, middleware)
  - Symfony-specific patterns (autowiring, security voters, doctrine ORM, messenger)
  - Clean Architecture and DDD patterns for PHP applications
- **WordPress Development Expertise**:
  - Custom plugin architecture and WordPress Plugin API
  - Theme development (child themes, block themes, Full Site Editing)
  - Gutenberg block development with React
  - WordPress REST API integration
  - WooCommerce customization and extensions
  - WordPress coding standards and security best practices

### Changed
- Updated `.claude-plugin/marketplace.json` with new PHP and WordPress agents metadata
- Enhanced README.md with PHP development capabilities documentation
- Total agents count increased with new PHP and WordPress specialists
- Updated agents documentation to include PHP/Laravel/Symfony and WordPress development capabilities
- Organized skills directory structure with `react-patterns` and `tailwind-css-patterns` renames
- Updated marketplace.json metadata for new skills
- Enhanced general agents documentation with PHP/WordPress capabilities

### Documentation
- Added comprehensive PHP agent definitions with specialized expertise in:
  - Code review with confidence-based filtering (≥80 threshold)
  - Refactoring with SOLID principles and clean code patterns
  - Security auditing with OWASP Top 10 compliance
  - Software architecture with Clean Architecture and DDD patterns
  - WordPress plugin and theme development best practices
- Enhanced agent descriptions with PHP framework expertise (Laravel, Symfony)
- Added WordPress-specific patterns and coding standards
- Added comprehensive Sage theme development guide with 281 lines of SKILL.md content
- Added reference documentation for ACF (465 lines), Blade (304 lines), Bud (327 lines), and Sage (130 lines)
- Included starter Blade templates for layouts and pages

## [1.23.0] - 2025-01-24

### Added
- **New DevOps Agents** (2 new specialized agents):
  - `general-docker-expert`: Expert Docker containerization specialist. Masters multi-stage builds, Docker Compose orchestration, container optimization, and production deployment strategies. Proficient in Dockerfile best practices, volume management, networking, security hardening, and container lifecycle management
  - `github-actions-pipeline-expert`: Expert GitHub Actions CI/CD pipeline architect. Masters workflow automation, pipeline optimization, deployment strategies, and production-grade CI/CD implementations. Proficient in composite actions, reusable workflows, custom actions, matrix builds, caching strategies, security hardening, and pipeline monitoring
- **New Python Agents** (4 new specialized agents):
  - `python-code-review-expert`: Expert Python code reviewer specializing in code quality, security, performance, and Pythonic best practices. Reviews Python codebases for bugs, logic errors, security vulnerabilities, and quality issues using confidence-based filtering
  - `python-refactor-expert`: Expert Python code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and Pythonic best practices
  - `python-security-expert`: Expert security auditor specializing in Python application security, DevSecOps, and compliance frameworks. Masters vulnerability assessment, threat modeling, secure authentication (OAuth2/JWT), OWASP standards, and security automation
  - `python-software-architect-expert`: Expert Python software architect specializing in Clean Architecture, Domain-Driven Design (DDD), and modern Python patterns. Reviews Python codebases for architectural integrity, proper module organization, and SOLID principles
- **New AWS CloudFormation Skills** (14 comprehensive skills with complete SKILL.md, examples.md, and reference.md files):
  - `aws-cloudformation-auto-scaling`: Auto Scaling groups, scaling policies, lifecycle hooks, and scheduled actions
  - `aws-cloudformation-bedrock`: Amazon Bedrock integration, AI/ML foundation models, and serverless AI inference
  - `aws-cloudformation-cloudfront`: CloudFront distributions, edge functions, origins, cache behaviors, and WAF integration
  - `aws-cloudformation-cloudwatch`: CloudWatch dashboards, alarms, metrics, logs, and monitoring strategies
  - `aws-cloudformation-dynamodb`: DynamoDB tables, GSIs, LSIs, streams, auto-scaling, and TTL configuration
  - `aws-cloudformation-ec2`: EC2 instances, launch templates, ASG integration, security groups, and ENI configuration
  - `aws-cloudformation-ecs`: ECS clusters, task definitions, services, capacity providers, and Fargate deployment
  - `aws-cloudformation-elasticache`: ElastiCache Redis/Memcached clusters, replication groups, and node configuration
  - `aws-cloudformation-iam`: IAM users, groups, roles, policies, and permission boundary management
  - `aws-cloudformation-lambda`: Lambda functions, layers, event sources, aliases, and versioning strategies
  - `aws-cloudformation-rds`: RDS instances, Aurora clusters, parameter groups, snapshot management, and Multi-AZ deployment
  - `aws-cloudformation-s3`: S3 buckets, policies, lifecycle rules, versioning, replication, and event notifications
  - `aws-cloudformation-security`: Security best practices, WAF, Shield, KMS encryption, and compliance patterns
  - `aws-cloudformation-vpc`: VPC design, subnets, route tables, NAT gateways, VPC endpoints, and peering
- **Enhanced AWS Architecture Review**:
  - Updated `aws-solution-architect-expert` agent with CloudFormation expertise
  - Added comprehensive infrastructure as code review capabilities
  - Enhanced Well-Architected Framework compliance checking
- **GitHub Actions Task Skill**:
  - `aws-cloudformation-task-ecs-deploy-gh`: Complete ECS deployment to GitHub Actions workflow skill
  - Production-grade pipeline templates with blue-green deployment
  - Comprehensive examples and reference documentation

### Changed
- Updated `.claude-plugin/marketplace.json` with new agents and skills metadata
- Enhanced README.md with new DevOps, CloudFormation skills, and Python agents documentation
- Total skills count increased significantly with 14 new AWS CloudFormation skills
- Total agents count increased from 28 to 34 with new DevOps and Python specialists
- Updated agents documentation to include Python development capabilities

### Documentation
- Added comprehensive SKILL.md files for all 14 CloudFormation skills with detailed patterns
- Added extensive examples.md files with practical CloudFormation template examples
- Added complete reference.md files with CloudFormation resource properties and reference documentation
- Added 4 new Python agent definitions with specialized expertise in code review, refactoring, security, and architecture
- Enhanced agent descriptions with DevOps and infrastructure expertise
- Added guide-skills-aws-cloudformation.md for comprehensive CloudFormation patterns documentation

## [1.22.0] - 2026-01-14

### Added
- **New AWS Cloud Architects Agents** (4 new specialized agents):
  - `aws-architecture-review-expert`: Expert AWS architecture and CloudFormation reviewer specializing in Well-Architected Framework compliance, security best practices, cost optimization, and IaC quality. Reviews AWS architectures and CloudFormation templates for scalability, reliability, and operational excellence
  - `aws-cloudformation-devops-expert`: Expert AWS DevOps engineer specializing in CloudFormation templates, Infrastructure as Code (IaC), and AWS deployment automation. Masters nested stacks, cross-stack references, custom resources, and CI/CD pipeline integration
  - `aws-solution-architect-expert`: Expert AWS Solution Architect specializing in scalable cloud architectures, Well-Architected Framework, and enterprise-grade AWS solutions. Masters multi-region deployments, high availability patterns, cost optimization, and security best practices
  - `general-refactor-expert`: Expert code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and language-specific best practices

## [1.21.0] - 2026-01-12

### Added
- `document-generator-expert` agent: Expert document generator for creating professional technical and business documentation
  - Assessment documents (technical debt, security, performance, maturity)
  - Feature documents (specifications, analysis, proposals)
  - Analysis documents (gap analysis, impact analysis, comparative studies)
  - Process documents (SOPs, runbooks, procedures)
  - Custom documents with user-defined formats
  - Multi-language support (English, Italian, Spanish, French, German, Portuguese)
  - Codebase-driven analysis for accurate documentation
  - Structured templates for each document type
  - Integration with existing Developer Kit agents
- `/devkit.generate-document` command: Interactive document generation with multi-language support
  - Parameters for language (`--lang`), document type (`--type`), and output format (`--format`)
  - Six-phase workflow (discovery, codebase analysis, content planning, generation, review, output)
  - Project-specific analysis agents (Spring Boot, NestJS, React, General)
  - Domain expert coordination for specialized content
  - Documents saved to `docs/` directory with summary

### Changed
- Total agents count increased from 27 to 28

## [1.20.0] - 2025-12-26

### Added
- `react-software-architect-review` agent: Expert React software architect specializing in frontend architecture, component design patterns, state management strategies, and performance optimization for complex React applications
  - React 19 architecture mastery (Server Components, Actions, use hook, concurrent features)
  - Component design patterns (Compound Components, Render Props, HOCs, Custom Hooks)
  - State management architecture (Context, TanStack Query, Zustand, Jotai, Redux Toolkit)
  - Framework-specific patterns for Next.js App Router, Remix, and Vite+React
  - Performance architecture (memoization, code splitting, lazy loading, bundle optimization)
  - Accessibility architecture (WCAG compliance, ARIA patterns, keyboard navigation)
  - Testing architecture (React Testing Library, Vitest, Playwright)
  - Design system architecture (component API design, theming, token systems)

### Changed
- Updated `/devkit.feature-development` command to use `react-software-architect-review` agent for React architecture reviews
- Updated `/devkit.fix-debugging` command to use `react-software-architect-review` agent for React debugging
- Updated `/devkit.refactor` command to use `react-software-architect-review` agent for React refactoring
- Total agents count increased from 26 to 27

## [1.19.0] - 2025-12-24

### Added
- `/devkit.refactor` command: Comprehensive guided refactoring command with backward compatibility options and multi-phase verification
  - **Phase 1**: Refactoring discovery and understanding
  - **Phase 2**: Compatibility requirements clarification (backward compatible, breaking changes, or internal-only)
  - **Phase 3**: Deep codebase exploration with parallel analysis of code structure, usages, and test coverage
  - **Phase 4**: Refactoring strategy design with risk assessment
  - **Phase 5**: Pre-refactoring baseline verification
  - **Phase 6**: Incremental implementation
  - **Phase 7**: Comprehensive verification (automated tests, static analysis, code review, architecture validation)
  - **Phase 8**: Issue resolution and remediation
  - **Phase 9**: Summary and documentation with migration guides
  - Multi-language support: `--lang=java|spring|typescript|nestjs|react|general`
  - Scope selection: `--scope=file|module|feature`
  - Specialized refactoring agents for each language
  - Breaking change management and deprecation strategy support

## [1.18.0] - 2025-12-18

### Added
- `expo-react-native-development-expert` (agents/expo-react-native-development-expert.md): Expert Expo & React Native mobile developer specializing in cross-platform mobile app development with Expo SDK 54, React Native 0.81.5, React 19.1, and TypeScript (781fcb9)


## [1.17.1] - 2025-12-16

### Fixed
- Added TypeScript/React support to `/devkit.feature-development` and `/devkit.fix-debugging` commands
- Improved language detection for frontend development tasks

## [1.17.0] - 2025-12-11

### Added
- **New Frontend Development Skills** (4 new skills):
  - `react`: React development patterns, hooks, state management, performance optimization
  - `shadcn-ui`: Modern UI component library with Radix UI primitives and Tailwind CSS
  - `tailwind-css`: Utility-first CSS framework for rapid UI development
  - `typescript-docs`: TypeScript documentation patterns and type definition best practices
- **New TypeScript & Frontend Agents** (8 new agents):
  - `react-frontend-development-expert`: React architecture, hooks, state management, performance
  - `nestjs-backend-development-expert`: NestJS modules, microservices, authentication, APIs
  - `nestjs-code-review-expert`: NestJS security, performance, architecture review
  - `nestjs-unit-testing-expert`: Unit, integration, and e2e testing with Jest
  - `typescript-documentation-expert`: JSDoc/TSDoc, API documentation, type definitions
  - `typescript-refactor-expert`: Modern patterns, performance optimization, legacy migration
  - `typescript-security-expert`: OWASP Top 10, npm audit, secure coding practices
  - `typescript-software-architect-review`: Design patterns, scalability, module organization
- **New General Purpose Agents** (3 new agents):
  - `general-code-explorer`: Code tracing, architecture mapping, dependency documentation
  - `general-code-reviewer`: Code quality, maintainability, best practices across languages
  - `general-software-architect`: System design, technology selection, scalability patterns
- **New Documentation**:
  - Complete Frontend Skills Guide (`docs/guide-skills-frontend.md`) with comprehensive patterns and examples
  - Updated Agents Guide with new TypeScript & Frontend Development section
- **Expanded Language Support**: TypeScript/Node.js added as fully supported language stack

### Changed
- Updated total skills count from 50 to 54
- Updated total agents count from 12 to 22
- Expanded Key Features to reflect full-stack development capabilities
- Updated Language Roadmap to show TypeScript/Node.js as completed

### Documentation
- Completely rewrote `docs/guide-skills-frontend.md` with practical examples and best practices
- Added TypeScript integration examples in frontend guide
- Updated agents documentation with comprehensive descriptions of all new agents

## [1.16.1] - 2025-12-08

### Added
- New debugging agent (`general-debugger.md`) for root cause analysis and debugging workflows
- New `/devkit.fix-debugging` command for quick debugging and issue resolution

### Fixed
- Fixed feature command issues on Claude Code with proper agent name checking
- Added missing test and compile checks in development workflows
- Corrected agent name prefix validation for developer-kit agents
- Updated agents documentation count in README for accuracy

## [1.15.0] - 2025-12-04

### Added
- **New comprehensive Makefile with multi-CLI support**:
  - `make install-claude` - Interactive installer for Claude Code projects
  - `make install-copilot` - Install for GitHub Copilot CLI
  - `make install-opencode` - Install for OpenCode CLI
  - `make install-codex` - Install for Codex CLI
  - `make install` - Install for all detected CLIs
  - `make status` - Show installation status for all CLIs
  - `make backup` - Create backup of existing configurations
  - `make uninstall` - Remove all installations
- **Interactive Claude Code installer** (`make install-claude`):
  - Step-by-step guided installation process with environment validation
  - Category-based skill selection (AWS Java, AI, JUnit Test, LangChain4j, Spring Boot)
  - Flexible agent selection (all, specific, or none)
  - Command selection with full 30-item listing
  - Smart conflict handling with overwrite, skip, or rename options
  - Complete project directory structure creation (.claude/skills/, .claude/agents/, .claude/commands/)
  - Installation progress tracking and detailed summary
  - Clean, colorized terminal UI with helpful next steps
- **CLI tool integrations**:
  - GitHub Copilot CLI support (agents installation)
  - OpenCode CLI support (agents and commands)
  - Codex CLI support (instructions and custom prompts)
- Comprehensive backup system for existing configurations
- Installation status monitoring and validation commands

### Changed
- Updated Makefile structure with comprehensive multi-CLI support
- Enhanced help documentation with clear usage examples for all CLI tools
- Streamlined installation flow for better user experience

### Fixed
- Cleaned up ignored files from repository (52bcd54)
- Fixed merge integration for new installation features

### Security
- Validates Claude Code environment before installation to ensure proper context
- Safe file handling with proper backup and restore mechanisms

## [1.14.0] - 2025-12-04

### Added
- New spring-boot-security-jwt skill with JWT authentication and authorization patterns:
  - JWT token generation and validation with JJWT
  - Bearer token and cookie-based authentication
  - OAuth2/OIDC provider integration
  - Database-backed authentication integration
  - Role-based (RBAC) and permission-based access control
  - Method-level security with annotations
  - Security headers and CSRF protection
- New spring-ai-mcp-server-patterns skill for Model Context Protocol:
  - MCP server implementation patterns for Spring AI
  - AI tool integration and context management
  - Function calling patterns
- Enhanced security documentation and best practices
- Integration patterns for AI-powered Spring Boot applications

### Changed
- Enhanced `/devkit.feature-development` command with improved user interaction:
  - Added `AskUserQuestion` tool for structured user prompts
  - Improved phase 3 clarifying questions with structured interaction
  - Enhanced phase 4 architecture design with user choice presentation
  - Fixed agent fallback order (developer-kit agents first, then general agents)
  - Better documentation and usage examples

## [1.13.0] - 2025-12-04

### Added
- New `/devkit.feature-development` command for guided feature development with systematic 7-phase approach
- Three new general-purpose agents for comprehensive feature development:
  - `explorer` - Analyzes existing codebase patterns and traces execution paths
  - `architect` - Designs complete implementation blueprints with detailed architecture decisions
  - `code-reviewer` - Reviews code for bugs, security vulnerabilities, and quality issues with confidence-based filtering
- Integrated Task tool usage pattern for parallel agent execution
- Fallback mechanism ensuring compatibility across different plugin installation scenarios

## [1.12.1] - 2025-11-30

### Fixed
- Updated commands for selecting correct agent on execution command (0028135)

## [1.12.0] - 2025-11-27

### Added
- Long-Running Agent (LRA) workflow commands and guide (12f495c)

### Changed
- Updated package path in refactoring task generator (a9a098f)

### Fixed
- Removed ignored files from project (cd75bd4)

## [1.11.0] - 2025-11-24

### Added
- New commands and agents for enhanced development workflow
- Comprehensive tutorial for agents, commands and skills
- Documentation updates for commands and project structure
- Enhanced README with new sections and improved organization

### Changed
- Removed optimize documentation references for cleaner structure
- Made changelog command language-agnostic for better cross-platform compatibility

### Fixed
- Fixed formatting of requirements section in guide
- Changed release dates in CHANGELOG.md for accuracy
- Minor fixes and improvements to command structure

## [1.10.0] - 2025-11-12

### Added
- GitHub workflow automation commands
- Dependency management commands
- Code refactoring commands
- Project documentation generation commands

### Changed
- Refactored command structure for better maintainability
- Made changelog generation commands language-agnostic

### Fixed
- Improved command compatibility across different platforms

## [1.9.0] - 2025-11-10

### Added
- New Java agents for specialized development tasks
- Enhanced skill collection for Java development
- Improved documentation structure

### Changed
- Updated marketplace configuration for new agents
- Enhanced README with new features documentation

## [1.8.0] - 2025-11-08

### Added
- Project documentation generation commands
- Code documentation automation
- Enhanced markdown generation capabilities

### Fixed
- Documentation formatting improvements
- Updated version management scripts

## [1.7.0] - 2025-11-06

### Added
- New Java commands for unit and integration testing
- CRUD pattern generation commands
- Enhanced testing capabilities

### Changed
- Improved command structure and organization
- Updated dependencies and build configuration

## [1.6.0] - 2025-11-05

### Added
- New agents for specialized development tasks
- Enhanced skill collection
- Improved documentation and examples

### Changed
- Refactored skill organization with Anthropics rules compliance
- Updated marketplace configuration
- Enhanced README structure

## [1.5.0] - 2025-11-05

### Added
- Python script templates for CRUD patterns
- Enhanced automation capabilities
- Improved developer experience features

### Changed
- Restructured project organization
- Updated documentation and guides
- Enhanced command-line interface

## [1.4.0] - 2025-11-10

### Added
- Initial Java development agents
- Spring Boot specialization
- Enhanced testing patterns

### Changed
- Improved project structure
- Updated dependencies
- Enhanced documentation

## [1.3.0] - 2024-11-08

### Added
- Comprehensive skill collection
- Enhanced command palette
- Improved developer tools

### Changed
- Restructured documentation
- Updated marketplace configuration
- Enhanced user experience

## [1.2.0] - 2025-11-06

### Added
- Initial release of Developer Kit
- Core skill framework
- Basic agent structure
- Essential documentation

### Changed
- Established project foundation
- Created initial structure
- Set up development workflow

## [1.1.0] - 2025-11-05

### Added
- Plugin configuration
- Marketplace metadata
- Initial skill templates

### Fixed
- Setup and configuration issues
- Documentation improvements

## [1.0.0] - 2025-11-02

### Added
- Initial project setup
- Basic structure
- Core functionality
- Foundation documentation

[Unreleased]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v2.3.0...HEAD
[2.3.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.25.1...v2.0.0
[1.25.1]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.25.0...v1.25.1
[1.25.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.24.0...v1.25.0
[1.24.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.23.0...v1.24.0
[1.23.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.22.0...v1.23.0
[1.22.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.20.0...v1.22.0
[1.21.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.20.0...v1.21.0
[1.20.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.19.0...v1.20.0
[1.19.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.18.0...v1.19.0
[1.18.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.17.1...v1.18.0
[1.17.1]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.17.0...v1.17.1
[1.17.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.16.1...v1.17.0
[1.16.1]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.15.0...v1.16.1
[1.15.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.12.1...v1.13.0
[1.12.1]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.12.0...v1.12.1
[1.12.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/giuseppe-trisciuoglio/developer-kit/releases/tag/v1.0.0
