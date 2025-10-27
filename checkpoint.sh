#!/bin/bash
# Checkpoint script: Increment version, commit, and push
# Usage: ./checkpoint.sh "commit message"

if [ -z "$1" ]; then
    echo "Error: Commit message required"
    echo "Usage: ./checkpoint.sh \"commit message\""
    exit 1
fi

COMMIT_MSG="$1"
VERSION_FILE="src/version.py"

# Read current version
CURRENT_VERSION=$(grep 'VERSION = ' $VERSION_FILE | cut -d'"' -f2)
echo "Current version: $CURRENT_VERSION"

# Increment patch version (X.Y.Z -> X.Y.Z+1)
IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
NEW_PATCH=$((patch + 1))
NEW_VERSION="$major.$minor.$NEW_PATCH"

echo "New version: $NEW_VERSION"

# Update version file
sed -i "s/VERSION = \"$CURRENT_VERSION\"/VERSION = \"$NEW_VERSION\"/" $VERSION_FILE

# Git add, commit, push
git add -A
git commit -m "$COMMIT_MSG

Version: $NEW_VERSION

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push

echo "✓ Checkpoint complete: Version $NEW_VERSION committed and pushed"
