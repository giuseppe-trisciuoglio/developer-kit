# Developer Kit for Claude Code

[![Run in Smithery](https://smithery.ai/badge/skills/giuseppe-trisciuoglio)](https://smithery.ai/skills?ns=giuseppe-trisciuoglio&utm_source=github&utm_medium=badge)


> A curated collection of reusable skills and agents for automating development tasks in Claude Code — focusing on
> Java/Spring Boot patterns with extensibility to TypeScript, Python, and PHP

**Developer Kit for Claude Code** teaches Claude how to **perform development tasks in a repeatable way** across
multiple languages and frameworks. It includes specialized agents for code review, testing patterns, REST API design,
and AI integration.

## 🚀 Quick Start

```bash
# Claude Code CLI
/plugin marketplace add giuseppe-trisciuoglio/developer-kit

# Or from local directory
/plugin install /path/to/developer-kit
```

**Claude Desktop**: [Enable Skills in Settings](https://claude.ai/settings/capabilities)

📖 **[Complete Installation Guide](docs/installation.md)** — Multi-CLI support, local project installation, team setup

---

## ✨ Key Features

- **Specialized** — Domain-specific agents for code review, testing, AI development, and full-stack development
- **Composable** — Skills stack together automatically based on task context
- **Portable** — Use across Claude.ai, Claude Code CLI, Claude Desktop, and Claude API
- **Efficient** — Skills load on-demand, consuming minimal tokens until actively used

---

## 📚 Available Components

### Skills

| Category           | Guide                                          |
|--------------------|------------------------------------------------|
| JUnit Testing      | [Guide](docs/guide-skills-junit-test.md)       |
| Spring Boot        | [Guide](docs/guide-skills-spring-boot.md)      |
| AWS Java SDK       | [Guide](docs/guide-skills-aws-java.md)         |
| AWS CloudFormation | [Guide](docs/guide-skills-aws-cloudformation.md) |
| LangChain4J        | [Guide](docs/guide-skills-langchain4j.md)      |
| React              | [Guide](docs/guide-skills-frontend.md)         |
| shadcn-ui          | [Guide](docs/guide-skills-frontend.md)         |
| Tailwind CSS       | [Guide](docs/guide-skills-frontend.md)         |
| TypeScript Docs    | [Guide](docs/guide-skills-frontend.md)         |
| NestJS             | [Guide](docs/guide-skills-nestjs.md)           |

### Agents

Specialized AI assistants for specific development domains.

📖 **[Complete Agents Guide](docs/guide-agents.md)** — All agents with usage examples

| Category          | Examples                                                                                                            |
|-------------------|---------------------------------------------------------------------------------------------------------------------|
| Java/Spring Boot  | `spring-boot-code-review-expert`, `java-refactor-expert`, `java-security-expert`                                    |
| TypeScript/NestJS | `nestjs-backend-development-expert`, `typescript-refactor-expert`, `nestjs-security-expert`                         |
| React/Frontend    | `react-frontend-development-expert`, `react-software-architect-review`, `expo-react-native-development-expert`      |
| Python            | `python-code-review-expert`, `python-refactor-expert`, `python-security-expert`, `python-software-architect-expert` |
| AWS               | `aws-solution-architect-expert`, `aws-cloudformation-devops-expert`, `aws-architecture-review-expert`               |
| AI/LangChain4J    | `langchain4j-ai-development-expert`, `prompt-engineering-expert`                                                    |
| General Purpose   | `general-debugger`, `general-code-reviewer`, `general-refactor-expert`, `document-generator-expert`                 |

### Commands

Workflow automation commands for development tasks.

📖 **[Complete Commands Guide](docs/guide-commands.md)** — All commands with examples

| Category         | Examples                                                                                             |
|------------------|------------------------------------------------------------------------------------------------------|
| Java Development | `/devkit.java.code-review`, `/devkit.java.write-unit-tests`, `/devkit.java.refactor-class`           |
| LRA Workflow     | `/devkit.lra.init`, `/devkit.lra.start-session`, `/devkit.lra.checkpoint`                            |
| Security         | `/devkit.java.security-review`, `/devkit.ts.security-review`, `/devkit.generate-security-assessment` |
| Spec Kit         | `/speckit.check-integration`, `/speckit.optimize`, `/speckit.verify`                                 |
| GitHub           | `/devkit.github.create-pr`, `/devkit.github.review-pr`                                               |
| TypeScript       | `/devkit.typescript.code-review`, `/devkit.ts.security-review`                                       |
| Documentation    | `/devkit.generate-document`, `/devkit.generate-changelog`, `/devkit.write-a-minute-of-a-meeting`     |
| Workflow         | `/devkit.feature-development`, `/devkit.fix-debugging`, `/devkit.refactor`                           |

---

## 🎯 Use Cases

- **Code Review & Architecture** — Automated reviews, architecture validation, security analysis
- **Testing Strategies** — Unit test patterns, integration testing with Testcontainers
- **REST API Design** — Standardized API development with proper HTTP semantics
- **AI Integration** — LangChain4J implementation, RAG patterns, MCP server creation
- **AWS Cloud Development** — RDS, S3, Lambda, DynamoDB, Secrets Manager patterns

---

## 🌍 Language Support

| Language           | Status                                           |
|--------------------|--------------------------------------------------|
| Java/Spring Boot   | ✅ Comprehensive (skills, agents, commands)       |
| TypeScript/Node.js | ✅ React, NestJS, Expo (skills, agents, commands) |
| Python             | 🚧 In Progress (agents available)                |
| PHP                | 📋 Planned (Laravel, Symfony)                    |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on adding skills, agents, and commands.

---

## 🔒 Security

⚠️ Skills can execute code. Review all custom skills before deploying.

- Only install from trusted sources
- Review SKILL.md before enabling
- Test in non-production environments first

---

## 📘 Documentation

| Guide                                                    | Description                                 |
|----------------------------------------------------------|---------------------------------------------|
| [Installation](docs/installation.md)                     | Multi-CLI setup, local project installation |
| [Agents](docs/guide-agents.md)                           | All agents with usage examples              |
| [Commands](docs/guide-commands.md)                       | All commands with workflows                 |
| [LRA Workflow](docs/guide-lra-workflow.md)               | Multi-session project management            |
| [Skills - Spring Boot](docs/guide-skills-spring-boot.md) | Spring Boot patterns                        |
| [Skills - JUnit](docs/guide-skills-junit-test.md)        | Testing patterns                            |
| [Skills - LangChain4J](docs/guide-skills-langchain4j.md) | AI integration                              |
| [Skills - AWS](docs/guide-skills-aws-java.md)            | AWS SDK patterns                            |
| [Skills - Frontend](docs/guide-skills-frontend.md)           | React, Tailwind, shadcn                        |
| [Skills - NestJS](docs/guide-skills-nestjs.md)             | NestJS patterns                               |
| [Skills - AWS CloudFormation](docs/guide-skills-aws-cloudformation.md) | Infrastructure as Code patterns               |

---

## 📚 Resources

- [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills) — Claude support article
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude) — Setup guide
- [anthropics/skills](https://github.com/anthropics/skills) — Official Anthropic skills repository

---

## 📝 License

See [LICENSE](LICENSE) file.

## 📞 Support

- **Questions?** [Open an issue](https://github.com/giuseppe-trisciuoglio/developer-kit/issues)
- **Contributions?** [Submit a PR](https://github.com/giuseppe-trisciuoglio/developer-kit/pulls)

## 📅 Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete history.

---

**Made with ❤️ for Developers using Claude Code**
