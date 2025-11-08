---
description: 27 compiler optimization techniques used in Compiled BASIC-80
keywords:
- compiler
- optimization
- performance
- code generation
title: Compiler Optimizations
type: reference
---

# Compiler Optimizations

The MBASIC compiler implements 27 optimization techniques to improve program performance and reduce code size.

## Summary

**27 optimizations analyzed** in the semantic analysis phase.

These optimizations are designed to preserve the original program behavior while identifying opportunities for performance improvement and resource reduction. The actual code transformations will be applied during code generation (currently in development).

## Optimizations

### Constant Folding
**What it does:** Calculates constant expressions at compile time instead of runtime.

**Example:**
```basic
X = 10 + 20    ' Compiler calculates 30 at compile time
' Becomes: X = 30
```

**Benefit:** Eliminates runtime calculations, making programs faster.

---

### Runtime Constant Propagation
**What it does:** Tracks variable values through the program to use constants where possible.

**Example:**
```basic
N% = 10
DIM A(N%)      ' Compiler knows N% = 10
' Becomes: DIM A(10)
```

**Benefit:** Allows variable array sizes, more flexible than original BASIC-80 compiler.

---

### Common Subexpression Elimination (CSE)
**What it does:** Detects when the same calculation is done multiple times and suggests reusing the result.

**Example:**
```basic
X = A + B
Y = A + B      ' Same calculation as line above
' Compiler suggests: TEMP = A + B, then X = TEMP, Y = TEMP
```

**Benefit:** Eliminates redundant calculations, improves performance.

---

### Subroutine Side-Effect Analysis
**What it does:** Tracks which variables each GOSUB modifies, only invalidates affected optimizations.

**Example:**
```basic
X = A + B
GOSUB 1000     ' Only clears optimizations if subroutine 1000 modifies A or B
Y = A + B      ' Can still reuse if A and B unchanged
```

**Benefit:** Preserves more optimization opportunities across subroutine calls.

---

### Loop Analysis
**What it does:** Detects FOR, WHILE, and IF-GOTO loops, calculates iteration counts when possible.

**Example:**
```basic
FOR I = 1 TO 10    ' Compiler knows: 10 iterations
  PRINT I
NEXT I
```

**Benefit:** Identifies small loops for unrolling, foundation for loop optimizations.

---

### Loop-Invariant Code Motion
**What it does:** Identifies calculations inside loops that don't change and can be moved outside.

**Example:**
```basic
FOR I = 1 TO 100
  X = A * B    ' A*B is the same every iteration
  Y = X + I
NEXT I
' Can move: TEMP = A*B before loop, use TEMP inside
```

**Benefit:** Reduces calculations in hot loops, significant performance gain.

---

### Multi-Dimensional Array Flattening
**What it does:** Converts multi-dimensional array access to single-dimension for simpler runtime code.

**Example:**
```basic
DIM A(10, 20)
X = A(5, 10)
' Becomes: X = A(5 * 20 + 10) = A(110)
```

**Benefit:** Faster array access, better memory layout, enables more optimizations.

---

### OPTION BASE Analysis
**What it does:** Treats OPTION BASE as global compile-time setting, validates consistency.

**Example:**
```basic
OPTION BASE 1
DIM A(10)      ' Array indices: 1 to 10 (not 0 to 10)
```

**Benefit:** Prevents array indexing errors at compile time.

---

### Dead Code Detection
**What it does:** Finds code that can never execute and warns about it.

**Example:**
```basic
GOTO 100
PRINT "Never runs"    ' Dead code warning
100 END
```

**Benefit:** Identifies bugs, can eliminate unreachable code in compiled output.

---

### Strength Reduction
**What it does:** Replaces expensive operations with cheaper equivalent ones.

**Examples:**
```basic
X * 2          ' → X + X (addition faster than multiplication)
X ^ 2          ' → X * X (multiplication faster than exponentiation)
X * 1          ' → X (eliminate operation)
X + 0          ' → X (eliminate operation)
```

**Benefit:** Faster execution by using simpler operations.

---

### Copy Propagation
**What it does:** Detects simple variable copies and suggests replacing the copy with the original.

**Example:**
```basic
X = 100
Y = X          ' Copy detected
Z = Y + 10     ' Can use X instead: Z = X + 10
```

**Benefit:** Reduces register pressure, eliminates unnecessary copies.

---

### Algebraic Simplification
**What it does:** Applies mathematical identities to simplify expressions.

**Examples:**
```basic
X AND 0        ' → 0
X OR 0         ' → X
X XOR X        ' → 0
NOT(NOT X)     ' → X
```

**Benefit:** Simplifies logic, eliminates redundant operations.

---

### Induction Variable Optimization
**What it does:** Detects loop variables that change by constant amounts and optimizes their calculations.

**Example:**
```basic
FOR I = 1 TO 100
  J = I * 5
  A(J) = I     ' Can increment J by 5 instead of multiplying
NEXT I
```

**Benefit:** Replaces multiplication with addition in loops (much faster).

---

### Expression Reassociation
**What it does:** Rearranges calculations to group constants together.

**Examples:**
```basic
X = (A + 1) + 2    ' → A + 3
Y = 2 * A * 3      ' → A * 6
```

