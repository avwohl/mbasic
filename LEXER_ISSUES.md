# Lexer Issues Found in Real BASIC Programs

## Test Results Summary

- **Total files tested**: 373
- **Successfully parsed**: 51 (15.8%)
- **Tokenized files (skipped)**: 50
- **Lexer errors**: 272

## Common Issues Identified

### 1. Period (.) in Unexpected Contexts

**Error**: `Unexpected character: '.' (0x2e)`

**Examples**:
```basic
10 :REMARK \t\tADD.BAS\t\tVersion 04.22.81
```

**Issue**: Period appears after line number but not as part of a number literal. This appears to be:
- In REMARK/REM comments (should be skipped)
- In version numbers like `04.22.81`
- After colons as line continuation

**Root Cause**: Lexer doesn't handle periods outside of number contexts. After reading a line number, we skip whitespace but encounter `.` which isn't valid.

**Fix Needed**: This is actually inside REM comments (`:REMARK`), so the issue is that we're not properly detecting REMARK as a keyword, only REM.

---

### 2. Hash/Pound Sign (#) Not at File Number Context

**Error**: `Unexpected character: '#' (0x23)`

**Examples**:
```basic
OPEN "I", #1, "FILE.DAT"
PRINT #1, "DATA"
CLOSE #1
```

**Issue**: The `#` character is used for file numbers in OPEN/PRINT/INPUT/GET/PUT/CLOSE statements. Our lexer doesn't recognize `#` as a valid token.

**Root Cause**: File number syntax `#1`, `#2` not supported. This is standard MBASIC syntax for file I/O.

**Fix Needed**: Add `#` as a token (HASH or FILE_NUMBER_PREFIX), or handle `#` followed by digits as a FILE_NUMBER token.

---

### 3. Square Brackets [ ]

**Error**: `Unexpected character: '[' (0x5b)`

**Examples**:
```basic
PRINT "[MENU]"
DIM A[10]
```

**Issue**: Square brackets appearing in code. Could be:
- In strings (should be fine)
- As array delimiters instead of parentheses (not standard MBASIC)
- Control characters in PRINT statements

**Root Cause**: Some BASIC dialects use `[]` for arrays instead of `()`. This is not MBASIC syntax.

**Fix Needed**: These files may not be MBASIC. Skip or add compatibility mode.

---

### 4. Unterminated Strings

**Error**: `Unterminated string`

**Examples**:
```basic
PRINT "This is a test
```

**Issue**: String literals that span multiple lines or have missing closing quotes.

**Root Cause**: Could be:
- Actual syntax errors in source
- Line continuation characters we don't handle
- Embedded control characters

**Fix Needed**: Investigate specific cases. May need to handle line continuation.

---

### 5. Ampersand (&) in Unexpected Context

**Error**: `Unexpected character: '&' (0x26)`

**Example**:
```basic
X = Y & Z
```

**Issue**: `&` used as operator (string concatenation or bitwise AND in some BASIC dialects).

**Root Cause**: Our lexer only handles `&` when followed by `H` (hex) or `O`/digit (octal). Stand-alone `&` as operator not supported.

**Fix Needed**: In some BASIC dialects, `&` is string concatenation. Need to handle standalone `&`.

---

### 6. Dollar Sign ($) in Unexpected Context

**Error**: `Unexpected character: '$' (0x24)`

**Example**:
```basic
10 A$ = B$ + C$
```

**Issue**: The `$` is being encountered in an unexpected place.

**Root Cause**: Likely a parsing issue where `$` appears after something we don't expect. In MBASIC, `$` should only be part of identifiers/function names.

**Fix Needed**: Debug specific case to understand context.

---

### 7. Null and Control Characters

**Error**: `Unexpected character: '' (0x00)` or `'' (0x1a)`

**Issue**: Binary or control characters in source files.

**Root Cause**: Files may contain:
- EOF markers (0x1A)
- Null terminators
- Binary data

**Fix Needed**: Handle or skip control characters more gracefully.

---

### 8. Colon-Statement Separator Issues

**Example**:
```basic
90 D9=1000::REMARK \tD9 IS DIFFICULTY DETERMINATOR
```

**Issue**: Double colon `::` before REMARK.

**Root Cause**: Empty statement between colons. Should be valid: `::` = empty statement + statement.

**Fix Needed**: Handle multiple colons properly.

---

## Priority Fixes

### High Priority (Common MBASIC Syntax)

1. **Add support for `#` (file numbers)**
   - `OPEN "I", #1, "FILE.DAT"`
   - `PRINT #1, X`
   - Add HASH token type

2. **Recognize REMARK as synonym for REM**
   - Many files use `REMARK` instead of `REM`
   - Add to keyword list

3. **Handle `&` as standalone operator**
   - Some dialects use for string concatenation
   - Add as operator token

4. **Handle control characters in files**
   - Skip 0x1A (EOF marker)
   - Skip 0x00 (null)
   - Better error messages for binary data

### Medium Priority

5. **Better string error recovery**
   - Detect unterminated strings more gracefully
   - Provide better error messages

6. **Handle empty statements (::)**
   - Multiple consecutive colons should be valid

### Low Priority (Non-MBASIC Dialects)

7. **Square brackets `[]`**
   - Not standard MBASIC
   - Mark as dialect-specific

8. **Other dialect-specific features**
   - Some files may be for other BASIC variants
   - Document which features are MBASIC vs extensions

---

## Files Successfully Parsed

These files demonstrate the lexer works for proper MBASIC:
- ACEY.bas (5753 tokens)
- HANOI.bas (1370 tokens)
- ONECHECK.bas (1478 tokens)
- OTHELLO.bas (2058 tokens)
- POKER.bas (3662 tokens)
- And 46 others...

---

## Recommendations

### Immediate Actions

1. **Add `#` token support** for file I/O
2. **Add REMARK keyword** (synonym for REM)
3. **Handle `&` operator** (string concatenation)
4. **Skip control characters** (0x00, 0x1A) more gracefully

### Documentation

1. **Create compatibility matrix** showing which BASIC dialect features we support
2. **Document known limitations** and unsupported dialects
3. **Provide migration guide** for fixing common issues

### Testing

1. **Re-run tests** after fixes
2. **Create unit tests** for each issue type
3. **Identify which files are not MBASIC** and document alternatives

---

## Next Steps

1. Fix high-priority issues in lexer
2. Add tokens for `#` and handle as file number prefix
3. Add REMARK to keywords
4. Handle `&` operator
5. Better control character handling
6. Re-test against corpus
7. Document dialect differences
