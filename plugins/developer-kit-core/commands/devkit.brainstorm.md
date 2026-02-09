---
description: Provides guided brainstorming capability to transform ideas into fully formed designs with documentation and next-step recommendations. Use when starting a new feature or exploring design alternatives.
argument-hint: "[ idea-description ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Brainstorming

Provides guided brainstorming to transform ideas into fully formed designs with professional documentation and next-step recommendations.

## Overview

This command helps developers transform an initial idea into a comprehensive, validated design through a systematic 9-phase process:

1. **Context Discovery** - Understand the project state and initial idea
2. **Idea Refinement** - Deeply understand requirements through structured dialogue
3. **Approach Exploration** - Present 2-3 approaches with trade-offs
4. **Codebase Exploration** - Analyze existing code for design constraints
5. **Design Presentation** - Present validated design sections incrementally
6. **Documentation Generation** - Generate professional design documents
7. **Document Review** - Quality review by specialist agent
8. **Next Steps Recommendation** - Suggest appropriate next command
9. **Summary** - Document what was accomplished

Use this command when starting a new feature, exploring design alternatives, or planning significant changes.

## Usage

```bash
/developer-kit:devkit.brainstorm [idea-description]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `idea-description` | No | Description of the idea or feature to brainstorm |

## Current Context

The command will automatically gather context information when needed:
- Current git branch and status
- Recent commits and changes
- Available when the repository has history

### Argument Details

**idea-description**
- Purpose: Describes the initial idea, feature, or problem to solve
- Format: Free text describing the concept
- Default: If not provided, the command will ask for it interactively
- Examples: "Add user authentication", "Refactor payment module", "Design caching strategy"

---

You are helping a developer transform an idea into a fully formed design. Follow a systematic approach: understand the project
context, explore the idea through targeted questions, explore existing code, propose alternative approaches, present the design
incrementally, generate professional documentation, review the document, and recommend the next development command.

## Core Principles

- **One question at a time**: Don't overwhelm with multiple questions
- **Multiple choice preferred**: Easier to answer than open-ended when possible
- **YAGNI ruthlessly**: Remove unnecessary features from all designs
- **Explore alternatives**: Always propose 2-3 approaches with trade-offs
- **Incremental validation**: Present design in sections, validate each
- **Code-based design**: Base design decisions on actual codebase exploration
- **Professional documentation**: Use specialist agent for high-quality documents
- **Be flexible**: Go back and clarify when something doesn't make sense
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates

---

## Phase 1: Context Discovery

**Goal**: Understand the current project state and the initial idea

**Initial idea**: $ARGUMENTS

**Actions**:

1. Create todo list with all phases
2. Explore the current project state:
    - Read recent commits to understand what's being worked on
    - Check for existing documentation (README, docs/, existing plans)
    - Identify the technology stack and architecture patterns
    - Look for related features or similar implementations
3. If the idea is unclear, ask the user for:
    - What problem are they trying to solve?
    - What is the high-level goal?
    - Any initial thoughts or constraints?

---

## Phase 2: Idea Refinement

**Goal**: Deeply understand the idea through structured dialogue

**CRITICAL**: This phase builds the foundation for the design. DO NOT rush.

**Actions**:

1. Ask questions **one at a time** to refine the idea
2. **Use the AskUserQuestion tool with multiple choice options when possible**
3. Focus on understanding:
    - **Purpose**: What is this trying to achieve?
    - **Constraints**: Are there technical, time, or resource constraints?
    - **Success Criteria**: How will we know if this is successful?
    - **Scope**: What is in scope and what is explicitly out of scope?
    - **Users**: Who will use this and how?

**Example structured questions**:

- "What is the primary success metric for this feature?"
- "Which constraint is most important: development time, performance, or maintainability?"
- "Who are the primary users of this feature?"

4. **Wait for each answer before asking the next question**
5. When the idea is clear, summarize understanding and get confirmation

---

## Phase 3: Approach Exploration

**Goal**: Present 2-3 different approaches with trade-offs

**Actions**:

1. Based on the refined idea, develop 2-3 distinct approaches:
    - **Approach A**: Simple/MVP (fastest to implement, may lack some features)
    - **Approach B**: Balanced (good feature set, reasonable complexity) - **typically your recommendation**
    - **Approach C**: Comprehensive (full-featured, more complex)

2. For each approach, describe:
    - High-level architecture
    - Key components
    - Pros (benefits, advantages)
    - Cons (drawbacks, risks)
    - Estimated complexity

3. **Use the AskUserQuestion tool to present the approaches**:
    - Lead with your recommended option
    - Explain your reasoning
    - Ask which approach they prefer

4. **Wait for user selection before proceeding**

---

## Phase 4: Codebase Exploration

**Goal**: Deep understanding of existing codebase before finalizing the design

**CRITICAL**: This phase ensures the design is based on actual codebase reality, not assumptions.

**Actions**:

1. Use the Task tool to launch a code-explorer subagent to analyze the existing codebase:

```
Task(
  description: "Explore codebase for design context",
  prompt: "Explore the codebase comprehensively to support the following design: [design summary]

    Focus on:
    1. Existing patterns and conventions used in similar features
    2. Architecture layers and module organization
    3. Key integration points and dependencies
    4. Data models and persistence patterns
    5. API design patterns (if applicable)
    6. Testing patterns and infrastructure
    7. Configuration and environment setup
    8. Any potential conflicts or integration challenges

    Return:
    - List of key files to read for deep understanding
    - Summary of relevant patterns found
    - Any recommendations or considerations for the design",
  subagent_type: "developer-kit:general-code-explorer"
)
```

2. Once the agent returns, read all identified critical files
3. Incorporate findings into the design understanding
4. If significant new information is discovered that affects the design:
    - **Use the AskUserQuestion tool to discuss with the user**
    - Potentially revisit Phase 3 (Approach Exploration) if needed

---

## Phase 5: Design Presentation

**Goal**: Present the approved design in validated sections

**DO NOT START WITHOUT APPROACH APPROVAL**

**Actions**:

1. Once the approach is selected and codebase is explored, present the design in sections of 200-300 words each
2. Incorporate findings from Phase 4 (Codebase Exploration) into the design
3. Cover the following areas in separate sections:

   **Section 1: Architecture Overview**
   - System architecture and how it fits into existing codebase
   - Key architectural patterns and principles (based on actual patterns found)
   - Integration points with existing systems

   **Section 2: Components and Modules**
   - Main components or classes involved
   - Responsibilities of each component
   - Relationships between components
   - Alignment with existing module structure

   **Section 3: Data Flow**
   - How data flows through the system
   - Key data structures
   - State management considerations

   **Section 4: Error Handling**
   - Expected failure scenarios
   - Error handling strategy
   - User-facing error messages vs. internal errors

   **Section 5: Testing Strategy**
   - Key test scenarios
   - Testing approach (unit, integration, e2e)
   - Edge cases to consider

3. **After each section, use the AskUserQuestion tool**:
    - "Does this section look right so far?"
    - Options: "Yes, continue", "Needs revision", "Go back to earlier section"

4. **Wait for validation before proceeding to the next section**

---

## Phase 6: Documentation Generation

**Goal**: Generate professional documentation using the document generator specialist

**Actions**:

1. Compile all validated design sections into a comprehensive design brief
2. Use the Task tool to launch the document-generator-expert subagent:

```
Task(
  description: "Generate design document",
  prompt: "Generate a professional design document based on the following validated design:

    **Design Title**: [title]
    **Date**: [current date]

    **Overview**: [brief summary]

    **Requirements**:
    - Functional: [list]
    - Non-Functional: [list]
    - Success Criteria: [list]

    **Approach Selected**: [name with rationale]

    **Architecture**: [from Section 1]
    **Components**: [from Section 2]
    **Data Flow**: [from Section 3]
    **Error Handling**: [from Section 4]
    **Testing Strategy**: [from Section 5]

    **Out of Scope**: [list]
    **Open Questions**: [list]

    Create a comprehensive, well-formatted design document and save it to: docs/plans/YYYY-MM-DD--design.md

    The document should be:
    - Professional and clearly formatted
    - DO NOT provide or request time estimates or implementation timelines
    - Complete with all sections
    - Ready for team review
    - Using proper markdown structure",
  subagent_type: "developer-kit:document-generator-expert"
)
```

3. Wait for the document generator to complete
4. Verify the document was created successfully
5. Update todos

---

## Phase 7: Document Review

**Goal**: Review the generated document for quality and completeness using specialist agent

**Actions**:

1. Use the Task tool to launch a code-reviewer subagent to review the document:

```
Task(
  description: "Review design document quality",
  prompt: "Review the design document at docs/plans/YYYY-MM-DD--design.md for:

    1. **Completeness**: All required sections are present (Overview, Requirements, Approach Selected, Architecture, Components, Data Flow, Error Handling, Testing Strategy, Out of Scope, Open Questions)

    2. **Quality**: Content is clear, specific, and actionable

    3. **Alignment**: Document matches the validated design from the brainstorming session:
       - Architecture overview is consistent with codebase patterns
       - Components and modules are properly defined
       - Data flow is logical and complete
       - Error handling covers edge cases
       - Testing strategy is comprehensive

    4. **Formatting**: Proper markdown structure, consistent formatting

    5. **Clarity**: Language is professional, concise, and unambiguous

    Provide:
    - Overall assessment (Excellent / Good / Needs Revision)
    - List of any missing sections or content
    - Specific issues found (if any)
    - Recommendations for improvement (if needed)",
  subagent_type: "developer-kit:general-code-reviewer"
)
```

2. Once the agent returns, synthesize the review findings

3. **Use the AskUserQuestion tool to present the review findings**:

   Present options based on agent assessment:
   - **Option A**: Document is excellent, proceed to next steps
   - **Option B**: Minor revisions needed (agent will specify what)
   - **Option C**: Major revisions needed (regenerate with corrections)

4. If revisions are needed:
    - For minor revisions: Edit the document directly based on agent feedback
    - For major revisions: Re-run Phase 6 with updated instructions from agent
    - Optionally: Re-run Phase 7 with another review if significant changes were made

5. Once approved, mark documentation phase complete

---

## Phase 8: Next Steps Recommendation

**Goal**: Recommend the appropriate next development command

**Actions**:

1. Analyze the design to determine the best next step:

   **For new features**: Recommend `/developer-kit:devkit.feature-development`
   - Use when: Creating new functionality, adding features, implementing the design from scratch
   - Arguments: Provide a concise summary of the feature description

   **For fixing issues**: Recommend `/developer-kit:devkit.fix-debugging`
   - Use when: The design addresses a bug, error, or production issue
   - Arguments: Provide the issue description or error message

   **For improving code**: Recommend `/developer-kit:devkit.refactor`
   - Use when: The design involves restructuring, reorganizing, or improving existing code
   - Arguments: Provide the refactoring description

2. **Use the AskUserQuestion tool to present the recommendation**:

   Present options:
   - **Option A**: [Recommended command] with pre-filled arguments
   - **Option B**: Choose a different command manually
   - **Option C**: Exit and review the design document first

3. Include the pre-filled command that can be copied/pasted:

```bash
# Example for feature development
/developer-kit:devkit.feature-development [concise feature description based on design]

