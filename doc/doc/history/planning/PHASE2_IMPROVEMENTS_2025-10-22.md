# Phase 2 Parser Improvements - Syntax Error Cleanup

**Date**: 2025-10-22
**Action**: Moved files with clear syntax errors to bad_syntax/

---

## Summary

**Files moved to bad_syntax**: 2
**Before**: 116/163 parsing (71.2%)
**After**: 116/161 parsing (72.0%)
**Improvement**: +0.8 percentage points (corpus cleanup)

---

## Files Moved to bad_syntax/

### 1. division.bas
**Reason**: GOTO with statement instead of line number

**Error**: Line 28 - `GOTO PRINT` (syntax error)

**Example**:
```basic
280 IF 100*R/V1>75 GOTO PRINT CS$Y$"&0SUPER!!"
```

**Issue**: GOTO requires a line number, not a statement. This is invalid MBASIC 5.21 syntax.

**Category**: Syntax error - malformed GOTO

---

### 2. sortuser.bas
**Reason**: Multiline IF statement (not MBASIC 5.21)

**Error**: Line 55 - IF condition continues on next line

**Example**:
```basic
740	IF I<>LAST.RECORD+1
	THEN PRINT "Output file incorrect size..ERROR..aborting" : STOP
```

**Issue**: The IF condition is on one line, THEN is on the next line. This is not standard MBASIC 5.21 syntax (likely structured BASIC or BASIC-80 5.3+ extension).

**Category**: Non-MBASIC 5.21 dialect feature

---

## Analysis of Remaining Failures

### Current Status
- **Total files**: 161 (down from 163)
- **Parsing**: 116 (72.0%)
- **Failing**: 45 (28.0%)

### Failure Categories

#### 1. Parser Limitations (4 files) - Complex IF Conditions
These files have very long or complex IF conditions that may hit parser limits:

- disasmb.bas - Line 288, column 56
- fndtble.bas - Line 24, column 42
- wordpuzl.bas - Line 113, column 59
- xref19.bas - Line 134, column 78

**Investigation needed**: These may be valid MBASIC but hit expression parsing limits or have subtle issues.

#### 2. Expected EQUAL Errors (6+ files)
Pattern: Parser expects `=` but gets something else

Files:
- backgamm.bas - Expected EQUAL, got COLON (likely CLEAR1000)
- bibsr2.bas - Expected EQUAL, got IF
- blackbox.bas - Expected EQUAL, got SEMICOLON (NULL subroutine call)
- cpkhex.bas - Expected EQUAL, got IDENTIFIER
- othello.bas - Expected EQUAL, got IDENTIFIER

**Common causes**:
- Concatenated keywords (CLEAR1000 instead of CLEAR 1000)
- Subroutine calls with unusual syntax
- Complex statement patterns

#### 3. Expression Syntax Errors (6 files)
Unexpected tokens in expressions:

- clock-m.bas - DATA in expression
- deprec.bas - EQUAL in expression
- header6.bas - NEWLINE in expression
- mbasedit.bas - NEWLINE in expression
- pcat.bas - LPRINT in expression
- proset.bas - COMMA in expression

**Likely causes**: String literal issues, multi-statement parsing edge cases

#### 4. Statement Syntax Errors (7 files)
- handplot.bas - Expected : or newline, got SEMICOLON
- ic-timer.bas - Expected : or newline, got RPAREN
- oldroute.bas - Expected : or newline, got LPAREN
- sdir.bas - Expected : or newline, got COMMA
- survival.bas - Expected : or newline, got REM (REM after THEN without colon)
- trade.bas - Expected : or newline, got MOD
- qubic.bas - Expected : or newline, got IDENTIFIER

**Likely causes**: Statement continuation, REM after THEN, complex multi-statement lines

#### 5. Other Edge Cases (22 files)
Various unique issues requiring individual investigation

---

## Progress Tracking

### Session Start
- **Files**: 163
- **Parsing**: 113 (69.3%)

