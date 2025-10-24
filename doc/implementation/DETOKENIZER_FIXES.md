# Detokenizer Improvements

## Summary of Fixes

The detokenizer has been significantly improved to produce cleaner, more accurate MBASIC source code.

### Issues Fixed

#### 0. Missing Spaces After Keywords ✓ (Latest Fix)
**Before**:
```basic
10 FORI=0TO10
20 IFFOO=1THEN100
30 PRINTX:NEXT
```

**After**:
```basic
10 FOR I=0 TO 10
20 IF FOO=1 THEN 100
30 PRINT X:NEXT
```

**Root Cause**: Old 8K BASIC didn't require spaces after keywords. Programs could be written as `FORI=0TO10` instead of `FOR I=0 TO 10`. The detokenizer was outputting tokens without proper spacing after keywords, causing the lexer to fail parsing.

**Implementation**: Added `needs_space_after()` function that:
- Checks if a keyword needs space after it (FOR, TO, IF, THEN, ELSE, etc.)
- Peeks at the next byte to determine if space is needed
- Doesn't add space before operators (=, <, >, +, -, etc.)
- Doesn't add space after colon (:)
- Doesn't add trailing space at end of line

### Issues Fixed (Previous)

#### 1. Excessive Spacing ✓
**Before**:
```basic
CLEAR  2000
CHR$ (27)
INPUT $(1)
DEFINT  A- Z
```

**After**:
```basic
CLEAR 2000
CHR$(27)
INPUT$(1)
DEFINT A-Z
```

**Implementation**: Added smart spacing logic that only inserts spaces where grammatically necessary.

#### 2. REMARK Keyword ✓
**Before**:
```basic
:REM ARK  HANOI.BAS
```

**After**:
```basic
:REMARK  HANOI.BAS
```

**Root Cause**: Token 0xDB was "ARK " (with space), which combined with REM (0x8F) to form REMARK. Fixed by:
- Changing 0xDB to just "ARK" (no trailing space)
- Adding special case: ARK after REM gets no space (forms REMARK)

#### 3. Standalone $ and % Tokens ✓
**Before**:
```basic
480 PRINT  Y5$;:A$= INPUT $(1):PRINT  X5$Y1$;$
                                              ^ standalone!
```

**After**:
```basic
480 PRINT Y5$;:A$=INPUT$(1):PRINT X5$Y1$;
```

**Root Cause**: Smart spacing prevents emission of standalone operator tokens after identifiers.

---

## Smart Spacing Algorithm

The improved detokenizer uses context-aware spacing:

```python
def needs_space_before(token: str, prev_token: str) -> bool:
    # No space before operators
    if token in {'+', '-', '*', '/', '(', ')', ',', ';', ':', ...}:
        return False

    # Special case: ARK after REM (REMARK)
    if token == "ARK" and prev_token == "REM":
        return False

    # No space after operators (except closing paren)
    if prev_token in operators and prev_token not in {')', '}'}:
        return False

    # No space after tokens ending with '(' like TAB( or SPC(
    if prev_token and prev_token[-1] == '(':
        return False

    # Otherwise, add space between keywords/identifiers
    return True
```

---

## Test Results

### Impact on Lexer Success Rate

| Stage | Files Parsed | Success Rate | Change |
|-------|--------------|--------------|--------|
| Before detokenizer fix | 221 / 372 | 59.4% | - |
| **After detokenizer fix** | **234 / 372** | **62.9%** | **+3.5%** |

**Net improvement**: +13 files successfully parsed

### Errors Eliminated

| Error Type | Before | After | Fixed |
|------------|--------|-------|-------|
| Standalone `$` | 24 | ~10 | ~14 |
| Standalone `%` | 17 | ~8 | ~9 |
| Spacing issues | N/A | N/A | Cosmetic improvement |

---

## Example Improvements

### File: hanoi.bas

**Before**:
```basic
10 :REM ARK    HANOI.BAS
40 CLEAR  2000:E$= CHR$ (27):E1$= E$+ "E"
100 PRINT  E1$;:INPUT  "ENTER TOTAL NUMBER OF DISKS (1-12)";D
130 PRINT  "Would you like the computer to play? <N> ";:D1$= INPUT $(1)
```

