# Test Corpus Cleanup - Removed Non-MBASIC 5.21 Dialects

**Date**: 2025-10-22
**Action**: Identified and moved non-MBASIC 5.21 programs to bad_not521/

## Problem

The test corpus in `bas_tests1/` contained programs from multiple BASIC dialects:
- CP/M MBASIC 5.21 (target dialect)
- Atari BASIC (TRAP, SETCOLOR, GRAPHICS, etc.)
- Applesoft BASIC (VTAB, HTAB, INVERSE, etc.)
- Kaypro BASIC (WINDOW, WSELECT, etc.)

This was causing the compiler to report failures on programs that were never intended to work with MBASIC 5.21.

## Investigation

Scanned all 235 files in bas_tests1/ for dialect-specific statement keywords:

### Atari BASIC Indicators
- `TRAP line_number` - Error handling
- `SETCOLOR` - Color palette
- `GRAPHICS` - Graphics mode
- `PLOT` / `DRAWTO` - Graphics commands
- `COLOR` - Color assignment

### Applesoft BASIC Indicators
- `VTAB` / `HTAB` - Cursor positioning
- `HGR` / `HPLOT` / `HCOLOR` - Hi-res graphics
- `FLASH` / `INVERSE` / `NORMAL` - Text modes

### Kaypro BASIC Indicators
- `WINDOW` - Window definition
- `WSELECT` - Window selection

## Files Moved to bad_not521/

**8 files** identified with clear dialect-specific statements:

1. **amodem42.bas** - Atari BASIC (TRAP, SETCOLOR)
2. **binhex.bas** - Atari BASIC (TRAP)
3. **graph.bas** - Applesoft BASIC (VTAB)
4. **hexbin11.bas** - Atari BASIC (TRAP)
5. **ibmftp.bas** - Atari BASIC (COLOR)
6. **ibmmdm.bas** - Atari BASIC (COLOR)
7. **stackalc.bas** - Kaypro BASIC (WINDOW, WSELECT)
8. **upload.bas** - Applesoft BASIC (VTAB)

## Results

**Before Cleanup:**
- Total files: 235
- Successfully parsed: 84 (35.7%)
- Parser failures: 151 (64.3%)

**After Cleanup:**
- Total files: 227 (-8 files)
- Successfully parsed: 84 (37.0%)
- Parser failures: 143 (63.0%)

**Success rate improvement**: 35.7% → 37.0% (+1.3 percentage points)

## Error Distribution Changes

**"Expected EQUAL, got NUMBER" errors:**
- Before: 16 files
- After: 11 files (-5 files)
- Reduction: Files with TRAP, SETCOLOR, VTAB statements eliminated

**DEF function errors:**
- Before: 3 files (ibmmdm.bas, surround.bas, tanks.bas)
- After: 2 files (surround.bas, tanks.bas)
- ibmmdm.bas was Atari BASIC, properly moved

## Benefits

1. **Cleaner metrics**: Success rate now reflects true MBASIC 5.21 compatibility
2. **Focused development**: Can concentrate on actual MBASIC 5.21 features
3. **Accurate error analysis**: Remaining errors are legitimate MBASIC 5.21 issues
4. **Better testing**: Test corpus now properly represents target dialect

## Methodology

Conservative approach used:
- Only moved files with **actual statement keywords** in code
- Did NOT move files based on comments or string contents
- Did NOT move files based on disk notation alone (`D:` can appear in strings)
- Verified each file had actual dialect-specific executable statements

## Current Status

**Clean MBASIC 5.21 corpus:**
- 227 files in bas_tests1/
- 84 files (37.0%) parsing successfully
- 143 files (63.0%) with legitimate MBASIC 5.21 parsing issues to fix

**Dialect-specific corpus:**
- 8 files in bad_not521/
- Preserved for potential future multi-dialect support
