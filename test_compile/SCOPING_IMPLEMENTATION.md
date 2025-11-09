# Lexical Scoping Implementation for MBASIC Compiler

## Overview

Implemented proper lexical scoping for control flow structures in the MBASIC-2025 compiler backend, targeting CP/M via z88dk C compilation.

## Features Implemented

### 1. WHILE/WEND Loops
- **BASIC Syntax**: `WHILE condition ... WEND`
- **C Implementation**: Standard C `while (condition) { ... }` loops
- **Scoping**: Properly scoped with C block structure
- **Nesting**: Fully supports nested WHILE loops

### 2. GOTO Statements
- **BASIC Syntax**: `GOTO line_number`
- **C Implementation**: `goto line_XXXX;` with line labels
- **Scoping**: Uses C goto with labeled statements
- **All lines labeled**: Every BASIC line gets a C label for flexibility

### 3. GOSUB/RETURN (Subroutines)
- **BASIC Syntax**: `GOSUB line_number ... RETURN`
- **C Implementation**:
  - Return stack: `int gosub_stack[100]` for return addresses
  - Stack pointer: `int gosub_sp` tracks depth
  - Unique return labels: Each GOSUB gets `gosub_return_N` label
  - Switch dispatch: RETURN uses switch statement to jump to correct return point

- **Scoping Features**:
  - Proper return stack management
  - Support for nested GOSUB calls (limited by stack size of 100)
  - Two-pass compilation to handle forward references
  - Each GOSUB gets unique return ID (0, 1, 2, ...)

- **Algorithm**:
  ```c
  // GOSUB line_number
  gosub_stack[gosub_sp++] = return_id;
  goto line_number;
  gosub_return_N:  // execution continues here after RETURN

  // RETURN
  switch (gosub_stack[--gosub_sp]) {
      case 0: goto gosub_return_0;
      case 1: goto gosub_return_1;
      // ... all return points
  }
  ```

### 4. FOR/NEXT Loops (Previously Implemented, Enhanced)
- **BASIC Syntax**: `FOR var = start TO end [STEP step] ... NEXT var`
- **C Implementation**: `for (var = start; var <= end; var += step) { ... }`
- **Scoping**: Loop variable declared at function scope (BASIC semantics)
- **Integration**: Works correctly with GOSUB inside FOR loops

## Variable Scoping

### Current Implementation
- **All variables global**: Following BASIC semantics, all variables declared at top of main()
- **Type-specific storage**: INTEGER (int), SINGLE (float), DOUBLE (double)
- **Shared across structures**: Variables accessible in subroutines and loops

### Why Global Scope?
Traditional BASIC (including Microsoft BASIC Compiler 1980) uses global variables:
- Variables persist across GOSUB calls
- Loop counters accessible everywhere
- Maintains BASIC language semantics

## Compilation Process

### Two-Pass Generation
1. **First Pass**: Scan program to count GOSUB statements
2. **Second Pass**: Generate code with complete knowledge of all return points

This ensures all RETURN statements have complete switch cases even when RETURN appears before some GOSUB statements in the source.

## Test Results

### Test 1: WHILE/WEND
```basic
120 WHILE I% <= 5
130 PRINT I%
140 I% = I% + 1
150 WEND
```
✓ Outputs: 1, 2, 3, 4, 5

### Test 2: GOTO
```basic
120 GOTO 150
130 PRINT 99  ' Skipped
150 PRINT 1
```
✓ Outputs: 1

### Test 3: GOSUB/RETURN
```basic
120 GOSUB 200
130 I% = 2
140 GOSUB 200
200 PRINT I%
220 RETURN
```
✓ Outputs: 1, 2

### Test 4: Nested GOSUB
```basic
120 GOSUB 300  ' Outer
300 PRINT 2
320 GOSUB 200  ' Inner
200 PRINT 3
220 RETURN
```
✓ Outputs: 1, 2, 3, 4 (correct nesting)

### Test 5: Comprehensive Scoping
- FOR loop with GOSUB inside
- WHILE loop in main
- WHILE loop inside subroutine
- All variables properly scoped

✓ All structures interact correctly

## Code Generation Quality

### Generated C Code Features
- Clean, readable C code
- Proper indentation
- Inline comments for BASIC line numbers
- Comments marking subroutines and return points
- Efficient switch-based dispatch for RETURN

### Example Generated Code
```c
int gosub_stack[100];
int gosub_sp = 0;

line_120:
    gosub_stack[gosub_sp++] = 0;
    goto line_200;
gosub_return_0:

line_200:
    printf("%d\n", i);
line_220:
    if (gosub_sp > 0) {
        switch (gosub_stack[--gosub_sp]) {
            case 0: goto gosub_return_0;
            default: break;
        }
    }
```

## Limitations

1. **GOSUB stack size**: Limited to 100 nested calls (configurable)
2. **No local variables**: All variables global (BASIC semantics)
3. **No recursion limit checking**: Stack overflow possible with deep nesting
4. **RETURN without GOSUB**: Undefined behavior (default case in switch)

## Future Enhancements

1. **Stack overflow detection**: Add runtime check for gosub_sp < 100
2. **ON GOSUB**: Implement computed GOSUB (ON expression GOSUB line1, line2, ...)
3. **ON GOTO**: Implement computed GOTO
4. **Error handling**: Better diagnostics for unmatched GOSUB/RETURN
5. **Optimization**: Eliminate unused return cases from switch statements

## References

- Microsoft BASIC Compiler 1980 Manual (docs/external/Microsoft_BASIC_Compiler_1980.pdf)
- MBASIC 5.21 Language Reference
- z88dk C Compiler Documentation

## Files Modified

- `src/codegen_backend.py`: Added WHILE/WEND, GOTO, GOSUB/RETURN generation
- `test_compile/test_*.bas`: Comprehensive test suite

## Compatibility

- ✓ CP/M executable via z88dk
- ✓ Runs on tnylpo CP/M emulator
- ✓ Compatible with BASIC-80 semantics
- ✓ Maintains MBASIC 5.21 language compatibility