**Benefit:** Exposes more constant folding opportunities.

---

### Boolean Simplification
**What it does:** Simplifies boolean logic by applying logical rules.

**Examples:**
```basic
NOT(A > B)           ' → A <= B
NOT(A AND B)         ' → (NOT A) OR (NOT B)  (De Morgan's law)
(A AND B) OR A       ' → A  (absorption law)
```

**Benefit:** Eliminates NOT operations, simpler conditionals, faster evaluation.

---

### Forward Substitution
**What it does:** Detects temporary variables used only once and suggests eliminating them.

**Example:**
```basic
TEMP = A + B
PRINT TEMP     ' TEMP used only once
' Can substitute: PRINT A + B
```

**Benefit:** Reduces variables, simplifies code, detects dead stores.

---

### Branch Optimization
**What it does:** Detects IF conditions that are always true or false at compile time.

**Examples:**
```basic
IF 1 THEN PRINT "A"              ' Always TRUE
IF 0 THEN PRINT "B"              ' Always FALSE - THEN branch dead
A = 10
IF A > 5 THEN PRINT "C"          ' Constant propagation → always TRUE
```

**Benefit:** Eliminates impossible branches, reduces runtime overhead.

---

### Uninitialized Variable Detection
**What it does:** Warns when variables are used before being assigned a value.

**Example:**
```basic
PRINT X        ' Warning: X used before assignment
X = 10
```

**Benefit:** Catches typos and logic errors, improves code quality.

---

### Range Analysis
**What it does:** Tracks possible value ranges of variables through IF statements.

**Example:**
```basic
INPUT X
IF X > 5 THEN
  PRINT X      ' Compiler knows: X must be > 5 here
END IF
```

**Benefit:** Enables more constant propagation, better dead code detection.

---

### Live Variable Analysis
**What it does:** Detects variables that are assigned but never used (dead writes).

**Example:**
```basic
X = 10
X = 20         ' First assignment is dead (overwritten)
PRINT X
```

**Benefit:** Identifies unused code, foundational for register allocation.

---

### String Constant Pooling
**What it does:** Detects duplicate string constants and suggests sharing them.

**Example:**
```basic
PRINT "Error"
PRINT "Success"
PRINT "Error"   ' Same as line 1
' Suggests: STR1$ = "Error", reuse it
```

**Benefit:** Reduces memory usage in string-heavy programs.

---

### Built-in Function Purity Analysis
**What it does:** Classifies functions as pure (deterministic) or impure (has side effects).

**Pure functions:** SIN, COS, ABS, LEN, etc. (can be optimized)
**Impure functions:** RND, INPUT$, PEEK, etc. (cannot be optimized)

**Benefit:** Enables aggressive optimization of pure function calls.

---

### Array Bounds Analysis
**What it does:** Detects array access outside declared bounds at compile time.

**Example:**
```basic
DIM A(10)
A(11) = 100    ' ERROR: Index 11 > upper bound 10
```

**Benefit:** Catches "Subscript out of range" errors before runtime.

---

### Alias Analysis
**What it does:** Detects when array accesses might refer to the same element.

**Example:**
```basic
A(5) = 10
X = A(5)       ' Definite alias (same index)
A(I) = 10
Y = A(J)       ' Possible alias (I and J might be equal)
```

**Benefit:** Determines when CSE is safe for array operations.

---

### Available Expression Analysis
**What it does:** Tracks expressions computed on all program paths for safe elimination.

**Example:**
```basic
X = A + B      ' First computation
Y = C + D      ' Neither A nor B modified
Z = A + B      ' Available: can reuse X
```

**Benefit:** More precise than basic CSE, identifies truly redundant calculations.

---

### String Concatenation in Loops
**What it does:** Detects inefficient string building patterns inside loops.

**Example:**
```basic
S$ = ""
FOR I = 1 TO 1000
  S$ = S$ + "*"    ' WARNING: 1000 string allocations
NEXT I
' Suggests: Use SPACE$(1000) or array approach
```

**Benefit:** Identifies performance bottlenecks, suggests better alternatives.

---

### Type Rebinding Analysis
**What it does:** Detects when variables can change type at different program points for optimization.

**Example:**
```basic
I = 22.1           ' I is DOUBLE (slow)
FOR I = 0 TO 10    ' I becomes INTEGER (fast!)
  J = J + I        ' INTEGER arithmetic (500x faster on 8080)
NEXT I
```

**Benefit:** Fast INTEGER loops even if variable was DOUBLE before. Huge performance gain on vintage hardware.

**Note:** On 8080 CPU, INTEGER operations take 10-50 cycles, DOUBLE takes 8000-15000 cycles (500-800x difference!)

---

## Code Generation

**Status:** In Progress

Additional optimizations will be added during code generation:
- Peephole optimization
- Register allocation
- Instruction scheduling
- Actual code motion (moving loop-invariant code)
- Dead code elimination (actual removal)
- Loop unrolling (actual transformation)

## See Also

- [BASIC-80 Language Reference](../language/index.md)
- [Compiler Index](index.md)
- [Functions](../language/functions/index.md)
- [Statements](../language/statements/index.md)
