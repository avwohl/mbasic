#!/bin/bash
# Build and deploy local documentation to /local/site for nginx
# Replaces GitHub URLs with local URLs for mbasic.awohl.com/docs

# This script always deploys the checkout below, whoever invokes it. Without the
# check, a failed cd left the script running in the caller's directory and it went
# on to build and publish whatever checkout that happened to be.
REPO_DIR="/home/mbasic/cl/mbasic"
if ! cd "$REPO_DIR"; then
    echo "❌ ERROR: cannot enter $REPO_DIR - local docs NOT deployed" >&2
    echo "   This script publishes that checkout specifically; run it as the user that owns it." >&2
    exit 1
fi

LOCAL_URL="https://mbasic.awohl.com/docs"
GITHUB_URL="https://avwohl.github.io/mbasic"

# Build with local URL config. Output is captured rather than discarded so a
# failure can be reported: silencing it hid build errors, and because the exit
# code went unchecked the script then published the previous site/ as if fresh.
# On success nothing is printed, keeping the checkpoint log clean.
if ! BUILD_OUTPUT=$(mkdocs build --strict -f mkdocs-local.yml 2>&1); then
    echo "❌ ERROR: mkdocs build failed - local docs NOT deployed" >&2
    echo "$BUILD_OUTPUT" >&2
    exit 1
fi

# Replace GitHub URLs in content with local URLs
find site/ -type f \( -name "*.html" -o -name "*.xml" -o -name "*.txt" -o -name "*.js" -o -name "*.json" \) \
    -exec sed -i "s|${GITHUB_URL}|${LOCAL_URL}|g" {} +

# Copy Google site verification file for local site (mbasic.awohl.com)
if [ -d "verification_files/local" ]; then
    cp verification_files/local/google*.html site/ 2>/dev/null || true
fi

# Deploy by pointing the /local/site symlink at a freshly staged build directory.
LIVE_LINK="/local/site"
TIMESTAMP=$(date +%s)
NEW_DIR="/local/site-${TIMESTAMP}"

if ! cp -r site "$NEW_DIR"; then
    echo "❌ ERROR: could not stage the new build in $NEW_DIR" >&2
    rm -rf "$NEW_DIR"
    exit 1
fi

# Swap with 'ln' to a staging path followed by 'mv -T', NOT 'ln -sfn <dir> /local/site'.
# If /local/site is a real directory, ln treats it as a destination *directory* and
# silently creates /local/site/site-<timestamp> inside it: the swap never happens,
# nginx keeps serving the old build, and the script still reports success. 'mv -T'
# always replaces the path itself, and being a rename it is atomic, so nginx never
# observes a missing /local/site.
# The staging link is named .site-new-* so the cleanup glob below cannot match it.
STAGING_LINK="/local/.site-new-$$"
ln -sfn "$NEW_DIR" "$STAGING_LINK"

# One-time migration: if a real directory still occupies the symlink's path, rename
# it aside first, because mv -T refuses to overwrite a directory. Its contents are
# mkdocs output that was just rebuilt above, so nothing unique is lost - but keep it
# until the swap succeeds so a failure can be rolled back.
OLD_DIR=""
if [ -d "$LIVE_LINK" ] && [ ! -L "$LIVE_LINK" ]; then
    echo "Converting $LIVE_LINK from a real directory into a deploy symlink..."
    OLD_DIR="/local/.site-replaced-$$"
    if ! mv "$LIVE_LINK" "$OLD_DIR"; then
        echo "❌ ERROR: could not move the existing $LIVE_LINK directory aside" >&2
        rm -f "$STAGING_LINK"
        rm -rf "$NEW_DIR"
        exit 1
    fi
fi

if ! mv -T "$STAGING_LINK" "$LIVE_LINK"; then
    echo "❌ ERROR: could not point $LIVE_LINK at $NEW_DIR" >&2
    if [ -n "$OLD_DIR" ]; then
        mv "$OLD_DIR" "$LIVE_LINK"   # put the directory we moved aside back
    fi
    rm -f "$STAGING_LINK"
    rm -rf "$NEW_DIR"
    exit 1
fi

if [ -n "$OLD_DIR" ]; then
    rm -rf "$OLD_DIR"
fi

# Confirm the swap took effect instead of trusting it - the old code's failure mode
# was reporting success while serving stale content.
if [ "$(readlink "$LIVE_LINK")" != "$NEW_DIR" ]; then
    echo "❌ ERROR: $LIVE_LINK does not point at $NEW_DIR" >&2
    exit 1
fi

# Clean up old versions (keep only current). nullglob stops the loop from running
# once on the literal pattern when no previous build directories exist.
shopt -s nullglob
for old in /local/site-*; do
    [ "$old" != "$NEW_DIR" ] && rm -rf "$old"
done
shopt -u nullglob

echo "✓ Local docs deployed to $LIVE_LINK -> $NEW_DIR"
