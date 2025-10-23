#!/bin/bash

# Script to update plugin version in marketplace.json and add entry to README.md
# Usage: ./update-version.sh [VERSION]
# If VERSION not provided, bumps minor version automatically

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKETPLACE_FILE="${REPO_ROOT}/.claude-plugin/marketplace.json"
README_FILE="${REPO_ROOT}/README.md"

# Get current version from marketplace.json
CURRENT_VERSION=$(jq -r '.metadata.version' "$MARKETPLACE_FILE")

# Determine new version
if [ -z "$1" ]; then
  # Auto-bump minor version: 1.1.0 → 1.2.0
  MAJOR=$(echo "$CURRENT_VERSION" | cut -d. -f1)
  MINOR=$(echo "$CURRENT_VERSION" | cut -d. -f2)
  PATCH=$(echo "$CURRENT_VERSION" | cut -d. -f3)
  NEW_VERSION="${MAJOR}.$((MINOR + 1)).0"
else
  NEW_VERSION="$1"
fi

echo "📦 Updating plugin version: $CURRENT_VERSION → $NEW_VERSION"

# Update marketplace.json version
# Using a temp file to preserve formatting
jq ".metadata.version = \"$NEW_VERSION\"" "$MARKETPLACE_FILE" > "${MARKETPLACE_FILE}.tmp" && mv "${MARKETPLACE_FILE}.tmp" "$MARKETPLACE_FILE"
echo "✅ Updated marketplace.json version to $NEW_VERSION"

# Add version entry to README.md at the end (before last line if it's blank)
TIMESTAMP=$(date -u +'%Y-%m-%d')
VERSION_ENTRY="- Version: $NEW_VERSION — $(date +'Added new optimization command: speckit.optimize for task workflow parallelization and subagent delegation strategy')"

# Remove last line if empty, add new version line, then re-add separator
if [ "$(tail -c 1 "$README_FILE" | wc -l)" -eq 0 ]; then
  echo "" >> "$README_FILE"
fi

# Add the new version entry
echo "$VERSION_ENTRY" >> "$README_FILE"
echo "✅ Added version entry to README.md"

echo ""
echo "✨ Version update complete!"
echo "   marketplace.json: version = $NEW_VERSION"
echo "   README.md: Added changelog entry"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff"
echo "   2. Commit: git commit -m 'chore: bump version to $NEW_VERSION'"
echo "   3. Push: git push origin main"
