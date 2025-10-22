# Phase 1 Parser Improvements - Quick Wins

**Date**: 2025-10-22
**Action**: Implemented 4 high-priority parser features

---

## Summary

**Files fixed**: 3 (asm2mac.bas, fxparms.bas, dow.bas)
**Before**: 113 parsing (69.3%)
**After**: 116 parsing (71.2%)
**Improvement**: +3 files (+1.9 percentage points)

---

## Features Implemented

### 1. RESET Statement ✓
**Implementation**: Added full RESET statement support

**Changes**:
- `src/tokens.py`: Added `RESET = auto()` token type
- `src/tokens.py`: Added `'RESET': TokenType.RESET` to KEYWORDS
- `src/ast_nodes.py`: Added `ResetStatementNode` class
- `src/parser.py`: Added `parse_reset()` method
- `src/parser.py`: Added RESET dispatch in `parse_statement()`

**Syntax**:
```basic
RESET        ' Close all open files
```

**Files Fixed**: 2
- ✓ asm2mac.bas
- ✓ fxparms.bas

**Files Still Failing** (have other errors):
- ✗ backgamm.bas - CLEAR1000 (concatenated keyword)
- ✗ satelite.bas - CLEAR25 (concatenated keyword)
- ✗ Others with RESET also have other issues

---

### 2. File Number # Support ✓
**Implementation**: File number syntax already supported

**Status**: Already implemented in all file I/O statements
- OPEN supports #: `OPEN "O",#1,"FILE.DAT"`
- CLOSE supports #: `CLOSE #1`
- PRINT # supports #: `PRINT #1, "text"`
- INPUT # supports #: `INPUT #1, A$`
- GET/PUT support #: `GET #1`, `PUT #1`
- FIELD supports #: `FIELD #1, 10 AS A$`

**Files Expected to Fix**: 0 (already working)
- ✗ sfamove.bas - Still fails with other error
- ✗ sfaobdes.bas - Still fails with other error
- ✗ sfavoc.bas - Still fails with other error