### After Phase 1 (Quick Wins)
- **Files**: 163
- **Parsing**: 116 (71.2%)
- **Improvement**: +3 files, +1.9%
- **Added**: RESET, INPUT ;LINE, SAVE ,A (already existed), # support (already existed)

### After Phase 2 (Syntax Cleanup)
- **Files**: 161 (moved 2 to bad_syntax)
- **Parsing**: 116 (72.0%)
- **Improvement**: +0.8% (corpus quality)
- **Moved**: division.bas, sortuser.bas

---

## Corpus Quality

### Current Directories

**basic/bas_tests1/** - 161 files (main test corpus)
- 116 parsing (72.0%)
- 45 failing (28.0%)

**basic/bad_syntax/** - 18 files
- Files with clear syntax errors
- Cannot be parsed by any MBASIC 5.21 parser

**basic/bad_not521/** - 40 files
- Valid BASIC but uses non-MBASIC 5.21 features

**Total**: 219 .bas files

---

## Lessons Learned

### What We Discovered

1. **Many errors have multiple causes**: Files often have more than one issue. Fixing RESET didn't fix all files with RESET because they also had other problems.

2. **Concatenated keywords are common**: Many files have `CLEAR1000` instead of `CLEAR 1000`, `GOTO1500` instead of `GOTO 1500`. These are likely OCR errors or typos.

3. **Multiline IF is rare**: Only found one file (sortuser.bas) with multiline IF. This is a dialect extension.

4. **Complex IF conditions**: Some files have very long IF conditions that may hit parser complexity limits.

5. **Most improvements already existed**: # in file numbers and SAVE ,A were already implemented. Only RESET and INPUT ;LINE were truly new.

---

## Next Steps for Phase 3

### High-Priority Investigations (Likely Quick Wins)

1. **REM After THEN Without Colon** (1 file: survival.bas)
   - MBASIC allows: `IF x THEN 100 REM comment`
   - Parser may require: `IF x THEN 100:REM comment`
   - Fix: Allow REM after line number in THEN clause

2. **Trailing Semicolon on Statements** (1 file: handplot.bas)
   - Example: `GOSUB 3750;` (trailing semicolon)
   - Fix: Allow optional trailing semicolon (no-op)

3. **ON GOTO/GOSUB Parsing** (1 file: el-e.bas)
   - May be edge case in ON statement parsing
   - Needs investigation

### Medium-Priority

4. **Concatenated Keywords** (Multiple files)
   - Decision needed: Fix in parser or move to bad_syntax?
   - Likely OCR errors (CLEAR1000, GOTO20, etc.)

5. **Complex Expression Parsing** (6 files)
   - Keywords in expression context
   - Expression termination issues

6. **Statement Continuation Edge Cases** (6 files)
   - Various unexpected token combinations

### Future Work

7. **Complex IF Conditions** (4 files)
   - May require parser improvements
   - Or may have subtle syntax errors

---

## Statistics

### Code Coverage
Successfully parsed programs contain:
- 14,224 lines of code
- 17,232 statements
- 144,017 tokens

### Session Progress
- **Started**: 69.3%
- **After Phase 1**: 71.2% (+1.9%)
- **After Phase 2**: 72.0% (+0.8%)
- **Total gain**: +2.7%

### Remaining Work
- **45 files** still failing (28.0%)
- Estimated potential: 80-85% with Phase 3 fixes
- Some files may be actual syntax errors to move

---

## Conclusion

Phase 2 focused on corpus cleanup by moving clear syntax errors to appropriate directories. This improved the success rate from 71.2% to 72.0% by reducing the test corpus size while maintaining the same number of passing files.

The cleanup revealed that many remaining failures are edge cases requiring individual investigation rather than broad parser improvements. The next phase should focus on targeted fixes for specific patterns like REM after THEN and trailing semicolons.

With continued systematic investigation and fixes, we can reach 75-80% success rate, with remaining files likely being actual syntax errors or non-MBASIC 5.21 dialect features.
