---
description: Create GitHub pull request with branch creation, commits, and detailed description
category: version-control-git
allowed-tools: Bash(git *), Bash(gh *)
argument-hint: [pr-title] [target-branch] [language]
---

# Create GitHub Pull Request

Create a new branch, commit changes, and submit a pull request with comprehensive description.

## Current Context

- **Current Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Remote Repository**: !`git config --get remote.origin.url`
- **Modified Files**: !`git diff --name-only`

## Configuration

**Arguments received**: `$ARGUMENTS`

**$1**: PR title (optional - will be generated if not provided)
**$2**: Target branch (optional - defaults to `main` or `master`)
**$3**: Language for PR description (optional - defaults to `en`)

**Supported languages**: `en`, `it`, `es`, `fr`, `de`

## Phase 1: Pre-Flight Validation

### 1.1 Check Working Directory

Verify git repository and working directory status:

```bash
# Verify git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    exit 1
fi

# Check for uncommitted changes
if [ -z "$(git status --porcelain)" ]; then
    echo "Error: No changes to commit"
    exit 1
fi

# Verify remote repository exists
if ! git config --get remote.origin.url > /dev/null 2>&1; then
    echo "Error: No remote repository configured"
    exit 1
fi

# Check GitHub CLI authentication
if ! gh auth status > /dev/null 2>&1; then
    echo "Error: GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi
```

### 1.2 Determine Target Branch

```bash
# Detect default branch
TARGET_BRANCH="${2:-$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)}"
if [ -z "$TARGET_BRANCH" ]; then
    TARGET_BRANCH="main"
fi

echo "Target branch: $TARGET_BRANCH"
```

## Phase 2: Change Analysis

### 2.1 Analyze Modified Files

```bash
# Get list of modified files
MODIFIED_FILES=$(git diff --name-only)
STAGED_FILES=$(git diff --cached --name-only)
UNTRACKED_FILES=$(git ls-files --others --exclude-standard)

echo "Modified files:"
echo "$MODIFIED_FILES"
echo ""
echo "Staged files:"
echo "$STAGED_FILES"
echo ""
echo "Untracked files:"
echo "$UNTRACKED_FILES"
```

### 2.2 Categorize Changes

Analyze changes by type:

- **Feature additions**: New files, new functionality
- **Bug fixes**: Corrections to existing code
- **Refactoring**: Code improvements without behavior changes
- **Documentation**: README, comments, docs
- **Configuration**: Build files, properties, YAML configs
- **Tests**: Test files and test data

## Phase 3: Branch Creation

### 3.1 Generate Branch Name

```bash
# Generate branch name from PR title or changes
if [ -n "$1" ]; then
    BRANCH_NAME=$(echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
else
    # Generate from changed files
    MAIN_CHANGE=$(echo "$MODIFIED_FILES" | head -1 | xargs dirname | sed 's/\//-/g')
    BRANCH_NAME="feature/${MAIN_CHANGE}-$(date +%s)"
fi

# Ensure unique branch name
COUNTER=1
ORIGINAL_BRANCH=$BRANCH_NAME
while git show-ref --verify --quiet refs/heads/$BRANCH_NAME; do
    BRANCH_NAME="${ORIGINAL_BRANCH}-${COUNTER}"
    ((COUNTER++))
done

echo "Branch name: $BRANCH_NAME"
```

### 3.2 Create and Switch Branch

```bash
# Create new branch
git checkout -b "$BRANCH_NAME"

echo "Created and switched to branch: $BRANCH_NAME"
```

## Phase 4: Commit Strategy

### 4.1 Analyze Commit Splitting

Determine if changes should be split into multiple commits:

**Single commit when**:
- Single file modified
- Related changes in same component
- Small focused change

**Multiple commits when**:
- Changes span multiple features
- Mix of feature and tests
- Configuration and code changes
- Documentation and implementation

### 4.2 Create Commits

