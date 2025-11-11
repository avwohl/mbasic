# Broken Links Analysis

Date: 2025-10-26

## Summary

Found **25 broken links** across help documentation pointing to **15 missing files**.

## Root Cause

Most broken links are due to **incorrect path prefixes**:
- Links point to `language/statements/index.md`  
- Should point to `common/language/statements/index.md`

## Missing Files Created

✅ **Created:**
- `common/language/statements/index.md` - Complete statements reference index

## Remaining Missing Files

### High Priority (frequently referenced)

1. **common/language/data-types.md** - Referenced from operators.md, getting-started.md
   - Should document: INTEGER (%), SINGLE (!), DOUBLE (#), STRING ($)
   - Should explain type suffixes and conversions

2. **getting-started.md** (at root) - Referenced from multiple curses UI docs
   - Should be at `docs/help/getting-started.md`  
   - Or fix links to point to `common/getting-started.md` (which exists)

3. **language/functions/index.md** - Referenced from curses help docs
   - File exists at `common/language/functions/index.md`
   - Fix: Update links to use correct path

4. **common/language/statements/if-then.md** - Referenced from getting-started
   - File exists as `if-then-else-if-goto.md`
   - Fix: Update link

### Medium Priority

5. **common/language/functions/randomize.md** - Referenced from peek.md
   - Should document RANDOMIZE statement

6. **common/examples/hello-world.md** - Referenced from getting-started
7. **common/examples/loops.md** - Referenced from getting-started  

8. **common/language/character-set.md** - Referenced from ascii-codes.md

### Low Priority (UI docs)

9. **common/ui/cli/index.md** - CLI interface docs
10. **common/ui/curses/editing.md** - Curses editor guide
11. **common/ui/tk/index.md** - Tk interface docs

### Not Real Files

12. **mbasic/not-implemented.md** - Document unsupported features
13. **ui/curses/link** - Typo in help-navigation.md (should be removed)

## Recommended Fixes

### Quick Wins (Fix Links)

```bash
# Fix: getting-started.md links
find docs/help -name "*.md" -exec sed -i 's|../../getting-started.md|../../common/getting-started.md|g' {} \;

# Fix: statements/index.md links  
find docs/help -name "*.md" -exec sed -i 's|language/statements/index.md|common/language/statements/index.md|g' {} \;
find docs/help -name "*.md" -exec sed -i 's|\.\./language/statements/index.md|../common/language/statements/index.md|g' {} \;

# Fix: functions/index.md links
find docs/help -name "*.md" -exec sed -i 's|language/functions/index.md|common/language/functions/index.md|g' {} \;

# Fix: if-then link
find docs/help -name "*.md" -exec sed -i 's|statements/if-then.md|statements/if-then-else-if-goto.md|g' {} \;
```

### Create Missing Docs

Priority order:
1. `common/language/data-types.md` - Core concept
2. `common/language/functions/randomize.md` - Simple statement doc
3. `common/examples/hello-world.md` + `loops.md` - Beginner examples  
4. `common/language/character-set.md` - Reference material

## Link Checker Script

Created `/tmp/check_broken_links.py` for ongoing validation.

Usage:
```bash
cd /home/wohl/cl/mbasic
python3 /tmp/check_broken_links.py
```

## Next Steps

1. Run quick fix sed commands to correct path issues
2. Create high-priority missing docs
3. Re-run link checker to verify
4. Remove/fix typo links (ui/curses/link)