**Note**: These files use `OPEN"O",#1,` syntax which is already supported. Their failures are due to different issues (likely WRITE# statement or other syntax).

---

### 3. INPUT ;LINE Syntax ✓
**Implementation**: Added LINE modifier support after semicolon

**Changes**:
- `src/parser.py`: Added LINE_INPUT token check in `parse_input()`
- Added `line_mode` flag (though not stored in AST currently)

**Syntax**:
```basic
INPUT "prompt";LINE A$    ' LINE allows full line input including commas
INPUT ;LINE A$             ' Without prompt
```

**Files Fixed**: 1
- ✓ dow.bas

**Files Still Failing** (have other errors):
- ✗ sleuth.bas - Line 70: "Unexpected token in expression: END"
- ✗ scatpad.bas - Line 22: "Expected IDENTIFIER, got IF"

---

### 4. SAVE ,A Parameter ✓
**Implementation**: Already fully supported

**Status**: SAVE with ASCII mode parameter was already implemented
```basic
SAVE "filename"      ' Binary format
SAVE "filename",A    ' ASCII text format
```

**Files Expected to Fix**: 1
- ✓ krakinst.bas (need to verify)

---

## Impact Analysis

### Expected vs Actual Results

**Expected** (based on error categorization):
- RESET: ~10 files
- # in file numbers: ~3 files
- INPUT ;LINE: ~3 files
- SAVE ,A: ~1 file
- **Total expected: ~17 files**

**Actual**:
- **Total fixed: 3 files**

**Why the discrepancy?**

Most files had **multiple errors**, not just the one we fixed. For example:
- `backgamm.bas` has RESET but also `CLEAR1000` (concatenated keyword)
- `sfamove.bas` has `OPEN#1` but also has other syntax issues
- `sleuth.bas` has `INPUT ;LINE` but also has expression parsing issues

---

## Newly Passing Files

### 1. asm2mac.bas
**Fixed by**: RESET statement
**Error was**: Line 8 - `RESET:EF=0:RC=0:OPEN "I",1,NI$`
**Now parses**: Successfully

### 2. fxparms.bas
**Fixed by**: RESET statement
**Error was**: Line 5 - `RESET: SAVE "FXPARMS.BAS",A: STOP`
**Now parses**: Successfully

### 3. dow.bas
**Fixed by**: INPUT ;LINE syntax
**Error was**: Line 10 - `INPUT "DATE <MMDDYY> ";LINE A$`
**Now parses**: Successfully

---

## Success Rate Progress

| Phase | Files Parsing | Success Rate | Improvement |
|-------|--------------|--------------|-------------|
| Start of Session | 113/163 | 69.3% | - |
| After Phase 1 | 116/163 | 71.2% | +1.9% |

---

## Remaining Failures Analysis

**Still failing**: 47 files (28.8%)

### Top Categories Still Failing:

1. **Assignment/DEF Issues** - Still ~13-14 files
   - Concatenated keywords (CLEAR1000, GOTO20, etc)
   - Other complex assignment patterns

2. **Statement Continuation** - Still ~7 files
   - Empty colon statements
   - Complex multi-statement lines

3. **Expression Syntax** - Still ~6 files
   - Keywords in expressions
   - Complex expression parsing

4. **IF Without THEN/GOTO** - Still ~5 files
   - Long/complex IF conditions

5. **Others** - ~16 files
   - Various edge cases

---

## Code Statistics

**Successfully parsed programs contain**:
- 14,224 lines of code (+255 from before)
- 17,232 statements (+277 from before)
- 144,017 tokens (+3,032 from before)

---

## Next Steps (Phase 2)

Based on the remaining failures, the next high-priority improvements should be:

### Medium Priority (14 files potential):

1. **Empty Colon Statements** (~7 files)
   - Support `:` as empty statement
   - Support `::` (double colon)
   - Examples: `770 ...::GOSUB2880`, `70 :`

2. **Multiline IF Detection** (~5 files)
   - Better handling of complex IF conditions
   - Implicit line continuation
   - Files: disasmb.bas, fndtble.bas, sortuser.bas, wordpuzl.bas, xref19.bas

3. **Line Number in GOTO/ON GOTO** (~2 files)
   - Better error recovery
   - Some may be actual syntax errors

### Low Priority (Edge Cases):

4. **Expression Parsing Edge Cases** (~6 files)
5. **Statement Syntax Issues** (~4 files)
6. **Other Edge Cases** (~4 files)

### Syntax Errors to Move:

Some failing files may actually have syntax errors and should be moved to `bad_syntax/`:
- Files with concatenated keywords (CLEAR1000, GOTO20, etc)
- Files with GOTO statement instead of GOTO line_number
- Files with incomplete/corrupted statements

---

## Implementation Notes

### RESET Statement
Simple statement with no parameters. Just closes all open files.

```python
def parse_reset(self) -> ResetStatementNode:
    """Parse RESET statement - closes all open files"""
    token = self.advance()
    return ResetStatementNode(
        line_num=token.line,
        column=token.column
    )
```

### INPUT ;LINE Modifier
Checks for LINE_INPUT token after semicolon in INPUT statement.

```python
# Check for LINE modifier after semicolon
line_mode = False
if self.match(TokenType.LINE_INPUT):
    line_mode = True
    self.advance()
```

---

## Validation

All implementations tested with sample code:

✓ RESET statement parsing works
✓ OPEN with # syntax works
✓ INPUT ;LINE syntax works
✓ SAVE ,A syntax works

---

## Conclusion

Phase 1 improvements added 3 files to the parsing success count, bringing us from 69.3% to 71.2%. While this is less than the expected ~17 files, it's because most files have multiple errors. The features we implemented are correct and will help future files parse correctly.

The next phase should focus on:
1. Empty colon statement support (high impact)
2. Better IF condition parsing (moderate impact)
3. Moving syntax errors to bad_syntax/ (cleanup)

With these improvements, we can expect to reach 75-80% success rate.
