# Developer Kit Core

Core agents and commands required by all Developer Kit plugins.

## Overview

The `developer-kit` plugin provides foundational agents and commands used across all Developer Kit plugins. This plugin is required by all other plugins in the Developer Kit marketplace.

> **Note:** The plugin name in the manifest (`plugin.json`) is `developer-kit` rather than `developer-kit-core` to maintain backward compatibility with the `devkit.*` command prefixes used in the legacy plugin. The directory is named `developer-kit-core` for structural clarity, but the plugin name remains `developer-kit` to ensure continuity with existing configurations.

## Agents

- **general-code-explorer** - Codebase navigation and understanding
- **general-code-reviewer** - Code review best practices
- **general-refactor-expert** - Refactoring strategies
- **general-software-architect** - Architecture design
- **general-debugger** - Debugging methodologies
- **document-generator-expert** - Documentation generation

## Commands

### Specification Workflow
- `devkit.brainstorm` - Full 9-phase idea generation and specification exploration
- `devkit.quick-spec` - Lightweight 4-phase spec for bug fixes and small features
- `devkit.spec-review` - Interactive specification quality assessment (max 5 questions)
- `devkit.spec-quality` - Maintain specification context quality (Knowledge Graph sync)
- `devkit.spec-to-tasks` - Convert functional specifications into executable tasks
- `devkit.spec-sync` - Synchronize specification with implementation state
- `devkit.task-implementation` - Guided task implementation (11-step workflow)

### Task Management
- `devkit.task-manage` - Post-generation task management (list, split, add, mark-optional, update)
- `devkit.task-review` - Verify implemented tasks meet specifications
- `devkit.task-implementation` - Guided single-task implementation with Knowledge Graph validation

### Core Workflows
- `devkit.refactor` - Refactoring coordination
- `devkit.feature-development` - Feature implementation guidance
- `devkit.fix-debugging` - Debugging assistance
- `devkit.generate-document` - Document creation
- `devkit.generate-changelog` - Changelog generation
- `devkit.generate-security-assessment` - Security assessment generation

### GitHub Integration
- `devkit.github.create-pr` - Pull request creation
- `devkit.github.review-pr` - Pull request review

### Long-Running Agent (LRA) Workflow
- `devkit.lra.init` - LRA workflow initialization
- `devkit.lra.add-feature` - LRA feature addition
- `devkit.lra.checkpoint` - LRA checkpoint management
- `devkit.lra.mark-feature` - LRA feature marking
- `devkit.lra.recover` - LRA session recovery
- `devkit.lra.start-session` - LRA session start
- `devkit.lra.status` - LRA status check

### Plugin Management
- `devkit.verify-skill` - Skill verification [TODO to be moved to a separate plugin]

## Skills

- **adr-drafting** - Draft new Architecture Decision Records (ADRs) for significant architectural changes
- **memory-md-management** - Project memory file management and optimization
- **drawio-logical-diagrams** - Professional logical flow diagrams and system architecture diagrams in draw.io XML format
- **github-issue-workflow** - GitHub issue creation and management with workflow automation
- **docs-updater** - Automated documentation updates by analyzing git changes between releases
- **knowledge-graph** - Knowledge Graph management for specifications with schema, query patterns, and integration examples

## Dependencies

None - this is the foundational plugin.
