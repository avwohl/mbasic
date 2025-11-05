---
description: Technical overview of MBASIC's interpreter and compiler architecture
keywords:
- architecture
- array
- branch
- command
- compiler
- condition
- dim
- error
- execute
- file
title: 'MBASIC Architecture: Interpreter and Compiler'
type: guide
---

# MBASIC Architecture: Interpreter and Compiler

## Overview

MBASIC is a **runtime interpreter** for MBASIC-80 programs. Unlike traditional BASIC interpreters that re-parse code on each execution, MBASIC uses a modern **compile-then-execute** architecture for better performance.

## Architecture Diagram

```
┌─────────────────┐
│  .BAS Source    │
│   File          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Lexer       │  Convert source to tokens
│  (lexer.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Parser      │  Build Abstract Syntax Tree (AST)
│  (parser.py)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AST (Program   │  Parsed representation
│  Structure)     │
└────────┬────────┘
         │
         ├──────────────────────────┐
         │                          │
         ▼                          ▼
┌─────────────────┐        ┌──────────────────┐
│  Interpreter    │        │  Semantic        │
│  (Execute Now)  │        │  Analyzer        │
│                 │        │  (Future: Compile│
│  Runtime        │        │  to Native)      │
│  Execution      │        └──────────────────┘
└─────────────────┘
```

## Interpreter Mode (Current Implementation)

### How It Works

1. **Tokenization** (`lexer.py`)
   - Reads source code character by character
   - Produces stream of tokens (keywords, numbers, operators, etc.)
   - Handles BASIC-80 quirks (no spaces between keywords)

2. **Parsing** (`parser.py`)
   - Builds Abstract Syntax Tree (AST) from tokens
   - One-time parse, validates syntax
   - Produces structured representation of program

3. **Runtime Execution** (`basic_runtime.py`)
   - Executes AST directly
   - Maintains runtime state (variables, arrays, stacks)
   - Dynamic typing, dynamic array sizing
   - Immediate execution of parsed code

### Hardware Compatibility Notes

**PEEK/POKE** - Emulated for compatibility:
- POKE: Parsed and executes successfully, but performs no operation (no-op)
- PEEK: Returns random integer 0-255 (for RNG seeding compatibility)
- **PEEK does NOT return values written by POKE** - no memory state is maintained
- No access to actual system memory

See [Compatibility Guide](compatibility.md) for full details on hardware-specific features.

### Benefits

✅ **Fast startup**: No compilation delay
✅ **Full compatibility**: Supports all BASIC-80 dynamic features
✅ **Interactive**: REPL mode works naturally
✅ **Flexible**: Variables can change types at runtime
✅ **No preprocessing**: Programs run as written

### Trade-offs

⚠️ **Runtime overhead**: Type checking, bounds checking at runtime
⚠️ **No optimizations**: Executes code as parsed
⚠️ **Memory usage**: Maintains full AST in memory

## Compiler Backend (Semantic Analyzer)

### What It Is

MBASIC includes a **semantic analyzer** (`semantic_analyzer.py`) that performs static analysis and optimization detection. This is the first phase of a potential **ahead-of-time compiler**.

**Current status**: Analysis only (no code generation yet)

### What It Does

The semantic analyzer implements **18 distinct optimizations**:

#### Core Optimizations (1-8)

1. **Constant Folding**
   - Evaluates constant expressions at compile time
   - Example: `X = 10 + 20 * 3` → `X = 70`

2. **Runtime Constant Propagation**
   - Tracks variable values through program flow
   - Example: `N% = 10: DIM A(N%)` → `DIM A(10)`
   - More flexible than 1980s BASIC compilers

3. **Common Subexpression Elimination (CSE)**
   - Detects repeated calculations
   - Example: `X = A + B: Y = A + B` → can reuse result

4. **Subroutine Side-Effect Analysis**
   - Analyzes what each GOSUB modifies
   - Precise interprocedural optimization
   - Only invalidates variables actually changed

5. **Loop Analysis**
   - Detects FOR, WHILE, and IF-GOTO loops
   - Calculates iteration counts for constant bounds
   - Identifies variables modified in loops

