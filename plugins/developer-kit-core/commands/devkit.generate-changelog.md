---
allowed-tools: Bash, Read, Write, Edit, Grep
argument-hint: "[action] [version] [format]"
description: Generates and manages project changelog following Keep a Changelog standard with Git integration and Conventional Commits support. Use when releasing a new version or updating the changelog after commits.
---

# Project Changelog Generator and Maintainer

## Overview

Generate and maintain project changelog following Keep a Changelog standard, extracting changes from Git history with
support for Conventional Commits, version detection from multiple build systems (Maven, Gradle, npm, pip, Cargo), and
automated changelog updates.

## Usage

```
/devkit.generate-changelog $ARGUMENTS
```

## Arguments

$1 specifies the action (optional - defaults to `update`):

- `init` - Create initial CHANGELOG.md following Keep a Changelog format
- `update` - Update changelog with changes since last tag/version
- `release` - Generate changelog entry for new release version
- `preview` - Preview changes without writing to file
- `validate` - Validate existing CHANGELOG.md format

$2 specifies the version (optional - auto-detected from build file):

- Version number (e.g., `1.2.3`, `2.0.0`)
- `auto` - Auto-detect from build files: pom.xml, build.gradle, package.json, setup.py, Cargo.toml (default)
- `latest-tag` - Use latest Git tag
- `snapshot` - Mark as unreleased/snapshot

$3 specifies the format (optional - defaults to `keepachangelog`):

- `keepachangelog` - Keep a Changelog format (default)
- `conventional` - Conventional Changelog format
- `github` - GitHub Release Notes format
- `json` - Structured JSON format

## Execution Instructions

**Agent Selection**: To execute this generation task, use the following approach:

- Primary: Use `general-purpose` agent with specialized knowledge of the task domain
- Or use appropriate specialized agent if available for the specific generation task
## Context

- **Project Root**: !`pwd`
- **Current Branch**: !`git branch --show-current 2>/dev/null || echo "Not a git repository"`
- **Latest Tag**: !`git describe --tags --abbrev=0 2>/dev/null || echo "No tags found"`
- **Build System**: !
  `if [ -f pom.xml ]; then echo "Maven"; elif [ -f build.gradle ]; then echo "Gradle"; elif [ -f package.json ]; then echo "npm"; elif [ -f setup.py ]; then echo "Python"; elif [ -f Cargo.toml ]; then echo "Rust"; else echo "Generic"; fi`
- **Existing Changelog**: !`if [ -f CHANGELOG.md ]; then echo "Found"; else echo "Not found"; fi`

## Changelog Standards

### Keep a Changelog Format

Follow https://keepachangelog.com/en/1.0.0/ specification:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New features for the next release

### Changed

- Changes in existing functionality

### Deprecated

- Soon-to-be removed features

### Removed

- Removed features

### Fixed

- Bug fixes

### Security

- Security improvements

## [1.2.0] - 2024-01-15

### Added

- User authentication with JWT tokens
- Health check endpoints
- Redis caching for sessions
- Comprehensive integration tests

### Changed

- Upgraded dependencies to latest stable versions
- Improved error handling
- Enhanced logging configuration

### Fixed

- Memory leak in background task executor
- Security vulnerability in authentication
- Timezone handling in date conversions

### Security

- Updated dependencies with known vulnerabilities
- Implemented CSRF protection
- Added rate limiting for sensitive endpoints

## [1.1.0] - 2023-12-10

### Added

- Email notification service
- Pagination for list endpoints
- Docker Compose setup for local development

### Fixed

- Null pointer exception in core service
- Transaction rollback issues

## [1.0.0] - 2023-11-01

### Added

- Initial release
- Basic CRUD operations
- REST API implementation
- Database integration
- Authentication system

[Unreleased]: https://github.com/username/project/compare/v1.2.0...HEAD

[1.2.0]: https://github.com/username/project/compare/v1.1.0...v1.2.0

[1.1.0]: https://github.com/username/project/compare/v1.0.0...v1.1.0

[1.0.0]: https://github.com/username/project/releases/tag/v1.0.0
```

## Changelog Generation Process

### 1. Initialize Changelog

Create initial CHANGELOG.md structure:

```bash
#!/bin/bash
# Initialize changelog

cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Features in development

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

EOF

echo "✅ CHANGELOG.md created successfully"
```

### 2. Extract Changes from Git

Analyze Git commits since last tag:

**Detect Version from Build File**

```bash
#!/bin/bash
# detect-version.sh - Auto-detect project version

