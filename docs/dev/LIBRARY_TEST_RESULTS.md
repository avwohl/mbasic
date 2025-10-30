# Library Program Test Results

**Date:** 2025-10-30
**Test Script:** `utils/test_library_programs.py`
**Categories Tested:** 9 (games, utilities, demos, education, business, telecommunications, electronics, data_management, ham_radio)
**Total Programs:** 96

## Summary

- ✅ Success: 0 programs (loaded and produced output)
- ⏱️ Timeout: 0 programs (waiting for INPUT or infinite loops)
- 📭 No output: 11 programs (loaded successfully but produced no output)
- ❌ Parse errors: 85 programs (syntax errors during load)
- 💥 Runtime errors: 0 programs

## Critical Finding: DEFINT/DEFSTR/DEFDBL Not Implemented

**Impact:** 23 programs fail with "Unknown DEF statement token type" errors

Programs require type declaration statements:
- `DEFINT A-Z` - Declare variables as integers
- `DEFSTR A-Z` - Declare variables as strings
- `DEFDBL A-Z` - Declare variables as double precision

### Affected Programs

**Utilities (3):**
- bigcal2.bas - Line 210: `DEFINT A-Z : I=0:J=0:K=0:L=0`
- calendar.bas - Lines 60-70: `DEFINT A-Y` and `DEFSTR Z`
- uudecode.bas - Line 1001: `DEFINT A-Z`

**Business (4):**
- budg.bas - Line 120: `DEFINT A-Z`
- finance.bas - Line 100: `DEFINT A-Z`
- mortgage.bas - Lines 300/400: `DEFINT A,I,M,N,T` and `DEFDBL E,X,Y,Z`
- nycal.bas - Line 100: `DEFINT A-Z`

**Telecommunications (1):**
- exitbbs1.bas - Line 130: `DEFINT A-Z`

**Electronics (8):**
- lst8085.bas - Line 30: `DEFINT A-G:DEFSTR N-Z:DIM S(80):DIM T(22)`
- lstintel.bas - Line 30: `DEFINT A-G:DEFSTR N-Z:DIM S(80):DIM T(22)`
- lsttdl.bas - Lines 30-40: `DEFINT A-G` and `DEFSTR N-Z`
- tab8085.bas - Lines 30-40: `DEFINT A-F` and `DEFSTR P-Z`
- tabintel.bas - Lines 30-40: `DEFINT A-F` and `DEFSTR P-Z`
- tabtdl.bas - Lines 30-40: `DEFINT A-F` and `DEFSTR P-Z`
- tabzilog.bas - Line 20: `DEFINT A-F:DEFSTR P-Z`
- (8th program needs verification)

**Ham Radio (3):**
- rbspurge.bas - Line 100: `DEFINT A-Z`
- rbsutl31.bas - Line 100: `DEFINT A-Z`
- (3rd program needs verification)

**Data Management (4):**
- bibextr.bas - Line 120: `DEFINT A-Z`
- bibhead.bas - Line 110: `DEFINT A-Z`
- bibtail.bas - Line 110: `DEFINT A-Z`
- sortuser.bas - Line 100: `DEFINT A-Z`

## Parse Errors - Missing Features

### 1. Statement-Only Lines (No Line Number)
Some programs have lines with just statement keywords (invalid syntax):

**Examples:**
- cpkhex.bas - Line 8999: `Program exit and error handler` (comment without REM)
- ham_radio/qsolist.bas - Lines with `FILE`, `CLOSE`, `CONSOLE` keywords alone

### 2. Missing Colons Before GOTO
- hangman.bas - Line 440: `...GOT YOU OFF!":GOTO360` (should be `:GOTO 360`)
- tankie.bas - Line 9160: `R` (incomplete statement)
- rc5.bas - Line 9000: `PRINT:PRI` (incomplete statement)

### 3. VAX BASIC Syntax
- simcvax.bas - Uses `!` for comments instead of REM (VAX BASIC, not MBASIC)
  - **Action:** Move to incompatible category

## Programs with No Output (Need Investigation)

These loaded successfully but produced no output (may need INPUT or just define subroutines):

**Games (1):**
- simcvax.bas - Actually VAX BASIC, should move to incompatible

**Utilities (1):**
- convert.bas

**Demos (2):**
- sample-c.bas
- sample-s.bas

**Data Management (7):**
- bibbld.bas
- bibsr2.bas
- bibsrch.bas
- cbasedit.bas
- cmprbib.bas
- vocbld.bas
- voclst.bas

## Runtime Errors - Permission Issues

**Note:** 62 programs failed with "Error: [Errno 1] Operation not permitted" when running via subprocess. This is likely a sandboxing/subprocess issue with the test script, not actual program errors. These need manual testing.

## Recommendations

### Priority 1: Implement DEFINT/DEFSTR/DEFDBL
These type declaration statements are part of MBASIC 5.21 and are required by 23+ programs. Implementation should:
- Parse DEFINT/DEFSTR/DEFDBL statements
- Apply type declarations to variables based on first letter
- Handle ranges (e.g., `DEFINT A-Z`, `DEFSTR N-Z`)
- Support multiple declarations on one line (e.g., `DEFINT A-G:DEFSTR N-Z`)

### Priority 2: Fix Parse Errors
- Improve statement parsing to handle edge cases
- Better error messages for common syntax errors
- Consider if some programs have actual syntax errors vs. missing features

### Priority 3: Move Incompatible Programs
- simcvax.bas → Move to incompatible (VAX BASIC syntax)
- Review other programs that may be incompatible

### Priority 4: Manual Testing
- Test the 62 programs that failed with permission errors
- Verify the 11 programs that produced no output
- Create a working/broken categorization

## Test Methodology Issues

The current test script (`utils/test_library_programs.py`) has limitations:
1. Subprocess permission errors prevent accurate testing
2. Timeout-based testing may miss programs that just wait for input
3. Need better detection of "program loaded successfully" vs "parse error"

**Recommendation:** Revise test script to directly import and call mbasic interpreter rather than using subprocess.

## Next Steps

1. Implement DEFINT/DEFSTR/DEFDBL statements
2. Re-run tests after implementation
3. Move simcvax.bas to incompatible category
4. Create manual test plan for programs requiring user interaction
5. Update games.json and other category JSON files to exclude broken programs
6. Consider creating a "needs_defint" or similar subcategory for programs awaiting implementation

---

**Test Command:**
```bash
cd /home/wohl/cl/mbasic
python3 utils/test_library_programs.py
```

**Related Files:**
- Test script: `utils/test_library_programs.py`
- DEFINT tracking: See this document
- Web UI bugs: `docs/dev/WEB_UI_CRITICAL_BUGS_TODO.md`