6. **Loop-Invariant Code Motion**
   - Identifies expressions computed multiple times in loop
   - Can hoist outside loop (when implemented)
   - Example: `FOR I=1 TO 100: X = A*B` → `A*B` is invariant

7. **Multi-Dimensional Array Flattening**
   - Converts `A(I,J)` to `A(I*stride+J)` at compile time
   - Calculates strides based on dimensions
   - Better cache locality, simpler runtime

8. **Dead Code Detection**
   - Finds unreachable code after GOTO, END, STOP
   - Identifies orphaned code with no incoming flow
   - Finds uncalled subroutines

#### Advanced Optimizations (9-18)

9. **Strength Reduction**
    - Replace expensive operations with cheaper ones
    - `X * 2` → `X + X` (addition cheaper than multiplication)
    - `X * 2^n` → detected for shift optimization

10. **Copy Propagation**
    - Tracks variable copies through flow
    - Example: `B = A: C = B` → `C = A`

11. **Algebraic Simplification**
    - Boolean identities: `X AND X` → `X`
    - Arithmetic identities: `X * 1` → `X`, `X * 0` → `0`
    - De Morgan's laws: `NOT (A AND B)` → `NOT A OR NOT B`

12. **Induction Variable Optimization**
    - Optimizes loop counter variables
    - Detects predictable patterns
    - Can eliminate unnecessary computations

13. **OPTION BASE Support**
    - Treats OPTION BASE as global compile-time declaration
    - Validates consistency across program
    - Enables better array optimization

14. **Expression Reassociation**
    - Regroups expressions to enable more constant folding
    - Example: `(X + 5) + 10` → `X + 15`

15. **Boolean Simplification**
    - NOT inversion: `NOT NOT X` → `X`
    - Absorption: `X OR (X AND Y)` → `X`
    - Complement: `X AND NOT X` → `0`

16. **Forward Substitution**
    - Eliminates single-use temporaries
    - Example: `T = A + B: X = T * 2` → `X = (A + B) * 2`

17. **Branch Optimization**
    - Detects constant conditions: `IF 1 THEN` → always true
    - Can eliminate dead branches

18. **Uninitialized Variable Detection**
    - Warns about use-before-assignment
    - Catches common bugs

### Performance

Semantic analysis is **very fast**:

| Program Size | Parse Time | Analysis Time | Total |
|--------------|------------|---------------|-------|
| 10 lines     | 0.3 ms     | 0.7 ms        | 1.0 ms|
| 100 lines    | 1.9 ms     | 1.4 ms        | 3.3 ms|
| 1000 lines   | 21.6 ms    | 13.7 ms       | 35 ms |

Even large programs analyze in milliseconds.

### Using the Analyzer

```bash
# Analyze a program (shows optimization opportunities)
python3 analyze_program.py myprogram.bas

# Summary view
python3 analyze_program.py myprogram.bas --summary

# JSON output
python3 analyze_program.py myprogram.bas --json
```

### Example Output

```
======================================================================
OPTIMIZATION SUMMARY
======================================================================

Optimization Opportunities Found:

  Constant Folding..................................  16
  Common Subexpressions.............................   1
  Strength Reductions...............................   4
  Forward Substitutions.............................   1
  Dead Stores.......................................   2
  Branch Optimizations..............................   4
  Induction Variables...............................   3
  Expression Reassociations.........................  13
  ------------------------------------------------------
  TOTAL.............................................  48

Program Statistics:

  Variables: 14
  Functions: 0
  Line Numbers: 217
  Loops Detected: 3
  Subroutines: 1

Recommendations:

  • Remove 2 unused assignment(s)
  • Eliminate 1 temporary variable(s)
  • Reuse 1 repeated computation(s)
```

## Compiled vs Interpreted: Key Differences

### Variable Types

**Interpreter (MBASIC)**:
- Dynamic typing at runtime
- Variables can change type
- DEF type statements execute when encountered
```basic
10 X = 5.5          ' X is single-precision
20 DEFINT X
30 X = 5.5          ' X is now integer (becomes 6)
```

**Compiler (if implemented)**:
- Static typing at compile time
- DEF type statements collected globally
- All DEFINT/DEFSNG/DEFDBL/DEFSTR apply to entire program
```basic
10 X = 5.5          ' X already integer everywhere
20 DEFINT X         ' Applies globally
30 X = 5.5          ' X was integer from line 10
```

