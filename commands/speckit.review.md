---
description: Verify the successful completion of the code implementation by rigorously checking tasks, logic, tests, and code quality against specifications.
---

# IMPORTANT: This prompt must operate in read-only mode. The only file authorized for writing is `verification-report.md` inside the feature directory. No other files, folders, or resources may be modified, created, or deleted under any circumstances.

Given the current feature context, do this:

1. Run `.specify/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. Load and analyze the verification context:
    - **REQUIRED**: Read tasks.md to confirm all tasks are marked as completed [X] with no pending items.
    - **REQUIRED**: Read plan.md for tech stack, architecture, file structure, and implementation details.
    - **REQUIRED**: Read spec.md (or the feature specification file) for requirements, user stories, acceptance criteria, and success metrics.
    - **IF EXISTS**: Read data-model.md for entity compliance and relationships.
    - **IF EXISTS**: Read contracts/ for API specifications, ensuring all endpoints are implemented and match contracts exactly.
    - **IF EXISTS**: Read research.md for adherence to technical decisions and constraints.
    - **IF EXISTS**: Read quickstart.md for integration scenarios and end-to-end validation.

3. Perform strict logical verification:
    - Cross-reference implemented code against specification: Every requirement, user story, and acceptance criterion must be fully addressed with no gaps, ambiguities, or deviations.
    - Validate architecture and design: Ensure code follows the plan.md structure, uses specified tech stack/libraries, and maintains separation of concerns (e.g., models, services, endpoints).
    - Check data integrity: If data-model.md exists, confirm entities are implemented correctly with proper relationships, validations, and no logical inconsistencies.
    - API compliance: For each contract in contracts/, verify implementation matches schema, error handling, and business logic precisely—no partial matches or unhandled edge cases.

4. Execute comprehensive testing:
    - Run all unit, integration, and end-to-end tests: All must pass 100% with no failures, warnings, or skips. Coverage must meet or exceed plan.md thresholds (e.g., 90%+).
    - If quickstart.md exists, simulate integration scenarios and confirm expected outcomes.
    - Perform manual logical walkthroughs: Trace code paths for key features to ensure no dead code, infinite loops, or incorrect state management.
    - Enforce TDD compliance: Confirm tests were written before (or alongside) implementation, covering positive/negative cases, boundaries, and errors.

5. Enforce code quality standards:
    - Run linters, formatters, and static analyzers (e.g., ESLint, Prettier, TypeScript checks): Zero violations, warnings, or style inconsistencies allowed.
    - Security and performance audit: Scan for vulnerabilities (e.g., injection risks, unused dependencies), ensure efficient code (no O(n^2) where O(n) suffices), and check for memory leaks or scalability issues.
    - Documentation review: All code must have inline comments for complex logic; README/quickstart updates must reflect changes accurately.
    - Readability and maintainability: Code must be modular, DRY, with clear naming, no magic numbers/strings, and adherence to project constitution principles (e.g., from .specify/memory/constitution.md).

6. Generate a verification report:
    - **Pass/Fail status**: Strict binary—fail if any check (logical, test, quality) identifies issues; no partial credits.
    - Detailed findings: List passed/failed items by category (e.g., "Logical: All requirements met", "Tests: 100% pass rate", "Quality: 0 lint errors").
    - If failed, provide precise remediation steps with file paths and expected fixes.
    - Metrics summary: Test coverage %, lint score, compliance to spec (e.g., 100% requirements covered).

7. Halt and report immediately on any failure:
    - Do not proceed to "success" if errors exist—require fixes before re-verification.
    - If all checks pass, confirm feature readiness for deployment/review.

8. Completion output:
    - Write the verification report to `FEATURE_DIR/verification-report.md`.
    - Summarize status to user: "Verification PASSED" or "Verification FAILED: [brief reasons]".
    - Suggest commit message if passed (e.g., `feat: complete implementation and verification for [feature]`).

Note: This verification is non-negotiable and exhaustive—any deviation from specs, failing tests, or quality issues constitutes failure. Re-run after fixes until 100% compliance.
