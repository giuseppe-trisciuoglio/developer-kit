# Universal Documentation Updater - Usage Examples

This document provides practical examples of using the Universal Documentation Auto-Updater skill in various scenarios.

## Table of Contents

1. [Basic Workflow](#basic-workflow)
2. [Release Preparation](#release-preparation)
3. [Continuous Documentation Sync](#continuous-documentation-sync)
4. [Multi-Plugin Projects](#multi-plugin-projects)
5. [Troubleshooting](#troubleshooting)

## Basic Workflow

### Scenario: Adding a New Feature

After implementing a new feature and committing your changes:

```
User: "Update docs for the new DynamoDB skill I just added"
```

**Expected Output:**

```bash
Latest release tag: v2.4.1
Current branch: develop
Version detected: 2.4.1
Comparing: v2.4.1 -> develop

Commits since v2.4.1: 3

Changed files:
  A plugins/developer-kit-typescript/skills/dynamodb-toolbox-patterns/SKILL.md
  A plugins/developer-kit-typescript/skills/dynamodb-toolbox-patterns/references/schema.md
  M plugins/developer-kit-typescript/.claude-plugin/plugin.json
```

**Generated CHANGELOG Entry:**

```markdown
## [Unreleased]

### Added
- **New DynamoDB-Toolbox v2 skill** (`developer-kit-typescript`):
  - `dynamodb-toolbox-patterns`: TypeScript patterns for DynamoDB-Toolbox v2
  - Includes schema/table/entity modeling and query/scan access patterns
```

## Release Preparation

### Scenario: Preparing for v2.5.0 Release

Before creating a release tag, ensure all documentation is up to date:

```
User: "Prepare documentation for v2.5.0 release"
```

**Analysis Summary:**

```bash
Latest release tag: v2.4.1
Commits since v2.4.1: 47

Commit breakdown:
- Features: 15
- Bug fixes: 8
- Breaking changes: 3
- Documentation: 12
- Refactoring: 9
```

**Proposed Documentation Updates:**

```markdown
## Proposed Documentation Updates

### Version Information
- Previous release: v2.4.1
- Current branch: main
- Commits analyzed: 47

### Files to Update
- [x] CHANGELOG.md - Add [2.5.0] section with date
- [x] README.md - Update skills list, version badges
- [ ] plugins/developer-kit-java/docs/ - No changes needed
- [ ] plugins/developer-kit-aws/docs/ - Update SAM examples

### Summary of Changes
**Added**: 5 new skills, 10 new features
**Changed**: 3 component enhancements
**Fixed**: 8 bug fixes
**Breaking**: 3 breaking changes (migration notes required)
```

## Continuous Documentation Sync

### Scenario: Regular Documentation Maintenance

Keeping documentation synchronized after regular development iterations:

```
User: "Sync documentation with latest changes"
```

**Quick Analysis (Small Changes):**

```bash
Latest release tag: v2.5.0
Commits since v2.5.0: 5

Changes:
  M plugins/developer-kit-core/skills/github-issue-workflow/SKILL.md
  M plugins/developer-kit-core/commands/devkit.brainstorm.md
```

**Generated Update:**

```markdown
## [Unreleased]

### Changed
- **GitHub Issue Workflow skill**: Enhanced security handling for untrusted issue content
- **Brainstorm command**: Added AskUserQuestion gates for user confirmation
```

## Multi-Plugin Projects

### Scenario: Developer Kit Multi-Plugin Structure

When working with a multi-plugin repository like the developer-kit:

```
User: "Update all docs across all plugins"
```

**Discovered Documentation Structure:**

```bash
Documentation folders found:
  - plugins/developer-kit-java/docs/
  - plugins/developer-kit-typescript/docs/
  - plugins/developer-kit-aws/docs/
  - plugins/developer-kit-python/docs/
  - plugins/developer-kit-php/docs/

Documentation files found:
  - README.md
  - CHANGELOG.md
  - CONTRIBUTING.md
  - CLAUDE.md
```

**Per-Plugin Changes Detected:**

```markdown
## [Unreleased]

### Added

**developer-kit-java:**
- `spring-boot-actuator`: Production-ready monitoring patterns
- `spring-boot-cache`: Caching configuration patterns

**developer-kit-typescript:**
- `dynamodb-toolbox-patterns`: DynamoDB-Toolbox v2 integration
- `drizzle-orm-patterns`: Drizzle ORM comprehensive patterns

**developer-kit-aws:**
- `aws-sam-bootstrap`: SAM project initialization patterns

### Changed

**developer-kit-core:**
- Enhanced all devkit commands with mandatory user confirmation gates
- Added Universal Documentation Updater skill

### Fixed

**developer-kit-java:**
- Fixed unit-test-config-properties skill examples

**developer-kit-typescript:**
- Fixed react-patterns skill hooks documentation
```

## Troubleshooting

### No Tags Found

**Error:**
```bash
No git tags found. This skill requires at least one release tag.
```

**Solution:**
```bash
# Create an initial release tag
git tag -a v1.0.0 -m "Initial release"

# Or tag the latest commit as a release
git tag -a v0.1.0 -m "Pre-release"
```

### Empty Diff Results

**Symptom:** No changes detected despite recent commits

**Possible causes:**
1. Current branch is at the same commit as the latest tag
2. No commits exist between tag and HEAD

**Verification:**
```bash
# Check commit count
git rev-list --count v2.4.1..HEAD

# Check current branch vs tag
git log v2.4.1..HEAD --oneline
```

### Non-Conventional Commits

**Issue:** Commits don't follow conventional commit format

**Example problematic commits:**
```
abc1234: updated stuff
def5678: fix bug
ghi9012: add feature
```

**Result:** Categorization may be less accurate

**Workaround:** The skill will attempt to categorize by message content, but results may be less precise. Consider using conventional commits for better changelog generation.

### Custom Changelog Format

**Issue:** Project uses a different changelog format than Keep a Changelog

**Solution:**
1. The skill generates entries following Keep a Changelog standard
2. Review the generated output and adapt to your project's format
3. Consider migrating to Keep a Changelog for consistency

## Advanced Usage

### Filtering by Component

To focus on specific plugin changes:

```bash
# Get changes for specific plugin only
git diff v2.4.1..HEAD -- plugins/developer-kit-java/

# Get changes for specific file types
git diff v2.4.1..HEAD -- "*.md"
```

### Custom Version Detection

For projects with non-standard tag formats:

```bash
# Get tags matching specific pattern
git tag -l "v*" | sort -V | tail -1

# Get tags with custom format
git tag -l "release-*" | sort -V | tail -1
```

### Verifying Generated Changelog

Before committing changes:

```bash
# Preview changelog changes
git diff CHANGELOG.md

# Verify markdown syntax
# (Use markdown linter if available)
```

## Best Practices

1. **Always verify before writing**: Show the user what will change before applying updates
2. **Follow Keep a Changelog**: Maintain consistent changelog formatting
3. **Categorize properly**: Use correct categories (Added, Changed, Fixed, etc.)
4. **Be specific**: Include plugin/component names in changelog entries
5. **Preserve structure**: Maintain existing documentation structure and style
6. **Reference commits**: Include commit hashes for traceability when helpful
7. **Handle breaking changes**: Clearly highlight breaking changes with migration notes
8. **Update version refs**: Keep version numbers consistent across documentation

## Constraints and Warnings

1. **Requires git tags**: This skill only works if the repository has at least one release tag
2. **Read-only analysis**: The skill analyzes changes but asks before writing
3. **Manual review required**: Generated changelog entries should be reviewed for accuracy
4. **Conventional commits**: Works best with projects using conventional commit format
5. **Does not create tags**: This skill updates docs but does not create release tags
6. **No auto-commit**: Documentation changes are prepared but not committed automatically
7. **Project-specific patterns**: Some projects may have custom changelog formats to respect
8. **File paths**: All file paths use forward slashes (Unix style) for cross-platform compatibility

## Tips for Best Results

1. **Use Conventional Commits**: Follow conventional commit format for better categorization
2. **Commit Frequently**: Small, focused commits make for clearer changelog entries
3. **Tag Releases**: Always create tags for releases (not just branches)
4. **Review Generated Content**: Always review and edit generated changelog entries
5. **Keep Descriptive Commit Messages**: Include context in commit messages for better documentation

## Sample Session

```
User: Update docs since last release

Claude: Let me analyze the changes since the last release...

[Latest release tag: v2.4.1]
[Commits analyzed: 12]

I found the following changes:
- 3 new skills added
- 2 bug fixes
- 1 documentation update

Here's the proposed changelog entry:

## [Unreleased]

### Added
- **New Universal Documentation Updater skill** (`developer-kit-core`):
  - Automatically updates project documentation based on git diff analysis
  - Supports CHANGELOG.md, README.md, and documentation folders

### Fixed
- **Plugin discovery**: Fixed marketplace.json missing developer-kit-tools entry

Should I apply these changes to CHANGELOG.md and README.md?

User: Yes, apply changes

Claude: Updating documentation files...

Changes applied:
✓ Updated CHANGELOG.md
✓ Updated README.md skills list

Git diff preview:
[Shows git diff of changes]
```
