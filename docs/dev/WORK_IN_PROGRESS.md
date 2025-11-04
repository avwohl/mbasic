# Work In Progress: Web UI Spacing and Error Reporting Fixes

**Date**: 2025-11-04
**Version**: 1.0.617 → targeting 1.0.618+

## Current Status: DEBUGGING - AVOIDING LOOP

**User complaint**: "note ive asked you fix this at least 6 times. so keep detailed notes in work in progress and watch out for being in a loop"

## Issues to Fix

### 1. Web UI Spacing - TOO MUCH SPACE BETWEEN TOP ROWS ⚠️
**Status**: Working on it (attempt #7+)

**Problem**: User reports "the spacing is the same. too much betwen top rows"

**Previous attempts** (all failed):
- v1.0.599-616: Multiple CSS changes - kept shifting space between top and bottom
- v1.0.617: Set gap:0 on .column, added targeted 2px margins - STILL too much space

**Next approach**:
- Need to MEASURE actual spacing in browser
- Check if NiceGUI is adding padding to menu bar or other elements
- May need to override NiceGUI's menu bar spacing directly

### 2. Duplicate Line Numbers in Error Messages ⚠️
**Status**: Not started

**Problem**: Error messages show line number twice:
```
10: Syntax error in 10: Lexer error at 1:23...
```

**Root cause**: `src/ui/web/nicegui_backend.py:2371` adds `f'Line {line_num}: '` prefix, but the exception message already contains line number info from `src/editing/manager.py:372`

**Fix**: Strip the redundant prefix from error messages in web UI

### 3. Lexer Reports Wrong Line:Column ⚠️
**Status**: Not started

**Problem**: Lexer says "at 1:23" when it should say "at 10:23" (BASIC line number)

**Root cause**: Lexer uses internal token coordinates, not BASIC line numbers

**Fix**: Need to pass BASIC line number context to lexer error reporting

### 4. BASIC Syntax Issue with `$a` ⚠️
**Status**: CONFUSED - need to verify with manual/real MBASIC

**Problem**: User's code `line input "foo" ; $a` gets error: `Unexpected character: '$' (0x24)`

**User says**: The manual shows using `:` separator (I incorrectly told them to use `;`)

**CRITICAL**: Before fixing anything else, I need to:
1. Check the actual Microsoft BASIC manual for LINE INPUT syntax
2. Test with real MBASIC 5.21 to see the correct syntax
3. Verify whether `$a` or `A$` is correct (I claimed `A$` but need to verify)

## Files Modified So Far
- `src/ui/web/nicegui_backend.py` (spacing CSS, v1.0.599-617)

## Files That Need Changes
- `src/ui/web/nicegui_backend.py` (_check_syntax method, line 2371)
- `src/editing/manager.py` (error formatting, line 372)
- `src/lexer.py` (error reporting with BASIC line numbers)
- CSS spacing in nicegui_backend.py (lines 1108-1133)

## Loop Prevention Strategy
1. ✅ Created this WORK_IN_PROGRESS.md doc
2. ✅ Using TodoWrite to track tasks
3. 🔄 BEFORE making any changes: Verify assumptions with manual/real MBASIC
4. 🔄 Test ONE fix at a time, get user feedback before moving to next
5. 🔄 If spacing fix doesn't work, ask user for screenshot or browser inspector info

## Next Steps (IN ORDER)
1. **FIRST**: Check manual for LINE INPUT syntax - is it `:` or `;`?
2. **SECOND**: Verify variable syntax - is it `$a` or `A$`?
3. **THIRD**: Fix spacing issue properly (may need browser debugging)
4. **FOURTH**: Fix error reporting (duplicate line numbers)
5. **FIFTH**: Fix lexer line:column reporting
