# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.22.0] - 2026-01-14

### Added
- **New AWS Cloud Architects Agents** (4 new specialized agents):
  - `aws-architecture-review-expert`: Expert AWS architecture and CloudFormation reviewer specializing in Well-Architected Framework compliance, security best practices, cost optimization, and IaC quality. Reviews AWS architectures and CloudFormation templates for scalability, reliability, and operational excellence
  - `aws-cloudformation-devops-expert`: Expert AWS DevOps engineer specializing in CloudFormation templates, Infrastructure as Code (IaC), and AWS deployment automation. Masters nested stacks, cross-stack references, custom resources, and CI/CD pipeline integration
  - `aws-solution-architect-expert`: Expert AWS Solution Architect specializing in scalable cloud architectures, Well-Architected Framework, and enterprise-grade AWS solutions. Masters multi-region deployments, high availability patterns, cost optimization, and security best practices
  - `general-refactor-expert`: Expert code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and language-specific best practices
### Added
- Features in development

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

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

[Unreleased]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.22.0...HEAD
[1.22.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.20.0...v1.22.0
[1.21.0]: https://github.com/giuseppe.trisciuoglio/developer-kit/compare/v1.20.0...v1.21.0
[1.20.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.19.0...v1.20.0
[1.19.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.18.0...v1.19.0
[1.18.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.17.1...v1.18.0
[1.17.1]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.17.0...v1.17.1
[1.17.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.16.1...v1.17.0
[1.16.1]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.15.0...v1.16.1
[1.15.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.12.1...v1.13.0
[1.12.1]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.12.0...v1.12.1
[1.12.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/releases/tag/v1.0.0
