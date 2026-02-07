# Developer Kit Documentation

Welcome to the Developer Kit documentation. The documentation has been reorganized into a decentralized structure, with each plugin maintaining its own documentation.

---

## New Documentation Structure

The documentation is now organized by plugin. Each plugin has its own `docs/` directory containing:

- **README.md**: Plugin overview and quick start
- **guide-agents.md**: Plugin-specific agent documentation
- **guide-commands.md**: Plugin-specific command documentation (if applicable)
- **guide-skills-*.md**: Plugin-specific skill guides (if applicable)

---

## Plugin Documentation

### Core Plugin

**Location**: [plugins/developer-kit-core/docs/](../plugins/developer-kit-core/docs/)

Contains:
- Installation guide
- Agent overview (hub document linking to all plugins)
- Command overview (hub document linking to all plugins)
- LRA workflow guide

---

### Language Plugins

#### Java Plugin

**Location**: [plugins/developer-kit-java/docs/](../plugins/developer-kit-java/docs/)

Contains:
- Spring Boot skills guide
- JUnit test skills guide
- LangChain4J skills guide
- AWS Java SDK skills guide
- Java agents guide
- Java commands guide

#### TypeScript Plugin

**Location**: [plugins/developer-kit-typescript/docs/](../plugins/developer-kit-typescript/docs/)

Contains:
- NestJS skills guide
- Frontend skills guide (React, TypeScript, UI frameworks)
- TypeScript agents guide
- TypeScript commands guide

#### Python Plugin

**Location**: [plugins/developer-kit-python/docs/](../plugins/developer-kit-python/docs/)

Contains:
- Python agents guide

#### PHP Plugin

**Location**: [plugins/developer-kit-php/docs/](../plugins/developer-kit-php/docs/)

Contains:
- PHP agents guide (including WordPress)

---

### Infrastructure Plugins

#### AWS Plugin

**Location**: [plugins/developer-kit-aws/docs/](../plugins/developer-kit-aws/docs/)

Contains:
- CloudFormation skills guide
- AWS agents guide

#### DevOps Plugin

**Location**: [plugins/developer-kit-devops/docs/](../plugins/developer-kit-devops/docs/)

Contains:
- DevOps agents guide (Docker, GitHub Actions)

---

### AI Plugin

**Location**: [plugins/developer-kit-ai/docs/](../plugins/developer-kit-ai/docs/)

Contains:
- Prompt engineering skill
- RAG skill
- Chunking strategy skill
- AI agents guide

---

### Project Management Plugins

#### Project Management Plugin

**Location**: [plugins/developer-kit-project-management/docs/](../plugins/developer-kit-project-management/docs/)

Contains:
- Project management commands guide

#### GitHub Spec Kit Plugin

**Location**: [plugins/github-spec-kit/docs/](../plugins/github-spec-kit/docs/)

Contains:
- GitHub Spec Kit commands guide

---

## Architecture Documents

**Location**: [plans/](./plans/)

Contains architecture and planning documents:
- [Decentralized Documentation Architecture Blueprint](./plans/2026-02-07--decentralized-documentation-architecture.md)
- [Decentralized Documentation Visual Diagram](./plans/2026-02-07--decentralized-documentation-diagram.md)

---

## Quick Navigation

| What you're looking for | Where to find it |
|-------------------------|------------------|
| Installation instructions | [Core Plugin → Installation](../plugins/developer-kit-core/docs/installation.md) |
| All agents overview | [Core Plugin → Agent Guide](../plugins/developer-kit-core/docs/guide-agents.md) |
| All commands overview | [Core Plugin → Command Guide](../plugins/developer-kit-core/docs/guide-commands.md) |
| Java/Spring Boot guides | [Java Plugin Documentation](../plugins/developer-kit-java/docs/) |
| TypeScript/React guides | [TypeScript Plugin Documentation](../plugins/developer-kit-typescript/docs/) |
| Python guides | [Python Plugin Documentation](../plugins/developer-kit-python/docs/) |
| PHP/WordPress guides | [PHP Plugin Documentation](../plugins/developer-kit-php/docs/) |
| AWS/CloudFormation guides | [AWS Plugin Documentation](../plugins/developer-kit-aws/docs/) |
| Docker/GitHub Actions guides | [DevOps Plugin Documentation](../plugins/developer-kit-devops/docs/) |
| AI/Prompt engineering guides | [AI Plugin Documentation](../plugins/developer-kit-ai/docs/) |
