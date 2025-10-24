# MBASIC Compiler Design Notes

## Key Differences: Interpreted vs Compiled BASIC

Based on Microsoft BASIC Compiler (BASCOM) for CP/M and QuickBASIC compiler behavior.

---

## 1. DEF Type Statements (DEFINT, DEFSNG, DEFDBL, DEFSTR)

### Interpreter Behavior (MBASIC)
- **Runtime/Control-flow dependent**: DEF statements are executed when encountered
- **Positional scope**: Only affects variables declared AFTER the DEF statement
- **Dynamic**: Type can change based on program flow

```basic
10 X = 5.5          ' X is single-precision (default)
20 DEFINT X
30 X = 5.5          ' X is now integer, becomes 6 (rounded)
```

### Compiler Behavior (BASCOM/Compiled BASIC)
- **Compile-time/Global scope**: All DEFINT/DEFSNG/DEFDBL/DEFSTR statements are collected during compilation
- **Non-positional**: Affects ALL variables starting with specified letters throughout the entire program
- **Static**: Variable types are determined at compile time and cannot change
- **Module-level**: In modular compilers (QuickBASIC), DEFtype affects all code in that module

```basic
10 X = 5.5          ' Compile error or X treated as integer throughout
20 DEFINT X
30 X = 5.5          ' X is integer everywhere
```

### Compiler Implementation Strategy
1. **First Pass**: Scan entire program for all DEFINT/DEFSNG/DEFDBL/DEFSTR statements
2. **Build Type Map**: Create a mapping of letter ranges to types
3. **Apply Globally**: When encountering variables, apply type rules from the global map
4. **Type Checking**: Ensure no conflicting type declarations

---

## 2. Line Numbers vs Labels

### Interpreter Behavior (MBASIC)
- **Line numbers required**: Every statement must have a line number
- **Execution order**: Determined by line number values
- **GOTO/GOSUB targets**: Must use line numbers

### Compiler Behavior (Modern Approach)
- **Line numbers optional**: Can use alphanumeric labels
- **Labels as targets**: GOTO and GOSUB can use named labels
- **Structured programming**: Encourages use of procedures instead of GOTO

```basic
' Compiled BASIC can support:
StartLoop:
  PRINT "Hello"
  INPUT X
  IF X < 10 THEN GOTO StartLoop
```

### Implementation Strategy
- Accept both line numbers and labels
- Build symbol table mapping labels/line numbers to code positions
- Generate jump instructions to absolute positions

---

## 3. Array Declarations (DIM)

### Interpreter Behavior (MBASIC)
- **Dynamic sizing**: `DIM A(X)` where X is a variable works
- **Runtime allocation**: Arrays allocated when DIM is executed
- **ERASE supported**: Can deallocate arrays at runtime

### Compiler Behavior (BASCOM)
- **Static sizing only**: `DIM A(20)` works, but `DIM A(X)` fails if X is variable
- **Compile-time allocation**: Array sizes must be constants or expressions that can be evaluated at compile time
- **No ERASE**: Arrays cannot be deallocated (static allocation)
- **Metacommands**: `REM $STATIC` or `REM $DYNAMIC` to control array behavior

```basic
' Interpreter - OK
10 INPUT N
20 DIM A(N)

' Compiler - ERROR (unless $DYNAMIC mode)
10 INPUT N
20 DIM A(N)        ' Compile error: non-constant dimension

' Compiler - OK
10 DIM A(100)      ' Constant dimension
```

### Implementation Strategy
1. **Default to static arrays**: Require constant dimensions
2. **$DYNAMIC mode**: Optional support for runtime-sized arrays (with overhead)
3. **Constant folding**: Evaluate constant expressions at compile time

---

## 4. Unsupported Statements in Compiler

### Direct Mode / Interactive Commands
These are interpreter-only and removed in compiled version:

- `AUTO` - automatic line numbering
- `CLEAR` - clear memory (compile-time allocation instead)
- `CONT` - continue after break (debugger feature)
- `DELETE` - delete lines (no source modification in compiled code)
- `EDIT` - edit lines (no source modification)
- `LIST` / `LLIST` - list program (no runtime source access)
- `LOAD` / `SAVE` / `MERGE` - file operations on BASIC source
- `NEW` - clear program
- `RENUM` - renumber lines

### Modified Behavior

- `COMMON` - May not be supported or works differently for linking
- `ERASE` - Not supported in static array mode
- `END` - Becomes program termination, not just stop execution
- `STOP` - May require `/D` debug mode in compiler

---

## 5. Error Handling

### Interpreter Behavior
- **ON ERROR GOTO**: Works as runtime error handler
- **Runtime line numbers**: Error reporting uses line numbers from source

### Compiler Behavior
- **Compile-time checking**: Many errors caught at compile time
- **Runtime errors**: Different error handler structure
- **Special flag required**: `/E` switch needed if using ON ERROR GOTO
- **No line number info**: Compiled code may not retain line number information

---

