# Parser Error Categories - Unsolved Parse Problems

**Date**: 2025-10-22
**Total Failures**: 50 files (30.7% of 163 file corpus)
**Successfully Parsing**: 113 files (69.3%)

---

## Executive Summary

The 50 remaining parser failures fall into 12 distinct categories. The top 3 categories account for 58% of all failures:

1. **Assignment/DEF statement issues** (32.0%) - Missing RESET statement, concatenated keywords
2. **Statement continuation issues** (14.0%) - Empty colon statements, statement after semicolon
3. **Invalid expression syntax** (12.0%) - Keywords in expressions, expression parsing edge cases

---

## Category Breakdown

### 1. DEF Statement Without FN / Assignment Issues ⚠️ HIGH PRIORITY
**Files**: 16 (32.0%)

**Root Causes**:

**A. RESET Statement** (10+ files)
- **Issue**: Parser doesn't recognize `RESET` statement
- **Syntax**: `RESET` - closes all files
- **Examples**:
  ```basic
  80 RESET:EF=0:RC=0:OPEN "I",1,NI$       ' asm2mac.bas L8
  7 RESET: SAVE "FXPARMS.BAS",A: STOP     ' fxparms.bas L5
  ```
- **Fix**: Add RESET statement to parser (simple statement, no arguments)

**B. Concatenated Keywords** (3 files)
- **Issue**: Keywords run together with numbers (OCR error or typo)
- **Examples**:
  ```basic
  60 CLEAR1000:PK=12                      ' backgamm.bas L8
  25 CLEAR25,,,8000                       ' satelite.bas L25
  ```
- **Fix**: These are syntax errors, should move to bad_syntax/ (but CLEAR 1000 is valid)

**C. DIM with # (File Numbers)** (3 files)
- **Issue**: OPEN statement uses #1 syntax
- **Examples**:
  ```basic
  10 OPEN"O",#1,"SFAMOVE.0"               ' sfamove.bas L3
  5 OPEN"O",#1,"SFAOBDES.0"               ' sfaobdes.bas L2
  ```
- **Fix**: Parser needs to allow optional `#` before file number in OPEN/CLOSE/PRINT/etc

**D. Other Assignment Edge Cases**
- Multi-variable assignments
- Complex LET statement patterns

**Files**:
- asm2mac.bas, backgamm.bas, bibsr2.bas, blackbox.bas, cpkhex.bas
- fxparms.bas, othello.bas, qsolist.bas, rbsutl31.bas, rc5.bas
- satelite.bas, sfamove.bas, sfaobdes.bas, sfavoc.bas, xformer.bas, xref.bas

---

### 2. Statement Continuation / Line Ending Issues ⚠️ MEDIUM PRIORITY
**Files**: 7 (14.0%)

**Root Causes**:

**A. Empty Colon Statement**
- **Issue**: Lone `:` used as empty statement or label
- **Examples**:
  ```basic
  70 :                                    ' Empty statement line
  770 TM=FM-D(M):GOSUB2880:FM=TM:TM=N::GOSUB2880  ' Double colon
  ```
- **Fix**: Allow empty statement between colons

**B. Statement After Semicolon in PRINT**
- **Issue**: Semicolon in GOSUB followed by newline
- **Example**:
  ```basic
  2950 GOSUB 3750;                        ' handplot.bas L447
  2960 PRINT "HIT RETURN"                 ' Next line
  ```
- **Fix**: Trailing semicolon on GOSUB should be allowed (no-op)

**C. Statement After Closing Paren**
- **Issue**: Complex statement continuation patterns
- **Example**:
  ```basic
  20 DEF FN...(...):X=Y:RETURN           ' ic-timer.bas L29
  ```

**D. Multiple Statements on Line (complex)**
- REM after other statements
- MOD in complex expression contexts

**Files**:
- handplot.bas, ic-timer.bas, oldroute.bas, qubic.bas
- sdir.bas, survival.bas, trade.bas

