---
description: Refactor this skill based on the official Anthropic skill format guidelines.
argument-hint: [skill-name]
allowed-tools: Read, Grep, Glob
---

# Refactor Skill: $1

Refactor this skill based on the official Anthropic skill format guidelines.

Skill: $1

Issues found:

- Missing sections: Overview
- Content very long (consider moving detailed docs to references/)

Requirements:

1. Follow the structure from @.docs/skill-creator-official.md
2. Ensure SKILL.md has proper YAML frontmatter with required fields (name, description, allowed-tools, category, tags, version)
3. Use imperative/infinitive form (verb-first), not second person
4. Keep instructions concise and procedural
5. Use 'When to use' sections with specific trigger phrases
6. Include concrete examples progressing from basic to advanced
7. Add best practices and constraints sections
8. Progressive disclosure: move detailed info to references/ when appropriate
9. Ensure directory structure follows: scripts/, references/, assets/
10. If content is too long, move to references/ and summarize in SKILL.md
11. Maintain clarity, avoid ambiguity, and ensure correctness
12. Use markdown formatting appropriately

# Download Official Documentation

For downloading the official documentation for this skill, follow these steps:

- Use mcp tool context7 for downloading the documentation.
- Use `u2m -v https://docs.example.com/` to get gfficial documentation (https://spring.io/guides/gs/rest-service).

IMPORTANT: Clean & save the documentation in the references/ folder.

File to refactor: ./skills/$1/SKILL.md

Begin validation now for skill: $1
