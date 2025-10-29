# Lexer Cleanup Complete

**Date:** 2025-10-29
**Status:** ✅ COMPLETED

## Summary

Successfully cleaned up the MBASIC lexer to properly parse MBASIC 5.21 syntax and remove handling of old BASIC dialects.

## Changes Made

### 1. Simplified Keyword Case Handling
- **Removed problematic policies**: `first_wins`, `error`, `preserve` don't make sense for keywords
- **Created `SimpleKeywordCase`**: Only supports sensible policies:
  - `force_lower` - all lowercase (default, MBASIC style)
  - `force_upper` - all UPPERCASE (classic BASIC)
  - `force_capitalize` - Capitalize first letter (modern style)
- **Rationale**: "first wins" doesn't work for keywords since the interpreter registers them at startup

### 2. Removed Old BASIC Keyword Handling
- **Removed STATEMENT_KEYWORDS processing** that split `NEXTI` into `NEXT I`
- **Now requires proper spacing**: `NextTime` is an identifier, not `NEXT Time`
- **Rationale**: MBASIC 5.21 requires spaces. Old BASIC should use preprocessing scripts

### 3. Clarified FILE_IO_KEYWORDS Handling
- **Kept but improved** handling of `PRINT#1` → `PRINT` + `#` + `1`
- **Better comments** explain why this is needed (# is both type suffix and file syntax)
- **Cleaner implementation** using existing KEYWORDS table

### 4. Fixed BASIC Programs
- **Found issues** in `finance.bas` and `lifscore.bas`:
  - `IFP=0` → `IF P=0`
  - `IFR=0` → `IF R=0`
  - `IFL1<-29` → `IF L1<-29`
- **Fixed manually** after discovering `fix_keyword_spacing.py` has bugs with OR/AND

## Files Modified

### Source Files
- `src/lexer.py` - Main lexer cleanup
- `src/simple_keyword_case.py` - New simplified keyword case handler (created)
- `src/settings_definitions.py` - Removed problematic keyword policies
- `src/case_string_handler.py` - Unified case handling (created but not used yet)

### BASIC Files Fixed
- `basic/finance.bas` - Fixed 2 instances of IF without space
- `basic/lifscore.bas` - Fixed 1 instance of IF without space

### Documentation
- `utils/UTILITY_SCRIPTS_INDEX.md` - Created comprehensive utility script index
- `.claude/CLAUDE.md` - Added utility script reference section
- This file - Documents the cleanup

## Testing

Verified lexer correctly handles:
```basic
10 NextTime = 100  ' Identifier, not NEXT Time
20 PRINT#1, "Hi"   ' Tokenizes as PRINT + # + 1
30 IF R=0 THEN END ' Proper spacing required
```

## Known Issues

### fix_keyword_spacing.py Bug
The script incorrectly splits OR/AND inside words:
- `HISTORY` → `HIST OR Y`
- `SORRY` → `S OR RY`
- `LIFESCORE` → `LIFESC OR E`

This needs to be fixed to use word boundaries: `\bOR\b` instead of just `OR`.

## Benefits

1. **Cleaner code**: Removed complex handling for obsolete dialects
2. **Better compliance**: Strictly follows MBASIC 5.21 syntax
3. **Simpler maintenance**: Less special cases to worry about
4. **Clearer intent**: Comments explain remaining special cases

## Migration Notes

Programs that relied on keywords running together must be preprocessed:
```bash
# Use fix_keyword_spacing.py (after fixing the OR/AND bug)
python3 utils/fix_keyword_spacing.py old_program.bas
```

## Related Documentation

- `docs/dev/LEXER_CLEANUP_TODO.md` - Original TODO (now complete)
- `docs/dev/LEXER_ISSUES.md` - Historical lexer issues
- `/home/wohl/lexer_sux.txt` - Original complaint that started this