---

### 3. Invalid Expression Syntax ⚠️ MEDIUM PRIORITY
**Files**: 6 (12.0%)

**Root Causes**:

**A. Keywords in Expression Context**
- **Issue**: DATA, LPRINT, COMMA appearing where expression expected
- **Examples**:
  ```basic
  ' DATA in expression (likely string parsing issue)
  58 ... DATA ...                        ' clock-m.bas L58

  ' LPRINT as expression
  2 ... LPRINT ...                       ' pcat.bas L2
  ```
- **Fix**: Likely multi-statement parsing or string literal issues

**B. Expression Termination**
- NEWLINE appearing unexpectedly in expression
- EQUAL sign in wrong context

**Files**:
- clock-m.bas, deprec.bas, header6.bas, mbasedit.bas, pcat.bas, proset.bas

---

### 4. IF Without THEN/GOTO (Multiline IF) ⚠️ MEDIUM PRIORITY
**Files**: 5 (10.0%)

**Root Causes**:

**A. Line Continuation in IF**
- **Issue**: IF condition spans line in some dialects, or complex condition
- **Examples**:
  ```basic
  288 IF ... [condition at column 56]    ' disasmb.bas
  24 IF ... [condition at column 42]     ' fndtble.bas
  ```
- **Fix**: May be implicit line continuation or missing THEN

**B. Complex Boolean Expressions**
- Very long conditions that may have parsing issues
- Nested parentheses in conditions

**Files**:
- disasmb.bas, fndtble.bas, sortuser.bas, wordpuzl.bas, xref19.bas

---

### 5. Invalid Statement Syntax ⚠️ LOW PRIORITY
**Files**: 4 (8.0%)

**Root Causes**:

**A. STRING$ Function in Wrong Context**
- **Example**:
  ```basic
  163 ... STRING ...                     ' goldmine.bas L163
  ```

**B. ELSE Without Matching IF**
- **Example**:
  ```basic
  153 ... ELSE ...                       ' tricks.bas L153
  ```

**C. Statement Starting with LPAREN or COMMA**
- Syntax errors or unusual patterns

**Files**:
- goldmine.bas, lanes.bas, tricks.bas, unpro2.bas

---

### 6. Expected Variable Name (LINE INPUT Issues) ⚠️ HIGH PRIORITY
**Files**: 3 (6.0%)

**Root Causes**:

**A. LINE INPUT Without #**
- **Issue**: Parser expects file number syntax but finds keyword
- **Example**:
  ```basic
  60 INPUT "DATE <MMDDYY> ";LINE A$      ' dow.bas L10
  ```
- **Fix**: This is actually `INPUT` with `;LINE` modifier, not `LINE INPUT`
  - `;LINE` suppresses the `?` and newline
  - Should parse as: `INPUT "prompt"; LINE A$`

**B. IF as Variable Name**
- Keyword used where variable expected

**Files**:
- dow.bas, scatpad.bas, sleuth.bas

---

### 7. FOR Loop / TO Issues ⚠️ LOW PRIORITY
**Files**: 2 (4.0%)

**Root Causes**:

**A. Missing TO in FOR Loop**
- Likely line continuation or syntax error
- **Example**:
  ```basic
  315 FOR I=1 [expecting TO at column 17] ' bigtime.bas
  ```

**B. Complex FOR Syntax**
- May involve expressions that confuse parser

**Files**:
- bigtime.bas, winning.bas

---

### 8. Missing Comma / Wrong Syntax ⚠️ LOW PRIORITY
**Files**: 2 (4.0%)

**Root Causes**:

**A. AS Keyword in Wrong Context**
- **Example**:
  ```basic
  6 ... AS ...                           ' pckget.bas L6
  ```
- May be `OPEN ... AS #1` syntax from other dialects

**B. Missing Comma in Statement**

