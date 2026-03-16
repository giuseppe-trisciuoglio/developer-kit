# Contributing to Developer Kit for Claude Code

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Developer Kit for Claude Code.

## 🎯 What You Can Contribute

The Developer Kit welcomes contributions in the following areas:

### 1. **New Skills** 📚
Add reusable capabilities for Claude Code covering:
- **Java/Spring Boot patterns** (expanded scope beyond existing)
- **New languages**: PHP, TypeScript, Python, Go, Rust, etc.
- **New frameworks**: Django, FastAPI, Laravel, Express, etc.
- **Specialized domains**: Cloud providers (AWS, GCP, Azure), data processing, DevOps, etc.

### 2. **Skill Improvements** ✨
Enhance existing skills with:
- Additional examples and use cases
- Better explanations or clearer documentation
- New best practices and patterns
- Performance or security improvements
- Supporting scripts or utilities

### 3. **Agents** 🤖
Create specialized AI assistants for:
- Domain-specific code reviews
- Language or framework specialists
- Testing and debugging automation
- Security and performance analysis

### 4. **Slash Commands** ⚡
Add quick-access commands for:
- Common development tasks
- Workflow automation
- Project-specific shortcuts

### 5. **Documentation** 📖
Improve project documentation:
- README updates with new capabilities
- Architecture documentation
- Troubleshooting guides
- Integration guides

### 6. **Bug Fixes & Issues** 🐛
- Report issues with existing skills
- Fix documentation errors
- Improve examples or code samples
- Suggest enhancements

## 📋 Before You Start

1. **Check existing content**: Search existing components in [plugins/](./plugins/) to avoid duplicating skills, agents, or commands
2. **Open an issue**: For significant changes, discuss your idea first by opening an issue
3. **Understand the structure**: Review the project organization and existing patterns

## 🚀 Creating a New Skill

### Directory Structure

```
skills/[category]/[skill-name]/
├── SKILL.md                 # Required: Skill metadata and instructions
├── reference.md             # Optional: Detailed API reference
├── examples.md              # Optional: Practical examples
├── scripts/                 # Optional: Helper scripts (Python, Bash, etc.)
│   ├── validator.py
│   └── processor.sh
└── templates/               # Optional: Templates and boilerplate
    └── sample.txt
```

### SKILL.md Format

```markdown
---
name: skill-descriptive-name
description: Brief description of what this skill does and when to use it. Include trigger keywords (max 1024 chars). Should mention BOTH capabilities AND use cases.
allowed-tools: Read, Write, Bash  # Optional: restrict tool access
---

# Skill Name

## When to Use
- Clear trigger phrases and context where this skill applies
- Specific use cases and scenarios
- What problems it solves

## Instructions
- Step-by-step guidance for using this skill
- Key concepts and terminology
- Common patterns and approaches

## Examples
- Basic example with expected output
- Intermediate example showing more features
- Advanced example with best practices
- Real-world use cases

## Best Practices
- Key principles and guidelines
- Common pitfalls to avoid
- Performance considerations
- Security considerations
- Integration with related skills

## Related Skills
- Links to complementary skills
- When to use instead of this skill
- How skills work together
```

### Creating a Skill - Step by Step

1. **Create the directory**:
   ```bash
   mkdir -p skills/[category]/[skill-name]
   ```

2. **Create SKILL.md** with required frontmatter:
   - `name`: lowercase, hyphens (no spaces)
   - `description`: Specific, includes trigger keywords, states both what AND when

3. **Add supporting files** as needed:
   - `reference.md`: Technical specifications, APIs, configurations
   - `examples.md`: Practical, runnable examples progressing from basic to advanced
   - `scripts/`: Helper utilities (Python, Bash, JavaScript)

4. **Follow content guidelines**:
   - Target audience: Developers using Claude Code for that domain
   - Include both Maven and Gradle configs for Java/Spring Boot skills
   - Code samples follow best practices from the domain
   - Examples should be copy-paste ready
   - Performance guidelines where applicable

5. **Test your skill**:
   - Ask Claude questions matching your description
   - Verify Claude discovers and uses the skill appropriately
   - Test with various use cases and edge cases

### Skill Content Guidelines

**Structure**:
- Keep SKILL.md focused on instructions (~200-400 lines)
- Use supporting files for extensive reference material
- Progressive disclosure: advanced topics in separate files
- Clear section hierarchy (H2 for main sections, H3 for subsections)

**Examples**:
- Show progression: simple → complex
- Include actual outputs/results
- Provide context for each example
- Use realistic data and scenarios
- For framework skills: include both Maven and Gradle

**Best Practices**:
- Language-specific conventions (Java vs Python vs TypeScript)
- Security considerations for the domain
- Performance guidelines and benchmarks
- SOLID principles where applicable
- Common anti-patterns to avoid
- Integration points with other tools/skills

**Documentation**:
- Assume reader has basic domain knowledge
- Define specialized terminology
- Link to related skills
- Include references to official documentation
- Credit sources and inspiration

## 🤖 Creating a New Agent

### Directory Structure
```
agents/[agent-name].md
```

### Agent File Format

```markdown
---
name: agent-name
description: Natural language description of when this agent should be used. Include specific use cases and trigger keywords.
tools: Read, Bash, Edit      # Optional: comma-separated. Omit to inherit all tools.
model: sonnet                 # Optional: sonnet, opus, haiku, or inherit
---

# Agent Name

You are a [specific role] expert. Your responsibilities include:
- Specific capability 1
- Specific capability 2
- Specific capability 3

## When to Use
- Clear trigger conditions
- Use cases and scenarios
- What problems it solves
- When NOT to use this agent

## Process
1. First step: Initial analysis or gathering information
2. Analysis: Investigation and understanding
3. Implementation: Action and solution
4. Verification: Testing and confirmation

## Guidelines
- Best practices for this domain
- Constraints and limitations
- Error handling and edge cases
- When to escalate back to main thread
- Performance considerations

## Example Workflow
Provide a concrete example showing typical usage
```

