#!/bin/bash
# De-Microsoft the codebase
# Replaces "MBASIC" and "MBASIC" references with appropriate alternatives

set -e

# Exclude directories
EXCLUDES="--exclude-dir=.git --exclude-dir=venv --exclude-dir=venv-build --exclude-dir=__pycache__"

echo "De-Microsofting codebase..."
echo "Excluding: venv, git"
echo

# Pattern 1: "MBASIC" -> "MBASIC"
echo "Pattern 1: 'MBASIC' -> 'MBASIC'"
grep -r $EXCLUDES -l "MBASIC" . 2>/dev/null | while read file; do
    echo "  Updating: $file"
    sed -i 's/MBASIC/MBASIC/g' "$file"
done

# Pattern 2: "MBASIC" -> "MBASIC" (in most contexts)
echo "Pattern 2: 'MBASIC' -> 'MBASIC'"
grep -r $EXCLUDES -l "MBASIC" . 2>/dev/null | while read file; do
    # Skip if file is about history or external references
    if [[ "$file" == *"HISTORY"* ]] || [[ "$file" == *"external"* ]]; then
        echo "  Skipping (history): $file"
        continue
    fi
    echo "  Updating: $file"
    sed -i 's/MBASIC/MBASIC/g' "$file"
done

# Pattern 3: "MBASIC" -> "MBASIC"
echo "Pattern 3: \"MBASIC\" -> 'MBASIC'"
grep -r $EXCLUDES -l "MBASIC" . 2>/dev/null | while read file; do
    echo "  Updating: $file"
    sed -i "s/MBASIC/MBASIC/g" "$file"
done

# Pattern 4: "the Microsoft" -> "the original" (in implementation contexts)
echo "Pattern 4: 'the original MBASIC interpreter' -> 'the original MBASIC interpreter'"
grep -r $EXCLUDES -l "the original MBASIC interpreter" . 2>/dev/null | while read file; do
    echo "  Updating: $file"
    sed -i 's/the original MBASIC interpreter/the original MBASIC interpreter/g' "$file"
done

echo
echo "Done! Summary:"
echo "- External docs preserved"
echo "- MBASIC_HISTORY.md preserves historical Microsoft references"
echo "- All other references updated to clarify independent implementation"
echo
echo "Remaining 'Microsoft' references (should be historical only):"
grep -r $EXCLUDES -i "microsoft" . 2>/dev/null | wc -l