**Files**:
- directio.bas, pckget.bas

---

### 9. Line Number Issues ⚠️ MEDIUM PRIORITY
**Files**: 2 (4.0%)

**Root Causes**:

**A. GOTO with Statement Instead of Line Number**
- **Issue**: GOTO followed by statement
- **Example**:
  ```basic
  28 IF ... GOTO PRINT ...               ' division.bas L28
  ```
- **Fix**: This is a syntax error - GOTO needs line number

**B. Complex ON GOTO with Expression**
- ON GOTO list parsing issues

**Files**:
- division.bas, rbbmin27.bas

---

### 10. ON Statement Syntax ⚠️ LOW PRIORITY
**Files**: 1 (2.0%)

**Root Cause**:
- ON expression parsing expecting GOTO or GOSUB

**Files**:
- el-e.bas

---

### 11. SAVE Statement Syntax ⚠️ LOW PRIORITY
**Files**: 1 (2.0%)

**Root Cause**:
- **Issue**: SAVE with ,A parameter
- **Example**:
  ```basic
  32 SAVE "file",A                       ' krakinst.bas L32
  ```
- **Fix**: Parser needs to support `,A` (ASCII format) parameter

**Files**:
- krakinst.bas

---

### 12. Missing Closing Parenthesis ⚠️ LOW PRIORITY
**Files**: 1 (2.0%)

**Root Cause**:
- Likely complex nested expression or function call

**Files**:
- speech.bas

---

## Priority Recommendations

### HIGH PRIORITY (Quick Wins - 38% of failures)

**1. Add RESET Statement** (affects ~10+ files in category 1)
```python
def parse_reset_statement(self):
    """RESET - Close all open files."""
    self.advance()  # consume RESET
    return ResetNode()
```

**2. Support # in File Numbers** (affects 3+ files)
```python
# In OPEN, CLOSE, PRINT #, etc:
if self.match(TokenType.HASH):
    self.advance()
file_num = self.parse_expression()
```

**3. Fix INPUT ;LINE Syntax** (affects 3 files)
```python
# In INPUT parsing:
if self.match(TokenType.SEMICOLON):
    self.advance()
    if self.match(TokenType.LINE):
        self.advance()  # LINE modifier
```

**4. Support SAVE with ,A Parameter** (affects 1 file)
```python
# In SAVE statement:
if self.match(TokenType.COMMA):
    self.advance()
    if self.current_token.value == 'A':
        ascii_mode = True
```

**Estimated Impact**: Fixing these 4 issues could resolve 19 files (38% of failures)

---

### MEDIUM PRIORITY (Moderate Complexity - 34% of failures)

**5. Allow Empty Colon Statements** (affects 7 files)
- Support `:` as empty statement
- Support `::` (double colon)

**6. Fix Multiline IF Detection** (affects 5 files)
- Better handling of complex IF conditions
- Implicit line continuation

**7. Fix Line Number in GOTO/ON GOTO** (affects 2 files)
- Better error messages
- Some may be actual syntax errors to move to bad_syntax/

**Estimated Impact**: 14 files (28% of failures)

---

### LOW PRIORITY (Complex/Edge Cases - 28% of failures)

**8. Expression Parsing Edge Cases** (affects 6 files)
- Keywords appearing in expressions
- Complex expression termination

**9. Statement Syntax Issues** (affects 4 files)
- STRING$ function contexts
- ELSE without IF
- Complex statement patterns

**10. Other Edge Cases** (affects 4 files)
- FOR loop edge cases
- Missing commas
- ON statement variants
- Parenthesis matching

**Estimated Impact**: 14 files (28% of failures)

---

## Implementation Roadmap

### Phase 1: Quick Wins (38% of failures)
1. ✓ Add RESET statement support
2. ✓ Add # in file numbers (OPEN #1, PRINT #1, etc)
3. ✓ Fix INPUT ;LINE syntax
4. ✓ Support SAVE ,A parameter

