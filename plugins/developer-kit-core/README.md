# Developer Kit Core

Core agents and commands required by all Developer Kit plugins.

## Overview

The `developer-kit` plugin provides foundational agents and commands used across all Developer Kit plugins. This plugin is required by all other plugins in the Developer Kit marketplace.

> **Nota:** Il nome del plugin nel manifesto (`plugin.json`) è `developer-kit` e non `developer-kit-core` per mantenere la retrocompatibilità con i prefissi dei comandi `devkit.*` utilizzati nel vecchio plugin. La directory è denominata `developer-kit-core` per chiarezza strutturale, ma il nome del plugin rimane `developer-kit` per garantire continuità con le configurazioni esistenti.

## Agents

- **general-code-explorer** - Codebase navigation and understanding
- **general-code-reviewer** - Code review best practices
- **general-refactor-expert** - Refactoring strategies
- **general-software-architect** - Architecture design
- **general-debugger** - Debugging methodologies
- **document-generator-expert** - Documentation generation

## Commands

### Core Workflows
- `devkit.brainstorm` - Idea generation and exploration
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

## Dependencies

None - this is the foundational plugin.

