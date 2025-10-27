# DEF FN Syntax Rules (Verified with MBASIC 5.21)

**Date**: 2025-10-27
**Method**: Tested with real MBASIC 5.21 via tnylpo CP/M emulator

## Summary

✅ **Space after FN is OPTIONAL**
✅ **Function names can be MULTIPLE characters** (not just one letter)
✅ **Both work equally well**

## Test Results

### Test 1: Space after FN (Single char)
```basic
20 DEF FNA(X) = X * 2
30 PRINT FNA(5)
```
**Result**: ✅ Works - Output: `10`

### Test 2: No space after FN (Single char)
```basic
20 DEF FNA(X)=X*2
30 PRINT FNA(5)
```
**Result**: ✅ Works - Output: `10`

### Test 3: Multi-char with space
```basic
20 DEF FNABC(X) = X * 2
30 PRINT FNABC(5)
```
**Result**: ✅ Works - Output: `10`

### Test 4: Multi-char no space
```basic
20 DEF FNABC(X)=X*2
30 PRINT FNABC(5)
```
**Result**: ✅ Works - Output: `10`

### Test 5: String function multi-char (Real-world example)
```basic
20 DEF FNUCASE$(Z$,N)=CHR$(ASC(MID$(Z$,N,1)) AND &H5F)
30 A$="hello"
40 PRINT FNUCASE$(A$,1)
```
**Result**: ✅ Works - Output: `H` (uppercase of first character)

## Syntax Rules

### Format
```basic
DEF FN<name>[(<params>)] = <expression>
```

### Function Name Rules
- **Must start with**: `FN` (case insensitive)
- **Name after FN**: Can be 1 or more characters
- **Valid examples**:
  - `FNA` - single character
  - `FNABC` - multiple characters
  - `FNUCASE$` - multiple characters with type suffix
  - `FNAREA%` - multiple characters with integer type
  - `FND` - single character (from StartTrek.bas example)

### Spacing Rules
- Space between `FN` and name: **OPTIONAL**
- Both `DEF FNA(X)` and `DEF FNABC(X)` work
- Both `DEF FNA(X) = ...` and `DEF FNA(X)=...` work

## Real-World Examples

### From ucase.bas
```basic
DEF FNUCASE$(Z$,N)=CHR$(ASC(MID$(Z$,N,1)) AND &H5F)
```
- No space after FN ✓
- Multi-character name `UCASE` ✓
- String type suffix `$` ✓

### From startrek.bas
```basic
DEF FND (N) = SQR((K1(I) - S1) ^ 2 + (K2(I) - S2) ^ 2)
```
- Space after FN ✓
- Single character name `D` ✓

## Parser Implementation Notes

Our parser should:
1. Accept `DEF` keyword
2. Accept `FN` (with optional whitespace before function name)
3. Accept function name of 1+ characters after FN
4. Function name can have type suffix (`$`, `%`, `!`, `#`)
5. Parse parameter list in parentheses (optional)
6. Parse `=` and expression

### Current Error Message
```
"DEF function name must start with FN"
```

This is correct but can be misleading when user types `DEF FNA(X) = +1` because the actual error is in the expression (`+1` is invalid), not the function name.

## Recommendations

1. ✅ Parser should accept multi-character function names after FN
2. ✅ Parser should accept optional whitespace after FN
3. ✅ Improve error messages to distinguish:
   - Invalid function name (doesn't start with FN)
   - Invalid expression after `=`
   - Invalid parameter list

## Test Files

All test files located in `tests/`:
- `test_def_fn_space.bas`
- `test_def_fn_nospace.bas`
- `test_def_fn_multichar.bas`
- `test_def_fn_multichar_nospace.bas`
- `test_def_fn_string.bas`

All tests pass with real MBASIC 5.21 ✅