### Array Sizing

**Interpreter (MBASIC)**:
- Dynamic sizing: `DIM A(N)` where N is a variable works
- Arrays allocated at runtime when DIM executes
- ERASE can deallocate arrays

**Compiler (if implemented)**:
- Static sizing: `DIM A(20)` works, `DIM A(N)` may not
- Array sizes must be constants or constant expressions
- No ERASE (static allocation)
- `REM $DYNAMIC` mode for runtime sizing (with overhead)

### Program Structure

**Interpreter (MBASIC)**:
- Executes lines in order
- GOTO/GOSUB resolved at runtime
- Can modify program at runtime (in interactive mode)

**Compiler (if implemented)**:
- All GOTO/GOSUB targets validated at compile time
- Dead code eliminated
- Optimizations applied
- No runtime program modification

### Interactive Commands

**Interpreter (MBASIC)**:
- Supports AUTO, DELETE, EDIT, LIST, RENUM
- Interactive REPL mode
- Direct mode (execute without line numbers)

**Compiler (if implemented)**:
- These commands removed (no source modification)
- Batch compilation only
- No interactive mode

## Future: Ahead-of-Time Compilation

The semantic analyzer is the first phase of a potential **native code compiler**:

### Planned Pipeline

```
Source → Lexer → Parser → Semantic Analyzer → Code Generator → Native Code
                                    ↑
                              (Implemented)
```

### Potential Targets

1. **Python Code Generation**
   - Compile .BAS to .py
   - Run with Python interpreter
   - Easier to debug

2. **C Code Generation**
   - Compile .BAS to .c
   - Compile with gcc/clang
   - Native performance

3. **JavaScript Code Generation**
   - Compile .BAS to .js
   - Run in browser or Node.js
   - Web deployment

4. **LLVM IR Generation**
   - Compile to LLVM intermediate representation
   - Full optimization suite
   - Multiple target architectures

### Benefits of Compilation

✅ **Performance**: 10-100x faster than interpretation
✅ **Optimizations**: All 18 optimizations applied
✅ **Type safety**: Errors caught at compile time
✅ **Distribution**: Standalone executables
✅ **Analysis**: Rich error messages and warnings

### Trade-offs

⚠️ **Compatibility**: Some dynamic features may not work
⚠️ **Compilation time**: Slower startup (analyze + compile)
⚠️ **Flexibility**: Cannot modify code at runtime
⚠️ **Debugging**: Harder to debug compiled code

## Why Both?

### Interpreter: Development and Compatibility

Use the interpreter for:
- ✅ Learning BASIC
- ✅ Quick prototyping
- ✅ Interactive experimentation
- ✅ Maximum BASIC-80 compatibility
- ✅ Dynamic programs (runtime DIM, type changes)

### Compiler: Production and Performance

Use the compiler (when available) for:
- ✅ Performance-critical code
- ✅ Standalone distribution
- ✅ Static analysis (find bugs)
- ✅ Optimization insights
- ✅ Production deployment

## Status

**Current Implementation**: ✅ **Interpreter** (fully functional)
**Semantic Analyzer**: ✅ **Complete** (18 optimizations)
**Code Generation**: ❌ **Not implemented** (future work)

The semantic analyzer is production-ready and can be used for:
- Program analysis and optimization reports
- Bug detection (uninitialized variables, dead code)
- Understanding program behavior
- Future compilation when code generator is added

## See Also

- [Features](features.md) - What's implemented in the interpreter
- [Compatibility](compatibility.md) - Differences from MBASIC 5.21
- [Not Implemented](not-implemented.md) - What doesn't work
- [Language Reference](../common/language/index.md) - BASIC-80 syntax

## Technical Documentation

For developers interested in the compiler design:
- `docs/design/future_compiler/README.md` - Compiler design overview
- `docs/design/future_compiler/OPTIMIZATION_STATUS.md` - Detailed optimization docs
- `docs/design/future_compiler/README_OPTIMIZATIONS.md` - Optimization guide
- `docs/history/COMPILER_DESIGN.md` - Compiler vs interpreter differences
- `docs/history/INTERPRETER_COMPILER_ARCHITECTURE_2025-10-22.md` - Architecture plan