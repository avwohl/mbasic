#!/bin/bash
# Checkpoint script: Increment version, commit, and push
# Usage: ./checkpoint.sh "commit message"

if [ -z "$1" ]; then
    echo "Error: Commit message required"
    echo "Usage: ./checkpoint.sh \"commit message\""
    exit 1
fi

# Activate venv if it exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

COMMIT_MSG="$1"
VERSION_FILE="src/version.py"

# Read current version (first match only, to avoid MBASIC_VERSION)
CURRENT_VERSION=$(grep '^VERSION = ' $VERSION_FILE | head -1 | cut -d"'" -f2)
echo "Current version: $CURRENT_VERSION"

# Increment patch version (X.Y.Z -> X.Y.Z+1)
# NOTE: This happens IMMEDIATELY so version increments even on failed validation
# This way version count > commit count, showing how many attempts were made
IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
NEW_PATCH=$((patch + 1))
NEW_VERSION="$major.$minor.$NEW_PATCH"

echo "New version: $NEW_VERSION"

# Update version file immediately
sed -i "s/VERSION = '$CURRENT_VERSION'/VERSION = '$NEW_VERSION'/" $VERSION_FILE

# Check if dev docs were modified - regenerate index
DEV_CHANGED=$(git diff --name-only docs/dev/ 2>/dev/null | grep -v "docs/dev/index.md" || echo "")

if [ -n "$DEV_CHANGED" ]; then
    echo "Dev documentation changed - regenerating index..."
    python3 utils/generate_dev_index.py
    if [ $? -eq 0 ]; then
        echo "✓ Dev index regenerated"
    else
        echo "❌ ERROR: Dev index generation failed"
        exit 1
    fi
fi

# Check if help documentation was modified
HELP_CHANGED=$(git diff --name-only docs/help/ 2>/dev/null || echo "")

if [ -n "$HELP_CHANGED" ]; then
    echo "Help documentation changed - rebuilding indexes..."
    PYTHONPATH=$(pwd) python3 utils/build_help_indexes.py
    if [ $? -eq 0 ]; then
        echo "✓ Help indexes rebuilt successfully"
    else
        echo "❌ ERROR: Help index build failed"
        echo "Fix the help index errors before committing"
        exit 1
    fi
fi

# Check if docs were modified - validate mkdocs build
# Use git diff-index to detect any changes to docs tree or config files
# This catches all changes (staged, unstaged, and untracked files)

# Check if docs/ has any changes (uses git's SHA256 internally)
if ! git diff-index --quiet HEAD docs/ 2>/dev/null || \
   [ -n "$(git ls-files --others --exclude-standard docs/ 2>/dev/null)" ] || \
   ! git diff --quiet mkdocs.yml .github/workflows/docs.yml 2>/dev/null || \
   ! git diff --quiet --cached mkdocs.yml .github/workflows/docs.yml 2>/dev/null; then
  DOCS_CHANGED=true
else
  DOCS_CHANGED=false
fi

if [ "$DOCS_CHANGED" = true ]; then
    echo "Documentation changed - regenerating keyboard shortcuts..."
    python3 mbasic --dump-keymap > docs/user/keyboard-shortcuts.md
    if [ $? -eq 0 ]; then
        echo "✓ Keyboard shortcuts regenerated"
    else
        echo "❌ ERROR: Keyboard shortcut generation failed"
        exit 1
    fi

    echo "Documentation changed - validating mkdocs builds..."
    if command -v mkdocs &> /dev/null; then
        # Build user docs (limited search indexing)
        echo "Building user documentation (site/)..."
        BUILD_OUTPUT=$(mkdocs build --strict 2>&1)
        BUILD_EXIT_CODE=$?

        # Check if mkdocs failed
        if [ $BUILD_EXIT_CODE -ne 0 ]; then
            echo "❌ ERROR: mkdocs build failed in strict mode!"
            echo ""
            echo "$BUILD_OUTPUT"
            echo ""
            echo "Fix the errors above before committing"
            exit 1
        fi

        # Also check for strict mode warnings (unrecognized links, missing anchors)
        # These are the issues that fail on GitHub but may not fail locally
        if echo "$BUILD_OUTPUT" | grep -E "contains an unrecognized relative link|does not contain an anchor|contains an absolute link" > /dev/null; then
            echo "❌ ERROR: mkdocs build has strict mode warnings!"
            echo ""
            echo "The following warnings will cause GitHub deployment to fail:"
            echo ""
            echo "$BUILD_OUTPUT" | grep -E "contains an unrecognized relative link|does not contain an anchor|contains an absolute link"
            echo ""
            echo "Run 'mkdocs build --strict' to see full details"
            exit 1
        fi

        echo "✓ User docs build validation passed (no warnings or errors)"

        # Build developer docs (full search indexing)
        # Note: Dev build runs without --strict since it includes history files with broken links
        echo "Building developer documentation (site-dev/)..."
        BUILD_OUTPUT_DEV=$(mkdocs build -f mkdocs-dev.yml 2>&1)
        BUILD_EXIT_CODE_DEV=$?

        if [ $BUILD_EXIT_CODE_DEV -ne 0 ]; then
            echo "❌ ERROR: mkdocs-dev build failed!"
            echo ""
            echo "$BUILD_OUTPUT_DEV"
            echo ""
            echo "Fix the errors above before committing"
            exit 1
        fi

        echo "✓ Developer docs build validation passed"
    else
        echo "❌ ERROR: mkdocs not installed!"
        echo ""
        echo "Install mkdocs to validate documentation builds:"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
fi

# Git add, commit, push
git add -A
git commit -m "$COMMIT_MSG

Version: $NEW_VERSION

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push

echo "✓ Checkpoint complete: Version $NEW_VERSION committed and pushed"
