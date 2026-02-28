# Developer Kit Java Plugin Documentation

Welcome to the Developer Kit Java Plugin documentation. This plugin provides comprehensive tools for Java, Spring Boot, LangChain4J, and AWS SDK development.

---

## Available Documentation

### Skills Guides

- **[Spring Boot Skills](./guide-skills-spring-boot.md)** - Spring Boot framework skills
- **[JUnit Test Skills](./guide-skills-junit-test.md)** - JUnit testing skills
- **[LangChain4J Skills](./guide-skills-langchain4j.md)** - LangChain4J AI framework skills
- **[AWS Java Skills](./guide-skills-aws-java.md)** - AWS SDK for Java skills
- **[Architecture Skills](./guide-skills-architecture.md)** - Clean Architecture and DDD skills

### Component Guides

- **[Agent Guide](./guide-agents.md)** - Java and Spring Boot specialized agents
- **[Command Guide](./guide-commands.md)** - Java and Spring Boot commands

---

## About Java Plugin

The Developer Kit Java Plugin provides:

- **Java Agents**: 9 specialized agents for Spring Boot, general Java, and LangChain4J development
- **Java Commands**: 11 commands for code review, testing, generation, refactoring, security, and dependency management
- **Java Skills**: 51 skills covering Spring Boot, JUnit testing, LangChain4J, AWS SDK, Spring AI, Qdrant, Clean Architecture, and more

---

## Plugin Structure

```
developer-kit-java/
├── agents/              # Java and Spring Boot agents
├── commands/            # Java commands (devkit.java.*)
├── skills/              # Java skills
│   ├── spring-boot-*/   # Spring Boot skills
│   ├── unit-test-*/     # JUnit testing skills
│   ├── langchain4j-*/   # LangChain4J skills
│   ├── aws-sdk-java-v2-*/  # AWS Java SDK skills
│   └── ...
└── docs/               # This documentation
```

---

## Quick Start

1. **Explore available agents**: See [Agent Guide](./guide-agents.md)
2. **Try Java commands**: See [Command Guide](./guide-commands.md)
3. **Learn Spring Boot patterns**: See [Spring Boot Skills](./guide-skills-spring-boot.md)
4. **Master JUnit testing**: See [JUnit Test Skills](./guide-skills-junit-test.md)

---

## Key Features

### Spring Boot Development
- REST API development with proper patterns
- Service layer design with dependency injection
- Repository layer with Spring Data JPA
- Configuration management
- Security with JWT
- Caching, resilience, and monitoring

### Testing
- JUnit 5 unit tests with Mockito
- Spring Boot integration tests
- Parameterized testing
- Test coverage optimization
- Testing strategies for controllers, services, repositories

### AI Integration
- LangChain4J framework integration
- AI service patterns
- RAG (Retrieval-Augmented Generation)
- Vector stores (Qdrant)
- Tool/function calling
- Spring AI MCP server patterns

### AWS Integration
- AWS SDK for Java 2.x
- S3, DynamoDB, RDS, Lambda, SNS/SQS
- Bedrock for AI/ML
- KMS for encryption
- Secrets Manager

---

## See Also

- [Core Plugin Documentation](../developer-kit-core/docs/) - Core guides and installation
- [TypeScript Plugin Documentation](../developer-kit-typescript/docs/) - TypeScript, NestJS, and React guides
- [AWS Plugin Documentation](../developer-kit-aws/docs/) - AWS CloudFormation guides

---

## Cross-Plugin References

The Java plugin contains AWS Java SDK skills that are related to the AWS plugin:

- **[AWS Java Skills](./guide-skills-aws-java.md)** - AWS SDK integration from Java
- See [AWS Plugin](../developer-kit-aws/docs/) for CloudFormation infrastructure skills