```bash
# Stage all changes
git add -A

# Get diff statistics
TOTAL_ADDITIONS=$(git diff --cached --numstat | awk '{s+=$1} END {print s}')
TOTAL_DELETIONS=$(git diff --cached --numstat | awk '{s+=$2} END {print s}')
FILES_CHANGED=$(git diff --cached --name-only | wc -l)

echo "Changes: +$TOTAL_ADDITIONS -$TOTAL_DELETIONS across $FILES_CHANGED files"
```

### 4.3 Generate Commit Messages

Follow Conventional Commits specification:

```
<type>(<scope>): <description>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Build, dependencies, tooling
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `security`: Security improvements

**Example commits**:
```bash
# Feature commit
git commit -m "feat(user-service): add email verification functionality

- Implement email verification service
- Add verification token generation
- Create email template
- Add integration tests

Closes #123"

# Bug fix commit
git commit -m "fix(auth): resolve JWT token expiration issue

JWT tokens were expiring prematurely due to timezone
miscalculation. Updated to use UTC consistently.

Fixes #456"

# Refactoring commit
git commit -m "refactor(repository): simplify user query methods

- Remove duplicate code
- Extract common query logic
- Improve method naming
- Add Javadoc comments"
```

## Phase 5: Push and PR Creation

### 5.1 Push Branch

```bash
# Push to remote
git push -u origin "$BRANCH_NAME"

echo "Pushed branch to remote: $BRANCH_NAME"
```

### 5.2 Generate PR Description

Create PR description based on language preference:

**English Template**:
```markdown
## Description

Brief description of changes and motivation.

## Changes

- Change 1
- Change 2
- Change 3

## Testing

Description of testing performed:
- Unit tests added/updated
- Integration tests verified
- Manual testing completed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Backward compatible
```

**Italian Template**:
```markdown
## Descrizione

Breve descrizione delle modifiche e motivazione.

## Modifiche

- Modifica 1
- Modifica 2
- Modifica 3

## Test

Descrizione dei test eseguiti:
- Test unitari aggiunti/aggiornati
- Test di integrazione verificati
- Test manuali completati

## Checklist

- [ ] Il codice segue le linee guida del progetto
- [ ] Test aggiunti/aggiornati e funzionanti
- [ ] Documentazione aggiornata
- [ ] Nessuna breaking change
- [ ] Retrocompatibile
```

### 5.3 Create Pull Request

```bash
# Detect language
LANG="${3:-en}"

# Generate PR description
case "$LANG" in
    it)
        DESCRIPTION="## Descrizione\n\n[Descrivi le modifiche]\n\n## Modifiche\n\n- [Modifica 1]\n\n## Test\n\n- Test unitari aggiornati\n- Test di integrazione verificati"
        ;;
    es)
        DESCRIPTION="## Descripción\n\n[Describe los cambios]\n\n## Cambios\n\n- [Cambio 1]\n\n## Pruebas\n\n- Tests unitarios actualizados\n- Tests de integración verificados"
        ;;
    fr)
        DESCRIPTION="## Description\n\n[Décrivez les modifications]\n\n## Modifications\n\n- [Modification 1]\n\n## Tests\n\n- Tests unitaires mis à jour\n- Tests d'intégration vérifiés"
        ;;
    de)
        DESCRIPTION="## Beschreibung\n\n[Beschreiben Sie die Änderungen]\n\n## Änderungen\n\n- [Änderung 1]\n\n## Tests\n\n- Unit-Tests aktualisiert\n- Integrationstests überprüft"
        ;;
    *)
        DESCRIPTION="## Description\n\n[Describe the changes]\n\n## Changes\n\n- [Change 1]\n\n## Testing\n\n- Unit tests updated\n- Integration tests verified"
        ;;
esac

# Create PR
gh pr create \
    --base "$TARGET_BRANCH" \
    --head "$BRANCH_NAME" \
    --title "${1:-Automated PR from $BRANCH_NAME}" \
    --body "$(echo -e "$DESCRIPTION")" \
    --web

echo "Pull request created successfully"
```

## Phase 6: Post-Creation

### 6.1 PR Information

```bash
# Get PR number and URL
PR_NUMBER=$(gh pr view --json number -q .number)
PR_URL=$(gh pr view --json url -q .url)