# Example for debugging
/developer-kit:devkit.fix-debugging [issue description based on design]

# Example for refactoring
/developer-kit:devkit.refactor [refactoring description based on design]
```

4. If user chooses to continue, remind them:
   - The design document has been saved at `docs/plans/YYYY-MM-DD--design.md`
   - They can reference this during implementation

---

## Phase 9: Summary

**Goal**: Document what was accomplished

**Actions**:

1. Mark all todos complete
2. Summarize:
    - **Original Idea**: What was brainstormed
    - **Approach Selected**: Which approach was chosen and why
    - **Codebase Analysis**: Key findings from codebase exploration
    - **Design Created**: Key aspects of the design
    - **Document Location**: `docs/plans/YYYY-MM-DD--design.md`
    - **Document Review**: Review outcome and any revisions made
    - **Recommended Next Step**: The suggested command with arguments
    - **Alternative Paths**: Other commands that could be used if priorities change

---

## Practical Examples

```bash
# Simple feature idea
/developer-kit:devkit.brainstorm Add user authentication with JWT tokens

# Complex feature idea
/developer-kit:devkit.brainstorm Implement real-time notifications using WebSockets

# Refactoring idea
/developer-kit:devkit.brainstorm Refactor the payment processing module to be more maintainable

# Bug fix design
/developer-kit:devkit.brainstorm Design a fix for the race condition in order processing