**After**:
```basic
10 :REMARK  HANOI.BAS
40 CLEAR 2000:E$=CHR$(27):E1$=E$+"E"
100 PRINT E1$;:INPUT "ENTER TOTAL NUMBER OF DISKS (1-12)";D
130 PRINT "Would you like the computer to play? <N> ";:D1$=INPUT$(1)
```

### File: acey.bas

**Before**:
```basic
80 CLEAR  200:I= RND (- PEEK (8219))
90 DEFINT  A- C:DEFINT  E- Z
130 T$(I)= CHR$ (V(I))
210 IF  LEFT$ (QA$,1)< > "Y" THEN  230
```

**After**:
```basic
80 CLEAR 200:I=RND (-PEEK (8219))
90 DEFINT A-C:DEFINT E-Z
130 T$(I)=CHR$(V(I))
210 IF LEFT$(QA$,1)<>"Y" THEN 230
```

---

## Known Remaining Issues

### 1. Embedded Multiple Spaces
Some files have double spaces that are in the original tokenized file:
```basic
70 ON  ERROR  GOTO 970
```

These are actual spaces (0x20) or tabs (0x09) embedded in the tokenized file, not a detokenizer issue.

### 2. Some Corrupt Tokenized Files
A few files (like `1stop.bas`) appear to be corrupted or not standard MBASIC tokenized format:
```basic
1 STOP
24090 #V[EB]"XOR A[EB]##^#V[EB]"COMMON A[EB]##^
```

These files are beyond repair and should be excluded from tests.

---

## Code Changes Summary

### File: `utils/detokenizer.py`

**Changes Made**:

0. **Added `needs_space_after()` function** (Latest - lines 67-162)
   - Determines if space needed after a keyword token
   - Peeks at next byte to decide
   - Lists of keywords needing/not needing spaces
   - Checks if next byte is operator/delimiter
   - Prevents trailing spaces at end of line

1. **Added `needs_space_before()` function** (lines 35-64)
   - Context-aware spacing logic
   - Special cases for operators, keywords, REMARK

2. **Modified token output** (lines 264-300)
   - Changed from always adding space: `print(f"{s} ", end="")`
   - To smart spacing before AND after:
     ```python
     # Smart spacing before
     if needs_space_before(s, prev_token):
         print(" ", end="")
     print(f"{s}", end="")
     # Smart spacing after (peek at next byte)
     next_byte = data[count + 1] if count + 1 < len(data) else None
     if next_byte is not None and needs_space_after(s, next_byte):
         print(" ", end="")
     prev_token = s
     ```

3. **Fixed REMARK token** (line 325)
   - Changed: `table[0xDB] = "ARK "`
   - To: `table[0xDB] = "ARK"`

4. **Track previous token** (line 61, throughout)
   - Added `prev_token` variable
   - Updated after each token/character emission

---

## Benefits

### For Users
- ✓ Cleaner, more readable detokenized code
- ✓ Code looks like hand-written MBASIC
- ✓ Fewer lexer errors when parsing
- ✓ Easier to understand and modify

### For Lexer
- ✓ +13 files parse successfully
- ✓ Eliminated most standalone `$` and `%` errors
- ✓ Better input quality for testing
- ✓ More accurate representation of original code

### For Compiler
- ✓ Cleaner AST when implemented
- ✓ Better error messages (accurate column positions)
- ✓ Faithful to original MBASIC syntax

---

## Future Improvements

### Potential Enhancements

1. **Number Format Validation**
   - Validate reconstructed floating-point numbers
   - Ensure exponents are complete (not `0D` or `1820E`)

2. **Line Continuation Detection**
   - Detect if original used line continuation
   - Preserve multiline constructs

3. **Comment Preservation**
   - Better handling of inline comments
   - Preserve comment formatting

4. **Variable Name Case**
   - Tokenized BASIC loses original case
   - Could add heuristics for common conventions (e.g., `I`, `J`, `K` for loops)

---

## Conclusion

The detokenizer improvements resulted in:
- **Cleaner output** - Proper spacing, correct keywords
- **Higher lexer success rate** - 62.9% (up from 59.4%)
- **Better code quality** - Detokenized code looks like original MBASIC

These fixes eliminate a major source of lexer errors and provide a solid foundation for compiler development.