### Agent Guidelines

- **Specific description** with trigger keywords (not generic)
- **Single responsibility** focused on one domain
- **Tool restrictions** for security and focus (omit tools: field to inherit all)
- **Detailed process** with clear workflow steps
- **Include "proactively"** in description if agent should auto-detect usage
- **Comprehensive guidelines** covering edge cases

## ⚡ Creating a Slash Command

### File Structure
```
commands/[category/]command-name.md
```

### Command Format

```markdown
---
description: Brief command description for /help
allowed-tools: Bash(git:*), Read, Edit
argument-hint: [arg1] [arg2] [arg3]
---

## Command Description

Clear explanation of what the command does.

Use $1, $2, $3 for positional arguments.
Use $ARGUMENTS for all arguments combined.

Include bash execution with ! prefix to run commands:
!echo "Current branch: $(git branch --show-current)"

Result: 
Include expected output here.
```

### Command Guidelines
- Keep it simple and single-purpose
- Clear argument hints for autocomplete
- Restrict tools to only what's needed
- Use bash execution (!) for dynamic context
- Document expected behavior and output

## 📝 Contributing Documentation

### README Updates
- Keep main README current with new capabilities
- Update tables of contents as needed
- Add new skills/agents to appropriate sections

### Architecture Documentation
- Explain patterns and design decisions
- Provide diagrams where helpful
- Document integration points

### Bug Reports and Fixes
- Include concrete examples and reproduction steps
- Propose solutions when possible
- Reference related issues or PRs

## ✅ Quality Standards

### For Skills
- ✅ Specific, discoverable description with trigger keywords
- ✅ Clear "When to Use" section explaining context
- ✅ Practical examples with expected output
- ✅ Best practices section with domain insights
- ✅ All file paths use forward slashes (Unix style)
- ✅ No hardcoded credentials or secrets
- ✅ Proper formatting and clear structure
- ✅ Links to related skills where applicable
- ✅ ~300 lines max per file (use supporting files for expansion)

### For Agents
- ✅ Detailed role description and responsibilities
- ✅ Clear process/workflow with numbered steps
- ✅ Specific trigger conditions and use cases
- ✅ Tool restrictions appropriate for the role
- ✅ Comprehensive guidelines including edge cases
- ✅ Include "proactively" if auto-detection desired

### For Commands
- ✅ Simple, focused purpose (single file)
- ✅ Clear argument hints and description
- ✅ Tool restrictions for security
- ✅ Example usage with expected output

### For Documentation
- ✅ Clear, concise writing
- ✅ Proper Markdown formatting
- ✅ Links to relevant resources
- ✅ Examples where helpful

## 🔄 Submission Process

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/developer-kit-claude-code.git
cd developer-kit-claude-code
```

### 2. Create a Feature Branch
```bash
git checkout -b feat/your-skill-name
# or
git checkout -b fix/issue-description
# or
git checkout -b docs/improvement-description
```

### 3. Make Your Changes
- Follow the guidelines above for your contribution type
- Test thoroughly before submitting
- Ensure YAML/JSON syntax is valid
- Verify file paths are correct

### 4. Commit with Clear Messages
```bash
git commit -m "feat: add spring-boot-caching skill"
git commit -m "fix: improve spring-boot-actuator examples"
git commit -m "fix: fixed typo in REST API standards"
git commit -m "docs: update README with new skills"
```

### 5. Push to Your Fork
```bash
git push origin feat/your-skill-name
```

### 6. Create a Pull Request
- Describe what you're adding/fixing
- Link related issues (if any)
- Provide context for reviewers
- Include examples of the skill/agent in action

## 🎓 Learning From Existing Content

Study these examples to understand project conventions:

### Spring Boot Skills
- [spring-boot-actuator](./plugins/developer-kit-java/skills/spring-boot-actuator/SKILL.md) - Full-featured skill with supporting files
- [spring-boot-crud-patterns](./plugins/developer-kit-java/skills/spring-boot-crud-patterns/SKILL.md) - Architecture patterns
- [spring-boot-dependency-injection](./plugins/developer-kit-java/skills/spring-boot-dependency-injection/SKILL.md) - Best practices focus

### JUnit Test Skills
- [JUnit test guide](./plugins/developer-kit-java/docs/guide-skills-junit-test.md) - Comprehensive testing patterns

### LangChain4j Skills
- [LangChain4j guide](./plugins/developer-kit-java/docs/guide-skills-langchain4j.md) - AI integration patterns

### Existing Agents
- [spring-boot-code-review-expert](./plugins/developer-kit-java/agents/spring-boot-code-review-expert.md) - Example agent

## 🐛 Reporting Issues

When reporting issues, include:
- **Clear title**: What's the problem?
- **Description**: Context and impact
- **Steps to reproduce**: How to see the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What happens instead
- **Suggested fix**: Ideas for resolution (if applicable)

## 💬 Questions or Feedback?

- Open an issue for discussions
- Use GitHub Discussions for broader topics
- Check existing issues before creating new ones

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as this project (see `LICENSE`).

## 🙏 Thank You!

Thank you for contributing to making Claude Code more powerful and useful for developers everywhere!

---

**Last updated**: October 2024
