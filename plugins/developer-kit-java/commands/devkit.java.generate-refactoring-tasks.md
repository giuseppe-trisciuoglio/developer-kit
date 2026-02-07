---
allowed-tools: Read, Grep, Glob, Write
argument-hint: "[bounded-context-name]"
description: Generates a comprehensive refactoring task list for a specific Bounded Context in project and saves it to a file. Use when planning refactoring work for a bounded context.
---

# Refactoring Task List Generator for Bounded Context

Analyze the bounded context **$1** in the project to create a complete refactoring task list and save it to a file.

Perform the following steps:

1. **Bounded Context Analysis**:
   - Search for all Java files in the package `$1`
   - Identify all TODO, FIXME comments, and technical debt indicators
   - Analyze DDD architecture and compliance with SOLID principles
   - Identify incomplete implementations and placeholder code

2. **Map the Structure**:
   - List all found files by layer (domain, application, infrastructure, presentation)
   - Identify dependencies between components
   - Analyze entities, aggregates, value objects, services, repositories, controllers
   - Detect architectural patterns and violations

3. **Generate Organized Task List**:
   Create a task list with this exact structure:

   ```markdown
   # $1 Bounded Context Refactoring Tasks
   > Generated on: 2025-11-24

   ## Overview
   List of refactoring activities to be performed in the $1 bounded context...

   ## Current State
   - **Identified TODOs**: [number] refactoring/clean comments
   - **Missing Documentation**: [number] classes without Javadoc
   - **Incomplete Implementations**: [number] methods with placeholders
   - **Unused Methods**: [number] methods to remove

   ## Task List

   ### Priority 1: Documentation and Critical Functionality

   #### 1.1 Complete Javadoc Documentation
   [List of checkboxes for each file with TODO javadoc]

   #### 1.2 Implement Incomplete Functionality
   [List of checkboxes for each placeholder method to implement]

   #### 1.3 Remove Unused Code
   [List of checkboxes for each unused method to remove]

   ### Priority 2: Domain Model Enhancement
   [Tasks to improve domain model, value objects, aggregates]

   ### Priority 3: Architecture Improvements
   [Tasks to improve architecture, ports, interfaces]

   ### Priority 4: Infrastructure Cleanup
   [Tasks for database cleanup, configuration, imports]

   ## Execution Notes
   ### Task Dependencies
   [Logical dependencies between priorities]

   ### Time Estimate
   [Days estimate for each priority]

   ### Validation Checklist for each Task
   [Standard validation criteria]
   ```

4. **Specific Details**:
   - For each file specify: filename, package, type of issue
   - For each method specify: signature, current issue, fix required
   - For each TODO specify: line number, type of fix, priority
   - Include full file paths

5. **Output Format**:
   - Use checkboxes `[ ]` for each task
   - Be specific about what to do
   - Clear priorities and logical dependencies
   - Realistic time estimates
   - Java code examples where necessary

6. **Focus on**:
   - Concrete and actionable tasks
   - Specific files and line numbers
   - Clear and measurable actions
   - DDD architecture compliance
   - SOLID principles application

7. **Save Output**:
   - Save the generated content to a file named `docs/refactoring/$1-refactoring-tasks.md`
   - Create the directory `docs/refactoring` if it doesn't exist
   - Confirm the file creation to the user

Do not include abstract sections like QA, theoretical metrics, or generic risk assessments. Focus only on practical tasks to implement.

## Execution Instructions

**Agent Selection**: To execute this generation task, use the following approach:
- Primary: Use `general-purpose` agent with specialized knowledge of the task domain
- Or use appropriate specialized agent if available for the specific generation task