detect_maven_version() {
    if [ -f "pom.xml" ]; then
        mvn help:evaluate -Dexpression=project.version -q -DforceStdout 2>/dev/null || \
        grep -oP '<version>\K[^<]+' pom.xml | head -1
    fi
}

detect_gradle_version() {
    if [ -f "build.gradle" ]; then
        grep "version" build.gradle | grep -oP "'\K[^']+" | head -1 || \
        grep "version" build.gradle | grep -oP '"\K[^"]+' | head -1
    elif [ -f "build.gradle.kts" ]; then
        grep "version" build.gradle.kts | grep -oP '"\K[^"]+' | head -1
    fi
}

detect_npm_version() {
    if [ -f "package.json" ]; then
        grep -oP '"version":\s*"\K[^"]+' package.json | head -1
    fi
}

detect_python_version() {
    if [ -f "setup.py" ]; then
        grep -oP 'version\s*=\s*["\047]\K[^"\047]+' setup.py | head -1
    elif [ -f "pyproject.toml" ]; then
        grep -oP 'version\s*=\s*"\K[^"]+' pyproject.toml | head -1
    fi
}

detect_rust_version() {
    if [ -f "Cargo.toml" ]; then
        grep -oP 'version\s*=\s*"\K[^"]+' Cargo.toml | head -1
    fi
}

# Detect version based on build system
if [ -f "pom.xml" ]; then
    VERSION=$(detect_maven_version)
    echo "Maven version: $VERSION"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    VERSION=$(detect_gradle_version)
    echo "Gradle version: $VERSION"
elif [ -f "package.json" ]; then
    VERSION=$(detect_npm_version)
    echo "npm version: $VERSION"
elif [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    VERSION=$(detect_python_version)
    echo "Python version: $VERSION"
elif [ -f "Cargo.toml" ]; then
    VERSION=$(detect_rust_version)
    echo "Rust version: $VERSION"
else
    VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')
    echo "Git tag version: $VERSION"
fi

echo "$VERSION"
```

**Extract Git Commits**

```bash
#!/bin/bash
# extract-changes.sh - Extract changes from Git history

# Get last tag or first commit
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
if [ -z "$LAST_TAG" ]; then
    LAST_TAG=$(git rev-list --max-parents=0 HEAD)
fi

echo "📊 Extracting changes since $LAST_TAG..."

# Get commit range
git log $LAST_TAG..HEAD --pretty=format:"%h|%s|%b|%an|%ad" --date=short > commits.tmp

# Categorize commits by type
declare -A categories
categories[Added]=""
categories[Changed]=""
categories[Deprecated]=""
categories[Removed]=""
categories[Fixed]=""
categories[Security]=""

while IFS='|' read -r hash subject body author date; do
    # Parse conventional commit format
    if [[ $subject =~ ^(feat|feature|add)(\([^)]+\))?:(.+) ]]; then
        categories[Added]+="- ${BASH_REMATCH[3]} (${hash})\n"
    elif [[ $subject =~ ^(fix|bugfix)(\([^)]+\))?:(.+) ]]; then
        categories[Fixed]+="- ${BASH_REMATCH[3]} (${hash})\n"
    elif [[ $subject =~ ^(chore|refactor|perf|style)(\([^)]+\))?:(.+) ]]; then
        categories[Changed]+="- ${BASH_REMATCH[3]} (${hash})\n"
    elif [[ $subject =~ ^(security|sec)(\([^)]+\))?:(.+) ]]; then
        categories[Security]+="- ${BASH_REMATCH[3]} (${hash})\n"
    elif [[ $subject =~ ^(remove|delete)(\([^)]+\))?:(.+) ]]; then
        categories[Removed]+="- ${BASH_REMATCH[3]} (${hash})\n"
    elif [[ $subject =~ ^(deprecate|deprecated)(\([^)]+\))?:(.+) ]]; then
        categories[Deprecated]+="- ${BASH_REMATCH[3]} (${hash})\n"
    else
        # Non-conventional commit, try to categorize by keywords
        if [[ $subject =~ [Aa]dd|[Nn]ew|[Ff]eature ]]; then
            categories[Added]+="- $subject (${hash})\n"
        elif [[ $subject =~ [Ff]ix|[Bb]ug ]]; then
            categories[Fixed]+="- $subject (${hash})\n"
        elif [[ $subject =~ [Ss]ecurity|[Vv]ulnerability|CVE ]]; then
            categories[Security]+="- $subject (${hash})\n"
        elif [[ $subject =~ [Rr]emove|[Dd]elete ]]; then
            categories[Removed]+="- $subject (${hash})\n"
        elif [[ $subject =~ [Dd]eprecate ]]; then
            categories[Deprecated]+="- $subject (${hash})\n"
        else
            categories[Changed]+="- $subject (${hash})\n"
        fi
    fi
