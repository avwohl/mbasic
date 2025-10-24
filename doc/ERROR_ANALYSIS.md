# Detailed Error Analysis - MBASIC Lexer

## Summary Statistics

**Test Corpus**: 373 files in `bas_tests1/`
- **Successfully parsed**: 163 files (43.7%)
- **Errors**: 210 files (56.3%)

---

## Error Categories

### 1. Period (.) Errors - 86 files (41% of errors)

#### Issue 1: Numbers starting with decimal point
**Example**: `.995*A(I)` from `555-ic.bas:400`
```basic
400 IF .995*A(I)>D THEN 420
```

**Problem**: MBASIC allows `.5` as shorthand for `0.5`
**Fix needed**: Update lexer to accept numbers starting with `.`

#### Issue 2: Periods in REM comments
**Example**: `upload.bas:110`
```basic
135 REM !          !    950 I    .    .    .    .    .    .    .    !          !
```

**Problem**: This should work fine since it's after REM, but error suggests REM not properly consuming rest of line
**Fix needed**: Verify REM handling is correct

#### Issue 3: Commodore BASIC abbreviations
**Example**: `P.` for `PRINT`, `G.` for `GOTO` (common in C64 BASIC)
**Problem**: This is non-MBASIC dialect
**Action**: Document as incompatible dialect

---

### 2. Unterminated String Errors - 48 files (23% of errors)

**Common causes**:

#### Cause 1: Detokenizer issues
Detokenized files may have malformed strings due to detokenization bugs

#### Cause 2: Embedded quotes
```basic
PRINT "He said "Hello" to me"
```
MBASIC doesn't have escape sequences - may use concatenation instead

#### Cause 3: Line continuation
Some BASIC dialects allow line continuation with backslash or underscore

**Investigation needed**: Look at specific examples to determine if fixable

---

### 3. Dollar Sign ($) Errors - 24 files (11% of errors)

#### Issue: Standalone $ tokens
**Example**: `add.bas:50`
```basic
480 PRINT  Y5$;:A$= INPUT $(1):PRINT  X5$Y1$;$
```

**Problem**: Detokenizer bug - standalone `$` at end of line
**Root cause**: Detokenizer spacing/token separation issue
**Action**:
- Option 1: Fix detokenizer to not emit standalone `$`
- Option 2: Lexer could skip standalone `$` as malformed token

---

### 4. Percent Sign (%) Errors - 17 files (8% of errors)

**Similar to $ errors**: Likely standalone `%` from detokenizer issues

**Example investigation needed**: Check if `%` appears standalone or in other contexts

---

### 5. Square Brackets [ ] - 18 files (9% of errors)

**Problem**: Non-MBASIC dialect using `[]` for arrays

**Examples**:
```basic
DIM A[10]           ' Instead of DIM A(10)
X = ARRAY[INDEX]    ' Instead of ARRAY(INDEX)
```

**Action**: These are genuinely different BASIC dialects (possibly GW-BASIC with extensions, or other variants)

---

### 6. Invalid Number Format - 5 files

**Examples**:
- `create.bas`: `0D` - Malformed double-precision number
- `dir.bas`: `0E` - Malformed exponential
- `foo.bas`: `2d` - Missing exponent
- `starwars.bas`: `1820E` - Missing exponent sign/digits

**Problem**: Detokenizer may be incorrectly reconstructing floating-point numbers

---

### 7. Other Characters (Low frequency)

- **@ (at sign)** - 2 files: TRS-80 or positioning syntax
- **! (exclamation)** - 2 files: Could be type suffix or comment in some dialects
- **_ (underscore)** - 3 files: Variable names or line continuation
- **` (backtick)** - 1 file: Unknown usage
- Various Unicode/high-bit chars - 1-2 files each: Encoding issues or binary data

---

## Recommended Fixes (Priority Order)

### High Priority - Will fix ~90 files (43%)

#### 1. Support numbers starting with decimal point
**Impact**: 86 files
**Implementation**:
```python
# In read_number(), before reading digits:
if char == '.' and self.peek_char() and self.peek_char().isdigit():
    # Leading decimal point - valid in BASIC
    num_str += self.advance()
```

**Complexity**: Low - small lexer change

#### 2. Fix or filter detokenizer artifacts
**Impact**: ~30-40 files ($ and % errors, malformed numbers)
**Options**:
- Fix detokenizer spacing
- Add lexer tolerance for standalone `$`, `%` (skip them)
- Document which detokenized files are unreliable

**Complexity**: Medium - requires detokenizer work OR lexer tolerance

### Medium Priority - Will fix ~48 files (23%)

#### 3. Investigate unterminated strings
**Impact**: 48 files
**Action**: Manual review of examples to categorize:
- Real syntax errors → mark as invalid
- Detokenizer bugs → fix detokenizer
- Dialect differences → document

**Complexity**: High - requires case-by-case analysis

### Low Priority - Different BASIC dialects

#### 4. Square brackets
**Impact**: 18 files
**Action**: Add optional compatibility mode OR document as non-MBASIC
**Complexity**: Medium - would require parser changes too

#### 5. Abbreviations (P. for PRINT)
**Impact**: Unknown, mixed with other period errors
**Action**: Document as Commodore BASIC, not MBASIC
**Complexity**: High - ambiguous with other uses of period

---

## Quick Win Implementation

The **highest ROI fix** is supporting decimal-point-leading numbers (`.5` syntax).

### Current Code (lexer.py, line ~122)
```python
# Check for decimal point
if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
    num_str += self.advance()  # Consume '.'
```

### Issue
This only works if we've already read some digits. Need to allow starting with `.`

### Fix
Handle `.` as start of number in main tokenization loop:

```python
# Numbers (including .5 shorthand)
if char.isdigit() or (char == '.' and self.peek_char() and self.peek_char().isdigit()):
    self.tokens.append(self.read_number())
    continue
```

Then in `read_number()`, handle leading decimal:
```python
# Check for leading decimal point
if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
    num_str += self.advance()

# Read decimal digits before decimal point (or after if we had leading .)
while self.current_char() is not None and self.current_char().isdigit():
    num_str += self.advance()
```

This single change should resolve 86 files (40% of remaining errors)!

---

## Expected Results After Quick Win

- **Current**: 163 files (43.7%) parsed successfully
- **After decimal-point fix**: ~249 files (66.8%) estimated
- **Improvement**: +86 files, +23 percentage points

---

## Long-term Recommendations

1. **Improve detokenizer**:
   - Fix spacing around operators
   - Fix standalone `$` and `%` emissions
   - Validate number reconstruction

2. **Dialect detection**:
   - Auto-detect square brackets → mark as non-MBASIC
   - Detect abbreviations → mark as Commodore BASIC
   - Add `--dialect` flag to lexer

3. **Robust error recovery**:
   - Continue after some errors
   - Report multiple errors per file
   - Suggest fixes

4. **Test corpus curation**:
   - Separate known-good MBASIC files
   - Create dialect-specific test suites
   - Mark files with detokenization issues