echo ""
echo "Pull Request Details:"
echo "Number: #$PR_NUMBER"
echo "URL: $PR_URL"
echo "Branch: $BRANCH_NAME -> $TARGET_BRANCH"
echo ""
```

### 6.2 Optional Actions

Available post-creation actions:

```bash
# Add labels
gh pr edit $PR_NUMBER --add-label "enhancement"
gh pr edit $PR_NUMBER --add-label "ready-for-review"

# Add reviewers
gh pr edit $PR_NUMBER --add-reviewer "username1,username2"

# Add assignees
gh pr edit $PR_NUMBER --add-assignee "@me"

# Request reviews
gh pr review $PR_NUMBER --comment -b "Please review when ready"

# Enable auto-merge (if repository allows)
gh pr merge $PR_NUMBER --auto --squash
```

## Best Practices

### Commit Message Guidelines

**Good commit messages**:
```
feat(api): add user authentication endpoint
fix(validation): correct email format validation
docs(readme): update installation instructions
test(user-service): add integration tests for user creation
refactor(utils): simplify date formatting utility
```

**Bad commit messages**:
```
update files
fix bug
changes
wip
asdf
```

### PR Title Guidelines

**Good PR titles**:
- "Add JWT authentication to user service"
- "Fix memory leak in background job processor"
- "Refactor user repository to use Spring Data JPA"
- "Update Spring Boot to version 3.2.0"

**Bad PR titles**:
- "Update"
- "Changes"
- "Fix"
- "WIP"

### PR Description Best Practices

1. **Clear summary**: Explain what and why
2. **Bullet points**: List specific changes
3. **Testing details**: How was it tested
4. **Screenshots**: For UI changes
5. **Breaking changes**: Clearly marked
6. **Related issues**: Link to issues
7. **Dependencies**: Mention related PRs
8. **Deployment notes**: Special deployment steps

## Error Handling

### Common Issues

**Authentication Error**:
```bash
# Authenticate with GitHub CLI
gh auth login
```

**Branch Already Exists**:
```bash
# Switch to existing branch
git checkout existing-branch
# Or delete and recreate
git branch -D existing-branch
git checkout -b existing-branch
```

**Merge Conflicts**:
```bash
# Update from target branch
git fetch origin
git merge origin/$TARGET_BRANCH
# Resolve conflicts manually
git add .
git commit -m "Resolve merge conflicts"
```

**No Changes to Commit**:
```bash
# Check status
git status
# Verify files are modified
git diff
```

## Examples

### Example 1: Simple Feature PR

```bash
# Create PR with title and default settings
./devkit.github.create-pr "Add user profile API"
```

### Example 2: Bug Fix PR with Custom Target

```bash
# Create PR targeting specific branch
./devkit.github.create-pr "Fix authentication timeout" develop
```

### Example 3: PR with Italian Description

```bash
# Create PR with Italian description
./devkit.github.create-pr "Aggiungere validazione email" main it
```

### Example 4: Auto-Generated PR

```bash
# Let the command generate title from changes
./devkit.github.create-pr
```

## Integration with CI/CD

The PR will automatically trigger:

- **CI Pipeline**: Build and test execution
- **Code Quality**: SonarQube analysis
- **Security Scan**: Dependency vulnerability check
- **Linting**: Code style validation
- **Coverage**: Test coverage report

## Your Task

Based on the provided arguments:

1. Analyze current changes in the working directory
2. Create an appropriate branch name
3. Categorize and commit changes logically
4. Generate clear commit messages following Conventional Commits
5. Push branch to remote repository
6. Create pull request with description in the specified language
7. Provide PR details and next steps

**Remember**: Keep PR descriptions concise and professional without emojis. Focus on technical content and clarity.

## Execution Instructions

**Agent Selection**: To execute this GitHub task, use the following approach:
- Primary: Use `general-purpose` agent with GitHub CLI expertise and code analysis capabilities