done < commits.tmp

rm commits.tmp

# Print categorized changes
for category in Added Changed Deprecated Removed Fixed Security; do
    if [ -n "${categories[$category]}" ]; then
        echo ""
        echo "### $category"
        echo -e "${categories[$category]}"
    fi
done
```

### 3. Conventional Commits Support

Support for Conventional Commits specification:

**Commit Types**

```
feat: New feature (Added section)
fix: Bug fix (Fixed section)
docs: Documentation changes (Changed section)
style: Code style changes (Changed section)
refactor: Code refactoring (Changed section)
perf: Performance improvements (Changed section)
test: Test additions/changes (Changed section)
chore: Build/tooling changes (Changed section)
security: Security fixes (Security section)
remove: Removed features (Removed section)
deprecate: Deprecated features (Deprecated section)
```

**Breaking Changes**

```bash
# Detect breaking changes in commit messages
git log $LAST_TAG..HEAD --grep="BREAKING CHANGE" --pretty=format:"%s" > breaking.tmp

if [ -s breaking.tmp ]; then
    echo ""
    echo "### ⚠️ BREAKING CHANGES"
    while read -r line; do
        echo "- $line"
    done < breaking.tmp
fi

rm breaking.tmp
```

### 4. Version Detection for Multiple Build Systems

Support for various project types:

**JavaScript/TypeScript (package.json)**

```json
{
  "name": "my-project",
  "version": "1.2.0",
  "description": "Project description"
}
```

**Python (setup.py or pyproject.toml)**

```python
# setup.py
setup(
    name="my-project",
    version="1.2.0",
    description="Project description"
)
```

```toml
# pyproject.toml
[project]
version = "1.2.0"
```

**Rust (Cargo.toml)**

```toml
[package]
name = "my-project"
version = "1.2.0"
```

**PHP (composer.json)**

```json
{
  "name": "vendor/package",
  "version": "1.2.0"
}
```

### 5. Update Changelog File

Insert new version entry into CHANGELOG.md:

```bash
#!/bin/bash
# update-changelog.sh - Update CHANGELOG.md with new version

VERSION=${1:-"Unreleased"}
DATE=$(date +%Y-%m-%d)
CHANGES_FILE=${2:-"changes.tmp"}

# Read existing CHANGELOG.md
if [ ! -f "CHANGELOG.md" ]; then
    echo "❌ CHANGELOG.md not found. Run with 'init' first."
    exit 1
fi

# Create new version section
NEW_SECTION="## [$VERSION] - $DATE

$(cat $CHANGES_FILE)

"

# Find insertion point (after ## [Unreleased])
# Insert new section after Unreleased section
sed -i.bak "/## \[Unreleased\]/r /dev/stdin" CHANGELOG.md << EOF
$NEW_SECTION
EOF

# Update comparison links at the end
# Add new version link
REPO_URL=$(git config --get remote.origin.url | sed 's/\.git$//' | sed 's/git@github.com:/https:\/\/github.com\//')
PREV_VERSION=$(grep -oP '\[\K[0-9]+\.[0-9]+\.[0-9]+(?=\])' CHANGELOG.md | head -2 | tail -1)

if [ -n "$PREV_VERSION" ]; then
    # Add comparison link
    echo "" >> CHANGELOG.md
    echo "[$VERSION]: $REPO_URL/compare/v$PREV_VERSION...v$VERSION" >> CHANGELOG.md
fi

rm CHANGELOG.md.bak

echo "✅ CHANGELOG.md updated with version $VERSION"
```

### 6. Build System Integration

**Maven Changes Plugin (Java)**

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-changes-plugin</artifactId>
    <version>2.12.1</version>
    <configuration>
        <includeOpenIssues>false</includeOpenIssues>
        <onlyMilestoneIssues>true</onlyMilestoneIssues>
    </configuration>
    <executions>
        <execution>
            <id>generate-changelog</id>
            <phase>generate-resources</phase>
            <goals>
                <goal>changes-report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

**Gradle Release Plugin (Java)**

```groovy
// build.gradle
plugins {
    id 'net.researchgate.release' version '3.0.2'
}

release {
    preTagCommitMessage = 'chore: prepare release'
    tagCommitMessage = 'chore: create tag'
    newVersionCommitMessage = 'chore: new version'
    buildTasks = ['build']

    git {
        requireBranch = 'main'
        signTag = false
    }
}

