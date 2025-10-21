# Developer Kit for Claude Code

This repository is a starter kit for building "skills" and "agents" for Claude Code. The current content focuses on patterns, conventions, and agents for Java projects (Spring Boot, JUnit), but the kit is designed to be extensible and multi-language (PHP, TypeScript, Python, etc.).

Goal
- Provide reusable examples of skills and agents that automate development tasks: code review, REST API guidance, testing patterns, snippet generation, and more.
- Offer a modular kit that other developers can quickly extend for new languages and frameworks.

Repository contents
- agents/: ready-to-use agents — currently contains specialist agents for Spring Boot.
  - `agents/spring-boot-code-review-specialist.md` — definition of an agent for reviewing Spring Boot projects.

- skills/: a collection of skills organized by topic and language.
  - `skills/spring-boot-patterns/SKILL.md` — patterns and best practices for Spring Boot.
  - `skills/spring-boot-rest-api-standards/SKILL.md` — REST API guidelines for Spring Boot.
  - `skills/spring-boot-test-patterns/SKILL.md` — testing patterns for Spring applications.
  - `skills/junit-test-patterns/SKILL.md` — examples and conventions for JUnit.

Current status and language roadmap
- Current status: most skills and agents contain Java examples and conventions (Spring Boot, JUnit).
- Roadmap: we plan to add dedicated skills and agents for:
  - PHP (e.g., Laravel, Symfony)
  - TypeScript (Node.js, NestJS, Express)
  - Python (Django, FastAPI)

How to contribute a new language
1. Create a folder under `skills/` named after the language or framework (e.g. `skills/php-laravel/`).
2. Add a `SKILL.md` that describes: purpose, conventions, sample exercises, useful snippets, and quality metrics.
3. If a language-specific agent is needed, add a file under `agents/` with a descriptive suffix (e.g. `agents/php-security-review-specialist.md`).
4. Follow the structure and format used by existing skills to keep consistency.

Maintainer guidelines
- Keep each skill focused (single responsibility or area of expertise).
- Provide minimal examples, expected behavioral tests, and integration instructions for Claude Code.
- Document external dependencies and the commands required to run local examples.

Quick example: adding TypeScript support
- Create `skills/typescript-node-patterns/SKILL.md` containing:
  - routing patterns, error handling, testing best practices (e.g., Jest)
  - scaffolding examples and code-review snippets
- Add `agents/typescript-code-review-specialist.md` if you want an agent that performs automated reviews tailored to TypeScript code.

Installation and usage (brief)
- This repository contains definitions and documentation usable in Claude Code; actual installation of skills depends on your Claude Code workflow.
- To test skills locally, copy the contents of the `skills/` and `agents/` folders into your Claude Code environment or follow your deployment instructions to upload new skills.

Contributing
- Open a pull request with the new `skills/<language>/` folder or new `agents/` file and include:
  - a short description of the goal
  - sample input/output expectations
  - any references or external resources

License
- The project inherits the main license in the repository root (`LICENSE`). Check that file for details.

Contact
- For questions or integration proposals, open an issue in this repository or create a PR describing the change.

---
Version: 1.0 — Initial Java support, designed to be extended to other languages


6. langchain4j-vector-stores-configuration
9. langchain4j-testing-strategies