## 6. Metacommands (Compiler Directives)

Compiler-specific commands not in interpreter:

### `REM $STATIC`
- Arrays are statically allocated at compile time
- Dimensions must be constants
- Faster execution, less memory flexibility

### `REM $DYNAMIC`
- Arrays can be dimensioned at runtime
- Dimensions can be variables
- Slower execution, more memory flexibility
- Required for ERASE to work

### `REM $INCLUDE: 'filename.bas'`
- Include external BASIC source files
- Compile-time file inclusion
- Not available in interpreter

### Other Potential Metacommands
- `REM $DEBUG` - Include debugging information
- `REM $OPTIMIZE` - Optimization level hints
- `REM $DATA` - Data segment directives

---

## 7. DEF FN (User-Defined Functions)

### Interpreter Behavior
- **Single-line only**: DEF FN must be one expression
- **Dynamic binding**: Function definition executed when encountered

```basic
10 DEF FN DOUBLE(X) = X * 2
20 PRINT FN DOUBLE(5)
```

### Compiler Behavior
- **May support multi-line**: Some compilers extend DEF FN to multiple lines
- **Compile-time binding**: Function compiled as inline code or subroutine
- **Type checking**: Arguments and return types checked at compile time

---

## 8. Memory Management

### Interpreter Behavior
- **Dynamic memory**: Variables allocated as needed
- **Garbage collection**: String space managed at runtime
- **CLEAR statement**: Can adjust memory allocation

### Compiler Behavior
- **Static allocation**: All variables allocated at compile time
- **Fixed memory layout**: Data segment, code segment, stack
- **No CLEAR needed**: Memory layout determined by compiler
- **May require size hints**: `/S` stack size, `/D` data size switches

---

## 9. Control Flow Analysis

### Interpreter Behavior
- **No analysis**: Executes line by line
- **Late binding**: GOSUB/GOTO targets resolved at runtime

### Compiler Behavior
- **Flow analysis**: All GOTO/GOSUB targets must exist
- **Unreachable code detection**: May warn about code after END
- **Label resolution**: All labels resolved at compile time
- **Dead code elimination**: Unused subroutines can be removed

---

## 10. Variable Scoping (Later Compilers)

### Interpreter Behavior
- **All global**: Every variable is global
- **No local variables**: Variables in GOSUB subroutines are global

### Compiler Behavior (Advanced)
- **Procedures with local scope**: SUB/FUNCTION with LOCAL variables
- **Parameter passing**: ByVal and ByRef
- **Automatic type inheritance**: Procedures inherit module-level DEFINT etc.

---

## Implementation Recommendations for Our Compiler

### Phase 1: Core Language Subset
1. ✓ **Lexer complete** - handles MBASIC 5.21 syntax
2. **Parser** - build AST with:
   - Global DEFINT/DEFSNG/DEFDBL/DEFSTR collection
   - Constant expression evaluation for DIM
   - Label/line number resolution
   - Control flow graph construction

3. **Semantic Analysis**:
   - Collect all DEF type statements first (pre-pass)
   - Build global type mapping (letter ranges → types)
   - Apply types to all variables
   - Validate array dimensions are constants
   - Check all GOTO/GOSUB targets exist

4. **Code Generation**:
   - Static allocation for all variables
   - Static allocation for arrays
   - Direct jumps for GOTO/GOSUB
   - No runtime interpreter overhead

### Phase 2: Extensions
- Optional $DYNAMIC arrays
- Optional metacommands ($INCLUDE, $STATIC, $DYNAMIC)
- Optional label support (alphanumeric labels)
- Optional procedures with local scope

### Phase 3: Optimization
- Constant folding
- Dead code elimination
- Common subexpression elimination
- Register allocation

---

## Compatibility Considerations

### Source Compatibility
- Programs written for MBASIC interpreter may NOT compile directly
- DEF type statements placement must be reviewed
- Array dimensions must use constants
- Interactive commands must be removed
- Error handling may need modification

### Recommended Approach
1. **Strict Mode**: Pure MBASIC interpreter semantics (issue errors for non-compilable constructs)
2. **Compiler Mode**: Modified semantics with global DEF type scope
3. **Explicit markers**: Require `REM $COMPILED` at start of programs designed for compiler

### Example Incompatibility

```basic
' This works in MBASIC interpreter:
10 X = 5.5: PRINT X          ' Prints 5.5
20 DEFINT X
30 X = 5.5: PRINT X          ' Prints 6

' In compiler, both print statements would print 6
' because DEFINT X applies to entire program
```

---

## Testing Strategy

1. **Create test suite** with both interpreter and compiler versions
2. **Document differences** in behavior
3. **Provide migration guide** for converting MBASIC programs to compilable form
4. **Offer validation tool** to check if program is compiler-compatible

---

## References

- Microsoft BASIC Compiler (BASCOM) for CP/M, 1980
- Microsoft QuickBASIC 4.5 Language Reference
- BASIC-80 (MBASIC) Reference Manual Version 5.21