// Task to update changelog before release
task updateChangelog(type: Exec) {
    commandLine './scripts/update-changelog.sh', version
}

beforeReleaseBuild.dependsOn updateChangelog
```

**npm version (JavaScript/TypeScript)**

```json
// package.json - scripts section
{
  "scripts": {
    "version": "node scripts/update-changelog.js && git add CHANGELOG.md",
    "postversion": "git push && git push --tags"
  }
}
```

**Python setuptools**

```python
# setup.py or release script
import subprocess

def update_changelog(version):
    subprocess.run(['./scripts/update-changelog.sh', version])

# Integrate with version bumping
```

### 7. GitHub Integration

**GitHub Releases from Changelog**

```bash
#!/bin/bash
# github-release.sh - Create GitHub release from changelog

VERSION=$1
CHANGELOG_FILE="CHANGELOG.md"

if [ -z "$VERSION" ]; then
    echo "❌ Version required"
    exit 1
fi

# Extract changelog section for this version
awk "/## \[$VERSION\]/,/## \[/" $CHANGELOG_FILE | sed '1d;$d' > release-notes.tmp

# Create GitHub release
gh release create "v$VERSION" \
    --title "Release $VERSION" \
    --notes-file release-notes.tmp \
    --verify-tag

rm release-notes.tmp

echo "✅ GitHub release v$VERSION created"
```

**Automated Release Workflow**

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Extract changelog
        id: changelog
        run: |
          VERSION=${{ steps.version.outputs.VERSION }}
          awk "/## \[$VERSION\]/,/## \[/" CHANGELOG.md | sed '1d;$d' > release-notes.md
          echo "NOTES<<EOF" >> $GITHUB_OUTPUT
          cat release-notes.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Build with Maven
        run: mvn clean package -DskipTests

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ steps.version.outputs.VERSION }}
          release_name: Release ${{ steps.version.outputs.VERSION }}
          body: ${{ steps.changelog.outputs.NOTES }}
          draft: false
          prerelease: false

      - name: Upload artifacts
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./target/*.jar
          asset_name: application.jar
          asset_content_type: application/java-archive
```

### 8. Validation and Quality Checks

**Validate Changelog Format**

```bash
#!/bin/bash
# validate-changelog.sh - Validate CHANGELOG.md format

CHANGELOG="CHANGELOG.md"

if [ ! -f "$CHANGELOG" ]; then
    echo "❌ CHANGELOG.md not found"
    exit 1
fi

echo "🔍 Validating CHANGELOG.md..."

# Check required sections
if ! grep -q "# Changelog" "$CHANGELOG"; then
    echo "❌ Missing main title '# Changelog'"
    exit 1
fi

if ! grep -q "## \[Unreleased\]" "$CHANGELOG"; then
    echo "⚠️  Warning: Missing [Unreleased] section"
fi

# Check for proper version format
if ! grep -qP "## \[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2}" "$CHANGELOG"; then
    echo "⚠️  Warning: No properly formatted version entries found"
fi

# Check for subsections
SUBSECTIONS=("Added" "Changed" "Deprecated" "Removed" "Fixed" "Security")
for section in "${SUBSECTIONS[@]}"; do
    if ! grep -q "### $section" "$CHANGELOG"; then
        echo "ℹ️  Info: No '### $section' section found"
    fi
done

# Check for comparison links
if ! grep -qP "\[Unreleased\]: .+/compare/.+\.\.\.HEAD" "$CHANGELOG"; then
    echo "⚠️  Warning: Missing or invalid comparison links"
fi

echo "✅ Changelog validation complete"
```

### 9. Release Automation Script

**Complete Release Script**

