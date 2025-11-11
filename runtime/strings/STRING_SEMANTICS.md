# MBASIC String Semantics for Compiler Implementation

## Core Semantic Rules

### 1. String Variables
- All string variables end with `$`
- Maximum length: 255 characters
- Uninitialized strings are empty (""), not null
- String variables are case-insensitive: `NAME$` = `name$` = `Name$`

### 2. String Literals
- Enclosed in double quotes: `"Hello"`
- To include a quote in a string: `"He said ""Hi"""`
- Empty string: `""`
- No escape sequences (no `\n`, `\t`, etc.)

### 3. String Assignment
```basic
A$ = "literal"  ' Direct assignment
B$ = A$         ' Copy/share assignment
```
- Assignment always succeeds (unless out of memory)
- No partial assignment: string is replaced entirely
- Assignment may share data (implementation detail, transparent to user)

### 4. String Concatenation
```basic
C$ = A$ + B$
D$ = "Hello" + " " + "World"
```
- Uses `+` operator (not `&` like some BASICs)
- Result length limited to 255 characters (truncated if longer)
- Empty strings act as identity: `A$ + "" = A$`

### 5. String Comparison
```basic
IF A$ = B$ THEN    ' Equality
IF A$ < B$ THEN    ' Lexicographic comparison
IF A$ > B$ THEN
IF A$ <= B$ THEN
IF A$ >= B$ THEN
IF A$ <> B$ THEN   ' Not equal
```
- Case-sensitive comparison
- Lexicographic (dictionary) ordering
- Empty string is less than any non-empty string

### 6. Substring Functions

#### LEFT$(string$, n)
- Returns leftmost n characters
- If n > LEN(string$), returns entire string
- If n = 0, returns empty string
- If n < 0, error

#### RIGHT$(string$, n)
- Returns rightmost n characters
- If n > LEN(string$), returns entire string
- If n = 0, returns empty string
- If n < 0, error

#### MID$(string$, start [, length])
- Uses 1-based indexing (first character is position 1)
- If start > LEN(string$), returns empty string
- If length omitted, returns from start to end
- If start + length > LEN(string$), returns available characters
- If start < 1, error
- If length < 0, error

### 7. MID$ Statement (Assignment)
```basic
MID$(A$, start [, length]) = replacement$
```
- Replaces characters in-place starting at position `start`
- Uses 1-based indexing
- Does NOT change string length
- If replacement$ longer than space available, truncates
- If start > LEN(A$), no operation
- Original: `A$ = "ABCDEFGH"`
- `MID$(A$, 3, 2) = "XX"` → `A$ = "ABXXEFGH"`
- `MID$(A$, 3) = "12345"` → `A$ = "AB12345H"` (if length omitted, replaces to end)

### 8. String Functions

#### LEN(string$)
- Returns length as integer (0-255)
- LEN("") = 0

#### ASC(string$)
- Returns ASCII code of first character
- Error if string is empty

#### CHR$(n)
- Returns single character string with ASCII code n
- n must be 0-255
- CHR$(65) = "A"

#### VAL(string$)
- Converts string to number
- Stops at first non-numeric character
- VAL("123.45") = 123.45
- VAL("12ABC") = 12
- VAL("ABC") = 0

#### STR$(n)
- Converts number to string
- Includes leading space for positive numbers
- STR$(123) = " 123"
- STR$(-45) = "-45"

### 9. String Arrays
```basic
DIM A$(10)        ' One dimension: A$(0) through A$(10) - 11 elements!
DIM B$(5, 3)      ' Two dimensions: B$(0,0) through B$(5,3)
```
- Arrays are 0-based by default
- Can be 1-based with OPTION BASE 1
- Each element is independent string
- Must be DIMmed before use (unless ≤10 elements)

### 10. INPUT Statement
```basic
INPUT A$
INPUT "Prompt: ", A$
LINE INPUT A$        ' Includes commas in input
```
- INPUT stops at comma or newline
- LINE INPUT reads entire line including commas
- Leading/trailing spaces preserved
- Empty input yields empty string

### 11. PRINT Statement
```basic
PRINT A$
PRINT A$; B$        ' No space between
PRINT A$, B$        ' Tab between
PRINT A$; " "; B$   ' Explicit space
```
- Semicolon: no spacing
- Comma: advance to next tab stop
- Trailing semicolon: no newline

## Implementation Requirements

### Memory Management
1. **Automatic**: User never explicitly allocates/frees
2. **Garbage Collection**: Transparent, happens as needed
3. **Out of Memory**: "?Out of string space error"

### Sharing and Optimization
1. **Substring Sharing**: Implementation may share data
2. **Copy-on-Write**: Transparent to user
3. **Constant Folding**: `"A" + "B"` can become `"AB"` at compile time

### Error Handling
1. **Graceful Degradation**: Operations should not crash
2. **BASIC Errors**:
   - "?Out of string space error"
   - "?Illegal function call" (for invalid arguments)
   - "?Type mismatch" (string/number confusion)

### Edge Cases

#### Empty Strings
- `LEN("") = 0`
- `"" + A$ = A$`
- `LEFT$("", n) = ""`
- `ASC("")` → Error

#### Maximum Length
- All operations truncate at 255 characters
- No error for exceeding limit, just truncation

#### String Sharing
```basic
A$ = "HELLO"
B$ = A$         ' May share
C$ = LEFT$(A$, 3)  ' May share
MID$(B$, 1) = "J"   ' B$ gets own copy, A$ unchanged
```

## Compatibility Notes

### MBASIC 5.21 Compatibility
- All syntax must match exactly
- Same error messages where possible
- Same behavior for edge cases
- Performance improvements are transparent

### Extensions (Not in Original)
- O(n log n) garbage collection (was O(n²))
- String sharing optimization
- Constant string optimization
- These are transparent - programs run identically

## Test Cases for Compiler

The compiler should be tested with:
1. Empty strings
2. Maximum length strings (255 chars)
3. Complex concatenation expressions
4. Nested substring operations
5. Array operations
6. MID$ statement on shared strings
7. Comparison operations
8. Mixed string/numeric operations (VAL, STR$)
9. INPUT with various inputs
10. Memory exhaustion scenarios

## Summary

The compiler must:
1. Preserve exact BASIC string semantics
2. Map operations to runtime functions correctly
3. Handle all edge cases gracefully
4. Maintain 1-based indexing for MID$
5. Ensure garbage collection is transparent
6. Never expose implementation details (sharing, etc.)
7. Generate efficient code while maintaining correctness