# Performance improvement
/developer-kit:devkit.brainstorm Design a caching strategy to reduce API response times

# Integration idea
/developer-kit:devkit.brainstorm Integrate Stripe payment processing for subscriptions

# Architecture idea
/developer-kit:devkit.brainstorm Design a microservices architecture for the reporting module
```

## Integration with Development Commands

This brainstorming command is designed to feed directly into the development workflow:

### Output Flow

```
/developer-kit:devkit.brainstorm
    ↓
Phase 4: Codebase Exploration (code-explorer agent)
    ↓
Phase 5: Design Presentation (validated incrementally)
    ↓
Phase 6: Documentation (document-generator-expert agent)
    ↓
Phase 7: Document Review (quality verification)
    ↓
[Creates: docs/plans/YYYY-MM-DD--design.md]
    ↓
[Recommends next command with pre-filled arguments]
    ↓
User executes recommended command:
  - /developer-kit:devkit.feature-development [description]
  - /developer-kit:devkit.fix-debugging [description]
  - /developer-kit:devkit.refactor [description]
```

### Design Document as Reference

The design document created by this command serves as:

1. **Reference during implementation**: The development commands can read the design document for context
2. **Communication tool**: Can be shared with team members for review
3. **Documentation**: Becomes part of the project's design history
4. **Testing guide**: The testing strategy section informs test creation

### Re-entering Brainstorming

If implementation reveals design issues, you can re-run `/developer-kit:devkit.brainstorm` with the revised idea:
- The previous design document will be preserved
- A new design document will be created with the current date
- You can reference the previous design during the new brainstorming session

## Todo Management

Throughout the process, maintain a todo list like:

```
[ ] Phase 1: Context Discovery
[ ] Phase 2: Idea Refinement
[ ] Phase 3: Approach Exploration
[ ] Phase 4: Codebase Exploration
[ ] Phase 5: Design Presentation
    [ ] Section 1: Architecture Overview
    [ ] Section 2: Components and Modules
    [ ] Section 3: Data Flow
    [ ] Section 4: Error Handling
    [ ] Section 5: Testing Strategy
[ ] Phase 6: Documentation Generation
[ ] Phase 7: Document Review
[ ] Phase 8: Next Steps Recommendation
[ ] Phase 9: Summary
```

Update the status as you progress through each phase and section.

---

**Note**: This command follows a collaborative, iterative approach with specialist agents to ensure designs are:
- Based on actual codebase exploration (not assumptions)
- Well-thought-out and validated incrementally
- Documented professionally with specialist assistance
- Reviewed for quality before proceeding
- Ready for implementation with clear next steps

--- 

## Examples

### Example 1: Simple Feature Idea

```
/developer-kit:devkit.brainstorm Add user authentication with JWT tokens
```

### Example 2: Complex Feature

```
/developer-kit:devkit.brainstorm Implement real-time notifications using WebSockets
```

### Example 3: Refactoring

```
/developer-kit:devkit.brainstorm Refactor the payment processing module to be more maintainable
```