```bash
#!/bin/bash
# release.sh - Automated release with changelog update

set -e

VERSION=$1
DRY_RUN=${2:-false}

if [ -z "$VERSION" ]; then
    echo "Usage: ./release.sh <version> [dry-run]"
    echo "Example: ./release.sh 1.2.0"
    exit 1
fi

echo "🚀 Starting release process for version $VERSION"

# 1. Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format. Use semantic versioning (e.g., 1.2.0)"
    exit 1
fi

# 2. Check working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory is not clean. Commit or stash changes first."
    exit 1
fi

# 3. Update version in build files
if [ -f "pom.xml" ]; then
    echo "📝 Updating version in pom.xml..."
    mvn versions:set -DnewVersion=$VERSION -DgenerateBackupPoms=false
elif [ -f "build.gradle" ]; then
    echo "📝 Updating version in build.gradle..."
    sed -i.bak "s/version = .*/version = '$VERSION'/" build.gradle
    rm build.gradle.bak
elif [ -f "package.json" ]; then
    echo "📝 Updating version in package.json..."
    npm version $VERSION --no-git-tag-version
elif [ -f "setup.py" ]; then
    echo "📝 Updating version in setup.py..."
    sed -i.bak "s/version=['\"].*['\"]/version='$VERSION'/" setup.py
    rm setup.py.bak
elif [ -f "Cargo.toml" ]; then
    echo "📝 Updating version in Cargo.toml..."
    sed -i.bak "s/^version = .*/version = \"$VERSION\"/" Cargo.toml
    rm Cargo.toml.bak
fi

# 4. Extract changes from Git
echo "📊 Extracting changes from Git history..."
./scripts/extract-changes.sh > changes.tmp

# 5. Update CHANGELOG.md
echo "📝 Updating CHANGELOG.md..."
./scripts/update-changelog.sh "$VERSION" changes.tmp
rm changes.tmp

# 6. Build and test
echo "🔨 Building and testing..."
if [ -f "pom.xml" ]; then
    mvn clean verify
elif [ -f "build.gradle" ]; then
    ./gradlew clean build
elif [ -f "package.json" ]; then
    npm test
elif [ -f "setup.py" ]; then
    python -m pytest
elif [ -f "Cargo.toml" ]; then
    cargo test
fi

if [ "$DRY_RUN" = "true" ]; then
    echo "🔍 DRY RUN - Changes preview:"
    git diff CHANGELOG.md
    echo ""
    echo "ℹ️  This was a dry run. No changes were committed."
    exit 0
fi

# 7. Commit changes
echo "💾 Committing changes..."
git add .
git commit -m "chore: release $VERSION

- Update version in build files
- Update CHANGELOG.md with release notes
"

# 8. Create Git tag
echo "🏷️  Creating Git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION"

# 9. Push changes
echo "⬆️  Pushing changes to remote..."
git push origin main
git push origin "v$VERSION"

echo "✅ Release $VERSION completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. GitHub Actions will create the release automatically"
echo "2. Wait for CI/CD pipeline to complete"
echo "3. Verify release at: https://github.com/<username>/<repo>/releases/tag/v$VERSION"
```

## Best Practices

### Commit Message Guidelines

Follow Conventional Commits for automatic categorization:

```
feat(auth): add JWT token refresh endpoint
fix(users): resolve null pointer in user lookup
docs(api): update API documentation
style: format code with prettier/eslint
refactor(service): simplify validation logic
perf(db): optimize query performance with indexes
test(integration): add integration tests
chore(deps): upgrade dependencies to latest versions
security(auth): fix SQL injection vulnerability
```

### Release Workflow

1. **Development**: Commit changes following Conventional Commits
2. **Feature Complete**: Merge feature branches to main
3. **Pre-Release**: Run `preview` to see what will be included
4. **Release**: Run release script with new version number
5. **Verification**: Review generated changelog and GitHub release
6. **Deploy**: CI/CD pipeline deploys to production

### Integration Points

- **CI/CD**: Automated changelog validation in pipeline
- **GitHub Releases**: Auto-generate release notes from changelog
- **Package Registries**: npm, PyPI, crates.io, Maven Central
- **Docker Tags**: Use changelog versions for container tags
- **Kubernetes**: Reference changelog in deployment annotations
- **Documentation Sites**: Include changelog in generated docs

## Your Task

Based on the specified action, perform:

1. **Initialize**: Create CHANGELOG.md with proper structure
2. **Update**: Extract changes from Git and update changelog
3. **Release**: Prepare changelog entry for new release
4. **Preview**: Show changes that would be added
5. **Validate**: Check changelog format compliance

Focus on **maintaining a clear, user-friendly changelog** that follows industry standards and integrates seamlessly with
any build system (Maven, Gradle, npm, pip, Cargo, etc.) and Git workflows.

---

## Examples

```bash
# Initialize new changelog
/developer-kit:devkit.generate-changelog init

# Update changelog with recent changes (auto-detect version)
/developer-kit:devkit.generate-changelog update auto

# Preview changes without writing to file
/developer-kit:devkit.generate-changelog preview

# Create release entry for specific version
/developer-kit:devkit.generate-changelog release 1.2.0

# Validate existing changelog
/developer-kit:devkit.generate-changelog validate

# Generate changelog in GitHub format
/developer-kit:devkit.generate-changelog update 1.2.0 github

# Generate changelog in JSON format
/developer-kit:devkit.generate-changelog update 1.2.0 json

# Full release process (dry-run)
./scripts/release.sh 1.2.0 true

# Full release process (live)
./scripts/release.sh 1.2.0
```