**Expected Result**: 69.3% → 81% success rate (+19 files)

### Phase 2: Medium Complexity (28% of failures)
5. Allow empty colon statements and ::
6. Improve IF condition parsing (multiline detection)
7. Better GOTO/ON GOTO error handling

**Expected Result**: 81% → 89% success rate (+14 files)

### Phase 3: Edge Cases (28% of failures)
8. Fix expression parsing edge cases
9. Handle complex statement syntax
10. Resolve remaining edge cases

**Expected Result**: 89% → 97%+ success rate (+14 files)

---

## Statistics Summary

| Category | Files | Percentage | Priority |
|----------|-------|------------|----------|
| Assignment/DEF issues | 16 | 32.0% | HIGH |
| Statement continuation | 7 | 14.0% | MEDIUM |
| Expression syntax | 6 | 12.0% | MEDIUM |
| IF without THEN/GOTO | 5 | 10.0% | MEDIUM |
| Invalid statement | 4 | 8.0% | LOW |
| Variable name issues | 3 | 6.0% | HIGH |
| FOR/TO issues | 2 | 4.0% | LOW |
| Missing comma | 2 | 4.0% | LOW |
| Line number issues | 2 | 4.0% | MEDIUM |
| ON statement | 1 | 2.0% | LOW |
| SAVE syntax | 1 | 2.0% | HIGH |
| Missing paren | 1 | 2.0% | LOW |
| **TOTAL** | **50** | **100%** | - |

---

## Expected Success Rates

| Phase | Action | Files Fixed | Success Rate | Improvement |
|-------|--------|-------------|--------------|-------------|
| Current | - | 113/163 | 69.3% | - |
| Phase 1 | Quick wins | +19 | 81.0% | +11.7% |
| Phase 2 | Medium | +14 | 88.8% | +7.8% |
| Phase 3 | Edge cases | +14 | 97.5% | +8.7% |
| Complete | All fixes | +46 | 97.5% | +28.2% |

**Note**: Some files may remain unparseable due to actual syntax errors that should be moved to bad_syntax/.

---

## Files by Category

### Category 1: Assignment/DEF Issues (16 files)
```
asm2mac.bas backgamm.bas bibsr2.bas blackbox.bas cpkhex.bas
fxparms.bas othello.bas qsolist.bas rbsutl31.bas rc5.bas
satelite.bas sfamove.bas sfaobdes.bas sfavoc.bas xformer.bas xref.bas
```

### Category 2: Statement Continuation (7 files)
```
handplot.bas ic-timer.bas oldroute.bas qubic.bas sdir.bas
survival.bas trade.bas
```

### Category 3: Expression Syntax (6 files)
```
clock-m.bas deprec.bas header6.bas mbasedit.bas pcat.bas proset.bas
```

### Category 4: IF Without THEN/GOTO (5 files)
```
disasmb.bas fndtble.bas sortuser.bas wordpuzl.bas xref19.bas
```

### Category 5: Invalid Statement (4 files)
```
goldmine.bas lanes.bas tricks.bas unpro2.bas
```

### Category 6: Variable Name Issues (3 files)
```
dow.bas scatpad.bas sleuth.bas
```

### Categories 7-12: Remaining (15 files)
```
bigtime.bas winning.bas directio.bas pckget.bas division.bas
rbbmin27.bas el-e.bas krakinst.bas speech.bas
```

---

## Next Steps

1. **Implement Phase 1 fixes** (RESET, #, INPUT ;LINE, SAVE ,A)
2. **Retest corpus** to verify improvements
3. **Analyze remaining failures** to refine categories
4. **Implement Phase 2 fixes** (empty colon, multiline IF)
5. **Move actual syntax errors to bad_syntax/** as appropriate

With systematic implementation of these fixes, we can achieve 80%+ success rate in Phase 1, and potentially 90%+ after Phase 2.
